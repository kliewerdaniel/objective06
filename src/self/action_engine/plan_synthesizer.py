"""Plan Synthesizer — creates execution plans with pre/postconditions."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .capability_registry import CapabilityRegistry


class PlanSynthesizer:
    def __init__(self, registry: CapabilityRegistry) -> None:
        self._registry = registry

    def synthesize(self, capability: str, params: dict[str, Any]) -> dict[str, Any]:
        cap = self._registry.get(capability)
        if cap is None:
            msg = f"Unknown capability: {capability}"
            raise ValueError(msg)
        pid = f"plan_{uuid4().hex}"
        plan = {
            "id": pid,
            "capability": capability,
            "params": params,
            "steps": self._build_steps(cap, params),
            "preconditions": self._build_preconditions(cap, params),
            "postconditions": self._build_postconditions(cap, params),
            "rollback_steps": self._build_rollback(cap, params),
            "created_at": datetime.now(UTC).isoformat(),
        }
        return plan

    def _build_steps(self, cap: dict[str, Any], params: dict[str, Any]) -> list[dict[str, Any]]:
        cid = cap["id"]
        if cid == "read_file":
            return [{"action": "read_file", "params": {"path": params.get("path", "")}}]
        if cid == "list_directory":
            return [{"action": "list_directory", "params": {"path": params.get("path", "")}}]
        if cid == "write_file":
            return [
                {
                    "action": "write_file",
                    "params": {
                        "path": params.get("path", ""),
                        "content": params.get("content", ""),
                    },
                }
            ]
        return []

    def _build_preconditions(
        self, cap: dict[str, Any], params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        cid = cap["id"]
        pre: list[dict[str, Any]] = []
        if cid in ("read_file", "write_file", "list_directory"):
            path = params.get("path", "")
            pre.append({"condition": "parent_dir_exists", "params": {"path": str(path)}})
        return pre

    def _build_postconditions(
        self, cap: dict[str, Any], params: dict[str, Any]
    ) -> list[dict[str, Any]]:
        cid = cap["id"]
        if cid == "read_file":
            return [{"condition": "file_readable", "params": {"path": params.get("path", "")}}]
        if cid == "list_directory":
            return [{"condition": "directory_listed", "params": {"path": params.get("path", "")}}]
        if cid == "write_file":
            return [{"condition": "file_exists", "params": {"path": params.get("path", "")}}]
        return []

    def _build_rollback(self, cap: dict[str, Any], params: dict[str, Any]) -> list[dict[str, Any]]:
        cid = cap["id"]
        if cid == "write_file":
            return [{"action": "delete_file", "params": {"path": params.get("path", "")}}]
        return []
