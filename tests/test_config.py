"""Tests for configuration."""

from __future__ import annotations

from self.config import Config


def test_default_config() -> None:
    config = Config()
    assert config.loop_interval_ms == 100
    assert config.embedding_model == "nomic-embed-text"
    assert config.duckdb_path is not None
    assert config.log_level == "INFO"
    assert config.model_lineage_id is None
