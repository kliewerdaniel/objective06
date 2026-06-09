"""Retention Manager — per-type retention policies, enforced removal."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

DEFAULT_RETENTION_DAYS: dict[str, float] = {
    "observation_event": 365.0,
    "event_log_entry": 365.0,
    "knowledge_object": 730.0,
    "audit_log_entry": 1825.0,
}


class RetentionManager:
    def __init__(
        self,
        storage: Any,
        audit_log: Any,
        policies: dict[str, float] | None = None,
    ) -> None:
        self._storage = storage
        self._audit_log = audit_log
        self._policies = {**DEFAULT_RETENTION_DAYS, **(policies or {})}

    def set_policy(self, record_type: str, days: float) -> None:
        self._policies[record_type] = days

    def get_policy(self, record_type: str) -> float:
        return self._policies.get(record_type, 0.0)

    def enforce(self, dry_run: bool = False) -> dict[str, int]:
        now = time.time()
        removed: dict[str, int] = {}

        for record_type, max_age_days in self._policies.items():
            if max_age_days <= 0:
                continue
            max_age_sec = max_age_days * 86400
            records = self._storage.query(record_type, {"limit": 1000000})
            count = 0
            for record in records:
                ts_str = record.get("timestamp", record.get("created_at", ""))
                if not ts_str:
                    continue
                try:
                    dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                    age = now - dt.timestamp()
                except (ValueError, TypeError):
                    continue
                if age > max_age_sec:
                    if not dry_run:
                        self._storage.delete(record_type, record["id"])
                        self._audit_log.append(
                            actor="memory.retention",
                            action="delete",
                            entity_type=record_type,
                            entity_id=record["id"],
                            reason=f"Retention policy: {max_age_days} days exceeded",
                        )
                    count += 1
            if count > 0:
                removed[record_type] = count

        if not dry_run and removed:
            self._audit_log.append(
                actor="memory.retention",
                action="delete",
                entity_type="retention_run",
                entity_id="enforce",
                reason=f"Removed {sum(removed.values())} records: {removed}",
            )
        return removed
