"""Evaluation Runner — executes evaluation specs against subsystems."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class EvaluationRunner:
    def __init__(self, storage: Any) -> None:
        self._storage = storage
        self._handlers: dict[str, Callable[[dict[str, Any]], Any]] = {}

    def register(self, capability: str, handler: Callable[[dict[str, Any]], Any]) -> None:
        self._handlers[capability] = handler

    def run_spec(
        self,
        spec_id: str,
        ground_truth_records: list[dict[str, Any]],
        config: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        spec_record = self._storage.get("evaluation_spec", spec_id)
        if spec_record is None:
            return {"ok": False, "error": f"Unknown spec: {spec_id}"}

        run_id = f"er_{uuid4().hex}"
        now = datetime.now(UTC).isoformat()
        run_record = {
            "schema_version": "0.1.0",
            "id": run_id,
            "spec_id": spec_id,
            "status": "running",
            "started_at": now,
            "config": config or {},
        }
        self._storage.insert("evaluation_run", run_record)

        results: list[dict[str, Any]] = []
        for gt in ground_truth_records:
            result = self._evaluate_one(gt, spec_record)
            if result:
                result["run_id"] = run_id
                result["recorded_at"] = datetime.now(UTC).isoformat()
                self._storage.insert("evaluation_result", result)
                results.append(result)

        threshold = spec_record.get("pass_threshold", 0.8)
        if not results:
            final_status = "completed"
            passed = True
            pass_rate = 1.0
        else:
            passed_count = sum(1 for r in results if r["passed"])
            total = len(results)
            pass_rate = passed_count / total
            passed = pass_rate >= threshold
            final_status = "completed" if passed else "failed"

        completed_at = datetime.now(UTC).isoformat()
        self._storage.update(
            "evaluation_run",
            run_id,
            {"status": final_status, "completed_at": completed_at},
        )

        return {
            "ok": True,
            "run_id": run_id,
            "spec_id": spec_id,
            "status": final_status,
            "passed": passed,
            "pass_rate": pass_rate,
            "threshold": threshold,
            "result_count": len(results),
            "results": results,
        }

    def _evaluate_one(
        self,
        ground_truth: dict[str, Any],
        spec: dict[str, Any],
    ) -> dict[str, Any] | None:
        procedure = spec.get("procedure", {})
        capability = procedure.get("capability", "")

        handler = self._handlers.get(capability)
        if handler is None:
            return {
                "schema_version": "0.1.0",
                "id": f"evr_{uuid4().hex}",
                "metric": "availability",
                "score": 0.0,
                "passed": False,
                "details": {
                    "error": f"No handler registered for capability: {capability}",
                    "spec_id": spec.get("id", ""),
                },
            }

        try:
            inputs = ground_truth.get("inputs", {})
            expected = ground_truth.get("expected_outputs", {})
            actual = handler(inputs)

            scores = self._compute_scores(actual, expected, spec.get("scoring_criteria", {}))
            threshold = spec.get("pass_threshold", 0.8)
            overall = sum(scores.values()) / max(len(scores), 1) >= threshold

            result_id = f"evr_{uuid4().hex}"
            return {
                "schema_version": "0.1.0",
                "id": result_id,
                "metric": "composite",
                "score": sum(scores.values()) / max(len(scores), 1),
                "passed": overall,
                "details": {"scores": scores, "ground_truth_id": ground_truth.get("id", "")},
            }
        except Exception as e:
            return {
                "schema_version": "0.1.0",
                "id": f"evr_{uuid4().hex}",
                "metric": "execution",
                "score": 0.0,
                "passed": False,
                "details": {"error": str(e), "ground_truth_id": ground_truth.get("id", "")},
            }

    def _compute_scores(
        self,
        actual: Any,
        expected: Any,
        criteria: dict[str, Any],
    ) -> dict[str, float]:
        scores: dict[str, float] = {}
        for metric_name, cfg in criteria.items():
            higher_is_better = cfg.get("higher_is_better", True) if isinstance(cfg, dict) else True
            score = self._score_metric(metric_name, actual, expected, higher_is_better)
            scores[metric_name] = score
        return scores

    def _score_metric(
        self,
        metric: str,
        actual: Any,
        expected: Any,
        higher_is_better: bool,
    ) -> float:
        if metric == "precision":
            return self._precision(actual, expected)
        if metric == "recall":
            return self._recall(actual, expected)
        if metric == "accuracy":
            return self._accuracy(actual, expected)
        if metric == "consistency":
            return self._consistency(actual, expected)
        if metric == "recall_at_k":
            return self._recall_at_k(actual, expected)
        if metric == "precision_at_k":
            return self._precision_at_k(actual, expected)
        if isinstance(actual, dict) and isinstance(expected, dict):
            score_val = actual.get("score")
            if score_val is not None:
                return float(score_val)
        return 1.0 if actual == expected else 0.0

    @staticmethod
    def _precision(actual: Any, expected: Any) -> float:
        a_set = EvaluationRunner._to_set(actual)
        e_set = EvaluationRunner._to_set(expected)
        if not a_set:
            return 1.0
        true_positives = len(a_set & e_set)
        return true_positives / len(a_set)

    @staticmethod
    def _recall(actual: Any, expected: Any) -> float:
        a_set = EvaluationRunner._to_set(actual)
        e_set = EvaluationRunner._to_set(expected)
        if not e_set:
            return 1.0
        true_positives = len(a_set & e_set)
        return true_positives / len(e_set)

    @staticmethod
    def _accuracy(actual: Any, expected: Any) -> float:
        if isinstance(expected, (int, float)):
            return 1.0 if actual == expected else 0.0
        a_set = EvaluationRunner._to_set(actual)
        e_set = EvaluationRunner._to_set(expected)
        union = a_set | e_set
        if not union:
            return 1.0
        intersection = a_set & e_set
        return len(intersection) / len(union)

    @staticmethod
    def _consistency(actual: Any, expected: Any) -> float:
        if isinstance(actual, dict):
            score: Any = actual.get("score")
            if score is None:
                score = actual.get("consistency", 0.0)
            return float(score)
        if isinstance(actual, (int, float)):
            return float(actual)
        return 0.0

    @staticmethod
    def _recall_at_k(actual: Any, expected: Any) -> float:
        a_set = EvaluationRunner._to_set(actual)
        e_set = EvaluationRunner._to_set(expected)
        if not e_set:
            return 1.0
        return len(a_set & e_set) / len(e_set)

    @staticmethod
    def _precision_at_k(actual: Any, expected: Any) -> float:
        a_set = EvaluationRunner._to_set(actual)
        e_set = EvaluationRunner._to_set(expected)
        if not a_set:
            return 1.0
        return len(a_set & e_set) / len(a_set)

    @staticmethod
    def _to_set(value: Any) -> set[Any]:
        if isinstance(value, set):
            return value
        if isinstance(value, list):
            return set(value)
        if isinstance(value, dict):
            result: set[Any] = set()
            for k, v in value.items():
                result.add(k)
                if isinstance(v, (list, set)):
                    result.update(v)
            return result
        if isinstance(value, str):
            return {value}
        return {value}
