"""Exporter/Importer — portable JSON archive of memory state."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

EXPORT_VERSION = "0.1.0"


class Exporter:
    def __init__(self, storage: Any, audit_log: Any) -> None:
        self._storage = storage
        self._audit_log = audit_log

    def export_all(self, output_path: str) -> str:
        events = self._storage.query("observation_event", {"limit": 1000000})
        knowledge = self._storage.query("knowledge_object", {"limit": 1000000})
        audit = self._storage.query("audit_log_entry", {"limit": 1000000})

        archive = {
            "schema_version": EXPORT_VERSION,
            "exported_at": datetime.now(UTC).isoformat(),
            "event_count": len(events),
            "knowledge_count": len(knowledge),
            "audit_count": len(audit),
            "events": events,
            "knowledge": knowledge,
            "audit_log": audit,
        }

        content = json.dumps(archive, default=str, sort_keys=True, indent=2)
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(content)

        integrity = hashlib.sha256(content.encode()).hexdigest()
        integrity_path = out.with_suffix(out.suffix + ".sha256")
        integrity_path.write_text(f"sha256:{integrity}  {out.name}\n")

        self._audit_log.append(
            actor="memory.exporter",
            action="create",
            entity_type="export",
            entity_id=out.name,
            reason=(
                f"Exported {len(events)} events, {len(knowledge)} knowledge, "
                f"{len(audit)} audit entries"
            ),
        )
        return str(out)

    def import_archive(self, input_path: str, dry_run: bool = False) -> dict[str, int]:
        path = Path(input_path)
        if not path.exists():
            msg = f"Archive not found: {input_path}"
            raise FileNotFoundError(msg)

        content = path.read_text()
        integrity_path = path.with_suffix(path.suffix + ".sha256")
        if integrity_path.exists():
            expected = integrity_path.read_text().strip().split()[0]
            actual = f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"
            if expected != actual:
                msg = f"Integrity mismatch: {expected} != {actual}"
                raise ValueError(msg)

        archive = json.loads(content)
        counts = {"events": 0, "knowledge": 0}

        if not dry_run:
            for event in archive.get("events", []):
                try:
                    self._storage.insert("observation_event", event)
                    counts["events"] += 1
                except Exception:
                    pass
            for ko in archive.get("knowledge", []):
                try:
                    self._storage.insert("knowledge_object", ko)
                    counts["knowledge"] += 1
                except Exception:
                    pass
            self._audit_log.append(
                actor="memory.exporter",
                action="create",
                entity_type="import",
                entity_id=path.name,
                reason=f"Imported {counts['events']} events, {counts['knowledge']} knowledge",
            )
        return counts
