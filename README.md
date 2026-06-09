# Local AI Chat (Ollama + Gradio)

**ollama-gradio-chat** is a lightweight AI chat interface for experimenting with local and cloud-based language models.

The application provides a Gradio web interface with model comparison, session management, Markdown export, configurable themes, and support for multiple languages.

It can be used as a local AI laboratory for testing models, prompts, and workflows.



## Features

* Local Ollama models
* Ollama cloud models
* A/B model comparison
* Session save and restore
* Chat save/load (.json)
* Markdown export (.md)
* Streaming and non-streaming modes
* Markdown rendering
* Syntax-highlighted code blocks
* External CSS themes
* Custom JavaScript enhancements
* Multi-language interface (EN / SV / RU)
* Persistent configuration
* Error reporting inside UI


## Quick Start

1. Install Ollama
2. Pull one or more models
3. Create virtual environment
4. Install dependencies
5. Run:

```bash
python aichat.py
```


## Installation

### 1. Clone repository

```bash
git clone https://github.com/Soviet9773Red/ollama-gradio-chat.git
cd ollama-gradio-chat
```

### 2. Create virtual environment

```bash
python -m venv .venv
```

Activate:

```bash
# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r req.txt
```

### 4. Install Ollama

Download:

https://ollama.com

Verify:

```bash
ollama --version
```

### 5. Install models

Example:

```bash
ollama pull qwen3:8b
ollama pull gemma3:12b
```

List installed models:

```bash
ollama list
```



## Running the Application

Start:

```bash
python aichat.py
```

Typical local address:

```text
http://127.0.0.1:7860
```

LAN access:

```text
http://YOUR_LOCAL_IP:7860
```


## System Requirements

### Local Models

Requirements depend on model size.

| Component | Recommended             |
| --------- | ----------------------- |
| CPU       | Intel i5-8400 or better |
| RAM       | 16 GB minimum           |
| RAM       | 32 GB+ recommended      |
| GPU       | GTX 1660 6 GB or better |
| OS        | Windows / Linux / macOS |

Notes:

* CPU-only operation is supported.
* Larger models require more RAM and VRAM.
* GPU acceleration significantly improves performance.

### Cloud Models

When using cloud-hosted models, hardware requirements are much lower.

| Component | Recommended              |
| --------- | ------------------------ |
| CPU       | Any modern dual-core CPU |
| RAM       | 4-8 GB                   |
| GPU       | Not required             |
| OS        | Windows / Linux / macOS  |

Notes:

* Model inference runs remotely.
* Local hardware mainly renders the web interface.
* Internet connection quality becomes more important than GPU performance.



## Project Structure

The project structure is documented separately:

```text
project-structure.txt
```



## Main Components

### aichat.py

Main application:

* Gradio interface
* Ollama integration
* Model comparison
* Session handling
* Theme management

### config.json

Persistent user settings.

### chats/

Stored chat sessions.

### exports/

Markdown exports.

### sys/

UI resources:

* CSS
* JavaScript
* Themes


## Supported Languages

* English
* Svenska
* Русский



## Use Cases

* Local LLM experimentation
* Prompt testing
* A/B model comparison
* Multilingual interaction
* Code generation
* Model evaluation



## GUI example

The screenshot below shows the main interface with model selection, session management, theme controls, and A/B comparison mode.

<img src="img/gui.jpg" width="656">

## Version

Current version:

```text
2.7.0
```

See: [changelog.md](hangelog.md) for release history.



## License

MIT License

(c) Alexander Soviet9773Red
