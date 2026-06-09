"""Filesystem Watcher adapter — polls directories for file changes."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any

from self.source_adapters.base import BaseSourceAdapter


class FilesystemWatcher(BaseSourceAdapter):
    def __init__(self, paths: list[str], poll_interval: float = 5.0) -> None:
        self._paths = [Path(p).resolve() for p in paths]
        self._poll_interval = poll_interval
        self._snapshots: dict[str, dict[str, float]] = {}
        self._running = False
        self._last_poll = 0.0

    @property
    def name(self) -> str:
        return "filesystem"

    def start(self) -> None:
        self._running = True
        for p in self._paths:
            self._snapshots[str(p)] = self._scan(p)

    def stop(self) -> None:
        self._running = False

    def poll(self) -> list[dict[str, Any]]:
        now = time.time()
        if now - self._last_poll < self._poll_interval:
            return []
        self._last_poll = now
        events: list[dict[str, Any]] = []
        for p in self._paths:
            key = str(p)
            old = self._snapshots.get(key, {})
            current = self._scan(p)
            events.extend(self._diff(key, old, current))
            self._snapshots[key] = current
        return events

    def health(self) -> dict[str, Any]:
        return {
            "status": "running" if self._running else "stopped",
            "paths": [str(p) for p in self._paths],
            "last_poll": self._last_poll,
        }

    def _scan(self, path: Path) -> dict[str, float]:
        result: dict[str, float] = {}
        if not path.exists():
            return result
        for root, _dirs, files in os.walk(str(path)):
            for fname in files:
                fpath = Path(root) / fname
                try:
                    stat = fpath.stat()
                    result[str(fpath)] = stat.st_mtime
                except OSError:
                    pass
        return result

    def _diff(
        self,
        base_path: str,
        old: dict[str, float],
        current: dict[str, float],
    ) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        old_set = set(old.keys())
        cur_set = set(current.keys())

        for fpath in cur_set - old_set:
            events.append(self._make_event("file.created", fpath, base_path))

        for fpath in old_set - cur_set:
            events.append(self._make_event("file.deleted", fpath, base_path))

        for fpath in old_set & cur_set:
            if old[fpath] != current[fpath]:
                events.append(self._make_event("file.modified", fpath, base_path))

        return events

    def _make_event(self, event_type: str, fpath: str, base_path: str) -> dict[str, Any]:
        fname = Path(fpath).name
        return {
            "event_type": event_type,
            "source_kind": "filesystem",
            "source_identifier": base_path,
            "adapter": "filesystem_watcher",
            "actor_kind": "system",
            "actor_identifier": "observer.filesystem",
            "payload_summary": f"{event_type.split('.')[1]}: {fname}",
            "payload_data": {
                "path": fpath,
                "filename": fname,
                "size_bytes": Path(fpath).stat().st_size if Path(fpath).exists() else 0,
            },
            "subject_kind": "file",
            "subject_identifier": fpath,
            "tags": ["filesystem"],
        }
