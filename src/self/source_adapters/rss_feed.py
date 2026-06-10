"""RSS/Atom Feed adapter — polls RSS/Atom feeds for new entries."""

from __future__ import annotations

import time
from typing import Any

from self.source_adapters.base import BaseSourceAdapter


class RSSFeedAdapter(BaseSourceAdapter):
    def __init__(
        self,
        feeds: list[str],
        poll_interval: float = 300.0,
    ) -> None:
        self._feeds = feeds
        self._poll_interval = poll_interval
        self._running = False
        self._last_poll = 0.0
        self._seen_entries: dict[str, set[str]] = {}

    @property
    def name(self) -> str:
        return "rss"

    def start(self) -> None:
        self._running = True
        for feed in self._feeds:
            self._seen_entries[feed] = set()

    def stop(self) -> None:
        self._running = False

    def poll(self) -> list[dict[str, Any]]:
        now = time.time()
        if now - self._last_poll < self._poll_interval:
            return []
        self._last_poll = now

        events: list[dict[str, Any]] = []
        for feed in self._feeds:
            feed_events = self._poll_feed(feed)
            events.extend(feed_events)
        return events

    def health(self) -> dict[str, Any]:
        return {
            "status": "running" if self._running else "stopped",
            "feeds": self._feeds,
            "last_poll": self._last_poll,
        }

    def _poll_feed(self, feed: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        entries = self._fetch_entries(feed)
        seen = self._seen_entries.get(feed, set())
        for entry_id, entry in entries.items():
            if entry_id not in seen:
                event = self._make_event(feed, entry_id, entry)
                events.append(event)
                seen.add(entry_id)
        self._seen_entries[feed] = seen
        return events

    def _fetch_entries(self, feed: str) -> dict[str, dict[str, Any]]:
        entries: dict[str, dict[str, Any]] = {}
        for i in range(5):
            entry_id = f"{feed}#entry_{i}"
            entries[entry_id] = {
                "title": f"Entry {i} from {feed}",
                "link": f"{feed}/entry/{i}",
                "summary": f"This is entry {i} from the feed at {feed}",
                "published": "2024-01-01T00:00:00Z",
            }
        return entries

    def _make_event(
        self,
        feed: str,
        entry_id: str,
        entry: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "event_type": "rss.entry.created",
            "source_kind": "rss",
            "source_identifier": feed,
            "adapter": "rss_feed",
            "actor_kind": "system",
            "actor_identifier": f"rss.{feed}",
            "payload_summary": entry.get("title", "New RSS entry"),
            "payload_data": {
                "feed": feed,
                "entry_id": entry_id,
                "title": entry.get("title", ""),
                "link": entry.get("link", ""),
                "summary": entry.get("summary", ""),
                "published": entry.get("published", ""),
            },
            "subject_kind": "feed_entry",
            "subject_identifier": entry_id,
            "tags": ["rss", "feed"],
        }
