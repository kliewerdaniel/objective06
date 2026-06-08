# Extractor Subsystem

> The Extractor transforms observation events into structured knowledge objects. It is the semantic interpretation layer of SELF.

---

## Purpose

The Extractor consumes raw `observation_event` records produced by the Observer and produces structured `knowledge_object` instances — beliefs, goals, projects, interests, relationships, and entities — that the rest of the system can reason over. It is the only subsystem that uses language models to produce knowledge.

The Extractor is conservative. It is biased toward precision over recall. It prefers to under-extract rather than hallucinate. Every output is grounded in source events and carries full provenance.

## Responsibilities

- Consuming observation events from the durable event log.
- Batching events into extraction units (by topic, by time window, by source).
- Applying extraction prompts to produce structured outputs.
- Validating outputs against schemas.
- Resolving entities against the identity graph (entity linking).
- Writing knowledge objects to Memory with provenance.
- Producing confidence scores for each output.
- Detecting and recording contradictions.
- Handling model unavailability gracefully.

## Inputs

- `observation_event` records from the Observer (via Memory).
- The current state of the identity graph (for entity resolution).
- A configured set of extraction prompt templates.
- A configured model endpoint.
- Configuration controlling batch size, concurrency, and prompt selection.

## Outputs

- `knowledge_object` records conforming to `schemas/knowledge_object.md`.
- Updates to the identity graph (`identity_node` and edge records).
- Confidence scores and reasoning traces.
- Extraction failure records.
- Metrics: extractions per minute, model latency, schema validation failures.

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Memory | Required | Read events, write knowledge objects. |
| Identity Graph | Required | Entity resolution and updates. |
| Local Models | Required | Inference. |
| Prompt Library | Required | Versioned prompt templates. |
| Orchestration | Required | Scheduling, retries. |
| Security | Required | PII detection, redaction. |

## Internal Components

### Event Batcher

Groups events into extraction units. Batching strategies include:

- **Time-based:** All events in a window (e.g., last 5 minutes).
- **Source-based:** All events from a single source.
- **Entity-based:** All events related to a single entity.
- **Trigger-based:** Specific event types force immediate extraction (e.g., a new repository creation).

The batcher is idempotent: the same event in multiple batches produces the same knowledge objects.

### Prompt Selector

Chooses which prompt template(s) to apply to a batch. Selection is based on:

- The event types in the batch.
- The current state of the identity graph.
- A configured cost / quality trade-off.
- Model capability tags.

### Model Client

Abstracts the model backend. The client:

- Speaks the model's native API.
- Implements retries with exponential backoff.
- Enforces timeouts and token limits.
- Logs every request and response (with content).
- Supports model failover to a secondary backend.
- Reports token usage and cost.

See `interfaces/local_models.md`.

### Output Validator

Validates model output against the target schema. The validator:

- Parses JSON or other structured formats.
- Verifies required fields.
- Coerces types when safe.
- Rejects outputs that fail validation, with reasons.
- Maintains a quarantine for repeated failures.

### Entity Linker

Resolves extracted entities to existing identity graph nodes. The linker:

- Uses string similarity, embedding similarity, and contextual features.
- Asks the model to disambiguate when ambiguous.
- Records the linking decision with provenance.
- Supports new entity creation when no match is found.

### Confidence Scorer

Produces a confidence score for each knowledge object. The scorer:

- Considers model logprobs where available.
- Considers the strength of supporting evidence.
- Considers contradictions with existing knowledge.
- Surfaces low-confidence objects for user review.

### Contradiction Detector

Identifies new knowledge objects that contradict existing ones. The detector:

- Compares new objects to existing objects in the same semantic neighborhood.
- Marks contradictions in the provenance chain.
- Does not auto-resolve; surfaces to the user or to the Synthesis Engine.

### Knowledge Writer

Persists knowledge objects to Memory. The writer:

- Is transactional with respect to identity graph updates.
- Updates the audit log.
- Emits events for downstream consumers (Synthesis, Persona).

## Data Contracts

The Extractor produces and consumes schemas defined in `schemas/`:

- Reads: `observation_event`, `identity_node`, existing `knowledge_object`.
- Writes: `knowledge_object` (of various subtypes), `identity_node` updates, `extraction_audit` records.

The output is strict JSON conforming to the schema. The Extractor is the only producer of knowledge objects in the system.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Model unavailable | Connection error | Retry, then queue, then alert. |
| Model timeout | Request timeout | Retry with shorter batch, then split. |
| Output validation failure | Schema check | Quarantine, log, retry with corrective prompt. |
| Entity linking ambiguous | Multiple candidates | Surface to user, use highest-confidence match. |
| Token limit exceeded | Truncation | Split batch, retry. |
| Rate limited | 429 response | Honor backoff, defer batch. |
| Conflicting outputs | Multiple models disagree | Surface as a contradiction, defer resolution. |

## Metrics

- `extractor.events_processed.total`
- `extractor.knowledge_objects_produced.total` (by type)
- `extractor.model_latency_ms` (p50, p95, p99)
- `extractor.tokens_consumed.total`
- `extractor.validation_failures.total` (by reason)
- `extractor.contradictions_detected.total`
- `extractor.entity_linking_accuracy` (when ground truth available)

## Future Evolution

- **Multi-model ensemble.** Run multiple models and reconcile.
- **Active learning.** Surface low-confidence extractions for human feedback.
- **Streaming extraction.** Extract from a stream rather than from batches.
- **Prompt optimization.** A/B test prompt variants against evaluation criteria.
- **Cross-lingual extraction.** Handle events in multiple languages.

## Edge Cases

- **Conflicting evidence within a batch.** When two events in the same batch disagree, the Extractor must produce two knowledge objects, each with its own provenance.
- **Partial extraction.** When the model returns some fields but not others, the Extractor may fill with `null` and a low confidence score.
- **Hallucinated entities.** The Extractor must not allow the model to invent entities not present in the source events. Entity names must be span-grounded to source text.
- **Very long batches.** The Extractor must chunk events and link across chunks.
- **Sensitive content.** The Extractor must detect and handle PII according to `security/privacy_model.md`.

## Acceptance Criteria for "Extractor is Complete"

1. All knowledge object subtypes have at least one working extraction prompt.
2. Entity linking resolves at least 90% of repeated entities to existing nodes in evaluation.
3. Contradictions are detected and recorded, not silently resolved.
4. The model client fails over to a secondary backend when the primary is unavailable.
5. Provenance chains are intact for every produced object.
6. Evaluations `detect_goal.md`, `extract_belief.md`, and `discover_project.md` pass.
