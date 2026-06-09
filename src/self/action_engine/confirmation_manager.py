"""Confirmation Manager — handles user confirmation for sensitive actions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class ConfirmationManager:
    def __init__(self, timeout_seconds: int = 60) -> None:
        self._pending: dict[str, dict[str, Any]] = {}
        self._timeout = timeout_seconds

    def request_confirmation(self, action: dict[str, Any]) -> str:
        cid = f"cf_{uuid4().hex}"
        self._pending[cid] = {
            "id": cid,
            "action": action,
            "status": "pending",
            "created_at": datetime.now(UTC).isoformat(),
        }
        return cid

    def confirm(self, confirmation_id: str) -> dict[str, Any]:
        entry = self._pending.get(confirmation_id)
        if entry is None:
            return {"ok": False, "error": "Unknown confirmation request"}
        if entry["status"] == "expired":
            return {"ok": False, "error": "Confirmation request expired"}
        entry["status"] = "confirmed"
        return {"ok": True, "confirmation_id": confirmation_id}

    def deny(self, confirmation_id: str) -> dict[str, Any]:
        entry = self._pending.get(confirmation_id)
        if entry is None:
            return {"ok": False, "error": "Unknown confirmation request"}
        entry["status"] = "denied"
        return {"ok": True, "confirmation_id": confirmation_id}

    def is_pending(self, confirmation_id: str) -> bool:
        entry = self._pending.get(confirmation_id)
        if entry is None:
            return False
        if entry["status"] == "expired":
            return False
        created = entry["created_at"]
        elapsed = (datetime.now(UTC) - datetime.fromisoformat(created)).total_seconds()
        if elapsed > self._timeout:
            entry["status"] = "expired"
            return False
        return entry["status"] == "pending"
