"""Tests for calendar_adapter."""

from __future__ import annotations

from self.source_adapters.calendar_adapter import CalendarAdapter


def test_calendar_adapter_name() -> None:
    adapter = CalendarAdapter()
    assert adapter.name == "calendar"


def test_calendar_adapter_health() -> None:
    adapter = CalendarAdapter(calendars=["primary", "work"])
    health = adapter.health()
    assert health["calendars"] == ["primary", "work"]
    assert health["status"] == "stopped"


def test_calendar_adapter_start_stop() -> None:
    adapter = CalendarAdapter()
    adapter.start()
    assert adapter._running is True
    adapter.stop()
    assert adapter._running is False


def test_calendar_adapter_poll_interval() -> None:
    adapter = CalendarAdapter(poll_interval=300.0)
    adapter.start()
    events = adapter.poll()
    assert isinstance(events, list)
    assert len(events) > 0


def test_calendar_adapter_event_structure() -> None:
    adapter = CalendarAdapter()
    adapter.start()
    events = adapter.poll()
    if events:
        event = events[0]
        assert "event_type" in event
        assert "source_kind" in event
        assert event["source_kind"] == "calendar"
        assert "adapter" in event
        assert event["adapter"] == "calendar"


def test_calendar_adapter_multiple_calendars() -> None:
    adapter = CalendarAdapter(calendars=["primary", "work"])
    adapter.start()
    events = adapter.poll()
    calendars_in_events = {e["payload_data"]["calendar"] for e in events}
    assert "primary" in calendars_in_events
    assert "work" in calendars_in_events


def test_calendar_adapter_deduplication() -> None:
    adapter = CalendarAdapter()
    adapter.start()
    adapter.poll()
    events2 = adapter.poll()
    assert len(events2) == 0
