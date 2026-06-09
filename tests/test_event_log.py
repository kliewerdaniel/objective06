"""Tests for durable event log."""

from __future__ import annotations

import tempfile
from pathlib import Path

from self.event_log import EventLog
from self.schemas import Actor, ObservationEvent, Payload, Provenance, Source
from self.storage import DuckDBAdapter


def _make_env() -> tuple[DuckDBAdapter, EventLog, str, str]:
    tmp_db = tempfile.mktemp(suffix=".duckdb")
    tmp_raw = tempfile.mktemp(suffix="_raw")
    Path(tmp_raw).mkdir(parents=True, exist_ok=True)
    storage = DuckDBAdapter(tmp_db)
    event_log = EventLog(storage=storage, raw_dir=tmp_raw)
    return storage, event_log, tmp_db, tmp_raw


def _make_event() -> dict:
    ev = ObservationEvent(
        event_type="git.commit",
        source=Source(kind="git", identifier="/repo", adapter="git_hooks", adapter_version="0.1.0"),
        actor=Actor(kind="user", identifier="dev"),
        payload=Payload(summary="commit", data={"msg": "fix bug"}),
        provenance=Provenance(producer="observer.git", producer_version="0.1.0"),
    )
    return ev.model_dump(mode="json")


def test_append_event() -> None:
    storage, event_log, db_path, raw_dir = _make_env()
    try:
        event = _make_event()
        storage.insert("observation_event", event)
        entry_id = event_log.append(event)
        assert entry_id.startswith("el_")
        assert event_log.size == 1
    finally:
        storage.close()
        Path(db_path).unlink(missing_ok=True)
        for p in Path(raw_dir).iterdir():
            p.unlink()
        Path(raw_dir).rmdir()


def test_time_range_query() -> None:
    storage, event_log, db_path, raw_dir = _make_env()
    try:
        event1 = _make_event()
        event2 = _make_event()
        storage.insert("observation_event", event1)
        event_log.append(event1)
        storage.insert("observation_event", event2)
        event_log.append(event2)

        results = event_log.query_time_range(limit=10)
        assert len(results) == 2
    finally:
        storage.close()
        Path(db_path).unlink(missing_ok=True)
        for p in Path(raw_dir).iterdir():
            p.unlink()
        Path(raw_dir).rmdir()
