"""Tests for Retention Manager."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from self.retention import RetentionManager


class MockStorage:
    def __init__(self) -> None:
        self._records: dict[str, list[dict]] = {
            "observation_event": [],
            "knowledge_object": [],
            "audit_log_entry": [],
        }
        self._deleted: list[str] = []

    def insert(self, rt: str, r: dict) -> str:
        self._records.setdefault(rt, []).append(r)
        return str(r["id"])

    def query(self, rt: str, spec: dict | None = None) -> list[dict]:
        return list(self._records.get(rt, []))

    def delete(self, rt: str, rid: str) -> bool:
        self._deleted.append(rid)
        return True


class MockAuditLog:
    def append(self, **kw: dict) -> None:
        pass


def test_dry_run_no_deletion() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    rm = RetentionManager(storage, audit, {"observation_event": 0.001})
    old = {
        "id": "evt_old",
        "event_type": "test",
        "timestamp": (datetime.now(UTC) - timedelta(days=10)).isoformat(),
    }
    storage.insert("observation_event", old)
    result = rm.enforce(dry_run=True)
    assert "observation_event" in result
    assert result["observation_event"] == 1
    assert len(storage._deleted) == 0


def test_enforce_deletes_expired() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    rm = RetentionManager(storage, audit, {"observation_event": 0.001})
    old = {
        "id": "evt_old",
        "event_type": "test",
        "timestamp": (datetime.now(UTC) - timedelta(days=10)).isoformat(),
    }
    storage.insert("observation_event", old)
    result = rm.enforce(dry_run=False)
    assert result.get("observation_event", 0) == 1


def test_fresh_record_not_expired() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    rm = RetentionManager(storage, audit, {"observation_event": 365})
    fresh = {
        "id": "evt_fresh",
        "event_type": "test",
        "timestamp": datetime.now(UTC).isoformat(),
    }
    storage.insert("observation_event", fresh)
    result = rm.enforce()
    assert result.get("observation_event", 0) == 0
