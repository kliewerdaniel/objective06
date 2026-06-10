"""Tests for rss_feed adapter."""

from __future__ import annotations

from self.source_adapters.rss_feed import RSSFeedAdapter


def test_rss_feed_name() -> None:
    adapter = RSSFeedAdapter(feeds=["http://example.com/feed.xml"])
    assert adapter.name == "rss"


def test_rss_feed_health() -> None:
    adapter = RSSFeedAdapter(feeds=["http://example.com/feed1.xml", "http://example.com/feed2.xml"])
    health = adapter.health()
    assert health["feeds"] == ["http://example.com/feed1.xml", "http://example.com/feed2.xml"]
    assert health["status"] == "stopped"


def test_rss_feed_start_stop() -> None:
    adapter = RSSFeedAdapter(feeds=["http://example.com/feed.xml"])
    adapter.start()
    assert adapter._running is True
    adapter.stop()
    assert adapter._running is False


def test_rss_feed_poll_interval() -> None:
    adapter = RSSFeedAdapter(feeds=["http://example.com/feed.xml"], poll_interval=300.0)
    adapter.start()
    events = adapter.poll()
    assert isinstance(events, list)
    assert len(events) > 0


def test_rss_feed_event_structure() -> None:
    adapter = RSSFeedAdapter(feeds=["http://example.com/feed.xml"])
    adapter.start()
    events = adapter.poll()
    if events:
        event = events[0]
        assert "event_type" in event
        assert "source_kind" in event
        assert event["source_kind"] == "rss"
        assert "adapter" in event
        assert event["adapter"] == "rss_feed"


def test_rss_feed_multiple_feeds() -> None:
    adapter = RSSFeedAdapter(feeds=["http://example.com/feed1.xml", "http://example.com/feed2.xml"])
    adapter.start()
    events = adapter.poll()
    feeds_in_events = {e["payload_data"]["feed"] for e in events}
    assert "http://example.com/feed1.xml" in feeds_in_events
    assert "http://example.com/feed2.xml" in feeds_in_events


def test_rss_feed_deduplication() -> None:
    adapter = RSSFeedAdapter(feeds=["http://example.com/feed.xml"])
    adapter.start()
    adapter.poll()
    events2 = adapter.poll()
    assert len(events2) == 0
