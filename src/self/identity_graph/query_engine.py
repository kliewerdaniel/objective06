"""Query Engine — high-level graph queries over nodes and edges."""

from __future__ import annotations

from typing import Any


class QueryPattern:
    def __init__(
        self,
        source_type: str | None = None,
        edge_type: str | None = None,
        target_type: str | None = None,
        max_depth: int = 2,
    ) -> None:
        self.source_type = source_type
        self.edge_type = edge_type
        self.target_type = target_type
        self.max_depth = max_depth


class QueryEngine:
    def __init__(self, node_store: Any, edge_store: Any) -> None:
        self._node_store = node_store
        self._edge_store = edge_store

    def find_neighbors(
        self, node_id: str, edge_type: str | None = None, max_depth: int = 1
    ) -> list[dict[str, Any]]:
        if max_depth <= 0:
            return []
        visited = {node_id}
        results: list[dict[str, Any]] = []
        current = {node_id}

        for _depth in range(max_depth):
            next_nodes: set[str] = set()
            for nid in current:
                out_edges = self._edge_store.find_by_source(nid)
                in_edges = self._edge_store.find_by_target(nid)
                for edge in out_edges + in_edges:
                    if edge_type and edge.get("type") != edge_type:
                        continue
                    is_source = edge.get("source_id") == nid
                    neighbor = edge.get("target_id") if is_source else edge.get("source_id")
                    if neighbor and neighbor not in visited:
                        visited.add(neighbor)
                        next_nodes.add(neighbor)
                        node = self._node_store.get(neighbor)
                        if node:
                            results.append(node)
            current = next_nodes
        return results

    def find_path(
        self, source_id: str, target_id: str, max_depth: int = 5
    ) -> list[list[dict[str, Any]]]:
        paths: list[list[dict[str, Any]]] = []
        self._dfs(source_id, target_id, {source_id}, [], paths, max_depth)
        return paths

    def _dfs(
        self,
        current: str,
        target: str,
        visited: set[str],
        path: list[dict[str, Any]],
        paths: list[list[dict[str, Any]]],
        max_depth: int,
    ) -> None:
        if len(path) > max_depth:
            return
        if current == target:
            paths.append(list(path))
            return
        edges = self._edge_store.find_by_source(current)
        for edge in edges:
            nid = edge.get("target_id")
            if nid and nid not in visited:
                visited.add(nid)
                node = self._node_store.get(nid)
                if node:
                    path.append(edge)
                    path.append(node)
                    self._dfs(nid, target, visited, path, paths, max_depth)
                    path.pop()
                    path.pop()
                    visited.discard(nid)

    def count_by_type(self, node_type: str) -> int:
        return len(self._node_store.find_by_type(node_type))

    def count_edges(self, edge_type: str | None = None) -> int:
        if edge_type:
            return len(self._edge_store.find_by_type(edge_type))
        return len(self._edge_store.all())
