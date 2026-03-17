# Changelog

All notable changes to this project will be documented in this file.

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
