"""Tests for the Normalizer."""

from __future__ import annotations

from self.normalizer import Normalizer, compute_content_hash


def test_normalize_basic() -> None:
    norm = Normalizer(producer="test")
    event = norm.normalize(
        event_type="file.created",
        source_kind="filesystem",
        source_identifier="/tmp/test",
        adapter="filesystem_watcher",
        actor_kind="system",
        actor_identifier="observer.test",
        payload_summary="created: test.txt",
        payload_data={"path": "/tmp/test/test.txt", "filename": "test.txt"},
    )
    assert event["schema_version"] == "0.1.0"
    assert event["event_type"] == "file.created"
    assert event["source"]["kind"] == "filesystem"
    assert event["source"]["identifier"] == "/tmp/test"
    assert event["actor"]["kind"] == "system"
    assert event["payload"]["summary"] == "created: test.txt"
    assert event["content_hash"].startswith("sha256:")
    assert event["id"].startswith("evt_")
    assert event["provenance"]["producer"] == "observer.filesystem_watcher"
    assert event["provenance"]["confidence"] == 1.0


def test_normalize_with_subject() -> None:
    norm = Normalizer()
    event = norm.normalize(
        event_type="git.commit",
        source_kind="git",
        source_identifier="/repo",
        adapter="git_poller",
        actor_kind="user",
        actor_identifier="author",
        payload_summary="commit: fix bug",
        payload_data={"hash": "abc123", "message": "fix bug"},
        subject_kind="commit",
        subject_identifier="abc123",
        subject_attributes={"branch": "main"},
    )
    assert event["subject"]["kind"] == "commit"
    assert event["subject"]["identifier"] == "abc123"
    assert event["subject"]["attributes"]["branch"] == "main"


def test_compute_content_hash() -> None:
    h1 = compute_content_hash({"a": 1, "b": 2})
    h2 = compute_content_hash({"b": 2, "a": 1})
    assert h1 == h2
    assert h1.startswith("sha256:")


def test_generate_event_id() -> None:
    from self.normalizer import generate_event_id

    ids = {generate_event_id() for _ in range(100)}
    assert len(ids) == 100
    for eid in ids:
        assert eid.startswith("evt_")
