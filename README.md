# Miransas Voice Agent

Miransas is a self-hosted voice AI backend for businesses. It handles natural
conversation, voice input, orders, appointments, and session memory through a
FastAPI service powered by Ollama and LLaMA 3.1 8B. The system is designed for
Turkish and Uzbek voice experiences, with a native Rust core for fast HTTP,
streaming, and session operations.

## Run Locally

Requirements: Python 3.12+, `uv`, Rust, Ollama, and FFmpeg.

```bash
brew install ollama ffmpeg
ollama pull llama3.1:8b
ollama serve
```

In a second terminal:

```bash
uv sync
uv run uvicorn app.server.api:app --reload --port 8000
```

The API is available at `http://localhost:8000`. Check it with:

```bash
curl localhost:8000/health
curl -X POST localhost:8000/api/chat \
  -H 'Content-Type: application/json' \
  -d '{"prompt":"What is on your menu?"}'
curl -X POST localhost:8000/api/voice -F "audio=@test.wav"
```

## Rust Optimization

The Rust crate (`rust/`) provides the performance-sensitive core through
PyO3. Build its optimized release profile with:

```bash
cargo build --manifest-path rust/Cargo.toml --release
```

Release builds use maximum compiler optimization (`opt-level = 3`) and link-time
optimization (`lto = true`). Use this build for production workloads; use the
default debug build while developing.

## Core Capabilities

- Text chat, streaming responses, and voice conversations
- Faster-Whisper speech-to-text and Edge TTS audio responses
- Session-based conversation memory
- Business tools for menus, carts, orders, and appointments
