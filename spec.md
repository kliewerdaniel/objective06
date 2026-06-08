# SELF — Canonical System Specification

> This document is the authoritative specification of the SELF (Synthetic Evolutionary Local Framework) system. It defines purpose, goals, concepts, terminology, architecture, subsystems, data flow, lifecycle, and success criteria. Where this document conflicts with implementation code, this document prevails until amended.

**Version:** 0.1.0
**Status:** Living specification
**Last updated:** Phase 1 (Foundation)

---

## 1. Purpose

SELF is a local-first, long-running cognitive infrastructure that maintains a persistent, evolving representation of a single user by:

1. **Observing** the user's activity across their digital environment.
2. **Extracting** structured knowledge from those observations.
3. **Remembering** the knowledge, the observations, and the history of both.
4. **Modeling** the user's identity as a temporal graph and a vector representation.
5. **Synthesizing** summaries, reflections, predictions, and narratives.
6. **Acting** on the user's behalf through an execution layer, with consent.
7. **Adapting** to changes in the user, the environment, and the underlying models.

The objective is **continuity of identity representation across time**.

---

## 2. System Goals

SELF's goals are prioritized. Higher-priority goals constrain lower-priority ones.

| Priority | Goal | Description |
| --- | --- | --- |
| 1 | Continuity | Unbroken, evolving representation across years. |
| 2 | Locality | Operates entirely on the user's hardware by default. |
| 3 | Auditability | Every state change is traceable. |
| 4 | Explainability | The system can justify every belief and action. |
| 5 | Provenance | Lineage is preserved through every transformation. |
| 6 | Model Independence | Survives changes in models, frameworks, languages. |
| 7 | Composability | Subsystems are replaceable, swappable, inspectable. |
| 8 | Autonomy with Consent | Acts only with explicit, revocable permission. |
| 9 | Expressiveness | Captures nuance, contradiction, evolution. |
| 10 | Performance | Runs on commodity hardware within reasonable bounds. |

A subsystem that improves goal 10 at the cost of goals 1–6 is rejected.

---

## 3. Core Concepts

The system is built on a small set of concepts that must be understood precisely.

### 3.1 Observation Event

An **observation event** is the atomic unit of input. It is a structured record of something that happened in the user's digital environment: a file was modified, a commit was made, an email was received, a webpage was visited, a terminal command was run, a note was written.

Observation events are **immutable**, **timestamped**, and **provenance-rich**. They are produced by the Observer subsystem.

See `schemas/observation_event.md`.

### 3.2 Knowledge Object

A **knowledge object** is a structured representation of meaning extracted from observation events. Knowledge objects include beliefs, goals, projects, interests, relationships, and the like. They are produced by the Extractor subsystem and refined over time.

Knowledge objects are **mutable** in the sense that they can be updated, deprecated, or superseded, but every mutation is recorded in the audit log with full provenance.

See `schemas/knowledge_object.md`.

### 3.3 Identity Node

An **identity node** is an entity in the user's identity graph: the user themselves, a person, a project, an organization, a tool, a concept, a place. Identity nodes have types, attributes, and temporal validity. Identity nodes use bitemporal modeling. `valid_time` tracks when a fact was true in the world; `transaction_time` tracks when SELF learned it. Queries must specify which time axis they operate on.

See `schemas/identity_node.md`.

### 3.4 Persona Vector

A **persona vector** is a high-dimensional embedding that represents the user's identity at a point in time. Persona vectors evolve continuously as new observations and knowledge objects are integrated.

See `schemas/persona_vector.md`.

### 3.5 Memory Snapshot

A **memory snapshot** is a point-in-time capture of the system's state, used for debugging, migration, and rollback.

See `schemas/memory_snapshot.md`.

### 3.6 Identity Snapshot

An **identity snapshot** is a point-in-time capture of the user's identity representation, used for reflection, comparison, and continuity across implementations.

See `schemas/identity_snapshot.md`.

### 3.7 Action Request and Result

An **action request** is a structured intent for the system to do something: send an email, create a file, open a browser tab, run a command. An **action result** is the outcome.

Actions are always authorized, logged, and explainable.

See `schemas/action_request.md` and `schemas/action_result.md`.

### 3.8 Summary

A **summary** is a synthesis artifact: a daily summary, a weekly summary, a topic summary, a project summary. Summaries are derived from knowledge objects and carry provenance to the underlying beliefs and observations.

See `schemas/daily_summary.md` and `schemas/weekly_summary.md`.

---

## 4. Terminology

