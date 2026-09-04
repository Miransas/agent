"""ReAct-style agent loop: LLM tool cagirirsa calistir, sonucunu geri besle."""

import json
import logging
import time
from collections.abc import AsyncGenerator

from app.llm import client as llm_client
from app.tools import registry

log = logging.getLogger("miralas.agent")

MAX_ITERATIONS = 4
MAX_RETRIES = 2
RETRY_DELAY = 1.0

LANG_HINT = {
    "tr": "[Sistem: Müşteri TÜRKÇE konuşuyor. Yanıtın TAMAMEN Türkçe olmalı.]",
    "en": "[System: Customer speaks ENGLISH. Your response MUST be entirely in English.]",
    "uz": "[Tizim: Mijoz O'ZBEKCHA gaplashmoqda. Javobingiz TO'LIQ o'zbek tilida bo'lishi kerak.]",
    "ru": "[Система: Клиент говорит по-РУССКИ. Ваш ответ ДОЛЖЕН быть полностью на русском.]",
}

MENU_TRIGGERS = ["menü", "menu", "ne var", "ürün", "urun", "satıyor", "ne sunuyorsunuz"]


def _needs_menu_tool(user_message: str) -> bool:
    return any(kw in user_message.lower() for kw in MENU_TRIGGERS)


async def _generate_with_retry(messages, tools=None, stream=False):
    """LLM call with retry logic."""
    for attempt in range(MAX_RETRIES):
        try:
            return await llm_client.generate(messages, tools=tools, stream=stream)
        except Exception as exc:
            if attempt == MAX_RETRIES - 1:
                log.error("LLM call failed after %d attempts: %s", MAX_RETRIES, exc)
                raise
            log.warning("LLM call failed (attempt %d/%d): %s", attempt + 1, MAX_RETRIES, exc)
            time.sleep(RETRY_DELAY)


async def run(
    messages: list[dict[str, str]],
    session_id: str,
    detected_lang: str = "tr",
) -> tuple[str, list[dict]]:
    """Agent'i calistirir (non-streaming). Returns (final_text, full_history)."""
    tools_schema = registry.get_tools_schema()
    history = list(messages)

    # Language hint'i son user message'a prepend et
    hint = LANG_HINT.get(detected_lang, LANG_HINT["tr"])
    for i in range(len(history) - 1, -1, -1):
        if history[i]["role"] == "user":
            history[i]["content"] = f"{hint}\n\n{history[i]['content']}"
            log.info("Language hint injected: %s", detected_lang)
            break

    for iteration in range(MAX_ITERATIONS):
        log.info("=== Agent iteration %d, %d messages ===", iteration, len(history))
        response_data = await _generate_with_retry(history, tools=tools_schema, stream=False)

        if "choices" not in response_data or not response_data["choices"]:
            log.error("Invalid response: %s", response_data)
            return "Uzgunum, bir sorun olustu.", history

        message = response_data["choices"][0]["message"]
        history.append(message)

        tool_calls = message.get("tool_calls")
        log.info(
            "LLM response: content=%r tool_calls=%d",
            (message.get("content") or "")[:50],
            len(tool_calls) if tool_calls else 0,
        )

        if not tool_calls:
            # LLM text dondurdu — guardrail: menü sorulduysa ama tool çağrılmadıysa reminder
            last_user = next((m["content"] for m in reversed(history) if m["role"] == "user"), "")
            if _needs_menu_tool(last_user) and iteration == 0:
                log.warning("🚨 Guardrail: menü soruldu ama tool çağrılmadı, reminder gönderiliyor")
                history.append(
                    {
                        "role": "user",
                        "content": "[SİSTEM UYARISI: Müşteri menü sordu. ÖNCE list_menu aracını çağır, sonra yanıt ver.]",
                    }
                )
                continue
            return (message.get("content") or "").strip(), history

        # Tool cagirildi
        for tc in tool_calls:
            fn_name = tc["function"]["name"]
            try:
                args = json.loads(tc["function"]["arguments"])
            except json.JSONDecodeError:
                args = {}

            # Guvenlik: session_id her zaman server'dan
            args["session_id"] = session_id

            log.info("Tool call: %s(%s)", fn_name, args)
            try:
                result = registry.call_tool(fn_name, args)
                log.info("Tool result: %s", result[:200])
            except Exception as exc:
                log.error("Tool call failed: %s(%s) → %s", fn_name, args, exc)
                result = json.dumps({"error": str(exc)})

            history.append({"role": "tool", "tool_call_id": tc["id"], "content": result})

    # Max iteration'a ulasilirsa son asistan mesaji
    last = next((m for m in reversed(history) if m["role"] == "assistant"), None)
    fallback = (last or {}).get("content") or "Uzgunum, islemi tamamlayamadim."
    return fallback.strip(), history


