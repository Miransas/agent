"""Bellek-ici konusma magazasi.
Rust build edilmisse DashMap (lock-free, ~3x hizli), yoksa Python dict fallback.
"""

import json
import time
import uuid
from collections import deque

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
            print("✅ Session store: Rust (DashMap)")
            self._rust_mode = True
        else:
            print("⚠️  Session store: Python fallback (dict)")
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
                ts = payload.get("ts", 0)
                if time.monotonic() - ts > self._ttl:
                    miralas_core.session_set(session_id, json.dumps({"ts": 0, "messages": []}))
                    return []
                return payload.get("messages", [])
            except json.JSONDecodeError:
                return []
        else:
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
                payload = json.loads(data)
                messages = deque(payload.get("messages", []), maxlen=self._max_messages)

            messages.append({"role": role, "content": content})
            miralas_core.session_set(
                session_id,
                json.dumps(
                    {
                        "ts": time.monotonic(),
                        "messages": list(messages),
                    }
                ),
            )
        else:
            entry = self._sessions.get(session_id)
            if entry is None:
                messages: deque[dict[str, str]] = deque(maxlen=self._max_messages)
            else:
                messages = entry[1]
            messages.append({"role": role, "content": content})
            self._sessions[session_id] = (time.monotonic(), messages)

    def clear(self, session_id: str) -> None:
        if self._rust_mode:
            miralas_core.session_set(session_id, json.dumps({"ts": 0, "messages": []}))
        else:
            self._sessions.pop(session_id, None)


store = SessionStore(ttl_seconds=1800, max_turns=12)
