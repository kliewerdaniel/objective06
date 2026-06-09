"""Retry Manager — exponential backoff with jitter."""

from __future__ import annotations

import random
import time
from collections.abc import Callable
from typing import Any


class RetryManager:
    def __init__(
        self, max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0
    ) -> None:
        self._max_retries = max_retries
        self._base_delay = base_delay
        self._max_delay = max_delay

    def run(self, fn: Callable[[], Any], label: str = "") -> dict[str, Any]:
        last_error: Exception | None = None
        for attempt in range(1, self._max_retries + 1):
            try:
                result = fn()
                return {"success": True, "result": result, "attempts": attempt, "label": label}
            except Exception as e:
                last_error = e
                if attempt < self._max_retries:
                    delay = min(self._base_delay * (2 ** (attempt - 1)), self._max_delay)
                    jitter = random.uniform(0, delay * 0.5)
                    time.sleep(delay + jitter)
        return {
            "success": False,
            "error": str(last_error) if last_error else "Unknown error",
            "attempts": self._max_retries,
            "label": label,
        }
