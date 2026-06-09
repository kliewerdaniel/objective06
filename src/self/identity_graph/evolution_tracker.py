"""Evolution Tracker — records and queries attribute changes over time."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class EvolutionTracker:
    def __init__(self, node_store: Any, edge_store: Any, storage: Any) -> None:
        self._node_store = node_store
        self._edge_store = edge_store
        self._storage = storage

    def record_change(
        self,
        entity_type: str,
        entity_id: str,
        attribute: str,
        old_value: Any,
        new_value: Any,
        reason: str = "",
    ) -> str:
        cid = f"ch_{uuid4().hex}"
        record = {
            "schema_version": "0.1.0",
            "id": cid,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "attribute": attribute,
            "old_value": old_value,
            "new_value": new_value,
            "changed_at": datetime.now(UTC).isoformat(),
            "reason": reason,
        }
        self._storage.insert("attribute_change", record)
        return cid

    def history(self, entity_id: str) -> list[dict[str, Any]]:
        return self._storage.query(
            "attribute_change",
            {"entity_id": entity_id, "limit": 1000, "order_by": "timestamp"},
        )

    def diff(self, entity_id: str, from_time: str, to_time: str) -> list[dict[str, Any]]:
        all_changes = self.history(entity_id)
        return [c for c in all_changes if from_time <= c.get("changed_at", "") <= to_time]
