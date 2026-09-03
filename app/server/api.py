import base64
import json
import logging
import os
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from httpx import ConnectError, TimeoutException
from starlette.staticfiles import StaticFiles

from app.core import agent
from app.core.types import ChatRequest, ChatResponse, VoiceResponse
from app.llm.prompts import VOICE_SYSTEM_PROMPT
from app.memory.store import store
from app.voice import stt

log = logging.getLogger("miralas.agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    stt.warmup()
    os.makedirs("static/audio", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    yield


app = FastAPI(
    title="Miransas Voice Agent Core",
    version="0.5.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def generate_voice_response(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or store.new_session_id()
    reply = await _run_agent(request.prompt, session_id)
    return ChatResponse(status="success", response=reply, session_id=session_id)


@app.post("/api/chat/stream")
async def stream_chat(request: ChatRequest):
    """SSE ile streaming text response."""
    session_id = request.session_id or store.new_session_id()

    async def event_generator():
        history = store.get(session_id)
        messages = [
            {"role": "system", "content": VOICE_SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": request.prompt},
        ]

        async for event in agent.run_stream(messages, session_id=session_id):
            if event["type"] == "token":
                yield f"data: {json.dumps({'token': event['content']})}\n\n"
            elif event["type"] == "done":
                store.add(session_id, "user", request.prompt)
                store.add(session_id, "assistant", event["full_response"])
                yield f"data: {json.dumps({'done': True, 'session_id': session_id})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.post("/api/voice", response_model=VoiceResponse)
async def voice_chat(
    audio: Annotated[UploadFile, File(...)],
    session_id: Annotated[str | None, Form()] = None,
) -> VoiceResponse:
    from app.voice import tts

    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail="Bos ses dosyasi")

    sid = session_id or store.new_session_id()
    transcript = await stt.transcribe(data)
    if not transcript:
        return VoiceResponse(
            status="success", transcript="", response="", session_id=sid, audio_url=None
        )

    reply = await _run_agent(transcript, sid)

    # TTS: text → audio
    audio_bytes = await tts.synthesize(reply, language="tr")
    filename = f"{uuid.uuid4().hex[:8]}.mp3"
    filepath = f"static/audio/{filename}"
    with open(filepath, "wb") as f:
        f.write(audio_bytes)

    audio_url = f"/static/audio/{filename}"
    return VoiceResponse(
        status="success", transcript=transcript, response=reply, session_id=sid, audio_url=audio_url
    )


@app.post("/api/voice/stream")
async def voice_chat_stream(
    audio: Annotated[UploadFile, File(...)],
    session_id: Annotated[str | None, Form()] = None,
):
    """Voice-to-voice streaming: audio → STT → agent → TTS → audio chunks (SSE)."""
    from app.voice import tts

    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail="Bos ses dosyasi")

    sid = session_id or store.new_session_id()
    transcript = await stt.transcribe(data)
    if not transcript:

        async def empty_stream():
            yield f"data: {json.dumps({'error': 'transcript_bos'})}\n\n"

        return StreamingResponse(empty_stream(), media_type="text/event-stream")

    async def event_generator():
        history = store.get(sid)
        messages = [
            {"role": "system", "content": VOICE_SYSTEM_PROMPT},
            *history,
            {"role": "user", "content": transcript},
        ]

        full_response = ""
        sentence_buffer = ""

        async for event in agent.run_stream(messages, session_id=sid):
            if event["type"] == "token":
                sentence_buffer += event["content"]

                # Cümle bitti mi? (nokta, soru işareti, ünlem)
                if any(
                    sentence_buffer.rstrip().endswith(p) for p in [".", "?", "!", "。", "？", "！"]
                ):
                    # Cümleyi TTS'e gönder, audio stream et
                    async for audio_chunk in tts.synthesize_stream(sentence_buffer, language="tr"):
                        audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                        yield f"data: {json.dumps({'audio': audio_b64})}\n\n"

                    full_response += sentence_buffer
                    sentence_buffer = ""

            elif event["type"] == "done":
                # Son cümle varsa (noktasız bitmiş)
                if sentence_buffer.strip():
                    async for audio_chunk in tts.synthesize_stream(sentence_buffer, language="tr"):
                        audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                        yield f"data: {json.dumps({'audio': audio_b64})}\n\n"
                    full_response += sentence_buffer

                # Session'a kaydet
                store.add(sid, "user", transcript)
                store.add(sid, "assistant", full_response)
                yield f"data: {json.dumps({'done': True, 'session_id': sid, 'transcript': transcript, 'response': full_response})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str) -> dict[str, str]:
    store.clear(session_id)
    return {"status": "cleared", "session_id": session_id}


async def _run_agent(user_message: str, session_id: str) -> str:
    history = store.get(session_id)
    messages = [
        {"role": "system", "content": VOICE_SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": user_message},
    ]
    try:
        reply, _full_history = await agent.run(messages, session_id=session_id)
    except ConnectError as exc:
        log.error("LLM server unreachable: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="LLM sunucusuna ulasilamadi. `ollama serve` calisiyor mu?",
        ) from exc
    except TimeoutException as exc:
        log.error("LLM timeout: %s", exc)
        raise HTTPException(status_code=504, detail="LLM zaman asimi.") from exc
    except Exception as exc:
        log.exception("Agent run failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    store.add(session_id, "user", user_message)
    store.add(session_id, "assistant", reply)

    return reply
