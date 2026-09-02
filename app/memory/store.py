import time
import uuid
from collections import deque


class SessionStore:
    """Bellek-ici konusma magazasi: TTL + mesaj limiti."""

    def __init__(self, ttl_seconds: int, max_turns: int) -> None:
        self._ttl = ttl_seconds
        self._max_messages = max_turns * 2  # user + assistant
        self._sessions: dict[str, tuple[float, deque[dict[str, str]]]] = {}

    def new_session_id(self) -> str:
        return uuid.uuid4().hex[:12]

    def get(self, session_id: str) -> list[dict[str, str]]:
        entry = self._sessions.get(session_id)
        if entry is None:
            return []
        ts, messages = entry
        if time.monotonic() - ts > self._ttl:
            del self._sessions[session_id]
            return []
        return list(messages)

    def add(self, session_id: str, role: str, content: str) -> None:
        entry = self._sessions.get(session_id)
        if entry is None:
            messages: deque[dict[str, str]] = deque(maxlen=self._max_messages)
        else:
            messages = entry[1]
        messages.append({"role": role, "content": content})
        self._sessions[session_id] = (time.monotonic(), messages)

    def clear(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)


store = SessionStore(ttl_seconds=1800, max_turns=12)
