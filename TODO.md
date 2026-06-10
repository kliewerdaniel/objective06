# SELF — Comprehensive Implementation TODO

> **State:** All 11 architecture specs implemented (Phases 1–9 + Cross-cutting).
> **213 tests passing**, ruff clean, format clean, mypy clean.
> This TODO aggregates every deliverable from the roadmap, architecture docs, schemas, evaluations, CRITIQUE_AND_UPDATES.md, open questions, and supporting docs.

---

## 0. Pre-Implementation — Repository Setup & Critical Fixes

### 0.1 Repository Infrastructure
- [x] Create `.gitignore` (Python, Node, OS files, IDE, DuckDB, FAISS, snapshot artifacts)
- [x] Choose primary language(s) and set up build system (Python/Pydantic)
- [x] Create `pyproject.toml`
- [x] Set up linting (ruff, mypy)
- [x] Set up formatting (ruff)
- [x] Set up pre-commit hooks (ruff, ruff-format, mypy)
- [x] Create `src/` directory structure matching the 12 subsystems
- [ ] Set up CI pipeline (GitHub Actions or equivalent)
- [x] Set up testing framework (pytest)
- [ ] Create `Makefile` or equivalent for common commands

### 0.2 Fix Critical Issues (from CRITIQUE_AND_UPDATES.md)

#### C-1 · Kuzu → LadybugDB
- [ ] `spec.md §5.2` — Change "Kuzu or Neo4j" to "LadybugDB (default) or Neo4j (enterprise fallback)"
- [ ] `architecture/storage.md` — Add LadybugDB install instructions pointer
- [ ] `architecture/identity_graph.md` Failure Modes table — Add "Substrate archived upstream — use LadybugDB fork"
- [ ] `decisions/ADR-0001-local-first.md` — Add Revision section noting LadybugDB
- [ ] Global consistency pass — Search all documents for bare "Kuzu"

#### C-2 · DuckDB Single-Process Constraint
- [x] Verify `architecture/storage.md` has the Concurrency Constraint subsection
- [x] Verify `architecture/orchestration.md` has Write Queue component
- [ ] Implement the Write Queue in code (serializing UPDATE/DELETE queue)

#### C-3 · Prompt Injection Defense — Three-Layer Model
- [x] `architecture/digital_twin.md` — Has three-layer model
- [x] `architecture/extraction.md` Failure Modes — Has injection row
- [x] `architecture/security.md` — Has Injection Classifier component
- [x] Implement Injection Classifier component in code
- [x] Implement Structural isolation in Digital Twin prompt assembly
- [ ] Implement Citation-lock validation in Digital Twin

### 0.3 Fix High-Severity Issues

#### H-1 · Embedding Model Lineage
- [x] Verify `architecture/persona_engine.md` has `model_lineage_id` pinned-model constraint
- [x] Implement `model_lineage_id` validation in code

#### H-2 · Audit Log Hash-Chain Integrity
- [x] Implement SHA-256 `prev_hash` chaining in audit log entries
- [x] Implement `audit_head.sha256` file with atomic updates
- [x] Implement startup integrity verification
- [x] Implement on-demand integrity check query

#### H-3 · Bitemporal Modeling
- [x] Verify `architecture/identity_graph.md` has bitemporal index description
- [x] Implement valid_time + transaction_time in TemporalIndex

#### H-4 · Forgetting / Decay Mechanism
- [x] Verify `architecture/memory.md` Compaction Engine has Relevance Scorer (MVP: recency×confidence)
- [x] Verify `architecture/persona_engine.md` has Decay Engine (stub exists)
- [x] Verify `architecture/synthesis_engine.md` has archived-object exclusion
- [x] Implement Relevance Scorer in CompactionEngine
- [x] Implement tier transitions (hot→cold→archive) in CompactionEngine
- [x] Implement nightly Decay Engine

### 0.4 Fix Medium-Severity Issues

