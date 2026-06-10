from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any


class DecayEngine:
    def __init__(self, persona_engine: Any) -> None:
        self._persona_engine = persona_engine
        self._log = logging.getLogger("self.persona_engine.decay_engine")

    def run(self) -> None:
        self._log.info("Running nightly decay engine")
        snapshots = self._persona_engine.vector_store.history()
        for snapshot in snapshots:
            ts_str = snapshot.get("timestamp", "")
            if not ts_str:
                continue
            try:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00")).timestamp()
                age = datetime.now(UTC).timestamp() - ts
                if age > 86400:
                    old_vec = snapshot.get("vector", [])
                    if old_vec:
                        decay_factor = max(0.0, 1.0 - (age / 3600 * 0.0001))
                        new_vec = [v * decay_factor for v in old_vec]
                        self._persona_engine.updater.save_snapshot(
                            new_vec,
                            self._persona_engine.embedder.model_id,
                            reason=f"Decayed snapshot {snapshot.get('id')}",
                        )
            except Exception as e:
                self._log.error("Failed to decay snapshot %s: %s", snapshot.get("id"), e)
