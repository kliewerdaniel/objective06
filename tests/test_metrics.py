"""Tests for metrics collection."""

from __future__ import annotations

from self.metrics import MetricsCollector


def test_counter() -> None:
    m = MetricsCollector()
    m.increment("test.count")
    assert m.get_counter("test.count") == 1
    m.increment("test.count", 5)
    assert m.get_counter("test.count") == 6


def test_gauge() -> None:
    m = MetricsCollector()
    m.gauge("test.value", 42.0)
    assert m.get_gauge("test.value") == 42.0
    m.gauge("test.value", 13.0)
    assert m.get_gauge("test.value") == 13.0


def test_histogram() -> None:
    m = MetricsCollector()
    for v in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
        m.observe("test.latency", float(v))
    summary = m.histogram_summary("test.latency")
    assert summary is not None
    assert summary["count"] == 10
    assert summary["min"] == 1.0
    assert summary["max"] == 10.0
    assert summary["avg"] == 5.5
    assert summary["p50"] == 6.0


def test_snapshot() -> None:
    m = MetricsCollector()
    m.increment("req.count", 10)
    m.gauge("cpu.pct", 45.0)
    m.observe("latency.ms", 100.0)
    snap = m.snapshot()
    assert snap["counters"]["req.count"] == 10
    assert snap["gauges"]["cpu.pct"] == 45.0
    assert snap["histograms"]["latency.ms"]["count"] == 1


def test_drain() -> None:
    m = MetricsCollector()
    m.increment("test")
    assert len(m.drain_values()) == 1
    assert len(m.drain_values()) == 0
