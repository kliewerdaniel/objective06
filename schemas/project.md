# Schema: project

> A knowledge object representing a project the user is working on or has worked on.

---

## Overview

Projects are concrete, time-bounded undertakings the user commits effort to. They are the operational counterpart to goals: a goal describes *what* the user wants; a project describes *how* and *with what artifacts* the user is getting there. Projects have a lifecycle (proposed → active → paused/completed/abandoned), a defined start, and an optional completion or abandonment. They may produce code repositories, documents, designs, and other artifacts, and they may involve collaborators.

Projects are produced by the Extractor when the user signals an intent to build, ship, or operate something concrete, and refined by the Identity Graph and Synthesis Engine. Projects are linked to goals (a project often serves one or more goals), to people (collaborators), to concepts (the technologies, domains, and ideas the project touches), and to the observation events that chronicle its progress.

A project's `history` is an append-only log of lifecycle events, written by the Extractor and the Synthesis Engine. The current `status` is always derivable from the latest event, but is stored denormalized for query efficiency.

## Schema Version

Current version: `0.1.0`

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Schema version. |
| `id` | string (UUID) | yes | Stable project ID. |
| `type` | string | yes | Always `project`. |
| `name` | string | yes | Short project name. |
| `description` | string | no | Detailed description of the project. |
| `status` | string | yes | `proposed`, `active`, `paused`, `completed`, or `abandoned`. |
| `priority` | number | yes | User-assigned or inferred priority in [0, 1]. |
| `collaborator_ids` | array of UUID | no | Identity nodes for collaborators. |
| `repository_url` | string (URL) | no | Primary source code or artifact repository. |
| `technology_stack` | array of string | no | Languages, frameworks, libraries, and tools. |
| `started_at` | string (ISO 8601) | no | When active work began. |
| `completed_at` | string (ISO 8601) | no | When completed. |
| `abandoned_at` | string (ISO 8601) | no | When abandoned. |
| `milestones` | array of `Milestone` | no | Discrete milestones within the project. |
| `tasks` | array of `Task` | no | Discrete tasks within the project. |
| `related_entity_ids` | array of UUID | no | Goals, beliefs, concepts, and other projects related to this project. |
| `history` | array of `ProjectEvent` | yes | Chronological history of lifecycle events. |
| `provenance` | `Provenance` object | yes | Provenance metadata. |
| `embedding_ref` | UUID | no | Reference to the vector embedding. |

### `Milestone` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | UUID | yes | Stable milestone ID. |
| `title` | string | yes | Short milestone title. |
| `description` | string | no | Detailed description. |
| `target_date` | string (ISO 8601) | no | Target date for completion. |
| `completed_at` | string (ISO 8601) | no | When the milestone was actually completed. |
| `status` | string | yes | `pending`, `in_progress`, `completed`, `blocked`, or `cancelled`. |

### `Task` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `id` | UUID | yes | Stable task ID. |
| `title` | string | yes | Short task title. |
| `description` | string | no | Detailed description. |
| `status` | string | yes | `pending`, `in_progress`, `completed`, `blocked`, or `cancelled`. |
| `assignee` | UUID | no | Identity node of the person responsible (user or collaborator). |
| `created_at` | string (ISO 8601) | yes | When the task was created. |
| `completed_at` | string (ISO 8601) | no | When the task was completed. |

### `ProjectEvent` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `event` | string | yes | `formed`, `started`, `progressed`, `paused`, `resumed`, `completed`, `abandoned`, or `milestone_reached`. |
| `timestamp` | string (ISO 8601) | yes | When the event occurred. |
| `source_event_ids` | array of UUID | yes | Observation events that caused this event. |
| `notes` | string | no | Free-form notes. |
| `milestone_id` | UUID | no | For `milestone_reached` events, the milestone that was reached. |

## Status Values

- `proposed` — the project has been conceived but no active work has begun.
- `active` — the project is being actively worked on.
- `paused` — the project is temporarily on hold; resumption is intended.
- `completed` — the project has reached its intended conclusion.
- `abandoned` — the project has been permanently discontinued.

## Milestone and Task Status Values

- `pending` — the item has not been started.
- `in_progress` — the item is currently being worked on.
- `completed` — the item is finished.
- `blocked` — the item cannot proceed until an external dependency is resolved.
- `cancelled` — the item will not be completed (typically because the project was redirected or abandoned).

## JSON Example

