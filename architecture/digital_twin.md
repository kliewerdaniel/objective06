# Digital Twin Subsystem

> The Digital Twin is the conversational interface to SELF. It takes natural-language queries and returns answers grounded in the user's identity, memory, and persona. It is the user's "second self" for reflection, retrieval, and exploration.

---

## Purpose

The Digital Twin is the face of SELF. It is the only subsystem that the user talks to directly. It takes questions like "what was I working on last week?", "who have I been talking to about X?", "what changed in my beliefs recently?", and returns grounded, sourced, human-readable answers.

The Twin is not a chatbot in the conventional sense. It is a constrained interface to the underlying state. Every answer it produces is grounded in:

- The identity graph (for entity-centric answers).
- Memory (for event-centric and knowledge-centric answers).
- The persona vector (for consistency and personalization).
- The synthesis engine (for summary-style answers).

The Twin never invents facts not present in the system's state. When it cannot answer, it says so.

## Responsibilities

- Accepting natural-language queries from the user.
- Classifying the query intent.
- Decomposing complex queries into sub-queries.
- Routing sub-queries to the appropriate subsystem.
- Composing answers from sub-query results.
- Grounding every assertion in source records.
- Producing explanations ("why this answer?").
- Producing confidence scores and uncertainty markers.
- Maintaining conversation state within a session.
- Honoring the permission system.
- Logging every interaction.

## Inputs

- Natural-language queries from the user.
- Conversation history within the current session.
- The current state of the identity graph, memory, persona, and synthesis outputs.
- The user's permissions.
- Configuration: model choice, tone, verbosity, language.

## Outputs

- Natural-language answers.
- Grounded citations: list of source records for each assertion.
- Confidence scores and uncertainty markers.
- Suggested follow-up queries.
- Action proposals (presented to the user, never executed without consent).
- Conversation logs.
- Metrics: query latency, grounding coverage, user satisfaction.

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Memory | Required | Read events, knowledge, summaries. |
| Identity Graph | Required | Entity queries. |
| Persona Engine | Required | Personalization, consistency. |
| Synthesis Engine | Required | Summary-style answers. |
| Action Engine | Required | Propose actions, never execute without consent. |
| Local Language Model | Required | Natural language understanding and generation. |
| Security | Required | Permission checks, prompt injection defenses. |
| Orchestration | Required | Session management. |

## Internal Components

### Query Intake

Receives queries from the user interface. The intake:

- Validates input.
- Sanitizes input against prompt injection.
- Establishes or extends a session.
- Logs the query.
- Returns session context to the rest of the Twin.

### Intent Classifier

Classifies the user's intent. Intent categories include:

- **Factual retrieval.** "What did I do on Tuesday?"
- **Entity exploration.** "Tell me about project X."
- **Summary request.** "Summarize my week."
- **Reflection request.** "What changed about me recently?"
- **Prediction request.** "What am I likely to do next?"
- **Action proposal.** "Help me draft an email to Y."
- **Meta-question.** "What do you know about me?"
- **Conversation.** General chat that does not require system state.

Classification is itself a model call, with the intent recorded for the audit log.

### Query Decomposer

Breaks complex queries into sub-queries. For example, "what changed about my relationship with X last month?" decomposes into:

- Retrieve the user-X edge history.
- Retrieve events mentioning X in the date range.
- Retrieve knowledge objects about X in the date range.
- Compute a diff.
- Compose an answer.

The decomposer is model-driven but constrained: it can only produce sub-queries that map to known query types.

### Sub-Query Router

Routes each sub-query to the appropriate subsystem. The router:

- Knows the capabilities of each subsystem.
- Sends sub-queries in parallel where possible.
- Aggregates results.

### Answer Composer

Composes a natural-language answer from sub-query results. The composer:

- Uses a language model with a constrained prompt.
- Includes grounding citations.
- Marks uncertainty explicitly.
- Avoids fabricating facts not in the sub-query results.
- Suggests follow-up queries.

### Citation Tracker

Tracks every assertion in the answer back to its source records. The citation tracker:

