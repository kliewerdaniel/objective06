"""Consistency Scorer — scores candidate knowledge against the persona."""

from __future__ import annotations

import math
from typing import Any


class ConsistencyScorer:
    def __init__(self, vector_store: Any, embedding_computer: Any) -> None:
        self._vector_store = vector_store
        self._embedder = embedding_computer

    def score(self, knowledge: dict[str, Any]) -> float:
        persona = self._vector_store.current()
        if persona is None:
            return 0.5
        persona_vec = persona.get("vector", [])
        if not persona_vec:
            return 0.5
        candidate_vec = self._embedder.embed_knowledge(knowledge)
        if not candidate_vec or len(candidate_vec) != len(persona_vec):
            return 0.5
        return self._cosine_similarity(persona_vec, candidate_vec)

    @staticmethod
    def _cosine_similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(y * y for y in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return max(0.0, min(1.0, dot / (norm_a * norm_b)))
