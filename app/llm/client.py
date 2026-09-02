import logging

import httpx

from app.config.settings import settings

log = logging.getLogger(__name__)


async def generate(user_message: str, *, system_prompt: str) -> str:
    """Ollama OpenAI-compatible endpoint."""
    async with httpx.AsyncClient(
        base_url=settings.llm_base_url,
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        timeout=httpx.Timeout(180.0, connect=10.0),  # 3 dakika timeout
    ) as client:
        payload = {
            "model": settings.llm_model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
            "stream": False,
        }

        log.info("Calling LLM: model=%s, tokens=%d", settings.llm_model, len(user_message))
        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()

        data = response.json()
        log.debug("LLM response: %s", data)

        if "choices" not in data or not data["choices"]:
            raise ValueError(f"Invalid LLM response: {data}")

        content = data["choices"][0].get("message", {}).get("content", "")
        return content.strip()
