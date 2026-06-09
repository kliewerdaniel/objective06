"""Executor — runs action plans with precondition evaluation."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .rollback_engine import RollbackEngine


class Executor:
    def __init__(self, rollback_engine: RollbackEngine) -> None:
        self._rollback = rollback_engine

    def execute(self, plan: dict[str, Any]) -> dict[str, Any]:
        preconditions = plan.get("preconditions", [])
        for pre in preconditions:
            check = self._check_precondition(pre)
            if not check["ok"]:
                return {
                    "status": "failed",
                    "error": f"Precondition failed: {check['reason']}",
                    "output": None,
                }

        results: list[dict[str, Any]] = []
        for step in plan.get("steps", []):
            result = self._run_step(step)
            results.append(result)
            if not result["ok"]:
                self._rollback.execute(plan)
                return {
                    "status": "failed",
                    "error": f"Step failed: {result.get('error', '')}",
                    "output": results,
                }

        postconditions = plan.get("postconditions", [])
        for post in postconditions:
            check = self._check_postcondition(post)
            if not check["ok"]:
                self._rollback.execute(plan)
                return {
                    "status": "rollback",
                    "error": f"Postcondition failed: {check['reason']}",
                    "output": results,
                }

        output = results[-1].get("output") if results else None
        return {"status": "success", "output": output, "error": None}

    def _check_precondition(self, pre: dict[str, Any]) -> dict[str, Any]:
        cond = pre.get("condition", "")
        params = pre.get("params", {})
        if cond == "parent_dir_exists":
            path = params.get("path", "")
            parent = str(Path(path).parent)
            if os.path.isdir(parent):
                return {"ok": True, "reason": ""}
            return {"ok": False, "reason": f"Parent directory does not exist: {parent}"}
        return {"ok": True, "reason": ""}

    def _check_postcondition(self, post: dict[str, Any]) -> dict[str, Any]:
        cond = post.get("condition", "")
        params = post.get("params", {})
        if cond in ("file_exists", "file_readable"):
            path = params.get("path", "")
            if os.path.isfile(path):
                return {"ok": True, "reason": ""}
            return {"ok": False, "reason": f"File does not exist: {path}"}
        if cond == "directory_listed":
            path = params.get("path", "")
            if os.path.isdir(path):
                return {"ok": True, "reason": ""}
            return {"ok": False, "reason": f"Directory does not exist: {path}"}
        return {"ok": True, "reason": ""}

    def _run_step(self, step: dict[str, Any]) -> dict[str, Any]:
        action = step.get("action", "")
        params = step.get("params", {})
        if action == "read_file":
            return self._read_file(params.get("path", ""))
        if action == "list_directory":
            return self._list_directory(params.get("path", ""))
        if action == "write_file":
            return self._write_file(params.get("path", ""), params.get("content", ""))
        return {"ok": False, "error": f"Unknown action: {action}"}

    @staticmethod
    def _read_file(path: str) -> dict[str, Any]:
        try:
            with open(path) as f:
                content = f.read()
            return {"ok": True, "output": content}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    def _list_directory(path: str) -> dict[str, Any]:
        try:
            entries = os.listdir(path)
            return {"ok": True, "output": entries}
        except Exception as e:
            return {"ok": False, "error": str(e)}

    @staticmethod
    def _write_file(path: str, content: str) -> dict[str, Any]:
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w") as f:
                f.write(content)
            return {"ok": True, "output": f"Written {len(content)} bytes to {path}"}
        except Exception as e:
            return {"ok": False, "error": str(e)}
