# SELF Architecture Critique and Update Directive

> **Purpose:** This document is the authoritative brief for the first coding session.
> The agent must read this document first, then propagate every noted change
> into the affected files before writing a single line of implementation code.
> Changes are ordered by severity. Each section names the exact files to touch,
> the specific text to revise, and the rationale drawn from current research.

**Prepared:** June 2026  
**Scope:** All documents under `architecture/`, `decisions/`, `schemas/`, `roadmap/`, `spec.md`, `CONSTITUTION.md`, `interfaces/`, and `security/`

---

## Critical Severity — Fix Before Any Implementation

### C-1 · Kuzu Is Archived; Graph Substrate Decision Is Broken

**Status:** COMPLETED ✅

**Solution.**  
LadybugDB is the community-designated successor to Kuzu. It is actively developed, retains Cypher, columnar storage, vector indices, and has a permissive MIT license. Neo4j Community Edition remains the supported alternative for users who require a client-server model or enterprise support.

**Post-archive fork lineage:**

| Fork | Status (June 2026) | Notes |
|---|---|---|
| **LadybugDB** (`LadybugDB/ladybug`) | Actively developed, MIT licence, Cypher + columnar + vector index | Community-driven successor; "the most viable Kuzu replacement" per the graph DB community |

**Note:** The Vela-Engineering/kuzu fork was not selected for SELF because it adds concurrent multi-writer support which is overkill for SELF's single-user model, and LadybugDB is the community-designated successor.

**Files Updated:**
- ✅ `architecture/storage.md` - Replaced Kuzu with LadybugDB (default) or Neo4j (enterprise fallback)
- ✅ `architecture/identity_graph.md` - Replaced Kuzu with LadybugDB (default) or Neo4j (enterprise fallback)
- ✅ `spec.md` § 5.2 - Replaced "Kuzu or Neo4j" with "LadybugDB (default) or Neo4j (enterprise fallback)"
- ✅ `decisions/ADR-0001-local-first.md` - Added Revision section
- ✅ `interfaces/storage.md` - Replaced Kuzu with LadybugDB (default) or Neo4j (enterprise fallback)
- ✅ `schemas/relationship.md` - Replaced Kuzu with LadybugDB (default) or Neo4j (enterprise fallback)
- ✅ `schemas/identity_node.md` - Replaced Kuzu with LadybugDB (default) or Neo4j (enterprise fallback)
- ✅ `roadmap/phase_01_foundation.md` - Replaced Kuzu with LadybugDB (default) or Neo4j (enterprise fallback)
- ✅ `roadmap/phase_05_identity.md` - Replaced Kuzu with LadybugDB (default) or Neo4j (enterprise fallback)
- ✅ `decisions/ADR-0002-graph-substrate.md` - Created new ADR

**New file to create.**

Create `decisions/ADR-0002-graph-substrate.md` with the following structure:

```markdown
# ADR-0002: Graph Substrate Selection

## Status
Accepted (supersedes implicit Kuzu default)

## Context
The original Kuzu embedded graph database was archived in October 2025.
Its on-disk format was never stable across minor releases, directly
violating SELF's Article IX (Continuity) requirement.

## Decision
LadybugDB (github.com/LadybugDB/ladybug) is the default graph substrate.
It is the community-designated successor to Kuzu, retains Cypher, columnar
storage, vector indices, and a permissive MIT licence. Neo4j Community
Edition remains the supported alternative for users who require a
client-server model or enterprise support.

## Consequences
- LadybugDB's storage format stability must be verified before each SELF
  minor release and documented in the changelog.
- If LadybugDB's development ceases, the fallback is Neo4j Community
  Edition. A migration path between the two must be maintained.

## Compliance
Directly supports Article IX §1 (data formats outlive code) and
Article II §1 (local-first).
```

---

### C-2 · DuckDB Multi-Process Write Restriction Is Undocumented; Will Cause Data Loss

