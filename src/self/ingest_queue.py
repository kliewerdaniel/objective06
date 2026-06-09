"""Bounded persistent ingest queue with priority lanes."""

from __future__ import annotations

import time
from typing import Any
from uuid import uuid4

HIGH = 0
MEDIUM = 1
LOW = 2


class IngestQueue:
    def __init__(self, storage: Any, max_size: int = 10_000) -> None:
        self._storage = storage
        self._max_size = max_size

    def enqueue(self, event: dict[str, Any], priority: int = MEDIUM) -> str:
        if self._storage.count("ingest_queue") >= self._max_size:
            raise OverflowError(f"Ingest queue full ({self._max_size}), cannot enqueue event")
        entry_id = f"iq_{uuid4().hex}"
        entry = {
            "schema_version": "0.1.0",
            "id": entry_id,
            "event_id": event.get("id", ""),
            "event": event,
            "priority": priority,
            "queued_at": time.time(),
            "status": "queued",
        }
        self._storage.insert("ingest_queue", entry)
        return entry_id

    def dequeue(self, batch_size: int = 10) -> list[dict[str, Any]]:
        results = self._storage.query(
            "ingest_queue",
            {"status": "queued", "order_by": "priority", "limit": batch_size},
        )
        if not results:
            return []
        for r in results:
            self._storage.update("ingest_queue", r["id"], {"status": "processing"})
        return [r["event"] for r in results]

    def mark_done(self, event_id: str) -> None:
        results = self._storage.query(
            "ingest_queue", {"event_id": event_id, "limit": 1, "order_by": "queued_at"}
        )
        for r in results:
            self._storage.update("ingest_queue", r["id"], {"status": "done"})

    def mark_failed(self, event_id: str, error: str = "") -> None:
        results = self._storage.query(
            "ingest_queue", {"event_id": event_id, "limit": 1, "order_by": "queued_at"}
        )
        for r in results:
            self._storage.update("ingest_queue", r["id"], {"status": "failed", "error": error})

    @property
    def size(self) -> int:
        return int(self._storage.count("ingest_queue", {"status": "queued"}))
