"""Evaluation subsystem facade — unified interface for all evaluation operations."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from .eval_spec import EvalSpec, builtin_specs
from .evaluation_runner import EvaluationRunner
from .ground_truth_manager import GroundTruthManager
from .metric_aggregator import MetricAggregator
from .report_generator import ReportGenerator


class Evaluation:
    def __init__(self, storage: Any) -> None:
        self._storage = storage
        self._specs: dict[str, EvalSpec] = {}
        self.runner = EvaluationRunner(storage)
        self.ground_truth = GroundTruthManager(storage)
        self.aggregator = MetricAggregator(storage)
        self.reporter = ReportGenerator(storage)

    def register_spec(self, spec: EvalSpec) -> str:
        self._specs[spec.id] = spec
        self._storage.insert("evaluation_spec", spec.to_record())
        return spec.id

    def register_handler(self, capability: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        self.runner.register(capability, handler)

    def register_builtins(self) -> list[str]:
        ids: list[str] = []
        for spec in builtin_specs():
            existing = self._storage.query("evaluation_spec", {"name": spec.name})
            if not existing:
                ids.append(self.register_spec(spec))
        return ids

    def get_spec(self, spec_id: str) -> dict[str, Any] | None:
        return self._storage.get("evaluation_spec", spec_id)

    def list_specs(self) -> list[dict[str, Any]]:
        return self._storage.query("evaluation_spec", {})

    def run(self, spec_id: str, gt_ids: list[str] | None = None) -> dict[str, Any]:
        if gt_ids:
            ground_truths = []
            for gid in gt_ids:
                gt = self.ground_truth.get(gid)
                if gt:
                    ground_truths.append(gt)
        else:
            ground_truths = self.ground_truth.list_for_spec(spec_id)
        return self.runner.run_spec(spec_id, ground_truths)

    def run_all(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        for spec_id in self._specs:
            result = self.run(spec_id)
            results.append(result)
        return results

    def create_ground_truth(
        self, spec_id: str, inputs: dict[str, Any], expected: dict[str, Any]
    ) -> str:
        return self.ground_truth.create(spec_id, inputs, expected)

    def seed_default_ground_truth(self) -> int:
        count = 0
        specs = self._storage.query("evaluation_spec", {})
        spec_map = {s["name"]: s["id"] for s in specs}

        entity_sid = spec_map.get("entity_resolution")
        if entity_sid:
            examples: list[tuple[dict[str, Any], dict[str, Any]]] = [
                ({"name": "Alice"}, {"name": "Alice", "found": True}),
                ({"name": "Bob"}, {"name": "Bob", "found": True}),
                ({"name": "Charlie"}, {"name": "Charlie", "found": True}),
            ]
            existing = self.ground_truth.list_for_spec(entity_sid)
            existing_inputs = {str(e.get("inputs", {}).get("name", "")) for e in existing}
            for inputs, expected in examples:
                if inputs["name"] not in existing_inputs:
                    self.ground_truth.create(entity_sid, inputs, expected)
                    count += 1

        persona_sid = spec_map.get("persona_consistency")
        if persona_sid:
            examples = [
                (
                    {"knowledge": {"topic": "python", "confidence": 0.9}},
                    {"score": 0.5, "consistency": 0.5},
                ),
            ]
            existing = self.ground_truth.list_for_spec(persona_sid)
            if not existing:
                for inputs, expected in examples:
                    self.ground_truth.create(persona_sid, inputs, expected)
                    count += 1

        return count

    def generate_report(self, run_ids: list[str]) -> dict[str, Any]:
        all_results: list[dict[str, Any]] = []
        for rid in run_ids:
            all_results.extend(self.aggregator.run_results(rid))
        summary = self.aggregator.aggregate(all_results)
        summary["run_count"] = len(run_ids)
        regressions: list[dict[str, Any]] = []
        seen: set[str] = set()
        for r in all_results:
            rid = r.get("run_id", "")
            if rid in seen:
                continue
            seen.add(rid)
            run = self._storage.get("evaluation_run", rid)
            if run:
                spec_id = run.get("spec_id", "")
                regressions.extend(self.aggregator.detect_regressions(spec_id))
        summary["regression_count"] = len(regressions)
        return self.reporter.generate(run_ids, summary)