**Problem.**  
The SELF architecture expects multiple subsystems (Observer, Extractor, Action Engine, Persona Engine, Synthesis Engine) to write to DuckDB concurrently. DuckDB explicitly does not support concurrent writes from multiple processes to the same database file — and likely never will, by design, because it is an in-process database. Cross-process concurrent writes produce lock errors or silent data corruption. None of the architecture documents warn about this. The phrase "Multiple subsystems may write concurrently; the storage layer must enforce serialization or use conflict-free replicated data types where appropriate" appears in `architecture/memory.md` without specifying *how*, which a coding agent will implement incorrectly.

DuckDB within a single process supports multiple connections (cursors) writing to disjoint tables, and appends to the same table never conflict. Cross-table UPDATE/DELETE from two cursors uses optimistic concurrency control and will fail on conflict.

**Files to update.**

| File | Change |
|---|---|
| `architecture/storage.md` — Substrate: DuckDB section | Add a **Concurrency Constraint** subsection: "DuckDB must be opened by exactly one OS process. All subsystems within that process may hold separate connections (cursors) to the same DuckDB file. Cross-process access is not supported and will produce lock errors. The Orchestration layer is the process boundary; it owns the DuckDB connection pool." |
| `architecture/memory.md` — Edge Cases: "Concurrent writes" | Replace the vague note with: "Concurrent writes are handled through DuckDB cursor isolation within a single process. The Orchestration layer serializes cross-table UPDATE/DELETE operations through the Write Queue component. Appends (INSERT) are conflict-free. No two OS processes may hold a read-write connection to the same DuckDB file simultaneously." |
| `architecture/orchestration.md` — Internal Components | Add a **Write Queue** component: "A serializing queue for UPDATE and DELETE operations issued to DuckDB. All subsystems enqueue writes rather than calling the Storage API directly for mutations. Appends bypass the queue." |
| `spec.md` § 5.2 — The Substrates | Add a note after the DuckDB entry: "DuckDB is a single-process embedded database. The Storage subsystem must own all read-write access; no subsystem may open a second DuckDB file handle in a separate process." |

---

### C-3 · Prompt Injection Defense Is Pattern-Matching Only; Insufficient for SELF's Attack Surface

**Problem.**  
`architecture/digital_twin.md` and `security/threat_model.md` describe prompt injection defense as pattern matching ("Detects attempts to override system instructions … Strips or escapes dangerous patterns"). Current research (OWASP LLM Top 10 2025, academic literature through early 2026) demonstrates that pattern-matching defenses reliably fail against optimization-based attacks and indirect injection through retrieved content. SELF's threat surface is particularly acute because:

1. The Observer ingests untrusted content (email bodies, web pages, RSS items, git commit messages) that flows directly into extraction prompts.
2. The Digital Twin feeds retrieved knowledge objects back into the LLM — classic RAG poisoning surface (OWASP LLM08:2025).
3. The Action Engine acts on Twin output — an attacker who poisons one knowledge object could ultimately trigger an unauthorized action.

The Constitution (Article VII §7) already states "Adversarial inputs are assumed. Prompts, web content, and email are untrusted. The system must not execute instructions embedded in observed data." But the architecture documents do not implement this with sufficient depth.

**Files to update.**

| File | Change |
|---|---|
| `security/threat_model.md` — Section 2 (Prompt Injection) | Expand mitigations to include: structural query separation (treat retrieved content as data, never as instruction); explicit trust-tier tagging on all prompt segments; a secondary classifier model whose sole job is to flag injection-suspicious content before it reaches the primary model; rate-limiting on re-extracted content from a single source that newly triggers high-confidence knowledge objects. |
| `architecture/digital_twin.md` — Prompt Sanitizer | Replace "Detects attempts to override system instructions … Strips or escapes dangerous patterns" with a three-layer model: (1) Structural isolation — retrieved content is injected into a fixed slot that the primary model is instructed to treat as data; (2) Secondary classifier — a lightweight model (distinct from the generation model) scores each retrieved segment for injection likelihood before assembly; (3) Citation-lock — if the generation model's output references a knowledge object not in the declared retrieval set, the response is rejected and regenerated. |
| `architecture/extraction.md` — Failure Modes table | Add row: `Indirect prompt injection in source content | Secondary classifier score exceeds threshold | Quarantine source event, emit security alert, surface to user.` |
| `architecture/security.md` — Article VII §7 implementation | Add a new subsystem component: **Injection Classifier** — "A lightweight model or fine-tuned classifier that scores all untrusted input segments (email bodies, page content, commit messages, note text) for prompt injection likelihood before they enter any extraction prompt. Outputs a score and a flag. Flagged content is quarantined and logged before the primary model sees it." |

