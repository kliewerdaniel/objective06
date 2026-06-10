"""Knowledge writer — persists knowledge objects to storage."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class KnowledgeWriter:
    def __init__(self, storage: Any, audit_log: Any) -> None:
        self._storage = storage
        self._audit_log = audit_log

    def write(
        self,
        *,
        type: str,
        name: str,
        description: str = "",
        content: str = "",
        confidence: float = 0.5,
        attributes: dict[str, Any] | None = None,
        source_event_ids: list[str] | None = None,
        prompt_id: str = "",
        model_id: str = "",
        producer: str = "extractor",
        producer_version: str = "0.1.0",
        reasoning: str = "",
        entity_id: str | None = None,
    ) -> str:
        now = datetime.now(UTC)
        ko_id = f"ko_{uuid4().hex}"
        record = {
            "schema_version": "0.1.0",
            "id": ko_id,
            "type": type,
            "name": name,
            "description": description,
            "attributes": {
                "content": content,
                "source_event_ids": source_event_ids or [],
                "reasoning": reasoning,
                "entity_id": entity_id,
                **(attributes or {}),
            },
            "confidence": max(0.0, min(1.0, confidence)),
            "provenance": {
                "producer": producer,
                "producer_version": producer_version,
                "produced_at": now.isoformat(),
                "prompt_id": prompt_id,
                "model_id": model_id,
                "parent_ids": source_event_ids or [],
                "notes": reasoning,
            },
            "created_at": now.isoformat(),
            "updated_at": now.isoformat(),
            "deprecated": False,
            "superseded_by": None,
        }
        self._storage.insert("knowledge_object", record)
        self._audit_log.append(
            actor=producer,
            action="create",
            entity_type="knowledge_object",
            entity_id=ko_id,
            reason=f"Extracted {type}: {name}",
        )
        return ko_id
