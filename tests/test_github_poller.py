"""Tests for github_poller adapter."""

from __future__ import annotations

from self.source_adapters.github_poller import GitHubPoller


def test_github_poller_name() -> None:
    poller = GitHubPoller(repos=["owner/repo"])
    assert poller.name == "github"


def test_github_poller_health() -> None:
    poller = GitHubPoller(repos=["owner/repo1", "owner/repo2"])
    health = poller.health()
    assert health["repos"] == ["owner/repo1", "owner/repo2"]
    assert health["status"] == "stopped"


def test_github_poller_start_stop() -> None:
    poller = GitHubPoller(repos=["owner/repo"])
    poller.start()
    assert poller._running is True
    poller.stop()
    assert poller._running is False


def test_github_poller_poll_interval() -> None:
    poller = GitHubPoller(repos=["owner/repo"], poll_interval=60.0)
    poller.start()
    events = poller.poll()
    assert isinstance(events, list)
    assert len(events) > 0


def test_github_poller_event_structure() -> None:
    poller = GitHubPoller(repos=["owner/repo"])
    poller.start()
    events = poller.poll()
    if events:
        event = events[0]
        assert "event_type" in event
        assert "source_kind" in event
        assert event["source_kind"] == "github"
        assert "adapter" in event
        assert event["adapter"] == "github_poller"


def test_github_poller_multiple_repos() -> None:
    poller = GitHubPoller(repos=["owner/repo1", "owner/repo2"])
    poller.start()
    events = poller.poll()
    repos_in_events = {e["payload_data"]["repo"] for e in events}
    assert "owner/repo1" in repos_in_events
    assert "owner/repo2" in repos_in_events
