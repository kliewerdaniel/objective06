# SELF — Comprehensive Implementation TODO

> **State:** Phase 1 (Foundation) — ~80% implemented.
> Core infrastructure: storage, audit log, event log, schemas, onboarding, tests.
> This TODO aggregates every deliverable from the roadmap, architecture docs, schemas, evaluations, CRITIQUE_AND_UPDATES.md, open questions, and supporting docs.

---

## 0. Pre-Implementation — Repository Setup & Critical Fixes

### 0.1 Repository Infrastructure
- [ ] Create `.gitignore` (Python, Node, OS files, IDE, DuckDB, FAISS, snapshot artifacts)
- [ ] Choose primary language(s) and set up build system
  - Decision needed: Python (Pydantic/FastAPI), Rust, or hybrid
  - Create `pyproject.toml` / `Cargo.toml` / `package.json` as appropriate
- [ ] Set up linting (ruff, mypy, or language-appropriate)
- [ ] Set up formatting (black/ruff, prettier)
- [ ] Set up pre-commit hooks (lint, format, typecheck)
- [ ] Create `src/` directory structure matching the 12 subsystems
- [ ] Set up CI pipeline (GitHub Actions or equivalent)
- [ ] Set up testing framework (pytest or language-appropriate)
- [ ] Create `Makefile` or equivalent for common commands (test, lint, run, build)

### 0.2 Fix Critical Issues (from CRITIQUE_AND_UPDATES.md)

#### C-1 · Kuzu → LadybugDB (partially done via ADR-0002)
- [ ] `spec.md §5.2` — Change "Kuzu or Neo4j" to "LadybugDB (default) or Neo4j (enterprise fallback)"
- [ ] `architecture/storage.md` — Add LadybugDB install instructions pointer
- [ ] `architecture/identity_graph.md` Failure Modes table — Add "Substrate archived upstream — use LadybugDB fork"
- [ ] `decisions/ADR-0001-local-first.md` — Add Revision section noting LadybugDB
- [ ] Global consistency pass — Search all documents for bare "Kuzu" (not preceded by "Ladybug") and replace with "LadybugDB"

#### C-2 · DuckDB Single-Process Constraint (done in docs — verify)
- [ ] Verify `architecture/storage.md` has the Concurrency Constraint subsection
- [ ] Verify `architecture/orchestration.md` has Write Queue component
- [ ] Verify `spec.md §5.2` has the DuckDB single-process note
- [ ] Implement the Write Queue in code (serializing UPDATE/DELETE queue)

#### C-3 · Prompt Injection Defense — Three-Layer Model
- [ ] `architecture/digital_twin.md` — Verify it has the three-layer model (Structural isolation, Secondary classifier, Citation-lock)
- [ ] `architecture/extraction.md` Failure Modes table — Add row for indirect prompt injection
- [ ] `architecture/security.md` — Add Injection Classifier subsystem component (verify exists)
- [ ] Implement Injection Classifier component in code
- [ ] Implement Structural isolation in Digital Twin prompt assembly
- [ ] Implement Citation-lock validation in Digital Twin

### 0.3 Fix High-Severity Issues (fix before Phase 2)

#### H-1 · Embedding Model Lineage (done via ADR-0003 — verify)
- [ ] Verify `interfaces/local_models.md` has Recommended Embedding Models section
- [ ] Verify `schemas/persona_vector.md` has cross-lineage similarity prohibition
- [ ] Verify `architecture/persona_engine.md` has `model_lineage_id` pinned-model constraint
- [ ] Implement `model_lineage_id` validation in code

#### H-2 · Audit Log Hash-Chain Integrity
- [ ] Implement SHA-256 `prev_hash` chaining in audit log entries
- [ ] Implement `audit_head.sha256` file with atomic updates
- [ ] Implement startup integrity verification
- [ ] Implement on-demand integrity check query
- [ ] Add `memory.audit_log_integrity` metric

#### H-3 · Bitemporal Modeling
- [ ] Verify `schemas/identity_node.md` has `recorded_at` and `recorded_updated_at`
- [ ] Verify `schemas/relationship.md` has `recorded_at` and `recorded_updated_at`
- [ ] Verify `architecture/identity_graph.md` has bitemporal index description
- [ ] Verify `spec.md §3.3` has bitemporal modeling note
- [ ] Implement valid_time + transaction_time B-tree indexes in graph store adapter
- [ ] Implement query-time axis selection (valid_time vs transaction_time)

#### H-4 · Forgetting / Decay Mechanism
- [ ] Verify `architecture/memory.md` Compaction Engine has Relevance Scorer
- [ ] Verify `architecture/persona_engine.md` has Decay Engine
- [ ] Verify `architecture/synthesis_engine.md` has archived-object exclusion
- [ ] Implement Relevance Scorer (recency, reinforcement, confidence, consistency)
- [ ] Implement tier transitions (hot → warm → cold → archived)
- [ ] Implement nightly Decay Engine
- [ ] Add `roadmap/phase_04_memory.md` deliverable if missing

### 0.4 Fix Medium-Severity Issues (fix before Phase 3)

