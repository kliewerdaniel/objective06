"""Tests for the Synthesis Engine."""

from __future__ import annotations

from src.self.synthesis_engine.content_aggregator import ContentAggregator
from src.self.synthesis_engine.generation_engine import GenerationEngine
from src.self.synthesis_engine.grounding_verifier import GroundingVerifier
from src.self.synthesis_engine.prompt_builder import PromptBuilder
from src.self.synthesis_engine.provenance_linker import ProvenanceLinker
from src.self.synthesis_engine.summary_cache import SummaryCache
from src.self.synthesis_engine.synthesis_engine import SynthesisEngine


class FakeModelClient:
    def __init__(self) -> None:
        self.model_name = "test-model"

    def generate(self, prompt: str, system: str | None = None) -> dict:
        return {
            "text": "Today worked on Python development. Progress on SELF framework.",
            "model": "test-model",
            "tokens": 25,
            "total_duration_ms": 100,
        }


class FakeMemory:
    def query_events(self, spec: dict | None = None) -> list[dict]:
        return [
            {
                "id": "evt_001",
                "event_type": "python_commit",
                "timestamp": "2026-06-08T10:00:00",
                "payload": {"summary": "Fixed duckdb adapter bug"},
            },
            {
                "id": "evt_002",
                "event_type": "meeting",
                "timestamp": "2026-06-08T14:00:00",
                "payload": {"summary": "Sprint planning"},
            },
        ]

    def query_knowledge(self, spec: dict | None = None) -> list[dict]:
        return [
            {
                "id": "ko_001",
                "name": "Python skills",
                "description": "User is proficient in Python",
                "attributes": {},
            },
            {
                "id": "ko_002",
                "name": "SELF architecture",
                "description": "Understanding SELF framework",
                "attributes": {"status": "active"},
            },
            {
                "id": "ko_003",
                "name": "Old knowledge",
                "description": "Legacy info",
                "attributes": {"status": "archived"},
            },
        ]


class FakeGraph:
    class NodeStore:
        @staticmethod
        def all() -> list[dict]:
            return [
                {"id": "id_001", "name": "Python", "type": "concept"},
                {"id": "id_002", "name": "SELF", "type": "project"},
            ]

    def __init__(self) -> None:
        self.node_store = self.NodeStore()


class FakeStorage:
    def __init__(self) -> None:
        self.records: list[dict] = []

    def insert(self, record_type: str, record: dict) -> str:
        self.records.append(record)
        return str(record["id"])


# --- Content Aggregator ---


def test_aggregator_returns_context() -> None:
    agg = ContentAggregator(FakeMemory(), FakeGraph())
    ctx = agg.aggregate()
    assert ctx["event_count"] == 2
    assert ctx["knowledge_count"] == 2  # archived excluded
    assert ctx["node_count"] == 2
    assert ctx["excluded_count"] == 1


def test_aggregator_with_topic() -> None:
    agg = ContentAggregator(FakeMemory(), FakeGraph())
    ctx = agg.aggregate(topic="Python")
    names = [n["name"] for n in ctx["nodes"]]
    assert "Python" in names


# --- Prompt Builder ---


def test_prompt_builder_daily() -> None:
    builder = PromptBuilder()
    ctx = {
        "events": [
            {"event_type": "test", "timestamp": "2026-01-01", "payload": {"summary": "test"}}
        ],
        "knowledge": [],
        "nodes": [],
    }
    prompt = builder.build("daily", ctx)
    assert "Daily Summary" in prompt
    assert "test" in prompt


def test_prompt_builder_unknown_type() -> None:
    builder = PromptBuilder()
    try:
        builder.build("unknown", {})
        assert False, "Should have raised"
    except ValueError:
        pass


def test_prompt_builder_version() -> None:
    builder = PromptBuilder()
    assert builder.get_version("daily") == "0.1.0"
    assert builder.get_version("unknown") == "0.0.0"


# --- Generation Engine ---


def test_generation_success() -> None:
    gen = GenerationEngine(FakeModelClient())
    result = gen.generate("test prompt")
    assert result["success"] is True
    assert "Python" in result["text"]


