"""Tests for Exporter/Importer."""

from __future__ import annotations

import tempfile
from pathlib import Path

from self.exporter import Exporter


class MockStorage:
    def __init__(self) -> None:
        self._records: dict[str, list[dict]] = {
            "observation_event": [],
            "knowledge_object": [],
            "audit_log_entry": [],
        }

    def insert(self, rt: str, r: dict) -> str:
        self._records.setdefault(rt, []).append(r)
        return str(r["id"])

    def query(self, rt: str, spec: dict | None = None) -> list[dict]:
        return list(self._records.get(rt, []))


class MockAuditLog:
    def append(self, **kw: dict) -> None:
        pass


def test_export_empty() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MockStorage()
        audit = MockAuditLog()
        exporter = Exporter(storage, audit)
        out_path = exporter.export_all(str(Path(tmpdir) / "export.json"))
        assert Path(out_path).exists()
        assert Path(out_path).with_suffix(".json.sha256").exists()


def test_export_with_data() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        storage = MockStorage()
        storage.insert("observation_event", {"id": "evt_001", "event_type": "test"})
        audit = MockAuditLog()
        exporter = Exporter(storage, audit)
        out_path = exporter.export_all(str(Path(tmpdir) / "export.json"))
        assert Path(out_path).exists()


def test_import_roundtrip() -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        src_storage = MockStorage()
        src_storage.insert("observation_event", {"id": "evt_001", "event_type": "test"})
        src_storage.insert("knowledge_object", {"id": "ko_001", "type": "belief", "name": "n"})
        audit = MockAuditLog()
        exporter = Exporter(src_storage, audit)
        out_path = exporter.export_all(str(Path(tmpdir) / "export.json"))

        dst_storage = MockStorage()
        importer = Exporter(dst_storage, audit)
        counts = importer.import_archive(out_path, dry_run=False)
        assert counts["events"] == 1
        assert counts["knowledge"] == 1