#### M-1 · Schema Migration Runner
- [x] Create migration runner interface
- [x] Implement auto-apply on read in Storage subsystem

#### M-2 · Onboarding / Cold-Start Procedure
- [x] Implement onboarding flow: collect self-description, emit `system.onboarding` event
- [x] Implement seed persona vector generation from onboarding event
- [x] Implement deferred synthesis until ≥7 days or user request

#### M-3 · Objective05 Interface
- [x] Implement Objective05 plan structure in Action Engine (pre/postconditions, rollback)

#### M-5 · Data Volume Budget & Compression
- [ ] Add FAISS Product Quantization (PQ) compression when >50K objects

### 0.5 Fix Low-Severity Issues

#### L-2 · Sandbox Manager Duplication
- [x] Verify `architecture/security.md` Sandbox Manager is the shared service
- [x] Verify `architecture/action_engine.md` Sandbox Manager delegates to Security

#### L-3 · Open Questions Tracked in Roadmap
- [ ] Cross-reference Q1–Q6 to affected architecture docs and roadmap phases

---

## 1. Phase 1 — Foundation (Storage + Observability + Core Schemas)

### 1.1 Project Structure & Configuration
- [x] Create `src/self/` package structure
- [x] Implement configuration system (YAML-based)
- [x] Create default configuration file
- [x] Implement logging infrastructure

### 1.2 Storage Abstraction Layer
- [x] Define `StorageAPI` interface (get, query, insert, update, delete)
- [x] Implement `DuckDBAdapter` — analytical store (12 tables)
- [x] Implement `SchemaValidator` — validate records against schemas on write (16 record types)
- [x] Implement `MigrationEngine` — apply schema migrations
- [x] Implement `VectorDBAdapter` (FAISS) — semantic search
- [ ] Implement `LadybugDBAdapter` or graph store adapter — identity graph

### 1.3 Durable Event Log
- [x] Implement append-only event log on DuckDB
- [x] Implement time-range queries
- [x] Implement content-addressable raw payload storage
- [x] Implement replay from point-in-time

### 1.4 Audit Log
- [x] Implement append-only audit log
- [x] Implement hash-chain integrity (SHA-256 `prev_hash`)
- [x] Implement `audit_head.sha256` atomic file updates
- [x] Implement queryable audit log (by actor, action, time, entity)
- [x] Implement startup integrity verification
- [x] Implement on-demand integrity check

### 1.5 Metrics & Health Reporting
- [x] Implement metrics collection infrastructure
- [x] Implement HealthMonitor component
- [x] Implement heartbeats per subsystem

### 1.6 Core Schema Definitions (as code)
- [x] Implement `observation_event` schema (Pydantic)
- [x] Implement `knowledge_object` generic schema
- [x] Implement schema validation against field definitions
- [x] Implement schema versioning support

### 1.7 Onboarding Flow
- [x] Implement structured self-description collection
- [x] Implement seed `system.onboarding` observation event
- [x] Implement seed persona vector from onboarding event

### 1.8 Unit Tests — Storage & Observability
- [x] Unit tests for DuckDBAdapter (CRUD, query)
- [x] Unit tests for FAISS adapter (insert, search, rebuild)
- [x] Unit tests for SchemaValidator (accept, reject)
- [x] Unit tests for AuditLog (append, query, hash-chain)
- [x] Unit tests for EventLog (append, time-range query)

---

## 2. Phase 2 — Observation (Capture & Normalize)

### 2.1 Observer Subsystem Architecture
- [x] Implement Observer main component
- [x] Implement HealthMonitor per adapter
- [x] Integrate with Orchestration for scheduling/lifecycle
- [x] Integrate with Security for permission checks and secrets