#### M-1 · Schema Migration Runner
- [ ] Create `tools/schema_migrate/` directory
- [ ] Create migration runner interface: `migrate(record, from_version, to_version) -> dict`
- [ ] Implement auto-apply on read in Storage subsystem
- [ ] Ensure idempotency
- [ ] Create `evaluations/schema_migration.md`
- [ ] Add one-line migration pointer to all schema files referencing observation_event.md

#### M-2 · Onboarding / Cold-Start Procedure
- [ ] Verify `spec.md §8.1` has onboarding flow (structured self-description → seed event → seed vector)
- [ ] Verify `roadmap/phase_01_foundation.md` has onboarding deliverable
- [ ] Verify `architecture/persona_engine.md` has cold-start edge case
- [ ] Implement onboarding flow: collect self-description, emit `system.onboarding` event
- [ ] Implement seed persona vector generation from onboarding event
- [ ] Implement deferred synthesis until ≥7 days or user request

#### M-3 · Objective05 Interface
- [ ] Create `interfaces/objective05.md` with minimal Execution Plan Schema
- [ ] Implement Objective05 plan structure in Action Engine

#### M-4 · Evaluation Harness Deliverables (cross-reference all phases)
- [ ] Add evaluation harness deliverable to each phase file (verify all done)

#### M-5 · Data Volume Budget & Compression
- [ ] Add `memory.projected_size_3yr` metric
- [ ] Add FAISS Product Quantization (PQ) compression when >50K objects
- [ ] Add `index_compression` config option in storage architecture

### 0.5 Fix Low-Severity Issues

#### L-1 · Glossary Gaps
- [ ] Add missing terms to `docs/glossary.md`: cold/warm/hot tier, transaction/valid time, model lineage, capability, bitemporal, injection classifier, Write Queue

#### L-2 · Sandbox Manager Duplication
- [ ] Verify `architecture/security.md` Sandbox Manager is the shared service
- [ ] Verify `architecture/action_engine.md` Sandbox Manager delegates to Security

#### L-3 · Open Questions Tracked in Roadmap
- [ ] Cross-reference Q1–Q6 to affected architecture docs and roadmap phases
- [ ] Verify Q1/Q6 tracked in Phase 1 roadmap
- [ ] Verify Q2 tracked in Phase 3 roadmap
- [ ] Verify Q3/Q4/Q5 tracked in Phase 9 roadmap

#### L-4 · GDPR/CCPA Actionable Requirements
- [ ] Add Right to Erasure (Art. 17) procedure to `security/privacy_model.md`
- [ ] Add Right to Portability (Art. 20) NDJSON export format to `security/privacy_model.md`
- [ ] Add Data Minimization observer filter guidance to `security/privacy_model.md`

---

## 1. Phase 1 — Foundation (Storage + Observability + Core Schemas)

### 1.1 Project Structure & Configuration
- [ ] Create `src/self/` package structure
- [ ] Implement configuration system (YAML/JSON/TOML, hot-reload support)
- [ ] Implement Configuration Manager component
- [ ] Create default configuration file
- [ ] Implement logging infrastructure

### 1.2 Storage Abstraction Layer
- [ ] Define `Storage API` interface (get, query, insert, update, delete, traverse, search, snapshot, restore, export, import)
- [ ] Implement `DuckDBAdapter` — analytical store
- [ ] Implement `DuckDB Connection Manager` with pool
- [ ] Implement `Schema Validator` — validate records against schemas on write
- [ ] Implement `Migration Engine` — apply schema migrations
- [ ] Implement `Transaction Coordinator` — cross-substrate coordination
- [ ] Implement `Backup Manager` — full/incremental backups, integrity verification, encryption
- [ ] Implement `Substrate Monitor` — query latency, error rates, resource usage
- [ ] Implement `VectorDBAdapter` (FAISS) — semantic search
- [ ] Implement `FileSystemAdapter` — raw artifacts, snapshots, logs, config
- [ ] Implement `LadybugDBAdapter` or graph store adapter — identity graph

### 1.3 Durable Event Log
- [ ] Implement append-only event log on DuckDB
- [ ] Implement time-range queries
- [ ] Implement content-addressable raw payload storage
- [ ] Implement replay from point-in-time

### 1.4 Audit Log
- [ ] Implement append-only audit log
- [ ] Implement hash-chain integrity (SHA-256 `prev_hash`)
- [ ] Implement `audit_head.sha256` atomic file updates
- [ ] Implement queryable audit log (by actor, action, time, entity)
- [ ] Implement startup integrity verification
- [ ] Implement on-demand integrity check
- [ ] Add `memory.audit_log_integrity` metric

### 1.5 Metrics & Health Reporting
- [ ] Implement metrics collection infrastructure
- [ ] Implement Health Monitor component
- [ ] Implement heartbeats per subsystem
- [ ] Implement Health Monitor in Orchestration layer

### 1.6 Core Schema Definitions (as code)
- [ ] Implement `observation_event` schema as code (Pydantic/dataclass)
- [ ] Implement `knowledge_object` generic schema as code
- [ ] Implement schema validation against field definitions
- [ ] Implement schema versioning support

### 1.7 Onboarding Flow
- [ ] Implement structured self-description collection
- [ ] Implement seed `system.onboarding` observation event
- [ ] Implement initial knowledge object generation from onboarding
- [ ] Implement seed persona vector from onboarding event
- [ ] Implement deferred synthesis logic

