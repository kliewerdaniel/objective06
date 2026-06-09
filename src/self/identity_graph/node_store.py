"""Node Store — CRUD for identity nodes."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class NodeStore:
    def __init__(self, storage: Any, schema_registry: Any) -> None:
        self._storage = storage
        self._registry = schema_registry

    def create(
        self,
        node_type: str,
        name: str,
        attributes: dict[str, Any] | None = None,
        aliases: list[str] | None = None,
    ) -> str:
        if not self._registry.is_valid_node_type(node_type):
            msg = f"Invalid node type: {node_type}"
            raise ValueError(msg)
        now = datetime.now(UTC)
        nid = f"id_{uuid4().hex}"
        record = {
            "schema_version": "0.1.0",
            "id": nid,
            "type": node_type,
            "name": name,
            "aliases": aliases or [],
            "attributes": attributes or {},
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "valid_from": now.isoformat(),
            "valid_to": None,
            "deprecated": False,
            "superseded_by": None,
        }
        self._storage.insert("identity_node", record)
        return nid

    def get(self, node_id: str) -> dict[str, Any] | None:
        return self._storage.get("identity_node", node_id)

    def update(self, node_id: str, changes: dict[str, Any]) -> bool:
        changes["updated_at"] = datetime.now(UTC).isoformat()
        return self._storage.update("identity_node", node_id, changes)

    def delete(self, node_id: str) -> bool:
        now = datetime.now(UTC).isoformat()
        return self._storage.update("identity_node", node_id, {"deprecated": True, "valid_to": now})

    def find_by_name(self, name: str, node_type: str | None = None) -> list[dict[str, Any]]:
        spec: dict[str, Any] = {"limit": 100}
        if node_type:
            spec["type"] = node_type
        results = self._storage.query("identity_node", spec)
        return [
            r
            for r in results
            if r.get("name", "").lower() == name.lower()
            or name.lower() in [a.lower() for a in r.get("aliases", [])]
        ]

    def find_by_type(self, node_type: str) -> list[dict[str, Any]]:
        return self._storage.query("identity_node", {"type": node_type, "limit": 1000})

    def all(self) -> list[dict[str, Any]]:
        return self._storage.query("identity_node", {"limit": 10000})
