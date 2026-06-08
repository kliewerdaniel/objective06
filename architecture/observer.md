# Observer Subsystem

> The Observer captures raw activity from the user's digital environment and emits immutable observation events. It is the input layer of SELF.

---

## Purpose

The Observer is responsible for detecting, collecting, and normalizing activity from the user's digital surfaces and emitting structured `observation_event` records. It is the only subsystem that interacts directly with external data sources. It does not interpret; it records.

The Observer is always running while SELF is active. It must never lose data, must never modify source data, and must never block the user's primary tools.

## Responsibilities

- Watching configured sources (filesystem, git, GitHub, RSS, email, browser, terminal, markdown).
- Detecting changes, additions, deletions, and actions.
- Normalizing source-specific payloads into a common `observation_event` shape.
- Timestamping events with monotonic and wall-clock times.
- Persisting events to the durable event log.
- Retrying failed ingestion with exponential backoff.
- Respecting source-side rate limits and privacy controls.
- Providing a backfill mechanism for historical data.

## Inputs

The Observer has two categories of inputs:

### 1. Source Streams

These are external, source-specific event or polling interfaces:

- Filesystem inotify / FSEvents / ReadDirectoryChangesW events.
- Git hooks (post-commit, post-checkout, post-merge).
- GitHub webhooks and REST/GraphQL polling.
- RSS / Atom feed polling responses.
- IMAP / Gmail API message events.
- Browser history sync (Chrome, Firefox, Safari).
- Terminal session log streams.
- Markdown file change events.

### 2. Configuration

The Observer receives a configuration describing:

- Which sources are enabled.
- For each source, which paths, repositories, accounts, or feeds to watch.
- For each source, the polling interval or trigger mode.
- For each source, retention and privacy settings.
- Backfill windows.

## Outputs

The Observer emits:

- `observation_event` records conforming to `schemas/observation_event.md`.
- Heartbeat records indicating liveness.
- Error records for failed ingestion attempts.
- Metrics: events per minute, queue depth, source health.

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Storage (filesystem + DuckDB) | Required | Durable event log. |
| Orchestration | Required | Schedule, monitoring, lifecycle. |
| Security | Required | Permission checks, secret handling. |
| Source-specific adapters | Required | One per source type (see `interfaces/`). |

## Internal Components

### Source Adapters

One adapter per source type. Each adapter:

- Knows how to connect to its source (file path, API endpoint, IMAP server).
- Polls or subscribes as appropriate.
- Translates source-specific events into the common `observation_event` shape.
- Handles authentication and re-authentication.
- Surfaces source health.

### Normalizer

A central component that takes adapter output and produces canonical `observation_event` records. The normalizer:

- Assigns stable IDs.
- Resolves timestamps to a consistent time base (UTC).
- Strips source-specific noise.
- Computes content hashes.
- Attaches provenance metadata.

### Ingest Queue

A bounded, persistent queue between adapters and the storage layer. The queue:

- Decouples source volatility from storage performance.
- Survives process restarts.
- Supports priority lanes (e.g., user-initiated actions before background syncs).
- Emits backpressure signals to adapters.

### Event Log Writer

Writes normalized events to the durable event log. The writer:

- Is transactional.
- Is append-only.
- Uses content-addressable storage for event payloads.
- Maintains a separate index for fast lookups by source, time, and entity.

### Backfill Engine

A component that performs historical ingestion. The backfill engine:

- Walks sources for historical events.
- Respects rate limits.
- Is pauseable and resumable.
- Is idempotent.

### Health Monitor

Tracks the liveness and health of each adapter. Emits alerts on:

- Stale sources (no events for too long).
- Repeated ingestion failures.
- Queue overflow.
- Authentication expiry.

## Data Contracts

The Observer's primary output is the `observation_event` schema. The Observer is also responsible for emitting:

- `source_health` records.
- `ingest_error` records.
- `backfill_progress` records.

All of these share the same provenance pattern as other SELF objects.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Source unavailable | Adapter health check | Retry with backoff, log, surface to user. |
| Authentication expired | Adapter returns 401/403 | Pause adapter, notify user, await re-auth. |
| Queue overflow | Queue depth threshold | Throttle new events from over-producing sources. |
| Disk full | Write failure | Halt writes, alert user, refuse new observations. |
| Schema mismatch | Validator error | Quarantine event, log, alert. |
| Clock skew | Timestamp comparison | Use monotonic time for ordering, log skew. |
| Adapter crash | Heartbeat miss | Restart adapter, replay from last checkpoint. |

## Metrics

- `observer.events_emitted.total` (counter, by source)
- `observer.events_dropped.total` (counter, by reason)
- `observer.queue_depth` (gauge)
- `observer.adapter_uptime` (gauge, by source)
- `observer.latency_p95_ms` (gauge, by source)
- `observer.backfill_progress` (gauge, by source)

## Future Evolution

- **Streaming ingestion over polling.** Where possible, replace polling with streaming.
- **Active probing.** Beyond reactive observation, the Observer may probe sources to detect silent changes.
- **Cross-source dedup.** Identify the same event reported by multiple sources.
- **Privacy filtering at the edge.** Strip sensitive content before it leaves the source adapter, configurable per source.
- **Differential privacy for shared contexts.** If the user opts into sharing anonymized patterns, support privacy-preserving aggregation.

## Edge Cases

- **Time travel.** When the system clock changes, the Observer must reconcile.
- **Concurrent modifications.** When a file is modified while being read, the Observer must produce a consistent event.
- **Permission revocation.** When the user revokes access to a source, in-flight events must complete or be cancelled cleanly.
- **Source schema changes.** When a source (e.g., GitHub API) changes shape, the adapter must version itself and migrate.

## Acceptance Criteria for "Observer is Complete"

1. All adapters listed in `interfaces/` are implemented and pass their unit tests.
2. The ingest queue survives process crashes without data loss.
3. Backfill works for at least one source end-to-end.
4. Heartbeat and health metrics are emitted and consumable by the Orchestration layer.
5. Privacy filters can be configured per source and are enforced at the adapter.
6. The Observer is documented in `interfaces/` for every supported source.
7. Evaluation: `evaluations/discover_project.md` is unblocked by the Observer.
