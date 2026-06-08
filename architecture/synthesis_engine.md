# Synthesis Engine Subsystem

> The Synthesis Engine produces summaries, reflections, predictions, and narratives from the system's accumulated state. It is SELF's narrator — the subsystem that turns data into stories the user can read.

---

## Purpose

The Synthesis Engine is the subsystem that takes the structured state of SELF — observations, knowledge, identity graph, persona — and produces human-readable artifacts: daily summaries, weekly summaries, topic summaries, project retrospectives, identity evolution reports, and predictions.

Synthesis is deliberate. The system observes continuously but synthesizes on schedules (end of day, end of week) and on demand. The Synthesis Engine is what makes the system's accumulated state legible to the user.

The Synthesis Engine does not introduce new facts. Every synthesized artifact is grounded in the underlying state and carries provenance. The user can always ask: "where did this summary come from?" and the system can answer.

## Responsibilities

- Producing daily summaries.
- Producing weekly summaries.
- Producing topic summaries (e.g., "summarize what I know about X").
- Producing project summaries and retrospectives.
- Producing identity evolution reports.
- Producing predictions (in coordination with the Persona Engine).
- Maintaining synthesis schedules.
- Honoring user preferences for synthesis style and frequency.
- Caching and invalidating synthesis outputs.
- Producing `summary` records with full provenance.

## Inputs

- `observation_event` records.
- `knowledge_object` records.
- The identity graph.
- The persona vector and its trajectory.
- Existing `summary` records (for continuity and avoiding duplication).
- User preferences (cadence, style, length, language).
- Configuration for synthesis prompts and templates.

## Outputs

- `summary` records of various subtypes.
- Notifications to the user when a summary is ready.
- Cached synthesis artifacts.
- Metrics: synthesis latency, summary length, user engagement.

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Memory | Required | Read state, write summaries. |
| Identity Graph | Required | Entity context. |
| Persona Engine | Required | Personalization, predictions. |
| Local Language Model | Required | Text generation. |
| Orchestration | Required | Scheduling. |
| Digital Twin | Required | On-demand synthesis requests. |

## Internal Components

### Summary Scheduler

Decides when to run synthesis. The scheduler:

