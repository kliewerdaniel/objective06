# Knowledge Object Schema

The `knowledge_object` is the primary unit of structured meaning within SELF. It represents any fact, belief, goal, project, interest, or relationship that the system has extracted from observations.

## Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | UUID | Unique identifier for the knowledge object. |
| `type` | String | The category of knowledge (e.g., "belief", "goal", "project", "interest", "relationship", "entity"). |
| `content` | String | The primary content or description of the knowledge object. |
| `confidence` | Float (0-1) | The system's confidence in this knowledge object. |
| `status` | String | The current state (e.g., "active", "superseded", "deprecated", "contradicted"). |
| `provenance` | Object | A reference to the source events, extractions, and models used to produce this object. |
| `last_updated` | Timestamp | The last time this object was updated. |
| `created_at` | Timestamp | The time this object was first created. |
| `tags` | Array(String) | Optional tags for categorization. |
| `metadata` | Object | Optional additional metadata (e.g., source-specific info). |

## Subtypes

- **Belief**: Represents a subjective opinion, conviction, or stated fact about the world or the user's life.
- **Goal**: Represents a desired outcome, objective, or planned activity.
- **Project**: Represents a structured set of tasks, resources, and deadlines aimed at achieving a goal.
- **Interest**: Represents a topic, activity, or area of focus that the user values.
- **Relationship**: Represents a connection between the user and another entity (person, organization, tool).
- **Entity**: Represents a discrete object, person, place, or concept in the user's digital environment.

## Provenance Requirements
Every `knowledge_object` MUST have a `provenance` field. This field must include:
- Source `observation_event` IDs.
- Extraction prompt identifier and version.
- Model identifier and version.
- Timestamp of extraction.
- Reasoning trace (optional but encouraged).

## Examples

### Belief
```json
{
  "id": "...",
  "type": "belief",
  "content": "I want to learn more about quantum computing.",
  "confidence": 0.95,
  "status": "active",
  "provenance": {
    "source_events": ["..."],
    "prompt_id": "ext_belief_01",
    "model_id": "llama-3-70b-local",
    "created_at": "..."
  }
}
```
