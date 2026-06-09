"""Configuration management for SELF."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG_PATH = Path("~/.config/self/config.yaml").expanduser()


class Config:
    def __init__(self, config_path: Path | None = None) -> None:
        self.config_path = config_path or DEFAULT_CONFIG_PATH
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        path = Path(str(self.config_path))
        if path.exists():
            with open(path) as f:
                self._data = yaml.safe_load(f) or {}
        self._data.setdefault("storage", {})
        s = self._data.setdefault("storage", {})
        base = Path("~/.local/share/self").expanduser()
        s.setdefault("duckdb_path", str(base / "data.duckdb"))
        s.setdefault("audit_log_path", str(base / "audit_log.duckdb"))
        s.setdefault("snapshot_dir", str(base / "snapshots"))
        s.setdefault("raw_dir", str(base / "raw"))
        s.setdefault("faiss_index_path", str(base / "vectors.faiss"))
        s.setdefault("audit_head_path", str(base / "audit_head.sha256"))
        log = self._data.setdefault("logging", {})
        log.setdefault("level", "INFO")
        log.setdefault("file", str(Path("~/.local/share/self/self.log").expanduser()))
        self._data.setdefault("loop_interval_ms", 100)
        self._data.setdefault("embedding_model", "nomic-embed-text")
        self._data.setdefault("model_lineage_id", None)
        self._data.setdefault("watch_paths", [])
        self._data.setdefault("watch_repos", [])

    @property
    def duckdb_path(self) -> str:
        return str(self._data["storage"]["duckdb_path"])

    @property
    def audit_log_path(self) -> str:
        return str(self._data["storage"]["audit_log_path"])

    @property
    def snapshot_dir(self) -> str:
        return str(self._data["storage"]["snapshot_dir"])

    @property
    def raw_dir(self) -> str:
        return str(self._data["storage"]["raw_dir"])

    @property
    def faiss_index_path(self) -> str:
        return str(self._data["storage"]["faiss_index_path"])

    @property
    def audit_head_path(self) -> str:
        return str(self._data["storage"]["audit_head_path"])

    @property
    def log_level(self) -> str:
        return str(self._data["logging"]["level"])

    @property
    def log_file(self) -> str:
        return str(self._data["logging"]["file"])

    @property
    def loop_interval_ms(self) -> int:
        return int(self._data.get("loop_interval_ms", 100))

    @property
    def embedding_model(self) -> str:
        return str(self._data.get("embedding_model", "nomic-embed-text"))

    @property
    def model_lineage_id(self) -> str | None:
        return self._data.get("model_lineage_id")

    @property
    def watch_paths(self) -> list[str]:
        return list(self._data.get("watch_paths", []))

    @property
    def watch_repos(self) -> list[str]:
        return list(self._data.get("watch_repos", []))

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def ensure_dirs(self) -> None:
        for path_str in [self.snapshot_dir, self.raw_dir]:
            Path(path_str).mkdir(parents=True, exist_ok=True)
        Path(self.duckdb_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.audit_log_path).parent.mkdir(parents=True, exist_ok=True)
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)

    @classmethod
    def from_env(cls) -> Config:
        config_path = os.environ.get("SELF_CONFIG")
        return cls(Path(config_path) if config_path else None)
