"""Tests for the Action Engine."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from src.self.action_engine import ActionEngine
from src.self.action_engine.capability_registry import CapabilityRegistry
from src.self.action_engine.confirmation_manager import ConfirmationManager
from src.self.action_engine.executor import Executor
from src.self.action_engine.permission_resolver import PermissionResolver
from src.self.action_engine.plan_synthesizer import PlanSynthesizer
from src.self.action_engine.rollback_engine import RollbackEngine


class FakeStorage:
    def __init__(self) -> None:
        self._data: dict[str, list[dict]] = {}

    def insert(self, record_type: str, record: dict) -> str:
        self._data.setdefault(record_type, []).append(record)
        return str(record["id"])

    def get(self, record_type: str, id: str) -> dict | None:
        for r in self._data.get(record_type, []):
            if r.get("id") == id:
                return r
        return None

    def query(self, record_type: str, spec: dict) -> list[dict]:
        return self._data.get(record_type, [])[: spec.get("limit", 100)]

    def update(self, record_type: str, id: str, changes: dict) -> bool:
        for r in self._data.get(record_type, []):
            if r.get("id") == id:
                r.update(changes)
                return True
        return False


# --- Capability Registry ---


def test_registry_has_builtin() -> None:
    reg = CapabilityRegistry()
    assert reg.has("read_file")
    assert reg.has("write_file")
    assert reg.has("list_directory")
    assert not reg.has("unknown")


def test_registry_get() -> None:
    reg = CapabilityRegistry()
    cap = reg.get("read_file")
    assert cap is not None
    assert cap["sensitivity"] == "safe"


def test_registry_list_all() -> None:
    reg = CapabilityRegistry()
    caps = reg.list_all()
    assert len(caps) == 3


# --- Permission Resolver ---


def test_permission_default_deny() -> None:
    res = PermissionResolver()
    check = res.check("user", "fs:read")
    assert check["allowed"] is False


def test_permission_grant() -> None:
    res = PermissionResolver()
    res.grant("user", "fs:read")
    check = res.check("user", "fs:read")
    assert check["allowed"] is True


def test_permission_revoke() -> None:
    res = PermissionResolver()
    res.grant("user", "fs:read")
    res.revoke("user", "fs:read")
    check = res.check("user", "fs:read")
    assert check["allowed"] is False


# --- Plan Synthesizer ---


def test_synthesize_read_file() -> None:
    syn = PlanSynthesizer(CapabilityRegistry())
    plan = syn.synthesize("read_file", {"path": "/tmp/test.txt"})
    assert plan["capability"] == "read_file"
    assert len(plan["steps"]) == 1
    assert plan["steps"][0]["action"] == "read_file"


def test_synthesize_write_file() -> None:
    syn = PlanSynthesizer(CapabilityRegistry())
    plan = syn.synthesize("write_file", {"path": "/tmp/test.txt", "content": "hello"})
    assert len(plan["preconditions"]) == 1
    assert len(plan["postconditions"]) == 1
    assert len(plan["rollback_steps"]) == 1
    assert plan["rollback_steps"][0]["action"] == "delete_file"


def test_synthesize_unknown() -> None:
    syn = PlanSynthesizer(CapabilityRegistry())
    try:
        syn.synthesize("unknown", {})
        assert False, "Should have raised"
    except ValueError:
        pass


# --- Confirmation Manager ---


def test_request_and_confirm() -> None:
    cm = ConfirmationManager(timeout_seconds=60)
    cid = cm.request_confirmation({"capability": "write_file"})
    assert cm.is_pending(cid)
    result = cm.confirm(cid)
    assert result["ok"] is True


def test_request_and_deny() -> None:
    cm = ConfirmationManager(timeout_seconds=60)
    cid = cm.request_confirmation({"capability": "write_file"})
    result = cm.deny(cid)
    assert result["ok"] is True
    assert not cm.is_pending(cid)


def test_unknown_confirmation() -> None:
    cm = ConfirmationManager()
    result = cm.confirm("unknown")
    assert result["ok"] is False


# --- Executor ---


def test_executor_read_file() -> None:
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("test content")
        tmp_path = f.name
    try:
        syn = PlanSynthesizer(CapabilityRegistry())
        rollback = RollbackEngine()
        executor = Executor(rollback)
        plan = syn.synthesize("read_file", {"path": tmp_path})
        result = executor.execute(plan)
        assert result["status"] == "success"
        assert result["output"] == "test content"
    finally:
        os.unlink(tmp_path)


def test_executor_read_nonexistent() -> None:
    syn = PlanSynthesizer(CapabilityRegistry())
    rollback = RollbackEngine()
    executor = Executor(rollback)
    plan = syn.synthesize("read_file", {"path": "/tmp/nonexistent_file_xyz.txt"})
    result = executor.execute(plan)
    assert result["status"] == "failed"


def test_executor_write_then_read() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "test.txt")
        syn = PlanSynthesizer(CapabilityRegistry())
        rollback = RollbackEngine()
        executor = Executor(rollback)
        plan = syn.synthesize("write_file", {"path": path, "content": "hello"})
        result = executor.execute(plan)
        assert result["status"] == "success"
        assert os.path.isfile(path)
        with open(path) as f:
            assert f.read() == "hello"


# --- Rollback Engine ---


def test_rollback_delete_file() -> None:
    with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
        f.write("to delete")
        tmp_path = f.name
    try:
        rollback = RollbackEngine()
        plan = {"rollback_steps": [{"action": "delete_file", "params": {"path": tmp_path}}]}
        result = rollback.execute(plan)
        assert result["status"] == "success"
        assert not os.path.isfile(tmp_path)
    except Exception:
        if os.path.isfile(tmp_path):
            os.unlink(tmp_path)


def test_rollback_idempotent() -> None:
    rollback = RollbackEngine()
    plan = {
        "rollback_steps": [{"action": "delete_file", "params": {"path": "/tmp/nonexistent_xyz"}}],
    }
    result = rollback.execute(plan)
    assert result["status"] == "success"


# --- Action Engine ---


def test_engine_list_capabilities() -> None:
    engine = ActionEngine(FakeStorage())
    caps = engine.list_capabilities()
    assert len(caps) == 3


def test_engine_unknown_capability() -> None:
    engine = ActionEngine(FakeStorage())
    result = engine.request("unknown", {})
    assert result["ok"] is False


def test_engine_permission_denied() -> None:
    engine = ActionEngine(FakeStorage())
    result = engine.request("read_file", {"path": "/tmp/test.txt"})
    assert result["status"] == "denied"


def test_engine_grant_then_execute() -> None:
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("engine test")
        tmp_path = f.name
    try:
        engine = ActionEngine(FakeStorage())
        engine.grant_permission("fs:read")
        result = engine.request("read_file", {"path": tmp_path})
        assert result["ok"] is True
        assert result["output"] == "engine test"
    finally:
        os.unlink(tmp_path)


def test_engine_write_needs_confirmation() -> None:
    engine = ActionEngine(FakeStorage())
    engine.grant_permission("fs:write")
    result = engine.request("write_file", {"path": "/tmp/test.txt", "content": "hello"})
    assert result["status"] == "needs_confirmation"
    assert "confirmation_id" in result


def test_engine_confirm_then_execute() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        path = str(Path(tmp) / "confirmed.txt")
        engine = ActionEngine(FakeStorage())
        engine.grant_permission("fs:write")
        req = engine.request("write_file", {"path": path, "content": "confirmed"})
        assert req["status"] == "needs_confirmation"
        result = engine.confirm(req["confirmation_id"], req["request_id"])
        assert result["ok"] is True
        assert os.path.isfile(path)


def test_engine_audit_trail() -> None:
    storage = FakeStorage()
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as f:
        f.write("audit test")
        tmp_path = f.name
    try:
        engine = ActionEngine(storage)
        engine.grant_permission("fs:read")
        engine.request("read_file", {"path": tmp_path})
        assert len(storage._data.get("action_request", [])) >= 1
        assert len(storage._data.get("action_audit", [])) >= 1
        assert len(storage._data.get("action_result", [])) >= 1
    finally:
        os.unlink(tmp_path)
