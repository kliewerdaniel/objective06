"""Tests for the Persona Engine."""

from __future__ import annotations

import math
import tempfile

from src.self.persona_engine.consistency_scorer import ConsistencyScorer
from src.self.persona_engine.embedding_computer import EmbeddingComputer
from src.self.persona_engine.persona_engine import PersonaEngine
from src.self.persona_engine.persona_updater import PersonaUpdater
from src.self.persona_engine.persona_vector_store import PersonaVectorStore


class FakeModelClient:
    def __init__(self) -> None:
        self.model_name = "test-model"

    def embed(self, text: str) -> list[float]:
        # deterministic embedding: sum of char codes mod 10
        s = sum(ord(c) for c in text)
        return [math.sin(s + i) for i in range(8)]


class FakeStorage:
    def __init__(self) -> None:
        self._data: dict[str, list[dict]] = {"persona_snapshot": []}

    def insert(self, record_type: str, record: dict) -> str:
        self._data.setdefault(record_type, []).append(record)
        return str(record["id"])

    def query(self, record_type: str, spec: dict) -> list[dict]:
        records = self._data.get(record_type, [])
        limit = spec.get("limit", 100)
        order = spec.get("order_by", "")
        if order == "timestamp":
            records = sorted(records, key=lambda r: r.get("timestamp", ""), reverse=True)
        return records[:limit]

    def get(self, record_type: str, id: str) -> dict | None:
        for r in self._data.get(record_type, []):
            if r.get("id") == id:
                return r
        return None


def test_vector_store_save_and_current() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = PersonaVectorStore(FakeStorage(), tmp)
        sid = store.save_snapshot([0.1, 0.2, 0.3], "m1", "test")
        curr = store.current()
        assert curr is not None
        assert curr["id"] == sid
        assert curr["model_id"] == "m1"
        assert curr["vector"] == [0.1, 0.2, 0.3]


def test_vector_store_at_time() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = PersonaVectorStore(FakeStorage(), tmp)
        store.save_snapshot([0.1], "m1")
        import time

        time.sleep(0.01)
        store.save_snapshot([0.3], "m1")
        snap = store.at_time("2100-01-01T00:00:00")
        assert snap is not None
        assert snap["vector"] == [0.3]


def test_vector_store_trajectory() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = PersonaVectorStore(FakeStorage(), tmp)
        store.save_snapshot([0.1], "m1")
        store.save_snapshot([0.2], "m1")
        traj = store.trajectory()
        assert len(traj) == 2


def test_vector_store_history() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = PersonaVectorStore(FakeStorage(), tmp)
        store.save_snapshot([0.1], "m1")
        n = store.history(limit=10)
        assert len(n) == 1


def test_embedding_computer() -> None:
    client = FakeModelClient()
    embedder = EmbeddingComputer(client)
    vec = embedder.embed_text("hello world")
    assert len(vec) == 8
    assert all(isinstance(v, float) for v in vec)


def test_embedding_computer_knowledge() -> None:
    client = FakeModelClient()
    embedder = EmbeddingComputer(client)
    k = {"name": "test", "description": "a test object", "content": "some content"}
    vec = embedder.embed_knowledge(k)
    assert len(vec) == 8


def test_updater_no_previous() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = PersonaVectorStore(FakeStorage(), tmp)
        embedder = EmbeddingComputer(FakeModelClient())
        updater = PersonaUpdater(store, embedder, alpha=0.1)
        sid = updater.update({"name": "first", "content": "test"})
        assert sid.startswith("ps_")
        curr = store.current()
        assert curr is not None


def test_updater_with_previous() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = PersonaVectorStore(FakeStorage(), tmp)
        embedder = EmbeddingComputer(FakeModelClient())
        updater = PersonaUpdater(store, embedder, alpha=0.5)
        k1 = {"name": "vec1", "content": "a" * 20}
        k2 = {"name": "vec2", "content": "b" * 20}
        updater.update(k1)
        updater.update(k2)
        curr = store.current()
        assert curr is not None
        vec = curr["vector"]
        assert len(vec) == 8


def test_consistency_scorer() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = PersonaVectorStore(FakeStorage(), tmp)
        embedder = EmbeddingComputer(FakeModelClient())
        store.save_snapshot([1.0, 0.0, 0.0, 0.0], "m1")
        scorer = ConsistencyScorer(store, embedder)
        k = {"name": "similar", "content": "hello"}
        s = scorer.score(k)
        assert 0.0 <= s <= 1.0


def test_consistency_scorer_no_persona() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        store = PersonaVectorStore(FakeStorage(), tmp)
        embedder = EmbeddingComputer(FakeModelClient())
        scorer = ConsistencyScorer(store, embedder)
        s = scorer.score({"name": "test", "content": "hello"})
        assert s == 0.5


def test_persona_engine() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        storage = FakeStorage()
        client = FakeModelClient()
        engine = PersonaEngine(storage, client, tmp)
        k = {"name": "test", "content": "hello"}
        sid = engine.update_from_knowledge(k)
        assert sid.startswith("ps_")
        c = engine.consistency(k)
        assert 0.0 <= c <= 1.0
        v = engine.current_vector()
        assert v is not None
        assert v["id"] == sid


def test_persona_engine_trajectory_empty() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        engine = PersonaEngine(FakeStorage(), FakeModelClient(), tmp)
        assert engine.trajectory() == []
        assert engine.current_vector() is None


def test_cosine_similarity() -> None:
    a = [1.0, 2.0, 3.0]
    b = [1.0, 2.0, 3.0]
    assert ConsistencyScorer._cosine_similarity(a, b) == 1.0
    c = [0.0, 0.0, 0.0]
    assert ConsistencyScorer._cosine_similarity(a, c) == 0.0
    d = [-1.0, -2.0, -3.0]
    assert ConsistencyScorer._cosine_similarity(a, d) == 0.0


def test_vector_dir_persistence() -> None:
    fake = FakeStorage()
    with tempfile.TemporaryDirectory() as tmp:
        store = PersonaVectorStore(fake, tmp)
        store.save_snapshot([0.5], "m1")
        sid = fake._data["persona_snapshot"][0]["id"]
        assert sid.startswith("ps_")
