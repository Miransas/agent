import asyncio
import io
import logging
import threading

from faster_whisper import WhisperModel

from app.config.settings import settings

log = logging.getLogger("miralas.stt")

_MODEL: WhisperModel | None = None


def _get_model() -> WhisperModel:
    global _MODEL
    if _MODEL is None:
        log.info("Loading Whisper model: %s", settings.stt_model_size)
        _MODEL = WhisperModel(
            settings.stt_model_size,
            device="auto",  # Mac'te CPU'ya duser (CTranslate2 Metal yok)
            compute_type="int8",  # CPU icin en verimli
        )
        log.info("Whisper model ready")
    return _MODEL


def warmup() -> None:
    """Server acilisinda modeli arka planda yukler (ilk istek yavas olmasin)."""
    threading.Thread(target=_get_model, daemon=True).start()


def _transcribe_bytes(audio: bytes) -> str:
    segments, info = _get_model().transcribe(
        io.BytesIO(audio),
        language=settings.stt_language or None,
        beam_size=5,
        vad_filter=True,
    )
    text = " ".join(seg.text for seg in segments).strip()
    log.info(
        "STT: lang=%s (%.2f) text=%r",
        info.language,
        info.language_probability,
        text,
    )
    return text


async def transcribe(audio: bytes) -> str:
    """Blocking Whisper cagrisini thread pool'da calistirir."""
    return await asyncio.to_thread(_transcribe_bytes, audio)
