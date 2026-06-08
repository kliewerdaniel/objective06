# Schema: persona_vector

> The vector representation of the user's identity at a point in time. The continuous, semantic complement to the discrete identity graph.

---

## Overview

The persona vector is a single high-dimensional embedding that captures the user's overall identity posture as it exists at a particular moment. Where the identity graph (see `schemas/identity_node.md`) and the belief store (see `schemas/belief.md`) are discrete, queryable, and human-readable, the persona vector is a continuous, semantic, similarity-friendly representation. It is what the Digital Twin and the Synthesis Engine reach for when they need to answer "who is this person like?" or "how close is this context to them?".

A persona vector is always a *snapshot*. It is produced by an embedding model over a curated set of identity-relevant inputs (beliefs, goals, recent observations, identity nodes, free-form reflections) and stored alongside its producing inputs, its update strategy, and its provenance. Vectors are updated over time as the user's identity drifts. Each update is itself a snapshot, and snapshots form a chronological sequence that supports rollback, comparison, and audit.

The persona vector is produced by the Persona Engine. It is consumed by the Digital Twin for retrieval, by the Synthesis Engine for reflection, and by the user interface for similarity exploration.

## Schema Version

Current version: `0.1.0`

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Schema version. |
| `id` | string (UUID) | yes | Stable persona vector snapshot ID. |
| `type` | string | yes | Always `persona_vector`. |
| `timestamp` | string (ISO 8601) | yes | When this snapshot was produced. |
| `vector` | array of float | yes | The embedding. Length must equal `dimensions`. |
| `dimensions` | integer | yes | Dimensionality of `vector`. Must be a positive integer. |
| `model` | string | yes | Embedding model identifier (e.g., `qwen3-embedding-8b`). |
| `model_version` | string | yes | Version of the embedding model used. |
| `update_strategy` | string | yes | How this snapshot was derived. See "Update Strategies". |
| `update_reason` | string | yes | Why the snapshot was produced. See "Update Reasons". |
| `contributing_knowledge_ids` | array of UUID | no | Knowledge objects (beliefs, goals, observations, identity nodes) that influenced this update. |
| `drift_from_previous` | number | no | Magnitude of change from the previous snapshot. Non-negative. |
| `previous_snapshot_id` | UUID | no | The snapshot this one was derived from, if any. |
| `confidence` | number | yes | Confidence in the snapshot's fidelity to the user's current identity, in [0, 1]. |
| `provenance` | `Provenance` object | yes | Provenance metadata. |

### Update Strategies

| Value | Description |
| --- | --- |
| `moving_average` | New vector is a weighted average of the previous vector and a freshly computed candidate. |
| `exponential_decay` | New vector blends a freshly computed candidate with prior vectors using an exponential decay. |
| `time_weighted` | New vector is a weighted average where weights reflect the recency of the contributing inputs. |
| `attention_based` | New vector is computed by an attention mechanism over contributing inputs (e.g., a transformer-based aggregator). |
| `user_tuned` | New vector was explicitly adjusted or anchored by the user. |

### Update Reasons

| Value | Description |
| --- | --- |
| `scheduled` | A routine update fired by the scheduler (e.g., daily, weekly). |
| `knowledge_added` | New knowledge (a belief, goal, observation) was added and triggered an update. |
| `user_feedback` | The user provided feedback that triggered an update. |
| `model_swap` | The embedding model changed and the vector was re-embedded from scratch or migrated. |

### `Provenance` Object

Same as `observation_event`'s provenance. See `schemas/observation_event.md`.

## JSON Example

