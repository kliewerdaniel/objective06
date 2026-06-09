"""Merge Engine — merges duplicate nodes with provenance preservation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any


class MergeEngine:
    def __init__(self, node_store: Any, edge_store: Any, storage: Any, audit_log: Any) -> None:
        self._node_store = node_store
        self._edge_store = edge_store
        self._storage = storage
        self._audit_log = audit_log

    def merge(self, keep_id: str, merge_id: str, reason: str = "") -> bool:
        keep = self._node_store.get(keep_id)
        merge = self._node_store.get(merge_id)
        if not keep or not merge:
            return False

        merged_aliases = list(
            set(keep.get("aliases", []) + merge.get("aliases", []) + [merge.get("name", "")])
        )
        merged_attrs = {**(merge.get("attributes", {}) or {}), **(keep.get("attributes", {}) or {})}

        self._node_store.update(
            keep_id,
            {
                "aliases": merged_aliases,
                "attributes": merged_attrs,
                "updated_at": datetime.now(UTC).isoformat(),
            },
        )
        self._node_store.update(
            merge_id,
            {
                "deprecated": True,
                "superseded_by": keep_id,
                "valid_to": datetime.now(UTC).isoformat(),
            },
        )

        merge_edges = self._edge_store.find_by_source(merge_id)
        for edge in merge_edges:
            self._edge_store.update(edge["id"], {"source_id": keep_id})
        merge_edges_target = self._edge_store.find_by_target(merge_id)
        for edge in merge_edges_target:
            self._edge_store.update(edge["id"], {"target_id": keep_id})

        self._audit_log.append(
            actor="identity_graph.merge_engine",
            action="update",
            entity_type="identity_node",
            entity_id=keep_id,
            reason=f"Merged node {merge_id} into {keep_id}: {reason}",
        )
        return True