```json
{
  "schema_version": "0.1.0",
  "id": "prj_01HZX3R8P3K4N5M6Q7R8S9T0V1",
  "type": "project",
  "name": "SELF",
  "description": "A local-first personal cognitive infrastructure that observes, extracts, remembers, and synthesizes a user's life into a queryable knowledge base and an evolving identity graph.",
  "status": "active",
  "priority": 0.95,
  "collaborator_ids": ["nd_person_alex_001", "nd_person_priya_002"],
  "repository_url": "https://github.com/kliewerdaniel/qwen.git",
  "technology_stack": [
    "Python",
    "DuckDB",
    "FastAPI",
    "Ollama",
    "Qwen2.5",
    "FAISS",
    "Pydantic",
    "Next.js",
    "TypeScript"
  ],
  "started_at": "2024-01-20T10:00:00.000Z",
  "completed_at": null,
  "abandoned_at": null,
  "milestones": [
    {
      "id": "ms_01HZX0R8P3K4N5M6Q7R8S9T0V0",
      "title": "Architecture documentation",
      "description": "All architecture, schemas, evaluations, examples, and ADRs published in the repository.",
      "target_date": "2026-08-01T00:00:00.000Z",
      "completed_at": null,
      "status": "in_progress"
    },
    {
      "id": "ms_01HZX0R8P3K4N5M6Q7R8S9T0V1",
      "title": "Local model integration",
      "description": "Ollama, vLLM, and llama.cpp adapters implemented and tested with Qwen2.5.",
      "target_date": "2026-10-01T00:00:00.000Z",
      "completed_at": null,
      "status": "pending"
    },
    {
      "id": "ms_01HZX0R8P3K4N5M6Q7R8S9T0V2",
      "title": "Extractor pipeline v1",
      "description": "Observation events produced end-to-end from chat, journal, and audio sources.",
      "target_date": "2026-09-15T00:00:00.000Z",
      "completed_at": "2026-07-22T18:30:00.000Z",
      "status": "completed"
    }
  ],
  "tasks": [
    {
      "id": "tsk_01HZX0R8P3K4N5M6Q7R8S9TAA0",
      "title": "Draft schemas/observation_event.md",
      "description": "Author the canonical observation event schema with field definitions, JSON example, and validation requirements.",
      "status": "completed",
      "assignee": "nd_user_001",
      "created_at": "2026-06-01T09:00:00.000Z",
      "completed_at": "2026-06-03T17:15:00.000Z"
    },
    {
      "id": "tsk_01HZX0R8P3K4N5M6Q7R8S9TAA1",
      "title": "Draft schemas/belief.md",
      "description": "Author the belief knowledge object schema with history and provenance.",
      "status": "completed",
      "assignee": "nd_user_001",
      "created_at": "2026-06-04T09:00:00.000Z",
      "completed_at": "2026-06-05T16:45:00.000Z"
    },
    {
      "id": "tsk_01HZX0R8P3K4N5M6Q7R8S9TAA2",
      "title": "Implement DuckDB knowledge store schema",
      "description": "Create tables, indexes, and migrations for observation events, beliefs, goals, projects, and identity nodes.",
      "status": "in_progress",
      "assignee": "nd_user_001",
      "created_at": "2026-06-10T09:00:00.000Z",
      "completed_at": null
    },
    {
      "id": "tsk_01HZX0R8P3K4N5M6Q7R8S9TAA3",
      "title": "Wire Ollama adapter into Extractor",
      "description": "Replace the cloud model call with a local Ollama client and verify parity on the belief detection prompt template.",
      "status": "pending",
      "assignee": "nd_person_alex_001",
      "created_at": "2026-06-15T09:00:00.000Z",
      "completed_at": null
    },
    {
      "id": "tsk_01HZX0R8P3K4N5M6Q7R8S9TAA4",
      "title": "Author evaluation harness for Extractor",
      "description": "Build a labeled dataset and grading scripts for belief, goal, and project extraction.",
      "status": "blocked",
      "assignee": "nd_person_priya_002",
      "created_at": "2026-06-20T09:00:00.000Z",
      "completed_at": null
    }
  ],
  "related_entity_ids": [
    "gl_01HZX3R8P3K4N5M6Q7R8S9T0V1",
    "blf_01HZX3R8P3K4N5M6Q7R8S9T0V1",
    "nd_concept_localfirst",
    "nd_concept_knowledge_graph"
  ],
  "history": [
    {
      "event": "formed",
      "timestamp": "2024-01-15T09:00:00.000Z",
      "source_event_ids": ["evt_01HZX0R8P3K4N5M6Q7R8S9T0V0"],
      "notes": "Initial conception from a long design document on local-first cognitive infrastructure.",
      "milestone_id": null
    },
    {
      "event": "started",
      "timestamp": "2024-01-20T10:00:00.000Z",
      "source_event_ids": ["evt_01HZX0R8P3K4N5M6Q7R8S9T0V1"],
      "notes": "Repository initialized; first commit pushed.",
      "milestone_id": null
    },
    {
      "event": "milestone_reached",
      "timestamp": "2026-07-22T18:30:00.000Z",
      "source_event_ids": ["evt_01HZX3R8P3K4N5M6Q7R8S9T0V2"],
      "notes": "Extractor pipeline v1 cut and verified end-to-end.",
      "milestone_id": "ms_01HZX0R8P3K4N5M6Q7R8S9T0V2"
    },
    {
      "event": "progressed",
      "timestamp": "2026-08-04T14:20:00.000Z",
      "source_event_ids": ["evt_01HZX3R8P3K4N5M6Q7R8S9T0V9"],
      "notes": "Schema documentation phase; belief, goal, and identity node schemas published.",
      "milestone_id": null
    }
  ],
  "provenance": {
    "producer": "extractor.project_detection",
    "producer_version": "0.1.0",
    "produced_at": "2024-01-15T09:00:00.000Z",
    "parent_ids": ["evt_01HZX0R8P3K4N5M6Q7R8S9T0V0"],
    "model": "qwen2.5-7b",
    "model_version": "0.1.0",
    "prompt_template": "project_detection",
    "prompt_version": "0.1.0",
    "confidence": 0.9,
    "notes": "Project extracted from a design document and reinforced by repository activity."
  },
  "embedding_ref": "emb_01HZX3R8P3K4N5M6Q7R8S9T0V1"
}
```