### 1.8 Unit Tests — Storage & Observability
- [ ] Unit tests for DuckDBAdapter (CRUD, query, migration)
- [ ] Unit tests for FAISS adapter (insert, search, rebuild)
- [ ] Unit tests for Schema Validator (accept, reject, versioning)
- [ ] Unit tests for Audit Log (append, query, hash-chain integrity)
- [ ] Unit tests for Event Log (append, replay, time-range query)
- [ ] Unit tests for Snapshot Manager (create, validate, restore)
- [ ] Unit tests for Migration Engine (apply, rollback)

### 1.9 Resolve Open Questions Before Phase 2
- [ ] **Q1:** What is the minimum viable observation surface for a useful first release?
- [ ] **Q6:** What is the right unit of action authorization (per action, per session, per capability)?

---

## 2. Phase 2 — Observation (Capture & Normalize)

### 2.1 Observer Subsystem Architecture
- [ ] Implement Observer main component
- [ ] Implement Heatlh Monitor per adapter
- [ ] Integrate with Orchestration for scheduling/lifecycle
- [ ] Integrate with Security for permission checks and secrets

### 2.2 Source Adapters
- [ ] **Filesystem Watcher** adapter (inotify/FSEvents/ReadDirectoryChangesW)
- [ ] **Git Hook** adapter (post-commit, post-checkout, post-merge)
- [ ] **GitHub Poller** adapter (REST/GraphQL polling, webhooks)
- [ ] **RSS/Atom Feed** adapter (polling, change detection)
- [ ] **Email** adapter (IMAP/Gmail API)
- [ ] **Browser History** adapter (Chrome/Firefox/Safari sync)
- [ ] **Terminal Session** adapter (shell history/log streams)
- [ ] **Markdown/Note** adapter (file change detection)
- [ ] **Calendar** adapter (CalDAV/Google Calendar)

### 2.3 Normalizer
- [ ] Implement stable ID assignment
- [ ] Implement UTC timestamp resolution (monotonic + wall-clock)
- [ ] Implement content hashing
- [ ] Implement provenance metadata attachment
- [ ] Implement source-specific noise stripping

### 2.4 Ingest Queue
- [ ] Implement bounded, persistent queue (survives restarts)
- [ ] Implement priority lanes (user actions > background syncs)
- [ ] Implement backpressure signals to adapters

### 2.5 Event Log Writer
- [ ] Implement transactional, append-only writer
- [ ] Implement content-addressable raw payload storage
- [ ] Implement index for fast lookup (by source, time, entity)

### 2.6 Backfill Engine
- [ ] Implement historical ingestion per source
- [ ] Implement rate limit respect
- [ ] Implement pause/resume
- [ ] Implement idempotency

### 2.7 Privacy Filtering (Edge)
- [ ] Implement per-source privacy filter configuration
- [ ] Implement content filtering at adapter level before storage

### 2.8 Evaluation — discover_project
- [ ] Build labeled dataset for project discovery
- [ ] Implement graded evaluation harness
- [ ] Verify precision > 80%, recall > 70%, 100% provenance integrity

---

## 3. Phase 3 — Extraction (Events → Knowledge)

### 3.1 Extractor Subsystem Architecture
- [ ] Implement Extractor main component
- [ ] Integrate with Memory (read events, write knowledge)
- [ ] Integrate with Identity Graph (entity resolution)
- [ ] Integrate with Local Models (inference)
- [ ] Integrate with Orchestration (scheduling, retries)

### 3.2 Event Batcher
- [ ] Implement time-based batching
- [ ] Implement source-based batching
- [ ] Implement entity-based batching
- [ ] Implement trigger-based batching
- [ ] Ensure idempotency

### 3.3 Prompt Selector
- [ ] Implement prompt selection by event types
- [ ] Implement prompt selection by identity graph state
- [ ] Implement cost/quality trade-off configuration
- [ ] Support model capability tags

### 3.4 Prompt Library
- [ ] Create `prompts/` directory with versioned prompt templates
- [ ] Implement belief extraction prompt
- [ ] Implement goal detection prompt
- [ ] Implement project discovery prompt
- [ ] Implement interest detection prompt
- [ ] Implement relationship extraction prompt
- [ ] Implement entity extraction prompt
- [ ] Implement prompt versioning and migration

### 3.5 Model Client
- [ ] Implement Ollama adapter
- [ ] Implement vLLM adapter
- [ ] Implement llama.cpp adapter
- [ ] Implement retries with exponential backoff
- [ ] Implement timeouts and token limits
- [ ] Implement model failover (primary → secondary)
- [ ] Implement token usage and cost reporting
- [ ] Implement request/response logging

### 3.6 Output Validator
- [ ] Implement JSON parsing and schema validation
- [ ] Implement required field verification
- [ ] Implement safe type coercion
- [ ] Implement quarantine for repeated failures

### 3.7 Entity Linker
- [ ] Implement string similarity matching
- [ ] Implement embedding similarity matching
- [ ] Implement contextual feature matching
- [ ] Implement disambiguation via model
- [ ] Implement new entity creation when no match found
- [ ] Record linking decisions with provenance

