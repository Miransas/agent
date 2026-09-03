"""ReAct-style agent loop: LLM tool cagirirsa calistir, sonucunu geri besle."""

import json
import logging

from app.llm import client as llm_client
from app.tools import registry

log = logging.getLogger("miralas.agent")

MAX_ITERATIONS = 4

MENU_TRIGGERS = ["menü", "menu", "ne var", "ürün", "urun", "satıyor", "ne sunuyorsunuz"]


def _needs_menu_tool(user_message: str) -> bool:
    return any(kw in user_message.lower() for kw in MENU_TRIGGERS)


async def run(
    messages: list[dict[str, str]],
    session_id: str,
) -> tuple[str, list[dict]]:
    """Agent'i calistirir. Returns (final_text, full_history)."""
    tools_schema = registry.get_tools_schema()
    history = list(messages)

    for iteration in range(MAX_ITERATIONS):
        log.info("=== Agent iteration %d, %d messages ===", iteration, len(history))
        response_data = await llm_client.generate(history, tools=tools_schema)

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
            result = registry.call_tool(fn_name, args)
            log.info("Tool result: %s", result[:200])

            history.append({"role": "tool", "tool_call_id": tc["id"], "content": result})

    # Max iteration'a ulasilirsa son asistan mesaji
    last = next((m for m in reversed(history) if m["role"] == "assistant"), None)
    fallback = (last or {}).get("content") or "Uzgunum, islemi tamamlayamadim."
    return fallback.strip(), history