## Validation Requirements

- All required fields must be present.
- `type` must equal `project`.
- `status` must be one of the allowed values: `proposed`, `active`, `paused`, `completed`, `abandoned`.
- `priority` must be in [0, 1].
- `history` must be non-empty and chronologically ordered (ascending by `timestamp`).
- The first event in `history` must be `formed`.
- The latest event in `history` must be compatible with `status`:
  - If `status` is `proposed`, the latest event must be `formed` and `started_at` must be null.
  - If `status` is `active`, the latest event must be `started`, `progressed`, `resumed`, or `milestone_reached`, and `started_at` must be set.
  - If `status` is `paused`, the latest event must be `paused`.
  - If `status` is `completed`, the latest event must be `completed`, and `completed_at` must be set.
  - If `status` is `abandoned`, the latest event must be `abandoned`, and `abandoned_at` must be set.
- `started_at` must be set if and only if the project has been started (`status` is `active`, `paused`, `completed`, or `abandoned`).
- `completed_at` must be set if and only if `status` is `completed`.
- `abandoned_at` must be set if and only if `status` is `abandoned`.
- `repository_url`, if present, must be a syntactically valid URL.
- Each `milestone.status` must be one of the allowed values: `pending`, `in_progress`, `completed`, `blocked`, `cancelled`.
- Each `task.status` must be one of the allowed values: `pending`, `in_progress`, `completed`, `blocked`, `cancelled`.
- For any `milestone_reached` event in `history`, `milestone_id` must be set and must reference a milestone present in the `milestones` array; conversely, any milestone with `status` `completed` must be referenced by exactly one `milestone_reached` event whose `timestamp` matches the milestone's `completed_at`.
- Every `collaborator_ids`, `related_entity_ids`, `milestone.id`, `task.id`, `task.assignee`, and `history[*].source_event_ids[*]` entry must be a valid UUID.
- `provenance` must conform to the standard `Provenance` object shape used across all knowledge objects.
- `embedding_ref`, if present, must reference an embedding stored in the vector store.

## Versioning Strategy

Standard semantic versioning. See `schemas/observation_event.md` — Migration Runner Interface. Additive changes (new optional fields, new event types, new status values that are backward compatible) bump the minor version. Breaking changes (renaming fields, changing the meaning of existing fields, removing required fields, or changing the allowed event vocabulary) bump the major version and require a migration plan that re-derives `status` from `history` for existing records.

## Storage Considerations

Projects are stored in the knowledge store (DuckDB) as a first-class table. The `milestones`, `tasks`, and `history` arrays are stored as JSON columns for full provenance and easy inspection. A parallel `Identity Graph` node of type `Project` is created in the graph store (e.g., Kuzu or Neo4j), with edges connecting the project to its collaborators, related goals, related beliefs, related concepts, and its own milestones and tasks. This allows both row-oriented queries (list active projects by priority) and graph queries (find all projects a person collaborated on, find all projects that depend on a concept). The `embedding_ref` is stored in the vector store with a back-reference in DuckDB so semantic queries can be traced back to their source project. Indexes should be created on `status`, `priority`, `started_at`, and JSON path expressions on `history[*].event` and `collaborator_ids[*]` for efficient filtering.

## Privacy Considerations

Projects may be sensitive: they reveal what the user is building, with whom, and where. Implementations must:

- Honor per-source privacy settings. A project extracted from a private journal entry or a private chat may be marked private; a project extracted from a public blog post or a public commit may be marked public. The most restrictive source setting wins for the derived object.
- Support redaction of specific projects. Redaction removes the object's name, description, repository URL, technology stack, tasks, and milestone details, and replaces the history with a single `[REDACTED]` event; the project ID is preserved so cross-references remain valid.
- Support selective deletion. Deleting a project cascades to its tasks and milestones in the knowledge store and removes the corresponding `Project` node and its edges from the identity graph. Related entities (goals, beliefs, concepts) are not deleted; their `related_entity_ids` are updated to remove the deleted project's ID. Embeddings referenced by `embedding_ref` are deleted from the vector store.
- Never export projects to third-party services, backups, or sync destinations without explicit user consent. Cloud-synced projects must be encrypted at rest and in transit, and the encryption keys must be derived from user-controlled material.
- Treat collaborator identities (in `collaborator_ids`) as third-party data. The user controls whether collaborators are recorded at all; if recorded, the collaborator's own privacy settings may further restrict how the project is exported or shared.
