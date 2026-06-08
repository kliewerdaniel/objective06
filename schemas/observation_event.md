# Schema: observation_event

> The atomic unit of input to SELF. An observation event is a structured, immutable record of something that happened in the user's digital environment.

---

## Overview

Every interaction SELF has with the outside world begins as an observation event. Files modified, commits made, emails received, pages visited, commands run, notes written — all become observation events. Events are produced by the Observer subsystem and consumed by the Extractor and (in some cases) other subsystems.

Observation events are **immutable**: once written, they are not modified. If the underlying activity changes (e.g., a file is deleted), a new event is produced. If the interpretation of an event changes (e.g., a more accurate extraction), a new knowledge object is produced. The original event remains.

## Schema Version

Current version: `0.1.0`

Versioning follows semantic versioning. Breaking changes require a major version bump. See "Versioning Strategy" below.

Migrations are implemented as versioned Python modules in `tools/schema_migrate/`. Each module exports a `migrate(record: dict, from_version: str, to_version: str) -> dict` function. The Storage subsystem automatically applies the chain of migrations on read when a record's `schema_version` does not match the current version. Migrations are idempotent. The migration chain is tested in `evaluations/schema_migration.md`.

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | The version of this schema the record conforms to. |
| `id` | string (UUID) | yes | Stable, unique identifier for this event. |
| `event_type` | string | yes | The high-level type of the event. See "Event Types". |
| `source` | `Source` object | yes | The source of the event. |
| `timestamp` | string (ISO 8601) | yes | Wall-clock time of the event (UTC). |
| `monotonic_ts` | integer | yes | Monotonic timestamp for ordering. |
| `observed_at` | string (ISO 8601) | yes | Wall-clock time SELF observed the event. |
| `actor` | `Actor` object | yes | The actor that produced the event. |
| `subject` | `Subject` object | no | The primary subject of the event. |
| `payload` | `Payload` object | yes | The event payload, type-dependent. |
| `content_hash` | string | yes | Hash of the canonicalized payload. |
| `raw_ref` | string | no | Filesystem reference to the raw artifact. |
| `tags` | array of string | no | User or system-provided tags. |
| `provenance` | `Provenance` object | yes | Provenance metadata. |

### `Source` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `kind` | string | yes | The source kind. See "Source Kinds". |
| `identifier` | string | yes | The source identifier (e.g., file path, repository URL). |
| `adapter` | string | yes | The adapter that produced this event. |
| `adapter_version` | string | yes | The version of the adapter. |

### `Actor` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `kind` | string | yes | "user", "system", "service", or "external". |
| `identifier` | string | yes | Stable identifier (e.g., user ID, service name). |

### `Subject` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `kind` | string | yes | The subject kind (file, commit, message, page, etc.). |
| `identifier` | string | yes | The subject identifier. |
| `attributes` | object | no | Free-form attributes. |

### `Payload` Object

The payload is a discriminated union by `event_type`. The shape is defined per event type. Common payload fields include:

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `summary` | string | yes | A human-readable summary of the event. |
| `data` | object | yes | Structured event-specific data. |
| `entities` | array of `EntityHint` | no | Entities the event hints at. |
| `language` | string | no | BCP-47 language tag of the content, if any. |

### `EntityHint` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `name` | string | yes | The hinted entity name. |
| `type` | string | no | The hinted entity type. |
| `span` | object | no | Source text span (start, end offsets). |

### `Provenance` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `producer` | string | yes | The subsystem that produced this record. |
| `producer_version` | string | yes | The version of the producer. |
| `produced_at` | string (ISO 8601) | yes | When the record was produced. |
| `parent_ids` | array of string | no | IDs of records this was derived from (empty for events). |
| `model` | string | no | Model used, if any. |
| `model_version` | string | no | Model version, if any. |
| `prompt_template` | string | no | Prompt template used, if any. |
| `prompt_version` | string | no | Prompt template version, if any. |
| `confidence` | number | no | Confidence in [0, 1], if applicable. |
| `notes` | string | no | Free-form notes. |

## Event Types

| `event_type` | Description |
| --- | --- |
| `file.created` | A file was created. |
| `file.modified` | A file was modified. |
| `file.deleted` | A file was deleted. |
| `file.renamed` | A file was renamed. |
| `git.commit` | A git commit was made. |
| `git.checkout` | A git checkout occurred. |
| `git.merge` | A git merge occurred. |
| `github.star` | A repository was starred. |
| `github.issue.opened` | A GitHub issue was opened. |
| `github.issue.closed` | A GitHub issue was closed. |
| `github.pr.opened` | A pull request was opened. |
| `github.pr.merged` | A pull request was merged. |
| `github.pr.reviewed` | A pull request review was submitted. |
| `rss.item.published` | An RSS item was published. |
| `email.received` | An email was received. |
| `email.sent` | An email was sent. |
| `browser.page.visited` | A web page was visited. |
| `browser.bookmark.added` | A bookmark was added. |
| `terminal.command.run` | A terminal command was executed. |
| `markdown.note.created` | A markdown note was created. |
| `markdown.note.modified` | A markdown note was modified. |
| `calendar.event.created` | A calendar event was created. |
| `calendar.event.completed` | A calendar event was completed. |
| `system.action.executed` | The system took an action (closing the loop). |

