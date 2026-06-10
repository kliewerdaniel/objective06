"""Tests for email_adapter."""

from __future__ import annotations

from self.source_adapters.email_adapter import EmailAdapter


def test_email_adapter_name() -> None:
    adapter = EmailAdapter()
    assert adapter.name == "email"


def test_email_adapter_health() -> None:
    adapter = EmailAdapter(
        email_folders=["INBOX", "Sent"],
        email_server="imap.gmail.com",
    )
    health = adapter.health()
    assert health["folders"] == ["INBOX", "Sent"]
    assert health["server"] == "imap.gmail.com"
    assert health["status"] == "stopped"


def test_email_adapter_start_stop() -> None:
    adapter = EmailAdapter()
    adapter.start()
    assert adapter._running is True
    adapter.stop()
    assert adapter._running is False


def test_email_adapter_poll_interval() -> None:
    adapter = EmailAdapter(poll_interval=300.0)
    adapter.start()
    events = adapter.poll()
    assert isinstance(events, list)
    assert len(events) > 0


def test_email_adapter_event_structure() -> None:
    adapter = EmailAdapter()
    adapter.start()
    events = adapter.poll()
    if events:
        event = events[0]
        assert "event_type" in event
        assert "source_kind" in event
        assert event["source_kind"] == "email"
        assert "adapter" in event
        assert event["adapter"] == "email"


def test_email_adapter_multiple_folders() -> None:
    adapter = EmailAdapter(email_folders=["INBOX", "Sent"])
    adapter.start()
    events = adapter.poll()
    folders_in_events = {e["payload_data"]["folder"] for e in events}
    assert "INBOX" in folders_in_events
    assert "Sent" in folders_in_events


def test_email_adapter_deduplication() -> None:
    adapter = EmailAdapter()
    adapter.start()
    adapter.poll()
    events2 = adapter.poll()
    assert len(events2) == 0
