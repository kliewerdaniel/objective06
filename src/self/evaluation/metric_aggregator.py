"""Metric Aggregator — aggregates results across runs, detects regressions."""

from __future__ import annotations

from typing import Any


class MetricAggregator:
    def __init__(self, storage: Any) -> None:
        self._storage = storage

    def run_results(self, run_id: str) -> list[dict[str, Any]]:
        return self._storage.query("evaluation_result", {"run_id": run_id})

    def spec_results(self, spec_id: str, limit: int = 100) -> list[dict[str, Any]]:
        runs = self._storage.query("evaluation_run", {"spec_id": spec_id, "limit": limit})
        all_results: list[dict[str, Any]] = []
        for run in runs:
            rid = run.get("id", "")
            results = self._storage.query("evaluation_result", {"run_id": rid})
            for r in results:
                r["_run_status"] = run.get("status", "")
                r["_run_started"] = run.get("started_at", "")
            all_results.extend(results)
        return all_results

    def aggregate(self, results: list[dict[str, Any]]) -> dict[str, Any]:
        if not results:
            return {"count": 0, "mean_score": 0.0, "pass_rate": 1.0, "metrics": {}}

        by_metric: dict[str, list[float]] = {}
        for r in results:
            metric = r.get("metric", "unknown")
            score = r.get("score", 0.0)
            by_metric.setdefault(metric, []).append(score)

        metrics_summary: dict[str, Any] = {}
        for metric, scores in by_metric.items():
            metrics_summary[metric] = {
                "count": len(scores),
                "mean": sum(scores) / len(scores),
                "min": min(scores),
                "max": max(scores),
            }

        all_scores = [r.get("score", 0.0) for r in results]
        passed = sum(1 for r in results if r.get("passed", False))
        return {
            "count": len(results),
            "mean_score": sum(all_scores) / len(all_scores),
            "pass_rate": passed / len(results) if results else 1.0,
            "metrics": metrics_summary,
        }

    def detect_regressions(
        self,
        spec_id: str,
        window: int = 5,
    ) -> list[dict[str, Any]]:
        runs = self._storage.query(
            "evaluation_run",
            {"spec_id": spec_id, "limit": window * 2, "order_by": "timestamp"},
        )
        if len(runs) < 2:
            return []

        recent_runs = runs[:window]
        baseline_runs = runs[window : window * 2] if len(runs) >= window * 2 else runs[window:]

        def _mean_score(run_list: list[dict[str, Any]]) -> float:
            scores: list[float] = []
            for run in run_list:
                rid = run.get("id", "")
                results = self._storage.query("evaluation_result", {"run_id": rid})
                scores.extend(r.get("score", 0.0) for r in results)
            return sum(scores) / max(len(scores), 1)

        recent_mean = _mean_score(recent_runs)
        baseline_mean = _mean_score(baseline_runs)

        regressions: list[dict[str, Any]] = []
        if baseline_mean > 0:
            delta = (recent_mean - baseline_mean) / baseline_mean
            if delta < -0.1:
                regressions.append(
                    {
                        "spec_id": spec_id,
                        "baseline_mean": baseline_mean,
                        "recent_mean": recent_mean,
                        "delta": delta,
                        "severity": "major" if delta < -0.2 else "minor",
                    }
                )
        return regressions
