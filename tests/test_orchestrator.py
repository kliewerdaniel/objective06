"""Tests for the Orchestrator."""

from __future__ import annotations

import time

from src.self.orchestrator import Orchestrator, RetryManager, Scheduler


class FakeObserver:
    def __init__(self) -> None:
        self.call_count = 0

    def poll_once(self) -> int:
        self.call_count += 1
        return 3


class FakeExtractor:
    def __init__(self) -> None:
        self.call_count = 0

    def process_events(self, events: list) -> list[str]:
        self.call_count += 1
        return [f"ko_{i}" for i in range(len(events))]


class FakeMemory:
    def __init__(self) -> None:
        self._events = [{"id": "evt_001"}, {"id": "evt_002"}]

    def query_events(self, spec: dict | None = None) -> list[dict]:
        return self._events

    def store_knowledge(self, ko: dict) -> str:
        return "ko_stored"


class FakeHealth:
    def __init__(self) -> None:
        self.heartbeats: list[str] = []

    def heartbeat(self, subsystem: str) -> None:
        self.heartbeats.append(subsystem)


class FakeAuditLog:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def append(self, **kwargs: str) -> None:
        self.entries.append(kwargs)


# --- Scheduler ---


def test_schedule_every() -> None:
    sch = Scheduler()
    calls: list[int] = []
    sch.every(0.01, lambda: calls.append(1), "test")
    due = sch.pop_due(time.time())
    assert len(due) == 1
    due[0]()
    assert len(calls) == 1


def test_schedule_once() -> None:
    sch = Scheduler()
    calls: list[int] = []
    sch.once(lambda: calls.append(1), "test")
    assert sch.pending_count() == 1
    due = sch.pop_due()
    assert len(due) == 1
    assert sch.pending_count() == 0


def test_schedule_cancel() -> None:
    sch = Scheduler()
    wid = sch.every(10, lambda: None, "test")
    assert sch.cancel(wid) is True
    assert sch.cancel("nonexistent") is False


# --- Retry Manager ---


def test_retry_success() -> None:
    rm = RetryManager(max_retries=3, base_delay=0.01)
    result = rm.run(lambda: "ok", "test")
    assert result["success"] is True
    assert result["attempts"] == 1


def test_retry_failure() -> None:
    rm = RetryManager(max_retries=2, base_delay=0.01)

    def fail() -> None:
        msg = "always fails"
        raise RuntimeError(msg)

    result = rm.run(fail, "fail_test")
    assert result["success"] is False
    assert result["attempts"] == 2


# --- Orchestrator ---


def test_orchestrator_start_stop() -> None:
    orch = Orchestrator(
        FakeObserver(),
        FakeExtractor(),
        FakeMemory(),
        FakeHealth(),
        FakeAuditLog(),
    )
    orch.start()
    assert orch._running
    orch.stop()
    assert not orch._running


def test_orchestrator_tick() -> None:
    orch = Orchestrator(
        FakeObserver(),
        FakeExtractor(),
        FakeMemory(),
        FakeHealth(),
        FakeAuditLog(),
    )
    orch.start()
    calls: list[int] = []
    orch.scheduler.every(0, lambda: calls.append(1), "test")
    count = orch.tick()
    assert count == 1
    assert len(calls) == 1


def test_orchestrator_pipeline() -> None:
    obs = FakeObserver()
    ext = FakeExtractor()
    mem = FakeMemory()
    health = FakeHealth()
    audit = FakeAuditLog()
    orch = Orchestrator(obs, ext, mem, health, audit)
    orch.start()
    total = orch.run_pipeline()
    assert total > 0
    assert obs.call_count == 1
    assert ext.call_count == 1


def test_orchestrator_audit_on_start() -> None:
    audit = FakeAuditLog()
    orch = Orchestrator(
        FakeObserver(),
        FakeExtractor(),
        FakeMemory(),
        FakeHealth(),
        audit,
    )
    orch.start()
    assert any(e.get("action") == "start" for e in audit.entries)


def test_orchestrator_health_on_tick() -> None:
    health = FakeHealth()
    orch = Orchestrator(
        FakeObserver(),
        FakeExtractor(),
        FakeMemory(),
        health,
        FakeAuditLog(),
    )
    orch.start()
    orch.tick()
    assert "orchestrator" in health.heartbeats
