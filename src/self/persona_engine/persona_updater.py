"""Persona Updater — incremental persona vector updates."""

from __future__ import annotations

from typing import Any


class PersonaUpdater:
    def __init__(self, vector_store: Any, embedding_computer: Any, alpha: float = 0.1) -> None:
        self._vector_store = vector_store
        self._embedder = embedding_computer
        self._alpha = alpha

    def update(self, knowledge: dict[str, Any]) -> str:
        new_vec = self._embedder.embed_knowledge(knowledge)
        current = self._vector_store.current()
        if current is None:
            merged = new_vec
        else:
            old_vec = current.get("vector", [])
            if old_vec and len(old_vec) == len(new_vec):
                merged = [(1 - self._alpha) * o + self._alpha * n for o, n in zip(old_vec, new_vec)]
            else:
                merged = new_vec
        return self._vector_store.save_snapshot(
            merged,
            self._embedder.model_id,
            reason=f"Updated from knowledge: {knowledge.get('name', '')}",
        )

    def seed_from_onboarding(self, data: dict[str, Any]) -> str:
        new_vec = self._embedder.embed_onboarding(data)
        return self._vector_store.save_snapshot(
            new_vec,
            self._embedder.model_id,
            reason=f"Seed from onboarding: {data.get('role', 'unknown')}",
        )
