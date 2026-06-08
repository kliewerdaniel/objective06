# Storage Interface

This interface defines how SELF interacts with its storage substrates. Subsystems never talk to the databases directly; they use this interface.

## Purpose
To decouple the system's logic from the specific database technologies used. This allows for swapping storage engines (e.g., switching from DuckDB to Postgres) without changing subsystem code.

## Substrates
- **Analytical (DuckDB)**: Used for querying observation events and knowledge objects. Supports SQL-like queries and efficient aggregation.
- **Graph (Kuzu / Neo4j)**: Used for the identity graph. Supports complex relationship traversals.
- **Vector (e.g., Qdrant, Milvus, Chroma)**: Used for semantic search and persona vector storage. Supports similarity search.
- **Filesystem**: Used for raw artifacts, snapshots, logs, and configuration.

## Core Operations
- **Write**: Save new entities, events, or knowledge objects.
- **Read**: Retrieve data by ID, query by filters (time, source, type), or perform complex traversals.
- **Update**: Modify existing objects (with audit logging).
- **Delete**: Remove data (with propagation checks).
- **Snapshot**: Export the entire state of a particular substrate.

## Governance
- **Provenance**: Every write operation must include provenance information.
- **Auditability**: All mutations must be recorded in a centralized audit log.
- **Locality**: All substrates must reside on the user's local hardware by default.
- **Data Integrity**: Ensure transactions are atomic where possible (especially for graph and analytical stores).

## Implementations
- **DuckDBAdapter**
- **KuzuAdapter**
- **VectorDBAdapter**
- **FileSystemAdapter**
