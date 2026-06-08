# Schema: interest

> A knowledge object representing an interest the user has — a topic, activity, or domain they are engaged with.

---

## Overview

Interests describe what the user pays attention to and engages with over time. They cover topics (e.g., "local-first software"), activities (e.g., "woodworking"), and domains (e.g., "jazz music"). Interests are not just preferences — they are evolving relationships between the user and the things they care about.

Interests emerge, deepen, go dormant, get revived, and occasionally get abandoned. SELF tracks this lifecycle so the system can reason about engagement, surface relevant context, and understand when the user's attention has shifted.

Interests are produced by the Extractor and refined by the Identity Graph and Synthesis Engine.

## Schema Version

Current version: `0.1.0`

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Schema version. |
| `id` | string (UUID) | yes | Stable interest ID. |
| `type` | string | yes | Always `interest`. |
| `name` | string | yes | Short name for the interest. |
| `description` | string | no | Longer description of what the interest covers. |
| `domains` | array of string | no | Knowledge domains (e.g., "software", "music", "crafts"). |
| `strength` | number | yes | Strength of current engagement in [0, 1]. |
| `status` | string | yes | `active`, `dormant`, `revived`, `abandoned`. |
| `first_formed` | string (ISO 8601) | yes | When the interest was first observed. |
| `last_engaged` | string (ISO 8601) | no | When the user most recently engaged with this interest. |
| `engagement_count` | number | yes | Total number of observed engagements. |
| `related_entity_ids` | array of UUID | no | Identity nodes related to the interest (people, concepts, tools). |
| `history` | array of `InterestEvent` | yes | Chronological history of lifecycle changes. |
| `provenance` | `Provenance` object | yes | Provenance metadata. |
| `embedding_ref` | UUID | no | Reference to the vector embedding. |

### `InterestEvent` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `event` | string | yes | `formed`, `reinforced`, `engaged`, `dormant`, `revived`, `abandoned`. |
| `timestamp` | string (ISO 8601) | yes | When the event occurred. |
| `source_event_ids` | array of UUID | yes | Observation events that caused this event. |
| `strength_before` | number | no | Strength before the event. |
| `strength_after` | number | no | Strength after the event. |
| `notes` | string | no | Free-form notes. |

## Status Values

- `active` — the interest is currently engaged.
- `dormant` — the interest is not currently being engaged, but is not abandoned.
- `revived` — the interest was dormant and has been re-engaged.
- `abandoned` — the interest is no longer pursued.

## Event Values

- `formed` — the interest was first observed.
- `reinforced` — existing evidence further supports the interest (strength increased).
- `engaged` — a new instance of engagement was observed (does not necessarily change strength, but updates `last_engaged` and `engagement_count`).
- `dormant` — engagement has stopped, and the interest is now resting.
- `revived` — the interest is active again after being dormant.
- `abandoned` — the interest has been given up.

## JSON Example

