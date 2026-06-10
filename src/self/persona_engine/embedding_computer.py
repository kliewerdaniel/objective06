"""Embedding Computer — computes embeddings via ModelClient."""

from __future__ import annotations

from typing import Any


class EmbeddingComputer:
    def __init__(self, model_client: Any, model_lineage_id: str | None = None) -> None:
        self._model_client = model_client
        self._model_lineage_id = model_lineage_id or "default"

    def embed_text(self, text: str) -> list[float]:
        result = self._model_client.embed(text)
        if isinstance(result, list):
            return result
        return []

    def embed_onboarding(self, data: dict[str, Any]) -> list[float]:
        role = data.get("role", "")
        interests = ", ".join(data.get("top_interests", []))
        projects = ", ".join(data.get("top_projects", []))
        description = data.get("free_form", "")
        text = (
            f"Role: {role}. Interests: {interests}. "
            f"Projects: {projects}. Description: {description}"
        )
        return self.embed_text(text.strip())

    def embed_knowledge(self, knowledge: dict[str, Any]) -> list[float]:
        parts = [
            knowledge.get("name", ""),
            knowledge.get("description", ""),
            knowledge.get("content", ""),
        ]
        text = " ".join(p for p in parts if p)
        content = knowledge.get("attributes", {})
        if isinstance(content, dict):
            extra = content.get("content", "")
            if extra:
                text = f"{text} {extra}"
        return self.embed_text(text.strip())

    def validate_lineage(self, snapshot_lineage: str) -> bool:
        """Validate that a snapshot's lineage matches the current model lineage."""
        return snapshot_lineage == self._model_lineage_id

    @property
    def model_id(self) -> str:
        name = self._model_client.model_name
        return str(name) if name else ""

    @property
    def model_lineage_id(self) -> str:
        return self._model_lineage_id
