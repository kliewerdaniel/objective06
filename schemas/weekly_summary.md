# Weekly Summary Schema

A **weekly summary** is a synthesis artifact produced by the Synthesis Engine that provides a high-level overview of the user's activity, progress, and evolution over the last 7 days.

## Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | UUID | Unique identifier for the weekly summary. |
| `week_ending` | Date | The date the summary covers. |
| `summary_text` | String | The human-readable summary of the week. |
| `key_themes` | Array(String) | Major themes of focus during the week. |
| `progress_report` | Object | Summary of progress on ongoing projects and goals. |
| `persona_evolution` | String | A narrative description of how the user's identity/persona evolved this week. |
| `knowledge_growth` | Array(Object) | Summary of new knowledge domains explored. |
| `provenance` | Object | Reference to the knowledge objects and observations from the week. |
| `timestamp` | Timestamp | When the summary was produced. |

## Example
```json
{
  "id": "...",
  "week_ending": "2023-11-03",
  "summary_text": "This week was defined by a deep dive into quantum computing. You transitioned from general interest to starting a structured project.",
  "key_themes": ["Quantum Computing", "Project Planning", "Research"],
  "progress_report": {
    "project_a": "Started foundation",
    "goal_b": "20% complete"
  },
  "persona_evolution": "The user is moving from a consumer of information to a producer of research.",
  "knowledge_growth": [
    { "domain": "Quantum Physics", "score": 0.8 },
    { "domain": "Shor's Algorithm", "score": 0.9 }
  ],
  "provenance": {
    "source_knowledge_objects": ["...", "..."]
  },
  "timestamp": "..."
}
```
