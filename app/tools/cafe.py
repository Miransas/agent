"""Kafe/restoran icin tool'lar — mock data ile basliyoruz."""

from datetime import datetime, timedelta
from typing import Any

# Mock menu (ileride DB'den gelecek)
MENU = [
    {"id": "burger", "name": "Burger", "price": 150, "category": "ana"},
    {"id": "pizza", "name": "Pizza Margherita", "price": 200, "category": "ana"},
    {"id": "fries", "name": "Patates Kızartması", "price": 60, "category": "yan"},
    {"id": "coke", "name": "Cola", "price": 40, "category": "icecek"},
    {"id": "water", "name": "Su", "price": 20, "category": "icecek"},
]

# Mock orders (session_id → order)
_orders: dict[str, dict[str, Any]] = {}


def list_menu() -> dict[str, Any]:
    """Kafenin menusunu listeler."""
    return {
        "menu": MENU,
        "currency": "TL",
        "message": "Menu yukarida. Musteriye kisa onerilerde bulun, hepsini okuma.",
    }


def add_to_cart(session_id: str, item_id: str, quantity: int = 1) -> dict[str, Any]:
    """Musterinin sepetine urun ekler."""
    item = next((m for m in MENU if m["id"] == item_id), None)
    if not item:
        return {"error": f"'{item_id}' menusunde yok"}

    order = _orders.setdefault(session_id, {"items": [], "total": 0})
    order["items"].append({"item": item, "quantity": quantity})
    order["total"] += item["price"] * quantity

    return {
        "added": item["name"],
        "quantity": quantity,
        "subtotal": order["total"],
        "message": f"{item['name']} sepete eklendi.",
    }


def get_cart(session_id: str) -> dict[str, Any]:
    """Musterinin mevcut sepetini getirir."""
    order = _orders.get(session_id, {"items": [], "total": 0})
    return order


def place_order(session_id: str) -> dict[str, Any]:
    """Sepetteki urunleri siparise cevirir."""
    order = _orders.get(session_id)
    if not order or not order["items"]:
        return {"error": "Sepet bos, siparis olusturulamaz."}

    order_id = f"ORD-{len(_orders) + 1:04d}"
    order["order_id"] = order_id
    order["placed_at"] = datetime.now().isoformat()

    return {
        "order_id": order_id,
        "total": order["total"],
        "message": f"Siparis olusturuldu: {order_id}. Musteriye bildirim yap.",
    }


def get_available_slots(date: str) -> dict[str, Any]:
    """Belirli bir tarihte randevu icin musait saatleri doner."""
    base = datetime.strptime(date, "%Y-%m-%d")
    slots = [(base + timedelta(hours=h)).strftime("%H:00") for h in range(10, 18)]
    return {"date": date, "available_slots": slots[:6]}


def book_appointment(session_id: str, customer_name: str, date: str, time: str) -> dict[str, Any]:
    """Randevu olusturur."""
    return {
        "appointment_id": f"APT-{len(_orders) + 100:04d}",
        "customer": customer_name,
        "date": date,
        "time": time,
        "message": f"Randevu alindi: {date} {time}. Musteriye onayla.",
    }
