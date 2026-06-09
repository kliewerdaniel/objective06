"""Content Aggregator — pulls relevant state for synthesis."""

from __future__ import annotations

from typing import Any


class ContentAggregator:
    def __init__(self, memory: Any, identity_graph: Any) -> None:
        self._memory = memory
        self._graph = identity_graph

    def aggregate(
        self,
        start: str = "",
        end: str = "",
        topic: str = "",
        max_events: int = 50,
        max_knowledge: int = 30,
    ) -> dict[str, Any]:
        events_spec: dict[str, Any] = {"limit": max_events}
        if start:
            events_spec["time_start"] = start
        if end:
            events_spec["time_end"] = end
        events = []
        if hasattr(self._memory, "query_events"):
            events = self._memory.query_events(events_spec)
        knowledge_spec: dict[str, Any] = {"limit": max_knowledge}
        knowledge = []
        if hasattr(self._memory, "query_knowledge"):
            knowledge = self._memory.query_knowledge(knowledge_spec)
        excluded_count = sum(
            1 for k in knowledge if k.get("attributes", {}).get("status") == "archived"
        )
        knowledge = [k for k in knowledge if k.get("attributes", {}).get("status") != "archived"]
        nodes: list[dict[str, Any]] = []
        if hasattr(self._graph, "node_store") and hasattr(self._graph.node_store, "all"):
            all_nodes = self._graph.node_store.all()
            if topic:
                nodes = [n for n in all_nodes if topic.lower() in n.get("name", "").lower()]
            else:
                nodes = all_nodes[:20]
        return {
            "events": events,
            "knowledge": knowledge,
            "nodes": nodes,
            "excluded_count": excluded_count,
            "event_count": len(events),
            "knowledge_count": len(knowledge),
            "node_count": len(nodes),
        }