---

## High Severity — Fix Before Phase 2 Implementation

### H-1 · Embedding Model Specification Is Underspecified; Will Produce Incomparable Vectors

**Problem.**  
`architecture/persona_engine.md` and `schemas/persona_vector.md` both acknowledge model swaps require re-anchoring, but neither document specifies what model to actually use, what dimension to target, or how to handle the fact that two persona vectors computed by different models cannot be compared in vector space. The example in `schemas/persona_vector.md` uses `qwen3-embedding-8b` (1024 dims) but this is never justified or referenced in any decision record. Meanwhile, the embedding model landscape has matured significantly: as of mid-2026, `nomic-embed-text` (768 dims, fully local via Ollama), `mxbai-embed-large` (1024 dims), and `llama-embed-nemotron-8b` (4096 dims) are the leading locally-runnable options. Mixing these silently will corrupt the persona trajectory.

**Files to update.**

| File | Change |
|---|---|
| `architecture/persona_engine.md` — Embedding Computer | Add: "The embedding model is pinned per SELF installation. The active model is stored in configuration alongside a `model_lineage_id` UUID. All vectors in a lineage share a model; cross-lineage similarity is prohibited. When a model swap occurs, the entire persona trajectory must be re-embedded under the new model before the system resumes normal operation. Partial re-embedding is not permitted." |
| `schemas/persona_vector.md` — Versioning Strategy | Expand the model-swap paragraph: "Implementations must refuse to compute cosine similarity between vectors from different `model_lineage_id` values. The re-anchoring procedure creates a new lineage, re-embeds all contributing knowledge IDs under the new model, and marks all prior snapshots as `lineage_archived`." |
| `interfaces/local_models.md` | Add a **Recommended Embedding Models** section listing `nomic-embed-text` (Ollama, 768 dims, default for memory-constrained systems), `mxbai-embed-large` (Ollama, 1024 dims, balanced), and `llama-embed-nemotron-8b` (Ollama, 4096 dims, high-fidelity but slow on CPU). Note that all three are available via `ollama pull`. |

**New file to create.**

Create `decisions/ADR-0003-embedding-model.md`:

```markdown
# ADR-0003: Embedding Model Default

## Status
Accepted

## Context
Persona vectors computed by different embedding models occupy incomparable
vector spaces. Mixing models without explicit lineage tracking silently
corrupts similarity scores and persona trajectories.

## Decision
The default embedding model is `nomic-embed-text` (768 dimensions) served
via Ollama. It is fully local, MIT-licensed, and fits within 4 GB RAM.
`mxbai-embed-large` (1024 dims) is the upgrade path for users with 8+ GB RAM.
All vectors are tagged with a `model_lineage_id`. Cross-lineage similarity
computations are prohibited at the storage layer.

## Consequences
A model swap triggers a full re-embedding pass. Until that pass completes,
the system operates in degraded mode: the persona engine reads from the last
complete lineage and queues new updates.

## Compliance
Supports Article VI (Model Independence) and Article V (Provenance).
```

---

### H-2 · The Audit Log Has No Integrity Mechanism; Append-Only Claim Is Unenforceable

**Problem.**  
`architecture/orchestration.md` and `architecture/memory.md` both describe an "append-only audit log" and state "The user can verify that the log is intact." But no document specifies *how* integrity is verified. Without a cryptographic mechanism, any process with filesystem access can silently truncate or edit the log. This directly undermines Article III (Auditability) of the CONSTITUTION.

