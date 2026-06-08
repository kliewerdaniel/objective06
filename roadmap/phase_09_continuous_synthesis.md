# Phase 09: Continuous Synthesis

## Status
- **Current Status:** Pending
- **Completion:** 0%

## Overview
Phase 09 implements the Synthesis Engine, which turns the system's accumulated state into human-readable narratives. This phase focuses on the "narrator" role of SELF.

## Objectives
- Implement the Synthesis Engine.
- Develop the Summary Scheduler for daily/weekly synthesis.
- Implement the Content Aggregator and Period Selector.
- Implement the Prompt Builder for various summary types (topic, project, evolution).
- Implement the Generation Engine with grounding verification.
- Implement the Style Adapter for persona-consistent narratives.

## Deliverables
- [ ] Synthesis Engine architecture and schema integration.
- [ ] Summary Scheduler implementation.
- [ ] Content Aggregator implementation.
- [ ] Prompt Builder for all summary types.
- [ ] Generation Engine with grounding checks.
- [ ] Style Adapter implementation.
- [ ] Notification Manager for synthesis completion.
- [ ] Build evaluation harness for evaluations/predict_next_task.md (create if not present).
- [ ] Resolve Q3 (synthesis cadence), Q4 (silence modeling), and Q5 (forgetting model) before implementation.

## Dependencies
- Phase 04: Memory (source of data).
- Phase 06: Persona (source of style and relevance).
- Phase 08: Action Engine (source of action history).

## Risks
- **Information Overload**: Producing too much summary content.
- **Grounding Failures**: The narrator making claims not supported by the data.
- **Synthesis Latency**: Ensuring long-running synthesis doesn't block the system.

## Success Criteria
- The system produces a daily summary at the user-configured time.
- The summary includes relevant projects, knowledge gained, and persona reflections.
- The user can request a summary for a specific topic.
- Every summary includes a provenance link to the underlying knowledge objects.
- Evaluation: `evaluations/knowledge_synthesis.md` passes.
