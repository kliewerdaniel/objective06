# Evaluation Subsystem

> The Evaluation subsystem defines and runs the metrics, benchmarks, and pass/fail criteria for every subsystem. SELF's correctness is not asserted; it is measured.

---

## Purpose

SELF is a complex system with many moving parts. Without a rigorous evaluation framework, the system cannot improve predictably, regressions cannot be caught, and the user cannot trust the outputs. The Evaluation subsystem is the answer.

The Evaluation subsystem:

- Defines what "correct" means for each subsystem and capability.
- Runs evaluations on demand, on schedule, and on change.
- Reports results to the user, the audit log, and the development workflow.
- Supports the documentation-first principle: every claim about the system must be backed by an evaluation.

The Evaluation subsystem is itself a first-class subsystem. It is not a debugging tool; it is part of the production system.

## Responsibilities

- Defining evaluations for every subsystem and capability.
- Running evaluations on schedules and on demand.
- Producing evaluation reports.
- Tracking evaluation results over time.
- Surfacing regressions and improvements.
- Supporting human-in-the-loop evaluation.
- Supporting A/B evaluation of prompts, models, and configurations.
- Publishing evaluation results in human-readable form.

## Inputs

- The system's current state (read-only).
- Configuration of evaluation criteria.
- Test fixtures and ground truth datasets.
- User feedback (when collected).
- A/B test configurations.

## Outputs

- Evaluation reports.
- Pass/fail signals.
- Metric trends.
- Regression alerts.
- Evaluation results in the audit log.
- Public evaluation reports (when the user opts in).

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Memory | Required | Read state for evaluation. |
| All other subsystems | Required | Subject of evaluation. |
| Orchestration | Required | Scheduling. |
| Local Models | Required | For evaluations that require inference. |

## Internal Components

### Evaluation Library

A library of evaluation specifications, one per capability. Each specification defines:

- Inputs (what state to evaluate against).
- Procedure (what to do).
- Expected outputs (what is correct).
- Scoring criteria (how to score the actual output).
- Pass/fail thresholds.

Evaluations are themselves versioned, like schemas. See `evaluations/`.

### Evaluation Runner

Runs evaluations. The runner:

- Supports on-demand runs.
- Supports scheduled runs.
- Supports regression runs (against a baseline).
- Supports A/B runs (two configurations side by side).
- Captures inputs, outputs, scores, and timings.
- Is reproducible (deterministic given the same inputs and configuration).

### Ground Truth Manager

Manages ground truth datasets. The manager:

- Stores curated examples with expected outputs.
- Supports user-provided examples.
- Supports synthetic example generation (with model assistance, audited).
- Version-controls ground truth.

### Metric Aggregator

Aggregates metrics across runs. The aggregator:

- Computes means, medians, distributions.
- Tracks trends over time.
- Detects regressions.
- Surfaces improvements.

### Human Evaluator Interface

Supports human-in-the-loop evaluation. The interface:

- Presents outputs to the user for rating.
- Records ratings.
- Uses ratings to refine automated metrics.
- Supports sampling-based evaluation.

### A/B Test Manager

Manages A/B tests of prompts, models, and configurations. The manager:

- Assigns traffic to variants deterministically.
- Collects results per variant.
- Computes statistical significance.
- Recommends winners (with human approval).

### Report Generator

Generates human-readable reports. The report generator:

- Produces markdown reports by default.
- Supports PDF, HTML, and JSON output.
- Includes per-evaluation scores, trends, and recommendations.
- Is diff-friendly (changes between reports are visible).

## Data Contracts

The Evaluation subsystem produces:

- `evaluation_run` records.
- `evaluation_result` records.
- `evaluation_report` records.

## Evaluation Categories

Evaluations are organized by category:

### Capability Evaluations

For each capability (e.g., "extract a belief from a paragraph"), there is a capability evaluation that measures precision, recall, F1, and other relevant metrics.

### End-to-End Evaluations

For each end-to-end example in `examples/`, there is an evaluation that runs the example and scores the outcome.

### Regression Evaluations

For each release, there is a regression evaluation that ensures no capability has regressed beyond a threshold.

### Human Evaluations

Selected outputs are routed to the user for rating. The ratings are recorded and used to refine automated metrics.

### Adversarial Evaluations

Selected inputs are designed to break the system (prompt injection, edge cases, contradictions). The system must handle them gracefully.

### Long-Run Evaluations

Some evaluations only make sense over time (e.g., "does the persona drift in a way that matches the user's actual evolution?"). These are scheduled over weeks or months.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Evaluation timeout | Watchdog | Mark as failed, log. |
| Ground truth missing | Validator | Refuse to run, log. |
| Model unavailable | Connection error | Use last-known scores, alert. |
| Score computation error | Validator | Reject, log. |
| A/B test contamination | Statistical check | Halt, alert. |

## Metrics

- `evaluation.runs.total` (by evaluation)
- `evaluation.pass_rate` (by evaluation)
- `evaluation.score_trend` (by evaluation, by metric)
- `evaluation.regressions_detected.total`
- `evaluation.human_ratings.total`
- `evaluation.ground_truth_size`

## Future Evolution

- **Continuous evaluation.** Every change triggers relevant evaluations.
- **Cross-model evaluation.** Compare the system's behavior across model backends.
- **User-defined evaluations.** The user can write their own evaluation criteria.
- **Privacy-preserving evaluation.** When sharing evaluation results, anonymize rigorously.

## Edge Cases

- **Evaluation on empty state.** Evaluations must handle the case where SELF has just been initialized.
- **Evaluation with corrupt state.** Evaluations must detect and report corrupt state, not produce misleading scores.
- **Long-running evaluations.** Some evaluations take hours. The runner must stream progress.
- **Conflicting metrics.** Two metrics may disagree (e.g., precision vs. recall). The system must report both.
- **User opt-out.** The user can opt out of certain evaluations. The system must respect this.

## Acceptance Criteria for "Evaluation Subsystem is Complete"

1. At least one evaluation exists per documented capability.
2. Evaluations can be run on demand and on schedule.
3. Evaluation results are stored and queryable.
4. Regressions are detected and reported.
5. A/B tests are supported for prompts and models.
6. Evaluation reports are human-readable.
7. The Evaluation subsystem itself is evaluated (meta-evaluation).
