# Schema: relationship

> An edge in the identity graph connecting two identity nodes with a typed, weighted, temporal relationship.

---

## Overview

The identity graph is the structured backbone of SELF's understanding of the user's world. A relationship is a directed edge in that graph that connects two identity nodes and encodes how those entities relate to one another over time.

Every relationship has a type, a weight indicating its strength, a directional or bidirectional flag, free-form attributes, a temporal validity window, a lifecycle status, an event history, and a provenance record.

Relationships are produced by the Extractor and the Identity Graph subsystem, refined by entity resolution and temporal decay models, and queried by the Digital Twin, the Synthesis Engine, and the user to reconstruct context, infer relevance, and reason about the user's evolving world.

## Schema Version

Current version: `0.1.0`

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Schema version. |
| `id` | string (UUID) | yes | Stable, unique relationship ID. |
| `type` | string | yes | Always `"relationship"`. |
| `source_node_id` | string (UUID) | yes | ID of the source identity node. |
| `target_node_id` | string (UUID) | yes | ID of the target identity node. |
| `relationship_type` | string | yes | Relationship type. See "Relationship Types". |
| `weight` | number | yes | Strength of the relationship in [0, 1]. |
| `bidirectional` | boolean | no | Whether the relationship is symmetric. Default `false`. |
| `attributes` | object | no | Free-form typed attributes. |
| `first_formed` | string (ISO 8601) | yes | When the relationship was first formed. |
| `last_reinforced` | string (ISO 8601) | yes | When the relationship was last reinforced or observed. |
| `valid_from` | string (ISO 8601) | no | When the relationship became valid. |
| `valid_to` | string (ISO 8601) | no | When the relationship ceased to be valid. |
| `recorded_at` | string (ISO 8601) | yes | When SELF first recorded this relationship. |
| `recorded_updated_at` | string (ISO 8601) | yes | When SELF last updated its record. |
| `status` | string | no | Lifecycle status. See "Status Values". |
| `history` | array of `RelationshipEvent` | no | Chronological list of state-change events. |
| `provenance` | `Provenance` object | yes | Provenance metadata. |

### `RelationshipEvent` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `event` | string | yes | Event type. See "Event Types". |
| `timestamp` | string (ISO 8601) | yes | When the event occurred. |
| `weight_after` | number | no | Weight value after the event. |
| `attributes_snapshot` | object | no | Attributes as they existed immediately after the event. |
| `reason` | string | no | Human-readable reason or source. |
| `provenance` | `Provenance` object | no | Provenance for this specific event. |

### `Provenance` Object

Same as `observation_event`'s provenance. See `schemas/observation_event.md`.

## Relationship Types

| Type | Description |
| --- | --- |
| `knows` | The source node knows the target node as a person or entity. |
| `works_on` | The source node works on the target node (typically a project, artifact, or organization). |
| `member_of` | The source node is a member of the target node (typically a community or organization). |
| `part_of` | The source node is a structural part of the target node. |
| `uses` | The source node uses the target node (typically a tool, library, or service). |
| `related_to` | A generic, typed-but-untyped relationship. |
| `located_in` | The source node is located in the target node (typically a place). |
| `participated_in` | The source node participated in the target node (typically an event). |
| `created` | The source node created the target node. |
| `believes` | The source node holds a belief expressed by the target node. |
| `pursues` | The source node is pursuing the target node (typically a goal). |
| `interested_in` | The source node has an interest in the target node. |
| `knows_about` | The source node has knowledge about the target node (typically a concept or topic). |
| `custom_*` | A custom relationship type prefixed with `custom_` and defined by the user or an integration. |

## Status Values

| Status | Description |
| --- | --- |
| `active` | The relationship is currently in force and considered live. |
| `dormant` | The relationship exists but has not been observed recently. |
| `dissolved` | The relationship has ended and is no longer valid. |
| `superseded` | The relationship has been replaced by another relationship. |

## Event Types

| Event | Description |
| --- | --- |
| `formed` | The relationship was first established. |
| `reinforced` | The relationship was observed or strengthened. |
| `weakened` | The relationship was observed to have weakened. |
| `dissolved` | The relationship ended. |
| `superseded` | The relationship was replaced by another. |
| `attributes_changed` | One or more attributes of the relationship changed. |

## Attributes

Attributes are free-form typed key-value pairs. The schema does not enforce a fixed set; instead, the Identity Graph subsystem maintains a schema registry of known attribute keys per relationship type.

Common attributes include:

