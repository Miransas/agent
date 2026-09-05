"""ReAct-style agent loop: LLM tool cagirirsa calistir, sonucunu geri besle."""

import asyncio
import json
import logging
from collections.abc import AsyncGenerator

from app.llm import client as llm_client
from app.tools import registry

log = logging.getLogger("miralas.agent")

MAX_ITERATIONS = 4
MAX_RETRIES = 2
RETRY_DELAY = 1.0

# Tek, paylasilan liste — agent.py ve server/api.py ayni fonksiyonu kullanir,
# farkli listeler birbiriyle celismesin diye.
TOOL_TRIGGER_KEYWORDS = [
    "menü", "menu", "ne var", "ürün", "urun", "satıyor", "ne sunuyorsunuz",
    "sipariş", "siparis", "sepet", "burger", "pizza", "cola", "randevu",
]


def needs_tool_call(user_message: str) -> bool:
    """Mesaj muhtemelen menu/siparis/randevu gibi bir tool cagrisi gerektiriyor mu."""
    text = user_message.lower()
    return any(kw in text for kw in TOOL_TRIGGER_KEYWORDS)


async def _generate_with_retry(messages, tools=None, stream=False):
    for attempt in range(MAX_RETRIES):
        try:
            return await llm_client.generate(messages, tools=tools, stream=stream)
        except Exception as exc:
            if attempt == MAX_RETRIES - 1:
                log.error("LLM call failed after %d attempts: %s", MAX_RETRIES, exc)
                raise
            log.warning("LLM call failed (attempt %d/%d): %s", attempt + 1, MAX_RETRIES, exc)
            await asyncio.sleep(RETRY_DELAY)


async def run(
    messages: list[dict[str, str]],
    session_id: str,
    detected_lang: str = "tr",
) -> tuple[str, list[dict]]:
    """Agent'i calistirir (non-streaming). Returns (final_text, full_history)."""
    tools_schema = registry.get_tools_schema()
    history = list(messages)

    for iteration in range(MAX_ITERATIONS):
        log.debug("Agent iteration %d, %d messages", iteration, len(history))
        response_data = await _generate_with_retry(history, tools=tools_schema, stream=False)

        if "choices" not in response_data or not response_data["choices"]:
            log.error("Invalid response: %s", response_data)
            return "Uzgunum, bir sorun olustu.", history

        message = response_data["choices"][0]["message"]
        history.append(message)
        tool_calls = message.get("tool_calls")

        if not tool_calls:
            last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
            if needs_tool_call(last_user) and iteration == 0:
                log.warning("Guardrail: tool gerektiren mesaj ama tool cagrilmadi, reminder gonderiliyor")
                history.append({
                    "role": "user",
                    "content": "[SİSTEM UYARISI: Müşteri menü/sipariş/randevu sordu. ÖNCE ilgili aracı çağır, sonra yanıt ver.]",
                })
                continue
            return (message.get("content") or "").strip(), history

        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}
            args["session_id"] = session_id  # Guvenlik: session_id her zaman server'dan

            log.info("Tool call: %s(%s)", fn_name, args)
            try:
                result = registry.call_tool(fn_name, args)
                log.debug("Tool result: %s", result[:200])
            except Exception as exc:
                log.error("Tool call failed: %s(%s) -> %s", fn_name, args, exc)
                result = json.dumps({"error": str(exc)})

            history.append({"role": "tool", "tool_call_id": tc["id"], "content": result})

    last = next((m for m in reversed(history) if m["role"] == "assistant"), None)
    fallback = (last or {}).get("content") or "Uzgunum, islemi tamamlayamadim."
    return fallback.strip(), history


async def _execute_tools_only(messages: list[dict[str, str]], session_id: str) -> list[dict[str, str]]:
    """Tool call'larini yapar, guncellenmis messages'i doner (final response uretmez)."""
    tools_schema = registry.get_tools_schema()
    history = list(messages)

    for iteration in range(MAX_ITERATIONS):
        log.debug("Tool execution iteration %d", iteration)
        response_data = await _generate_with_retry(history, tools=tools_schema, stream=False)

        if "choices" not in response_data or not response_data["choices"]:
            log.error("Invalid response: %s", response_data)
            return history

        message = response_data["choices"][0]["message"]
        history.append(message)
        tool_calls = message.get("tool_calls")

        if not tool_calls:
            if history and history[-1]["role"] == "assistant":
                history.pop()
            return history

        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}
            args["session_id"] = session_id

            log.info("Tool call: %s(%s)", fn_name, args)
            try:
                result = registry.call_tool(fn_name, args)
                log.debug("Tool result: %s", result[:200])
            except Exception as exc:
                log.error("Tool call failed: %s(%s) -> %s", fn_name, args, exc)
                result = json.dumps({"error": str(exc)})

            history.append({"role": "tool", "tool_call_id": tc["id"], "content": result})

    return history


async def run_stream(
    messages: list[dict[str, str]],
    session_id: str,
    detected_lang: str = "tr",
) -> AsyncGenerator[dict, None]:
    """Agent'i streaming modda calistirir."""
    last_user = next((m["content"] for m in reversed(messages) if m["role"] == "user"), "")

    if needs_tool_call(last_user):
        log.debug("Tool-requiring query, executing tools then streaming final response")
        history = await _execute_tools_only(messages, session_id)
        full_response = ""
        stream = await _generate_with_retry(history, tools=None, stream=True)

        async for chunk in stream:
            if "choices" not in chunk or not chunk["choices"]:
                continue
            content = chunk["choices"][0].get("delta", {}).get("content")
            if content:
                full_response += content
                yield {"type": "token", "content": content}

        yield {"type": "done", "full_response": full_response}
        return

    log.debug("Conversational query, streaming")
    full_response = ""
    stream = await _generate_with_retry(messages, tools=None, stream=True)

    async for chunk in stream:
        if "choices" not in chunk or not chunk["choices"]:
            continue
        content = chunk["choices"][0].get("delta", {}).get("content")
        if content:
            full_response += content
            yield {"type": "token", "content": content}

    yield {"type": "done", "full_response": full_response}