A standard approach: hash-chaining (each entry includes the SHA-256 of the previous entry's hash), similar to certificate transparency logs. This gives O(1) tamper detection per entry and a full Merkle-style proof for any range.

**Files to update.**

| File | Change |
|---|---|
| `architecture/orchestration.md` — Audit Logger | Add: "Each audit log entry includes a `prev_hash` field containing the SHA-256 of the previous entry's canonical JSON. The log head hash is stored in a separate, user-readable `audit_head.sha256` file updated atomically on each write. Integrity verification reads the chain from any entry forward, recomputing hashes." |
| `architecture/memory.md` — Audit Log | Add: "The Audit Log is hash-chained. Any gap, truncation, or edit is detectable by re-computing the chain from the genesis entry. The `memory.audit_log_integrity` metric reports the result of the most recent integrity check." |
| `security/threat_model.md` — Section 6 (State Corruption) | Add: "Audit log tampering is detected via hash-chain verification. The chain is checked on startup and on demand. A broken chain halts the system and alerts the user." |

---

### H-3 · Bitemporal Modeling Is Missing; "As Of" Queries Will Produce Wrong Answers

**Problem.**  
`architecture/identity_graph.md` models nodes and edges with `valid_from` / `valid_to` fields for "valid time" (when was something true in the world), but makes no mention of "transaction time" (when did SELF learn about it). This matters in practice: if SELF learns on June 1 that a project started on January 1, a query for "what was I doing in February?" should return that project even though SELF did not know about it until June. Without bitemporal indexing, such queries either return wrong results or require full-table scans of the audit log.

The research literature on temporal knowledge graphs (including the Zep agent memory architecture, published January 2025) converges on bitemporal storage as the minimum viable design for long-lived personal memory systems.

**Files to update.**

| File | Change |
|---|---|
| `architecture/identity_graph.md` — Temporal Index | Add: "The temporal index is bitemporal: it tracks both `valid_time` (when the fact was true in the world) and `transaction_time` (when SELF recorded the fact). Queries default to valid-time semantics. Audit-time queries use transaction-time semantics. The `Temporal Index` component maintains separate B-tree indexes for both dimensions." |
| `schemas/identity_node.md` | Add two fields to the top-level fields table: `recorded_at` (ISO 8601, required) — when SELF first recorded this node; `recorded_updated_at` (ISO 8601, required) — when SELF last updated its record. Add validation requirement: "`recorded_at` must be less than or equal to `valid_from` when both are present." |
| `schemas/relationship.md` | Same addition: `recorded_at` and `recorded_updated_at` fields. |
| `spec.md` — Section 3.3 (Identity Node) | Add: "Identity nodes use bitemporal modeling. `valid_time` tracks when a fact was true in the world; `transaction_time` tracks when SELF learned it. Queries must specify which time axis they operate on." |

---

### H-4 · No Forgetting or Decay Mechanism for Knowledge Objects; System Will Become Unusable Over Time

**Problem.**  
The current architecture treats every knowledge object as permanent until explicitly deleted by the user. Over years of operation, this produces an unbounded corpus of contradictory, superseded, and low-confidence knowledge objects that will degrade retrieval quality, inflate persona vectors, and slow semantic search. The synthesis engine's `importance` ranking is mentioned but never defined. No document specifies how to handle the equivalent of human forgetting — the natural decay of low-signal knowledge.

Academic research on long-term AI memory (MemoryOS 2025, Reflective Memory Management 2025) converges on a tiered memory model: hot (recent, high-confidence), warm (older but reinforced), cold (low-signal, candidate for archival), and archived (retained for provenance but excluded from retrieval).

**Files to update.**

| File | Change |
|---|---|
| `architecture/memory.md` — Compaction Engine | Expand to describe a **Relevance Scorer** that runs during compaction: scores each knowledge object on recency, reinforcement count, confidence, and consistency with the current persona. Objects scoring below a configurable threshold are moved to a `cold` tier, excluded from semantic retrieval but retained for provenance. Objects in the `cold` tier for longer than a configurable window are moved to `archived` (filesystem-only, not indexed). |
| `architecture/persona_engine.md` — Decay Engine | Expand: "The decay engine runs nightly. It applies a configurable decay function to the influence weight of each knowledge object on the persona vector. Objects not reinforced within the decay horizon contribute diminishing influence. Decay does not delete knowledge objects; it reduces their weight in future persona updates." |
| `architecture/synthesis_engine.md` — Content Aggregator | Add: "The aggregator excludes `archived` knowledge objects from synthesis input unless the query explicitly requests historical content. It logs the exclusion count in the synthesis audit record." |
| `roadmap/phase_04_memory.md` | Add deliverable: "[ ] Relevance Scorer and tiered storage (hot/warm/cold/archived)." |

---

## Medium Severity — Fix Before Phase 3 Implementation

### M-1 · Schema Versioning Strategy Lacks a Migration Runner Specification

**Problem.**  
Every schema file states "standard semantic versioning; see `schemas/observation_event.md`" for the migration strategy, but `observation_event.md` only describes the *policy* (major bump = breaking, migration required) without specifying the *mechanism*. There is no `tools/schema_migrate/` directory referenced, no migration runner interface, and no description of how the coding agent should implement cross-version reads. A coding agent will invent something inconsistent.

**Files to update.**

| File | Change |
|---|---|
| `schemas/observation_event.md` — Versioning Strategy | Add a **Migration Runner Interface** subsection: "Migrations are implemented as versioned Python modules in `tools/schema_migrate/`. Each module exports a `migrate(record: dict, from_version: str, to_version: str) -> dict` function. The Storage subsystem automatically applies the chain of migrations on read when a record's `schema_version` does not match the current version. Migrations are idempotent. The migration chain is tested in `evaluations/schema_migration.md`." |
| All other schema files that reference "see `schemas/observation_event.md`" | Add a one-line note: "Migration runner specification: see `schemas/observation_event.md` — Migration Runner Interface." |

**New file to create.**

Create `evaluations/schema_migration.md`:

```markdown
# Evaluation: Schema Migration

## Purpose
Verify that the migration runner correctly transforms records written under
any prior schema version to the current version without data loss.

## Methodology
1. For each schema type, load a fixture written under each supported
   prior version.
2. Run the migration chain.
3. Validate the output against the current schema.
4. Verify that provenance is preserved.

## Success Criteria
- 100% of fixture records migrate without error.
- 0% data loss (all required fields present after migration).
- Provenance chain intact.
- Migration is idempotent (running twice produces the same result).
```

---

### M-2 · Onboarding / First Run Is Severely Underspecified

**Problem.**  
`spec.md` § 8.1 (First Run) states the system "initializes its storage substrates … does not perform synthesis until enough observations have accumulated" but defines "enough" nowhere. The Persona Engine requires an initial vector, which must be seeded from something — but the document only says "or a seed derived from a brief onboarding" without specifying what that onboarding looks like, what questions it asks, or how the answers are encoded into the initial vector. The roadmap's `phase_01_foundation.md` does not include an onboarding UX deliverable. A cold-start persona engine that returns a zero vector will produce nonsensical consistency scores from day one.

**Files to update.**

| File | Change |
|---|---|
| `spec.md` — Section 8.1 (First Run) | Add: "The first-run onboarding collects a structured self-description from the user: current role, top three interests, top three active projects, and one free-form statement. This is encoded as a seed `observation_event` of type `system.onboarding` and processed through the Extractor to produce the initial knowledge objects. The Persona Engine uses these objects to compute the seed persona vector. Synthesis is suppressed until at least 7 days of observations have accumulated or the user explicitly requests it." |
| `roadmap/phase_01_foundation.md` — Deliverables | Add: "[ ] Onboarding flow specification and implementation (structured self-description → seed observation event → seed persona vector)." |
| `architecture/persona_engine.md` — Edge Cases | Add: "Cold start — when the user is new, the persona vector is seeded from the onboarding observation event. The system must not operate with a zero vector; it must defer initialization until at least one onboarding event has been processed." |

---

### M-3 · The Objective05 Interface Is Referenced Everywhere But Never Defined

**Problem.**  
`architecture/action_engine.md` references `interfaces/objective05.md` in its very first paragraph and throughout the architecture, but that file does not exist in the repository. No schema, interface, or roadmap document defines what an "Objective05-style execution layer" actually looks like from a protocol, API, or data-contract perspective. A coding agent cannot implement the Action Engine without this. Given that the project repo is at `github.com/kliewerdaniel/qwen` (referenced in `schemas/project.md`), this is presumably the Objective03/Objective05 project referenced in project context, but it is not documented here.

**Files to update.**

| File | Change |
|---|---|
| `architecture/action_engine.md` — Purpose paragraph | Replace `See interfaces/objective05.md` with: "The Objective05 execution pattern is documented in `interfaces/objective05.md`. Until that document is authored, the Action Engine treats an execution plan as a sequence of typed steps, each with a `capability_id`, `inputs`, `preconditions`, `postconditions`, and `rollback_step`. This is the minimal contract; `interfaces/objective05.md` will formalize it." |

**New file to create.**

Create `interfaces/objective05.md` with a minimal stub:

```markdown
# Interface: Objective05 Execution Layer

> Status: Stub — to be fleshed out before Phase 8 implementation.

## Purpose
Objective05 is the declarative action-execution pattern used by SELF's
Action Engine. An Objective05 plan is a typed, verifiable sequence of steps
that the Action Engine executes in a sandboxed environment.

## Execution Plan Schema (minimal)

```json
{
  "plan_id": "UUID",
  "capability_id": "string",
  "steps": [
    {
      "step_id": "UUID",
      "capability_id": "string",
      "inputs": {},
      "preconditions": ["string"],
      "postconditions": ["string"],
      "rollback_step": {}
    }
  ]
}
```

## References
See `architecture/action_engine.md` for the Action Engine's use of plans.
See `schemas/action_request.md` for the upstream data contract.
```

---

### M-4 · Evaluation Framework Has No Execution Timeline; Will Be Skipped Under Pressure

**Problem.**  
`architecture/evaluation.md` is comprehensive on what to evaluate, but the roadmap phases do not integrate evaluation milestones. Each phase says "Evaluation X passes" in the Success Criteria, but there is no corresponding deliverable in the phase's Deliverables list for *building* the evaluation harness. Under implementation pressure, this will result in evaluations being deferred indefinitely.

**Files to update.**  
For each roadmap file, add an evaluation harness deliverable:

| File | Deliverable to add |
|---|---|
| `roadmap/phase_02_observation.md` | `[ ] Build evaluation harness for evaluations/discover_project.md` |
| `roadmap/phase_03_extraction.md` | `[ ] Build evaluation harness for evaluations/extract_belief.md and evaluations/detect_goal.md (create these files if not present)` |
| `roadmap/phase_04_memory.md` | `[ ] Build evaluation harness for evaluations/memory_retrieval.md (create if not present)` |
| `roadmap/phase_05_identity.md` | `[ ] Build evaluation harness for evaluations/build_identity_snapshot.md (create if not present)` |
| `roadmap/phase_06_persona.md` | `[ ] Build evaluation harness for evaluations/update_persona.md (create if not present)` |
| `roadmap/phase_07_digital_twin.md` | `[ ] Build evaluation harnesses for evaluations/memory_retrieval.md and evaluations/knowledge_synthesis.md (create latter if not present)` |
| `roadmap/phase_09_continuous_synthesis.md` | `[ ] Build evaluation harness for evaluations/predict_next_task.md (create if not present)` |

---

### M-5 · No Data Volume Budget; System Will Silently Degrade on Long-Running Installations

**Problem.**  
SELF is explicitly described as a "years-long" system, but no document estimates or bounds data volumes. Practical estimates: a moderately active user generates 50–500 filesystem events per day, 10–50 git commits per week, 20–100 emails per day, and 5–20 RSS items per day. Over three years, the observation event table could accumulate 50,000–500,000 raw events. If every event produces 3–5 knowledge objects (generous), the knowledge store holds 150,000–2,500,000 objects. A FAISS index over 2.5 million 1024-dim float32 vectors requires ~10 GB RAM. No document warns about this.

**Files to update.**

| File | Change |
|---|---|
| `architecture/memory.md` — Metrics section | Add a `memory.projected_size_3yr` metric and a note: "The Compaction Engine must be tuned such that the cold+archived tier absorbs the majority of accumulated events. A SELF installation should target fewer than 100,000 active (hot/warm) knowledge objects in the semantic index." |
| `architecture/storage.md` — Substrate: Vector Database | Add: "The default FAISS index uses Product Quantization (PQ) compression when the knowledge object count exceeds 50,000. This reduces memory from ~4 MB/1K objects (float32, 1024 dims) to ~0.2 MB/1K objects at modest accuracy cost. The Storage API exposes an `index_compression` configuration option." |
| `roadmap/phase_04_memory.md` — Risks | Add: "Data volume growth — a long-running installation can accumulate millions of objects. The tiered storage and index compression strategies must be in place before any production deployment." |

---

## Low Severity — Quality and Consistency Improvements

### L-1 · Glossary Gaps and Inconsistencies

**Problem.**  
`docs/glossary.md` is missing several terms used throughout the architecture documents: `cold tier`, `warm tier`, `hot tier`, `transaction time`, `valid time`, `model lineage`, `capability` (as used in the Action Engine), `bitemporal`, `injection classifier`, and `Write Queue`. The term "Digital Twin" is defined but its abbreviation "Twin" is used interchangeably in some documents and as "the Twin" in others.

**Files to update.**

| File | Change |
|---|---|
| `docs/glossary.md` | Add all missing terms. Standardise "Digital Twin" — always use the full term on first mention in each document, abbreviate as "Twin" thereafter. |

---

### L-2 · Security Architecture Conflates Process Isolation with Sandboxing

**Problem.**  
`architecture/security.md` describes a Sandbox Manager that "provides isolated environments for code, models, and actions." But the Action Engine's Sandbox Manager is a separate component described in `architecture/action_engine.md`. These two components overlap without referencing each other. A coding agent will implement two separate sandbox managers or conflate them.

**Files to update.**

| File | Change |
|---|---|
| `architecture/security.md` — Sandbox Manager | Add: "The Security Sandbox Manager is a shared service. The Action Engine's Sandbox Manager delegates to it. A single sandbox pool is maintained; it is not duplicated per subsystem." |
| `architecture/action_engine.md` — Sandbox Manager | Add: "The Action Engine's Sandbox Manager is a client of the Security subsystem's Sandbox Manager. It does not implement sandboxing independently." |

---

### L-3 · The `spec.md` Section 12 Open Questions Are Not Tracked

**Problem.**  
`spec.md` § 12 lists six open questions (Q1–Q6) that affect fundamental design choices (synthesis cadence, silence modeling, forgetting, action authorization granularity). None of these are cross-referenced to the architecture documents that are blocked on them, and none appear in the roadmap as decision milestones.

**Files to update.**

| File | Change |
|---|---|
| `spec.md` — Section 12 | For each open question, add a cross-reference to the affected architecture document(s) and the roadmap phase in which it must be resolved. |
| `roadmap/phase_01_foundation.md` | Add a non-implementation deliverable: "[ ] Resolve Q1 (minimum viable observation surface) and Q6 (action authorization granularity) before Phase 2 begins." |
| `roadmap/phase_03_extraction.md` | Add: "[ ] Resolve Q2 (conflicting sources) before implementation." |
| `roadmap/phase_09_continuous_synthesis.md` | Add: "[ ] Resolve Q3 (synthesis cadence), Q4 (silence modeling), and Q5 (forgetting model) before implementation." |

---

### L-4 · Privacy Model Mentions GDPR/CCPA But Gives No Actionable Guidance

**Problem.**  
`security/privacy_model.md` § 8 states "SELF is designed to be compliant with major privacy regulations (GDPR, CCPA, etc.)" but provides no actionable requirements. In practice, GDPR Article 17 (Right to Erasure) requires that deletion cascade to all derived records — this is partially addressed in schema-level notes but not enforced at the system level. GDPR Article 20 (Portability) requires that exported data be in a "commonly used, machine-readable format" — the export format is unspecified.

**Files to update.**

| File | Change |
|---|---|
| `security/privacy_model.md` — Section 8 | Replace the single paragraph with three subsections: (1) **Right to Erasure (GDPR Art. 17)** — "A deletion request for any knowledge object, observation event, or identity node must cascade through the full provenance chain. The cascade is logged in the audit log. The system must confirm completion to the user with a count of deleted and redacted records." (2) **Right to Portability (GDPR Art. 20)** — "The export format is newline-delimited JSON (NDJSON), one schema-conformant record per line, with a manifest file listing record counts by type and schema version." (3) **Data Minimization** — "The Observer's privacy filters are the primary minimization mechanism. Filters must be configurable per source and applied before any content enters the event store." |

---

## Agent Execution Instructions

The coding agent must execute the following steps in order before writing any implementation code:

1. Read this document in full.
2. For each change listed, open the target file, locate the relevant section, and apply the specified edit.
3. For each new file listed, create the file with the specified content.
4. After all document updates are complete, re-read `BUILDING.md` and confirm that all updated documents satisfy the Definition of Completion for documentation tasks.
5. Only after steps 1–4 are verified complete: proceed to Phase 1 implementation as defined in `roadmap/phase_01_foundation.md`.

Do not skip document updates to reach implementation sooner. The documentation is the system until the code exists.

**Note:** C-1 (Kuzu → LadybugDB migration) is now **COMPLETED**. All Kuzu references have been replaced with LadybugDB (default) or Neo4j (enterprise fallback) across all documentation files.

---

## Summary Table

| ID | Severity | Primary File | Action |
|---|---|---|---|
| C-1 | Critical | `architecture/storage.md`, `architecture/identity_graph.md`, `spec.md` | Replace Kuzu with LadybugDB; create ADR-0002 |
| C-2 | Critical | `architecture/storage.md`, `architecture/memory.md`, `architecture/orchestration.md` | Document DuckDB single-process constraint; add Write Queue |
| C-3 | Critical | `security/threat_model.md`, `architecture/digital_twin.md`, `architecture/extraction.md`, `architecture/security.md` | Upgrade prompt injection defense to three-layer model |
| H-1 | High | `architecture/persona_engine.md`, `schemas/persona_vector.md`, `interfaces/local_models.md` | Pin embedding model; add lineage system; create ADR-0003 |
| H-2 | High | `architecture/orchestration.md`, `architecture/memory.md`, `security/threat_model.md` | Add hash-chain audit log integrity |
| H-3 | High | `architecture/identity_graph.md`, `schemas/identity_node.md`, `schemas/relationship.md`, `spec.md` | Add bitemporal modeling |
| H-4 | High | `architecture/memory.md`, `architecture/persona_engine.md`, `architecture/synthesis_engine.md`, `roadmap/phase_04_memory.md` | Add tiered memory and decay mechanism |
| M-1 | Medium | `schemas/observation_event.md` + all schema files | Add migration runner spec; create `evaluations/schema_migration.md` |
| M-2 | Medium | `spec.md`, `roadmap/phase_01_foundation.md`, `architecture/persona_engine.md` | Specify onboarding and cold-start procedure |
| M-3 | Medium | `architecture/action_engine.md` | Create `interfaces/objective05.md` stub |
| M-4 | Medium | All `roadmap/phase_0*.md` files | Add evaluation harness deliverables |
| M-5 | Medium | `architecture/memory.md`, `architecture/storage.md`, `roadmap/phase_04_memory.md` | Add data volume budget and compression guidance |
| L-1 | Low | `docs/glossary.md` | Add missing terms |

**Status:** C-1 (Kuzu → LadybugDB migration) is now **COMPLETED** ✅
| L-2 | Low | `architecture/security.md`, `architecture/action_engine.md` | Reconcile duplicate Sandbox Manager |
| L-3 | Low | `spec.md`, `roadmap/phase_01_foundation.md`, etc. | Cross-reference open questions to roadmap phases |
| L-4 | Low | `security/privacy_model.md` | Add actionable GDPR/CCPA requirements |

**Status:** C-1 (Kuzu → LadybugDB migration) is now **COMPLETED**