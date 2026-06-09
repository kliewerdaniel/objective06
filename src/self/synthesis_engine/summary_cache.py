"""Summary Cache — caches synthesis outputs with TTL."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any


class SummaryCache:
    def __init__(self, ttl_minutes: int = 60) -> None:
        self._cache: dict[str, dict[str, Any]] = {}
        self._ttl = timedelta(minutes=ttl_minutes)

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self._cache.get(key)
        if entry is None:
            return None
        age = datetime.now(UTC) - datetime.fromisoformat(entry["cached_at"])
        if age > self._ttl:
            del self._cache[key]
            return None
        return entry["data"]

    def set(self, key: str, data: dict[str, Any]) -> None:
        self._cache[key] = {"data": data, "cached_at": datetime.now(UTC).isoformat()}

    def invalidate(self, key: str) -> None:
        self._cache.pop(key, None)

    def clear(self) -> None:
        self._cache.clear()

    def size(self) -> int:
        now = datetime.now(UTC)
        count = 0
        expired = []
        for key, entry in self._cache.items():
            age = now - datetime.fromisoformat(entry["cached_at"])
            if age > self._ttl:
                expired.append(key)
            else:
                count += 1
        for key in expired:
            del self._cache[key]
        return count
