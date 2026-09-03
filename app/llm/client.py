import json
import logging
from collections.abc import AsyncGenerator

import httpx

from app.config.settings import settings

log = logging.getLogger(__name__)

try:
    import miralas_core

    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False


async def generate(
    messages: list[dict[str, str]],
    *,
    tools: list[dict] | None = None,
    stream: bool = False,
) -> dict | AsyncGenerator[dict, None]:
    """OpenAI-compatible /chat/completions."""
    if stream:
        return _generate_stream(messages, tools)

    # Non-streaming
    if _RUST_AVAILABLE and not tools:
        # Sadece tool-less conversation için Rust kullan
        return await _generate_rust(messages)
    else:
        return await _generate_httpx(messages, tools)


async def _generate_rust(messages: list[dict[str, str]]) -> dict:
    """Rust reqwest ile (10x hızlı)."""
    log.info("LLM call (Rust): model=%s messages=%d", settings.llm_model, len(messages))

    messages_json = json.dumps(messages, ensure_ascii=False)
    response_json = miralas_core.llm_generate_sync(
        settings.llm_base_url,
        settings.llm_api_key,
        settings.llm_model,
        messages_json,
        settings.llm_temperature,
        settings.llm_max_tokens,
    )

    data = json.loads(response_json)
    log.debug("LLM response (Rust): %s", data)

    if "choices" not in data or not data["choices"]:
        raise ValueError(f"Invalid LLM response: {data}")
    return data


async def _generate_httpx(
    messages: list[dict[str, str]],
    tools: list[dict] | None = None,
) -> dict:
    """httpx fallback."""
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
            "LLM call (httpx): model=%s messages=%d tools=%d",
            settings.llm_model,
            len(messages),
            len(tools) if tools else 0,
        )

        response = await client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        log.debug("LLM response (httpx): %s", data)
        if "choices" not in data or not data["choices"]:
            raise ValueError(f"Invalid LLM response: {data}")
        return data


def _generate_stream(
    messages: list[dict[str, str]],
    tools: list[dict] | None = None,
) -> AsyncGenerator[dict, None]:
    """Streaming: httpx (PyO3 async generator karmaşık)."""

    async def _stream():
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
                "LLM streaming (httpx): model=%s messages=%d", settings.llm_model, len(messages)
            )

            async with client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        chunk_str = line[6:]
                        if chunk_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(chunk_str)
                            yield chunk
                        except json.JSONDecodeError:
                            log.warning("Failed to parse chunk: %s", chunk_str)

    return _stream()