### 3.8 Confidence Scorer
- [ ] Implement logprob-based scoring
- [ ] Implement evidence strength scoring
- [ ] Implement contradiction detection scoring
- [ ] Surface low-confidence objects for user review

### 3.9 Contradiction Detector
- [ ] Implement semantic neighborhood comparison
- [ ] Implement contradiction marking in provenance chain
- [ ] Surface contradictions (do not auto-resolve)

### 3.10 Knowledge Writer
- [ ] Implement transactional writes to Memory
- [ ] Implement identity graph update coordination
- [ ] Implement event emission for downstream consumers (Synthesis, Persona)

### 3.11 Evaluations
- [ ] Build labeled dataset for belief extraction
- [ ] Implement graded evaluation harness for `evaluations/extract_belief.md`
- [ ] Build labeled dataset for goal detection
- [ ] Implement graded evaluation harness for `evaluations/detect_goal.md`

### 3.12 Resolve Open Questions Before Phase 4
- [ ] **Q2:** How does the system handle conflicting sources (belief supported by one, contradicted by another)?

---

## 4. Phase 4 — Memory (Storage + Retrieval + Compaction)

### 4.1 Memory Subsystem Architecture
- [ ] Implement Memory API (interfaces/memory_api.md)
- [ ] Integrate all stores (Event, Knowledge, Summary, Audit Log, Vector Index)
- [ ] Implement Query Planner for cross-store routing
- [ ] Integrate with Orchestration for compaction/retention scheduling

### 4.2 Event Store
- [ ] Implement partitioned event storage (by source, by time)
- [ ] Implement time-range query support
- [ ] Implement content-addressable raw payload storage
- [ ] Implement replay from point-in-time

### 4.3 Knowledge Store
- [ ] Implement indexing by type, entity, confidence
- [ ] Implement full-text search
- [ ] Implement semantic search via vector index
- [ ] Implement historical version preservation

### 4.4 Summary Store
- [ ] Implement indexing by time, topic, entity
- [ ] Implement provenance linkage to underlying knowledge
- [ ] Implement temporal retrieval ("summary from date X")

### 4.5 Vector Index
- [ ] Implement incremental index building
- [ ] Implement k-nearest-neighbor queries
- [ ] Implement index rebuild from underlying records
- [ ] Implement replaceable backend (FAISS → managed service)
- [ ] Implement FAISS Product Quantization compression when >50K objects

### 4.6 Snapshot Manager
- [ ] Implement cross-store consistent snapshots
- [ ] Implement point-in-time snapshots
- [ ] Implement named snapshots
- [ ] Implement snapshot validation and restore
- [ ] Implement snapshot lineage tracking

### 4.7 Compaction Engine (with Relevance Scorer)
- [ ] Implement Relevance Scorer (recency, reinforcement, confidence, consistency)
- [ ] Implement hot → warm → cold → archived tier transitions
- [ ] Implement cold tier (excluded from semantic search, retained for provenance)
- [ ] Implement archived tier (filesystem-only, not indexed)
- [ ] Implement configurable tier thresholds
- [ ] Implement reversibility window

### 4.8 Retention Manager
- [ ] Implement per-source retention policies
- [ ] Implement per-type retention rules
- [ ] Implement policy expiration enforcement
- [ ] Implement user consent before removal
- [ ] Log every removal in audit log

### 4.9 Exporter / Importer
- [ ] Implement portable versioned archive
- [ ] Implement all stores + indexes + audit log export
- [ ] Implement integrity verification with checksums
- [ ] Implement resume on interrupt
- [ ] Implement archive validation on import
- [ ] Implement schema migration on import

### 4.10 Evaluation — memory_retrieval
- [ ] Build ground truth dataset for retrieval
- [ ] Implement graded evaluation harness for `evaluations/memory_retrieval.md`

---

## 5. Phase 5 — Identity Graph (Temporal Entity Model)

### 5.1 Identity Graph Subsystem Architecture
- [ ] Implement Identity Graph main component
- [ ] Integrate with Memory for persistence
- [ ] Integrate with Extractor for entity/edge proposals
- [ ] Integrate with Orchestration for maintenance tasks

### 5.2 Node Store
- [ ] Implement node CRUD (User, Person, Project, Organization, Tool, Concept, Place, Event, Artifact, Goal, Interest, Belief, Community, Publication)
- [ ] Implement attribute store (free-form key-value)
- [ ] Implement temporal validity tracking
- [ ] Implement provenance attachment

### 5.3 Edge Store
- [ ] Implement edge CRUD (all relationship types)
- [ ] Implement weight tracking
- [ ] Implement bidirectional edge support
- [ ] Implement temporal validity tracking
- [ ] Implement provenance attachment

### 5.4 Temporal Index (Bitemporal)
- [ ] Implement valid_time B-tree index
- [ ] Implement transaction_time B-tree index
- [ ] Implement "as of time T" queries
- [ ] Implement "during range [T1, T2]" queries
- [ ] Implement "changed at time T" queries
- [ ] Implement "recorded at time T" queries

