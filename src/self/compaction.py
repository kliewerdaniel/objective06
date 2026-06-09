"""Compaction engine — relevance scoring, tier transitions, archival."""

from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

HOT = "hot"
COLD = "cold"
ARCHIVED = "archived"


class CompactionEngine:
    def __init__(
        self,
        storage: Any,
        audit_log: Any,
        archive_dir: str,
        cold_threshold_days: float = 90.0,
        archive_threshold_days: float = 365.0,
    ) -> None:
        self._storage = storage
        self._audit_log = audit_log
        self._archive_dir = Path(archive_dir)
        self._archive_dir.mkdir(parents=True, exist_ok=True)
        self._cold_threshold = cold_threshold_days * 86400
        self._archive_threshold = archive_threshold_days * 86400

    def score(self, record: dict[str, Any]) -> float:
        recency = self._recency_score(record)
        confidence = record.get("confidence", 0.5)
        return 0.6 * recency + 0.4 * confidence

    def _recency_score(self, record: dict[str, Any]) -> float:
        now = time.time()
        created = record.get("created_at", record.get("timestamp", ""))
        if isinstance(created, str):
            try:
                dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                created_ts = dt.timestamp()
            except (ValueError, TypeError):
                return 0.0
        else:
            return 0.0
        age = now - created_ts
        if age <= 0:
            return 1.0
        return max(0.0, 1.0 - (age / self._cold_threshold))

    def compact_knowledge(self) -> dict[str, int]:
        now = time.time()
        records = self._storage.query("knowledge_object", {"limit": 1000000})
        cold_count = 0
        archive_count = 0

        for record in records:
            created = record.get("created_at", "")
            if isinstance(created, str):
                try:
                    dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    age = now - dt.timestamp()
                except (ValueError, TypeError):
                    continue
            else:
                continue

            attributes = record.get("attributes", {})
            if isinstance(attributes, str):
                try:
                    attributes = json.loads(attributes)
                except (json.JSONDecodeError, ValueError):
                    attributes = {}
            tier = attributes.get("tier", HOT)

            if age > self._archive_threshold and tier != ARCHIVED:
                self._archive_record(record)
                archive_count += 1
            elif age > self._cold_threshold and tier == HOT:
                self._move_to_cold(record)
                cold_count += 1

        self._audit_log.append(
            actor="memory.compaction",
            action="update",
            entity_type="compaction",
            entity_id="run",
            reason=f"Compacted: {cold_count} to cold, {archive_count} archived",
        )
        return {"cold": cold_count, "archived": archive_count}

    def _move_to_cold(self, record: dict[str, Any]) -> None:
        attributes = record.get("attributes", {})
        if isinstance(attributes, str):
            try:
                attributes = json.loads(attributes)
            except (json.JSONDecodeError, ValueError):
                attributes = {}
        attributes["tier"] = COLD
        attributes["compacted_at"] = datetime.now(UTC).isoformat()
        self._storage.update("knowledge_object", record["id"], {"attributes": attributes})

    def _archive_record(self, record: dict[str, Any]) -> None:
        archive_path = self._archive_dir / f"{record['id']}.json"
        with open(archive_path, "w") as f:
            json.dump(record, f, default=str, indent=2)
        attributes = record.get("attributes", {})
        if isinstance(attributes, str):
            try:
                attributes = json.loads(attributes)
            except (json.JSONDecodeError, ValueError):
                attributes = {}
        attributes["tier"] = ARCHIVED
        attributes["archived_at"] = datetime.now(UTC).isoformat()
        attributes["archive_path"] = str(archive_path)
        self._storage.update("knowledge_object", record["id"], {"attributes": attributes})
