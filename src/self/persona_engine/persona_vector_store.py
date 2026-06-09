"""Persona Vector Store — time-series storage of persona vectors."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


class PersonaVectorStore:
    def __init__(self, storage: Any, vector_dir: str) -> None:
        self._storage = storage
        self._vector_dir = Path(vector_dir)
        self._vector_dir.mkdir(parents=True, exist_ok=True)

    def save_snapshot(
        self,
        vector: list[float],
        model_id: str,
        reason: str = "",
    ) -> str:
        now = datetime.now(UTC)
        sid = f"ps_{uuid4().hex}"
        record = {
            "schema_version": "0.1.0",
            "id": sid,
            "model_id": model_id,
            "vector": vector,
            "timestamp": now.isoformat(),
            "reason": reason,
        }
        vec_path = self._vector_dir / f"{sid}.json"
        with open(vec_path, "w") as f:
            json.dump({"vector": vector, "model_id": model_id, "timestamp": now.isoformat()}, f)
        self._storage.insert("persona_snapshot", record)
        return sid

    def current(self) -> dict[str, Any] | None:
        results = self._storage.query("persona_snapshot", {"limit": 1, "order_by": "timestamp"})
        return results[0] if results else None

    def history(self, limit: int = 100) -> list[dict[str, Any]]:
        return self._storage.query("persona_snapshot", {"limit": limit, "order_by": "timestamp"})

    def at_time(self, target: str) -> dict[str, Any] | None:
        results = self._storage.query("persona_snapshot", {"limit": 100, "order_by": "timestamp"})
        for r in results:
            if r.get("timestamp", "") <= target:
                return r
        return None

    def trajectory(self) -> list[dict[str, Any]]:
        return self._storage.query("persona_snapshot", {"limit": 1000, "order_by": "timestamp"})
