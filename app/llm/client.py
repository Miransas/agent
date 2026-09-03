import json
import logging
from collections.abc import AsyncGenerator

import httpx

from app.config.settings import settings

log = logging.getLogger(__name__)


async def generate(
    messages: list[dict[str, str]],
    *,
    tools: list[dict] | None = None,
    stream: bool = False,
) -> dict | AsyncGenerator[dict, None]:
    """OpenAI-compatible /chat/completions.

    stream=False → full response (dict)
    stream=True → async generator yielding chunks
    """
    if not stream:
        # Non-streaming: normal request
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
                "LLM call: model=%s messages=%d tools=%d stream=%s",
                settings.llm_model,
                len(messages),
                len(tools) if tools else 0,
                stream,
            )

            response = await client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            log.debug("LLM response: %s", data)
            if "choices" not in data or not data["choices"]:
                raise ValueError(f"Invalid LLM response: {data}")
            return data
    else:
        # Streaming: return generator
        async def stream_generator():
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
                    "stream": True,
                }
                if tools:
                    payload["tools"] = tools
                    payload["tool_choice"] = "auto"

                log.info(
                    "LLM streaming call: model=%s messages=%d tools=%d",
                    settings.llm_model,
                    len(messages),
                    len(tools) if tools else 0,
                )

                async with client.stream("POST", "/chat/completions", json=payload) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            chunk_str = line[6:]  # Remove "data: "
                            if chunk_str == "[DONE]":
                                break
                            try:
                                chunk = json.loads(chunk_str)
                                yield chunk
                            except json.JSONDecodeError:
                                log.warning("Failed to parse chunk: %s", chunk_str)

        return stream_generator()
