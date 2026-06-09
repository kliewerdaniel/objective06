"""Query Router — route sub-queries to appropriate subsystems."""

from __future__ import annotations

from typing import Any


class QueryRouter:
    def __init__(
        self, memory: Any, identity_graph: Any, persona_engine: Any, model_client: Any
    ) -> None:
        self._memory = memory
        self._graph = identity_graph
        self._persona = persona_engine
        self._model = model_client

    def route(
        self, intent: str, query: str, session_context: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        if intent == "factual_retrieval":
            return self._handle_factual(query)
        if intent == "entity_exploration":
            return self._handle_entity(query)
        if intent == "summary_request":
            return self._handle_summary()
        if intent == "reflection_request":
            return self._handle_reflection()
        if intent == "prediction_request":
            return self._handle_prediction()
        if intent == "meta_question":
            return self._handle_meta(session_context)
        return self._handle_conversation(query)

    def _handle_factual(self, query: str) -> dict[str, Any]:
        events = (
            self._memory.query_events({"limit": 20})
            if hasattr(self._memory, "query_events")
            else []
        )
        knowledge = (
            self._memory.query_knowledge({"limit": 10})
            if hasattr(self._memory, "query_knowledge")
            else []
        )
        return {"source": "memory", "events": events, "knowledge": knowledge}

    def _handle_entity(self, query: str) -> dict[str, Any]:
        nodes = []
        if hasattr(self._graph, "node_store"):
            words = query.split()
            for word in words:
                found = self._graph.node_store.find_by_name(word)
                nodes.extend(found)
        if not nodes:
            nodes = (
                self._graph.node_store.all()
                if hasattr(self._graph, "node_store") and hasattr(self._graph.node_store, "all")
                else []
            )
        return {"source": "identity_graph", "nodes": nodes[:20]}

    def _handle_summary(self) -> dict[str, Any]:
        knowledge = (
            self._memory.query_knowledge({"limit": 20})
            if hasattr(self._memory, "query_knowledge")
            else []
        )
        return {"source": "memory", "knowledge": knowledge}

    def _handle_reflection(self) -> dict[str, Any]:
        trajectory = self._persona.trajectory() if hasattr(self._persona, "trajectory") else []
        current = (
            self._persona.current_vector() if hasattr(self._persona, "current_vector") else None
        )
        result: dict[str, Any] = {"source": "persona", "trajectory": trajectory}
        if current:
            result["current_vector"] = current
        return result

    def _handle_prediction(self) -> dict[str, Any]:
        return {"source": "persona", "prediction": "Prediction not yet implemented"}

    def _handle_meta(self, session_context: dict[str, Any] | None) -> dict[str, Any]:
        return {"source": "system", "context": session_context or {}}

    def _handle_conversation(self, query: str) -> dict[str, Any]:
        return {"source": "model", "message": query}
