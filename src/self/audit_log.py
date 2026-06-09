"""Audit log with SHA-256 hash-chain integrity."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class AuditLog:
    def __init__(self, storage: Any, audit_head_path: str) -> None:
        self._storage = storage
        self._audit_head_path = audit_head_path
        Path(audit_head_path).parent.mkdir(parents=True, exist_ok=True)
        self._last_hash = self._load_head()

    def _load_head(self) -> str | None:
        path = Path(self._audit_head_path)
        if path.exists():
            return path.read_text().strip()
        return None

    def _save_head(self, hash_value: str) -> None:
        path = Path(self._audit_head_path)
        tmp = path.with_suffix(".tmp")
        tmp.write_text(hash_value)
        tmp.rename(path)

    def _compute_hash(self, entry: dict[str, Any]) -> str:
        canonical = json.dumps(entry, sort_keys=True, default=str)
        return hashlib.sha256(canonical.encode()).hexdigest()

    def append(
        self,
        actor: str,
        action: str,
        entity_type: str,
        entity_id: str,
        *,
        before_hash: str | None = None,
        after_hash: str | None = None,
        reason: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        entry = {
            "schema_version": "0.1.0",
            "id": f"aud_{uuid4().hex}",
            "timestamp": datetime.now(UTC).isoformat(),
            "actor": actor,
            "action": action,
            "entity_type": entity_type,
            "entity_id": entity_id,
            "before_hash": before_hash,
            "after_hash": after_hash,
            "reason": reason,
            "prev_hash": self._last_hash,
            "metadata": metadata or {},
        }
        entry_hash = self._compute_hash(entry)
        self._storage.insert("audit_log_entry", entry)
        self._save_head(entry_hash)
        self._last_hash = entry_hash
        return entry

    def verify_chain(self) -> list[dict[str, Any]]:
        entries = self._storage.query("audit_log_entry", {"limit": 1000000})
        errors: list[dict[str, Any]] = []
        entries.sort(key=lambda e: e["timestamp"])
        prev: str | None = None
        for entry in entries:
            expected_prev = entry.get("prev_hash")
            if expected_prev != prev:
                errors.append(
                    {
                        "id": entry["id"],
                        "error": "hash_chain_broken",
                        "expected_prev": str(expected_prev),
                        "actual_prev": str(prev),
                    }
                )
            entry_hash = self._compute_hash(entry)
            prev = entry_hash
        return errors

    def query(
        self,
        *,
        actor: str | None = None,
        action: str | None = None,
        entity_type: str | None = None,
        entity_id: str | None = None,
        time_start: str | None = None,
        time_end: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        spec: dict[str, Any] = {"limit": limit}
        if actor:
            spec["actor"] = actor
        if action:
            spec["action"] = action
        if entity_type:
            spec["entity_type"] = entity_type
        if entity_id:
            spec["entity_id"] = entity_id
        if time_start:
            spec["time_start"] = time_start
        if time_end:
            spec["time_end"] = time_end
        return self._storage.query("audit_log_entry", spec)

    def check_integrity(self) -> dict[str, Any]:
        errors = self.verify_chain()
        head = self._load_head()
        return {
            "chain_intact": len(errors) == 0,
            "errors": len(errors),
            "head_hash": head,
            "details": errors[:10],
        }

    @property
    def entry_count(self) -> int:
        return self._storage.count("audit_log_entry")
