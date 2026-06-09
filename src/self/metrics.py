"""Metrics collection infrastructure for SELF."""

from __future__ import annotations

import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricValue:
    name: str
    value: float | int | str
    timestamp: float = field(default_factory=time.time)
    tags: dict[str, str] = field(default_factory=dict)


class MetricsCollector:
    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)
        self._gauges: dict[str, float] = {}
        self._histograms: dict[str, list[float]] = defaultdict(list)
        self._values: list[MetricValue] = []

    def increment(self, name: str, amount: int = 1, tags: dict[str, str] | None = None) -> None:
        self._counters[name] += amount
        self._values.append(MetricValue(name=name, value=self._counters[name], tags=tags or {}))

    def gauge(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        self._gauges[name] = value
        self._values.append(MetricValue(name=name, value=value, tags=tags or {}))

    def observe(self, name: str, value: float, tags: dict[str, str] | None = None) -> None:
        self._histograms[name].append(value)
        self._values.append(MetricValue(name=name, value=value, tags=tags or {}))

    def get_counter(self, name: str) -> int:
        return self._counters.get(name, 0)

    def get_gauge(self, name: str) -> float | None:
        return self._gauges.get(name)

    def histogram_summary(self, name: str) -> dict[str, float] | None:
        values = self._histograms.get(name)
        if not values:
            return None
        sorted_v = sorted(values)
        n = len(sorted_v)

        def percentile(p: float) -> float:
            idx = max(0, min(n - 1, int(n * p)))
            return sorted_v[idx]

        return {
            "count": n,
            "min": sorted_v[0],
            "max": sorted_v[-1],
            "avg": sum(sorted_v) / n,
            "p50": percentile(0.5),
            "p95": percentile(0.95),
            "p99": percentile(0.99),
        }

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": dict(self._counters),
            "gauges": dict(self._gauges),
            "histograms": {k: self.histogram_summary(k) for k in self._histograms},
        }

    def drain_values(self) -> list[MetricValue]:
        values = list(self._values)
        self._values.clear()
        return values


_collector = MetricsCollector()


def get_collector() -> MetricsCollector:
    return _collector
