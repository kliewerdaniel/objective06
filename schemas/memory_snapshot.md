# Schema: memory_snapshot

> A point-in-time capture of the entire memory state. Used for backup, migration, rollback, and debugging.

---

## Overview

A memory snapshot is a complete, self-contained, content-addressable capture of the state of SELF's memory at a specific point in time. Snapshots freeze the event store, the knowledge store, the summaries, the audit log, and any associated embeddings into a single, restorable bundle.

Snapshots serve four primary purposes:

1. **Backup** — periodic durable copies of the user's memory, stored locally or off-device.
2. **Migration** — moving memory state between machines, accounts, or SELF installations.
3. **Rollback** — restoring prior state after a bad update, a botched extraction, or a model regression.
4. **Debugging** — capturing a reproducible state for triage, regression testing, and post-mortem analysis.

Snapshots are produced by the Memory subsystem's Snapshot Manager and can be created on demand, on a schedule, automatically before risky operations (upgrades, migrations), or as incremental deltas against a prior snapshot.

A snapshot is **immutable** once written. Its `content_address` is the cryptographic identity of the bundle; any modification after the fact invalidates the integrity hash. To "edit" a snapshot, the system writes a new snapshot that supersedes the old one.

A snapshot is **self-describing**. The manifest (this schema) contains everything needed to verify, restore, and reason about the bundle without external context, except for the encryption key referenced by `encryption.key_reference`.

## Schema Version

Current version: `0.1.0`

Versioning follows semantic versioning. Breaking changes require a major version bump. See "Versioning Strategy" below.

## Field Definitions

### Top-Level Fields

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `schema_version` | string | yes | Schema version of this manifest. |
| `id` | string (UUID) | yes | Stable, unique identifier for this snapshot. |
| `type` | string | yes | Always `memory_snapshot`. |
| `name` | string | yes | User-given human-readable name for the snapshot. |
| `description` | string | no | Free-form description of why the snapshot was taken. |
| `snapshot_type` | string | yes | Kind of snapshot. See "Snapshot Types". |
| `created_at` | string (ISO 8601) | yes | Wall-clock time the snapshot was created (UTC). |
| `system_version` | string | yes | Semver of the SELF version that created the snapshot. |
| `storage_substrate_versions` | object | yes | Map of substrate name to its semver at snapshot time. |
| `event_count` | integer | yes | Number of observation events included. |
| `knowledge_object_count` | integer | yes | Number of knowledge objects included. |
| `summary_count` | integer | yes | Number of summaries included. |
| `audit_log_entry_count` | integer | yes | Number of audit log entries included. |
| `total_size_bytes` | integer | yes | Uncompressed total size of all included payloads, in bytes. |
| `content_address` | string | yes | Content-addressable hash of the canonicalized bundle. |
| `parent_snapshot_id` | string (UUID) | no | For incremental snapshots, the snapshot this is a delta of. |
| `included_paths` | array of string | yes | Source paths included in the snapshot. |
| `excluded_paths` | array of string | no | Source paths explicitly excluded. |
| `compression` | `Compression` object | yes | Compression algorithm and parameters. |
| `encryption` | `Encryption` object | yes | Encryption algorithm and key reference. |
| `integrity_hash` | string | yes | sha256 of the canonicalized manifest and payload bundle. |
| `integrity_verified` | boolean | yes | Whether integrity was verified at write time. |
| `provenance` | `Provenance` object | yes | Provenance metadata. |

### `Compression` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `algorithm` | string | yes | `none`, `gzip`, `zstd`, or `lz4`. |
| `level` | integer | no | Compression level (algorithm-specific). |
| `compressed_size_bytes` | integer | yes | Total compressed size, in bytes. |

### `Encryption` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `algorithm` | string | yes | `none`, `aes-256-gcm`, or `chacha20-poly1305`. |
| `key_reference` | string | yes | Opaque reference to the key used (never the key itself). |
| `nonce` | string | no | Nonce or IV, base64 encoded. Required when algorithm is not `none`. |
| `aad` | string | no | Additional authenticated data, base64 encoded, if any. |

### `Provenance` Object

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `producer` | string | yes | The subsystem that produced the snapshot. |
| `producer_version` | string | yes | The version of the producer. |
| `produced_at` | string (ISO 8601) | yes | When the snapshot was produced. |
| `parent_ids` | array of string | no | IDs of records this was derived from (snapshots and the parent snapshot, if any). |
| `trigger` | string | yes | What triggered the snapshot (user, schedule, pre_upgrade, pre_migration, manual). |
| `notes` | string | no | Free-form notes. |

