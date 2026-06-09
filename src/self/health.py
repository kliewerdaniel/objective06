"""Health monitor with heartbeats for subsystem monitoring."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SubsystemStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STOPPED = "stopped"


@dataclass
class Heartbeat:
    subsystem: str
    timestamp: float = field(default_factory=time.time)
    status: SubsystemStatus = SubsystemStatus.HEALTHY
    message: str = ""


class HealthMonitor:
    def __init__(self, heartbeat_timeout: float = 30.0) -> None:
        self._heartbeat_timeout = heartbeat_timeout
        self._heartbeats: dict[str, Heartbeat] = {}
        self._statuses: dict[str, SubsystemStatus] = {}

    def heartbeat(
        self, subsystem: str, status: SubsystemStatus = SubsystemStatus.HEALTHY, message: str = ""
    ) -> None:
        self._heartbeats[subsystem] = Heartbeat(
            subsystem=subsystem,
            timestamp=time.time(),
            status=status,
            message=message,
        )
        self._statuses[subsystem] = status

    def get_status(self, subsystem: str) -> SubsystemStatus:
        hb = self._heartbeats.get(subsystem)
        if hb is None:
            return SubsystemStatus.STOPPED
        if time.time() - hb.timestamp > self._heartbeat_timeout:
            return SubsystemStatus.UNHEALTHY
        return hb.status

    def all_statuses(self) -> dict[str, dict[str, Any]]:
        result: dict[str, dict[str, Any]] = {}
        for subsystem in list(self._heartbeats.keys()) + list(self._statuses.keys()):
            status = self.get_status(subsystem)
            hb = self._heartbeats.get(subsystem)
            result[subsystem] = {
                "status": status.value,
                "last_heartbeat": hb.timestamp if hb else None,
                "message": hb.message if hb else "",
            }
        return result

    @property
    def system_healthy(self) -> bool:
        if not self._heartbeats:
            return False
        return all(self.get_status(s) == SubsystemStatus.HEALTHY for s in self._heartbeats)

    @property
    def degraded_subsystems(self) -> list[str]:
        return [
            s
            for s in self._heartbeats
            if self.get_status(s) in (SubsystemStatus.DEGRADED, SubsystemStatus.UNHEALTHY)
        ]