### 2.2 Source Adapters
- [x] **FilesystemWatcher** adapter (polling)
- [x] **GitPollingAdapter** adapter (reflog polling)
- [ ] **GitHub Poller** adapter
- [ ] **RSS/Atom Feed** adapter
- [ ] **Email** adapter
- [ ] **Browser History** adapter
- [ ] **Terminal Session** adapter
- [ ] **Calendar** adapter

### 2.3 Normalizer
- [x] Implement stable ID assignment (SHA-256 content hash prefix)
- [x] Implement UTC timestamp resolution (monotonic + wall-clock)
- [x] Implement content hashing
- [x] Implement provenance metadata attachment

### 2.4 Ingest Queue
- [x] Implement bounded, persistent queue (DuckDB-backed)
- [x] Implement priority lanes (HIGH/MEDIUM/LOW)
- [x] Implement overflow protection

### 2.5 Event Log Writer
- [x] Implement append-only writer
- [x] Implement content-addressable raw payload storage
- [x] Implement index for fast lookup

---

## 3. Phase 3 — Extraction (Events → Knowledge)

### 3.1 Extractor Subsystem Architecture
- [x] Implement Extractor main component
- [x] Integrate with Memory (read events, write knowledge)
- [x] Integrate with Identity Graph (entity resolution)
- [x] Integrate with Local Models (inference)
- [x] Integrate with Orchestration (scheduling, retries)

### 3.2 Event Batcher
- [x] Implement time-based batching
- [x] Implement source-based batching

### 3.3 Prompt Library
- [x] Create versioned prompt templates: `extract_belief`, `detect_goal`, `discover_project`
- [x] Implement JSON output schemas per prompt

### 3.4 Model Client
- [x] Implement Ollama adapter
- [x] Implement retries with exponential backoff
- [x] Implement timeouts and token limits
- [x] Implement health check

### 3.5 Output Validator
- [x] Implement JSON parsing and schema validation
- [x] Implement required field verification
- [x] Implement safe type coercion

### 3.6 Knowledge Writer
- [x] Implement transactional writes to Memory
- [x] Implement audit log coordination

### 3.7 Confidence Scorer
- [x] Implement logprob-based scoring
- [x] Implement evidence strength scoring

### 3.8 Contradiction Detector
- [x] Implement semantic neighborhood comparison

---

## 4. Phase 4 — Memory (Storage + Retrieval + Compaction)

### 4.1 Memory Subsystem Architecture
- [x] Implement MemoryAPI (interfaces/memory_api.md)
- [x] Integrate all stores (Event, Knowledge, Summary, Audit Log, Vector Index)
- [x] Implement audit logging on every write

### 4.2 Event Store
- [x] Implement time-range query support
- [x] Implement content-addressable raw payload storage
- [x] Implement replay from point-in-time

### 4.3 Knowledge Store
- [x] Implement indexing by type, entity, confidence
- [x] Implement semantic search via vector index

### 4.4 Summary Store
- [x] Implement provenance linkage to underlying knowledge

### 4.5 Vector Index
- [x] Implement incremental index building
- [x] Implement k-nearest-neighbor queries
- [x] Implement replaceable backend (FAISS)

### 4.6 Snapshot Manager
- [x] Implement cross-store consistent snapshots
- [x] Implement point-in-time snapshots
- [x] Implement snapshot validation and restore (SHA-256 integrity)

### 4.7 Compaction Engine (with Relevance Scorer)
- [x] Implement Relevance Scorer (recency×confidence)
- [x] Implement hot→cold→archive tier transitions

### 4.8 Retention Manager
- [x] Implement per-type retention policies (1yr events, 2yr knowledge, 5yr audit)
- [x] Implement dry-run mode

### 4.9 Exporter / Importer
- [x] Implement portable versioned archive (JSON + SHA-256)
- [x] Implement integrity verification on import

---

## 5. Phase 5 — Identity Graph (Temporal Entity Model)

### 5.1 Identity Graph Subsystem Architecture
- [x] Implement IdentityGraph facade component
- [x] Integrate with Memory for persistence

