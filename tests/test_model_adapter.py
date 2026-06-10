"""Tests for model_adapter module."""

from __future__ import annotations

from self.persona_engine.model_adapter import ModelAdapter


class FakeEmbedder:
    def compute(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


class FakeVectorStore:
    def __init__(self) -> None:
        self._model_id: str | None = None

    def current(self) -> dict | None:
        return None

    def trajectory(self) -> list[dict]:
        return []


def test_model_adapter_initial_state() -> None:
    store = FakeVectorStore()
    embedder = FakeEmbedder()
    adapter = ModelAdapter(store, embedder)
    assert adapter.get_current_model() is None


def test_model_adapter_set_model() -> None:
    store = FakeVectorStore()
    embedder = FakeEmbedder()
    adapter = ModelAdapter(store, embedder)
    adapter.set_current_model("model_v1")
    assert adapter.get_current_model() == "model_v1"


def test_model_adapter_needs_reanchoring() -> None:
    store = FakeVectorStore()
    embedder = FakeEmbedder()
    adapter = ModelAdapter(store, embedder)
    adapter.set_current_model("model_v1")
    assert adapter.needs_reanchoring("model_v2") is True
    assert adapter.needs_reanchoring("model_v1") is False


def test_model_adapter_reanchor() -> None:
    store = FakeVectorStore()
    embedder = FakeEmbedder()
    adapter = ModelAdapter(store, embedder)
    adapter.set_current_model("model_v1")
    result = adapter.reanchor("model_v2")
    assert result["reanchored"] is True
    assert result["old_model"] == "model_v1"
    assert result["new_model"] == "model_v2"


def test_model_adapter_reanchor_no_change() -> None:
    store = FakeVectorStore()
    embedder = FakeEmbedder()
    adapter = ModelAdapter(store, embedder)
    adapter.set_current_model("model_v1")
    result = adapter.reanchor("model_v1")
    assert result["reanchored"] is False
    assert result["reason"] == "no_model_change"