### 5.5 Entity Resolver
- [ ] Implement string similarity matching
- [ ] Implement embedding similarity matching
- [ ] Implement structural feature matching
- [ ] Implement context-based disambiguation
- [ ] Implement manual confirmation for ambiguous cases
- [ ] Record resolution decisions with provenance

### 5.6 Merge Engine
- [ ] Implement node merging with provenance preservation
- [ ] Implement edge re-targeting on merge
- [ ] Implement merge logging in audit log
- [ ] Implement reversible merges (configurable window)

### 5.7 Evolution Tracker
- [ ] Implement attribute change recording
- [ ] Implement diff queries between time points
- [ ] Implement history queries per node/edge

### 5.8 Query Engine
- [ ] Implement pattern matching queries
- [ ] Implement path finding queries
- [ ] Implement neighborhood queries
- [ ] Implement temporal scoping
- [ ] Implement aggregations (counts, sums, weights)
- [ ] Implement query budgets

### 5.9 Schema Registry
- [ ] Implement versioned node type definitions
- [ ] Implement versioned edge type definitions
- [ ] Implement attribute key validation
- [ ] Support type extension without breaking old data

### 5.10 Evaluation — build_identity_snapshot
- [ ] Build ground truth dataset for identity snapshot
- [ ] Implement graded evaluation harness for `evaluations/build_identity_snapshot.md`

---

## 6. Phase 6 — Persona Engine (Vector Identity)

### 6.1 Persona Engine Subsystem Architecture
- [ ] Implement Persona Engine main component
- [ ] Integrate with Memory for knowledge/vs tor reads and writes
- [ ] Integrate with Identity Graph for entity context
- [ ] Integrate with Local Embedding Model
- [ ] Integrate with Orchestration for scheduling

### 6.2 Embedding Computer
- [ ] Implement model selection and pinning per installation
- [ ] Implement `model_lineage_id` tracking
- [ ] Implement cross-lineage similarity prohibition
- [ ] Implement caching for unchanged content
- [ ] Implement model swap → full re-embedding
- [ ] Implement per-embedding model version annotation

### 6.3 Persona Vector Store
- [ ] Implement time-indexed vector sequence storage
- [ ] Implement current vector retrieval
- [ ] Implement historical vector retrieval ("persona at time T")
- [ ] Implement trajectory queries (vector deltas over time)
- [ ] Implement similarity queries (current vs. historical)

### 6.4 Persona Updater
- [ ] Implement embedding computation for new knowledge
- [ ] Implement update strategies: moving average, exponential decay, time-weighted, attention-based, user-tuned
- [ ] Implement update provenance recording
- [ ] Implement undo within configurable window

### 6.5 Consistency Scorer
- [ ] Implement cosine similarity between candidate and persona vector
- [ ] Implement score in [0, 1]
- [ ] Implement top-N nearest persona snapshots retrieval
- [ ] Record scores with provenance

### 6.6 Predictor
- [ ] Implement persona trajectory extrapolation
- [ ] Implement identity graph constraint incorporation
- [ ] Implement ranked predictions with confidence scores
- [ ] Record predictions with provenance

### 6.7 Decay Engine
- [ ] Implement nightly decay run
- [ ] Implement configurable decay function (influence weight reduction)
- [ ] Implement knowledge retention (decay ≠ deletion)
- [ ] Implement decay auditability

### 6.8 Model Adapter
- [ ] Implement model change detection
- [ ] Implement re-anchoring (re-embed all historical knowledge)
- [ ] Implement lineage boundary creation
- [ ] Preserve cross-lineage history

### 6.9 Evaluation — update_persona
- [ ] Build ground truth dataset for persona consistency
- [ ] Implement graded evaluation harness for `evaluations/update_persona.md`

---

## 7. Phase 7 — Digital Twin (Conversational Interface)

### 7.1 Digital Twin Subsystem Architecture
- [ ] Implement Digital Twin main component
- [ ] Integrate with Memory (read events, knowledge, summaries)
- [ ] Integrate with Identity Graph (entity queries)
- [ ] Integrate with Persona Engine (personalization, consistency)
- [ ] Integrate with Synthesis Engine (summary answers)
- [ ] Integrate with Action Engine (action proposals)
- [ ] Integrate with Local Language Model
- [ ] Integrate with Security (permissions, injection defense)
- [ ] Integrate with Orchestration (session management)

### 7.2 Query Intake
- [ ] Implement input validation
- [ ] Implement prompt injection sanitization (layer 1: structural isolation)
- [ ] Implement session establishment/extension
- [ ] Implement query logging

### 7.3 Intent Classifier
- [ ] Implement intent classification (factual retrieval, entity exploration, summary, reflection, prediction, action proposal, meta-question, conversation)
- [ ] Implement confidence-based clarification
- [ ] Record intent in audit log

### 7.4 Query Decomposer
- [ ] Implement complex query → sub-query decomposition
- [ ] Constrain to known query types
- [ ] Record decomposition decisions

### 7.5 Sub-Query Router
- [ ] Implement per-subsystem routing
- [ ] Implement parallel sub-query execution
- [ ] Implement result aggregation

### 7.6 Answer Composer
- [ ] Implement constrained prompt generation
- [ ] Implement grounding citations
- [ ] Implement explicit uncertainty marking
- [ ] Implement follow-up query suggestions
- [ ] Implement citation-lock validation (layer 3)

