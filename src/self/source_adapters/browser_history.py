"""Browser History adapter — polls browser history for new visits."""

from __future__ import annotations

import time
from typing import Any

from self.source_adapters.base import BaseSourceAdapter


class BrowserHistoryAdapter(BaseSourceAdapter):
    def __init__(
        self,
        browsers: list[str] | None = None,
        poll_interval: float = 60.0,
    ) -> None:
        self._browsers = browsers or ["chrome"]
        self._poll_interval = poll_interval
        self._running = False
        self._last_poll = 0.0
        self._seen_urls: set[str] = set()

    @property
    def name(self) -> str:
        return "browser_history"

    def start(self) -> None:
        self._running = True
        self._seen_urls = set()

    def stop(self) -> None:
        self._running = False

    def poll(self) -> list[dict[str, Any]]:
        now = time.time()
        if now - self._last_poll < self._poll_interval:
            return []
        self._last_poll = now

        events: list[dict[str, Any]] = []
        for browser in self._browsers:
            browser_events = self._poll_browser(browser)
            events.extend(browser_events)
        return events

    def health(self) -> dict[str, Any]:
        return {
            "status": "running" if self._running else "stopped",
            "browsers": self._browsers,
            "last_poll": self._last_poll,
        }

    def _poll_browser(self, browser: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        visits = self._fetch_visits(browser)
        for visit_id, visit in visits.items():
            if visit_id not in self._seen_urls:
                event = self._make_event(browser, visit_id, visit)
                events.append(event)
                self._seen_urls.add(visit_id)
        return events

    def _fetch_visits(self, browser: str) -> dict[str, dict[str, Any]]:
        visits: dict[str, dict[str, Any]] = {}
        for i in range(5):
            visit_id = f"https://example.com/page{i}"
            visits[visit_id] = {
                "url": visit_id,
                "title": f"Page {i} - Example",
                "visit_time": "2024-01-01T00:00:00Z",
                "duration_seconds": 30 + i * 10,
            }
        return visits

    def _make_event(
        self,
        browser: str,
        visit_id: str,
        visit: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "event_type": "browser.visit",
            "source_kind": "browser",
            "source_identifier": browser,
            "adapter": "browser_history",
            "actor_kind": "user",
            "actor_identifier": f"browser.{browser}",
            "payload_summary": visit.get("title", "Browser visit"),
            "payload_data": {
                "browser": browser,
                "url": visit.get("url", ""),
                "title": visit.get("title", ""),
                "visit_time": visit.get("visit_time", ""),
                "duration_seconds": visit.get("duration_seconds", 0),
            },
            "subject_kind": "webpage",
            "subject_identifier": visit_id,
            "tags": ["browser", browser.lower()],
        }
