# Persona Engine Subsystem

> The Persona Engine maintains the vector representation of the user's identity. It produces a continuously updated, semantically meaningful embedding of "who the user is right now" and "how the user has changed over time."

---

## Purpose

The Persona Engine is SELF's continuous, semantic representation of the user. While the Identity Graph is structured and discrete, the Persona Engine is continuous and semantic. Together they form a dual representation: the graph answers "what entities are in the user's life and how are they related?"; the persona vector answers "what does the user feel like, semantically, right now?"

The persona vector is the basis for:

- Consistency checks: "is this new knowledge consistent with who the user is?"
- Predictions: "what would the user do next?"
- Retrieval: "what is the most relevant knowledge to surface for the user right now?"
- Synthesis: "how should the system describe the user in a summary?"

The persona is not a profile. It is a moving point in a high-dimensional space, anchored by the user's history.

## Responsibilities

- Maintaining the current persona vector.
- Maintaining the historical trajectory of persona vectors.
- Updating the persona vector incrementally as new knowledge objects arrive.
- Producing consistency scores for candidate knowledge.
- Producing predictions about user behavior.
- Producing similarity scores between knowledge and persona.
- Supporting "persona at time T" queries for retrospection.
- Surviving model changes (with re-anchoring).

## Inputs

- New knowledge objects from the Extractor.
- Identity graph changes.
- Existing persona vector and its history.
- Configuration: update rate, decay function, embedding model.
- Optional user feedback ("this is / is not like me").

## Outputs

- Updated persona vector.
- Persona trajectory (time series of vectors).
- Consistency scores for candidate knowledge.
- Predictions (e.g., next project, next contact, next interest).
- "Nearest knowledge" queries: what is the user closest to in their history?
- Metrics: drift, stability, update latency.

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Memory | Required | Read knowledge, write persona snapshots. |
| Identity Graph | Required | Read entity context. |
| Local Embedding Model | Required | Compute embeddings. |
| Orchestration | Required | Scheduling of updates and predictions. |
| Synthesis Engine | Required | Consumes persona for summaries. |
| Digital Twin | Required | Consumes persona for responses. |

## Internal Components

### Persona Vector Store

Stores the persona vector over time. The store:

- Holds a sequence of persona vectors indexed by time.
- Supports retrieval of the current vector.
- Supports retrieval of vectors at specific past times.
- Supports trajectory queries (vector deltas over time).
- Supports similarity queries (is the current persona close to a past persona?).

### Embedding Computer
Computes embeddings for knowledge objects and updates. The embedding computer:

- The embedding model is pinned per SELF installation. The active model is stored in configuration alongside a `model_lineage_id` UUID. All vectors in a lineage share a model; cross-lineage similarity is prohibited. When a model swap occurs, the entire persona trajectory must be re-embedded under the new model before the system resumes normal operation. Partial re-embedding is not permitted.
- Supports model swapping.
- Caches embeddings for unchanged content.
- Is model-version-aware: each embedding carries the model ID and version.


### Persona Updater

Updates the persona vector as new knowledge arrives. The updater:

- Computes the embedding of the new knowledge.
- Combines it with the current persona vector using a learned or configured rule.
- Supports multiple update strategies: moving average, exponential decay, time-weighted, attention-based.
- Records the update with provenance.
- Supports undo within a configurable window.

### Consistency Scorer

Scores candidate knowledge for consistency with the current persona. The consistency scorer:

- Computes cosine similarity between the candidate's embedding and the persona vector.
- Returns a score in [0, 1].
- Returns the top-N nearest persona snapshots for context.
- Records the score with provenance.

### Predictor

Predicts the user's next likely actions, interests, or knowledge acquisitions. The predictor:

- Uses the persona trajectory to extrapolate.
- Uses the identity graph to constrain predictions (e.g., "the user is more likely to learn about tools they already use").
- Returns a ranked list of predictions with confidence scores.
- Records predictions with provenance for later evaluation.

### Decay Engine

Models the temporal decay of persona influence. The decay engine:

- Runs nightly.
- Applies a configurable decay function to the influence weight of each knowledge object on the persona vector. Objects not reinforced within the decay horizon contribute diminishing influence.
- Decay does not delete knowledge objects; it reduces their weight in future persona updates.
- Is configurable.
- Is auditable: the user can see how decay affects their persona.

### Model Adapter

Adapts to embedding model changes. The model adapter:

- Detects when the embedding model has changed.
- Supports re-anchoring: re-embed all historical knowledge with the new model.
- Records the model version used for each persona snapshot.
- Preserves history across model changes.

## Data Contracts

The Persona Engine implements:

- `schemas/persona_vector.md` for persona state.
- Provides query results via the Persona API.

It also produces:

- `persona_update` records (for the audit log).
- `prediction` records.

The Persona Engine exposes a query interface. Direct access to the vector store from other subsystems is discouraged.

## Update Strategies

The Persona Engine supports several update strategies. The default is configurable.

- **Moving average.** New vector = (1 - α) * old + α * new. Simple, stable.
- **Exponential decay.** Old vectors decay exponentially. New vectors are weighted by recency.
- **Time-weighted.** Each knowledge object is weighted by its timestamp's recency.
- **Attention-based.** A small attention model combines the most recent and most salient knowledge.
- **User-tuned.** The user can provide explicit weights or overrides.

The strategy is part of the persona configuration. Changes to the strategy are recorded in the audit log and re-anchoring is supported.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Embedding model unavailable | Connection error | Use last known vector, queue updates. |
| Update produces NaN | Validator | Reject update, log, retain previous. |
| Trajectory corruption | Integrity check | Rebuild from records. |
| Decay function misconfigured | Sanity check | Reject, log, default to safe value. |
| Prediction drift | Monitor | Re-anchor, retrain. |

## Metrics

- `persona.current_vector_norm`
- `persona.drift_rate` (per day)
- `persona.stability_score`
- `persona.update_latency_ms`
- `persona.consistency_score_distribution`
- `persona.prediction_accuracy` (when ground truth available)
- `persona.model_version`

## Future Evolution

- **Multi-vector personas.** Maintain multiple vectors for different aspects (work, personal, learning).
- **Persona-conditioned generation.** Use the persona vector to bias generation in the Synthesis Engine and Digital Twin.
- **Persona visualization.** Project the persona vector into 2D / 3D for user exploration.
- **Cross-user comparison.** Compare personas (with consent) for collaboration.
- **Persona explanations.** "Why does the system think this is like you?" with grounded traces.

## Edge Cases

- **Sudden change.** When the user's behavior changes abruptly, the persona vector should adapt, but not oscillate. The update strategy should be tuned for this.
- **Long silence.** When the user has been silent for a long time, the persona should be stable but not stale.
- **Contradictory updates.** When two knowledge objects update the persona in opposite directions, the conflict is recorded and the user is informed.
- **Model swap.** When the embedding model changes, the persona trajectory is preserved but each snapshot is annotated with the model version.

## Acceptance Criteria for "Persona Engine is Complete"

1. The persona vector updates incrementally and predictably.
2. Consistency scores correlate with human judgment in evaluation.
3. Predictions are non-trivially better than random.
4. The persona trajectory is queryable as a time series.
5. The persona survives an embedding model change with re-anchoring.
6. Evaluation: `evaluations/update_persona.md` passes.
