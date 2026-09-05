"""Bellek-ici konusma magazasi.
Rust build edilmisse DashMap (lock-free), yoksa Python dict fallback.

NOT: Tek process icin tasarlandi. `--workers > 1` ile calistirilirsa her
worker'in kendi ayri store'u olur, ayni session_id farkli worker'a dusunce
gecmis kaybolur. Coklu worker'a gecerken Redis gibi paylasilan bir store'a tasi.
"""

import asyncio
import json
import logging
import time
import uuid
from collections import deque

from app.config.settings import settings

log = logging.getLogger("miralas.memory")

try:
    import miralas_core

    _RUST_AVAILABLE = True
except ImportError:
    _RUST_AVAILABLE = False


class SessionStore:
    """Bellek-ici konusma magazasi: TTL + mesaj limiti."""

    def __init__(self, ttl_seconds: int, max_turns: int) -> None:
        self._ttl = ttl_seconds
        self._max_messages = max_turns * 2  # user + assistant

        if _RUST_AVAILABLE:
            log.info("Session store: Rust (DashMap)")
            self._rust_mode = True
        else:
            log.warning("Session store: Python fallback (dict)")
            self._rust_mode = False
            self._sessions: dict[str, tuple[float, deque[dict[str, str]]]] = {}

    def new_session_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def get(self, session_id: str) -> list[dict[str, str]]:
        if self._rust_mode:
            data = miralas_core.session_get(session_id)
            if data is None:
                return []
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                return []
            if time.monotonic() - payload.get("ts", 0) > self._ttl:
                miralas_core.session_set(session_id, json.dumps({"ts": 0, "messages": []}))
                return []
            return payload.get("messages", [])

        entry = self._sessions.get(session_id)
        if entry is None:
            return []
        ts, messages = entry
        if time.monotonic() - ts > self._ttl:
            del self._sessions[session_id]
            return []
        return list(messages)

    def add(self, session_id: str, role: str, content: str) -> None:
        if self._rust_mode:
            data = miralas_core.session_get(session_id)
            if data is None:
                messages: deque[dict[str, str]] = deque(maxlen=self._max_messages)
            else:
                try:
                    payload = json.loads(data)
                except json.JSONDecodeError:
                    payload = {}
                messages = deque(payload.get("messages", []), maxlen=self._max_messages)

            messages.append({"role": role, "content": content})
            miralas_core.session_set(
                session_id,
                json.dumps({"ts": time.monotonic(), "messages": list(messages)}),
            )
            return

        entry = self._sessions.get(session_id)
        messages = entry[1] if entry else deque(maxlen=self._max_messages)
        messages.append({"role": role, "content": content})
        self._sessions[session_id] = (time.monotonic(), messages)

    def clear(self, session_id: str) -> None:
        if self._rust_mode:
            miralas_core.session_set(session_id, json.dumps({"ts": 0, "messages": []}))
        else:
            self._sessions.pop(session_id, None)

    def sweep_expired(self) -> int:
        """Suresi gecmis session'lari gercekten siler."""
        if self._rust_mode:
            return miralas_core.session_sweep(int(self._ttl))

        now = time.monotonic()
        expired = [sid for sid, (ts, _) in self._sessions.items() if now - ts > self._ttl]
        for sid in expired:
            del self._sessions[sid]
        return len(expired)


store = SessionStore(
    ttl_seconds=settings.memory_ttl_seconds,
    max_turns=settings.memory_max_messages // 2,
)


async def start_cleanup_task(interval_seconds: int = 600) -> None:
    """Periyodik olarak suresi gecmis session'lari temizler. lifespan'da baslatilir."""
    while True:
        await asyncio.sleep(interval_seconds)
        removed = store.sweep_expired()
        if removed:
            log.info("Session cleanup: %d suresi gecmis session silindi", removed)