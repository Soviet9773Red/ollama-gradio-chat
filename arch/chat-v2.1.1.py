# ============================================================
# @license (c) Alexander Soviet9773Red - https://github.com/Soviet9773Red/ollama-gradio-chat
# Local AI Chat Interface
# Ollama + Gradio
#
# Description:
# A lightweight local AI chat interface that connects to
# Ollama models and provides a multi-model comparison UI.
#
# Features:
# - Multiple local models
# - Streaming responses
# - Markdown rendering
# - Model comparison (A/B)
# - Deep Thinking toggle
# - Multi-language UI (EN / SV / RU)
#
# ============================================================
APP_VERSION = "v2.1.1 build 20260316"
DEFAULT_USER_NAME = "John Doe" # Replace with your name (used as default user identifier)
# chat.py с Markdown-code in the answer body
import gradio as gr
import ollama
import time
import re
import html  
import subprocess
import socket
from   typing import List, Dict

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

    except Exception:
        return []

# Language support
LANG = {
    "EN": {
        "send_btn": "Ask model",
        "placeholder": "Type your question.\nEnter = new line\nAsk model or Shift+Enter = ask question",
        "clear_btn": "Clear history",
        "chat_title": "# Ollama + Gradio Local AI Lab.\n### Multi-model local \nAI interface Numbered questions and model-labelled responses.",
        "empty_history": "History is empty...",
        "deep_thinking": "Deep Thinking",
        "model_a": "Model A",
        "model_b": "Model B"
    },
    "SV": {
        "send_btn": "Ställ frågan",
        "placeholder": "Skriv din fråga.\nEnter = ny rad\nFråga-knappen eller Shift+Enter = ställ frågan",
        "clear_btn": "Rensa historik",
        "chat_title": "# Ollama + Gradio Local AI Lab. \n Numrerade frågor och modellmärkta svar.",
        "empty_history": "Historiken är tom...",
        "deep_thinking": "Djup analys",
        "model_a": "Modell A",
        "model_b": "Modell B"
    },
    "RU": {
        "send_btn": "Отправить вопрос",
        "placeholder": "Введите вопрос.\nEnter — новая строка\nКнопка или Shift+Enter - отправляет вопрос",
        "clear_btn": "Стереть вопросы и ответы модели",
        "chat_title": "# Локальный ИИ. \n #вопроса и ответы с именем модели.",
        "empty_history": "История пуста...",
        "deep_thinking": "Глубокое мышление",
        "model_a": "Модель A",
        "model_b": "Модель B"
    }
}

DEEP_THINKING_MODELS = {
    "cogito:14b"
}
"""
# Idea for future
model_settings = {

    "cogito:14b": {
        "temperature": 0.6,
        "top_p": 0.9
    },

    "qwen3.5:27b": {
        "temperature": 0.7,
        "top_p": 0.95
    },

    "ministral-3:14b": {
        "temperature": 0.5,
        "top_k": 40
    },

    "gemma3n:e4b-it-fp16": {
        "temperature": 0.7
    }

}
"""

