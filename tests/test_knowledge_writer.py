"""Tests for Knowledge Writer."""

from __future__ import annotations

from self.knowledge_writer import KnowledgeWriter


class MockStorage:
    def __init__(self) -> None:
        self.records: list[dict] = []

    def insert(self, record_type: str, record: dict) -> str:
        self.records.append(record)
        return str(record["id"])


class MockAuditLog:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def append(self, **kwargs: str) -> None:
        self.entries.append(kwargs)


def test_write_belief() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    writer = KnowledgeWriter(storage, audit)
    ko_id = writer.write(
        type="belief",
        name="user likes python",
        content="User expressed interest in Python programming",
        confidence=0.9,
        source_event_ids=["evt_001"],
        prompt_id="extract_belief",
        model_id="test-model",
    )
    assert ko_id.startswith("ko_")
    assert len(storage.records) == 1
    record = storage.records[0]
    assert record["type"] == "belief"
    assert record["name"] == "user likes python"
    assert record["confidence"] == 0.9
    assert len(audit.entries) == 1


def test_write_confidence_clamped() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    writer = KnowledgeWriter(storage, audit)
    writer.write(type="goal", name="test", confidence=2.0)
    assert storage.records[0]["confidence"] == 1.0
    storage.records.clear()
    writer.write(type="goal", name="test", confidence=-0.5)
    assert storage.records[0]["confidence"] == 0.0