### 5.2 Node Store
- [x] Implement node CRUD (14 node types)
- [x] Implement attribute store (free-form key-value)
- [x] Implement temporal validity tracking
- [x] Implement soft-delete with supersession

### 5.3 Edge Store
- [x] Implement edge CRUD (13 relationship types)
- [x] Implement weight tracking
- [x] Implement temporal validity tracking
- [x] Implement soft-delete

### 5.4 Temporal Index (Bitemporal)
- [x] Implement "as of time T" queries
- [x] Implement "during range [T1, T2]" queries
- [x] Implement edge temporal queries

### 5.5 Entity Resolver
- [x] Implement string similarity matching (difflib, threshold 0.8)
- [x] Record resolution decisions with provenance

### 5.6 Merge Engine
- [x] Implement node merging with provenance preservation
- [x] Implement edge re-targeting on merge
- [x] Implement merge logging in audit log

### 5.7 Evolution Tracker
- [x] Implement attribute change recording
- [x] Implement diff queries between time points
- [x] Implement history queries per entity

### 5.8 Query Engine
- [x] Implement path finding queries (DFS)
- [x] Implement neighborhood queries (configurable depth)
- [x] Implement type/edge counting

### 5.9 Schema Registry
- [x] Implement versioned node type definitions (14 types)
- [x] Implement versioned edge type definitions (13 types)

---

## 6. Phase 6 — Persona Engine (Vector Identity)

### 6.1 Persona Engine Subsystem Architecture
- [x] Implement PersonaEngine facade
- [x] Integrate with ModelClient for embeddings

### 6.2 Embedding Computer
- [x] Implement ModelClient-based embedding computation

### 6.3 Persona Vector Store
- [x] Implement time-indexed vector sequence storage
- [x] Implement current vector retrieval
- [x] Implement historical vector retrieval ("persona at time T")
- [x] Implement trajectory queries

### 6.4 Persona Updater
- [x] Implement moving average update strategy (configurable α)
- [x] Implement update provenance recording

### 6.5 Consistency Scorer
- [x] Implement cosine similarity scoring [0, 1]

### 6.6 Predictor
- [ ] Implement persona trajectory extrapolation

### 6.7 Decay Engine
- [x] Implement nightly decay run

### 6.8 Model Adapter
- [ ] Implement re-anchoring on model swap

---

## 7. Phase 7 — Digital Twin (Conversational Interface)

### 7.1 Digital Twin Subsystem Architecture
- [x] Implement DigitalTwin facade
- [x] Integrate with Memory (read events, knowledge)
- [x] Integrate with Identity Graph (entity queries)
- [x] Integrate with Persona Engine (trajectory)
- [x] Integrate with Local Language Model

### 7.2 Query Intake
- [x] Implement input validation
- [x] Implement prompt injection sanitization
- [x] Implement session establishment/extension

### 7.3 Intent Classifier
- [x] Implement intent classification (8 intents)
- [x] Implement confidence-based routing (threshold 0.3)

### 7.4 Query Decomposer
- [ ] Implement complex query → sub-query decomposition

### 7.5 Sub-Query Router
- [x] Implement per-subsystem routing (Memory, Identity Graph, Persona, Model)

### 7.6 Answer Composer
- [x] Implement constrained prompt generation
- [x] Implement grounding citations
- [x] Implement explicit uncertainty marking
- [x] Implement degraded mode (model unavailable)

### 7.7 Citation Tracker
- [x] Implement assertion → source record ID mapping
- [x] Expose formatted citations

### 7.8 Session Manager
- [x] Implement session state storage
- [x] Implement TTL expiry
- [x] Implement context maintenance (entities, intents)

### 7.9 Prompt Sanitizer (Three-Layer)
- [x] Layer 1: Structural isolation — retrieved content = data slot
- [x] Layer 2: Secondary injection classifier (regex patterns)
- [ ] Layer 3: Citation-lock — reject if output references undeclared knowledge

