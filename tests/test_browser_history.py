"""Tests for browser_history adapter."""

from __future__ import annotations

from self.source_adapters.browser_history import BrowserHistoryAdapter


def test_browser_history_name() -> None:
    adapter = BrowserHistoryAdapter()
    assert adapter.name == "browser_history"


def test_browser_history_health() -> None:
    adapter = BrowserHistoryAdapter(browsers=["chrome", "firefox"])
    health = adapter.health()
    assert health["browsers"] == ["chrome", "firefox"]
    assert health["status"] == "stopped"


def test_browser_history_start_stop() -> None:
    adapter = BrowserHistoryAdapter()
    adapter.start()
    assert adapter._running is True
    adapter.stop()
    assert adapter._running is False


def test_browser_history_poll_interval() -> None:
    adapter = BrowserHistoryAdapter(poll_interval=60.0)
    adapter.start()
    events = adapter.poll()
    assert isinstance(events, list)
    assert len(events) > 0


def test_browser_history_event_structure() -> None:
    adapter = BrowserHistoryAdapter()
    adapter.start()
    events = adapter.poll()
    if events:
        event = events[0]
        assert "event_type" in event
        assert "source_kind" in event
        assert event["source_kind"] == "browser"
        assert "adapter" in event
        assert event["adapter"] == "browser_history"


def test_browser_history_multiple_browsers() -> None:
    adapter = BrowserHistoryAdapter(browsers=["chrome", "firefox"])
    adapter.start()
    events = adapter.poll()
    browsers_in_events = {e["payload_data"]["browser"] for e in events}
    assert len(browsers_in_events) >= 1


def test_browser_history_deduplication() -> None:
    adapter = BrowserHistoryAdapter()
    adapter.start()
    adapter.poll()
    events2 = adapter.poll()
    assert len(events2) == 0
