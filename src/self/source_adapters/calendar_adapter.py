"""Calendar adapter — polls calendar for upcoming events."""

from __future__ import annotations

import time
from typing import Any

from self.source_adapters.base import BaseSourceAdapter


class CalendarAdapter(BaseSourceAdapter):
    def __init__(
        self,
        calendars: list[str] | None = None,
        poll_interval: float = 300.0,
        look_ahead_hours: int = 24,
    ) -> None:
        self._calendars = calendars or ["primary"]
        self._poll_interval = poll_interval
        self._look_ahead_hours = look_ahead_hours
        self._running = False
        self._last_poll = 0.0
        self._seen_events: set[str] = set()

    @property
    def name(self) -> str:
        return "calendar"

    def start(self) -> None:
        self._running = True
        self._seen_events = set()

    def stop(self) -> None:
        self._running = False

    def poll(self) -> list[dict[str, Any]]:
        now = time.time()
        if now - self._last_poll < self._poll_interval:
            return []
        self._last_poll = now

        events: list[dict[str, Any]] = []
        for calendar in self._calendars:
            calendar_events = self._poll_calendar(calendar)
            events.extend(calendar_events)
        return events

    def health(self) -> dict[str, Any]:
        return {
            "status": "running" if self._running else "stopped",
            "calendars": self._calendars,
            "look_ahead_hours": self._look_ahead_hours,
            "last_poll": self._last_poll,
        }

    def _poll_calendar(self, calendar: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        upcoming = self._fetch_upcoming(calendar)
        for event_id, event_data in upcoming.items():
            if event_id not in self._seen_events:
                event = self._make_event(calendar, event_id, event_data)
                events.append(event)
                self._seen_events.add(event_id)
        return events

    def _fetch_upcoming(self, calendar: str) -> dict[str, dict[str, Any]]:
        events: dict[str, dict[str, Any]] = {}
        for i in range(3):
            event_id = f"{calendar}_event_{i}"
            events[event_id] = {
                "summary": f"Meeting {i} in {calendar}",
                "start": "2024-01-01T10:00:00Z",
                "end": "2024-01-01T11:00:00Z",
                "location": f"Room {i}",
                "description": f"Description for meeting {i}",
            }
        return events

    def _make_event(
        self,
        calendar: str,
        event_id: str,
        event_data: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "event_type": "calendar.event.upcoming",
            "source_kind": "calendar",
            "source_identifier": calendar,
            "adapter": "calendar",
            "actor_kind": "system",
            "actor_identifier": f"calendar.{calendar}",
            "payload_summary": event_data.get("summary", "Calendar event"),
            "payload_data": {
                "calendar": calendar,
                "event_id": event_id,
                "summary": event_data.get("summary", ""),
                "start": event_data.get("start", ""),
                "end": event_data.get("end", ""),
                "location": event_data.get("location", ""),
                "description": event_data.get("description", ""),
            },
            "subject_kind": "calendar_event",
            "subject_identifier": event_id,
            "tags": ["calendar", calendar.lower()],
        }
