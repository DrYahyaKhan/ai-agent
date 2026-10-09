# DrYahyaKhan / ai-agent

**Latest commit:** `167d802 · Stop tracking workspace folder · 1 minute ago`  
**Total commits:** 6

## Files

| File / Folder      | Last commit message                                       | Pushed         |
|--------------------|-----------------------------------------------------------|----------------|
| `.gitignore`       | Initial commit                                            | 8 hours ago    |
| `.python-version`  | Initial commit                                            | 8 hours ago    |
| `README.md`        | Initialize README with project details                    | 5 hours ago    |
| `pyproject.toml`   | Working assistant: qwen2.5:3b with streaming output       | 6 hours ago    |
| `uv.lock`          | Working assistant: qwen2.5:3b with streaming output       | 6 hours ago    |
| `v0.py`            | Add conversation memory and /quit command                 | 5 hours ago    |
| `v1.py`            | Add v1 and v2 agents                                      | 8 minutes ago  |
| `v2.py`            | Add v1 and v2 agents                                      | 8 minutes ago  |

## What each file does

### `v0.py` — Chatbot with memory
A streaming chatbot using Ollama's OpenAI-compatible endpoint.
- Streams tokens as they arrive
- Keeps conversation history between turns
- Supports `/quit` command

### `v1.py` — Simple tool-calling agent
An agent that can call tools to interact with the local filesystem.
- Tools: `list_files()`, `read_file(filename)`
- Single tool call per turn
- Uses OpenAI tool schema

### `v2.py` — Bounded-loop agent (current best)
An improved agent that chains multiple tool calls in one turn.
- Same tools as v1
- `MAX_STEPS = 5` cap to prevent infinite loops
- Tool errors are caught and returned to the model
- Graceful fallback if the step limit is reached

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- A model pulled locally: `ollama pull qwen2.5:3b`
- Optional, for better tool-calling: `ollama pull qwen2.5:7b`

## Setup

