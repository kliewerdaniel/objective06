"""Persona Engine — facade over persona components."""

from __future__ import annotations

from typing import Any

from .consistency_scorer import ConsistencyScorer
from .decay_engine import DecayEngine
from .embedding_computer import EmbeddingComputer
from .model_adapter import ModelAdapter
from .persona_updater import PersonaUpdater
from .persona_vector_store import PersonaVectorStore
from .predictor import Predictor


class PersonaEngine:
    def __init__(
        self,
        storage: Any,
        model_client: Any,
        vector_dir: str,
        model_lineage_id: str | None = None,
    ) -> None:
        self.vector_store = PersonaVectorStore(storage, vector_dir)
        self.embedder = EmbeddingComputer(model_client, model_lineage_id)
        self.updater = PersonaUpdater(self.vector_store, self.embedder)
        self.scorer = ConsistencyScorer(self.vector_store, self.embedder)
        self.decay_engine = DecayEngine(self)
        self.predictor = Predictor(self.vector_store)
        self.model_adapter = ModelAdapter(self.vector_store, self.embedder)

    def update_from_knowledge(self, knowledge: dict[str, Any]) -> str:
        return self.updater.update(knowledge)

    def seed_from_onboarding(self, data: dict[str, Any]) -> str:
        return self.updater.seed_from_onboarding(data)

    def consistency(self, knowledge: dict[str, Any]) -> float:
        return self.scorer.score(knowledge)

    def current_vector(self) -> dict[str, Any] | None:
        return self.vector_store.current()

    def trajectory(self) -> list[dict[str, Any]]:
        return self.vector_store.trajectory()

    def predict_next_vector(self, steps_ahead: int = 1) -> dict[str, Any]:
        return self.predictor.predict_next_vector(steps_ahead)

    def reanchor_model(self, new_model_id: str) -> dict[str, Any]:
        return self.model_adapter.reanchor(new_model_id)
