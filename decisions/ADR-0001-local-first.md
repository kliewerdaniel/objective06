# ADR-0001: Local-First Operation

## Status
Accepted

## Context
SELF is designed as a personal cognitive infrastructure. The user's digital identity is highly sensitive. For this reason, it is paramount that the system operates primarily on the user's own hardware.

## Decision
All components of SELF, including storage, models, and orchestration, must run on the user's local machine by default. No data shall leave the user's machine unless the user explicitly opts into a remote capability (e.g., a remote LLM or cloud-based search).

**Revision**

**Revision 1.1** (2026-06-10)
- Updated graph substrate from Kuzu to LadybugDB as the default.
- KuzuDB is archived; LadybugDB is the community-designated successor.
- Neo4j remains as the enterprise fallback option.

## Consequences

- **Performance**: The system's performance is limited by the user's hardware.
- **Privacy**: Data remains under the user's control.
- **Maintenance**: The user (or the system on their behalf) is responsible for maintaining the local infrastructure (e.g., starting the Ollama server).
- **Model Availability**: The user is limited to models they can run locally, which may have different capabilities than cloud models.

## Compliance
This decision directly supports **Article II (Local-First Operation)** of the SELF Constitution.