### 7.7 Citation Tracker
- [ ] Implement sentence → source record ID mapping
- [ ] Expose mapping to user
- [ ] Record mapping in conversation log

### 7.8 Session Manager
- [ ] Implement session state storage
- [ ] Implement context maintenance (entities, intents)
- [ ] Implement session-scoped permissions
- [ ] Implement session resumption

### 7.9 Prompt Sanitizer (Three-Layer)
- [ ] Layer 1: Structural isolation — retrieved content = data slot, not instructions
- [ ] Layer 2: Secondary injection classifier (lightweight model scoring each segment)
- [ ] Layer 3: Citation-lock — reject if output references undeclared knowledge objects
- [ ] Record attempted attacks

### 7.10 Permission Enforcer
- [ ] Check read authorization for requested state
- [ ] Check action proposal authorization
- [ ] Refuse with explanation when permissions exceeded

### 7.11 Evaluations
- [ ] Implement graded evaluation harness for `evaluations/memory_retrieval.md` (retrieval via Twin)
- [ ] Build ground truth for knowledge synthesis
- [ ] Implement graded evaluation harness for `evaluations/knowledge_synthesis.md`

---

## 8. Phase 8 — Action Engine (World Side-Effects)

### 8.1 Action Engine Subsystem Architecture
- [ ] Implement Action Engine main component
- [ ] Integrate with Memory (persistence of action records)
- [ ] Integrate with Identity Graph (context)
- [ ] Integrate with Security (permission checks, sandboxing)
- [ ] Integrate with Objective05 Runtime
- [ ] Integrate with Orchestration (scheduling, retries)
- [ ] Implement Objective05 plan structure from `interfaces/objective05.md`

### 8.2 Action Intake
- [ ] Implement action request validation against schema
- [ ] Implement user/session lookup
- [ ] Implement capability resolution
- [ ] Log intake

### 8.3 Permission Resolver
- [ ] Implement explicit grant checking
- [ ] Implement session-scoped grant checking
- [ ] Implement default-deny rules
- [ ] Implement revocation honoring
- [ ] Return yes/no/require-confirmation with reasons

### 8.4 Plan Synthesizer
- [ ] Implement capability definition lookup
- [ ] Implement parameter resolution against current state
- [ ] Implement precondition generation
- [ ] Implement postcondition generation
- [ ] Implement rollback plan generation
- [ ] Implement policy validation

### 8.5 Capability Registry
- [ ] Define initial capabilities (at least 3)
- [ ] Implement unique identifier per capability
- [ ] Implement human-readable description
- [ ] Implement permission requirements
- [ ] Implement sensitivity level
- [ ] Implement Objective05 specification
- [ ] Implement test cases

### 8.6 Sandbox Manager (delegates to Security)
- [ ] Implement execution isolation
- [ ] Implement network access limitation
- [ ] Implement filesystem access limitation
- [ ] Implement subprocess limitation
- [ ] Implement system call logging
- [ ] Implement timeout and resource budget enforcement

### 8.7 Executor
- [ ] Implement precondition evaluation (abort if fail)
- [ ] Implement step-by-step execution
- [ ] Implement output/side-effect capture
- [ ] Implement postcondition evaluation
- [ ] Implement rollback trigger on postcondition failure
- [ ] Stream progress to audit log

### 8.8 Rollback Engine
- [ ] Implement reverse execution of rollback plan
- [ ] Implement rollback success verification
- [ ] Log rollback attempts
- [ ] Support best-effort and strict rollback modes

### 8.9 Confirmation Manager
- [ ] Implement action plan presentation to user
- [ ] Implement sensitivity highlighting
- [ ] Implement user response recording
- [ ] Implement "always allow" per session
- [ ] Implement "always deny" permanent rules

### 8.10 Result Emitter
- [ ] Implement action result capture
- [ ] Implement diff computation
- [ ] Implement structured observation event from result
- [ ] Trigger downstream observers

### 8.11 Action Categories (Sensitivity Levels)
- [ ] Implement read-only local (generally safe)
- [ ] Implement write local (requires confirmation default)
- [ ] Implement execute local (explicit confirmation)
- [ ] Implement network read (generally safe)
- [ ] Implement network write (explicit confirmation)
- [ ] Implement external system (explicit confirmation + sandboxing)

---

## 9. Phase 9 — Continuous Synthesis (Summaries & Narratives)

### 9.1 Synthesis Engine Subsystem Architecture
- [ ] Implement Synthesis Engine main component
- [ ] Integrate with Memory (read state, write summaries)
- [ ] Integrate with Identity Graph (entity context)
- [ ] Integrate with Persona Engine (personalization, predictions)
- [ ] Integrate with Local Language Model
- [ ] Integrate with Orchestration (scheduling)
- [ ] Integrate with Digital Twin (on-demand requests)

### 9.2 Summary Scheduler
- [ ] Implement user-configured cadences (daily, weekly)
- [ ] Implement natural synthesis moment detection
- [ ] Implement excessive synthesis avoidance
- [ ] Observable schedule

### 9.3 Period Selector
- [ ] Implement daily boundary selection
- [ ] Implement weekly boundary selection
- [ ] Implement topic-based selection
- [ ] Implement project-based selection