| Term | Definition |
| --- | --- |
| **User** | The single human whose digital existence SELF models. SELF is a single-user system. |
| **System** | The SELF installation as a whole. |
| **Subsystem** | A named component with defined responsibilities (Observer, Extractor, etc.). |
| **Event** | An observation event. The atomic unit of input. |
| **Knowledge** | A knowledge object. The atomic unit of meaning. |
| **Graph** | The identity graph maintained by the Identity Graph subsystem. |
| **Vector** | A persona vector maintained by the Persona Engine. |
| **Action** | A discrete thing the system does on the user's behalf. |
| **Synthesis** | The production of summaries, reflections, and predictions. |
| **Provenance** | The lineage of a knowledge object back to its source events. |
| **Extraction** | The process of turning an event into a knowledge object. |
| **Embedding** | A dense numerical vector representing semantic content. |
| **Checkpoint** | A persistent milestone in the system's evolution. |
| **Twin** | The digital twin — the queryable, conversational face of the system. |
| **Backbone** | The orchestration layer that schedules and coordinates subsystems. |

---

## 5. Architecture Overview

SELF is organized as a directed graph of subsystems with the Orchestration layer as the spine.

### 5.1 The Loop

```
Observation → Extraction → Memory → Identity Graph → Persona → Synthesis → Twin
       ↑                                                                          ↓
       └─────────────────────── Action (with consent) ──────────────────────────┘
```

The loop is continuous. Observation never stops while the system runs. Extraction runs on schedules and on triggers. Memory, identity graph, and persona are updated incrementally. Synthesis runs on schedules (daily, weekly) and on demand. The twin is the conversational surface. Actions are taken only with consent and always return to observation.

### 5.2 The Substrates

The system is bound to four storage substrates, each chosen for fit:

- **DuckDB** — analytical queries over observation events and knowledge objects.
- **LadybugDB (default) or Neo4j (enterprise fallback)** — graph queries over the identity graph.
- **Vector Database** — semantic similarity over embeddings.
- **Filesystem** — raw artifacts, snapshots, configuration, logs.

Subsystems interact with these substrates through well-defined interfaces, never directly. A substrate may be swapped without rewriting subsystems.

### 5.3 The Models

The system uses two classes of model:

- **Language models** — for extraction, synthesis, reflection, prediction, and conversational response.
- **Embedding models** — for semantic retrieval and persona vector updates.

Both classes are accessed through interfaces. The system supports local models (Ollama, vLLM, llama.cpp) and may, with explicit consent, use remote models. No model is a permanent dependency.

---

## 6. Subsystem Descriptions

Each subsystem is described in detail in its `architecture/` document. The summary:

### 6.1 Observer

Captures observation events from configured sources. The Observer is always running. It does not interpret; it records. Its output is the input stream of the entire system.

See `architecture/observer.md`.

### 6.2 Extractor

Transforms observation events into knowledge objects. Uses language models to identify entities, relationships, beliefs, goals, projects, and interests. Operates on a schedule and on event triggers.

See `architecture/extraction.md`.

### 6.3 Memory

Stores observation events, knowledge objects, and derived state. Provides retrieval APIs by ID, by time range, by graph traversal, and by semantic similarity. Manages compaction, archival, and snapshots.

See `architecture/memory.md`.

### 6.4 Identity Graph

Maintains a temporal graph of identity nodes and their relationships. Tracks changes: when a node appeared, when an attribute changed, when a relationship formed or dissolved. Supports queries about the user's evolving identity.

See `architecture/identity_graph.md`.

### 6.5 Persona Engine

Maintains a vector representation of the user's identity. Updates the persona vector as new knowledge objects arrive. Provides similarity queries ("is this consistent with who the user is?") and prediction queries ("what would the user do next?").

See `architecture/persona_engine.md`.

### 6.6 Digital Twin

The conversational interface. Takes natural-language queries and returns answers grounded in the identity graph, memory, and persona. The twin can summarize, reflect, predict, and propose actions, but never invents facts not grounded in the system's state.

See `architecture/digital_twin.md`.

### 6.7 Action Engine

Executes actions on the user's behalf through Objective05-style layers. Every action is authorized, scoped, logged, and explainable. The Action Engine is the only subsystem that produces side effects in the external world.

See `architecture/action_engine.md`.

### 6.8 Synthesis Engine

Produces summaries, reflections, predictions, and narratives. Operates on schedules (daily, weekly) and on demand. The Synthesis Engine is the system's narrator — it turns state into stories the user can read.

See `architecture/synthesis_engine.md`.

### 6.9 Storage

Defines the interfaces to DuckDB, LadybugDB (default) or Neo4j (enterprise fallback), the vector database, and the filesystem. The Storage subsystem is the substrate abstraction layer. No other subsystem talks to storage directly.

See `architecture/storage.md`.

### 6.10 Evaluation

Defines the metrics, benchmarks, and pass/fail criteria for every subsystem. SELF's correctness is not asserted; it is measured.

See `architecture/evaluation.md`.

### 6.11 Orchestration

Schedules and coordinates the subsystems. Owns the main loop. Handles retries, back-pressure, and graceful degradation. Owns the audit log.

See `architecture/orchestration.md`.

### 6.12 Security

Enforces the constitutional principles of user ownership, auditability, consent, and protection. Owns the permission system, the threat model, and the security audit process.

See `architecture/security.md`.

---

## 7. Data Flow

The flow of data through SELF is the most important thing to understand.

### 7.1 The Happy Path

