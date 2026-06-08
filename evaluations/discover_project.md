# Evaluation: Discover Project

This evaluation measures the system's ability to identify and structure a user's "projects" from raw observations.

## Purpose
To verify that the Extractor can correctly identify project-related knowledge from disparate events (e.g., a new git repo, a notebook file, and an email about a task).

## Methodology
1. **Input Data**: Provide a set of 50 observation events spanning 2 weeks of activity (file writes, git commits, emails).
2. **Expected Output**: The system should identify at least one "Project" knowledge object with a >90% confidence score.
3. **Ground Truth**: The "Ground Truth" is a manually defined project scope provided by the evaluator.

## Metrics
- **Precision**: % of identified projects that are valid.
- **Recall**: % of valid projects identified by the system.
- **Provenance Integrity**: 100% of identified projects must have correct provenance to the source events.

## Success Criteria
- Precision > 80%
- Recall > 70%
- 100% Provenance Integrity

## Test Cases
- TC-01: New GitHub repository creation.
- TC-02: Creation of a new project folder with multiple files.
- TC-03: Email exchange regarding a specific task.
- TC-04: Conflict - two projects with similar names.

## Environment
- **Model**: Llama-3-70b-local
- **Subsystems**: Observer, Extractor, Memory, Identity Graph.
