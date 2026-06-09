"""Scheduler — cron-like and interval-based work scheduling."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any


class Scheduler:
    def __init__(self) -> None:
        self._recurring: list[dict[str, Any]] = []
        self._one_shot: list[dict[str, Any]] = []

    def every(self, interval_seconds: float, callback: Callable[[], Any], name: str = "") -> str:
        wid = f"sch_{len(self._recurring)}_{int(time.time())}"
        self._recurring.append(
            {
                "id": wid,
                "name": name or wid,
                "callback": callback,
                "interval": interval_seconds,
                "last_run": 0.0,
            }
        )
        return wid

    def once(self, callback: Callable[[], Any], name: str = "") -> str:
        wid = f"os_{len(self._one_shot)}_{int(time.time())}"
        self._one_shot.append({"id": wid, "name": name or wid, "callback": callback, "done": False})
        return wid

    def pop_due(self, now: float | None = None) -> list[Callable[[], Any]]:
        if now is None:
            now = time.time()
        due: list[Callable[[], Any]] = []
        for item in self._recurring:
            if now - item["last_run"] >= item["interval"]:
                item["last_run"] = now
                due.append(item["callback"])
        remaining: list[dict[str, Any]] = []
        for item in self._one_shot:
            if not item["done"]:
                item["done"] = True
                due.append(item["callback"])
            else:
                remaining.append(item)
        self._one_shot = remaining
        return due

    def cancel(self, work_id: str) -> bool:
        for pool in (self._recurring, self._one_shot):
            for item in pool:
                if item["id"] == work_id:
                    pool.remove(item)
                    return True
        return False

    def pending_count(self) -> int:
        return len(self._recurring) + sum(1 for o in self._one_shot if not o["done"])
