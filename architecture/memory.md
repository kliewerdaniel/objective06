# Memory Subsystem

> The Memory subsystem is the durable substrate of SELF. It stores observation events, knowledge objects, summaries, and the audit log, and provides retrieval interfaces by ID, by time, by graph traversal, and by semantic similarity.

---

## Purpose

Memory is the long-term store of SELF. It is where observation events accumulate, where knowledge objects are written, where summaries are persisted, and where the audit log lives. It provides the retrieval primitives that every other subsystem depends on.

Memory is designed to be:

- **Append-mostly.** Writes are additions or updates with full provenance; nothing is silently lost.
- **Queryable.** Retrieval by ID, by time range, by graph traversal, by semantic similarity.
- **Durable.** Data survives crashes, restarts, and migrations.
- **Portable.** Data can be exported and reimported on another machine.
- **Auditable.** Every write is recorded in the audit log.

## Responsibilities

- Storing `observation_event` records.
- Storing `knowledge_object` records.
- Storing `summary` records.
- Storing the audit log.
- Storing `memory_snapshot` and `identity_snapshot` records.
- Providing retrieval APIs:
  - By primary key.
  - By time range.
  - By source, by entity, by type.
  - By semantic similarity (via the vector index).
  - By graph traversal (delegated to Identity Graph).
- Managing compaction, archival, and retention.
- Supporting export and import.
- Enforcing the schema validation gate.
- Maintaining the audit log.

## Inputs

- Writes from Observer (observation events).
- Writes from Extractor (knowledge objects, identity node updates).
- Writes from Identity Graph (node and edge records).
- Writes from Persona Engine (vector snapshots).
- Writes from Synthesis Engine (summaries).
- Writes from Action Engine (action records).
- Writes from Orchestration (audit log entries).
- Read queries from any subsystem.
- Configuration for retention, compaction, and storage paths.

## Outputs

- Stored records, accessible through the Memory API.
- Query results (events, knowledge, summaries).
- Snapshot artifacts.
- Export bundles.
- Metrics: storage size, query latency, compaction progress.

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Storage (DuckDB, filesystem) | Required | Primary and archival storage. |
| Vector Database | Required | Semantic retrieval. |
| Identity Graph | Required | Graph queries (logical). |
| Orchestration | Required | Scheduling of compaction, retention. |
| Security | Required | Access control, encryption. |

## Internal Components

### Event Store

Stores `observation_event` records. The event store:

- Is append-only at the storage layer.
- Supports time-range queries.
- Is partitioned by source and time for fast access.
- Maintains a content-addressable backing for raw payloads.
- Supports replay from a point in time.

### Knowledge Store

Stores `knowledge_object` records. The knowledge store:

- Indexes by type, by entity, by confidence.
- Supports full-text search over knowledge text.
- Supports semantic search via the vector index.
- Preserves all historical versions of mutable knowledge.

### Summary Store

Stores `summary` records. The summary store:

- Is indexed by time, by topic, by entity.
- Carries provenance to underlying knowledge objects.
- Supports retrieval of "the summary that was generated on date X for entity Y."

### Audit Log

An append-only log of every state change in the system. The audit log:

- Is write-once.
- Includes: timestamp, actor, action, before-state-hash, after-state-hash, reason.
- Is queryable by actor, by action, by entity, by time.
- Is itself auditable: the user can verify that the log is intact.

### Vector Index

A semantic index over knowledge objects, summaries, and (optionally) raw events. The vector index:

- Is built incrementally as new knowledge arrives.
- Supports k-nearest-neighbor queries.
- Is rebuildable from the underlying records.
- Can be replaced (e.g., from FAISS to a managed service) without changing the interface.

### Snapshot Manager

Creates and restores `memory_snapshot` and `identity_snapshot` records. The snapshot manager:

- Produces consistent snapshots across stores.
- Supports point-in-time and named snapshots.
- Validates snapshots on restore.
- Tracks snapshot lineage.

### Compaction Engine

Compacts and archives data. The compaction engine:

- Merges small records into larger storage units.
- Moves cold data to archival storage.
- Respects retention policies.
- Is reversible within a configurable window.

### Retention Manager

Enforces retention policies. The retention manager:

- Removes data only after explicit policy expiration AND user consent.
- Logs every removal in the audit log.
- Supports per-source, per-type retention rules.

### Query Planner

Routes queries to the appropriate store. The query planner:

- Translates high-level queries into store-specific queries.
- Combines results from multiple stores.
- Caches results when appropriate.
- Enforces query budgets (cost, time).

### Exporter / Importer

Exports and imports the entire memory state. The exporter:

- Produces a portable, versioned archive.
- Includes all stores, indexes, and the audit log.
- Verifies integrity with checksums.
- Is resumable.

The importer:

- Validates the archive against schema versions.
- Migrates data if necessary.
- Verifies integrity after import.
- Reports any data that could not be imported.

## Data Contracts

Memory implements the storage half of every schema in `schemas/`. The Memory API is the only way other subsystems read or write data. Direct database access from other subsystems is prohibited.

The Memory API is described by:

- `interfaces/memory_api.md` (to be created during Phase 4).
- The schema definitions in `schemas/`.
- The type definitions in the implementation.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Disk full | Write error | Halt writes, alert, refuse new observations. |
| Index corruption | Validator | Rebuild from records. |
| Query timeout | Watchdog | Return partial result, log. |
| Snapshot integrity check failure | Hash mismatch | Refuse to restore, alert. |
| Compaction error | Compaction log | Roll back to last good state. |
| Audit log corruption | Integrity check | Halt system, alert. |
| Schema migration failure | Migration log | Roll back, alert. |
| Export / import error | Checksum mismatch | Halt, alert, allow resume. |

## Metrics

- `memory.size_bytes` (by store)
- `memory.records_total` (by store, by type)
- `memory.query_latency_ms` (p50, p95, p99)
- `memory.compaction_progress`
- `memory.audit_log_entries.total`
- `memory.vector_index_size`
- `memory.snapshot_count`

## Future Evolution

- **Tiered storage.** Hot, warm, cold, and archive tiers with different backends.
- **Distributed storage.** For users running SELF on multiple machines (not a primary use case, but possible).
- **Encrypted at rest.** Optional user-controlled encryption.
- **Time-travel queries.** Query the state of memory at any past point.
- **Cross-instance sync.** Sync two SELF installations (e.g., laptop and server).

## Edge Cases

- **Schema migration during operation.** Memory must support online migrations that do not require downtime.
- **Compaction during heavy read load.** Compaction must not block reads for extended periods.
- **Vector index drift.** When records are updated, the index must be updated consistently.
- **Audit log size.** The audit log grows unbounded; compression and archival strategies are required.
- **Time zone handling.** All timestamps are stored in UTC; conversion to local time is a presentation concern.
- **Concurrent writes.** Multiple subsystems may write concurrently; the storage layer must enforce serialization or use conflict-free replicated data types where appropriate.

## Acceptance Criteria for "Memory is Complete"

1. All schema records can be stored and retrieved.
2. Retrieval by ID, by time, by entity, by type, and by semantic similarity all work.
3. Snapshots can be created, validated, and restored.
4. Export and import round-trip a full memory state.
5. The audit log records every state change.
6. Compaction runs without data loss and is reversible.
7. Evaluation: `evaluations/memory_retrieval.md` passes.
