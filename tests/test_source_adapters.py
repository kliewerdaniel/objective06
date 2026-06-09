"""Tests for source adapters."""

from __future__ import annotations

import os
import tempfile

from self.source_adapters import FilesystemWatcher, GitPollingAdapter


def test_filesystem_watcher_poll() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        watcher = FilesystemWatcher([tmpdir], poll_interval=0)
        watcher.start()

        events = watcher.poll()
        assert len(events) == 0

        test_file = os.path.join(tmpdir, "test.txt")
        with open(test_file, "w") as f:
            f.write("hello")

        events = watcher.poll()
        assert len(events) == 1
        assert events[0]["event_type"] == "file.created"
        assert events[0]["source_kind"] == "filesystem"
        assert events[0]["payload_data"]["filename"] == "test.txt"


def test_filesystem_watcher_health() -> None:
    watcher = FilesystemWatcher(["/tmp"])
    health = watcher.health()
    assert health["status"] == "stopped"
    watcher.start()
    health = watcher.health()
    assert health["status"] == "running"


def test_git_adapter_health() -> None:
    adapter = GitPollingAdapter([], poll_interval=0)
    health = adapter.health()
    assert health["status"] == "stopped"
    assert health["repos"] == []
    adapter.start()
    assert adapter.health()["status"] == "running"


def test_git_adapter_no_repos() -> None:
    adapter = GitPollingAdapter([], poll_interval=0)
    adapter.start()
    events = adapter.poll()
    assert events == []