def test_generation_failure() -> None:
    class FailingModel:
        def generate(self, prompt: str, system: str | None = None) -> dict:
            msg = "model unavailable"
            raise RuntimeError(msg)

    gen = GenerationEngine(FailingModel())
    result = gen.generate("test")
    assert result["success"] is False


# --- Grounding Verifier ---


def test_grounding_verifier_covered() -> None:
    verifier = GroundingVerifier()
    text = "Today the user worked on Python development."
    ctx = {
        "events": [{"event_type": "python_commit", "payload": {"summary": "Python work"}}],
        "knowledge": [],
        "nodes": [],
    }
    result = verifier.verify(text, ctx)
    assert result["covered_sentences"] >= 1


def test_grounding_empty() -> None:
    verifier = GroundingVerifier()
    result = verifier.verify("", {})
    assert result["grounded"] is False


# --- Provenance Linker ---


def test_provenance_linker() -> None:
    linker = ProvenanceLinker()
    ctx = {
        "events": [{"id": "evt_001"}],
        "knowledge": [{"id": "ko_001"}],
        "nodes": [{"id": "id_001"}],
    }
    prov = linker.link("sum_001", ctx)
    assert prov["total_sources"] == 3
    assert "evt_001" in prov["source_records"]["events"]


def test_provenance_linker_no_ids() -> None:
    linker = ProvenanceLinker()
    ctx = {"events": [{"event_id": "evt_001"}], "knowledge": [], "nodes": []}
    prov = linker.link("sum_001", ctx)
    assert prov["total_sources"] == 1


# --- Summary Cache ---


def test_cache_set_and_get() -> None:
    cache = SummaryCache(ttl_minutes=60)
    cache.set("daily:today", {"text": "summary"})
    assert cache.get("daily:today") == {"text": "summary"}


def test_cache_miss() -> None:
    cache = SummaryCache()
    assert cache.get("nonexistent") is None


def test_cache_invalidate() -> None:
    cache = SummaryCache()
    cache.set("key", {"data": 1})
    cache.invalidate("key")
    assert cache.get("key") is None


def test_cache_clear() -> None:
    cache = SummaryCache()
    cache.set("a", {"data": 1})
    cache.set("b", {"data": 2})
    cache.clear()
    assert cache.size() == 0


# --- Synthesis Engine ---


def test_synthesize_daily() -> None:
    engine = SynthesisEngine(FakeMemory(), FakeModelClient(), FakeGraph(), FakeStorage())
    result = engine.summarize_daily()
    assert result["ok"] is True
    assert result["summary_type"] == "daily"
    assert "summary_id" in result
    assert "provenance" in result


def test_synthesize_weekly() -> None:
    engine = SynthesisEngine(FakeMemory(), FakeModelClient(), FakeGraph(), FakeStorage())
    result = engine.summarize_weekly()
    assert result["ok"] is True


def test_synthesize_topic() -> None:
    engine = SynthesisEngine(FakeMemory(), FakeModelClient(), FakeGraph(), FakeStorage())
    result = engine.summarize_topic("Python")
    assert result["ok"] is True


def test_synthesize_project() -> None:
    engine = SynthesisEngine(FakeMemory(), FakeModelClient(), FakeGraph(), FakeStorage())
    result = engine.summarize_project("SELF")
    assert result["ok"] is True


def test_synthesize_empty_context() -> None:
    class EmptyMemory:
        @staticmethod
        def query_events(spec: dict | None = None) -> list[dict]:
            return []

        @staticmethod
        def query_knowledge(spec: dict | None = None) -> list[dict]:
            return []

    class EmptyGraph:
        class NodeStore:
            @staticmethod
            def all() -> list[dict]:
                return []

        def __init__(self) -> None:
            self.node_store = self.NodeStore()

    engine = SynthesisEngine(EmptyMemory(), FakeModelClient(), EmptyGraph(), FakeStorage())
    result = engine.summarize_daily()
    assert result["ok"] is True
    assert "No activity found" in result["text"]


def test_synthesize_caches() -> None:
    storage = FakeStorage()
    engine = SynthesisEngine(FakeMemory(), FakeModelClient(), FakeGraph(), storage)
    r1 = engine.summarize_daily()
    r2 = engine.summarize_daily()
    assert r1["summary_id"] == r2["summary_id"]
    assert len(storage.records) == 1  # only stored once
