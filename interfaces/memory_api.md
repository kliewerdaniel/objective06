# Memory API

> The Memory API is the unified interface for reading and writing all durable state in SELF. Every subsystem uses this API to interact with storage; direct database access from other subsystems is prohibited.

## Purpose

The Memory API provides a single, stable interface for:
- Storing observation events, knowledge objects, and summaries
- Retrieving records by ID, time range, entity, type, or semantic similarity
- Counting records by type
- Coordinating audit log entries on every state change

## Interface

### Write Operations

```python
def store_event(event: dict[str, Any]) -> str
```
Stores an observation event. Returns the event ID. Automatically appends an audit log entry.

```python
def store_knowledge(ko: dict[str, Any]) -> str
```
Stores a knowledge object. Returns the knowledge object ID. Automatically appends an audit log entry.

```python
def store_summary(summary: dict[str, Any]) -> str
```
Stores a summary. Returns the summary ID. Automatically appends an audit log entry.

### Read Operations

```python
def get_event(event_id: str) -> dict[str, Any] | None
```
Retrieves a single observation event by ID. Returns `None` if not found.

```python
def get_knowledge(ko_id: str) -> dict[str, Any] | None
```
Retrieves a single knowledge object by ID. Returns `None` if not found.

```python
def query_events(spec: dict[str, Any] | None = None) -> list[dict[str, Any]]
```
Queries observation events by specification (time range, source, type). Returns all events if no spec is provided.

```python
def query_knowledge(spec: dict[str, Any] | None = None) -> list[dict[str, Any]]
```
Queries knowledge objects by specification (type, entity, confidence). Returns all knowledge objects if no spec is provided.

### Semantic Search

```python
def semantic_search(query_vector: list[float], k: int = 10) -> list[dict[str, Any]]
```
Performs k-nearest-neighbor search over the vector index. Returns up to `k` results. Returns empty list if no vector index is configured.

### Count Operations

```python
event_count: int
knowledge_count: int
audit_count: int
```
Read-only properties returning record counts by type.

## Implementation

The canonical implementation is `src/self/memory.py`. It delegates to the Storage subsystem for persistence and the Audit Log for provenance tracking. The Memory API object is the only way to write to or read from the system's durable state.

## Governance

- **Provenance**: Every write operation records an audit log entry with actor, action, entity type, entity ID, and reason.
- **Immutability**: Observation events are append-only once stored. Knowledge objects and summaries may be updated.
- **Schema Validation**: All records are validated against the schema definitions in `schemas/` before storage.
