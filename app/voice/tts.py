"""Text-to-speech via edge-tts (Microsoft, ücretsiz)."""

import io
import logging

import edge_tts

log = logging.getLogger("miralas.tts")

# Dil → ses mapping (Türkçe, İngilizce, Özbekçe, Rusça)
VOICE_MAP = {
    "tr": "tr-TR-AhmetNeural",  # Erkek ses
    "en": "en-US-AriaNeural",
    "uz": "uz-UZ-MadinaNeural",
    "ru": "ru-RU-DmitryNeural",
}


async def synthesize(text: str, language: str = "tr") -> bytes:
    """Text → WAV bytes."""
    voice = VOICE_MAP.get(language, VOICE_MAP["tr"])
    log.info("TTS: lang=%s voice=%s text=%r", language, voice, text[:50])

    communicate = edge_tts.Communicate(text, voice)

    # Audio buffer'ına yaz
    audio_buffer = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_buffer.write(chunk["data"])

    audio_buffer.seek(0)
    return audio_buffer.read()
