"""Tests for Memory API."""

from __future__ import annotations

from self.memory import MemoryAPI


class MockStorage:
    def __init__(self) -> None:
        self._records: dict[str, list[dict]] = {
            "observation_event": [],
            "knowledge_object": [],
            "summary": [],
        }

    def insert(self, rt: str, r: dict) -> str:
        self._records.setdefault(rt, []).append(r)
        return str(r["id"])

    def get(self, rt: str, rid: str) -> dict | None:
        for r in self._records.get(rt, []):
            if r["id"] == rid:
                return r
        return None

    def query(self, rt: str, spec: dict | None = None) -> list[dict]:
        return list(self._records.get(rt, []))

    def count(self, rt: str) -> int:
        return len(self._records.get(rt, []))


class MockAuditLog:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def append(self, **kw: dict) -> None:
        self.entries.append(kw)


def test_store_and_get_event() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    mem = MemoryAPI(storage, audit)
    eid = mem.store_event({"id": "evt_001", "event_type": "test"})
    assert eid == "evt_001"
    retrieved = mem.get_event("evt_001")
    assert retrieved is not None
    assert retrieved["event_type"] == "test"


def test_store_knowledge() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    mem = MemoryAPI(storage, audit)
    kid = mem.store_knowledge({"id": "ko_001", "name": "test", "type": "belief"})
    assert kid == "ko_001"
    assert mem.knowledge_count == 1


def test_query_events() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    mem = MemoryAPI(storage, audit)
    mem.store_event({"id": "evt_001", "event_type": "a"})
    mem.store_event({"id": "evt_002", "event_type": "b"})
    results = mem.query_events()
    assert len(results) == 2


def test_counts() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    mem = MemoryAPI(storage, audit)
    mem.store_event({"id": "e1", "event_type": "t"})
    mem.store_knowledge({"id": "k1", "name": "n", "type": "t"})
    assert mem.event_count == 1
    assert mem.knowledge_count == 1
