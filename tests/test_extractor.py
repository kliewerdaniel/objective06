"""Tests for Extractor."""

from __future__ import annotations

from self.extractor import Extractor
from self.knowledge_writer import KnowledgeWriter
from self.model_client import ModelClient


class FakeModelClient(ModelClient):
    def __init__(self, responses: list | None = None) -> None:
        super().__init__(base_url="http://fake:11434", model="fake-model")
        self._responses = responses or []
        self._call_count = 0

    def generate(self, prompt: str, system: str | None = None) -> dict:
        if self._call_count < len(self._responses):
            resp = self._responses[self._call_count]
            self._call_count += 1
            return resp
        return {
            "text": '[{"content": "default extraction", "confidence": 0.5}]',
            "model": "fake-model",
            "tokens": 10,
            "total_duration_ms": 100,
        }


class FakeStorage:
    def __init__(self) -> None:
        self.records: list[dict] = []

    def insert(self, record_type: str, record: dict) -> str:
        self.records.append(record)
        return str(record["id"])


class FakeAuditLog:
    def append(self, **kwargs: str) -> None:
        pass


def _event(eid: str, kind: str = "filesystem", summary: str = "test event") -> dict:
    return {
        "id": eid,
        "event_type": "file.modified",
        "source": {"kind": kind, "identifier": "/tmp"},
        "monotonic_ts": 1000,
        "payload": {"summary": summary, "data": {"path": "/tmp/test.txt"}},
        "timestamp": "2026-06-08T12:00:00Z",
        "observed_at": "2026-06-08T12:00:00Z",
        "actor": {"kind": "user", "identifier": "user"},
        "provenance": {
            "producer": "test",
            "producer_version": "0.1.0",
            "produced_at": "2026-06-08T12:00:00Z",
        },
    }


def test_process_events() -> None:
    model = FakeModelClient()
    writer = KnowledgeWriter(FakeStorage(), FakeAuditLog())
    extractor = Extractor(model, writer)
    events = [_event("evt_001"), _event("evt_002")]
    ids = extractor.process_events(events, prompt_ids=["extract_belief"])
    assert len(ids) == 1
    assert ids[0].startswith("ko_")


def test_process_empty_events() -> None:
    model = FakeModelClient()
    writer = KnowledgeWriter(FakeStorage(), FakeAuditLog())
    extractor = Extractor(model, writer)
    ids = extractor.process_events([])
    assert ids == []
