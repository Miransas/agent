"""Tool'lari kaydeder, LLM icin OpenAI-compatible schema uretir, cagirir."""

import json
from collections.abc import Callable
from typing import Any

from app.tools import cafe

_TOOLS: list[tuple[str, Callable[..., Any], str, dict[str, Any]]] = [
    (
        "list_menu",
        cafe.list_menu,
        "Kafenin menusunu listeler: urun isimleri, fiyatlar ve kategoriler.",
        {"type": "object", "properties": {}, "required": []},
    ),
    (
        "add_to_cart",
        cafe.add_to_cart,
        "Musterinin sepetine bir urun ekler. item_id menu ID'si olmali.",
        {
            "type": "object",
            "properties": {
                "item_id": {
                    "type": "string",
                    "description": "Menu urun ID'si (burger, pizza, fries, coke, water)",
                },
                "quantity": {"type": "integer", "description": "Adet", "default": 1},
            },
            "required": ["item_id"],
        },
    ),
    (
        "get_cart",
        cafe.get_cart,
        "Musterinin mevcut sepetini ve toplam tutari getirir.",
        {"type": "object", "properties": {}, "required": []},
    ),
    (
        "place_order",
        cafe.place_order,
        "Sepetteki tum urunleri siparise cevirir. Sepet bos ise hata doner.",
        {"type": "object", "properties": {}, "required": []},
    ),
    (
        "get_available_slots",
        cafe.get_available_slots,
        "Belirli bir tarihte (YYYY-MM-DD) musait randevu saatlerini doner.",
        {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Tarih, YYYY-MM-DD formatinda"},
            },
            "required": ["date"],
        },
    ),
    (
        "book_appointment",
        cafe.book_appointment,
        "Musteri icin randevu olusturur.",
        {
            "type": "object",
            "properties": {
                "customer_name": {"type": "string", "description": "Musteri adi"},
                "date": {"type": "string", "description": "YYYY-MM-DD"},
                "time": {"type": "string", "description": "HH:MM formatinda saat"},
            },
            "required": ["customer_name", "date", "time"],
        },
    ),
]


def get_tools_schema() -> list[dict[str, Any]]:
    """LLM'e gonderilecek schema. session_id YOK — server enjekte eder."""
    return [
        {
            "type": "function",
            "function": {"name": name, "description": desc, "parameters": params},
        }
        for name, _, desc, params in _TOOLS
    ]


def call_tool(name: str, arguments: dict[str, Any]) -> str:
    """Tool'u cagirir, sonucu JSON string olarak doner."""
    tool = next((fn for n, fn, _, _ in _TOOLS if n == name), None)
    if tool is None:
        return json.dumps({"error": f"Tool bulunamadi: {name}"}, ensure_ascii=False)
    try:
        result = tool(**arguments)
    except Exception as exc:
        result = {"error": str(exc)}
    return json.dumps(result, ensure_ascii=False)
