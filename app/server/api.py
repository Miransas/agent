import asyncio
import base64
import json
import logging
import os
import time
import uuid
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from httpx import ConnectError, TimeoutException
from starlette.staticfiles import StaticFiles

from app.config.logging_config import setup_logging
from app.config.settings import settings
from app.core import agent
from app.core.types import ChatRequest, ChatResponse, VoiceResponse
from app.llm import client as llm_client
from app.llm.prompts import get_system_prompt
from app.memory.store import start_cleanup_task, store

from app.voice import stt


setup_logging()

log = logging.getLogger("miralas.agent")


AUDIO_DIR = "static/audio"


@asynccontextmanager
async def lifespan(app: FastAPI):
    stt.warmup()
    os.makedirs(AUDIO_DIR, exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    background_tasks = [
        asyncio.create_task(_warmup_llm()),
        asyncio.create_task(_warmup_tts()),
        asyncio.create_task(start_cleanup_task()),
        asyncio.create_task(_audio_cleanup_task()),
    ]
    yield
    for t in background_tasks:
        t.cancel()


async def _warmup_llm():
    """Ollama'ya bos istek atar, ilk gercek istek soguk baslangic gecikmesi yemesin."""
    try:
        await llm_client.generate([{"role": "user", "content": "merhaba"}], tools=None)
        log.info("LLM warmed up")
    except Exception as exc:
        log.warning("LLM warmup failed: %s", exc)


async def _warmup_tts():
    from app.voice import tts

    try:
        await tts.synthesize(" ", language="tr")
        log.info("TTS warmed up")
    except Exception as exc:
        log.warning("TTS warmup failed: %s", exc)


async def _audio_cleanup_task(interval_seconds: int = 900) -> None:
    while True:
        await asyncio.sleep(interval_seconds)
        removed = await asyncio.to_thread(_remove_old_audio_files)
        if removed:
            log.info("Audio cleanup: %d eski dosya silindi", removed)


def _remove_old_audio_files() -> int:
    now = time.time()
    removed = 0
    for name in os.listdir(AUDIO_DIR):
        path = os.path.join(AUDIO_DIR, name)
        try:
            if now - os.path.getmtime(path) > settings.audio_retention_seconds:
                os.remove(path)
                removed += 1
        except OSError:
            continue
    return removed


app = FastAPI(title="Miransas Voice Agent Core", version="0.7.0", lifespan=lifespan)


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
    session_id = request.session_id or store.new_session_id()

    async def event_generator():
        try:
            history = store.get(session_id)
            messages = [
                {"role": "system", "content": get_system_prompt("tr")},
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
        except Exception as exc:
            log.exception("Chat stream failed")
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


def _check_upload_size(data: bytes) -> None:
    if len(data) > settings.max_upload_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Ses dosyasi cok buyuk (limit: {settings.max_upload_bytes // (1024 * 1024)}MB)",
        )


def _write_file(path: str, data: bytes) -> None:
    with open(path, "wb") as f:
        f.write(data)


@app.post("/api/voice", response_model=VoiceResponse)
async def voice_chat(
    audio: Annotated[UploadFile, File(...)],
    session_id: Annotated[str | None, Form()] = None,
) -> VoiceResponse:
    from app.voice import tts

    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail="Bos ses dosyasi")
    _check_upload_size(data)

    sid = session_id or store.new_session_id()
    request_start = time.monotonic()
    transcript, detected_lang = await stt.transcribe(data)
    log.info("STT: %.2fs lang=%s", time.monotonic() - request_start, detected_lang)
    if not transcript:
        return VoiceResponse(status="success", transcript="", response="", session_id=sid, audio_url=None)

    reply = await _run_agent(transcript, sid, detected_lang=detected_lang)

    tts_lang = _resolve_tts_lang(detected_lang)
    audio_bytes = await tts.synthesize(reply, language=tts_lang)
    filename = f"{uuid.uuid4().hex[:8]}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)
    await asyncio.to_thread(_write_file, filepath, audio_bytes)

    return VoiceResponse(
        status="success", transcript=transcript, response=reply,
        session_id=sid, audio_url=f"/static/audio/{filename}",
    )


@app.post("/api/voice/stream")
async def voice_chat_stream(
    audio: Annotated[UploadFile, File(...)],
    session_id: Annotated[str | None, Form()] = None,
):
    from app.voice import tts

    data = await audio.read()
    if not data:
        raise HTTPException(status_code=400, detail="Bos ses dosyasi")
    _check_upload_size(data)

    sid = session_id or store.new_session_id()
    request_start = time.monotonic()
    transcript, detected_lang = await stt.transcribe(data)
    log.info("STT: %.2fs lang=%s", time.monotonic() - request_start, detected_lang)

    if not transcript:
        async def empty_stream():
            yield f"data: {json.dumps({'error': 'transcript_bos'})}\n\n"
        return StreamingResponse(empty_stream(), media_type="text/event-stream")

    tts_lang = _resolve_tts_lang(detected_lang)

    async def event_generator():
        try:
            history = store.get(sid)
            messages = [
                {"role": "system", "content": get_system_prompt(detected_lang)},
                *history,
                {"role": "user", "content": transcript},
            ]

            full_response = ""
            sentence_buffer = ""
            first_token_logged = False
            first_audio_logged = False

            if agent.needs_tool_call(transcript):
                filler_text = FILLER.get(tts_lang, FILLER["tr"])
                async for chunk in tts.synthesize_stream(filler_text, language=tts_lang):
                    yield f"data: {json.dumps({'audio': base64.b64encode(chunk).decode()})}\n\n"
                log.debug("Filler sent: %s", filler_text)

            async for event in agent.run_stream(messages, session_id=sid, detected_lang=detected_lang):
                if event["type"] == "token":
                    if not first_token_logged:
                        log.info("First token: %.2fs", time.monotonic() - request_start)
                        first_token_logged = True
                    sentence_buffer += event["content"]

                    if _should_flush_sentence(sentence_buffer):
                        async for chunk in tts.synthesize_stream(sentence_buffer, language=tts_lang):
                            if not first_audio_logged:
                                log.info("First audio chunk: %.2fs", time.monotonic() - request_start)
                                first_audio_logged = True
                            yield f"data: {json.dumps({'audio': base64.b64encode(chunk).decode()})}\n\n"
                        full_response += sentence_buffer
                        sentence_buffer = ""

                elif event["type"] == "done":
                    if sentence_buffer.strip():
                        async for chunk in tts.synthesize_stream(sentence_buffer, language=tts_lang):
                            yield f"data: {json.dumps({'audio': base64.b64encode(chunk).decode()})}\n\n"
                        full_response += sentence_buffer

                    store.add(sid, "user", transcript)
                    store.add(sid, "assistant", full_response)
                    yield f"data: {json.dumps({'done': True, 'session_id': sid, 'transcript': transcript, 'response': full_response})}\n\n"
        except Exception as exc:
            log.exception("Voice stream failed")
            yield f"data: {json.dumps({'error': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str) -> dict[str, str]:
    store.clear(session_id)
    return {"status": "cleared", "session_id": session_id}


def _should_flush_sentence(buffer: str) -> bool:
    text = buffer.strip()
    if not text:
        return False
    word_count = len(text.split())
    if any(text.endswith(p) for p in [".", "?", "!", "。", "？", "！"]):
        return True
    if text.endswith(",") and word_count >= 4:
        return True
    if text.endswith(":") and word_count >= 3:
        return True
    return word_count >= 6


FILLER = {
    "tr": "Hımm, bir bakayım.",
    "en": "Hmm, let me see.",
    "uz": "Hmm, ko'rib turaman.",
    "ru": "Хм, сейчас посмотрю.",
}


def _resolve_tts_lang(detected_lang: str) -> str:
    supported = {"tr", "en", "uz", "ru"}
    return detected_lang if detected_lang in supported else "tr"


async def _run_agent(user_message: str, session_id: str, detected_lang: str = "tr") -> str:
    history = store.get(session_id)
    messages = [
        {"role": "system", "content": get_system_prompt(detected_lang)},
        *history,
        {"role": "user", "content": user_message},
    ]
    try:
        reply, _ = await agent.run(messages, session_id=session_id, detected_lang=detected_lang)
    except ConnectError as exc:
        log.error("LLM server unreachable: %s", exc)
        raise HTTPException(status_code=503, detail="LLM sunucusuna ulasilamadi. `ollama serve` calisiyor mu?") from exc
    except TimeoutException as exc:
        log.error("LLM timeout: %s", exc)
        raise HTTPException(status_code=504, detail="LLM zaman asimi.") from exc
    except Exception as exc:
        log.exception("Agent run failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    store.add(session_id, "user", user_message)
    store.add(session_id, "assistant", reply)
    return reply