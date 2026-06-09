"""Synthesis Engine — facade for summary generation."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from .content_aggregator import ContentAggregator
from .generation_engine import GenerationEngine
from .grounding_verifier import GroundingVerifier
from .prompt_builder import PromptBuilder
from .provenance_linker import ProvenanceLinker
from .summary_cache import SummaryCache


class SynthesisEngine:
    def __init__(self, memory: Any, model_client: Any, identity_graph: Any, storage: Any) -> None:
        self._memory = memory
        self._graph = identity_graph
        self._storage = storage
        self._aggregator = ContentAggregator(memory, identity_graph)
        self._prompt_builder = PromptBuilder()
        self._generator = GenerationEngine(model_client)
        self._verifier = GroundingVerifier()
        self._linker = ProvenanceLinker()
        self._cache = SummaryCache()

    def summarize_daily(self, start: str = "", end: str = "") -> dict[str, Any]:
        return self._synthesize("daily", start=start, end=end)

    def summarize_weekly(self, start: str = "", end: str = "") -> dict[str, Any]:
        return self._synthesize("weekly", start=start, end=end)

    def summarize_topic(self, topic: str) -> dict[str, Any]:
        return self._synthesize("topic", topic=topic)

    def summarize_project(self, project_name: str) -> dict[str, Any]:
        return self._synthesize("project", topic=project_name)

    def _synthesize(
        self,
        summary_type: str,
        start: str = "",
        end: str = "",
        topic: str = "",
    ) -> dict[str, Any]:
        cache_key = f"{summary_type}:{start}:{end}:{topic}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached
        context = self._aggregator.aggregate(start=start, end=end, topic=topic)
        empty = (
            context["event_count"] == 0
            and context["knowledge_count"] == 0
            and context["node_count"] == 0
        )
        if empty:
            result = {
                "ok": True,
                "text": f"No activity found for this {summary_type} period.",
                "summary_type": summary_type,
                "provenance": {},
            }
            self._cache.set(cache_key, result)
            return result
        prompt = self._prompt_builder.build(summary_type, context, topic=topic)
        gen_result = self._generator.generate(prompt)
        if not gen_result["success"]:
            return {
                "ok": False,
                "error": gen_result.get("error", "Generation failed"),
                "summary_type": summary_type,
            }
        text = gen_result.get("text", "")
        grounding = self._verifier.verify(text, context)
        if not grounding["grounded"]:
            gen_result = self._generator.generate(prompt)
            text = gen_result.get("text", "Summary could not be generated.")
        sid = f"sum_{uuid4().hex}"
        provenance = self._linker.link(sid, context)
        provenance["synthesis_params"] = {
            "prompt_version": self._prompt_builder.get_version(summary_type),
            "model": gen_result.get("model", ""),
            "tokens": gen_result.get("tokens", 0),
            "duration_ms": gen_result.get("duration_ms", 0),
            "grounding_coverage": grounding["coverage"],
        }
        record = {
            "schema_version": "0.1.0",
            "id": sid,
            "type": summary_type,
            "content": text,
            "source_ids": provenance.get("source_records", {}),
            "created_at": datetime.now(UTC).isoformat(),
            "provenance": provenance,
        }
        if hasattr(self._storage, "insert"):
            self._storage.insert("summary", record)
        result = {
            "ok": True,
            "text": text,
            "summary_type": summary_type,
            "summary_id": sid,
            "provenance": provenance,
        }
        self._cache.set(cache_key, result)
        return result
