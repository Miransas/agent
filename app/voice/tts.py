"""Text-to-speech via edge-tts (Microsoft, ücretsiz)."""

import io
import logging
from collections.abc import AsyncGenerator

import edge_tts

log = logging.getLogger("miralas.tts")

# Dil → ses mapping (kadın sesleri ağırlıklı)
VOICE_MAP = {
    "tr": "tr-TR-EmelNeural",  # Kadın sesi (doğal, sıcak ton)
    "en": "en-GB-SoniaNeural",  # Kadın sesi (British accent, profesyonel)
    "uz": "uz-UZ-MadinaNeural",  # Kadın sesi (Özbekçe native)
    "ru": "ru-RU-SvetlanaNeural",  # Kadın sesi (Rusça native)
}


# Ses kişiselleştirme (Emel'i klasik havadan kurtar)
VOICE_TWEAKS = {
    "tr": {"rate": "+5%", "pitch": "+2Hz", "volume": "+0%"},  # Biraz hızlı, hafif tiz
    "en": {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
    "uz": {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
    "ru": {"rate": "+0%", "pitch": "+0Hz", "volume": "+0%"},
}


async def synthesize(text: str, language: str = "tr") -> bytes:
    """Text → audio bytes (non-streaming)."""
    voice = VOICE_MAP.get(language, VOICE_MAP["tr"])
    tweaks = VOICE_TWEAKS.get(language, VOICE_TWEAKS["tr"])
    log.info("TTS: lang=%s voice=%s text=%r", language, voice, text[:50])

    communicate = edge_tts.Communicate(
        text,
        voice,
        rate=tweaks["rate"],
        pitch=tweaks["pitch"],
        volume=tweaks["volume"],
    )

    # Audio buffer'ına yaz
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])

    audio_buffer.seek(0)
    return audio_buffer.read()


async def synthesize_stream(text: str, language: str = "tr") -> AsyncGenerator[bytes, None]:
    """Text → audio chunks (streaming).

    Yields: audio bytes (MP3 chunks)
    """
    voice = VOICE_MAP.get(language, VOICE_MAP["tr"])
    log.info("TTS streaming: lang=%s voice=%s text=%r", language, voice, text[:50])

    communicate = edge_tts.Communicate(text, voice)

    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            yield chunk["data"]