## Source Kinds

| `kind` | Description |
| --- | --- |
| `filesystem` | A file or directory. |
| `git` | A git repository. |
| `github` | A GitHub repository. |
| `rss` | An RSS or Atom feed. |
| `email` | An email account. |
| `browser` | A browser. |
| `terminal` | A terminal session. |
| `markdown` | A markdown note collection. |
| `calendar` | A calendar service. |
| `system` | The system itself. |

## JSON Example

```json
{
  "schema_version": "0.1.0",
  "id": "evt_01HZX3R8P3K4N5M6Q7R8S9T0V1",
  "event_type": "git.commit",
  "source": {
    "kind": "git",
    "identifier": "/Users/user/projects/self",
    "adapter": "git_hooks",
    "adapter_version": "0.1.0"
  },
  "timestamp": "2026-06-08T14:23:11.123Z",
  "monotonic_ts": 1234567890,
  "observed_at": "2026-06-08T14:23:11.456Z",
  "actor": {
    "kind": "user",
    "identifier": "user_001"
  },
  "subject": {
    "kind": "commit",
    "identifier": "a1b2c3d4e5f6",
    "attributes": {
      "branch": "main",
      "message_excerpt": "feat(memory): add snapshot manager"
    }
  },
  "payload": {
    "summary": "Committed changes to the memory subsystem on main.",
    "data": {
      "branch": "main",
      "message": "feat(memory): add snapshot manager",
      "files_changed": 4,
      "insertions": 187,
      "deletions": 23
    },
    "entities": [
      {
        "name": "memory",
        "type": "Tool",
        "span": null
      }
    ],
    "language": "en"
  },
  "content_hash": "sha256:abcd1234...",
  "raw_ref": "raw/2026/06/08/evt_01HZX3R8P3K4N5M6Q7R8S9T0V1.json",
  "tags": ["work", "self-project"],
  "provenance": {
    "producer": "observer.git_hooks",
    "producer_version": "0.1.0",
    "produced_at": "2026-06-08T14:23:11.456Z",
    "parent_ids": [],
    "model": null,
    "model_version": null,
    "prompt_template": null,
    "prompt_version": null,
    "confidence": 1.0,
    "notes": "Post-commit hook fired."
  }
}
```

## Validation Requirements

- All required fields must be present and non-null.
- `schema_version` must equal the current version (or a supported prior version).
- `id` must be a valid UUID.
- `timestamp` must be a valid ISO 8601 string in UTC.
- `monotonic_ts` must be a non-negative integer.
- `content_hash` must be a valid hash with a recognized algorithm prefix.
- `event_type` must be a known event type.
- `source.kind` must be a known source kind.
- `actor.kind` must be a known actor kind.
- The payload must conform to the schema for the given `event_type`.
- `provenance.producer` must be non-empty.
- `provenance.produced_at` must be a valid ISO 8601 string.

## Versioning Strategy

Schemas are versioned semantically:

- **Major** version bump: a breaking change to the schema. Records written under the old major version are not guaranteed to be readable by the new implementation. Migration scripts are required.
- **Minor** version bump: a backwards-compatible addition (e.g., a new optional field). Records written under the old minor version are readable by the new implementation.
- **Patch** version bump: a documentation or example fix. No schema change.

The current version is recorded in the `schema_version` field of every record. Implementations must support reading the current version and the immediately prior major version. Older versions are migrated on read.

When a new version is introduced:

1. The new schema is documented in this file.
2. A migration script is provided.
3. The new version is announced in the changelog.
4. A deprecation notice is added to the old version.
5. After one major version cycle, the old version is no longer supported.

## Storage Considerations

Observation events are stored in the event store of the Memory subsystem. They are partitioned by `source.kind` and time for efficient retrieval. The `raw_ref` points to the canonical raw artifact on the filesystem, which is content-addressable.

## Privacy Considerations

Observation events may contain sensitive content (e.g., the text of a note, the body of an email). Implementations must:

- Apply the privacy filters configured for each source at the adapter level.
- Encrypt at rest where configured.
- Never log event content in plain text outside the system.
- Support selective deletion of events and their derived records.

See `security/privacy_model.md`.
