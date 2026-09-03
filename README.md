# Miransas Voice Agent

Self-hosted voice AI agent for businesses — answers calls, takes orders,
books appointments. LLaMA-3.1 8B (Ollama) + faster-whisper STT.
Part of the Miralas ecosystem (own TTS & voice-clone models, native Uzbek/Turkish).

## Run

    # one-time
    brew install ollama ffmpeg
    ollama pull llama3.1:8b

    # terminal 1
    ollama serve

    # terminal 2
    uv sync
    uv run uvicorn app.server.api:app --reload --port 8000

## Try

    curl -s localhost:8000/health

    curl -s -X POST localhost:8000/api/chat \
      -H 'Content-Type: application/json' \
      -d '{"prompt":"Menünüzde neler var?"}'

    curl -s -X POST localhost:8000/api/voice -F "audio=@test.wav"

## What works

- text chat + voice input (STT)
- conversation memory (sessions)
- tool calling: menu, cart, orders, appointments

## Coming soon

TTS output, streaming, phone integration, Redis memory.
