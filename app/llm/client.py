import logging

import httpx

from app.config.settings import settings
from app.core.types import Message

log = logging.getLogger("miralas.llm")


async def generate(messages: list[Message], *, system_prompt: str) -> str:
    """Ollama OpenAI-compatible endpoint'e history ile cagri."""
    async with httpx.AsyncClient(
        base_url=settings.llm_base_url,
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        timeout=httpx.Timeout(180.0, connect=10.0),
    ) as client:
        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *[m.model_dump() for m in messages],
            ],
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
            "stream": False,
        }
        log.info("LLM call: model=%s, messages=%d", settings.llm_model, len(messages))
        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        if "choices" not in data or not data["choices"]:
            raise ValueError(f"Invalid LLM response: {data}")
        return data["choices"][0]["message"]["content"].strip()
