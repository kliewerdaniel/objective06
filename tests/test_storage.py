"""Tests for storage subsystem."""

from __future__ import annotations

import tempfile
from pathlib import Path

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
