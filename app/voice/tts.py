"""Text-to-speech via edge-tts (Microsoft, ücretsiz)."""

import io
import logging
from collections.abc import AsyncGenerator

import edge_tts

log = logging.getLogger("miralas.tts")

VOICE_MAP = {
    "tr": "tr-TR-EmelNeural",
    "en": "en-GB-SoniaNeural",
    "uz": "uz-UZ-MadinaNeural",
    "ru": "ru-RU-SvetlanaNeural",
}

VOICE_TWEAKS = {
    "tr": {"rate": "+5%", "pitch": "+2Hz", "volume": "+0%"},
    "en": {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
    "uz": {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
    "ru": {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
}


def _voice_and_tweaks(language: str) -> tuple[str, dict[str, str]]:
    voice = VOICE_MAP.get(language, VOICE_MAP["tr"])
    tweaks = VOICE_TWEAKS.get(language, VOICE_TWEAKS["tr"])
    return voice, tweaks


async def synthesize(text: str, language: str = "tr") -> bytes:
    """Text → audio bytes (non-streaming)."""
    voice, tweaks = _voice_and_tweaks(language)
    log.debug("TTS: lang=%s voice=%s text=%r", language, voice, text[:50])

    communicate = edge_tts.Communicate(
        text, voice,
        rate=tweaks["rate"], pitch=tweaks["pitch"], volume=tweaks["volume"],
    )

    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])

    audio_buffer.seek(0)
    return audio_buffer.read()


async def synthesize_stream(text: str, language: str = "tr") -> AsyncGenerator[bytes, None]:
    """Text → audio chunks (streaming)."""
    voice, tweaks = _voice_and_tweaks(language)
    log.debug("TTS streaming: lang=%s voice=%s text=%r", language, voice, text[:50])

    communicate = edge_tts.Communicate(
        text, voice,
        rate=tweaks["rate"], pitch=tweaks["pitch"], volume=tweaks["volume"],
    )

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]