# Local AI Chat (Ollama + Gradio) ollama-gradio-chat

Lightweight local AI chat interface for experimenting with multiple Ollama models.

This project provides a simple web interface that allows you to interact with local LLMs, compare responses from different models, and display answers in structured Markdown format.

The interface is designed as a local AI laboratory for testing models and prompts.

## Features

- Runs completely locally
- Uses Ollama as the model backend
- Web interface built with Gradio
- Supports multiple models simultaneously
- Model A / Model B comparison
- Streaming responses
- Markdown rendering
- Numbered questions
- Model-labelled answers
- Optional Deep Thinking mode
- Multi-language interface:   English, Swedish, Russian

## Screenshot

Example interface:

Ollama + Gradio Local AI Lab

(Interface shows numbered questions and answers from multiple models.)

## Requirements

You must install:
- Ollama (local LLM runtime)
- Python (Gradio and other libraries will be installed later using pip)

### 1 Install Ollama

Download Ollama from: https://ollama.ai
>Minimum system requirements:
>- CPU: performance comparable to Intel i5-8400 or higher [9000+ PassMark](https://www.cpubenchmark.net/cpu.php?cpu=Intel+Core+i5-8400+%40+2.80GHz&id=3097)
>- RAM: 16 GB min (32-128 GB recommended)
>- GPU: NVIDIA GTX1660 6 GB or better (e.g. RTX 3060 12 GB)
>- OS: Windows, Linux or macOS
>  
>Note:
>- The application can run on CPU only, but performance may be slow.
>- GPU significantly improves response time (if supported by Ollama).
>- Larger models (14B+) require more RAM and VRAM.

### 2 Install models

Example models:
```
ollama pull cogito:14b
ollama pull qwen3.5:9b
ollama pull gemma3n:e4b-it-fp16
ollama pull ministral-3:14b
```
The example models above are only suggestions. You can use any models available in the Ollama library:
[https://ollama.com/search?o=newest](https://ollama.com/search?o=newest)

After installation verify in terminal:
```
ollama list
```
For testing and comparison it is recommended to install at least two models.<br>
The interface supports switching between models, so having multiple models allows you to compare responses and behavior directly. Installed models also will automatically appear in the interface.

### 3 Install Python packages

Install dependencies:
```
pip install gradio ollama
```

Or using requirements file:
```bash
pip install -r requirements.txt
```

### 4 Run the application

Start the server: ```python chat.py```

Console output will show something like:
```
STEP 1: requesting model list from Ollama
STEP 2: models detected: ['None', 'qwen3.5:9b', 'ministral-3:14b', 'qwen3.5:27b', 'gemma3n:e4b-it-fp16', 'cogito:14b']
STEP 3: detecting local IP
STEP 4: local IP detected: 192.168.10.15
Local server: http://127.0.0.1:7860/?__theme=dark
LAN access:  http://192.168.10.15:7860/?__theme=dark
STEP 5: starting Gradio server. ⬆ Use local or LAN IP ⬆
AI Chat version: v2.1.1 build 20260316
* Running on local URL:  http://0.0.0.0:7860
* To create a public link, set `share=True` in `launch()`.
```

Open the link in your browser with Ctrl+ LMB

## Interface overview

The interface allows:
- selecting language
- selecting Model A
- selecting Model B
- enabling Deep Thinking
- asking questions

Each question is numbered:
```
 #1
 #2
 #3
```
Each answer is labelled with the model name. Example:
```
### cogito:14b
response text

### qwen3.5:27b
response text
```

### Deep Thinking mode

> Some models support an optional Deep Thinking mode.
When enabled the system prompt includes an additional instruction that encourages deeper reasoning.

Currently enabled for:
```
cogito:14b
```

## Architecture

Main components:
```
chat.py
```

Core parts:
- Ollama streaming API
- Markdown rendering
- Gradio UI
- multi-model response comparison

### Use cases

This interface can be used for:
- local LLM experimentation
- prompt testing
- model comparison
- multilingual interaction
- code generation testing

## Custom UI animation

The interface uses a GIF animation displayed at the top.

The file must be placed in the same directory as `chat.py`: ai.gif

You can replace `ai.gif` with your own animation.

If the file is missing, the image will not be displayed.

### Current version:

v2.1.1 build 20260316


### License

MIT License