### 9.4 Content Aggregator
- [ ] Pull observations for period
- [ ] Pull knowledge objects for period
- [ ] Pull identity graph changes for period
- [ ] Pull persona updates
- [ ] Implement deduplication
- [ ] Implement importance ranking (persona consistency, recency, frequency)
- [ ] Exclude archived objects (unless explicitly requested)
- [ ] Log exclusion count

### 9.5 Prompt Builder
- [ ] Use versioned prompt templates
- [ ] Include aggregated state
- [ ] Include user preferences (length, tone, language)
- [ ] Include grounding/citation instructions

### 9.6 Generation Engine
- [ ] Implement local model-based generation
- [ ] Implement output constraint enforcement
- [ ] Implement streaming for long summaries
- [ ] Implement regeneration with different parameters
- [ ] Record model, prompt version, parameters

### 9.7 Grounding Verifier
- [ ] Implement claim → source record tracing
- [ ] Flag ungrounded claims for regeneration/removal
- [ ] Record grounding coverage metric

### 9.8 Provenance Linker
- [ ] Record contributing observation/knowledge/graph IDs
- [ ] Store links in summary provenance
- [ ] Support "show me the source" queries

### 9.9 Cache Manager
- [ ] Implement summary caching with TTL
- [ ] Implement cache invalidation on state change
- [ ] Implement partial invalidation
- [ ] Audit cache operations

### 9.10 Style Adapter
- [ ] Honor configured length, tone, language
- [ ] Adapt to persona vector (technical vs. plain language)
- [ ] Support user-provided style examples

### 9.11 Notification Manager
- [ ] Implement configured channel delivery (in-app, local notification)
- [ ] Respect quiet hours
- [ ] Include preview
- [ ] Support snooze and regenerate actions

### 9.12 Synthesis Types
- [ ] Research and implement:
- [ ] Daily Summary production
- [ ] Weekly Summary production
- [ ] Topic Summary production
- [ ] Project Summary production
- [ ] Identity Evolution Report production
- [ ] Prediction production

### 9.13 Evaluations
- [ ] Build ground truth for knowledge synthesis
- [ ] Implement graded evaluation harness for `evaluations/knowledge_synthesis.md`
- [ ] Build ground truth for next-task prediction
- [ ] Implement graded evaluation harness for `evaluations/predict_next_task.md`

### 9.14 Resolve Open Questions Before Phase 10
- [ ] **Q3:** What is the right cadence for synthesis (daily, weekly, on-demand, or all three)?
- [ ] **Q4:** How does the system represent silence (absence of observation) and what does it infer?
- [ ] **Q5:** How does the system handle the user's forgetting? Is forgetting modeled?

---

## 10. Phase 10 — Autonomy & Evaluation Framework

### 10.1 Self-Reflection Loop
- [ ] Implement system self-assessment (health, data quality, coverage gaps)
- [ ] Implement improvement proposal generation
- [ ] Implement self-tuning configuration
- [ ] Implement self-diagnosis on anomalies

### 10.2 Capability Discovery & Proposal
- [ ] Implement capability inventory scanning
- [ ] Implement new capability proposal to user
- [ ] Implement capability activation workflow

### 10.3 Autonomous Backup & Health Management
- [ ] Implement scheduled autonomous snapshots
- [ ] Implement pre-upgrade automatic snapshots
- [ ] Implement health-check-driven recovery
- [ ] Implement automatic rollback on detected regression

### 10.4 Multi-Agent Coordination Framework
- [ ] Implement inter-subsystem communication protocols
- [ ] Implement coordination patterns (sequential, parallel, conditional)
- [ ] Implement resource-aware scheduling across subsystems
- [ ] Implement conflict detection between concurrent subsystem goals

### 10.5 Evaluation Framework Implementation
- [ ] Implement Evaluation Library (per-capability evaluation specs)
- [ ] Implement Evaluation Runner (on-demand, scheduled, regression, A/B)
- [ ] Implement Ground Truth Manager (curated + synthetic + user-provided)
- [ ] Implement Metric Aggregator (trends, regression detection)
- [ ] Implement Human Evaluator Interface (rating collection)
- [ ] Implement A/B Test Manager (traffic splitting, statistical significance)
- [ ] Implement Report Generator (markdown, JSON, diff-friendly)
- [ ] Implement meta-evaluation (evaluation of the Evaluation subsystem)

### 10.6 Final System Evaluation
- [ ] Verify all 10+ evaluation specs pass with defined thresholds
- [ ] Verify end-to-end example (`examples/identity_evolution.md`) passes evaluation
- [ ] Verify adversarial evaluations (prompt injection, edge cases, contradictions)
- [ ] Produce final system evaluation report

### 10.7 User Guide for Autonomous Interaction
- [ ] Document autonomous capabilities
- [ ] Document consent/revocation procedures
- [ ] Document failure modes and recovery steps

---

## 11. Cross-Cutting Infrastructure