- `role` (string) — the role the source node plays in the relationship (e.g., "lead", "contributor", "observer").
- `context` (string) — a short description of the relationship's context.
- `confidence` (number) — extractor confidence in [0, 1].
- `evidence_count` (integer) — number of independent observations supporting the relationship.
- `tags` (array of string) — free-form tags.
- `mutual` (boolean) — whether the target node has acknowledged the relationship.
- `emotional_valence` (number) — user-assigned emotional valence in [-1, 1].
- `privacy` (string) — per-relationship privacy level (`public`, `private`, `restricted`).

## JSON Example

```json
{
  "schema_version": "0.1.0",
  "id": "re_01HZX4S9Q4L5O6P7R8S9T0V2W3",
  "type": "relationship",
  "source_node_id": "nd_01HZX0Q8P3K4N5M6Q7R8S9T0U8",
  "target_node_id": "nd_01HZX3R8P3K4N5M6Q7R8S9T0V1",
  "relationship_type": "works_on",
  "weight": 0.92,
  "bidirectional": false,
  "attributes": {
    "role": "lead",
    "context": "Primary project lead for the SELF cognitive infrastructure.",
    "confidence": 0.95,
    "evidence_count": 47,
    "tags": ["core", "long-term"],
    "mutual": true,
    "emotional_valence": 0.8,
    "privacy": "private"
  },
  "first_formed": "2024-01-15T09:00:00.000Z",
  "last_reinforced": "2026-06-08T14:23:11.123Z",
  "valid_from": "2024-01-15T09:00:00.000Z",
  "valid_to": null,
  "status": "active",
  "history": [
    {
      "event": "formed",
      "timestamp": "2024-01-15T09:00:00.000Z",
      "weight_after": 0.6,
      "attributes_snapshot": {
        "role": "lead",
        "confidence": 0.8,
        "evidence_count": 1
      },
      "reason": "Initial project creation detected from README and first commit.",
      "provenance": {
        "producer": "extractor.relationship_inference",
        "producer_version": "0.1.0",
        "produced_at": "2024-01-15T09:00:00.000Z",
        "parent_ids": ["obs_01HZX0R8P3K4N5M6Q7R8S9T0V0"],
        "confidence": 0.8
      }
    },
    {
      "event": "reinforced",
      "timestamp": "2024-03-10T11:15:00.000Z",
      "weight_after": 0.75,
      "attributes_snapshot": {
        "evidence_count": 12
      },
      "reason": "Multiple commits and design documents referenced the relationship.",
      "provenance": {
        "producer": "extractor.relationship_inference",
        "producer_version": "0.1.0",
        "produced_at": "2024-03-10T11:15:00.000Z",
        "parent_ids": ["obs_01HZX1S9Q4L5O6P7R8S9T0V2W1"],
        "confidence": 0.88
      }
    },
    {
      "event": "attributes_changed",
      "timestamp": "2024-06-01T00:00:00.000Z",
      "attributes_snapshot": {
        "role": "lead",
        "context": "Primary project lead for the SELF cognitive infrastructure.",
        "mutual": true
      },
      "reason": "User confirmed the role and mutual status during a review session.",
      "provenance": {
        "producer": "user.confirmation",
        "producer_version": "0.1.0",
        "produced_at": "2024-06-01T00:00:00.000Z",
        "parent_ids": ["int_01HZX2T0R5M6P7Q8S9T0V3W4X2"],
        "confidence": 1.0
      }
    },
    {
      "event": "reinforced",
      "timestamp": "2026-06-08T14:23:11.123Z",
      "weight_after": 0.92,
      "attributes_snapshot": {
        "evidence_count": 47
      },
      "reason": "Recent commit activity and synthesis output reference the relationship.",
      "provenance": {
        "producer": "extractor.relationship_inference",
        "producer_version": "0.1.0",
        "produced_at": "2026-06-08T14:23:11.123Z",
        "parent_ids": ["obs_01HZX4S9Q4L5O6P7R8S9T0V3X4"],
        "confidence": 0.95
      }
    }
  ],
  "provenance": {
    "producer": "extractor.relationship_inference",
    "producer_version": "0.1.0",
    "produced_at": "2026-06-08T14:23:11.123Z",
    "parent_ids": [
      "obs_01HZX0R8P3K4N5M6Q7R8S9T0V0",
      "obs_01HZX1S9Q4L5O6P7R8S9T0V2W1",
      "obs_01HZX4S9Q4L5O6P7R8S9T0V3X4"
    ],
    "model": "qwen2.5-7b",
    "model_version": "0.1.0",
    "prompt_template": "relationship_extraction",
    "prompt_version": "0.1.0",
    "confidence": 0.93,
    "notes": "Aggregated across 47 supporting observations spanning the full project history."
  }
}
```

## Validation Requirements