async def _execute_tools_only(
    messages: list[dict[str, str]],
    session_id: str,
    detected_lang: str = "tr",
) -> list[dict[str, str]]:
    """Tool call'larını yap, güncellenmiş messages'i döndür (final response üretmez)."""
    tools_schema = registry.get_tools_schema()
    history = list(messages)

    # Language hint ekle
    hint = LANG_HINT.get(detected_lang, LANG_HINT["tr"])
    for i in range(len(history) - 1, -1, -1):
        if history[i]["role"] == "user":
            history[i]["content"] = f"{hint}\n\n{history[i]['content']}"
            break

    for iteration in range(MAX_ITERATIONS):
        log.info("=== Tool execution iteration %d ===", iteration)
        response_data = await _generate_with_retry(history, tools=tools_schema, stream=False)

        if "choices" not in response_data or not response_data["choices"]:
            log.error("Invalid response: %s", response_data)
            return history

        message = response_data["choices"][0]["message"]
        history.append(message)

        tool_calls = message.get("tool_calls")

        if not tool_calls:
            # Tool call yok, son assistant message'ı sil (streaming'de yeniden üretilecek)
            if history and history[-1]["role"] == "assistant":
                history.pop()
            return history

        # Tool çağır
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
                log.info("Tool result: %s", result[:200])
            except Exception as exc:
                log.error("Tool call failed: %s(%s) → %s", fn_name, args, exc)
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

    # Tool gerektiren soru mu?
    tool_keywords = ["menü", "sipariş", "sepet", "burger", "pizza", "cola", "randevu"]
    needs_tools = any(kw in last_user.lower() for kw in tool_keywords)

    if needs_tools:
        log.info("Tool-requiring query, executing tools then streaming final response")
        # Tool call'larını yap (non-streaming, hızlı)
        history = await _execute_tools_only(messages, session_id, detected_lang)

        # Final response'u streaming ile üret (tools YOK, sadece text)
        full_response = ""

        stream = await _generate_with_retry(history, tools=None, stream=True)

        async for chunk in stream:
            if "choices" not in chunk or not chunk["choices"]:
                continue

            choice = chunk["choices"][0]
            delta = choice.get("delta", {})
            content = delta.get("content")

            if content:
                full_response += content
                yield {"type": "token", "content": content}

        yield {"type": "done", "full_response": full_response}
        return

    # Conversational soru — direkt streaming
    log.info("Conversational query, streaming")

    # Language hint ekle
    hint = LANG_HINT.get(detected_lang, LANG_HINT["tr"])
    for i in range(len(messages) - 1, -1, -1):
        if messages[i]["role"] == "user":
            messages[i]["content"] = f"{hint}\n\n{messages[i]['content']}"
            break

    full_response = ""
    stream = await _generate_with_retry(messages, tools=None, stream=True)

    async for chunk in stream:
        if "choices" not in chunk or not chunk["choices"]:
            continue

        choice = chunk["choices"][0]
        delta = choice.get("delta", {})
        content = delta.get("content")

        if content:
            full_response += content
            yield {"type": "token", "content": content}

    yield {"type": "done", "full_response": full_response}
