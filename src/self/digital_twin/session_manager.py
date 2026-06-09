"""Session Manager — conversation state and context."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4


class SessionManager:
    def __init__(self, session_ttl_minutes: int = 30) -> None:
        self._sessions: dict[str, dict[str, Any]] = {}
        self._ttl = timedelta(minutes=session_ttl_minutes)

    def create_session(self, user: str = "default") -> str:
        sid = f"twin_{uuid4().hex}"
        self._sessions[sid] = {
            "id": sid,
            "user": user,
            "created_at": datetime.now(UTC).isoformat(),
            "last_active": datetime.now(UTC).isoformat(),
            "history": [],
            "context": {"entities": [], "last_intent": None, "turn_count": 0},
        }
        return sid

    def get_session(self, session_id: str) -> dict[str, Any] | None:
        session = self._sessions.get(session_id)
        if session is None:
            return None
        last = datetime.fromisoformat(session["last_active"])
        if datetime.now(UTC) - last > self._ttl:
            del self._sessions[session_id]
            return None
        session["last_active"] = datetime.now(UTC).isoformat()
        return session

    def add_turn(self, session_id: str, query: str, answer: dict[str, Any]) -> None:
        session = self.get_session(session_id)
        if session is None:
            return
        session["history"].append(
            {"query": query, "answer": answer, "timestamp": datetime.now(UTC).isoformat()}
        )
        session["context"]["turn_count"] += 1
        if len(session["history"]) > 100:
            session["history"] = session["history"][-100:]

    def recent_history(self, session_id: str, limit: int = 10) -> list[dict[str, Any]]:
        session = self.get_session(session_id)
        if session is None:
            return []
        return session["history"][-limit:]

    def update_context(self, session_id: str, **kwargs: Any) -> None:
        session = self.get_session(session_id)
        if session is None:
            return
        session["context"].update(kwargs)

    def destroy_session(self, session_id: str) -> None:
        self._sessions.pop(session_id, None)