- Maintains a mapping from sentence to source record ID.
- Exposes the mapping to the user.
- Records the mapping in the conversation log.

### Session Manager

Manages conversation state within a session. The session manager:

- Stores recent turns.
- Maintains context (entities mentioned, intents inferred).
- Honors session-scoped permissions.
- Supports session resumption.

### Prompt Sanitizer

Defends against prompt injection in user input. The sanitizer:

- (1) Structural isolation — retrieved content is injected into a fixed slot that the primary model is instructed to treat as data;
- (2) Secondary classifier — a lightweight model (distinct from the generation model) scores each retrieved segment for injection likelihood before assembly;
- (3) Citation-lock — if the generation model's output references a knowledge object not in the declared retrieval set, the response is rejected and regenerated.
- Records attempted attacks.

### Permission Enforcer

Honors the permission system. The permission enforcer:

- Checks that the user has authorized the Twin to read the requested state.
- Checks that the user has authorized the Twin to propose actions.
- Refuses queries that exceed permissions, with a clear explanation.

## Data Contracts

The Twin consumes:

- All schemas in `schemas/` (read-only).
- Configuration.

The Twin produces:

- `twin_interaction` records (for the audit log).
- `twin_answer` records (cached answers).
- Action proposals (which become `action_request` records only upon user approval).

## Prompt Discipline

The Twin's prompts follow strict rules:

- **System prompts are immutable from the user side.** The user cannot override them.
- **Retrieved content is data, not instructions.** The Twin treats retrieved content as untrusted.
- **No secrets in prompts.** The Twin never includes secrets in prompts.
- **Citations are mandatory.** Every assertion in an answer must have a citation, or be marked as uncertain.
- **No invented facts.** If the underlying state does not support an assertion, the Twin must say so.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Model unavailable | Connection error | Degrade to retrieval-only mode; return raw results. |
| Intent misclassification | Confidence check | Ask for clarification. |
| Sub-query timeout | Watchdog | Return partial answer with caveat. |
| Citation missing | Validator | Reject answer, regenerate. |
| Prompt injection detected | Pattern match | Refuse, log, alert. |
| Permission denied | Permission check | Refuse with explanation. |
| Hallucination detected | Citation mismatch | Reject, regenerate with stricter prompt. |

## Metrics

- `twin.queries.total` (by intent)
- `twin.answer_latency_ms` (p50, p95, p99)
- `twin.grounding_coverage` (fraction of assertions with citations)
- `twin.user_satisfaction` (thumbs up / down, when collected)
- `twin.hallucination_rate` (estimated from citation coverage and user feedback)
- `twin.action_proposals.total` (by category)
- `twin.action_proposals.accepted_rate`

## Future Evolution

- **Multi-modal twin.** Accept voice, image, and other modalities.
- **Proactive twin.** The Twin initiates interactions based on important events.
- **Persona-conditioned tone.** The Twin's tone adapts to the user's current persona state.
- **Twin of twins.** The user can spawn scoped twins for specific contexts (work, learning, etc.).
- **Multi-user twins (with consent).** Two users can have a twin-mediated conversation.

## Edge Cases

- **Empty state.** When the user is new and the system has little data, the Twin must say so honestly.
- **Conflicting evidence.** When the underlying state contains contradictions, the Twin must surface them.
- **Sensitive topics.** The Twin must handle health, legal, financial, and other sensitive topics with care, referring to professionals when appropriate.
- **User distress.** The Twin must detect signs of user distress and respond with care, not as a mental health professional.
- **Adversarial user.** The Twin must resist attempts to manipulate it into violating its principles.

## Acceptance Criteria for "Digital Twin is Complete"

1. All intent categories are supported.
2. Every answer has citations for every assertion.
3. The Twin refuses to answer questions that exceed permissions.
4. The Twin survives model unavailability (degraded mode).
5. Prompt injection attempts are detected and refused.
6. Evaluation: `evaluations/memory_retrieval.md` and `evaluations/knowledge_synthesis.md` pass.
