# Phase 02: Observation

## Status
- **Current Status:** Pending
- **Completion:** 0%

## Overview
Phase 02 focuses on building the Observer subsystem, which is the primary data ingestion layer for SELF. This phase establishes the ability to capture raw events from the user's digital environment.

## Objectives
- Implement the Observer subsystem.
- Develop source-specific adapters (Filesystem, Git, etc.).
- Implement the Normalizer to produce canonical `observation_event` records.
- Implement the Ingest Queue for decoupled processing.
- Implement the Event Log Writer for durable storage.
- Establish basic health monitoring for adapters.

## Deliverables
- [ ] Observer subsystem architecture and schema integration.
- [ ] Filesystem Watcher adapter.
- [ ] Git hook adapter.
- [ ] GitHub Poller adapter.
- [ ] Normalizer implementation.
- [ ] Ingest Queue implementation.
- [ ] Event Log Writer implementation.
- [ ] Basic health metrics and alerts.
- [ ] Build evaluation harness for evaluations/discover_project.md.

## Dependencies
- Phase 01: Foundation (Storage, Audit Logs).

## Risks
- **Permission handling:** Ensuring adapters respect user-defined privacy boundaries.
- **Rate limiting:** Managing API limits for external sources like GitHub.

## Success Criteria
- The system can observe and record changes in a local filesystem.
- The system can observe and record commits in a local git repository.
- `observation_events` are correctly normalized and stored in DuckDB.
- Metrics show event ingestion rates and queue depths.
