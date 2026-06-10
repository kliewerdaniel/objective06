"""Tests for storage subsystem."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from self.schemas import Actor, ObservationEvent, Payload, Provenance, Source
from self.storage import DuckDBAdapter, SchemaValidator


def _make_event(overrides: dict | None = None) -> dict:
    src = Source(
        kind="filesystem",
        identifier="/tmp/test",
        adapter="test",
        adapter_version="0.1.0",
    )
    base = ObservationEvent(
        event_type="file.modified",
        source=src,
        actor=Actor(kind="user", identifier="user"),
        payload=Payload(summary="test", data={"msg": "hello"}),
        provenance=Provenance(producer="test", producer_version="0.1.0"),
    ).model_dump(mode="json")
    if overrides:
        base.update(overrides)
    return base


def _make_adapter() -> tuple[DuckDBAdapter, str]:
    tmp = tempfile.mktemp(suffix=".duckdb")
    adapter = DuckDBAdapter(tmp)
    return adapter, tmp


def test_insert_and_get() -> None:
    adapter, path = _make_adapter()
    try:
        event = _make_event()
        event_id = adapter.insert("observation_event", event)
        retrieved = adapter.get("observation_event", event_id)
        assert retrieved is not None
        assert retrieved["id"] == event_id
        assert retrieved["event_type"] == "file.modified"
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_query_by_type() -> None:
    adapter, path = _make_adapter()
    try:
        for i in range(3):
            ev = _make_event({"event_type": f"test.type.{i}"})
            adapter.insert("observation_event", ev)
        results = adapter.query("observation_event", {"limit": 10})
        assert len(results) == 3
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_insert_audit_entry() -> None:
    adapter, path = _make_adapter()
    try:
        entry: dict[str, object] = {
            "schema_version": "0.1.0",
            "id": "aud_test123",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "system",
            "action": "create",
            "entity_type": "test",
            "entity_id": "test_001",
            "before_hash": None,
            "after_hash": None,
            "reason": "test entry",
            "prev_hash": None,
            "metadata": {},
        }
        adapter.insert("audit_log_entry", entry)
        got = adapter.get("audit_log_entry", "aud_test123")
        assert got is not None
        assert got["actor"] == "system"
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_update_record() -> None:
    adapter, path = _make_adapter()
    try:
        event = _make_event({"tags": ["initial"]})
        event_id = adapter.insert("observation_event", event)
        adapter.update("observation_event", event_id, {"tags": ["updated"]})
        got = adapter.get("observation_event", event_id)
        assert got is not None
        assert got["tags"] == ["updated"]
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_delete_record() -> None:
    adapter, path = _make_adapter()
    try:
        event = _make_event()
        event_id = adapter.insert("observation_event", event)
        adapter.delete("observation_event", event_id)
        assert adapter.get("observation_event", event_id) is None
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_schema_validator() -> None:
    validator = SchemaValidator()
    valid_event = _make_event()
    assert validator.is_valid("observation_event", valid_event)

    invalid = {"bad": "data"}
    assert not validator.is_valid("observation_event", invalid)


def test_count() -> None:
    adapter, path = _make_adapter()
    try:
        for i in range(5):
            adapter.insert("observation_event", _make_event({"event_type": f"test.{i}"}))
        assert adapter.count("observation_event") == 5
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_queue_write_update() -> None:
    adapter, path = _make_adapter()
    try:
        # Create a record to update
        event = _make_event({"tags": ["initial"]})
        event_id = adapter.insert("observation_event", event)

        # Queue an UPDATE operation
        write_id = adapter.queue_write(
            record_type="observation_event",
            operation="UPDATE",
            record_id=event_id,
            data={"tags": ["updated"]},
            priority=1,
        )

        # Verify it's in the pending queue
        pending = adapter.get_pending_writes()
        assert len(pending) == 1
        assert pending[0]["record_type"] == "observation_event"
        assert pending[0]["operation"] == "UPDATE"

        # Process the write queue
        processed = adapter.process_write_queue()
        assert len(processed) == 1

        # Verify the update was applied
        updated = adapter.get("observation_event", event_id)
        assert updated is not None
        assert updated["tags"] == ["updated"]

        # Verify the write queue entry is now completed
        completed = adapter.get("write_queue", write_id)
        assert completed is not None
        assert completed["status"] == "completed"
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_queue_write_delete() -> None:
    adapter, path = _make_adapter()
    try:
        # Create a record to delete
        event = _make_event()
        event_id = adapter.insert("observation_event", event)

        # Queue a DELETE operation
        write_id = adapter.queue_write(
            record_type="observation_event",
            operation="DELETE",
            record_id=event_id,
            data={},
            priority=2,
        )

        # Process the write queue
        processed = adapter.process_write_queue()
        assert len(processed) == 1

        # Verify the record was deleted
        deleted = adapter.get("observation_event", event_id)
        assert deleted is None

        # Verify the write queue entry is now completed
        completed = adapter.get("write_queue", write_id)
        assert completed is not None
        assert completed["status"] == "completed"
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_queue_write_priority() -> None:
    adapter, path = _make_adapter()
    try:
        # Queue writes with different priorities
        for priority in [3, 1, 2]:
            event = _make_event({"tags": [f"priority_{priority}"]})
            event_id = adapter.insert("observation_event", event)
            adapter.queue_write(
                record_type="observation_event",
                operation="UPDATE",
                record_id=event_id,
                data={},
                priority=priority,
            )

        # Process all writes
        adapter.process_write_queue()

        # Verify all updates were applied
        for priority in [1, 2, 3]:
            result = adapter.query(
                "observation_event", {"tags": [f"priority_{priority}"], "limit": 1}
            )
            assert len(result) == 1
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_queue_write_append_bypasses() -> None:
    """Verify that INSERT operations bypass the write queue."""
    adapter, path = _make_adapter()
    try:
        # Direct INSERT should work without queuing
        event = _make_event({"event_type": "test.insert_bypass"})
        event_id = adapter.insert("observation_event", event)

        # Verify the record was inserted directly
        retrieved = adapter.get("observation_event", event_id)
        assert retrieved is not None
        assert retrieved["event_type"] == "test.insert_bypass"

        # Verify no write queue entry was created
        pending = adapter.get_pending_writes()
        assert len(pending) == 0
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)


def test_queue_write_invalid_operation() -> None:
    """Verify that invalid operations raise ValueError."""
    adapter, path = _make_adapter()
    try:
        with pytest.raises(ValueError, match="Unsupported operation"):
            adapter.queue_write(
                record_type="observation_event",
                operation="INSERT",  # Invalid
                record_id="test",
                data={},
            )
    finally:
        adapter.close()
        Path(path).unlink(missing_ok=True)
