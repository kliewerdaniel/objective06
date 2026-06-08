# Schema: goal

> A knowledge object representing a goal the user is pursuing or has pursued.

---

## Schema Version

`0.1.0`

## Field Definitions

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Schema version. |
| `id` | string (UUID) | yes | Stable goal ID. |
| `type` | string | yes | Always `goal`. |
| `title` | string | yes | Short title. |
| `description` | string | no | Detailed description. |
| `horizon` | string | yes | `short_term`, `medium_term`, `long_term`, `aspirational`. |
| `status` | string | yes | `active`, `paused`, `achieved`, `abandoned`, `superseded`. |
| `priority` | number | yes | User-assigned or inferred priority in [0, 1]. |
| `progress` | number | yes | Inferred progress in [0, 1]. |
| `milestones` | array of `Milestone` | no | Discrete milestones. |
| `parent_goal_id` | UUID | no | The parent goal, if hierarchical. |
| `sub_goal_ids` | array of UUID | no | Sub-goals. |
| `related_entity_ids` | array of UUID | no | Projects, people, etc., related to the goal. |
| `first_formed` | string (ISO 8601) | yes | When the goal was first inferred. |
| `target_date` | string (ISO 8601) | no | Target completion date. |
| `achieved_at` | string (ISO 8601) | no | When achieved. |
| `abandoned_at` | string (ISO 8601) | no | When abandoned. |
| `history` | array of `GoalEvent` | yes | Chronological history. |
| `provenance` | `Provenance` object | yes | Provenance metadata. |
| `embedding_ref` | UUID | no | Reference to vector embedding. |

### `Milestone` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | UUID | yes | Milestone ID. |
| `title` | string | yes | Milestone title. |
| `description` | string | no | Description. |
| `target_date` | string (ISO 8601) | no | Target date. |
| `completed_at` | string (ISO 8601) | no | When completed. |
| `status` | string | yes | `pending`, `in_progress`, `completed`, `blocked`, `cancelled`. |

### `GoalEvent` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `event` | string | yes | `formed`, `progressed`, `paused`, `resumed`, `achieved`, `abandoned`, `reinstated`, `milestone_completed`. |
| `timestamp` | string (ISO 8601) | yes | When the event occurred. |
| `source_event_ids` | array of UUID | yes | Source observation events. |
| `notes` | string | no | Free-form notes. |
| `delta` | number | no | Change in progress, if applicable. |

## JSON Example

```json
{
  "schema_version": "0.1.0",
  "id": "gl_01HZX3R8P3K4N5M6Q7R8S9T0V1",
  "type": "goal",
  "title": "Ship SELF v1.0",
  "description": "Complete the SELF cognitive infrastructure to a usable v1.0 release with local models, observation, extraction, memory, identity graph, persona, synthesis, and action.",
  "horizon": "long_term",
  "status": "active",
  "priority": 0.95,
  "progress": 0.32,
  "milestones": [
    {
      "id": "ms_01HZX0R8P3K4N5M6Q7R8S9T0V0",
      "title": "Documentation complete",
      "description": "All architecture, schemas, evaluations, examples, ADRs in place.",
      "target_date": "2026-08-01T00:00:00.000Z",
      "completed_at": null,
      "status": "in_progress"
    },
    {
      "id": "ms_01HZX0R8P3K4N5M6Q7R8S9T0V1",
      "title": "Local model integration",
      "description": "Ollama/vLLM/llama.cpp adapter complete.",
      "target_date": "2026-10-01T00:00:00.000Z",
      "completed_at": null,
      "status": "pending"
    }
  ],
  "parent_goal_id": null,
  "sub_goal_ids": ["gl_01HZX0R8P3K4N5M6Q7R8S9T0V0"],
  "related_entity_ids": ["nd_proj_self", "nd_concept_localfirst"],
  "first_formed": "2024-01-15T09:00:00.000Z",
  "target_date": "2027-06-01T00:00:00.000Z",
  "achieved_at": null,
  "abandoned_at": null,
  "history": [
    {
      "event": "formed",
      "timestamp": "2024-01-15T09:00:00.000Z",
      "source_event_ids": ["evt_01HZX0R8P3K4N5M6Q7R8S9T0V0"],
      "notes": "Initial formation from a project planning document.",
      "delta": null
    },
    {
      "event": "progressed",
      "timestamp": "2026-06-08T14:00:00.000Z",
      "source_event_ids": ["evt_01HZX3R8P3K4N5M6Q7R8S9T0V9"],
      "notes": "Documentation phase in progress.",
      "delta": 0.05
    }
  ],
  "provenance": {
    "producer": "extractor.goal_detection",
    "producer_version": "0.1.0",
    "produced_at": "2024-01-15T09:00:00.000Z",
    "parent_ids": ["evt_01HZX0R8P3K4N5M6Q7R8S9T0V0"],
    "model": "qwen2.5-7b",
    "model_version": "0.1.0",
    "prompt_template": "goal_detection",
    "prompt_version": "0.1.0",
    "confidence": 0.85,
    "notes": "Goal extracted from a project README."
  },
  "embedding_ref": "emb_01HZX3R8P3K4N5M6Q7R8S9T0V1"
}
```

## Validation Requirements

- All required fields must be present.
- `type` must equal `goal`.
- `horizon` must be one of the allowed values.
- `status` must be one of the allowed values.
- `priority` and `progress` must be in [0, 1].
- `history` must be non-empty and chronologically ordered.
- The first event must be `formed`.
- The latest event must match `status`.
- `achieved_at` must be set if and only if `status` is `achieved`.
- `abandoned_at` must be set if and only if `status` is `abandoned`.

## Versioning Strategy

Standard semantic versioning. See `schemas/observation_event.md` — Migration Runner Interface.

## Storage Considerations

Goals are stored in the knowledge store with a parallel `Identity Graph` node (type `Goal`) for graph queries.

## Privacy Considerations

Goals may be personal or sensitive. Implementations must honor per-source privacy settings and support selective deletion.
