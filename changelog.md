# Changelog
All notable changes to this project will be documented in this file.

---

## [2.7.0] - 2026-06-08

### Added

- Session save and restore

- Chat export to Markdown (.md)

- Chat save/load in JSON format

- Persistent application configuration

- External CSS theme support

- External JavaScript support

- Runtime theme selection

- Status bar and loading indicators

- Floating navigation controls

- Improved code block rendering

- Markdown-aware code formatting prompts

- Ollama error reporting in UI

- Automatic Ollama startup attempt

- Isolated A/B conversation architecture

### Changed

- Replaced linear chat history with turn-based storage

- Reworked model comparison workflow

- Reorganized project structure

- Moved CSS and JavaScript into external files

- Improved session persistence

- Updated multilingual interface

- Updated application layout

### Fixed

- Duplicate model selection handling

- Configuration fallback logic

- Session loading edge cases

- Interrupted response recovery

- Ollama connection error handling

- Markdown rendering consistency

### Notes

Version 2.7.0 is a major update compared to version 2.2.0.

The project now includes persistent sessions, chat export, save/load functionality, configurable themes, external UI resources, and a redesigned A/B model comparison architecture.

---

## [v2.2.0] - 2026-03-17

### Added

* Manual **Streaming toggle** (ON/OFF) in UI
* Streaming is now **disabled by default**
* Ability to switch between:

  * streaming responses (token-by-token)
  * full responses (non-streaming)

### Changed

* Chat logic updated to support dual mode:

  * `stream=True` (streaming)
  * `stream=False` (standard response)
* Event handlers updated to pass streaming state into `chat_fn`
* UI layout updated with new checkbox control

### Fixed

* Incorrect execution flow for Model B (indentation issue)
* Duplicate event handlers removed
* Initialization order issues in Gradio components

### Notes

* This version improves compatibility with mobile browsers
* Non-streaming mode provides more stable rendering on slow clients

---

## [v2.1.1] - 2026-03-16

### Added

* Version label displayed in UI header
* Improved UI layout with language selector and version info

### Features

* Multi-model chat (Model A / Model B)
* Streaming responses (default behavior)
* Markdown-based chat rendering
* Deep Thinking toggle (model-specific)
* Multi-language interface (EN / SV / RU)

### Technical

* System prompt architecture with:

  * base prompt
  * optional model patches
  * deep thinking extension
* Modular chat pipeline:

  * history handling
  * streaming renderer
  * markdown builder

---

## [v2.0.x] (baseline)

### Initial architecture

* Ollama + Gradio integration
* Streaming response rendering
* Basic chat history
* Markdown output
* Multi-model comparison (A/B)

---

## Versioning

Format:
vMAJOR.MINOR.PATCH

* MAJOR - breaking changes
* MINOR - new features
* PATCH - fixes and small improvements

---
