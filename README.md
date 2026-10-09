# AI Agent

A local AI assistant powered by [Ollama](https://ollama.com/), running entirely on your own machine — no API keys, no cloud, no cost.

## Features

- 🖥️ 100% local inference via Ollama
- ⚡ Streaming responses (tokens appear as they're generated)
- 🧠 Conversation memory (remembers the whole session)
- 🛑 Clean exit with `/quit`

## Requirements

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running
- A model pulled locally, e.g.:
  ```bash
  ollama pull qwen2.5:3b
