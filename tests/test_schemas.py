"""Tests for core schema definitions."""

from __future__ import annotations

from self.schemas import (
    Actor,
    AuditLogEntry,
    KnowledgeObject,
    ObservationEvent,
    Payload,
    Provenance,
    Source,
)


def test_observation_event_defaults() -> None:
    src = Source(
        kind="filesystem",
        identifier="/tmp/test",
        adapter="fs_watcher",
        adapter_version="0.1.0",
    )
    event = ObservationEvent(
        event_type="file.modified",
        source=src,
        actor=Actor(kind="user", identifier="user_001"),
        payload=Payload(summary="File modified", data={"path": "/tmp/test"}),
        provenance=Provenance(producer="observer.fs_watcher", producer_version="0.1.0"),
    )
    assert event.schema_version == "0.1.0"
    assert event.id.startswith("evt_")
    assert event.event_type == "file.modified"
    assert event.content_hash.startswith("sha256:")
    assert event.provenance.producer == "observer.fs_watcher"


def test_knowledge_object_validation() -> None:
    ko = KnowledgeObject(
        type="belief",
        name="test belief",
        provenance=Provenance(producer="extractor", producer_version="0.1.0"),
    )
    assert ko.id.startswith("ko_")
    assert ko.confidence == 0.5
    assert ko.deprecated is False


def test_audit_log_entry() -> None:
    entry = AuditLogEntry(
        actor="system",
        action="create",
        entity_type="observation_event",
        entity_id="evt_test",
        prev_hash=None,
    )
    assert entry.id.startswith("aud_")
    assert entry.actor == "system"
    canonical = entry.to_canonical_json()
    assert '"actor": "system"' in canonical
    assert "prev_hash" not in canonical
