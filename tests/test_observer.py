"""Tests for the Observer."""

from __future__ import annotations

from self.health import HealthMonitor
from self.ingest_queue import IngestQueue
from self.metrics import MetricsCollector
from self.normalizer import Normalizer
from self.observer import Observer
from self.source_adapters.base import BaseSourceAdapter


class MockAdapter(BaseSourceAdapter):
    def __init__(self, events: list[dict] | None = None) -> None:
        self._events = events or []
        self._running = False

    @property
    def name(self) -> str:
        return "mock"

    def start(self) -> None:
        self._running = True

    def stop(self) -> None:
        self._running = False

    def poll(self) -> list[dict]:
        e = list(self._events)
        self._events.clear()
        return e

    def health(self) -> dict:
        return {"status": "running" if self._running else "stopped"}


class MockEventLog:
    def __init__(self) -> None:
        self.events: list[dict] = []

    def append(self, event: dict) -> str:
        self.events.append(event)
        return event["id"]


def test_observer_poll_once(storage: object) -> None:
    norm = Normalizer("test")
    queue = IngestQueue(storage)
    elog = MockEventLog()
    health = HealthMonitor()
    metrics = MetricsCollector()
    adapter = MockAdapter(
        [
            {
                "event_type": "file.created",
                "source_kind": "filesystem",
                "source_identifier": "/tmp",
                "adapter": "mock",
                "actor_kind": "system",
                "actor_identifier": "observer.test",
                "payload_summary": "created: file.txt",
                "payload_data": {"path": "/tmp/file.txt", "filename": "file.txt"},
            }
        ]
    )
    obs = Observer(norm, queue, elog, health, metrics, adapters=[adapter])
    count = obs.poll_once()
    assert count == 1
    assert len(elog.events) == 1
    assert elog.events[0]["event_type"] == "file.created"
    assert queue.size == 1


def test_observer_adapter_failure(storage: object) -> None:
    class FailingAdapter(MockAdapter):
        def poll(self) -> list[dict]:
            msg = "adapter error"
            raise RuntimeError(msg)

    norm = Normalizer("test")
    queue = IngestQueue(storage)
    elog = MockEventLog()
    health = HealthMonitor()
    metrics = MetricsCollector()
    adapter = FailingAdapter()
    obs = Observer(norm, queue, elog, health, metrics, adapters=[adapter])
    count = obs.poll_once()
    assert count == 0
    assert health.get_status("mock") != "healthy"


def test_observer_start_stop(storage: object) -> None:
    norm = Normalizer("test")
    queue = IngestQueue(storage)
    elog = MockEventLog()
    health = HealthMonitor()
    metrics = MetricsCollector()
    adapter = MockAdapter()
    obs = Observer(norm, queue, elog, health, metrics, adapters=[adapter])
    obs.start()
    assert adapter._running
    obs.stop()
    assert not adapter._running
