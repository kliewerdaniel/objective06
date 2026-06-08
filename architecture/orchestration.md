# Orchestration Subsystem

> The Orchestration subsystem is the spine of SELF. It owns the main loop, schedules subsystems, handles retries and backpressure, and owns the audit log.

---

## Purpose

Orchestration is the subsystem that makes the rest of SELF work together. It is the only subsystem that:

- Knows about every other subsystem.
- Schedules subsystem work.
- Handles failures and retries.
- Owns the audit log.
- Owns the lifecycle of the system as a whole.

The Orchestration layer is the system's central nervous system. It does not interpret data; it routes work. It does not store state; it persists the audit log. It does not make decisions about the user; it makes decisions about the system.

The Orchestration layer is the only subsystem that should run in a privileged context. All other subsystems are invoked by Orchestration and have no autonomous agency.

## Responsibilities

- Owning the main loop.
- Scheduling subsystem work (recurring, triggered, on-demand).
- Routing events between subsystems.
- Handling retries with exponential backoff.
- Managing backpressure and resource budgets.
- Owning the audit log.
- Owning the lifecycle (start, stop, restart, upgrade).
- Surfacing system health to the user.
- Coordinating graceful degradation.
- Coordinating with external processes (when applicable).

## Inputs

- Configuration: schedules, retry policies, resource budgets.
- Triggers from other subsystems (e.g., "a new knowledge object was created").
- Triggers from external sources (e.g., a scheduled cron).
- Triggers from the user.
- Health signals from other subsystems.
- The audit log (read for debugging, never modified directly by anyone but Orchestration).

## Outputs

- Invocations of other subsystems.
- Audit log entries.
- Health and status reports.
- Notifications to the user.
- Metrics: subsystem latencies, queue depths, error rates, resource usage.

## Dependencies

The Orchestration layer depends on:

- The Storage subsystem (for the audit log).
- The Configuration subsystem (for schedules and policies).
- The Security subsystem (for permission checks).
- All other subsystems (to invoke them).

Orchestration does not depend on the user's data. It is metadata-only.

## Internal Components

### Main Loop

The continuous loop that drives SELF. The main loop:

- Sleeps for a configurable interval (default 100ms).
- Wakes up and processes pending work.
- Dispatches work to subsystems.
- Handles responses and failures.
- Records everything in the audit log.

The main loop is single-threaded by default but supports worker pools for parallel subsystems.

### Scheduler

Schedules subsystem work. The scheduler:

- Supports cron-like expressions.
- Supports interval-based scheduling.
- Supports trigger-based scheduling (event X causes subsystem Y to run).
- Supports one-shot and recurring schedules.
- Honors user-configured quiet hours and resource budgets.

### Event Bus

A pub/sub mechanism for inter-subsystem communication. The event bus:

- Supports topics (e.g., `knowledge.created`, `action.completed`).
- Supports multiple subscribers per topic.
- Supports delivery guarantees (at-least-once, at-most-once).
- Persists events for replay.
- Is itself auditable.

### Retry Manager

Manages retries for failed operations. The retry manager:

- Implements exponential backoff with jitter.
- Honors maximum retry counts.
- Distinguishes between transient and permanent failures.
- Records retry attempts in the audit log.
- Supports manual intervention.

### Backpressure Manager

Monitors and enforces resource budgets. The backpressure manager:

- Tracks CPU, memory, disk, and network usage.
- Tracks per-subsystem queue depths.
- Throttles work when budgets are exceeded.
- Surfaces backpressure events to the user.
- Supports user-defined budgets.

### Audit Logger
Owns the audit log. The audit logger:

- Records every state change.
- Records every action.
- Records every subsystem invocation and result.
- Is append-only.
- Supports queries.
- Supports integrity verification via hash-chaining. Each audit log entry includes a `prev_hash` field containing the SHA-256 of the previous entry's canonical JSON. The log head hash is stored in a separate, user-readable `audit_head.sha256` file updated atomically on each write. Integrity verification reads the chain from any entry forward, recomputing hashes.

