"""Tests for Compaction Engine."""

from __future__ import annotations

import tempfile
from datetime import UTC, datetime, timedelta

from self.compaction import CompactionEngine


class MockStorage:
    def __init__(self) -> None:
        self._records: list[dict] = []
        self._updates: list[tuple[str, str, dict]] = []

    def query(self, rt: str, spec: dict | None = None) -> list[dict]:
        return list(self._records)

    def update(self, rt: str, rid: str, changes: dict) -> bool:
        self._updates.append((rt, rid, changes))
        return True

    def insert(self, rt: str, r: dict) -> str:
        self._records.append(r)
        return str(r["id"])


class MockAuditLog:
    def append(self, **kw: dict) -> None:
        pass


def test_score_recency_fresh() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    engine = CompactionEngine(storage, audit, "/tmp/archive", cold_threshold_days=90)
    record = {"created_at": datetime.now(UTC).isoformat(), "confidence": 0.9}
    score = engine.score(record)
    assert score > 0.8


def test_score_recency_old() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    engine = CompactionEngine(storage, audit, "/tmp/archive", cold_threshold_days=1)
    record = {
        "created_at": (datetime.now(UTC) - timedelta(days=10)).isoformat(),
        "confidence": 0.5,
    }
    score = engine.score(record)
    assert score < 0.5


def test_no_compaction_for_fresh() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MockStorage()
        audit = MockAuditLog()
        engine = CompactionEngine(
            storage,
            audit,
            tmpdir,
            cold_threshold_days=365,
            archive_threshold_days=730,
        )
        record = {
            "id": "ko_001",
            "type": "belief",
            "name": "test",
            "confidence": 0.9,
            "created_at": datetime.now(UTC).isoformat(),
            "attributes": {},
        }
        storage.insert("knowledge_object", record)
        result = engine.compact_knowledge()
        assert result["cold"] == 0
        assert result["archived"] == 0
