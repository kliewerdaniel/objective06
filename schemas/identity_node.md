# Schema: identity_node

> A node in the user's identity graph. Represents an entity: the user, a person, a project, an organization, a tool, a concept, a place, or an event.

---

## Overview

The identity graph is the structured backbone of SELF's understanding of the user's world. An identity node is an entity in that graph. Every node has a type, attributes, aliases, and a temporal validity.

Nodes are produced by the Extractor and the Identity Graph subsystem, refined by entity resolution, and queried by the Digital Twin, the Synthesis Engine, and the user.

## Schema Version

Current version: `0.1.0`

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Schema version. |
| `id` | string (UUID) | yes | Stable, unique node ID. |
| `type` | string | yes | Node type. See "Node Types". |
| `name` | string | yes | Primary display name. |
| `aliases` | array of string | no | Alternative names. |
| `attributes` | object | no | Free-form typed attributes. |
| `first_seen` | string (ISO 8601) | yes | When the entity was first observed. |
| `last_seen` | string (ISO 8601) | yes | When the entity was last observed. |
| `valid_from` | string (ISO 8601) | no | When the entity became valid. |
| `valid_to` | string (ISO 8601) | no | When the entity ceased to be valid. |
| `deprecated` | boolean | no | Whether the node has been deprecated. |
| `superseded_by` | string (UUID) | no | The node that supersedes this one. |
| `merged_into` | string (UUID) | no | The node this was merged into. |
| `provenance` | `Provenance` object | yes | Provenance metadata. |

### `Provenance` Object

Same as `observation_event`'s provenance. See `schemas/observation_event.md`.

## Node Types

| Type | Description |
| --- | --- |
| `User` | The user themselves. Exactly one. |
| `Person` | Another human. |
| `Project` | A project. |
| `Organization` | An organization. |
| `Tool` | A tool, library, framework, service. |
| `Concept` | A concept, topic, idea. |
| `Place` | A physical or virtual place. |
| `Event` | A significant occurrence. |
| `Artifact` | A file, document, or other created work. |
| `Goal` | A goal the user is pursuing. |
| `Interest` | An interest the user has. |
| `Belief` | A belief the user holds. |
| `Community` | A group or community. |
| `Publication` | A publication (article, book, paper). |

## Attributes

Attributes are free-form typed key-value pairs. The schema does not enforce a fixed set; instead, the Identity Graph subsystem maintains a schema registry of known attribute keys per node type.

Common attributes include:

- `description` (string) — human-readable description.
- `url` (string) — primary URL.
- `email` (string) — primary email.
- `tags` (array of string) — free-form tags.
- `importance` (number) — user-assigned importance in [0, 1].
- `status` (string) — lifecycle status (active, dormant, completed, abandoned).

## JSON Example

```json
{
  "schema_version": "0.1.0",
  "id": "nd_01HZX3R8P3K4N5M6Q7R8S9T0V1",
  "type": "Project",
  "name": "SELF",
  "aliases": ["self-project", "synthetic-evolutionary-local-framework"],
  "attributes": {
    "description": "Local-first cognitive infrastructure.",
    "url": "https://github.com/example/self",
    "status": "active",
    "importance": 0.95
  },
  "first_seen": "2024-01-15T09:00:00.000Z",
  "last_seen": "2026-06-08T14:23:11.123Z",
  "valid_from": "2024-01-15T09:00:00.000Z",
  "valid_to": null,
  "deprecated": false,
  "superseded_by": null,
  "merged_into": null,
  "provenance": {
    "producer": "extractor.entity_linking",
    "producer_version": "0.1.0",
    "produced_at": "2024-01-15T09:00:00.000Z",
    "parent_ids": ["evt_01HZX0R8P3K4N5M6Q7R8S9T0V0"],
    "model": "qwen2.5-7b",
    "model_version": "0.1.0",
    "prompt_template": "entity_extraction",
    "prompt_version": "0.1.0",
    "confidence": 0.93,
    "notes": "Project name extracted from README and referenced in multiple commits."
  }
}
```

## Validation Requirements

- All required fields must be present and non-null.
- `schema_version` must equal the current version.
- `id` must be a valid UUID.
- `type` must be a known node type.
- `name` must be non-empty.
- `first_seen` and `last_seen` must be valid ISO 8601 strings in UTC.
- `valid_from` (if present) must be a valid ISO 8601 string.
- `valid_to` (if present) must be a valid ISO 8601 string and must be after `valid_from`.
- `superseded_by` and `merged_into` (if present) must be valid UUIDs.
- `provenance.producer` must be non-empty.
- Exactly one `User` node may exist at any time.

## Versioning Strategy

Standard semantic versioning. See `schemas/observation_event.md` for the full strategy.

## Storage Considerations

Identity nodes are stored in the graph store (Kuzu or Neo4j). They are indexed by type, name, and aliases for fast lookup. The temporal validity is indexed for temporal queries.

## Privacy Considerations

Identity nodes may reference people, organizations, and other entities the user interacts with. Implementations must:

- Honor the user's privacy settings for which entities to retain.
- Support anonymization (replacing real names with pseudonyms).
- Support selective deletion.
- Not include nodes in exports unless the user has opted in.
