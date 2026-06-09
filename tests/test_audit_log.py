"""Tests for audit log with hash-chain integrity."""

from __future__ import annotations

import tempfile
from pathlib import Path

from self.audit_log import AuditLog
from self.storage import DuckDBAdapter


def _make_env() -> tuple[DuckDBAdapter, AuditLog, str, str]:
    tmp_db = tempfile.mktemp(suffix=".duckdb")
    tmp_head = tempfile.mktemp(suffix=".sha256")
    storage = DuckDBAdapter(tmp_db)
    audit = AuditLog(storage=storage, audit_head_path=tmp_head)
    return storage, audit, tmp_db, tmp_head


def test_append_entry() -> None:
    storage, audit, db_path, head_path = _make_env()
    try:
        audit.append("system", "create", "test", "obj_001", reason="test")
        assert audit.entry_count == 1
        entries = audit.query(actor="system", limit=10)
        assert len(entries) == 1
        assert entries[0]["action"] == "create"
    finally:
        storage.close()
        Path(db_path).unlink(missing_ok=True)
        Path(head_path).unlink(missing_ok=True)


def test_hash_chain_integrity() -> None:
    storage, audit, db_path, head_path = _make_env()
    try:
        audit.append("system", "start", "system", "self")
        audit.append("observer", "create", "observation_event", "evt_001")
        audit.append("extractor", "create", "knowledge_object", "ko_001")

        result = audit.check_integrity()
        assert result["chain_intact"] is True
        assert result["errors"] == 0
        assert result["head_hash"] is not None
    finally:
        storage.close()
        Path(db_path).unlink(missing_ok=True)
        Path(head_path).unlink(missing_ok=True)


def test_query_by_filters() -> None:
    storage, audit, db_path, head_path = _make_env()
    try:
        audit.append("system", "start", "system", "self")
        audit.append("observer", "create", "event", "evt_001")
        audit.append("observer", "update", "event", "evt_001")

        results = audit.query(actor="observer", limit=10)
        assert len(results) == 2

        results = audit.query(action="start", limit=10)
        assert len(results) == 1

        results = audit.query(entity_id="evt_001", limit=10)
        assert len(results) == 2
    finally:
        storage.close()
        Path(db_path).unlink(missing_ok=True)
        Path(head_path).unlink(missing_ok=True)


def test_multiple_entries_chain() -> None:
    storage, audit, db_path, head_path = _make_env()
    try:
        count = 10
        for i in range(count):
            audit.append("system", "test", "test_type", f"obj_{i}")
        assert audit.entry_count == count
        result = audit.check_integrity()
        assert result["chain_intact"] is True
    finally:
        storage.close()
        Path(db_path).unlink(missing_ok=True)
        Path(head_path).unlink(missing_ok=True)
