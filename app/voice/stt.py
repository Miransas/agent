import asyncio
import io
import logging
import threading

from faster_whisper import WhisperModel

from app.config.settings import settings

log = logging.getLogger("miralas.stt")

_MODEL: WhisperModel | None = None
_MODEL_LOCK = threading.Lock()


def _get_model() -> WhisperModel:
    global _MODEL
    if _MODEL is None:
        with _MODEL_LOCK:
            # Lock alindiktan sonra tekrar kontrol et — baska bir thread
            # lock'u beklerken zaten yuklemis olabilir.
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


def _transcribe_bytes(audio: bytes) -> tuple[str, str]:
    segments, info = _get_model().transcribe(
        io.BytesIO(audio),
        language=settings.stt_language or None,
        beam_size=5,
        vad_filter=True,
    )
    text = " ".join(seg.text for seg in segments).strip()
    detected_lang = info.language
    log.info(
        "STT: lang=%s (%.2f) text=%r",
        detected_lang,
        info.language_probability,
        text,
    )
    return text, detected_lang


async def transcribe(audio: bytes) -> tuple[str, str]:
    """Blocking Whisper cagrisini thread pool'da calistirir.

    Returns: (transcript, detected_language)
    """
    return await asyncio.to_thread(_transcribe_bytes, audio)