"""Ground Truth Manager — stores curated examples with expected outputs."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class GroundTruthManager:
    def __init__(self, storage: Any) -> None:
        self._storage = storage

    def create(
        self,
        spec_id: str,
        inputs: dict[str, Any],
        expected_outputs: dict[str, Any],
    ) -> str:
        now = datetime.now(UTC).isoformat()
        gid = f"gt_{uuid4().hex}"
        record = {
            "schema_version": "0.1.0",
            "id": gid,
            "spec_id": spec_id,
            "inputs": inputs,
            "expected_outputs": expected_outputs,
            "version": 1,
            "created_at": now,
            "updated_at": now,
            "deprecated": False,
        }
        self._storage.insert("ground_truth", record)
        return gid

    def get(self, gt_id: str) -> dict[str, Any] | None:
        return self._storage.get("ground_truth", gt_id)

    def list_for_spec(self, spec_id: str) -> list[dict[str, Any]]:
        return self._storage.query("ground_truth", {"spec_id": spec_id})

    def list_all(self) -> list[dict[str, Any]]:
        return self._storage.query("ground_truth", {})

    def update(self, gt_id: str, expected_outputs: dict[str, Any]) -> dict[str, Any] | None:
        existing = self._storage.get("ground_truth", gt_id)
        if existing is None:
            return None
        now = datetime.now(UTC).isoformat()
        changes = {
            "expected_outputs": expected_outputs,
            "updated_at": now,
            "version": (existing.get("version", 1) or 1) + 1,
        }
        self._storage.update("ground_truth", gt_id, changes)
        return {**existing, **changes}

    def deprecate(self, gt_id: str) -> bool:
        existing = self._storage.get("ground_truth", gt_id)
        if existing is None:
            return False
        self._storage.update("ground_truth", gt_id, {"deprecated": True})
        return True

    def count(self) -> int:
        return self._storage.count("ground_truth")
