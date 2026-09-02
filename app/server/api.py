import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from httpx import ConnectError, TimeoutException

from app.core.types import ChatRequest, ChatResponse, VoiceResponse
from app.llm import client as llm_client
from app.llm.prompts import VOICE_SYSTEM_PROMPT
from app.memory.store import store
from app.voice import stt

log = logging.getLogger("miralas.agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    stt.warmup()  # Whisper'i arka planda yukle
    yield


app = FastAPI(
    title="Miransas Voice Agent Core",
    version="0.3.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def generate_voice_response(request: ChatRequest) -> ChatResponse:
    session_id = request.session_id or store.new_session_id()
    reply = await _ask_llm(request.prompt, session_id)
    return ChatResponse(status="success", response=reply, session_id=session_id)


@app.post("/api/voice", response_model=VoiceResponse)
async def voice_chat(
    audio: Annotated[UploadFile, File(...)],
    session_id: Annotated[str | None, Form()] = None,
) -> VoiceResponse:
    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail="Bos ses dosyasi")

    sid = session_id or store.new_session_id()
    transcript = await stt.transcribe(data)
    if not transcript:
        return VoiceResponse(status="success", transcript="", response="", session_id=sid)

    reply = await _ask_llm(transcript, sid)
    return VoiceResponse(status="success", transcript=transcript, response=reply, session_id=sid)


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str) -> dict[str, str]:
    store.clear(session_id)
    return {"status": "cleared", "session_id": session_id}


async def _ask_llm(user_message: str, session_id: str) -> str:
    history = store.get(session_id)
    messages = [
        {"role": "system", "content": VOICE_SYSTEM_PROMPT},
        *history,
        {"role": "user", "content": user_message},
    ]
    try:
        reply = await llm_client.generate(messages)
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
        log.exception("LLM call failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    store.add(session_id, "user", user_message)
    store.add(session_id, "assistant", reply)
    return reply