```json
{
  "schema_version": "0.1.0",
  "id": "int_01HZX4S9Q4L5O6N7P8Q9R0S1T2",
  "type": "interest",
  "name": "Local-first software",
  "description": "Building software that prioritizes local data ownership, offline operation, and peer-to-peer sync over cloud-centric architectures.",
  "domains": ["software", "infrastructure", "philosophy"],
  "strength": 0.88,
  "status": "active",
  "first_formed": "2024-01-22T09:15:00.000Z",
  "last_engaged": "2026-06-12T20:30:00.000Z",
  "engagement_count": 47,
  "related_entity_ids": [
    "nd_user_001",
    "nd_concept_localfirst",
    "nd_concept_crdt",
    "nd_person_inkandswitch"
  ],
  "history": [
    {
      "event": "formed",
      "timestamp": "2024-01-22T09:15:00.000Z",
      "source_event_ids": ["evt_01HZX1S9Q4L5O6N7P8Q9R0S1T0"],
      "strength_before": null,
      "strength_after": 0.6,
      "notes": "First surfaced after the user read Incandescent's 'Local-first software' essay and shared an extended reflection."
    },
    {
      "event": "reinforced",
      "timestamp": "2024-03-04T14:00:00.000Z",
      "source_event_ids": ["evt_01HZX2T0R5M6P7Q8R9S0T1U2V3"],
      "strength_before": 0.6,
      "strength_after": 0.75,
      "notes": "User cited the essay in a blog post and built a prototype sync layer."
    },
    {
      "event": "engaged",
      "timestamp": "2024-11-18T11:00:00.000Z",
      "source_event_ids": ["evt_01HZX3U1S6N7Q8R9S0T1U2V3W4"],
      "strength_before": 0.75,
      "strength_after": 0.75,
      "notes": "Discussed CRDT tradeoffs with a collaborator during a long call."
    },
    {
      "event": "dormant",
      "timestamp": "2025-02-01T00:00:00.000Z",
      "source_event_ids": ["evt_01HZX4V2T7O8R9S0T1U2V3W4X5"],
      "strength_before": 0.75,
      "strength_after": 0.4,
      "notes": "User shifted focus to identity graph work; no observable engagement for two months."
    },
    {
      "event": "revived",
      "timestamp": "2025-05-09T08:30:00.000Z",
      "source_event_ids": ["evt_01HZX5W3U8P9S0T1U2V3W4X5Y6"],
      "strength_before": 0.4,
      "strength_after": 0.7,
      "notes": "User started designing a new local-first notes tool; mentioned the essay again."
    },
    {
      "event": "engaged",
      "timestamp": "2026-06-12T20:30:00.000Z",
      "source_event_ids": ["evt_01HZX6X4V9Q0T1U2V3W4X5Y6Z7"],
      "strength_before": 0.7,
      "strength_after": 0.88,
      "notes": "Shipped the v0.2 release of the local-first notes tool and wrote a retrospective."
    }
  ],
  "provenance": {
    "producer": "extractor.interest_detection",
    "producer_version": "0.1.0",
    "produced_at": "2024-01-22T09:15:00.000Z",
    "parent_ids": ["evt_01HZX1S9Q4L5O6N7P8Q9R0S1T0"],
    "model": "qwen2.5-7b",
    "model_version": "0.1.0",
    "prompt_template": "interest_detection",
    "prompt_version": "0.1.0",
    "confidence": 0.9,
    "notes": "Interest extracted from a long-form reflection post citing the canonical local-first essay."
  },
  "embedding_ref": "emb_01HZX4S9Q4L5O6N7P8Q9R0S1T2"
}
```

## Validation Requirements

- All required fields must be present.
- `type` must equal `interest`.
- `strength` must be in [0, 1].
- `engagement_count` must be a non-negative integer.
- `status` must be one of `active`, `dormant`, `revived`, `abandoned`.
- `history` must be non-empty and chronologically ordered (ascending by `timestamp`).
- The first event in `history` must be `formed`.
- `engaged` events must be reflected in `engagement_count` (each `engaged` event contributes one increment).
- The latest event in `history` must be consistent with `status`:
  - If `status` is `active`, the latest event may be `formed`, `reinforced`, `engaged`, or `revived`.
  - If `status` is `dormant`, the latest event must be `dormant`.
  - If `status` is `revived`, the latest event must be `revived`.
  - If `status` is `abandoned`, the latest event must be `abandoned`.
- `last_engaged` (if present) must match the timestamp of the most recent `engaged` event in `history`.
- `first_formed` must match the timestamp of the `formed` event in `history`.
- `related_entity_ids` (if present) must each be valid UUIDs.

## Versioning Strategy

Standard semantic versioning. See `schemas/observation_event.md` — Migration Runner Interface.

## Storage Considerations

Interests are stored in the knowledge store (DuckDB). The `history` array is preserved as a JSON column for full lifecycle provenance. The `embedding_ref` is stored in the vector store with a back-reference in DuckDB. Each interest also corresponds to an Identity Graph node of type `Interest`, with edges to related entities (people, concepts, tools) via `related_entity_ids`.

## Privacy Considerations

Interests may reveal sensitive information about the user (hobbies, health, politics, relationships, professional focus). Implementations must:

- Honor per-source privacy settings.
- Support redaction of specific interests.
- Support selective deletion (and cascade to derived records and identity graph edges).
- Not export interests without explicit user consent.
