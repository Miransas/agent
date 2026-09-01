# Miransas Voice Agent

A lightweight, low-latency voice AI backend for the Miransas ecosystem. This project exposes a simple API that sends a prompt to a local Llama model through Ollama and returns a short, natural spoken-style response suitable for voice conversations.

The current implementation is intentionally minimal and focused on a fast local-first agent flow. It is designed to be easy to extend for real-world voice assistant scenarios, including conversational UX, agent prompts, and external service integration.

---

## Overview

This repository contains the core backend for a voice agent that:

- accepts a user prompt from an HTTP endpoint
- prepends a system prompt tuned for natural voice interaction
- sends the request to a local Ollama model
- returns the generated text as a JSON response

The backend currently runs as a FastAPI service and is designed to work with the Llama 3.1 8B model.

---

## Tech Stack

- AI model: Llama 3.1 8B via Ollama
- Backend: Python + FastAPI
- Runtime / dependency management: uv
- HTTP client: requests
- Validation: Pydantic

---

## Prerequisites

Before starting, make sure you have the following installed on your machine:

- [Ollama](https://ollama.com/)
- [uv](https://github.com/astral-sh/uv)

Then start Ollama and pull the model used by this project:

```bash
ollama serve
ollama pull llama3.1:8b
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/Miransas/agent.git
cd agent
```

### 2. Install dependencies

The project dependencies are listed in the backend requirements file.

```bash
cd backend
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 3. Start the API server

```bash
uv run python main.py
```

The server will run at:

```text
http://127.0.0.1:8000
```

---

## API Endpoint

### POST /api/chat

Request body:

```json
{
  "prompt": "Hello, tell me about the Miralas ecosystem."
}
```

Example call:

```bash
curl -X POST "http://127.0.0.1:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, tell me about the Miralas ecosystem."}'
```

Example response:

```json
{
  "status": "success",
  "response": "...agent reply..."
}
```

---

## Project Structure

```text
agent/
├── backend/
│   ├── main.py
│   ├── prompt.py
│   └── requirements.txt
├── .container/
├── .github/
├── hooks/
├── scripts/
├── AGENTS.md
├── CLAUDE.md
├── LICENSE
├── README.md
└── .gitignore
```

### Key files

- `backend/main.py`: FastAPI application and Ollama request flow
- `backend/prompt.py`: voice system prompt used to guide the assistant tone and style
- `backend/requirements.txt`: Python dependencies

---

## Voice Prompt Behavior

The assistant is configured to behave like a short, natural voice interaction partner:

- concise replies
- conversational tone
- no bullet lists
- no code blocks or long explanations
- single-paragraph responses that feel like spoken dialogue

This behavior is controlled via the system prompt in `backend/prompt.py`.

---

## Notes

- This project is intentionally local-first and is designed to work with a running Ollama instance.
- The current endpoint is a minimal backend layer and can be extended for TTS, STT, conversation memory, tool calls, or integration with downstream services.
- The `.container` folder is currently reserved for container-related assets and can be used for Docker or devcontainer setup in future iterations.

---

## License

This project is released under the MIT License.

---

Built with passion by the Miransas team.