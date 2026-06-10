"""Sandbox Manager — provides execution isolation for actions."""

from __future__ import annotations

import logging
from typing import Any


class SandboxManager:
    def __init__(self, security: Any = None) -> None:
        self._security = security
        self._log = logging.getLogger("self.sandbox_manager")
        self._active_sandboxes: dict[str, dict[str, Any]] = {}

    def create_sandbox(
        self,
        action_id: str,
        capabilities: list[str] | None = None,
        timeout_seconds: int = 300,
    ) -> dict[str, Any]:
        sandbox_id = f"sandbox_{action_id}"
        sandbox = {
            "id": sandbox_id,
            "action_id": action_id,
            "capabilities": capabilities or [],
            "timeout_seconds": timeout_seconds,
            "created_at": "2024-01-01T00:00:00Z",
            "status": "active",
        }
        self._active_sandboxes[sandbox_id] = sandbox
        self._log.info("Created sandbox %s for action %s", sandbox_id, action_id)
        return sandbox

    def check_permission(
        self,
        sandbox_id: str,
        capability: str,
    ) -> dict[str, Any]:
        sandbox = self._active_sandboxes.get(sandbox_id)
        if not sandbox:
            return {
                "allowed": False,
                "reason": "sandbox_not_found",
                "sandbox_id": sandbox_id,
            }

        if sandbox["status"] != "active":
            return {
                "allowed": False,
                "reason": "sandbox_not_active",
                "sandbox_id": sandbox_id,
                "status": sandbox["status"],
            }

        if capability in sandbox["capabilities"]:
            return {
                "allowed": True,
                "sandbox_id": sandbox_id,
                "capability": capability,
            }

        return {
            "allowed": False,
            "reason": "capability_not_in_sandbox",
            "sandbox_id": sandbox_id,
            "capability": capability,
            "allowed_capabilities": sandbox["capabilities"],
        }

    def close_sandbox(self, sandbox_id: str) -> dict[str, Any]:
        sandbox = self._active_sandboxes.get(sandbox_id)
        if not sandbox:
            return {
                "closed": False,
                "reason": "sandbox_not_found",
                "sandbox_id": sandbox_id,
            }

        sandbox["status"] = "closed"
        self._log.info("Closed sandbox %s", sandbox_id)
        return {
            "closed": True,
            "sandbox_id": sandbox_id,
        }

    def get_sandbox(self, sandbox_id: str) -> dict[str, Any] | None:
        return self._active_sandboxes.get(sandbox_id)

    def list_sandboxes(self) -> list[dict[str, Any]]:
        return list(self._active_sandboxes.values())
