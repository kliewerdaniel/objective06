"""Model Adapter — handles re-anchoring when model is swapped."""

from __future__ import annotations

import logging
from typing import Any


class ModelAdapter:
    def __init__(self, vector_store: Any, embedder: Any) -> None:
        self._vector_store = vector_store
        self._embedder = embedder
        self._log = logging.getLogger("self.model_adapter")
        self._current_model: str | None = None

    def get_current_model(self) -> str | None:
        return self._current_model

    def set_current_model(self, model_id: str) -> None:
        self._current_model = model_id

    def needs_reanchoring(self, new_model_id: str) -> bool:
        if self._current_model is None:
            return False
        return self._current_model != new_model_id

    def reanchor(
        self,
        new_model_id: str,
        anchor_text: str = "self-identification anchor",
    ) -> dict[str, Any]:
        if not self.needs_reanchoring(new_model_id):
            return {
                "reanchored": False,
                "reason": "no_model_change",
                "current_model": self._current_model,
                "new_model": new_model_id,
            }

        old_model = self._current_model
        anchor_vector = self._compute_anchor_vector(anchor_text)
        if anchor_vector:
            self._store_anchor(new_model_id, anchor_vector)
            self._log.info(
                "Reanchored from model %s to %s",
                old_model,
                new_model_id,
            )
            return {
                "reanchored": True,
                "old_model": old_model,
                "new_model": new_model_id,
                "anchor_vector": anchor_vector,
            }

        self._current_model = new_model_id
        return {
            "reanchored": True,
            "old_model": old_model,
            "new_model": new_model_id,
            "anchor_vector": None,
            "note": "anchor_computation_failed",
        }

    def _compute_anchor_vector(self, text: str) -> list[float] | None:
        try:
            result = self._embedder.compute(text)
            if isinstance(result, dict) and "vector" in result:
                return result["vector"]
            elif isinstance(result, list):
                return result
            return None
        except Exception as e:
            self._log.warning("Anchor vector computation failed: %s", e)
            return None

    def _store_anchor(self, model_id: str, vector: list[float]) -> None:
        self._current_model = model_id
