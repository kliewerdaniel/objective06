# Storage Subsystem

> The Storage subsystem defines the interfaces and implementations for the durable substrates of SELF: DuckDB for analytical state, Kuzu or Neo4j for graph state, a vector database for semantic retrieval, and the filesystem for raw artifacts.

---

## Purpose

The Storage subsystem is the substrate abstraction layer of SELF. It hides the details of how data is stored, indexed, queried, and retrieved behind a stable interface. No other subsystem talks to a database, a vector store, or a filesystem directly. They all go through Storage.

The Storage subsystem is also the place where substrate choices are made. SELF uses:

- **DuckDB** for analytical queries over observation events and knowledge objects.
- **Kuzu or Neo4j** for the identity graph.
- **A vector database** (FAISS, sqlite-vss, Qdrant, or compatible) for semantic retrieval.
- **The filesystem** for raw artifacts, snapshots, configuration, and logs.

These choices are documented in `decisions/`. They are not permanent. The Storage subsystem is designed to allow replacement of any substrate without rewriting the subsystems that depend on it.

## Responsibilities

- Defining the Storage API used by all other subsystems.
- Implementing the Storage API on top of the chosen substrates.
- Managing connections, transactions, and migrations.
- Enforcing schema validation on writes.
- Providing query planning and execution.
- Implementing backup, restore, and export.
- Surfacing storage-level metrics.
- Supporting substrate migration.

## Inputs

- Read queries (by ID, by time, by entity, by type, by semantic similarity, by graph pattern).
- Write operations (insert, update, delete with provenance).
- Schema migration commands.
- Backup and restore commands.
- Configuration (paths, credentials, retention).

## Outputs

- Query results.
- Confirmation of writes.
- Snapshot artifacts.
- Export bundles.
- Metrics: storage size, query latency, throughput.

## Dependencies

The Storage subsystem depends on the chosen substrate libraries. It does not depend on any other SELF subsystem. It is the lowest layer.

## Substrate: DuckDB

DuckDB is the analytical store for SELF. It holds:

- `observation_event` records.
- `knowledge_object` records.
- `summary` records.
- Audit log entries.
- Persona vector metadata (the vectors themselves live in the vector store; the metadata lives in DuckDB).

DuckDB is chosen for:

- Embedded operation (no separate server).
- Excellent analytical query performance.
- Columnar storage.
- Strong support for time-range and aggregation queries.
- Easy backup as a single file.

See `decisions/ADR-004-duckdb.md`.

## Substrate: Kuzu or Neo4j

The graph store for the Identity Graph. It holds:

- Identity nodes.
- Identity edges.
- Temporal annotations.

Kuzu is the default. Neo4j is supported as an alternative. The choice between them is documented in `decisions/`. Either way, the graph store is accessed through the Identity Graph subsystem, not directly.

## Substrate: Vector Database

A vector store for semantic retrieval. It holds:

- Embeddings of knowledge objects.
- Embeddings of summaries.
- Embeddings of observation events (optional).
- The persona vector history.

The default is FAISS (file-based, embedded) with optional sqlite-vss. The interface is designed to be compatible with Qdrant, Weaviate, and pgvector.

## Substrate: Filesystem

The filesystem is used for:

- Raw observation payloads (content-addressable).
- Snapshots.
- Configuration.
- Logs.
- Backups.

Filesystem layout is documented in `interfaces/filesystem.md`.

## Internal Components

### Storage API

The single API used by all subsystems. The API is defined by:

- Type definitions in the implementation.
- Schema definitions in `schemas/`.
- This document.

The API is intentionally narrow:

- `get(id)` — retrieve by ID.
- `query(spec)` — retrieve by specification.
- `insert(record)` — write a record.
- `update(id, changes)` — update a record.
- `delete(id)` — delete a record (rare, always audited).
- `traverse(pattern)` — graph traversal (delegated to graph store).
- `search(vector, k)` — semantic search.
- `snapshot(name)` — create a snapshot.
- `restore(snapshot_id)` — restore from a snapshot.
- `export(target)` — export the storage state.
- `import(source)` — import a previous export.

### Substrate Adapters

One adapter per substrate. Each adapter:

- Translates Storage API calls into substrate-specific calls.
- Handles connection management.
- Handles transactions.
- Reports substrate-level metrics.

### Connection Manager

Manages connections to substrates. The manager:

- Pools connections where appropriate.
- Detects connection failures.
- Reconnects with backoff.
- Surfaces connection state to the Orchestration layer.

### Transaction Coordinator

Coordinates transactions across substrates where needed. The coordinator:

- Implements two-phase commit where supported.
- Implements best-effort commit where not.
- Records transaction outcomes in the audit log.

### Migration Engine

Handles schema migrations. The migration engine:

- Reads migration scripts.
- Validates against current schema version.
- Applies migrations in order.
- Supports rollback (where possible).
- Records every migration in the audit log.

### Schema Validator

Validates records against schemas before write. The validator:

- Rejects invalid records with structured error messages.
- Logs validation failures.
- Supports per-record schema versioning.

### Backup Manager

Handles backups. The backup manager:

- Creates full and incremental backups.
- Verifies backup integrity.
- Encrypts backups at the user's option.
- Stores backups to user-specified destinations.
- Supports scheduled and on-demand backups.

### Substrate Monitor

Monitors substrate health. The monitor:

- Tracks query latency, error rates, and resource usage per substrate.
- Detects anomalies.
- Triggers failovers where configured.
- Reports metrics.

## Data Contracts

Storage implements the persistence half of every schema in `schemas/`. Subsystems see records as schema-conformant Python objects (or the language equivalent). They do not see SQL, Cypher, FAISS calls, or file paths.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Substrate unavailable | Connection error | Retry, alert, degrade. |
| Schema validation failure | Validator | Reject, log. |
| Migration failure | Migration log | Roll back, alert. |
| Disk full | Write error | Halt, alert. |
| Backup failure | Backup log | Retry, alert. |
| Transaction conflict | Coordinator | Retry, log. |
| Corruption | Integrity check | Restore from snapshot, alert. |

## Metrics

- `storage.substrate_size_bytes` (per substrate)
- `storage.query_latency_ms` (per substrate, per operation)
- `storage.write_throughput` (per substrate)
- `storage.cache_hit_rate`
- `storage.backup_age_hours`
- `storage.migration_pending`

## Future Evolution

- **Tiered storage.** Hot, warm, cold, archive tiers.
- **Multi-region replication.** For users running SELF on multiple machines.
- **Encrypted at rest.** Optional user-controlled encryption with user-held keys.
- **Compression strategies.** Adaptive compression based on access patterns.
- **Cross-substrate queries.** Queries that span DuckDB, the graph store, and the vector store in a single call.

## Edge Cases

- **Substrate migration during operation.** A substrate change (e.g., DuckDB to ClickHouse) must support online migration with zero data loss.
- **Concurrent writes.** Multiple subsystems may write concurrently; the storage layer enforces serialization.
- **Schema evolution.** Records written under an older schema must be readable under a newer one.
- **Backup during heavy load.** Backups must not block writes.
- **Substrate failure cascade.** A failure in one substrate must not propagate to others.

## Acceptance Criteria for "Storage is Complete"

1. All substrate adapters are implemented and tested.
2. The Storage API covers all subsystem needs.
3. Schema validation is enforced on every write.
4. Backups can be created, verified, and restored.
5. Substrate health is monitored and metrics are emitted.
6. Storage survives a substrate restart without data loss.
7. Evaluation: `evaluations/memory_retrieval.md` passes (since memory is layered on top of storage).
