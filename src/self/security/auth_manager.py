"""Auth Manager — token-based authentication with sessions."""

from __future__ import annotations

import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4


class AuthManager:
    def __init__(self, storage: Any, session_ttl_hours: int = 24) -> None:
        self._storage = storage
        self._ttl = timedelta(hours=session_ttl_hours)

    def authenticate(self, user: str, key: str) -> dict[str, Any]:
        now = datetime.now(UTC)
        expires = now + self._ttl
        token = f"tok_{secrets.token_hex(32)}"
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        sid = f"auth_{uuid4().hex}"
        record = {
            "schema_version": "0.1.0",
            "id": sid,
            "user": user,
            "token_hash": token_hash,
            "created_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "revoked": False,
        }
        self._storage.insert("auth_session", record)
        return {
            "ok": True,
            "session_id": sid,
            "token": token,
            "user": user,
            "expires_at": expires.isoformat(),
        }

    def validate(self, token: str) -> dict[str, Any]:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        results = self._storage.query("auth_session", {"limit": 100})
        now = datetime.now(UTC)
        for session in results:
            if session.get("token_hash") == token_hash:
                if session.get("revoked"):
                    return {"ok": False, "error": "Session revoked"}
                expires = datetime.fromisoformat(session["expires_at"])
                if now > expires:
                    return {"ok": False, "error": "Session expired"}
                return {"ok": True, "session_id": session["id"], "user": session["user"]}
        return {"ok": False, "error": "Invalid token"}

    def revoke(self, session_id: str) -> bool:
        return self._storage.update("auth_session", session_id, {"revoked": True})
