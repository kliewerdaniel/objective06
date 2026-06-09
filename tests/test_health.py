"""Tests for health monitor."""

from __future__ import annotations

import time

from self.health import HealthMonitor, SubsystemStatus


def test_initial_state() -> None:
    h = HealthMonitor()
    assert h.system_healthy is False
    assert h.get_status("nonexistent") == SubsystemStatus.STOPPED


def test_heartbeat() -> None:
    h = HealthMonitor(heartbeat_timeout=60.0)
    h.heartbeat("storage", SubsystemStatus.HEALTHY)
    assert h.get_status("storage") == SubsystemStatus.HEALTHY
    assert h.system_healthy is True


def test_degraded_status() -> None:
    h = HealthMonitor()
    h.heartbeat("extractor", SubsystemStatus.DEGRADED, "model unavailable")
    assert h.get_status("extractor") == SubsystemStatus.DEGRADED
    assert "extractor" in h.degraded_subsystems


def test_heartbeat_timeout() -> None:
    h = HealthMonitor(heartbeat_timeout=0.1)
    h.heartbeat("observer", SubsystemStatus.HEALTHY)
    assert h.get_status("observer") == SubsystemStatus.HEALTHY
    time.sleep(0.15)
    assert h.get_status("observer") == SubsystemStatus.UNHEALTHY


def test_all_statuses() -> None:
    h = HealthMonitor()
    h.heartbeat("storage")
    h.heartbeat("observer", SubsystemStatus.DEGRADED)
    statuses = h.all_statuses()
    assert "storage" in statuses
    assert "observer" in statuses
    assert statuses["observer"]["status"] == "degraded"
