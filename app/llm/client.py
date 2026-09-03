import logging

import httpx

from app.config.settings import settings

log = logging.getLogger(__name__)


async def generate(
    messages: list[dict[str, str]],
    *,
    tools: list[dict] | None = None,
) -> dict:
    """OpenAI-compatible /chat/completions."""
    async with httpx.AsyncClient(
        base_url=settings.llm_base_url,
        headers={"Authorization": f"Bearer {settings.llm_api_key}"},
        timeout=httpx.Timeout(180.0, connect=10.0),
    ) as client:
        payload = {
            "model": settings.llm_model,
            "messages": messages,
            "temperature": settings.llm_temperature,
            "max_tokens": settings.llm_max_tokens,
            "stream": False,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"

        log.info(
            "LLM call: model=%s messages=%d tools=%d",
            settings.llm_model,
            len(messages),
            len(tools) if tools else 0,
        )
        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        log.debug("LLM response: %s", data)

    if "choices" not in data or not data["choices"]:
        raise ValueError(f"Invalid LLM response: {data}")

    return data
