"""Entity Resolver — matches candidate entities to existing nodes."""

from __future__ import annotations

import difflib
import uuid
from datetime import UTC, datetime
from typing import Any


class EntityResolver:
    def __init__(self, node_store: Any, storage: Any) -> None:
        self._node_store = node_store
        self._storage = storage
        self._similarity_threshold = 0.8

    def resolve(
        self,
        name: str,
        node_type: str | None = None,
        attributes: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        candidates = self.find_candidates(name, node_type)
        if not candidates:
            return None
        best = candidates[0]
        if best["score"] >= self._similarity_threshold:
            return best["node"]
        return None

    def find_candidates(self, name: str, node_type: str | None = None) -> list[dict[str, Any]]:
        all_nodes = (
            self._node_store.find_by_type(node_type) if node_type else self._node_store.all()
        )
        scored: list[dict[str, Any]] = []
        for node in all_nodes:
            score = self._name_similarity(name, node.get("name", ""))
            for alias in node.get("aliases", []):
                alias_score = self._name_similarity(name, alias)
                score = max(score, alias_score)
            if score >= 0.5:
                scored.append({"node": node, "score": score})
        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored

    def _name_similarity(self, a: str, b: str) -> float:
        return difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

    def record_resolution(
        self,
        candidate_name: str,
        resolved_node_id: str,
        source_event_id: str = "",
        method: str = "string_similarity",
    ) -> None:
        self._storage.insert(
            "entity_resolution",
            {
                "schema_version": "0.1.0",
                "id": f"er_{uuid.uuid4().hex}",
                "candidate_name": candidate_name,
                "resolved_node_id": resolved_node_id,
                "source_event_id": source_event_id,
                "method": method,
                "resolved_at": datetime.now(UTC).isoformat(),
            },
        )
