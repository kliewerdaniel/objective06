"""Edge Store — CRUD for typed edges between nodes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class EdgeStore:
    def __init__(self, storage: Any, schema_registry: Any) -> None:
        self._storage = storage
        self._registry = schema_registry

    def create(
        self,
        edge_type: str,
        source_id: str,
        target_id: str,
        weight: float = 1.0,
        attributes: dict[str, Any] | None = None,
    ) -> str:
        if not self._registry.is_valid_edge_type(edge_type):
            msg = f"Invalid edge type: {edge_type}"
            raise ValueError(msg)
        now = datetime.now(UTC)
        eid = f"ed_{uuid4().hex}"
        record = {
            "schema_version": "0.1.0",
            "id": eid,
            "type": edge_type,
            "source_id": source_id,
            "target_id": target_id,
            "weight": weight,
            "attributes": attributes or {},
            "created_at": now.isoformat(),
            "valid_from": now.isoformat(),
            "valid_to": None,
            "deprecated": False,
        }
        self._storage.insert("identity_edge", record)
        return eid

    def get(self, edge_id: str) -> dict[str, Any] | None:
        return self._storage.get("identity_edge", edge_id)

    def update(self, edge_id: str, changes: dict[str, Any]) -> bool:
        return self._storage.update("identity_edge", edge_id, changes)

    def delete(self, edge_id: str) -> bool:
        now = datetime.now(UTC).isoformat()
        return self._storage.update("identity_edge", edge_id, {"deprecated": True, "valid_to": now})

    def find_by_source(self, source_id: str) -> list[dict[str, Any]]:
        return self._storage.query("identity_edge", {"source_id": source_id, "limit": 1000})

    def find_by_target(self, target_id: str) -> list[dict[str, Any]]:
        return self._storage.query("identity_edge", {"target_id": target_id, "limit": 1000})

    def find_by_type(self, edge_type: str) -> list[dict[str, Any]]:
        return self._storage.query("identity_edge", {"type": edge_type, "limit": 1000})

    def find_between(self, source_id: str, target_id: str) -> list[dict[str, Any]]:
        results = self._storage.query("identity_edge", {"source_id": source_id, "limit": 1000})
        return [r for r in results if r.get("target_id") == target_id]

    def all(self) -> list[dict[str, Any]]:
        return self._storage.query("identity_edge", {"limit": 10000})