- Honors user-configured cadences (daily, weekly, custom).
- Detects "natural" synthesis moments (e.g., a major project completion).
- Avoids excessive synthesis (e.g., a quiet day should produce a short summary, not none).
- Is itself observable (the user can see what's scheduled).

### Period Selector

Selects the period to synthesize over. The selector:

- For daily: the user's "day" (configurable boundary, e.g., 4am).
- For weekly: the user's "week" (configurable boundary, e.g., Sunday evening).
- For topic: the relevant subset of state.
- For project: the project-scoped subset.

### Content Aggregator

Aggregates the relevant state for synthesis. The aggregator:

- Pulls observations for the period.
- Pulls relevant knowledge objects.
- Pulls identity graph changes.
- Pulls persona updates.
- Deduplicates.
- Ranks by importance (using persona consistency, recency, and frequency).

### Prompt Builder

Builds the synthesis prompt. The prompt builder:

- Uses versioned prompt templates.
- Includes aggregated state.
- Includes user preferences.
- Includes instructions for grounding and citation.
- Includes length and style constraints.

### Generation Engine

Generates the synthesis text. The generation engine:

- Uses a local language model by default.
- Enforces output constraints.
- Streams output for long summaries.
- Supports regeneration with different parameters.
- Records model, prompt version, and parameters in the artifact.

### Grounding Verifier

Verifies that the generated summary is grounded in the input state. The verifier:

- Checks that every claim in the summary can be traced to source records.
- Flags ungrounded claims for regeneration or removal.
- Records grounding coverage as a metric.

### Provenance Linker

Links the summary to its source records. The linker:

- Records the IDs of observations, knowledge objects, and graph changes that contributed.
- Stores the link in the summary's provenance field.
- Supports "show me the source of this sentence" queries.

### Cache Manager

Caches synthesis outputs. The cache manager:

- Stores generated summaries with TTL.
- Invalidates when underlying state changes.
- Supports partial invalidation (only re-synthesize what changed).
- Is auditable.

### Style Adapter

Adapts the synthesis to the user's preferences. The style adapter:

- Honors configured length, tone, language.
- Adapts to the persona vector (e.g., more technical language for technical personas).
- Supports user-provided style examples.
- Logs style adaptations in the artifact.

### Notification Manager

Notifies the user when a summary is ready. The notification manager:

- Uses the configured channels (in-app, local notification, etc.).
- Respects quiet hours.
- Includes a preview.
- Supports "snooze" and "regenerate" actions.

## Data Contracts

The Synthesis Engine produces:

- `summary` records of subtypes: `daily`, `weekly`, `topic`, `project`, `identity_evolution`, `prediction`.
- `synthesis_audit` records.

See `schemas/daily_summary.md` and `schemas/weekly_summary.md` for the primary subtypes.

## Synthesis Types

### Daily Summary

A summary of the user's day. Includes:

- Top activities (by time and importance).
- Key entities encountered.
- Knowledge gained.
- Project progress.
- Open questions or interruptions.
- Notable contradictions or surprises.

### Weekly Summary

A summary of the user's week. Includes:

- Theme of the week.
- Projects advanced.
- People interacted with.
- Topics explored.
- Beliefs or goals changed.
- Predictions for next week.

### Topic Summary

A summary of everything SELF knows about a topic. Includes:

- Definition and scope.
- Timeline of engagement.
- Key entities and their relationships.
- Current state of the user's knowledge and beliefs.
- Open questions.

### Project Summary

A summary of a project. Includes:

- Project description and goal.
- Timeline of activity.
- Key collaborators.
- Milestones and progress.
- Open issues.
- Predicted next steps.

### Identity Evolution Report

A summary of how the user has changed over a period. Includes:

- Beliefs added, modified, deprecated.
- Goals added, achieved, abandoned.
- Interests emerged, faded.
- Relationships strengthened, weakened.
- Persona vector drift.

### Prediction

A prediction about the user's future. Includes:

- Predicted action, with confidence.
- Supporting evidence.
- Counter-evidence.
- Horizon (next day, next week, next month).

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Model unavailable | Connection error | Defer synthesis, queue, retry. |
| Generation produces ungrounded claims | Grounding verifier | Reject, regenerate. |
| Period selection ambiguous | Edge case detection | Default to safe selection, log. |
| User preference conflict | Validator | Use most recent preference, log. |
| Cache corruption | Integrity check | Invalidate, regenerate. |
| Notification failure | Notification log | Retry, log. |

## Metrics

- `synthesis.summaries_produced.total` (by type)
- `synthesis.grounding_coverage` (per summary)
- `synthesis.length_distribution`
- `synthesis.user_engagement` (read, dismissed, expanded)
- `synthesis.latency_ms`
- `synthesis.regenerations.total`

## Future Evolution

- **Personalized narrative style.** Learn the user's preferred narrative style from examples.
- **Cross-period synthesis.** "Tell me the story of my year."
- **Multi-modal summaries.** Include images, charts, and timelines.
- **Interactive summaries.** The user can click into any sentence for the source.
- **Counterfactual synthesis.** "What would my week have looked like without project X?"

## Edge Cases

- **Empty periods.** When the period has no activity, the summary is honest about that.
- **Overload periods.** When there is enormous activity, the summary highlights the most important.
- **Contradictory activity.** When the user did contradictory things, the summary notes the contradiction.
- **Sensitive activity.** The summary does not include sensitive content by default; the user can opt in.
- **Model drift.** When the underlying model changes, summaries are regenerated only on the next synthesis point, not retroactively.

## Acceptance Criteria for "Synthesis Engine is Complete"

1. Daily and weekly summaries are produced on schedule.
2. Every summary has grounding coverage above 0.9.
3. Summaries are stored with full provenance.
4. The user can request a regeneration.
5. The user can drill into any sentence to see its source.
6. Sensitive content is filtered by default.
7. Evaluations: `evaluations/knowledge_synthesis.md` and `evaluations/predict_next_task.md` pass.
