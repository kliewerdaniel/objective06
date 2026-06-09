"""Shared fixtures for tests."""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest

from self.storage import DuckDBAdapter


@pytest.fixture
def storage() -> Generator[Any, None, None]:
    tmp = tempfile.mktemp(suffix=".duckdb")
    adapter = DuckDBAdapter(tmp)
    try:
        yield adapter
    finally:
        adapter.close()
        Path(tmp).unlink(missing_ok=True)
