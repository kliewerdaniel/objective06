"""Tests for the Ingest Queue."""

from __future__ import annotations

import pytest

from self.ingest_queue import IngestQueue


def test_enqueue_dequeue(storage: object) -> None:
    queue = IngestQueue(storage, max_size=100)
    event = {"id": "evt_001", "event_type": "test"}
    qid = queue.enqueue(event, priority=0)
    assert qid.startswith("iq_")
    assert queue.size == 1

    batch = queue.dequeue(batch_size=10)
    assert len(batch) == 1
    assert batch[0]["id"] == "evt_001"


def test_priority_ordering(storage: object) -> None:
    queue = IngestQueue(storage)
    queue.enqueue({"id": "evt_002"}, priority=2)
    queue.enqueue({"id": "evt_001"}, priority=0)
    batch = queue.dequeue(batch_size=10)
    assert batch[0]["id"] == "evt_001"


def test_mark_done(storage: object) -> None:
    queue = IngestQueue(storage)
    queue.enqueue({"id": "evt_001"})
    queue.mark_done("evt_001")
    assert queue.size == 0


def test_mark_failed(storage: object) -> None:
    queue = IngestQueue(storage)
    queue.enqueue({"id": "evt_001"})
    queue.mark_failed("evt_001", "timeout")
    assert queue.size == 0


def test_max_size(storage: object) -> None:
    queue = IngestQueue(storage, max_size=2)
    queue.enqueue({"id": "evt_001"})
    queue.enqueue({"id": "evt_002"})
    with pytest.raises(OverflowError):
        queue.enqueue({"id": "evt_003"})
