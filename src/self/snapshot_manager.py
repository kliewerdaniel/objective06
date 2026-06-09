"""Snapshot Manager — cross-store point-in-time snapshots."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

SNAPSHOT_VERSION = "0.1.0"


class SnapshotManager:
    def __init__(self, storage: Any, audit_log: Any, snapshot_dir: str) -> None:
        self._storage = storage
        self._audit_log = audit_log
        self._snapshot_dir = Path(snapshot_dir)
        self._snapshot_dir.mkdir(parents=True, exist_ok=True)

    def create_snapshot(
        self,
        name: str = "",
        description: str = "",
        snapshot_type: str = "full",
    ) -> dict[str, Any]:
        now = datetime.now(UTC)
        sid = f"ms_{uuid4().hex}"

        events = self._storage.query("observation_event", {"limit": 1000000})
        knowledge = self._storage.query("knowledge_object", {"limit": 1000000})
        audit_entries = self._storage.query("audit_log_entry", {"limit": 1000000})

        bundle = {
            "events": events,
            "knowledge": knowledge,
            "audit": audit_entries,
        }
        bundle_bytes = json.dumps(bundle, default=str, sort_keys=True).encode()
        content_hash = f"sha256:{hashlib.sha256(bundle_bytes).hexdigest()}"

        snapshot_id = time.strftime("%Y%m%d_%H%M%S") + f"_{sid[:12]}"
        snapshot_path = self._snapshot_dir / snapshot_id
        snapshot_path.mkdir(parents=True, exist_ok=True)

        manifest = {
            "schema_version": SNAPSHOT_VERSION,
            "id": sid,
            "type": "memory_snapshot",
            "name": name or f"snapshot_{snapshot_id}",
            "description": description,
            "snapshot_type": snapshot_type,
            "created_at": now.isoformat(),
            "system_version": "0.1.0",
            "storage_substrate_versions": {
                "event_store": "0.1.0",
                "knowledge_store": "0.1.0",
                "audit_log": "0.1.0",
            },
            "event_count": len(events),
            "knowledge_object_count": len(knowledge),
            "audit_log_entry_count": len(audit_entries),
            "total_size_bytes": len(bundle_bytes),
            "content_address": content_hash,
            "parent_snapshot_id": None,
            "included_paths": ["events/", "knowledge/", "audit/"],
            "compression": {
                "algorithm": "none",
                "level": 0,
                "compressed_size_bytes": len(bundle_bytes),
            },
            "encryption": {"algorithm": "none", "key_reference": "none"},
            "integrity_hash": content_hash,
            "integrity_verified": True,
            "provenance": {
                "producer": "memory.snapshot_manager",
                "producer_version": "0.1.0",
                "produced_at": now.isoformat(),
                "parent_ids": [],
                "trigger": "manual",
                "notes": description,
            },
        }

        with open(snapshot_path / "manifest.json", "w") as f:
            json.dump(manifest, f, indent=2, default=str)
        with open(snapshot_path / "bundle.json", "wb") as f:
            f.write(bundle_bytes)

        self._audit_log.append(
            actor="memory",
            action="create",
            entity_type="memory_snapshot",
            entity_id=sid,
            reason=f"Snapshot created: {manifest['name']}",
        )
        return manifest

    def list_snapshots(self) -> list[dict[str, Any]]:
        snapshots: list[dict[str, Any]] = []
        if not self._snapshot_dir.exists():
            return snapshots
        for entry in sorted(self._snapshot_dir.iterdir()):
            if entry.is_dir():
                manifest_path = entry / "manifest.json"
                if manifest_path.exists():
                    with open(manifest_path) as f:
                        snapshots.append(json.load(f))
        return snapshots

    def restore_snapshot(self, snapshot_id: str) -> int:
        for entry in self._snapshot_dir.iterdir():
            if not entry.is_dir():
                continue
            manifest_path = entry / "manifest.json"
            if not manifest_path.exists():
                continue
            with open(manifest_path) as f:
                manifest = json.load(f)
            if manifest["id"] == snapshot_id or entry.name.endswith(snapshot_id):
                bundle_path = entry / "bundle.json"
                if not bundle_path.exists():
                    msg = f"Bundle not found for snapshot {snapshot_id}"
                    raise FileNotFoundError(msg)
                with open(bundle_path) as f:
                    bundle = json.load(f)
                restored = 0
                for event in bundle.get("events", []):
                    try:
                        self._storage.insert("observation_event", event)
                        restored += 1
                    except Exception:
                        pass
                for ko in bundle.get("knowledge", []):
                    try:
                        self._storage.insert("knowledge_object", ko)
                        restored += 1
                    except Exception:
                        pass
                self._audit_log.append(
                    actor="memory",
                    action="restore",
                    entity_type="memory_snapshot",
                    entity_id=snapshot_id,
                    reason=f"Restored {restored} records from snapshot",
                )
                return restored
        msg = f"Snapshot not found: {snapshot_id}"
        raise FileNotFoundError(msg)
