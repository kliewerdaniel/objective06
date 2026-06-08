# Schema: belief

> A knowledge object representing a belief the user holds. A belief is a proposition the user accepts as true (or partly true), with a confidence level and provenance.

---

## Overview

Beliefs are central to the user's identity model. They represent what the user thinks is true about the world, about themselves, about other people, about topics. Beliefs change over time — they are added, refined, contradicted, and abandoned. SELF tracks these changes.

Beliefs are produced by the Extractor and refined by the Identity Graph and Synthesis Engine.

## Schema Version

Current version: `0.1.0`

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Schema version. |
| `id` | string (UUID) | yes | Stable belief ID. |
| `type` | string | yes | Always `belief`. |
| `statement` | string | yes | The belief statement. |
| `polarity` | string | yes | `affirm`, `deny`, `uncertain`, or `conditional`. |
| `condition` | string | no | For conditional beliefs, the condition. |
| `domains` | array of string | no | Knowledge domains (e.g., "programming", "politics"). |
| `strength` | number | yes | Strength of belief in [0, 1]. |
| `confidence` | number | yes | Confidence in the system's representation in [0, 1]. |
| `subject_entities` | array of UUID | no | Identity nodes the belief is about. |
| `first_formed` | string (ISO 8601) | yes | When the belief was first inferred. |
| `last_reinforced` | string (ISO 8601) | yes | When the belief was last supported. |
| `last_contradicted` | string (ISO 8601) | no | When the belief was last contradicted. |
| `status` | string | yes | `active`, `weakening`, `abandoned`, `superseded`. |
| `superseded_by` | UUID | no | The belief that supersedes this one. |
| `history` | array of `BeliefEvent` | yes | Chronological history of changes. |
| `provenance` | `Provenance` object | yes | Provenance metadata. |
| `embedding_ref` | UUID | no | Reference to the vector embedding. |

### `BeliefEvent` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `event` | string | yes | `formed`, `reinforced`, `contradicted`, `weakened`, `abandoned`, `superseded`, `reinstated`. |
| `timestamp` | string (ISO 8601) | yes | When the event occurred. |
| `source_event_ids` | array of UUID | yes | Observation events that caused this event. |
| `strength_before` | number | no | Strength before the event. |
| `strength_after` | number | no | Strength after the event. |
| `notes` | string | no | Free-form notes. |

## Polarity Values

- `affirm` — the user holds the statement as true.
- `deny` — the user holds the statement as false (i.e., believes the negation).
- `uncertain` — the user is undecided.
- `conditional` — the user holds the statement as true under the specified condition.

## Status Values

- `active` — the belief is currently held.
- `weakening` — the belief is being challenged but not yet abandoned.
- `abandoned` — the belief is no longer held.
- `superseded` — the belief has been replaced by a successor.

## JSON Example

```json
{
  "schema_version": "0.1.0",
  "id": "blf_01HZX3R8P3K4N5M6Q7R8S9T0V1",
  "type": "belief",
  "statement": "Local-first software is the right model for personal cognitive infrastructure.",
  "polarity": "affirm",
  "condition": null,
  "domains": ["software", "philosophy", "infrastructure"],
  "strength": 0.92,
  "confidence": 0.88,
  "subject_entities": ["nd_user_001", "nd_concept_localfirst"],
  "first_formed": "2024-02-10T11:30:00.000Z",
  "last_reinforced": "2026-06-05T16:45:00.000Z",
  "last_contradicted": null,
  "status": "active",
  "superseded_by": null,
  "history": [
    {
      "event": "formed",
      "timestamp": "2024-02-10T11:30:00.000Z",
      "source_event_ids": ["evt_01HZX0R8P3K4N5M6Q7R8S9T0V0"],
      "strength_before": null,
      "strength_after": 0.7,
      "notes": "Initial formation from a long reflection post."
    },
    {
      "event": "reinforced",
      "timestamp": "2026-06-05T16:45:00.000Z",
      "source_event_ids": ["evt_01HZX3R8P3K4N5M6Q7R8S9T0V9"],
      "strength_before": 0.7,
      "strength_after": 0.92,
      "notes": "Reinforced by a podcast and a long discussion with a collaborator."
    }
  ],
  "provenance": {
    "producer": "extractor.belief_detection",
    "producer_version": "0.1.0",
    "produced_at": "2024-02-10T11:30:00.000Z",
    "parent_ids": ["evt_01HZX0R8P3K4N5M6Q7R8S9T0V0"],
    "model": "qwen2.5-7b",
    "model_version": "0.1.0",
    "prompt_template": "belief_detection",
    "prompt_version": "0.1.0",
    "confidence": 0.88,
    "notes": "Belief extracted from a structured reflection."
  },
  "embedding_ref": "emb_01HZX3R8P3K4N5M6Q7R8S9T0V1"
}
```

## Validation Requirements

- All required fields must be present.
- `type` must equal `belief`.
- `polarity` must be one of the allowed values.
- `strength` and `confidence` must be in [0, 1].
- `status` must be one of the allowed values.
- `history` must be non-empty and chronologically ordered.
- The first event in `history` must be `formed`.
- The latest event in `history` must match `status` (e.g., if `status` is `abandoned`, the latest event must be `abandoned`).
- `superseded_by` (if present) must be a valid UUID and the referenced belief must have this belief in its `superseded_by` chain.

## Versioning Strategy

Standard semantic versioning. See `schemas/observation_event.md`.

## Storage Considerations

Beliefs are stored in the knowledge store (DuckDB). The `history` array is preserved as a JSON column for full provenance. The `embedding_ref` is stored in the vector store with a back-reference in DuckDB.

## Privacy Considerations

Beliefs may be sensitive. Implementations must:

- Honor per-source privacy settings.
- Support redaction of specific beliefs.
- Support selective deletion (and cascade to derived records).
- Not export beliefs without explicit user consent.
