"""Permission Resolver — determine whether actions are permitted."""

from __future__ import annotations

from typing import Any


class PermissionResolver:
    def __init__(self) -> None:
        self._grants: dict[str, set[str]] = {}
        self._default_deny = True

    def grant(self, user: str, permission: str) -> None:
        self._grants.setdefault(user, set()).add(permission)

    def revoke(self, user: str, permission: str) -> None:
        self._grants.get(user, set()).discard(permission)

    def check(self, user: str, required_permission: str) -> dict[str, Any]:
        user_grants = self._grants.get(user, set())
        if required_permission in user_grants:
            return {"allowed": True, "reason": "Explicit grant"}
        if self._default_deny:
            reason = f"Default deny: user '{user}' lacks '{required_permission}'"
            return {"allowed": False, "reason": reason}
        return {"allowed": True, "reason": "Default allow"}
