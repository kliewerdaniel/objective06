"""Action Engine — facade over all action engine components."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .capability_registry import CapabilityRegistry
from .confirmation_manager import ConfirmationManager
from .executor import Executor
from .permission_resolver import PermissionResolver
from .plan_synthesizer import PlanSynthesizer
from .rollback_engine import RollbackEngine


class ActionEngine:
    def __init__(self, storage: Any) -> None:
        self._storage = storage
        self._registry = CapabilityRegistry()
        self._permissions = PermissionResolver()
        self._synthesizer = PlanSynthesizer(self._registry)
        self._rollback = RollbackEngine()
        self._executor = Executor(self._rollback)
        self._confirmations = ConfirmationManager()
        self._user = "default"

    def request(
        self, capability: str, params: dict[str, Any], session_id: str = ""
    ) -> dict[str, Any]:
        if not self._registry.has(capability):
            return {"ok": False, "error": f"Unknown capability: {capability}", "status": "rejected"}
        cap = self._registry.get(capability)
        rid = f"ar_{uuid4().hex}"
        now = datetime.now(UTC).isoformat()
        sensitivity = (cap or {}).get("sensitivity", "safe")
        record = {
            "schema_version": "0.1.0",
            "id": rid,
            "capability": capability,
            "params": params,
            "requested_by": self._user,
            "session_id": session_id,
            "status": "pending",
            "sensitivity": sensitivity,
            "requires_confirmation": sensitivity == "sensitive",
            "created_at": now,
            "updated_at": now,
        }
        self._storage.insert("action_request", record)
        perm = cap.get("required_permission", "") if cap else ""
        check = self._permissions.check(self._user, perm)
        if not check["allowed"]:
            self._storage.update("action_request", rid, {"status": "denied"})
            return {"ok": False, "error": check["reason"], "status": "denied", "request_id": rid}
        if sensitivity == "sensitive":
            cid = self._confirmations.request_confirmation(record)
            return {
                "ok": True,
                "status": "needs_confirmation",
                "request_id": rid,
                "confirmation_id": cid,
            }
        return self._execute(rid, capability, params)

    def confirm(self, confirmation_id: str, request_id: str) -> dict[str, Any]:
        result = self._confirmations.confirm(confirmation_id)
        if not result["ok"]:
            return result
        rec = self._storage.get("action_request", request_id)
        if rec is None:
            return {"ok": False, "error": "Unknown request"}
        return self._execute(request_id, rec["capability"], rec["params"])

    def deny(self, confirmation_id: str) -> dict[str, Any]:
        return self._confirmations.deny(confirmation_id)

    def grant_permission(self, permission: str) -> None:
        self._permissions.grant(self._user, permission)

    def revoke_permission(self, permission: str) -> None:
        self._permissions.revoke(self._user, permission)

    def list_capabilities(self) -> list[dict[str, Any]]:
        return self._registry.list_all()

    def _execute(self, rid: str, capability: str, params: dict[str, Any]) -> dict[str, Any]:
        plan = self._synthesizer.synthesize(capability, params)
        now = datetime.now(UTC).isoformat()
        self._audit(rid, "plan_synthesized", "success", {"plan_id": plan["id"]})
        result = self._executor.execute(plan)
        ar_status = "success" if result["status"] == "success" else "failed"
        ar_record = {
            "schema_version": "0.1.0",
            "id": f"ar_{uuid4().hex}",
            "request_id": rid,
            "status": ar_status,
            "output": result.get("output"),
            "error": result.get("error"),
            "rollback_status": result.get("status") if result["status"] != "success" else None,
            "executed_at": now,
        }
        self._storage.insert("action_result", ar_record)
        self._storage.update("action_request", rid, {"status": ar_status, "updated_at": now})
        self._audit(rid, "execution", ar_status, result)
        return {
            "ok": ar_status == "success",
            "status": ar_status,
            "request_id": rid,
            "output": result.get("output"),
            "error": result.get("error"),
        }

    def _audit(self, request_id: str, step: str, status: str, detail: dict[str, Any]) -> None:
        entry = {
            "schema_version": "0.1.0",
            "id": f"aa_{uuid4().hex}",
            "request_id": request_id,
            "step": step,
            "status": status,
            "detail": detail,
            "timestamp": datetime.now(UTC).isoformat(),
        }
        self._storage.insert("action_audit", entry)
