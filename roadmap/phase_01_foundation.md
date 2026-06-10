# Phase 01: Foundation

## Status
- **Current Status:** In Progress
- **Completion:** 10%

## Overview
Phase 01 focuses on the fundamental infrastructure required for all other subsystems. We are building the "scaffolding" that allows for a modular, scalable, and auditable system.

## Objectives
- Establish the project scaffolding (folders, basic build tools).
- Implement the Storage Substrates (DuckDB, LadybugDB (default) or Neo4j (enterprise fallback), Vector DB, Filesystem).
- Implement the primary Observability primitives (logging, metrics, audit logs).
- Define the core data schemas for the basic entities (Observation Event, Knowledge Object).
- Establish the CI/CD and local development environment.

## Deliverables
- [ ] Basic project structure and configuration.
- [ ] Storage abstraction layer (Storage Subsystem).
- [ ] Durable Event Log implementation.
- [ ] Audit Log implementation.
- [ ] Basic Metrics and Health reporting.
- [ ] Core Schema definitions (Observation Event, Knowledge Object).
- [ ] Unit tests for Storage and Observability primitives.
- [ ] Onboarding flow specification and implementation (structured self-description → seed observation event → seed persona vector).

## Dependencies
- None.

## Risks
- **Storage Complexity:** Choosing and configuring the right vector database for local-first operation.
- **Performance:** Ensuring the storage layer meets the latency requirements for real-time observation.

## Success Criteria
- A user can run the system and see "Foundation Complete" in the logs.
- A raw observation can be ingested, stored in DuckDB, and retrieved by ID.
- Every write to the database is accompanied by a corresponding entry in the audit log.
\n\n[ ] Resolve Q1 (minimum viable observation surface) and Q6 (action authorization granularity) before Phase 2 begins.