### Write Queue
A serializing queue for UPDATE and DELETE operations issued to DuckDB. All subsystems enqueue writes rather than calling the Storage API directly for mutations. Appends bypass the queue.

### Lifecycle Manager


Owns the system's lifecycle. The lifecycle manager:

- Handles start, stop, restart.
- Handles graceful shutdown.
- Handles crash recovery.
- Handles upgrades.
- Handles migrations.
- Honors shutdown signals from the user.

### Health Monitor

Monitors subsystem health. The health monitor:

- Collects heartbeats.
- Tracks per-subsystem metrics.
- Detects stuck or failing subsystems.
- Triggers recovery actions.
- Surfaces status to the user.

### Configuration Manager

Owns configuration. The configuration manager:

- Loads configuration from disk.
- Validates configuration.
- Supports hot-reload of safe configuration.
- Records configuration changes in the audit log.
- Supports per-user configuration.

### Notification Manager

Notifies the user of important events. The notification manager:

- Honors user preferences (channels, quiet hours).
- Distinguishes informational from actionable.
- Aggregates notifications to avoid spam.
- Logs every notification.
- Supports "do not disturb" mode.

## Data Contracts

The Orchestration layer produces:

- `audit_log_entry` records (see `security/auditability.md`).
- `health_status` records.
- `notification` records.
- `schedule` records.

The Orchestration layer consumes configuration only. It does not consume user data directly.

## Main Loop

The main loop is the heart of SELF. It runs continuously while the system is active.

```
loop:
    now = current_time()
    due_work = scheduler.pop_due(now)
    for work in due_work:
        invoke_subsystem(work)
    pending_events = event_bus.pop_pending()
    for event in pending_events:
        route_event(event)
    health = collect_health()
    if health.degraded:
        handle_degradation(health)
    backpressure = check_backpressure()
    if backpressure.exceeded:
        apply_backpressure(backpressure)
    sleep(config.loop_interval)
```

The loop interval is configurable. A shorter interval means more responsive but more CPU. A longer interval means less responsive but less load. The default is 100ms.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Subsystem crash | Heartbeat miss | Restart, replay from checkpoint, log. |
| Storage failure | Storage error | Halt main loop, alert, await recovery. |
| Audit log failure | Write error | Halt system, alert. Audit log is non-negotiable. |
| Scheduler failure | Schedule timeout | Re-invoke, log. |
| Event bus overflow | Queue depth | Drop oldest, log, alert. |
| Resource exhaustion | Backpressure trigger | Throttle, alert. |
| User-initiated stop | Signal | Graceful shutdown. |

## Metrics

- `orchestrator.loop_iterations.total`
- `orchestrator.subsystem_invocations.total` (by subsystem, by outcome)
- `orchestrator.queue_depths` (per queue)
- `orchestrator.retry_rate`
- `orchestrator.audit_log_size`
- `orchestrator.resource_usage` (CPU, memory, disk, network)
- `orchestrator.uptime_seconds`

## Future Evolution

- **Distributed orchestration.** Run multiple SELF instances coordinated by a leader.
- **Cloud-hybrid orchestration.** Offload heavy work to a remote accelerator with consent.
- **Self-tuning schedules.** The scheduler learns optimal cadences.
- **Speculative execution.** Pre-compute likely next states.

## Edge Cases

- **Clock skew.** The scheduler uses monotonic time for ordering, wall-clock for human-readable timestamps.
- **Concurrent invocations.** The Orchestration layer must prevent the same scheduled work from running twice.
- **Long-running subsystems.** A subsystem may run for hours. The Orchestration layer must not block on it.
- **Subsystem cancellation.** The Orchestration layer must be able to cancel a long-running subsystem.
- **Replay after crash.** The Orchestration layer must be able to replay pending work after a crash without duplicating completed work.

## Acceptance Criteria for "Orchestration is Complete"

1. The main loop runs continuously and survives crashes.
2. Schedules fire on time, within the configured tolerance.
3. The audit log records every state change and action.
4. Retries honor exponential backoff and max retry counts.
5. Backpressure prevents resource exhaustion.
6. The system can be stopped and started cleanly.
7. Health is observable to the user at all times.
