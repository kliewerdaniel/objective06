"""Versioned prompt templates for knowledge extraction."""

from __future__ import annotations

from typing import Any

PROMPTS: dict[str, dict[str, Any]] = {
    "extract_belief": {
        "id": "extract_belief",
        "version": "0.1.0",
        "description": "Extract beliefs from observation events",
        "system": (
            "You are a belief extraction system. Extract subjective opinions, convictions, "
            "or stated facts about the world or the user's life from the given observations. "
            "Output a JSON array of objects, each with: content (string), confidence (0.0-1.0). "
            "Be conservative: only extract what is clearly supported by the evidence."
        ),
        "template": (
            "Extract beliefs from the following observations:\n\n"
            "{events}\n\n"
            "Return a JSON array of belief objects."
        ),
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["content", "confidence"],
                "properties": {
                    "content": {"type": "string"},
                    "confidence": {"type": "number"},
                },
            },
        },
    },
    "detect_goal": {
        "id": "detect_goal",
        "version": "0.1.0",
        "description": "Detect goals from observation events",
        "system": (
            "You are a goal detection system. Identify desired outcomes, objectives, "
            "or planned activities from the given observations. "
            "Output a JSON array of objects, each with: content (string), confidence (0.0-1.0), "
            "timeframe (string, one of: 'immediate', 'short_term', 'long_term'). "
            "Only extract goals that are clearly indicated by the evidence."
        ),
        "template": (
            "Detect goals from the following observations:\n\n"
            "{events}\n\n"
            "Return a JSON array of goal objects."
        ),
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["content", "confidence", "timeframe"],
                "properties": {
                    "content": {"type": "string"},
                    "confidence": {"type": "number"},
                    "timeframe": {"type": "string"},
                },
            },
        },
    },
    "discover_project": {
        "id": "discover_project",
        "version": "0.1.0",
        "description": "Discover projects from observation events",
        "system": (
            "You are a project discovery system. Identify structured sets of tasks, "
            "resources, or efforts that constitute a project from the given observations. "
            "Output a JSON array of objects, each with: name (string), description (string), "
            "confidence (0.0-1.0). "
            "Only extract projects that are clearly indicated by the evidence."
        ),
        "template": (
            "Discover projects from the following observations:\n\n"
            "{events}\n\n"
            "Return a JSON array of project objects."
        ),
        "output_schema": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["name", "description", "confidence"],
                "properties": {
                    "name": {"type": "string"},
                    "description": {"type": "string"},
                    "confidence": {"type": "number"},
                },
            },
        },
    },
}


def get_prompt(prompt_id: str) -> dict[str, Any]:
    if prompt_id not in PROMPTS:
        raise KeyError(f"Unknown prompt: {prompt_id}")
    return dict(PROMPTS[prompt_id])


def list_prompts() -> list[str]:
    return list(PROMPTS.keys())


def format_prompt(prompt_id: str, events: str) -> tuple[str, str]:
    prompt_def = get_prompt(prompt_id)
    system = prompt_def["system"]
    user = prompt_def["template"].format(events=events)
    return system, user
