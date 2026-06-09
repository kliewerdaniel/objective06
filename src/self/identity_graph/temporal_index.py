"""Temporal Index — bitemporal queries for nodes and edges."""

from __future__ import annotations

from typing import Any


class TemporalIndex:
    def __init__(self, node_store: Any, edge_store: Any) -> None:
        self._node_store = node_store
        self._edge_store = edge_store

    def as_of(self, timestamp: str, node_type: str | None = None) -> list[dict[str, Any]]:
        nodes = self._node_store.find_by_type(node_type) if node_type else self._node_store.all()
        return [n for n in nodes if self._is_valid_at(n, timestamp)]

    def during(self, start: str, end: str, node_type: str | None = None) -> list[dict[str, Any]]:
        nodes = self._node_store.find_by_type(node_type) if node_type else self._node_store.all()
        return [n for n in nodes if self._overlaps(n, start, end)]

    def edges_as_of(self, timestamp: str, edge_type: str | None = None) -> list[dict[str, Any]]:
        edges = self._edge_store.find_by_type(edge_type) if edge_type else self._edge_store.all()
        return [e for e in edges if self._is_valid_at(e, timestamp)]

    def _is_valid_at(self, record: dict[str, Any], timestamp: str) -> bool:
        valid_from = record.get("valid_from", "")
        valid_to = record.get("valid_to")
        if record.get("deprecated", False):
            return False
        if timestamp < valid_from:
            return False
        if valid_to and timestamp > valid_to:
            return False
        return True

    def _overlaps(self, record: dict[str, Any], start: str, end: str) -> bool:
        valid_from = record.get("valid_from", "")
        valid_to = record.get("valid_to")
        if record.get("deprecated", False):
            return False
        if valid_to and valid_to < start:
            return False
        if end < valid_from:
            return False
        return True
