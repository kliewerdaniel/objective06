"""Tests for Prompt Library."""

from __future__ import annotations

from self.prompt_library import format_prompt, get_prompt, list_prompts


def test_list_prompts() -> None:
    prompts = list_prompts()
    assert "extract_belief" in prompts
    assert "detect_goal" in prompts
    assert "discover_project" in prompts


def test_get_prompt() -> None:
    prompt = get_prompt("extract_belief")
    assert prompt["id"] == "extract_belief"
    assert prompt["version"] == "0.1.0"
    assert "system" in prompt
    assert "template" in prompt
    assert "output_schema" in prompt


def test_unknown_prompt() -> None:
    import pytest

    with pytest.raises(KeyError):
        get_prompt("nonexistent")


def test_format_prompt() -> None:
    system, user = format_prompt("extract_belief", "event1: foo\n event2: bar")
    assert "belief" in system.lower()
    assert "event1" in user
    assert "event2" in user
