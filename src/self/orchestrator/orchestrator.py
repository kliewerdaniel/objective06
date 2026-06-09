"""Orchestrator — main loop, lifecycle, and pipeline wiring."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

from .retry_manager import RetryManager
from .scheduler import Scheduler


class Orchestrator:
    def __init__(
        self,
        observer: Any,
        extractor: Any,
        memory: Any,
        health: Any,
        audit_log: Any,
        loop_interval: float = 0.1,
    ) -> None:
        self._observer = observer
        self._extractor = extractor
        self._memory = memory
        self._health = health
        self._audit_log = audit_log
        self._loop_interval = loop_interval
        self._scheduler = Scheduler()
        self._retry = RetryManager()
        self._running = False

    @property
    def scheduler(self) -> Scheduler:
        return self._scheduler

    def start(self) -> None:
        self._running = True
        self._audit_log.append(
            actor="orchestrator", action="start", entity_type="system", entity_id="main"
        )
        self._health.heartbeat("orchestrator")

    def stop(self) -> None:
        self._running = False
        self._audit_log.append(
            actor="orchestrator", action="stop", entity_type="system", entity_id="main"
        )

    def tick(self) -> int:
        if not self._running:
            return 0
        now = time.time()
        due = self._scheduler.pop_due(now)
        for callback in due:
            self._invoke(callback)
        self._health.heartbeat("orchestrator")
        return len(due)

    def run_forever(self) -> None:
        self.start()
        while self._running:
            self.tick()
            time.sleep(self._loop_interval)

    def run_pipeline(self, source: str = "filesystem") -> int:
        total = 0
        poll_result = self._retry.run(lambda: self._observer.poll_once(), label="observer.poll")
        if poll_result["success"]:
            total += poll_result["result"]
        events = self._memory.query_events({"limit": 100})
        if events:
            extract_result = self._retry.run(
                lambda: self._extractor.process_events(events), label="extractor.process"
            )
            if extract_result["success"]:
                total += len(extract_result["result"])
        self._health.heartbeat("orchestrator")
        return total

    def _invoke(self, callback: Callable[[], Any]) -> None:
        try:
            callback()
        except Exception as e:
            self._audit_log.append(
                actor="orchestrator",
                action="callback_failed",
                entity_type="callback",
                entity_id=str(id(callback)),
                reason=str(e),
            )
