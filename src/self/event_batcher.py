"""Event batcher — groups observation events into extraction units."""

from __future__ import annotations

from typing import Any


class EventBatcher:
    def __init__(self, max_batch_size: int = 20) -> None:
        self._max_batch_size = max_batch_size

    def time_batches(
        self, events: list[dict[str, Any]], window_minutes: float = 5.0
    ) -> list[list[dict[str, Any]]]:
        if not events:
            return []
        sorted_events = sorted(events, key=lambda e: e.get("monotonic_ts", 0))
        batches: list[list[dict[str, Any]]] = []
        current: list[dict[str, Any]] = []
        for event in sorted_events:
            current.append(event)
            if len(current) >= self._max_batch_size:
                batches.append(current)
                current = []
        if current:
            batches.append(current)
        return batches

    def source_batches(self, events: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = {}
        for event in events:
            source_kind = event.get("source", {}).get("kind", "unknown")
            grouped.setdefault(source_kind, []).append(event)
        result = []
        for group in grouped.values():
            for batch in self.time_batches(group):
                result.append(batch)
        return result

    def format_events(self, events: list[dict[str, Any]]) -> str:
        lines = []
        for event in events:
            eid = event.get("id", "")[:12]
            etype = event.get("event_type", "unknown")
            summary = event.get("payload", {}).get("summary", "")
            lines.append(f"[{eid}] {etype}: {summary}")
        return "\n".join(lines) if lines else "(no events)"
