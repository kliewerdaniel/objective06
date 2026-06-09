"""Report Generator — produces human-readable evaluation reports."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class ReportGenerator:
    def __init__(self, storage: Any) -> None:
        self._storage = storage

    def generate(
        self,
        run_ids: list[str],
        summary: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        results: list[dict[str, Any]] = []
        for rid in run_ids:
            run = self._storage.get("evaluation_run", rid)
            if run:
                result_records = self._storage.query("evaluation_result", {"run_id": rid})
                results.append({"run": run, "results": result_records})

        markdown = self._render_markdown(results, summary)
        now = datetime.now(UTC).isoformat()
        report_id = f"erep_{uuid4().hex}"
        record = {
            "schema_version": "0.1.0",
            "id": report_id,
            "run_ids": run_ids,
            "summary": summary or {},
            "markdown": markdown,
            "created_at": now,
        }
        self._storage.insert("evaluation_report", record)
        return {**record, "ok": True}

    def _render_markdown(
        self,
        runs_data: list[dict[str, Any]],
        summary: dict[str, Any] | None,
    ) -> str:
        lines: list[str] = [
            "# Evaluation Report",
            "",
            f"**Generated:** {datetime.now(UTC).isoformat()}",
            "",
        ]

        if summary:
            lines.append("## Summary")
            lines.append("")
            lines.append(f"- **Runs:** {summary.get('run_count', 0)}")
            lines.append(f"- **Overall Pass Rate:** {summary.get('pass_rate', 0):.1%}")
            lines.append(f"- **Regressions Detected:** {summary.get('regression_count', 0)}")
            lines.append("")

        for item in runs_data:
            run = item.get("run", {})
            results = item.get("results", [])
            spec_id = run.get("spec_id", "unknown")
            spec = self._storage.get("evaluation_spec", spec_id)
            spec_name = spec.get("name", spec_id) if spec else spec_id
            status = run.get("status", "unknown")

            lines.append(f"## {spec_name}")
            lines.append("")
            lines.append(f"- **Run ID:** {run.get('id', 'unknown')}")
            lines.append(f"- **Status:** {status}")
            lines.append(f"- **Started:** {run.get('started_at', 'unknown')}")
            lines.append("")

            if results:
                lines.append("| Metric | Score | Passed | Details |")
                lines.append("| --- | --- | --- | --- |")
                for r in results:
                    metric = r.get("metric", "?")
                    score = r.get("score", 0.0)
                    passed = "✅" if r.get("passed", False) else "❌"
                    details = str(r.get("details", {}))[:80]
                    lines.append(f"| {metric} | {score:.3f} | {passed} | {details} |")
                lines.append("")

            lines.append("---")
            lines.append("")

        return "\n".join(lines)

    def get(self, report_id: str) -> dict[str, Any] | None:
        return self._storage.get("evaluation_report", report_id)

    def list_reports(self, limit: int = 20) -> list[dict[str, Any]]:
        return self._storage.query("evaluation_report", {"limit": limit, "order_by": "timestamp"})