1. **Source systems** (filesystem, git, GitHub, RSS, email, browser, terminal, markdown) produce raw activity.
2. The **Observer** captures raw activity and emits immutable `observation_event` objects with timestamps and source identifiers.
3. The **Extractor** consumes observation events, batches them, and uses a language model to produce structured `knowledge_object` instances.
4. Knowledge objects are written to **Memory** and used to update the **Identity Graph** and the **Persona Engine**.
5. The **Synthesis Engine** periodically reads Memory, the Identity Graph, and the Persona Engine to produce summaries.
6. The **Digital Twin** exposes the entire state to the user through natural-language queries.
7. The **Action Engine** receives authorized action requests from the user (or from the Twin on the user's behalf), executes them through Objective05, and logs results.
8. Action results become new observation events, closing the loop.

### 7.2 The Provenance Flow

Provenance is recorded at every step. A knowledge object's provenance includes the source events, the extraction prompt, the model used, the timestamp, and the confidence. A summary's provenance includes the knowledge objects it was derived from. An action's provenance includes the authorization, the inputs, and the outputs.

Walking the provenance chain from any object must be possible in O(1) lookups.

### 7.3 The Failure Path

When any subsystem fails, the failure is logged, retried according to policy, and, if persistent, surfaced to the user. Failures do not cascade. The system continues to observe even if synthesis is failing; it continues to extract even if the persona engine is offline.

### 7.4 Backpressure

If the system is overloaded — for example, a burst of email — observation continues but extraction is throttled. The user is informed. No data is lost; it is queued.

---

## 8. Lifecycle

SELF has a lifecycle distinct from a typical application.

### 8.1 First Run

On first run, the system:

1. Initializes its storage substrates.
2. Creates an empty identity graph with a single node: the user.
3. Initializes an empty persona vector (or a seed derived from a brief onboarding).
4. Begins observation of the configured sources.
5. Does **not** perform synthesis until enough observations have accumulated.

### 8.2 Steady State

In steady state, the system:

1. Continuously observes.
2. Extracts on schedules and triggers.
3. Updates the identity graph and persona incrementally.
4. Produces daily summaries at a user-configured time.
5. Produces weekly summaries at a user-configured time.
6. Serves twin queries on demand.
7. Executes authorized actions.

### 8.3 Migration

When the user moves to a new machine, the system:

1. Exports its state as a portable archive.
2. Imports on the new machine.
3. Resumes the loop with no data loss.

### 8.4 Upgrade

When the system is upgraded:

1. The new version reads the existing state.
2. Migrations are applied if needed.
3. The loop resumes.

### 8.5 Decommission

When the user wishes to stop using SELF, the system:

1. Exports a final archive.
2. Optionally deletes all data.
3. Optionally deletes the audit log.
4. Confirms completion to the user.

---

## 9. Success Criteria

SELF is successful when:

1. After one year of operation, the system can accurately summarize what the user did, who they interacted with, what they learned, and what changed about them.
2. The system can answer "what was I working on three months ago?" with a grounded, sourced response.
3. The system can detect a change in the user's belief within a week of the change occurring.
4. The system can predict the user's next major task with non-trivial accuracy.
5. The system can take an authorized action (e.g., draft an email, create a file) and the user can verify what it did, why, and based on what.
6. The user can read the entire state of the system in human-readable form.
7. The system continues to function when the user is offline.
8. The system survives model changes without losing accumulated knowledge.
9. The system can be migrated to a new machine with no data loss.
10. The user trusts the system — not because it never makes mistakes, but because every mistake is auditable and reversible.

These criteria are not measured by benchmarks alone. They are measured by the user's lived experience of using the system over time.

---

## 10. Out of Scope

SELF explicitly does not attempt to:

- Replace the user's primary tools (email client, editor, terminal).
- Provide a multi-user experience.
- Operate as a chatbot for arbitrary third-party users.
- Train or fine-tune its own foundation models.
- Replace the user's memory in the philosophical sense.
- Make decisions for the user about values, ethics, or relationships.

SELF is a tool, not an agent with its own agency.

---

## 11. Versioning

This specification is versioned semantically. Breaking changes to data shapes require a major version bump. Backwards-compatible clarifications require a minor version bump. Editorial fixes require a patch version bump.

The current version is 0.1.0. The system is not yet feature-complete. The specification will be amended as the system evolves.

---

## 12. Open Questions

The following questions are tracked and will be resolved in future revisions:

- Q1. What is the minimum viable observation surface for a useful first release?
- Q2. How does the system handle conflicting sources (e.g., a belief supported by one source and contradicted by another)?
- Q3. What is the right cadence for synthesis? Daily, weekly, on-demand, or all three?
- Q4. How does the system represent silence — the absence of observation — and what does it infer from it?
- Q5. How does the system handle the user's forgetting? Is forgetting modeled?
- Q6. What is the right unit of action authorization? Per action, per session, per capability?

These are open questions, not gaps in the architecture. The architecture is designed to be revised as these are answered.