- All required fields must be present and non-null.
- `schema_version` must equal the current version.
- `id` must be a valid UUID.
- `type` must equal `"relationship"`.
- `source_node_id` must be a valid UUID and must reference an existing identity node.
- `target_node_id` must be a valid UUID and must reference an existing identity node.
- `source_node_id` must not equal `target_node_id` (no self-loops).
- `relationship_type` must be a known type (from the list above, or a `custom_*` type registered in the schema registry).
- `weight` must be a number in the closed interval [0, 1].
- `bidirectional`, if present, must be a boolean.
- `first_formed` and `last_reinforced` must be valid ISO 8601 strings in UTC, and `last_reinforced` must be greater than or equal to `first_formed`.
- `valid_from` (if present) must be a valid ISO 8601 string.
- `valid_to` (if present) must be a valid ISO 8601 string and must be after `valid_from`.
- `status`, if present, must be one of `active`, `dormant`, `dissolved`, or `superseded`.
- `attributes`, if present, must be a JSON object whose keys are strings and whose values are JSON-typed.
- `history`, if present, must be an array of `RelationshipEvent` objects ordered chronologically (ascending by `timestamp`).
- Every `RelationshipEvent` must have a non-empty `event` from the known set, a valid ISO 8601 `timestamp`, and (when present) a `weight_after` in [0, 1].
- `provenance.producer` must be non-empty.
- If `status` is `dissolved` or `superseded`, `valid_to` must be present.
- A relationship marked `bidirectional: true` must be stored as a single canonical edge; queries may traverse it in either direction without creating a duplicate.

## Versioning Strategy

Standard semantic versioning. See `schemas/observation_event.md` for the full strategy. Relationships follow the same rules as identity nodes: additive changes bump the minor version, breaking changes bump the major version, and bug fixes bump the patch version.

When a new `relationship_type` is added without altering existing fields, the minor version is bumped and existing relationships remain valid. When a field is renamed, removed, or its semantics change, the major version is bumped and a migration path is required.

## Storage Considerations

Relationships are stored in the graph store (LadybugDB (or compatible Kuzu-successor) or Neo4j) as directed edges between two identity nodes. The relationship ID is stored as an edge property and used as the primary key for retrieval, updates, and history lookups.

The following indexes are required for production use:

- Composite index on `(source_node_id, relationship_type)` for forward traversal.
- Composite index on `(target_node_id, relationship_type)` for reverse traversal.
- Index on `relationship_type` alone for type-wide queries.
- Index on `status` for filtering live versus historical relationships.
- Index on `last_reinforced` for temporal decay and recency queries.
- Index on `weight` for ranking by relationship strength.

The `history` array is stored inline on the edge for relationships with a small number of events, and is moved to a separate `relationship_event` table or collection for relationships with large histories. In LadybugDB, history is modeled as an additional node type connected to the edge via a `HAS_EVENT` relationship. In Neo4j, history is modeled as an embedded list for small histories and as linked event nodes for large histories.

Bidirectional relationships are stored as a single canonical edge with `bidirectional: true`; the graph store is queried in both directions without duplicating the edge. Reverse traversal is handled by the query layer.

Temporal queries (e.g., "what did the user work on in 2025?") use the `valid_from` and `valid_to` fields. The history array supports event-level queries (e.g., "when was this relationship last reinforced?").

## Privacy Considerations

Relationships are the most privacy-sensitive artifacts in the identity graph because they encode the connections between the user and other people, organizations, projects, and concepts. Implementations must:

- Honor per-relationship privacy settings stored in `attributes.privacy`. A relationship marked `private` or `restricted` must not appear in cross-user sharing, exports, or model training data.
- Support per-relationship visibility: the user may mark some relationships as visible to a subset of integrations (e.g., a calendar integration) and hide them from others (e.g., a social graph integration).
- Support selective deletion. When the user requests deletion of a relationship, both endpoints (`source_node_id` and `target_node_id`) must be notified so that the other side can also be cleaned up if appropriate. For example, deleting a `knows` relationship between the user and another person should cascade a notification to the other person's record (within the local store) so the user can decide whether to remove the reverse reference.
- Cascade-deletion behavior must be configurable per relationship type. Some relationships (e.g., `part_of`) should cascade-delete when either endpoint is deleted. Others (e.g., `knows`) should be dissolved but not cascade-delete the other node.
- Anonymize third parties by default in any export. Real names of non-user persons must be replaced with pseudonyms unless the user has explicitly opted in to sharing them.
- Audit all access to relationships marked `restricted`, including reads, writes, and exports.
- Never include relationships in model training data unless the user has explicitly opted in at the integration level.
- Honor the right to be forgotten. When a user requests deletion of all data, all relationships involving that user must be dissolved, and the dissolution events must be recorded in each affected relationship's history before the relationship itself is purged.