# System prompts
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
    """
}


# Optional model-specific prompt adjustments.
# Use this dictionary to add extra instructions for specific models.
#
# IMPORTANT:
# The model name must match the exact name used in Ollama
# (see the output of `ollama list` on your system).
#
# If the name does not match an installed model, the patch will simply be ignored.
# Model-specific patches are optional and can be safely removed.

MODEL_PROMPT_PATCH = {}

# Example:
"""
MODEL_PROMPT_PATCH = {
    "cogito:14b": {
        "EN": "If you make a mistake, accept corrections.",
        "SV": "Om du gör ett misstag ska du acceptera korrigering."
    },

    "qwen3.5:9b": {
        "EN": "Prefer structured reasoning."
    }
}
"""

# Build the system prompt for a given model and language.
# Combines:
# - base prompt
# - optional model-specific patch
# - optional deep-thinking instruction
def get_system_prompt(model_name: str, lang: str, deep: bool):
    base = BASE_PROMPT.get(lang, BASE_PROMPT["EN"])
    patch = MODEL_PROMPT_PATCH.get(model_name, {}).get(lang, "")
    text = base
    
    if patch:
        text += "\n\n" + patch
    if model_name in DEEP_THINKING_MODELS and deep:
        text += "\nEnable deep thinking."

    return {
        "role": "system",
        "content": text
    }

def build_full_markdown(history: List[dict]) -> str:
    lines = []
    q_counter = 0
    for msg in history:
        role = msg["role"]
        content = msg["content"]
        content = content.strip() 
        model_name = msg.get("model_name", "")
        if role == "system":
            continue
        elif role == "user":
            q_counter += 1
            #lines.append(f" ? #{q_counter}: <br>{content}<br>")
            lines.append(f"\n\n## ? #{q_counter}\n\n{content}\n")
        elif role == "assistant":
            if model_name:

                lines.append(
                    f"\n\n---\n\n### {model_name}\n\n{content}"
                )
 
            else:
                lines.append(f"**Answer:**\n```\n{content}\n```")
        else:
            lines.append(f"**{role}**:\n\n{content}")
    return "\n\n".join(lines)

# Stream response tokens from Ollama model.
# This allows progressive rendering of the answer
# in the Gradio interface.
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

# MD streaming optimization
def build_history_markdown(history):
    """Build markdown only for finished history."""
    lines = []
    q_counter = 0

    for msg in history:
        role = msg["role"]
        content = msg["content"]
        model_name = msg.get("model_name", "")

        if role == "system":
            continue

        elif role == "user":
            q_counter += 1
            lines.append(f"\n\n### ? #{q_counter}\n\n{content}\n")

        elif role == "assistant":
            lines.append(
                f"\n\n---\n\n### {model_name}\n\n{content}"
            )

    return "\n\n".join(lines)
    
def stream_markdown(history_md, model_name, text):
    return (
        history_md
        + f"\n\n---\n\n### {model_name}\n\n{text}"
    )
    
# Main chat logic.
# Handles:
# - user input
# - message history
# - sequential calls to Model A and Model B
# - streaming responses

def chat_fn(user_text, history, model_a, model_b, deep_thinking_enabled, lang_code):

    if not user_text.strip():
        yield "", history, build_full_markdown(history)
        return

    if not any(msg["role"] == "system" for msg in history):
        history = [get_system_prompt(model_a, lang_code, deep_thinking_enabled)]

    updated = history + [{"role": "user", "content": user_text}]

    # Model A
    history_md = build_history_markdown(updated)
    yield "", updated, stream_markdown(history_md, model_a, "⏳ generating...")

    text_a = ""
    start_a = time.time()

    for partial in stream_model_answer(model_a, updated):
        text_a = partial
        yield "", updated, stream_markdown(history_md, model_a, text_a)

    time_a = time.time() - start_a
    ans_a = text_a + f"\n\n(⏱ {time_a:.2f}s)"

    new_history = updated + [
        {"role": "assistant", "content": ans_a, "model_name": model_a}
    ]

    # Model B
    if model_b != "None" and model_b != model_a:
        history_md_b = build_history_markdown(new_history)
        yield "", history, stream_markdown(history_md_b, model_b, "⏳ generating...")

        text_b = ""
        start_b = time.time()

        for partial in stream_model_answer(model_b, updated):
            text_b = partial
            yield "", new_history, stream_markdown(history_md_b, model_b, text_b)

        time_b = time.time() - start_b
        ans_b = text_b + f"\n\n(⏱ {time_b:.2f}s)"

        new_history.append(
            {"role": "assistant", "content": ans_b, "model_name": model_b}
        )

    yield "", new_history, build_full_markdown(new_history)

# Clear history
def clear_history_fn(cur_model: str, lang_code: str):
    return "", [get_system_prompt(cur_model, lang_code, False)], LANG[lang_code]["empty_history"]


# Lang menu frame and GUI
# Convert chat history into Markdown format
# with numbered questions and model-labelled answers.

with gr.Blocks(title="AI Chat with Code in Markdown") as demo:

    with gr.Row():
        lang_selector = gr.Radio(
            choices=["SV", "EN", "RU"],
            value="SV",
            label="Language",
            scale=3
        )

        version_label = gr.Markdown(
            f"<div style='text-align:right; opacity:0.6;'>v{APP_VERSION}</div>"
        )

    gr.Image(value="ai.gif", width=250, show_label=False, container=False)

    chat_title = gr.Markdown()
    chat_box = gr.Markdown()

    with gr.Row():
        deep_thinking_box = gr.Checkbox(label="Deep Thinking", value=False, visible=False)
        
        print("STEP 1: requesting model list from Ollama")
        models = ["None"] + get_installed_models()
        default_model = models[1] if len(models) > 1 else "None"
        print("STEP 2: models detected:", models)

        model_a = gr.Dropdown(
            choices=models,
            value=models[1],
            label=LANG["SV"]["model_a"]
        )

        model_b = gr.Dropdown(
            choices=models,
            value="None",
            label=LANG["SV"]["model_b"]
        )
        clear_btn = gr.Button()

    msg = gr.Textbox(lines=4, placeholder=LANG["SV"]["placeholder"])
    send_btn = gr.Button(value=LANG["SV"]["send_btn"])
    state = gr.State([])

    def update_ui_lang(lang):
        labels = LANG[lang]
        return (
            gr.update(value=labels["chat_title"]),
            gr.update(label=labels["deep_thinking"]),
            gr.update(label=labels["model_a"]),
            gr.update(label=labels["model_b"]),
            gr.update(value=labels["clear_btn"]),
            gr.update(placeholder=labels["placeholder"]),
            gr.update(value=labels["send_btn"])
        )

    # Update checkbox visibility when the selected model changes
    def update_deep_thinking_visibility(model_name: str, lang_code: str):    
        supports_deep = model_name in DEEP_THINKING_MODELS            
        labels = LANG[lang_code]
        
        return gr.update(
            visible=supports_deep,
            value=supports_deep,
            label=labels["deep_thinking"]
        )

    lang_selector.change(
        fn=update_ui_lang,
        inputs=lang_selector,
        outputs=[chat_title, deep_thinking_box, model_a, model_b, clear_btn, msg, send_btn]
    )

    # Add handler for model change
    model_a.change(
        fn=update_deep_thinking_visibility,
        inputs=[model_a, lang_selector],
        outputs=deep_thinking_box
    )

    def on_load_ui(lang: str, cur_model: str):
        labels = LANG[lang]
        if not cur_model or cur_model not in models:
            cur_model = models[0]
        supports_deep = cur_model in DEEP_THINKING_MODELS
        return (
            gr.update(value=labels["chat_title"]),
            gr.update(
                label=labels["deep_thinking"],
                visible=supports_deep,
                value=supports_deep
            ),
            gr.update(label=labels["model_a"], value=cur_model),
            gr.update(label=labels["model_b"]),
            gr.update(value=labels["clear_btn"]),
            gr.update(placeholder=labels["placeholder"]),
            gr.update(value=labels["send_btn"]),
        )

    demo.load(
        fn=on_load_ui,
        inputs=[lang_selector, model_a],
        outputs=[chat_title, deep_thinking_box, model_a, model_b, clear_btn, msg, send_btn]
    )

    # Event handlers for UI actions: buttons and text input
    send_btn.click(
        fn=chat_fn,
        inputs=[msg, state, model_a, model_b, deep_thinking_box, lang_selector],
        outputs=[msg, state, chat_box]
    )
    
    msg.submit(
        fn=chat_fn,
        inputs=[msg, state, model_a, model_b, deep_thinking_box, lang_selector],
        outputs=[msg, state, chat_box]
    )
    
    clear_btn.click(
        fn=clear_history_fn,
        inputs=[model_a, lang_selector],
        outputs=[msg, state, chat_box]
    )


# Local server IP and launch

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
demo.launch(
    theme=gr.themes.Origin(),
    server_name="0.0.0.0",
    server_port=port
)
print("GRADIO: server closed")

# Optional Gradio themes:
    #gr.themes.Default()
    #gr.themes.Base()
    #gr.themes.Origin()
    #gr.themes.Monochrome()
    #gr.themes.Soft()
    #gr.themes.Glass()