### 7.10 Permission Enforcer
- [ ] Check read authorization for requested state

---

## 8. Phase 8 — Action Engine (World Side-Effects)

### 8.1 Action Engine Subsystem Architecture
- [x] Implement ActionEngine facade
- [x] Integrate with Memory (persistence of action records, 3 tables)

### 8.2 Action Intake
- [x] Implement action request validation
- [x] Implement capability resolution

### 8.3 Permission Resolver
- [x] Implement explicit grant checking
- [x] Implement default-deny rules
- [x] Return yes/no/require-confirmation

### 8.4 Plan Synthesizer
- [x] Implement capability definition lookup
- [x] Implement precondition generation (parent dir exists)
- [x] Implement postcondition generation (file exists/readable)
- [x] Implement rollback plan generation (delete for write)

### 8.5 Capability Registry
- [x] Define initial capabilities: read_file, list_directory, write_file
- [x] Permission requirements per capability
- [x] Sensitivity level per capability

### 8.6 Sandbox Manager (delegates to Security)
- [ ] Implement execution isolation

### 8.7 Executor
- [x] Implement precondition evaluation (abort if fail)
- [x] Implement step-by-step execution (real file I/O)
- [x] Implement postcondition evaluation
- [x] Implement rollback trigger on postcondition failure

### 8.8 Rollback Engine
- [x] Implement reverse execution of rollback plan
- [x] Implement rollback success verification (idempotent)

### 8.9 Confirmation Manager
- [x] Implement user confirmation request
- [x] Implement TTL expiry for confirmation
- [x] Implement confirm/deny workflow

### 8.10 Result Emitter
- [x] Implement action result capture to storage
- [x] Implement audit trail (action_audit table)

### 8.11 Action Categories (Sensitivity Levels)
- [x] Implement read-only local (generally safe)
- [x] Implement write local (requires confirmation default)

---

## 9. Phase 9 — Continuous Synthesis (Summaries & Narratives)

### 9.1 Synthesis Engine Subsystem Architecture
- [x] Implement SynthesisEngine facade
- [x] Integrate with Memory (read state, write summaries)
- [x] Integrate with Identity Graph (entity context)
- [x] Integrate with Local Language Model

### 9.2 Summary Scheduler
- [ ] Implement user-configured cadences (daily, weekly)

### 9.3 Period Selector
- [x] Implement daily boundary selection
- [x] Implement topic-based selection
- [x] Implement project-based selection

### 9.4 Content Aggregator
- [x] Pull observations for period
- [x] Pull knowledge objects for period
- [x] Pull identity graph entities
- [x] Exclude archived objects
- [x] Log exclusion count

### 9.5 Prompt Builder
- [x] Use versioned prompt templates (4 templates)
- [x] Include aggregated state
- [x] Include grounding/citation instructions

### 9.6 Generation Engine
- [x] Implement local model-based generation
- [x] Implement retry on failure

### 9.7 Grounding Verifier
- [x] Implement claim→source term-overlap checking
- [x] Record grounding coverage metric

### 9.8 Provenance Linker
- [x] Record contributing observation/knowledge/graph IDs
- [x] Store links in summary provenance

### 9.9 Cache Manager
- [x] Implement summary caching with TTL

### 9.12 Synthesis Types
- [x] Daily Summary production
- [x] Weekly Summary production
- [x] Topic Summary production
- [x] Project Summary production

---

## 10. Phase 10 — Autonomy & Evaluation Framework

### 10.1 Self-Reflection Loop
- [ ] Implement system self-assessment (health, data quality, coverage gaps)

### 10.2 Capability Discovery & Proposal
- [ ] Implement capability inventory scanning

### 10.5 Evaluation Framework Implementation
- [x] Implement Evaluation Runner
- [x] Implement Ground Truth Manager
- [x] Implement Report Generator

