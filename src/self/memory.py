"""Memory API — unified interface wrapping all stores with query routing."""

from __future__ import annotations

from typing import Any


class MemoryAPI:
    def __init__(
        self,
        storage: Any,
        audit_log: Any,
        event_log: Any | None = None,
        faiss_adapter: Any | None = None,
    ) -> None:
        self._storage = storage
        self._audit_log = audit_log
        self._event_log = event_log
        self._faiss = faiss_adapter

    # --- Write operations ---

    def store_event(self, event: dict[str, Any]) -> str:
        eid = self._storage.insert("observation_event", event)
        self._audit_log.append(
            actor="memory",
            action="create",
            entity_type="observation_event",
            entity_id=eid,
            reason="Store observation event",
        )
        if self._event_log:
            self._event_log.append(event)
        return eid

    def store_knowledge(self, ko: dict[str, Any]) -> str:
        kid = self._storage.insert("knowledge_object", ko)
        self._audit_log.append(
            actor="memory",
            action="create",
            entity_type="knowledge_object",
            entity_id=kid,
            reason=f"Store knowledge: {ko.get('name', '')}",
        )
        return kid

    def store_summary(self, summary: dict[str, Any]) -> str:
        sid = self._storage.insert("summary", summary)
        self._audit_log.append(
            actor="memory",
            action="create",
            entity_type="summary",
            entity_id=sid,
            reason="Store summary",
        )
        return sid

    # --- Read operations ---

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        return self._storage.get("observation_event", event_id)

    def get_knowledge(self, ko_id: str) -> dict[str, Any] | None:
        return self._storage.get("knowledge_object", ko_id)

    def query_events(
        self,
        spec: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        return self._storage.query("observation_event", spec or {})

    def query_knowledge(
        self,
        spec: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        return self._storage.query("knowledge_object", spec or {})

    # --- Semantic search ---

    def semantic_search(self, query_vector: list[float], k: int = 10) -> list[dict[str, Any]]:
        if self._faiss is None:
            return []
        return self._faiss.search(query_vector, k)

    # --- Counts ---

    @property
    def event_count(self) -> int:
        return self._storage.count("observation_event")

    @property
    def knowledge_count(self) -> int:
        return self._storage.count("knowledge_object")

    @property
    def audit_count(self) -> int:
        return self._storage.count("audit_log_entry")
