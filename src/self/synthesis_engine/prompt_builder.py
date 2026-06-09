"""Prompt Builder — versioned synthesis prompt templates."""

from __future__ import annotations

from typing import Any

SYNTHESIS_TEMPLATES: dict[str, str] = {
    "daily": (
        "You are a personal AI assistant writing a daily summary. "
        "Summarize the user's day based ONLY on the provided events, knowledge, and entities. "
        "Include: top activities, key entities encountered, knowledge gained, any notable changes. "
        "Be concise (3-5 paragraphs). Mark uncertainty explicitly.\n\n"
        "Events:\n{events}\n\n"
        "Knowledge:\n{knowledge}\n\n"
        "Entities:\n{nodes}\n\n"
        "Daily Summary:"
    ),
    "weekly": (
        "You are a personal AI assistant writing a weekly summary. "
        "Summarize the user's week based ONLY on the provided context. "
        "Include: theme, projects advanced, topics explored, belief or goal changes. "
        "Be concise (4-6 paragraphs). Mark uncertainty explicitly.\n\n"
        "Events:\n{events}\n\n"
        "Knowledge:\n{knowledge}\n\n"
        "Entities:\n{nodes}\n\n"
        "Weekly Summary:"
    ),
    "topic": (
        "You are a personal AI assistant summarizing everything known about a topic. "
        "Based ONLY on the provided events, knowledge, and entities, describe: "
        "the definition and scope, timeline of engagement, key entities and their relationships, "
        "and the current state of the user's knowledge. "
        "Be concise (3-5 paragraphs). Mark uncertainty explicitly.\n\n"
        "Topic: {topic}\n\n"
        "Events:\n{events}\n\n"
        "Knowledge:\n{knowledge}\n\n"
        "Entities:\n{nodes}\n\n"
        "Topic Summary:"
    ),
    "project": (
        "You are a personal AI assistant summarizing a project. "
        "Based ONLY on the provided context, describe: "
        "project description and goal, timeline of activity, key collaborators, "
        "milestones and progress, and predicted next steps. "
        "Be concise (3-5 paragraphs). Mark uncertainty explicitly.\n\n"
        "Events:\n{events}\n\n"
        "Knowledge:\n{knowledge}\n\n"
        "Entities:\n{nodes}\n\n"
        "Project Summary:"
    ),
}


class PromptBuilder:
    VERSIONS: dict[str, str] = {
        "daily": "0.1.0",
        "weekly": "0.1.0",
        "topic": "0.1.0",
        "project": "0.1.0",
    }

    def build(self, summary_type: str, context: dict[str, Any], topic: str = "") -> str:
        template = SYNTHESIS_TEMPLATES.get(summary_type)
        if template is None:
            msg = f"Unknown summary type: {summary_type}"
            raise ValueError(msg)
        events_text = (
            "\n".join(
                f"- [{e.get('event_type', '')}] {e.get('timestamp', '')}: "
                f"{e.get('payload', {}).get('summary', '')}"
                for e in context.get("events", [])[:10]
            )
            or "No events in this period."
        )
        knowledge_text = (
            "\n".join(
                f"- {k.get('name', '')}: {k.get('description', '')}"
                for k in context.get("knowledge", [])[:10]
            )
            or "No knowledge objects."
        )
        nodes_text = (
            "\n".join(
                f"- {n.get('name', '')} ({n.get('type', '')})"
                for n in context.get("nodes", [])[:10]
            )
            or "No entities found."
        )
        return template.format(
            events=events_text,
            knowledge=knowledge_text,
            nodes=nodes_text,
            topic=topic,
        )

    def get_version(self, summary_type: str) -> str:
        return self.VERSIONS.get(summary_type, "0.0.0")
