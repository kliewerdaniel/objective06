"""Tests for Snapshot Manager."""

from __future__ import annotations

import tempfile
from pathlib import Path

from self.snapshot_manager import SnapshotManager


class MockStorage:
    def __init__(self) -> None:
        self._records: dict[str, list[dict]] = {
            "observation_event": [],
            "knowledge_object": [],
            "audit_log_entry": [],
        }

    def insert(self, rt: str, r: dict) -> str:
        self._records.setdefault(rt, []).append(r)
        return str(r["id"])

    def query(self, rt: str, spec: dict | None = None) -> list[dict]:
        return list(self._records.get(rt, []))


class MockAuditLog:
    def append(self, **kw: dict) -> None:
        pass


def test_create_and_list_snapshots() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MockStorage()
        audit = MockAuditLog()
        sm = SnapshotManager(storage, audit, tmpdir)
        manifest = sm.create_snapshot(name="test-snap", description="unit test")
        assert manifest["name"] == "test-snap"
        assert manifest["type"] == "memory_snapshot"
        assert manifest["event_count"] == 0
        snapshots = sm.list_snapshots()
        assert len(snapshots) == 1


def test_snapshot_contains_data() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MockStorage()
        storage.insert("observation_event", {"id": "evt_001", "event_type": "test"})
        storage.insert("knowledge_object", {"id": "ko_001", "type": "belief", "name": "test"})
        audit = MockAuditLog()
        sm = SnapshotManager(storage, audit, tmpdir)
        manifest = sm.create_snapshot()
        assert manifest["event_count"] == 1
        assert manifest["knowledge_object_count"] == 1


def test_snapshot_persists_to_disk() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MockStorage()
        audit = MockAuditLog()
        sm = SnapshotManager(storage, audit, tmpdir)
        sm.create_snapshot()
        assert len(list(Path(tmpdir).iterdir())) == 1
