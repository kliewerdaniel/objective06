"""Query Intake — validate, sanitize, log incoming queries."""

from __future__ import annotations

from typing import Any

from .prompt_sanitizer import PromptSanitizer
from .session_manager import SessionManager


class QueryIntake:
    def __init__(
        self, session_manager: SessionManager, sanitizer: PromptSanitizer | None = None
    ) -> None:
        self._sessions = session_manager
        self._sanitizer = sanitizer or PromptSanitizer()

    def receive(self, query: str, session_id: str = "") -> dict[str, Any]:
        if not query or not query.strip():
            return {"ok": False, "error": "Query is empty", "session_id": session_id}
        if len(query) > 10000:
            return {
                "ok": False,
                "error": "Query exceeds 10000 character limit",
                "session_id": session_id,
            }
        if not session_id:
            session_id = self._sessions.create_session()
        session = self._sessions.get_session(session_id)
        if session is None:
            session_id = self._sessions.create_session()
        sanitized = self._sanitizer.check(query)
        if not sanitized["safe"]:
            return {
                "ok": False,
                "error": f"Query rejected: {sanitized['reason']}",
                "session_id": session_id,
            }
        return {"ok": True, "query": query.strip(), "session_id": session_id}