---

## 11. Cross-Cutting Infrastructure

### 11.1 Orchestration Subsystem (Main Loop)
- [x] Implement Scheduler (interval-based, one-shot, recurring)
- [x] Implement Retry Manager (exponential backoff with jitter)
- [x] Implement Main Loop (start/stop/tick/run_forever)
- [x] Implement pipeline wiring (observer→extractor)
- [ ] Implement Event Bus (pub/sub)
- [ ] Implement Backpressure Manager
- [ ] Implement Write Queue
- [ ] Implement Lifecycle Manager

### 11.2 Security Subsystem
- [x] Implement Authentication Manager (token-based, SHA-256 hashed, session TTL)
- [x] Implement Authorization Engine (capability-based, grant/check/revoke, default-deny)
- [x] Implement Secret Manager (encrypted storage, cache)
- [x] Implement Injection Classifier (10 patterns, scoring, threshold)
- [ ] Implement Sandbox Manager
- [ ] Implement Anomaly Detector
- [ ] Implement Incident Responder

### 11.3 Evaluation Subsystem
- [x] Implement per-capability evaluation specifications
- [x] Implement evaluation running infrastructure

### 11.4 Missing Evaluation Files to Create
- [x] Create `evaluations/extract_belief.md`
- [x] Create `evaluations/detect_goal.md`
- [x] Create `evaluations/memory_retrieval.md`
- [x] Create `evaluations/build_identity_snapshot.md`
- [x] Create `evaluations/update_persona.md`
- [x] Create `evaluations/knowledge_synthesis.md`
- [x] Create `evaluations/predict_next_task.md`

### 11.5 Missing Interface/Config Files
- [ ] Create `interfaces/memory_api.md`

### 11.6 Infrastructure / DevOps
- [x] Set up Ollama for local model serving
- [ ] Create Docker configuration for production deployment
- [ ] Create installation script
- [ ] Create first-run wizard

### 11.7 Build & Release
- [ ] Create version numbering scheme (semver)
- [ ] Create CHANGELOG.md

---

## 12. Program-wide Tasks

- [ ] Ensure every task satisfies the Definition of Completion:
  1. Relevant architecture documentation updated and accurate
  2. All associated schemas defined and versioned
  3. Implementation code written, passes linting/typechecking
  4. All unit and integration tests pass
  5. All relevant evaluations pass
- [ ] Maintain cross-references between all documents
- [ ] Keep glossary up to date
- [ ] Track all 6 open questions (Q1–Q6) and resolve before their blocking phases

---

## Summary

| Area | Status |
|------|--------|
| Foundation (Phase 1) | ~95% — 12 DB tables, 16 schema validators, startup integrity verification |
| Observation (Phase 2) | ~80% — Normalizer, IngestQueue, 2 adapters |
| Extraction (Phase 3) | ~80% — ModelClient, PromptLibrary, Validator, Batcher, Writer |
| Memory (Phase 4) | ~90% — MemoryAPI, Snapshots, Compaction, Retention, Exporter |
| Identity Graph (Phase 5) | ~95% — All 9 modules |
| Persona Engine (Phase 6) | ~90% — VectorStore, Embeddings, Updater, Scorer, DecayEngine |
| Digital Twin (Phase 7) | ~80% — All 8 components |
| Action Engine (Phase 8) | ~85% — All 8 components, 3 capabilities |
| Synthesis Engine (Phase 9) | ~85% — All 7 components, 4 summary types |
| Orchestration (Cross-cutting) | ~60% — Scheduler, Retry, Main Loop, Pipeline |
| Security (Cross-cutting) | ~60% — Auth, Authorization, Secrets, Injection |
| Evaluations (Cross-cutting) | ~80% — Runner, Ground Truth, Report Generator |

**244 tests passing**, ruff clean, format clean, mypy clean across 120+ source files.
