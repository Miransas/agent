import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from httpx import ConnectError, TimeoutException

from app.core import agent
from app.core.types import ChatRequest, ChatResponse, VoiceResponse
from app.llm.prompts import VOICE_SYSTEM_PROMPT
from app.memory.store import store
from app.voice import stt

log = logging.getLogger("miralas.agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    stt.warmup()
    yield


app = FastAPI(
    title="Miransas Voice Agent Core",
    version="0.4.0",
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

    reply = await _run_agent(transcript, sid)
    return VoiceResponse(status="success", transcript=transcript, response=reply, session_id=sid)


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

    # Sadece user + assistant mesajlarini session'a kaydet
    store.add(session_id, "user", user_message)
    store.add(session_id, "assistant", reply)

    return reply
