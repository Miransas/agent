import logging
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, HTTPException, UploadFile
from httpx import ConnectError, TimeoutException

from app.core.types import ChatRequest, ChatResponse, VoiceResponse
from app.llm import client as llm_client
from app.llm.prompts import VOICE_SYSTEM_PROMPT
from app.voice import stt

log = logging.getLogger("miralas.agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    stt.warmup()
    yield


app = FastAPI(
    title="Miransas Voice Agent Core",
    version="0.2.0",
    lifespan=lifespan,
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def generate_voice_response(request: ChatRequest) -> ChatResponse:
    reply = await _ask_llm(request.prompt)
    return ChatResponse(status="success", response=reply)


@app.post("/api/voice", response_model=VoiceResponse)
async def voice_chat(audio: Annotated[UploadFile, File(...)]) -> VoiceResponse:
    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail="Bos ses dosyasi")

    transcript = await stt.transcribe(data)
    if not transcript:
        return VoiceResponse(status="success", transcript="", response="")

    reply = await _ask_llm(transcript)
    return VoiceResponse(status="success", transcript=transcript, response=reply)


async def _ask_llm(user_message: str) -> str:
    try:
        return await llm_client.generate(
            user_message=user_message,
            system_prompt=VOICE_SYSTEM_PROMPT,
        )
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
