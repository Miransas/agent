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

from app.core import agent
from app.core.types import ChatRequest, ChatResponse, VoiceResponse
from app.llm.prompts import get_system_prompt
from app.memory.store import store
from app.voice import stt

log = logging.getLogger("miralas.agent")


@asynccontextmanager
async def lifespan(app: FastAPI):
    stt.warmup()
    os.makedirs("static/audio", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")
    # Warmup: TTS + LLM (ilk istek hızlı olsun)
    warmup_tasks = [
        asyncio.create_task(_warmup_tts()),
        asyncio.create_task(_warmup_tts()),
    ]
    yield
    for t in warmup_tasks:
        t.cancel()


async def _warmup_tts():
    """edge-tts'e boş request gönder, DNS + TLS handshake bir kerelik olsun."""
    from app.voice import tts

    try:
        await tts.synthesize(" ", language="tr")
        log.info("✅ TTS warmed up")
    except Exception as exc:
        log.warning("TTS warmup failed: %s", exc)


app = FastAPI(
    title="Miransas Voice Agent Core",
    version="0.6.0",
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
    session_id = request.session_id or store.new_session_id()

    async def event_generator():
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
    request_start = time.monotonic()
    transcript, detected_lang = await stt.transcribe(data)
    print(f"⏱️  STT: {time.monotonic() - request_start:.2f}s lang={detected_lang}")
    if not transcript:
        return VoiceResponse(
            status="success", transcript="", response="", session_id=sid, audio_url=None
        )

    reply = await _run_agent(transcript, sid, detected_lang=detected_lang)

    tts_lang = _resolve_tts_lang(detected_lang)
    audio_bytes = await tts.synthesize(reply, language=tts_lang)
    filename = f"{uuid.uuid4().hex[:8]}.mp3"
    filepath = f"static/audio/{filename}"
    with open(filepath, "wb") as f:
        f.write(audio_bytes)

    audio_url = f"/static/audio/{filename}"
    return VoiceResponse(
        status="success",
        transcript=transcript,
        response=reply,
        session_id=sid,
        audio_url=audio_url,
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

    sid = session_id or store.new_session_id()
    request_start = time.monotonic()
    transcript, detected_lang = await stt.transcribe(data)
    print(f"⏱️  STT: {time.monotonic() - request_start:.2f}s lang={detected_lang}")
    if not transcript:

        async def empty_stream():
            yield f"data: {json.dumps({'error': 'transcript_bos'})}\n\n"

        return StreamingResponse(empty_stream(), media_type="text/event-stream")

    tts_lang = _resolve_tts_lang(detected_lang)

    async def event_generator():
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

        # Tool gerektiren soruysa hemen "düşünme sesi" gönder (canlılık hissi)
        tool_keywords = ["menü", "menu", "sipariş", "sepet", "burger", "pizza", "cola", "randevu"]
        if any(kw in transcript.lower() for kw in tool_keywords):
            filler_text = FILLER.get(tts_lang, FILLER["tr"])
            async for audio_chunk in tts.synthesize_stream(filler_text, language=tts_lang):
                audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                yield f"data: {json.dumps({'audio': audio_b64})}\n\n"
            print(f"🗣️  Filler sent: {filler_text}", flush=True)

        async for event in agent.run_stream(messages, session_id=sid, detected_lang=detected_lang):
            if event["type"] == "token":
                if not first_token_logged:
                    print(f"⏱️  First token: {time.monotonic() - request_start:.2f}s")
                    first_token_logged = True
                sentence_buffer += event["content"]

                if _should_flush_sentence(sentence_buffer):
                    async for audio_chunk in tts.synthesize_stream(
                        sentence_buffer, language=tts_lang
                    ):
                        if not first_audio_logged:
                            log.info(
                                "⏱️  First audio chunk: %.2fs", time.monotonic() - request_start
                            )
                            first_audio_logged = True
                        audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                        yield f"data: {json.dumps({'audio': audio_b64})}\n\n"

                    full_response += sentence_buffer
                    sentence_buffer = ""

            elif event["type"] == "done":
                if sentence_buffer.strip():
                    async for audio_chunk in tts.synthesize_stream(
                        sentence_buffer, language=tts_lang
                    ):
                        audio_b64 = base64.b64encode(audio_chunk).decode("utf-8")
                        yield f"data: {json.dumps({'audio': audio_b64})}\n\n"
                    full_response += sentence_buffer

                store.add(sid, "user", transcript)
                store.add(sid, "assistant", full_response)
                yield (
                    f"data: {json.dumps({'done': True, 'session_id': sid, 'transcript': transcript, 'response': full_response})}\n\n"
                )

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
    """Agresif cümle detection — ilk audio chunk'ı erken gönder."""
    text = buffer.strip()
    if not text:
        return False

    word_count = len(text.split())
    print(f"🔤 Sentence check: {text[:60]!r} | words={word_count}", flush=True)

    if any(text.endswith(p) for p in [".", "?", "!", "。", "？", "！"]):
        print(f"  ✅ Flush: punctuation | {text!r}", flush=True)
        return True
    if text.endswith(",") and word_count >= 4:
        print(f"  ✅ Flush: comma + {word_count} words", flush=True)
        return True
    if text.endswith(":") and word_count >= 3:
        print("  ✅ Flush: colon", flush=True)
        return True
    if word_count >= 6:
        print(f"  ✅ Flush: {word_count} words", flush=True)
        return True
    return False


FILLER = {
    "tr": "Hımm, bir bakayım.",
    "en": "Hmm, let me see.",
    "uz": "Hmm, ko'rib turaman.",
    "ru": "Хм, сейчас посмотрю.",
}


def _resolve_tts_lang(detected_lang: str) -> str:
    """Detected language'i TTS voice mapping'e çevir. Desteklenmeyen dil → tr."""
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
        reply, _full_history = await agent.run(
            messages, session_id=session_id, detected_lang=detected_lang
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
        log.exception("Agent run failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    store.add(session_id, "user", user_message)
    store.add(session_id, "assistant", reply)

    return reply