## Snapshot Types

| `snapshot_type` | Description |
| --- | --- |
| `full` | A complete capture of all memory state. Self-contained; no `parent_snapshot_id` required. |
| `incremental` | A delta against `parent_snapshot_id`. Restoring requires chaining back to a `full` snapshot. |
| `named` | A user-tagged snapshot (e.g., "before refactor", "year-end state"). Always `full`. |
| `scheduled` | Produced by the snapshot scheduler on a cadence. Always `full`. |
| `pre_upgrade` | Automatically taken before a SELF version upgrade. Always `full`. |
| `pre_migration` | Automatically taken before a storage or substrate migration. Always `full`. |

## Storage Substrate Versions

The `storage_substrate_versions` object maps each storage substrate name to its semver at snapshot time. Known keys include:

- `event_store` — the substrate backing observation events.
- `knowledge_store` — the substrate backing knowledge objects (DuckDB).
- `vector_store` — the substrate backing embeddings.
- `summary_store` — the substrate backing summaries.
- `audit_log` — the substrate backing the audit log.
- `raw_artifact_store` — the content-addressable raw artifact store.

Unknown keys are permitted to accommodate new substrates added in future SELF versions.

## JSON Example

```json
{
  "schema_version": "0.1.0",
  "id": "ms_01HZX3R8P3K4N5M6Q7R8S9T0V1",
  "type": "memory_snapshot",
  "name": "year-end-2026",
  "description": "Full snapshot taken at the close of 2026 for archival.",
  "snapshot_type": "full",
  "created_at": "2026-12-31T23:59:00.000Z",
  "system_version": "0.7.4",
  "storage_substrate_versions": {
    "event_store": "0.3.1",
    "knowledge_store": "0.4.2",
    "vector_store": "0.2.0",
    "summary_store": "0.1.5",
    "audit_log": "0.1.0",
    "raw_artifact_store": "0.2.1"
  },
  "event_count": 148293,
  "knowledge_object_count": 18472,
  "summary_count": 612,
  "audit_log_entry_count": 89321,
  "total_size_bytes": 1784290304,
  "content_address": "sha256:9f3c1a8b7d2e4f6a0c5b8d1e3f7a9c2b4d6e8f0a1c3b5d7e9f1a3c5b7d9e1f3a",
  "parent_snapshot_id": null,
  "included_paths": [
    "events/",
    "knowledge/",
    "summaries/",
    "audit/",
    "embeddings/"
  ],
  "excluded_paths": [
    "knowledge/redacted/"
  ],
  "compression": {
    "algorithm": "zstd",
    "level": 9,
    "compressed_size_bytes": 612438912
  },
  "encryption": {
    "algorithm": "aes-256-gcm",
    "key_reference": "keyref:user:main:7c1a",
    "nonce": "Y2Jhc2U2NA==",
    "aad": "c25hcHNob3Q6eWVhci1lbmQtMjAyNg=="
  },
  "integrity_hash": "sha256:1a2b3c4d5e6f70819a2b3c4d5e6f70819a2b3c4d5e6f70819a2b3c4d5e6f7081",
  "integrity_verified": true,
  "provenance": {
    "producer": "memory.snapshot_manager",
    "producer_version": "0.1.0",
    "produced_at": "2026-12-31T23:59:00.000Z",
    "parent_ids": [],
    "trigger": "scheduled",
    "notes": "End-of-year scheduled full snapshot."
  }
}
```

## Validation Requirements

- All required fields must be present and non-null.
- `type` must equal `memory_snapshot`.
- `schema_version` must equal the current version (or a supported prior version).
- `id` must be a valid UUID.
- `name` must be non-empty and at most 256 characters.
- `snapshot_type` must be one of: `full`, `incremental`, `named`, `scheduled`, `pre_upgrade`, `pre_migration`.
- `system_version` must be a valid semver string (`MAJOR.MINOR.PATCH`, optionally with prerelease and build metadata).
- `storage_substrate_versions` must contain semver values for every known substrate.
- `event_count`, `knowledge_object_count`, `summary_count`, `audit_log_entry_count`, `total_size_bytes` must be non-negative integers.
- `total_size_bytes` must be greater than or equal to the sum of included payload sizes.
- `content_address` must be unique across all known snapshots.
- `integrity_hash` must be non-empty and use a recognized algorithm prefix (e.g., `sha256:`).
- `integrity_verified` must be `true` for any snapshot accepted into the snapshot registry.
- If `snapshot_type` is `incremental`, `parent_snapshot_id` is required and must reference an existing snapshot.
- If `snapshot_type` is `full`, `named`, `scheduled`, `pre_upgrade`, or `pre_migration`, `parent_snapshot_id` must be `null`.
- `compression.algorithm` must be one of: `none`, `gzip`, `zstd`, `lz4`.
- `compression.compressed_size_bytes` must be non-negative and less than or equal to `total_size_bytes` when `algorithm` is not `none`.
- `encryption.algorithm` must be one of: `none`, `aes-256-gcm`, `chacha20-poly1305`.
- `encryption.key_reference` must be non-empty and must never contain key material.
- If `encryption.algorithm` is not `none`, `encryption.nonce` is required.
- `included_paths` must be non-empty; `excluded_paths` must not overlap with `included_paths`.
- `created_at` and `provenance.produced_at` must be valid ISO 8601 strings in UTC.
- `provenance.producer` must be non-empty.
- `provenance.trigger` must be one of: `user`, `schedule`, `pre_upgrade`, `pre_migration`, `manual`.

