"""Rollback Engine — reverts side effects from failed actions."""

from __future__ import annotations

import os
from typing import Any


class RollbackEngine:
    def execute(self, plan: dict[str, Any]) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        rollback_steps = plan.get("rollback_steps", [])
        for step in reversed(rollback_steps):
            result = self._run_rollback_step(step)
            results.append(result)
        all_ok = all(r["ok"] for r in results)
        return {"status": "success" if all_ok else "partial", "results": results}

    def _run_rollback_step(self, step: dict[str, Any]) -> dict[str, Any]:
        action = step.get("action", "")
        params = step.get("params", {})
        if action == "delete_file":
            return self._delete_file(params.get("path", ""))
        return {"ok": False, "error": f"Unknown rollback action: {action}"}

    @staticmethod
    def _delete_file(path: str) -> dict[str, Any]:
        try:
            if os.path.isfile(path):
                os.remove(path)
                return {"ok": True, "output": f"Deleted: {path}"}
            return {"ok": True, "output": f"File did not exist: {path}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
