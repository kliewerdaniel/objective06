"""Tests for onboarding flow."""

from __future__ import annotations

import tempfile
from pathlib import Path

from self.onboarding import OnboardingFlow
from self.storage import DuckDBAdapter


def test_collect_self_description() -> None:
    tmp = tempfile.mktemp(suffix=".duckdb")
    storage = DuckDBAdapter(tmp)
    try:
        flow = OnboardingFlow(storage=storage)
        result = flow.collect_self_description(
            role="developer",
            interests=["AI", "systems"],
            projects=["SELF"],
            free_form="Building cognitive infrastructure.",
        )
        assert result["event_type"] == "system.onboarding"
        assert result["source"]["kind"] == "system"
        assert result["provenance"]["producer"] == "onboarding_flow"
    finally:
        storage.close()
        Path(tmp).unlink(missing_ok=True)


def test_needs_onboarding() -> None:
    tmp = tempfile.mktemp(suffix=".duckdb")
    storage = DuckDBAdapter(tmp)
    try:
        assert OnboardingFlow.needs_onboarding(storage) is True
        flow = OnboardingFlow(storage=storage)
        flow.collect_self_description("dev", ["AI"], ["SELF"], "test")
        assert OnboardingFlow.needs_onboarding(storage) is False
    finally:
        storage.close()
        Path(tmp).unlink(missing_ok=True)
