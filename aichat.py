# ============================================================
# Soviet9773Red/ollama-gradio-chat is licensed under the MIT License
# @license (c) Alexander Soviet9773Red - https://github.com/Soviet9773Red/ollama-gradio-chat
# Local AI Chat Interface
# Ollama + Gradio
#
# Description:
# A lightweight local AI chat interface that connects to
# Ollama models and provides a multi-model comparison UI.
#
# Features:
# - Local and Ollama cloud models
# - Streaming responses
# - Markdown rendering with code syntax highlighting
# - Isolated A/B model comparison (turn-based slots)
# - Late model attachment / per-slot model switching
# - Ollama error handling in UI (incl. subscription 403)
# - Session save/load + Markdown export
# - Multi-language UI (EN / SV / RU)
# - Auto copy-buttons for code blocks
# - External CSS / JS
# ============================================================
APP_VERSION = "2.7.0 bld 20260608"
DEFAULT_USER_NAME = "Alexander" 

import gradio as gr
import ollama
import time
import re
import html  
import subprocess
import socket
import os
import json
from typing import List, Dict
from datetime import datetime

# Get the absolute path to the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SYS_DIR = os.path.join(SCRIPT_DIR, "sys")
CSS_DIR = os.path.join(SYS_DIR, "themes") # sys/themes/
DATA_DIR = os.path.join(SCRIPT_DIR, "chats", "current")
EXPORTS_DIR = os.path.join(SCRIPT_DIR, "exports")
SAVES_DIR = os.path.join(SCRIPT_DIR, "chats")


# CONFIGURATION
# ===========================================
CONFIG_DEFAULTS = {
    "model_a":      "None",
    "model_b":      "None",
    "lang":         "EN",
    "streaming":    True,
    "css_theme":    "no-css",
    "gradio_theme": "Base"
}

GRADIO_THEMES = {
    "Default":    gr.themes.Default(),
    "Base":       gr.themes.Base(),
    "Citrus":     gr.themes.Citrus(),
    "Glass":      gr.themes.Glass(),
    "Monochrome": gr.themes.Monochrome(),
    "Origin":     gr.themes.Origin(),
    "Ocean":      gr.themes.Ocean(),
    "Soft":       gr.themes.Soft()
}

# FILE SYSTEM
# ===========================================
# Paths to config, CSS, JS files
CONFIG_PATH = os.path.join(SCRIPT_DIR, "config.json")
JS_PATH = os.path.join(SYS_DIR, "script.js")