```json
{
  "schema_version": "0.1.0",
  "id": "pvec_01HZX4S9P3K4N5M6Q7R8S9T0V2",
  "type": "persona_vector",
  "timestamp": "2026-06-08T09:15:00.000Z",
  "vector": [0.0234, -0.0156, 0.0841, -0.0023, 0.1192, 0.0445, -0.0778, 0.0321, "...truncated for readability, 1024 floats total..."],
  "dimensions": 1024,
  "model": "qwen3-embedding-8b",
  "model_version": "1.2.0",
  "update_strategy": "time_weighted",
  "update_reason": "scheduled",
  "contributing_knowledge_ids": [
    "blf_01HZX3R8P3K4N5M6Q7R8S9T0V1",
    "blf_01HZX3R8P3K4N5M6Q7R8S9T0V3",
    "goal_01HZX2A7P3K4N5M6Q7R8S9T0V5",
    "obs_01HZX1B6P3K4N5M6Q7R8S9T0V7",
    "nd_concept_localfirst",
    "nd_project_objself"
  ],
  "drift_from_previous": 0.0412,
  "previous_snapshot_id": "pvec_01HZX3G7P3K4N5M6Q7R8S9T0V1",
  "confidence": 0.83,
  "provenance": {
    "producer": "persona_engine.snapshot",
    "producer_version": "0.1.0",
    "produced_at": "2026-06-08T09:15:00.000Z",
    "parent_ids": [
      "pvec_01HZX3G7P3K4N5M6Q7R8S9T0V1",
      "blf_01HZX3R8P3K4N5M6Q7R8S9T0V1",
      "blf_01HZX3R8P3K4N5M6Q7R8S9T0V3",
      "goal_01HZX2A7P3K4N5M6Q7R8S9T0V5",
      "obs_01HZX1B6P3K4N5M6Q7R8S9T0V7"
    ],
    "model": "qwen3-embedding-8b",
    "model_version": "1.2.0",
    "prompt_template": "persona_aggregation",
    "prompt_version": "0.1.0",
    "confidence": 0.83,
    "notes": "Weekly scheduled snapshot. Aggregated over 6 contributing knowledge objects using the time_weighted strategy with a 30-day half-life."
  }
}
```

## Validation Requirements

- All required fields must be present.
- `type` must equal `persona_vector`.
- `dimensions` must be a positive integer.
- `vector` must be an array whose length exactly equals `dimensions`.
- All elements of `vector` must be finite numbers (no `NaN` or `Infinity`).
- `model` and `model_version` must be non-empty strings.
- `update_strategy` must be one of the allowed values: `moving_average`, `exponential_decay`, `time_weighted`, `attention_based`, `user_tuned`.
- `update_reason` must be one of the allowed values: `scheduled`, `knowledge_added`, `user_feedback`, `model_swap`.
- `drift_from_previous`, if present, must be a non-negative finite number.
- `confidence` must be in [0, 1].
- `previous_snapshot_id`, if present, must be a valid UUID and must reference an existing prior snapshot.
- `contributing_knowledge_ids`, if present, must contain only valid UUIDs, and each referenced object must exist in the knowledge store at the time of validation.
- `timestamp` must be a valid ISO 8601 timestamp and must not precede the `timestamp` of `previous_snapshot_id` (snapshots are monotonic in time).
- The `model` and `model_version` in the top-level fields must match those in `provenance`.

## Versioning Strategy

Standard semantic versioning. See `schemas/observation_event.md`.

When the embedding model changes (a `model_swap` update), the new snapshot is the first of a new model lineage. Snapshots across model lineages are not directly comparable in vector space and must not be used as inputs to similarity computations that assume a shared embedding space. Implementations must record `model` and `model_version` on every snapshot precisely so that lineage boundaries are auditable.

## Storage Considerations

Persona vectors are stored in two coordinated stores:

- The high-dimensional `vector` itself is stored in a vector database (FAISS or a FAISS-compatible index such as Qdrant, Milvus, or pgvector). Each entry is keyed by the snapshot `id`.
- All other fields (metadata, provenance, update strategy, contributing knowledge IDs, drift, confidence, timestamps) are stored in DuckDB, keyed by `id`, with a back-reference to the vector index entry.

This split keeps the metadata queryable in SQL (for audit, lineage, and lineage-restricted similarity) while keeping the embedding itself in an index optimized for nearest-neighbor search. Snapshots are never deleted by the system; they form an append-only history. When the user requests deletion of their data, see Privacy Considerations.

## Privacy Considerations

Persona vectors may encode sensitive information. Even when stripped of explicit identifiers, a high-dimensional embedding over beliefs, goals, and identity can leak attributes that the user did not intend to expose. Implementations must:

- Encrypt vectors at rest using the same key-management regime as the rest of the knowledge store.
- Encrypt vectors in transit between the embedding service, the vector database, and the DuckDB metadata store.
- Restrict raw vector access to the Persona Engine, the Digital Twin, and the Synthesis Engine. Similarity queries from user-facing surfaces must return results (neighbor IDs, similarity scores) but not the raw vectors.
- Support full deletion of a snapshot and its associated vector on user request. Deletion must be cascading: if a snapshot is removed, derived artifacts (similarity caches, reflection logs that reference it by ID) must be purged or have the reference redacted.
- Support user-driven "vector reset" — a `user_tuned` snapshot anchored to a neutral prior — without exposing the mechanism to surface sensitive intermediate states.
- Honor per-source privacy settings: a contributing knowledge object marked private must not be silently included in a persona snapshot without explicit user consent at the time of inclusion.
- Not export persona vectors or similarity results outside the local knowledge store without explicit user consent.
