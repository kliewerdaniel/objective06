"""Durable append-only event log on DuckDB."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class EventLog:
    def __init__(self, storage: Any, raw_dir: str) -> None:
        self._storage = storage
        self._raw_dir = raw_dir
        Path(raw_dir).mkdir(parents=True, exist_ok=True)

    def append(self, event: dict[str, Any]) -> str:
        raw_path = self._store_raw(event)
        entry = {
            "schema_version": "0.1.0",
            "id": f"el_{uuid4().hex}",
            "event_id": event["id"],
            "timestamp": event.get("timestamp", datetime.now(UTC).isoformat()),
            "source_kind": event.get("source", {}).get("kind", "unknown"),
            "event_type": event.get("event_type", "unknown"),
            "content_hash": event.get("content_hash", ""),
            "raw_payload_ref": raw_path,
        }
        self._storage.insert("event_log_entry", entry)
        return entry["id"]

    def _store_raw(self, event: dict[str, Any]) -> str:
        import json

        event_id = event["id"]
        rel_path = f"{event_id}.json"
        full_path = str(Path(self._raw_dir) / rel_path)
        with open(full_path, "w") as f:
            json.dump(event, f, default=str, indent=2)
        return full_path

    def query_time_range(
        self,
        start: str | None = None,
        end: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        spec: dict[str, Any] = {"limit": limit}
        if start:
            spec["time_start"] = start
        if end:
            spec["time_end"] = end
        return self._storage.query("event_log_entry", spec)

    def reply_from(self, point_in_time: str) -> list[dict[str, Any]]:
        return self._storage.query(
            "event_log_entry",
            {"time_start": point_in_time, "limit": 1000000},
        )

    @property
    def size(self) -> int:
        return self._storage.count("event_log_entry")
