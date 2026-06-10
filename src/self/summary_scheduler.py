"""Summary Scheduler — manages user-configured cadences for summaries."""

from __future__ import annotations

import logging
from typing import Any


class SummaryScheduler:
    def __init__(self) -> None:
        self._log = logging.getLogger("self.summary_scheduler")
        self._schedules: dict[str, dict[str, Any]] = {}

    def add_schedule(
        self,
        name: str,
        cadence: str,
        summary_type: str,
        enabled: bool = True,
    ) -> dict[str, Any]:
        schedule = {
            "name": name,
            "cadence": cadence,
            "summary_type": summary_type,
            "enabled": enabled,
            "last_run": None,
            "next_run": None,
        }
        self._schedules[name] = schedule
        self._log.info("Added schedule %s with cadence %s", name, cadence)
        return schedule

    def remove_schedule(self, name: str) -> bool:
        if name in self._schedules:
            del self._schedules[name]
            self._log.info("Removed schedule %s", name)
            return True
        return False

    def enable_schedule(self, name: str) -> bool:
        if name in self._schedules:
            self._schedules[name]["enabled"] = True
            return True
        return False

    def disable_schedule(self, name: str) -> bool:
        if name in self._schedules:
            self._schedules[name]["enabled"] = False
            return True
        return False

    def get_schedule(self, name: str) -> dict[str, Any] | None:
        return self._schedules.get(name)

    def list_schedules(self) -> list[dict[str, Any]]:
        return list(self._schedules.values())

    def get_due_schedules(self) -> list[dict[str, Any]]:
        due: list[dict[str, Any]] = []
        for schedule in self._schedules.values():
            if schedule["enabled"] and self._is_due(schedule):
                due.append(schedule)
        return due

    def _is_due(self, schedule: dict[str, Any]) -> bool:
        return schedule["last_run"] is None

    def mark_run(self, name: str) -> None:
        if name in self._schedules:
            self._schedules[name]["last_run"] = "2024-01-01T00:00:00Z"