# Save session (turn-based)
def save_session(turns):
    os.makedirs(DATA_DIR, exist_ok=True)
    data = {
        "version":  APP_VERSION,
        "saved_at": datetime.now().isoformat(),
        "turns":    turns
    }
    session_path = os.path.join(DATA_DIR, "session.json")
    with open(session_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Load session (turn-based)
def load_session():
    session_path = os.path.join(DATA_DIR, "session.json")
    if not os.path.exists(session_path):
        return {"turns": []}
    try:
        with open(session_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {"turns": data.get("turns", [])}
    except Exception as e:
        print("Load session ERROR:", e)
        return {"turns": []}   

# Delete session
def delete_session_file():
    session_path = os.path.join(DATA_DIR, "session.json")
    if os.path.exists(session_path):
        os.remove(session_path)

# Load config
def load_config():
    if not os.path.exists(CONFIG_PATH):
        return CONFIG_DEFAULTS.copy()
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        # backward-compatible merge: дефолты + то что есть в файле
        return {**CONFIG_DEFAULTS, **data}
    except Exception as e:
        print("Load config ERROR:", e)
        return CONFIG_DEFAULTS.copy()
        
# Save config
def save_config(model_a, model_b, lang, streaming, css_theme="no-css", gradio_theme="Default"):
    data = {
        "model_a":       model_a,
        "model_b":       model_b,
        "lang":          lang,
        "streaming":     streaming,
        "css_theme":     css_theme,
        "gradio_theme":  gradio_theme
    }
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# Export to Markdown
def export_md(state):
    turns = unpack_state(state)
    if not turns:
        return "Nothing to export — history is empty"
    os.makedirs(EXPORTS_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = os.path.join(EXPORTS_DIR, f"chat_{ts}.md")
    with open(path, "w", encoding="utf-8") as f:
        header = f"# Chat export\n\nSaved: {datetime.now().isoformat()}\n\n"
        f.write(header + render_chat(turns))
    return f"Saved to: {path}"

# Save chat to json
def save_chat_fn(state):
    turns = unpack_state(state)
    if not turns:
        return "Nothing to save — history is empty"
    os.makedirs(SAVES_DIR, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"_{ts}.json"
    path = os.path.join(SAVES_DIR, filename)
    data = {
        "version":  APP_VERSION,
        "saved_at": datetime.now().isoformat(),
        "turns":    turns
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return f"💾 Saved: **{filename}**"

# Get themes list
def get_css_themes():
    if not os.path.exists(CSS_DIR):
        return ["no-css"]
    files = [f[:-4] for f in os.listdir(CSS_DIR) if f.endswith(".css")]
    return ["no-css"] + sorted(files)

# OLLAMA API 
# ===========================================

# check Ollama serve state 
def ensure_ollama_running():
    import time
    try:
        # Try to run in background 
        proc = subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE
        )
        # Waiting 1s and check if no err
        time.sleep(1)
        if proc.poll() is not None:
            # Процесс завершился — читаем stderr
            err = proc.stderr.read().decode()
            if "bind" in err:
                print("         Ollama already running.")
            else:
                print(f"         Ollama error: {err}")
        else:
            # Process OK? - Ollama is running
            print("         Ollama started, waiting 4s...")
            time.sleep(4)
    except FileNotFoundError:
        print("         Ollama not found in PATH.")
    except Exception as e:
        print(f"         Ollama start error: {e}")
   
# Detect installed models: Ollama list
def get_installed_models():
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            return []
        lines = result.stdout.splitlines()[1:]
        models = []
        for line in lines:
            parts = line.split()
            if parts:
                models.append(parts[0])
        return models
    except subprocess.TimeoutExpired as e:
        e.process.kill()
        print("Ollama timeout — start Ollama manually and restart app")
        return []
    except FileNotFoundError:
        print("Ollama not found in PATH.")
        return []
    except Exception as e:
        print(f"Ollama error: {e}")
        return []

# Language support
LANG = {
    "EN": {
        "send_btn": "Ask model",
        "placeholder": "Type your question.\nEnter = new line\nAsk model or Shift+Enter = ask question",
        "clear_btn": "Clear chat",
        "chat_title": "# Ollama + Gradio Local AI Lab",
        "subtitle": " Numbered questions · model-labelled responses",
        "empty_history": "History is empty...",
        "model_a": "🤖 Model A",
        "model_b": "🤖 Model B",
        "save_md": "Export .md"
    },
    "SV": {
        "send_btn": "Ställ frågan",
        "placeholder": "Skriv din fråga.\nEnter = ny rad\nFråga-knappen eller Shift+Enter = ställ frågan",
        "clear_btn": "Rensa chat",
        "chat_title": "# Ollama + Gradio Local AI Lab",
        "subtitle":  " Numrerade frågor och modellmärkta svar.",
        "empty_history": "Historiken är tom...",
        "model_a": "🤖 Modell A",
        "model_b": "🤖 Modell B",
        "save_md": "Spara som .md"
    },
    "RU": {
        "send_btn": "Отправить вопрос",
        "placeholder": "Введите вопрос.\nEnter — новая строка\nКнопка или Shift+Enter - отправляет вопрос",
        "clear_btn": "Очистить чат",
        "chat_title": "# Локальный ИИ",
        "subtitle":  "вопросы и ответы с именем модели.",
        "empty_history": "История пуста...",
        "model_a": "🤖 Модель A",
        "model_b": "🤖 Модель Б",
        "save_md": "Сохранить в .md"
    }
}


# System prompts - UPDATED with explicit code formatting instructions
BASE_PROMPT = {
    "EN":
    """
    You are an AI language model.
    The user interacting with you is named {DEFAULT_USER_NAME}.
    You are the assistant.

    Respond clearly, directly, and concisely.
    Do not invent facts. If you are unsure, say so.
    Respond in the same language as the user's message.

    If the user asks for code without specifying a language, use JavaScript.
    If the user asks for Python code, use Python.

    IMPORTANT: When providing code, always wrap it in Markdown code blocks with triple backticks.
    Specify the language after the opening backticks (e.g., ```python, ```javascript, ```bash, ```cpp).
    Example:
    ```python
    def hello():
        print("Hello, World!")
    ```
    """,

    "SV":
    """
    Du är en AI-språkmodell.
    Användaren du pratar med heter {DEFAULT_USER_NAME}.
    Du är assistenten.

    Svara tydligt, direkt och sakligt.
    Hitta inte på fakta. Om du är osäker ska du säga det.
    Svara på samma språk som användaren skriver.

    Om användaren ber om kod utan att ange språk, använd JavaScript.
    Om användaren ber om Python-kod, använd Python.

    VIKTIGT: När du tillhandahåller kod, omslut den alltid med Markdown-kodblock med tre backticks.
    Ange språket efter de inledande backticks (t.ex. ```python, ```javascript, ```cpp, ```bash).
    """,

    "RU":
    """
    Ты — языковая модель искусственного интеллекта.
    Пользователь, с которым ты общаешься, — {DEFAULT_USER_NAME}.
    Ты являешься ассистентом.

    Отвечай ясно, прямо и по делу.
    Не выдумывай факты. Если не уверен — так и скажи.
    Отвечай на том же языке, на котором пишет пользователь.

    Если пользователь просит написать код и не указывает язык,
    используй JavaScript.
    Если пользователь просит код на Python, используй Python.

    ВАЖНО: Когда ты предоставляешь код, всегда обрамляй его в Markdown-блоки с тремя обратными кавычками.
    Указывай язык после открывающих кавычек (например, ```python, ```javascript, ```cpp, ```bash).
    Пример:
    ```python
    def hello():
        print("Привет, мир!")
    ```
    """
}

MODEL_PROMPT_PATCH = {}

def get_system_prompt(model_name: str, lang: str):
    base_template = BASE_PROMPT.get(lang, BASE_PROMPT["EN"])
    base = base_template.format(DEFAULT_USER_NAME=DEFAULT_USER_NAME)
    patch = MODEL_PROMPT_PATCH.get(model_name, {}).get(lang, "")
    if patch:
        base += "\n\n" + patch
    return {
        "role": "system",
        "content": base
    }

def looks_like_code(text: str) -> bool:
    """Heuristic to detect if text looks like code"""
    code_indicators = [
        'def ', 'class ', 'import ', 'from ',
        'function ', 'const ', 'let ', 'var ',
        '<?php', '#include', 'package ',
        '    ', '\t',  # indentation
        '```'  # already has code blocks
    ]
    text_lower = text.lower()
    return any(ind in text for ind in code_indicators) or '\n' in text and ('    ' in text or '\t' in text)

def format_user_content(content: str) -> str:
    """Format user content for display - escape HTML and optionally wrap code"""
    # Escape HTML to prevent XSS and markdown breakage
    safe_content = html.escape(content)
    
    # If it looks like code but isn't wrapped in backticks, wrap it
    if looks_like_code(content) and not content.strip().startswith('`'):
        return f"<pre><code>{safe_content}</code></pre>"
    
    return safe_content

# Render for history A/B and state unpack
def unpack_state(state):
    """Return turns list from state dict."""
    if isinstance(state, dict):
        return list(state.get("turns", []))
    return []

def build_messages(turns, slot, model_name, lang):
    """Linear Ollama messages for one slot: system + only the turns this slot answered."""
    msgs = [get_system_prompt(model_name, lang)]
    for t in turns:
        ans = t["answers"].get(slot)
        if ans is not None:
            msgs.append({"role": "user", "content": t["q"]})
            msgs.append({"role": "assistant", "content": ans["content"]})
    return msgs

def render_chat(turns):
    """Render turns: one question, then whatever slots answered (A, B). Missing slot = skip."""
    lines = []
    for i, t in enumerate(turns):
        q = format_user_content(t["q"].strip())
        lines.append(f'<div class="user-message">\n\n### 👤❓ #{i+1}\n\n{q}\n\n</div>')
        for slot in ("A", "B"):
            ans = t["answers"].get(slot)
            if ans:
                body = ans["content"].strip() + f"\n\n*(⏱ {ans.get('time', 0):.2f}s)*"
                lines.append(
                    f'<div class="assistant-message">\n\n---\n\n'
                    f'### 🤖 #{i+1}{slot} {ans["model"]}\n\n{body}\n\n</div>'
                )
    return "\n\n".join(lines)

# Stream        
def stream_model_answer(model_name, messages):
    stream = ollama.chat(
        model=model_name,
        messages=messages,
        stream=True
    )
    text = ""
    for chunk in stream:
        token = chunk["message"]["content"]
        text += token
        yield text

    
def stream_markdown(history_md, model_name, text):
    return (
        history_md
        + f'\n\n<div class="assistant-message">\n\n---\n\n### 🤖 {model_name}\n\n{text}\n\n</div>'
    )

# Error format    
def format_ollama_error(model_name: str, exc: Exception) -> str:
    """Render an Ollama/runtime error as an assistant-style markdown block."""
    status = getattr(exc, "status_code", None)   # есть у ollama.ResponseError
    raw = str(exc).strip() or exc.__class__.__name__

    if status == 403:
        title = "Error: 403 Forbidden"
    elif status == 404:
        title = "Error: 404 Not Found"
    elif status == 401:
        title = "Error: 401 Unauthorized"
    elif status == 500:
        title = "Error: 500 Internal Server Error"
    elif status is not None:
        title = f"Error: {status}"
    elif isinstance(exc, ConnectionError) or "connect" in raw.lower():
        title = "Error: no connection to Ollama (ollama serve?)"
    else:
        title = f"Error: {exc.__class__.__name__}"

    return (
        '<div class="assistant-message">\n\n'
        '---\n\n'
        f'### ⚠ {model_name}\n\n'
        f'**{title}**\n\n'
        f'```\n{raw}\n```\n\n'
        '</div>'
    )    
    
# Chat fn    
def chat_fn(user_text, state, model_a, model_b, streaming, lang):
    status_msg = ""
    turns = unpack_state(state)

    if model_a == "None" and model_b == "None":
        yield "", state, render_chat(turns), "No model selected"
        return
    if model_a != "None" and model_a == model_b:
        model_b = "None"
        status_msg = f"Model B disabled (same as Model A: {model_a})"

    if not user_text.strip():
        yield "", state, render_chat(turns), ""
        return

    base_turns = turns                       # original list, never mutated
    new_turn = {"q": user_text, "answers": {}}
    turns = turns + [new_turn]               # new list; only new_turn is mutated

    plan = []
    if model_a != "None":
        plan.append(("A", model_a))
    if model_b != "None":
        plan.append(("B", model_b))

    committed = {"turns": base_turns}        # state to persist if interrupted now

    for slot, model_name in plan:
        messages = build_messages(base_turns, slot, model_name, lang) \
                   + [{"role": "user", "content": user_text}]
        base_md = render_chat(turns)

        loading = f"<span class='loading'>{model_name}: </span>"
        if status_msg:
            loading = f"{status_msg}<br>" + loading
            status_msg = ""

        text = ""
        start = time.time()
        try:
            if streaming:
                yield "", committed, base_md, loading
                for partial in stream_model_answer(model_name, messages):
                    text = partial
                    yield "", committed, stream_markdown(base_md, model_name, text), \
                          f"<span class='loading'>{model_name}: </span>"
            else:
                yield "", committed, base_md, loading
                response = ollama.chat(model=model_name, messages=messages, stream=False)
                text = response["message"]["content"]
        except Exception as e:
            err_md = format_ollama_error(model_name, e)
            partial_md = stream_markdown(base_md, model_name, text) if text else base_md
            if new_turn["answers"]:
                save_session(turns)
                yield "", {"turns": turns}, partial_md + "\n\n" + err_md, \
                      f"Slot {slot} error (status {getattr(e, 'status_code', '?')})"
            else:
                yield user_text, {"turns": base_turns}, \
                      render_chat(base_turns) + "\n\n" + err_md, \
                      f"Slot {slot} error (status {getattr(e, 'status_code', '?')})"
            return

        elapsed = time.time() - start
        new_turn["answers"][slot] = {"model": model_name, "content": text, "time": elapsed}
        committed = {"turns": turns}
        save_session(turns)
        if not streaming:
            yield "", committed, render_chat(turns), ""

    yield "", committed, render_chat(turns), ""
    
# Clear history and unlock models change  
def clear_history_fn(lang_code: str):
    delete_session_file()
    return (
        "",
        {"turns": []},
        LANG[lang_code]["empty_history"],
        ""
    )
    
# Init app
def init_app(lang, cur_model):
    cfg = load_config()
    state_data = load_session()

    lang = cfg["lang"]
    labels = LANG[lang]

    cur_model = cfg["model_a"]
    if cur_model not in models:
        cur_model = models[1] if len(models) > 1 else "None"

    model_b_val = cfg["model_b"] if cfg["model_b"] in models else "None"

    session_path = os.path.join(DATA_DIR, "session.json")
    loaded_label = ". chats/current/session.json" if os.path.exists(session_path) else "No session"

    return (
        gr.update(value=labels["chat_title"]),                # chat_title
        gr.update(value=labels["subtitle"]),                  # top_status
        gr.update(label=labels["model_a"], value=cur_model),  # model_a
        gr.update(label=labels["model_b"], value=model_b_val),# model_b
        gr.update(value=labels["clear_btn"]),                 # clear_btn
        gr.update(placeholder=labels["placeholder"]),         # msg
        gr.update(value=labels["send_btn"]),                  # send_btn
        gr.update(value=labels["save_md"]),                   # export_btn
        gr.update(value=cfg["streaming"]),                    # streaming_box
        gr.update(value=lang),                                # lang_selector
        state_data,                                           # state
        render_chat(state_data["turns"]),                     # chat_box
        loaded_label                                          # loaded_chat_box
    )

# Read CSS and JS files for embedding
def load_file_content(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"Error loading {filepath}: {e}")
        return ""


# START HTTP SERVER with js and css in DOM 
# ===========================================
js_content = load_file_content(JS_PATH)
base_css = load_file_content(os.path.join(SYS_DIR, "base.css"))

# Load themes from config on start
_cfg = load_config()

# Gradio theme
_gradio_theme_name = _cfg.get("gradio_theme", "Default")
_gradio_theme = GRADIO_THEMES.get(_gradio_theme_name, gr.themes.Default())

# CSS theme
_css_theme_name = _cfg.get("css_theme", "no-css")
if _css_theme_name != "no-css":
    _theme_css = load_file_content(os.path.join(CSS_DIR, f"{_css_theme_name}.css"))
else:
    _theme_css = ""

custom_head = f'''
<style>{base_css}</style>
<style id="dynamic-theme">{_theme_css}</style>
<script>{js_content}</script>
'''

# === HTML RENDER ===
with gr.Blocks(title="Ollama AI Chat") as aichat:
    
    # FUNCTIONS
    def show_file():
        return gr.update(visible=True)

    # Load chat json
    def load_chat(file):
        if file is None:
            return gr.update(visible=False), "No file", gr.update(), gr.update()
        try:
            with open(file.name, "r", encoding="utf-8") as f:
                data = json.load(f)
            turns = data.get("turns", [])
            save_session(turns)
            return (
                gr.update(visible=False),
                f"📁.. {os.path.basename(file.name)}",
                {"turns": turns},
                render_chat(turns)
            )
        except Exception as e:
            return gr.update(visible=False), f"ERROR: {e}", gr.update(), gr.update()

    # HIDDEN FILE PICKER
    file_input = gr.File(
        file_types=[".json"],
        visible=False
    )
    
    #  TOP BAR - HTML part
    # =========================
    with gr.Row():

        with gr.Group():
            with gr.Column():
                load_btn = gr.Button("Open 📂 chat")
                path_label = gr.Markdown("&nbsp; json: ./chats")
                save_btn = gr.Button("Save 💾 chat")

        loaded_chat_box = gr.Textbox(label="Session:")

        with gr.Group():
            with gr.Column():
                version_label = gr.Markdown(f"<div style='text-align:right; opacity:0.6;'>Version &nbsp;{APP_VERSION}</div>")
                #Ftemp = gr.Slider(label="Temperature", value=70)                


    # CHAT
    # =========================
    chat_title = gr.Markdown()    
    top_status = gr.Markdown()
    
    with gr.Row():    
        gr.Markdown()
        btn_dwn = gr.Button("▾ To input", scale=0)
        gr.Markdown()
        
    chat_box = gr.Markdown("CHAT AREA", elem_id="chat_box")
    status_bar = gr.Markdown("", elem_id="status_bar")


    # CONTROL PANEL
    # =========================
    with gr.Row():
        print("STEP 0: starting Ollama if needed")
        ensure_ollama_running()
        print("STEP 1: requesting model list from Ollama")
        print("         (if Ollama is not running, start it first: ollama serve)")
        models = ["None"] + get_installed_models()
        if len(models) == 1:  # только "None"
            print("WARNING: No models loaded. Is Ollama running? Try 'ollama list' in >terminal")
        print("STEP 2: models detected:", models)
        
        with gr.Group():
            with gr.Column():
                streaming_box = gr.Checkbox(label="🚀 Stream answers", value=False, elem_id="streaming_toggle")
                with gr.Row():    
                    model_a = gr.Dropdown(choices=models, value=models[1] if len(models) > 1 else "None", label=LANG["SV"]["model_a"])
                    model_b = gr.Dropdown(choices=models, value="None", label=LANG["SV"]["model_b"])
                
        with gr.Group():
            export_btn = gr.Button(LANG["SV"]["save_md"])
            gr.Markdown("&nbsp; → .md · ./export") # Path note cell
            clear_btn = gr.Button()

    # INPUT
    # =========================
    with gr.Column():
        with gr.Row():
            lang_selector = gr.Radio(choices=["SV", "EN", "RU"], value="SV", label="🌐 Language", scale=1)
            btn_up = gr.Button("▴ Back to top", scale=0)
                
        msg = gr.Textbox(label=" ✏️ Type ·  ➤ Shift+Enter ",lines=5, placeholder=LANG["SV"]["placeholder"], elem_id="chat_input")
        send_btn = gr.Button(value=LANG["SV"]["send_btn"])
        state = gr.State({"turns": []})
    
        gr.Markdown("\n --- \n")
    
        gr.Markdown(" ⚙ THEMES CONFIG<br><small>· Restart aichat.py to apply</small>")
    
        with gr.Row():
            
                
            _gradio_val = _cfg.get("gradio_theme", "Default")
            gradio_theme_selector = gr.Dropdown(
                choices=list(GRADIO_THEMES.keys()),
                value=_gradio_val,
                label="🎨 Gradio theme"
            )
            
            _css_val = _cfg.get("css_theme", "no-css")
            _css_choices = get_css_themes()
            css_theme_selector = gr.Dropdown(
                choices=_css_choices,
                value=_css_val if _css_val in _css_choices else _css_choices[0],
                label="+ CSS overlay"
            )

# END OF HTML PART
# ===========================

    def update_ui_lang(lang, ma, mb, streaming, css_theme, gradio_theme):
        save_config(ma, mb, lang, streaming, css_theme, gradio_theme)
        labels = LANG[lang]
        return (
            gr.update(value=labels["chat_title"]),
            gr.update(label=labels["model_a"]),
            gr.update(label=labels["model_b"]),
            gr.update(value=labels["clear_btn"]),
            gr.update(placeholder=labels["placeholder"]),
            gr.update(value=labels["send_btn"]),
            gr.update(value=labels["save_md"])
        )

    # LOAD
    aichat.load(
        fn=init_app,
        inputs=[lang_selector, model_a],
        outputs=[
            chat_title, top_status,
            model_a, model_b,
            clear_btn, msg,
            send_btn, export_btn,
            streaming_box,
            lang_selector,
            state, chat_box,
            loaded_chat_box
        ]
    )
    
    
    # EVENTS
    # =========================
    
    lang_selector.change(
        fn=update_ui_lang,
        inputs=[lang_selector, model_a, model_b, streaming_box, css_theme_selector, gradio_theme_selector],
        outputs=[chat_title, model_a, model_b, clear_btn, msg, send_btn, export_btn]
    )
    
    send_btn.click(
        fn=chat_fn,
        inputs=[msg, state, model_a, model_b, streaming_box, lang_selector],
        outputs=[msg, state, chat_box, status_bar]
    )

    msg.submit(
        fn=chat_fn,
        inputs=[msg, state, model_a, model_b, streaming_box, lang_selector],
        outputs=[msg, state, chat_box, status_bar]
    )
    
    clear_btn.click(
        fn=clear_history_fn,
        inputs=[lang_selector],
        outputs=[msg, state, chat_box, status_bar]
    )
    
    export_btn.click(
        fn=export_md,
        inputs=[state],
        outputs=[status_bar]
    )
    
    load_btn.click(
        fn=show_file,
        outputs=file_input
    )
    
    save_btn.click(
        fn=save_chat_fn,
        inputs=[state],
        outputs=[top_status]
    )

    file_input.change(
        fn=load_chat,
        inputs=file_input,
        outputs=[file_input, loaded_chat_box, state, chat_box]
    )
    
    btn_dwn.click(
        fn=None,
        js="() => {const input = document.getElementById('chat_input'); if(input) { input.scrollIntoView({behavior:'smooth', block:'center'}); input.focus(); } }"
    )

    btn_up.click(
        fn=None,
        js="() => window.scrollTo({top: 0, behavior: 'smooth'})"
    )
    
    # Apply theme
    # ==================================   
    
    def on_config_change(model_a, model_b, lang, streaming, css_theme, gradio_theme):
        save_config(model_a, model_b, lang, streaming, css_theme, gradio_theme)

    config_inputs = [model_a, model_b, lang_selector, streaming_box, css_theme_selector, gradio_theme_selector]
    
# Events listener
    model_a.change(fn=on_config_change, inputs=config_inputs)
    model_b.change(fn=on_config_change, inputs=config_inputs)
    streaming_box.change(fn=on_config_change, inputs=config_inputs)
    lang_selector.change(fn=on_config_change, inputs=config_inputs)
    gradio_theme_selector.change(fn=on_config_change, inputs=config_inputs)
    css_theme_selector.change(fn=on_config_change, inputs=config_inputs)

def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip
    
print("STEP 3: detecting local IP")
ip = get_local_ip()
port = 7860
print("STEP 4: local IP detected:", ip)
print(f"Local server: http://127.0.0.1:{port}/?__theme=dark")
print(f"LAN access:  http://{ip}:{port}/?__theme=dark")
print("STEP 5: starting Gradio server. ⬆ Use local or LAN IP ⬆")
print(f"AI Chat version: {APP_VERSION}")

# Start
# -------------------------
# Launch without css parameter since styles are already embedded in head
aichat.launch(
    theme=_gradio_theme,
    head=custom_head,
    server_name="0.0.0.0",
    server_port=port
)
print("GRADIO: server closed")




