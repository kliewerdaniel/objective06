"""Tests for predictor module."""

from __future__ import annotations

from typing import Any

from self.persona_engine.predictor import Predictor


class FakeVectorStore:
    def __init__(self, vectors: list[list[float]] | None = None) -> None:
        self._vectors = vectors or []
        self._index = 0

    def current(self) -> dict[str, Any] | None:
        if not self._vectors:
            return None
        return {
            "vector": self._vectors[-1],
            "timestamp": "2024-01-01T00:00:00Z",
        }

    def trajectory(self) -> list[dict[str, Any]]:
        return [
            {"vector": v, "timestamp": f"2024-01-0{i + 1}T00:00:00Z"}
            for i, v in enumerate(self._vectors)
        ]


def test_predict_next_vector_empty_store() -> None:
    store = FakeVectorStore(vectors=[])
    predictor = Predictor(store)
    result = predictor.predict_next_vector()
    assert result["vector"] == []
    assert result["confidence"] == 0.0


def test_predict_next_vector_single_vector() -> None:
    store = FakeVectorStore(vectors=[[1.0, 0.0, 0.0]])
    predictor = Predictor(store)
    result = predictor.predict_next_vector()
    assert len(result["vector"]) == 3
    assert result["method"] == "static"
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_next_vector_multiple_vectors() -> None:
    store = FakeVectorStore(vectors=[[1.0, 0.0], [0.8, 0.2], [0.6, 0.4]])
    predictor = Predictor(store)
    result = predictor.predict_next_vector(steps_ahead=1)
    assert len(result["vector"]) == 2
    assert result["method"] == "linear_extrapolation"
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_next_vector_steps_ahead() -> None:
    store = FakeVectorStore(vectors=[[1.0, 0.0], [0.8, 0.2]])
    predictor = Predictor(store)
    result1 = predictor.predict_next_vector(steps_ahead=1)
    result2 = predictor.predict_next_vector(steps_ahead=2)
    assert result1["vector"] != result2["vector"]


def test_predict_similarity() -> None:
    store = FakeVectorStore(vectors=[[1.0, 0.0], [0.8, 0.2]])
    predictor = Predictor(store)
    result = predictor.predict_similarity([1.0, 0.0])
    assert "similarity" in result
    assert "confidence" in result
    assert -1.0 <= result["similarity"] <= 1.0
