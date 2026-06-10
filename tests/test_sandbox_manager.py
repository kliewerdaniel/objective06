"""Tests for sandbox_manager module."""

from __future__ import annotations

from self.sandbox_manager import SandboxManager


def test_create_sandbox() -> None:
    manager = SandboxManager()
    sandbox = manager.create_sandbox("action_123", capabilities=["read_file"])
    assert sandbox["id"] == "sandbox_action_123"
    assert sandbox["action_id"] == "action_123"
    assert sandbox["capabilities"] == ["read_file"]
    assert sandbox["status"] == "active"


def test_check_permission_allowed() -> None:
    manager = SandboxManager()
    sandbox = manager.create_sandbox("action_123", capabilities=["read_file"])
    result = manager.check_permission(sandbox["id"], "read_file")
    assert result["allowed"] is True


def test_check_permission_denied() -> None:
    manager = SandboxManager()
    sandbox = manager.create_sandbox("action_123", capabilities=["read_file"])
    result = manager.check_permission(sandbox["id"], "write_file")
    assert result["allowed"] is False
    assert result["reason"] == "capability_not_in_sandbox"


def test_check_permission_sandbox_not_found() -> None:
    manager = SandboxManager()
    result = manager.check_permission("nonexistent", "read_file")
    assert result["allowed"] is False
    assert result["reason"] == "sandbox_not_found"


def test_close_sandbox() -> None:
    manager = SandboxManager()
    sandbox = manager.create_sandbox("action_123")
    result = manager.close_sandbox(sandbox["id"])
    assert result["closed"] is True


def test_get_sandbox() -> None:
    manager = SandboxManager()
    sandbox = manager.create_sandbox("action_123")
    retrieved = manager.get_sandbox(sandbox["id"])
    assert retrieved is not None
    assert retrieved["id"] == sandbox["id"]


def test_list_sandboxes() -> None:
    manager = SandboxManager()
    manager.create_sandbox("action_1")
    manager.create_sandbox("action_2")
    sandboxes = manager.list_sandboxes()
    assert len(sandboxes) == 2
