"""Observer — orchestrates adapters, normalizer, ingest queue, and event log."""

from __future__ import annotations

import logging
import time
from typing import Any

from self.health import HealthMonitor, SubsystemStatus
from self.metrics import MetricsCollector
from self.normalizer import Normalizer
from self.source_adapters.base import BaseSourceAdapter


class Observer:
    def __init__(
        self,
        normalizer: Normalizer,
        ingest_queue: Any,
        event_log: Any,
        health_monitor: HealthMonitor,
        metrics: MetricsCollector,
        adapters: list[BaseSourceAdapter] | None = None,
    ) -> None:
        self._normalizer = normalizer
        self._queue = ingest_queue
        self._event_log = event_log
        self._health = health_monitor
        self._metrics = metrics
        self._adapters: list[BaseSourceAdapter] = adapters or []
        self._log = logging.getLogger("self.observer")

    def register_adapter(self, adapter: BaseSourceAdapter) -> None:
        self._adapters.append(adapter)

    def start(self) -> None:
        for adapter in self._adapters:
            adapter.start()
            self._health.heartbeat(adapter.name, SubsystemStatus.HEALTHY, "started")
            self._log.info("Adapter started: %s", adapter.name)

    def stop(self) -> None:
        for adapter in self._adapters:
            adapter.stop()
            self._health.heartbeat(adapter.name, SubsystemStatus.STOPPED, "stopped")
            self._log.info("Adapter stopped: %s", adapter.name)

    def poll_once(self) -> int:
        total = 0
        for adapter in self._adapters:
            try:
                raw_events = adapter.poll()
                if not raw_events:
                    continue
                for raw in raw_events:
                    event = self._normalizer.normalize(**raw)
                    try:
                        self._queue.enqueue(event)
                    except OverflowError:
                        self._log.error("Queue full, dropping event %s", event["id"])
                        self._metrics.increment(
                            "observer.events_dropped.total",
                            tags={"reason": "queue_full"},
                        )
                        continue
                    self._event_log.append(event)
                    self._metrics.increment(
                        "observer.events_emitted.total",
                        tags={"source": adapter.name},
                    )
                    total += 1
                self._health.heartbeat(
                    adapter.name,
                    SubsystemStatus.HEALTHY,
                    f"{len(raw_events)} events",
                )
            except Exception:
                self._log.exception("Adapter poll failed: %s", adapter.name)
                self._health.heartbeat(
                    adapter.name,
                    SubsystemStatus.DEGRADED,
                    "poll failed",
                )
                self._metrics.increment(
                    "observer.events_dropped.total",
                    tags={"reason": "adapter_error"},
                )
        self._metrics.gauge("observer.queue_depth", self._queue.size)
        return total

    def run_loop(self, interval_ms: float = 1000.0, max_cycles: int | None = None) -> None:
        self.start()
        cycles = 0
        try:
            while max_cycles is None or cycles < max_cycles:
                count = self.poll_once()
                if count > 0:
                    self._log.info("Polled %d events", count)
                cycles += 1
                time.sleep(interval_ms / 1000.0)
        except KeyboardInterrupt:
            self._log.info("Observer loop interrupted")
        finally:
            self.stop()
