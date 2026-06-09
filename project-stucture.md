Project Structure

```text
ollama-gradio-chat/

├── aichat.py
├── README.md
├── changelog.md
├── req.txt
│
├── img/
│   Project screenshots
│
├── sys/
│   ├── script.js
│   ├── base.css
│   └── themes/
│
├── config.json              [created during runtime]
│
├── chats/                   [created during runtime]
│   └── current/
│       └── session.json
│
└── exports/                 [created during runtime]
```

Notes

Static files included in the repository:

* aichat.py
* sys/
* img/
* README.md
* changelog.md
* req.txt

Created automatically during runtime:

* config.json

  * Created when application settings are saved.

* chats/

  * Created when a chat is saved.

* chats/current/session.json

  * Stores the current session.
  * Used for automatic session restore after restart.

* exports/

  * Created when exporting chat history to Markdown (.md).


## Session Storage

Saved chats are stored in:

```text id="92d8za"
chats/
```

Each saved conversation is stored as a JSON file.

Default filename format:

```text id="vyz3bo"
_YYYY-MM-DD_HHMMSS.json
```

Example:

```text id="t7cnq4"
_2026-06-09_214530.json
```

The application intentionally saves chats using a neutral timestamp-based filename.

This format allows users to manually add a descriptive name before the timestamp if desired.

Examples:

```text id="9s79b9"
Qwen_Test_2026-06-09_214530.json

JavaScript_Project_2026-06-09_214530.json

Cogito_vs_Gemma_2026-06-09_214530.json
```

Renaming is performed manually using the operating system file manager.

The application does not modify existing filenames after saving.

Current automatic session storage:

```text id="m68y7d"
chats/current/session.json
```

This file contains the currently active chat session.

The application automatically updates this file during operation and attempts to restore it on startup.

Deleting `session.json` resets the current session without affecting any saved chats stored in the `chats/` directory.