### 11.1 Orchestration Subsystem (Main Loop)
- [ ] Implement Main Loop (configurable interval, single-threaded + worker pools)
- [ ] Implement Scheduler (cron, interval, trigger-based, one-shot, recurring)
- [ ] Implement Event Bus (pub/sub, topics, delivery guarantees, persistence, audit)
- [ ] Implement Retry Manager (exponential backoff, max retries, transient/permanent)
- [ ] Implement Backpressure Manager (CPU/memory/disk/network tracking, throttling)
- [ ] Implement Write Queue (serialized UPDATE/DELETE for DuckDB)
- [ ] Implement Lifecycle Manager (start, stop, restart, crash recovery, upgrade, migration)
- [ ] Implement Health Monitor (heartbeats, per-subsystem metrics, stuck detection)
- [ ] Implement Notification Manager (channels, quiet hours, aggregation, DND mode)

### 11.2 Security Subsystem
- [ ] Implement Authentication Manager (password, key file, hardware token, MFA, session timeout)
- [ ] Implement Authorization Engine (capability-based, consent evaluation, default-deny)
- [ ] Implement Permission Store (append-only, per-action/session/time rules, user-editable)
- [ ] Implement Secret Manager (encrypted storage, need-to-know access, rotation, audit)
- [ ] Implement Sandbox Manager (process isolation, resource limits, network restriction, audit)
- [ ] Implementation Injection Classifier (lightweight model for untrusted content scoring)
- [ ] Implement Cryptographic Provider (OpenSSL/libsodium, symmetric/asymmetric, key derivation)
- [ ] Implement Anomaly Detector (behavior monitoring, alerting, protective actions)
- [ ] Implement Audit Query Engine (actor/action/time/entity queries, export)
- [ ] Implement Incident Responder (playbooks, alerts, manual override, user notification)

### 11.3 Evaluation Subsystem
- [ ] Implement per-capability evaluation specifications (see Phase 10.5)
- [ ] Implement evaluation running infrastructure
- [ ] Implement ground truth management
- [ ] Implement metric aggregation and trend tracking
- [ ] Implement human evaluation interface
- [ ] Implement report generation

### 11.4 Missing Evaluation Files to Create
- [ ] Create `evaluations/extract_belief.md` — belief extraction evaluation
- [ ] Create `evaluations/detect_goal.md` — goal detection evaluation
- [ ] Create `evaluations/memory_retrieval.md` — memory retrieval evaluation
- [ ] Create `evaluations/build_identity_snapshot.md` — identity snapshot evaluation
- [ ] Create `evaluations/update_persona.md` — persona update evaluation
- [ ] Create `evaluations/knowledge_synthesis.md` — knowledge synthesis evaluation
- [ ] Create `evaluations/predict_next_task.md` — next-task prediction evaluation
- [ ] Create `evaluations/schema_migration.md` — schema migration evaluation

### 11.5 Missing Interface/Config Files
- [ ] Create `interfaces/objective05.md` — Objective05 execution plan schema
- [ ] Create `interfaces/memory_api.md` — Memory API specification
- [ ] Create `interfaces/filesystem.md` — Filesystem layout specification

### 11.6 Infrastructure / DevOps
- [ ] Set up Ollama for local model serving (default embedding + language models)
- [ ] Create Docker configuration for production deployment
- [ ] Create installation script (install.sh / install.ps1)
- [ ] Create first-run wizard
- [ ] Document system requirements (RAM, disk, CPU, GPU)
- [ ] Implement crash reporting (opt-in)
- [ ] Implement update mechanism

### 11.7 Build & Release
- [ ] Create version numbering scheme (semver)
- [ ] Implement CHANGELOG.md
- [ ] Create release workflow (tag → build → publish)
- [ ] Define backward compatibility policy

---

## 12. Program-wide Tasks

- [ ] Ensure every task satisfies the Definition of Completion (BUILDING.md):
  1. Relevant architecture documentation updated and accurate
  2. All associated schemas defined and versioned
  3. Implementation code written, passes linting/typechecking, follows style
  4. All unit and integration tests pass
  5. All relevant evaluations pass
  6. Audit log correctly populated by new functionality
  7. User notified of completion
- [ ] Maintain cross-references between all documents (no dead links)
- [ ] Keep glossary up to date as new concepts are introduced
- [ ] Update `spec.md` as implementation reveals spec gaps
- [ ] Track all 6 open questions (Q1–Q6) and resolve before their blocking phases

---

## Summary

| Area | Count |
|------|-------|
| Pre-implementation critical fixes | ~20 sub-tasks |
| Phase 1: Foundation | ~35 sub-tasks |
| Phase 2: Observation | ~25 sub-tasks |
| Phase 3: Extraction | ~30 sub-tasks |
| Phase 4: Memory | ~25 sub-tasks |
| Phase 5: Identity Graph | ~25 sub-tasks |
| Phase 6: Persona Engine | ~20 sub-tasks |
| Phase 7: Digital Twin | ~25 sub-tasks |
| Phase 8: Action Engine | ~25 sub-tasks |
| Phase 9: Synthesis | ~30 sub-tasks |
| Phase 10: Autonomy & Eval | ~25 sub-tasks |
| Cross-cutting infrastructure | ~35 sub-tasks |
| Missing files to create | ~14 files |
| Open questions to resolve | 6 |

**Estimated total: ~300+ actionable sub-tasks**
