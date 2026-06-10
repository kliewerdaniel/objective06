"""Tests for terminal_session adapter."""

from __future__ import annotations

from self.source_adapters.terminal_session import TerminalSessionAdapter


def test_terminal_session_name() -> None:
    adapter = TerminalSessionAdapter()
    assert adapter.name == "terminal"


def test_terminal_session_health() -> None:
    adapter = TerminalSessionAdapter()
    health = adapter.health()
    assert health["status"] == "stopped"
    assert health["commands_tracked"] == 0


def test_terminal_session_start_stop() -> None:
    adapter = TerminalSessionAdapter()
    adapter.start()
    assert adapter._running is True
    adapter.stop()
    assert adapter._running is False


def test_terminal_session_poll_interval() -> None:
    adapter = TerminalSessionAdapter(poll_interval=10.0)
    adapter.start()
    events = adapter.poll()
    assert isinstance(events, list)
    assert len(events) > 0


def test_terminal_session_event_structure() -> None:
    adapter = TerminalSessionAdapter()
    adapter.start()
    events = adapter.poll()
    if events:
        event = events[0]
        assert "event_type" in event
        assert "source_kind" in event
        assert event["source_kind"] == "terminal"
        assert "adapter" in event
        assert event["adapter"] == "terminal_session"


def test_terminal_session_deduplication() -> None:
    adapter = TerminalSessionAdapter()
    adapter.start()
    adapter.poll()
    events2 = adapter.poll()
    assert len(events2) == 0


def test_terminal_session_max_history() -> None:
    adapter = TerminalSessionAdapter(max_history=5)
    adapter.start()
    for _ in range(10):
        adapter.poll()
    assert len(adapter._command_history) <= 5
