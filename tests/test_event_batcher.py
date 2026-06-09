"""Tests for Event Batcher."""

from __future__ import annotations

from self.event_batcher import EventBatcher


def _event(eid: str, kind: str = "filesystem", ts: int = 0) -> dict:
    return {
        "id": eid,
        "event_type": "file.modified",
        "source": {"kind": kind, "identifier": "/tmp"},
        "monotonic_ts": ts,
        "payload": {"summary": f"event {eid}"},
    }


def test_time_batches_empty() -> None:
    b = EventBatcher()
    assert b.time_batches([]) == []


def test_time_batches_single() -> None:
    b = EventBatcher(max_batch_size=10)
    events = [_event("e1", ts=1)]
    batches = b.time_batches(events)
    assert len(batches) == 1
    assert len(batches[0]) == 1


def test_time_batches_max_size() -> None:
    b = EventBatcher(max_batch_size=3)
    events = [_event(f"e{i}", ts=i) for i in range(10)]
    batches = b.time_batches(events)
    assert len(batches) == 4
    assert all(len(b) <= 3 for b in batches)


def test_source_batches() -> None:
    b = EventBatcher(max_batch_size=10)
    events = [
        _event("e1", kind="filesystem"),
        _event("e2", kind="git"),
        _event("e3", kind="filesystem"),
    ]
    batches = b.source_batches(events)
    assert len(batches) == 2
    fs_events = [e for batch in batches for e in batch if e["source"]["kind"] == "filesystem"]
    assert len(fs_events) == 2


def test_format_events() -> None:
    b = EventBatcher()
    events = [_event("e1", ts=1)]
    text = b.format_events(events)
    assert "event e1" in text
