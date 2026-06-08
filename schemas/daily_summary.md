# Daily Summary Schema

A **daily summary** is a synthesis artifact produced by the Synthesis Engine that provides a high-level overview of the user's activity and progress over the last 24 hours.

## Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | UUID | Unique identifier for the daily summary. |
| `date` | Date | The date the summary covers. |
| `summary_text` | String | The human-readable summary of the day. |
| `highlights` | Array(Object) | A list of key achievements or significant events. |
| `knowledge_updates` | Array(UUID) | IDs of new or significantly updated knowledge objects from today. |
| `pending_tasks` | Array(UUID) | IDs of unfinished tasks or projects. |
| `persona_reflection` | String | A brief reflection on how the user's persona evolved today. |
| `provenance` | Object | Reference to the knowledge objects and observations from today. |
| `timestamp` | Timestamp | When the summary was produced. |

## Example
```json
{
  "id": "...",
  "date": "2023-10-27",
  "summary_text": "Today was focused on quantum computing research. You read three papers and started a new project in your notebook.",
  "highlights": [
    { "type": "project_start", "content": "Quantum Computing Research Project" },
    { "type": "learning", "content": "Understand Shor's algorithm" }
  ],
  "knowledge_updates": ["...", "..."],
  "pending_tasks": ["..."],
  "persona_reflection": "The user showed high engagement with theoretical physics content.",
  "provenance": {
    "source_knowledge_objects": ["...", "..."]
  },
  "timestamp": "..."
}
```
