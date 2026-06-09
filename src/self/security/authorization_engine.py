"""Authorization Engine — capability-based permission resolution."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

SENSITIVITY_MAP: dict[str, str] = {
    "read.filesystem": "low",
    "write.filesystem": "medium",
    "network.read": "medium",
    "network.write": "high",
    "execute.command": "high",
    "model.invoke": "low",
    "email.read": "medium",
    "email.send": "high",
    "github.read": "low",
    "github.write": "high",
    "fs:read": "low",
    "fs:write": "medium",
}


class AuthorizationEngine:
    def __init__(self, storage: Any) -> None:
        self._storage = storage

    def grant(self, user: str, capability: str, scope: str = "*", ttl_hours: int = 0) -> str:
        now = datetime.now(UTC)
        gid = f"pg_{uuid4().hex}"
        expires = (now + timedelta(hours=ttl_hours)).isoformat() if ttl_hours > 0 else ""
        record = {
            "schema_version": "0.1.0",
            "id": gid,
            "user": user,
            "capability": capability,
            "scope": scope,
            "granted_at": now.isoformat(),
            "expires_at": expires or None,
            "revoked": False,
        }
        self._storage.insert("permission_grant", record)
        return gid

    def check(self, user: str, capability: str) -> dict[str, Any]:
        grants = self._storage.query("permission_grant", {"user": user, "limit": 1000})
        now = datetime.now(UTC)
        for g in grants:
            if g.get("revoked"):
                continue
            if g["capability"] != capability and g["capability"] != "*":
                continue
            if g.get("expires_at"):
                expires = datetime.fromisoformat(g["expires_at"])
                if now > expires:
                    continue
            return {
                "allowed": True,
                "reason": f"Granted by {g['id']}",
                "sensitivity": SENSITIVITY_MAP.get(capability, "medium"),
            }
        return {
            "allowed": False,
            "reason": f"Default deny: no grant for '{capability}'",
            "sensitivity": SENSITIVITY_MAP.get(capability, "medium"),
        }

    def revoke(self, grant_id: str) -> bool:
        return self._storage.update("permission_grant", grant_id, {"revoked": True})
