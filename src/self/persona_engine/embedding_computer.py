"""Embedding Computer — computes embeddings via ModelClient."""

from __future__ import annotations

from typing import Any


class EmbeddingComputer:
    def __init__(self, model_client: Any) -> None:
        self._model_client = model_client

    def embed_text(self, text: str) -> list[float]:
        result = self._model_client.embed(text)
        if isinstance(result, list):
            return result
        return []

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

    @property
    def model_id(self) -> str:
        name = self._model_client.model_name
        return str(name) if name else ""