## Versioning Strategy

Schemas are versioned semantically:

- **Major** version bump: a breaking change to the manifest schema or the on-disk bundle layout. Snapshots written under the old major version are not guaranteed to be readable by the new implementation. Migration tools are required.
- **Minor** version bump: a backwards-compatible addition (e.g., a new optional field, a new substrate key). Old snapshots remain readable.
- **Patch** version bump: a documentation or example fix. No schema or layout change.

The current version is recorded in the `schema_version` field of every manifest. Implementations must support reading the current version and the immediately prior major version. Older versions are migrated on read.

When a new version is introduced:

1. The new schema is documented in this file.
2. A migration tool is provided in `tools/snapshot_migrate/`.
3. The new version is announced in the changelog.
4. A deprecation notice is added to the old version.
5. After one major version cycle, the old version is no longer supported.

`storage_substrate_versions` allows each substrate to evolve independently. A substrate format change requires a major version bump of that substrate, and the snapshot's `system_version` plus substrate versions together determine the migration path on restore.

## Storage Considerations

Snapshots are stored on the filesystem in a content-addressable layout:

```
snapshots/
  ab/
    cd/
      abcd1234.../
        manifest.json
        bundle.bin          (the encrypted, compressed payload)
        index.json          (substrate -> offset/offset+length map)
        signatures/         (optional detached signatures)
```

The manifest (`manifest.json`) is the canonicalized JSON defined by this schema, with `content_address` derived from its canonical form. The bundle (`bundle.bin`) is the encrypted and compressed concatenation of the included substrate payloads, framed by the index.

Metadata about each snapshot — including `id`, `name`, `snapshot_type`, `created_at`, `content_address`, `parent_snapshot_id`, `total_size_bytes`, `compression.compressed_size_bytes`, and `integrity_verified` — is mirrored into the DuckDB snapshot registry for fast lookup, listing, and policy enforcement. The filesystem remains the source of truth; the registry is a derived index.

Incremental snapshots chain back to a `full` snapshot. Restoring an incremental snapshot reconstructs state by applying each link in the chain from the base. Chains are validated at write time: a missing or corrupted link in the chain causes the entire chain to be rejected on restore.

Retention is policy-driven. The Snapshot Manager enforces user-configured retention rules (e.g., keep last 7 daily, 4 weekly, all named, all pre_upgrade, all pre_migration). Expired snapshots are garbage-collected only after their content address is no longer referenced by any other snapshot or by the live memory state.

## Privacy Considerations

A memory snapshot contains the full privacy-sensitive contents of the user's memory. Implementations must:

- Encrypt snapshots at rest with user-held keys. The `encryption.key_reference` is an opaque pointer to a key held in the user's keychain or secret store; key material is never stored in the manifest.
- Refuse to write unencrypted snapshots (`encryption.algorithm = none`) unless the user has explicitly opted in and the snapshot is staying on-device.
- Honor the privacy settings that were in effect at the time of snapshot creation. A snapshot taken with a record redacted remains redacted in the snapshot, even if privacy settings later change.
- Cascade deletion. When a snapshot is deleted, all bundles, indices, signatures, and registry entries referencing it are removed. Incremental chains that depend on the deleted snapshot are also removed.
- Require explicit user consent before exporting or uploading a snapshot off-device.
- Never log snapshot content, key references, or nonces in plain text outside the system.
- Support a "scrub" operation that overwrites a snapshot's bundle on disk with random bytes before unlinking it, for users on storage that may not honor unlink.

See `security/privacy_model.md` and `security/key_management.md`.
