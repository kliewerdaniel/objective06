# Evaluation: Detect Goal

This evaluation measures the system's ability to detect and extract goal knowledge objects from observation events.

## Purpose
To verify that the Extractor can correctly identify user goals (short-term and long-term objectives) from raw events and produce structured knowledge objects.

## Methodology
1. **Input Data**: Provide a set of 40 observation events containing goal-related content (task lists, project milestones, stated objectives).
2. **Expected Output**: The system should extract goal knowledge objects with name, description, timeline, and priority fields.
3. **Ground Truth**: Manually annotated goals extracted from the same event set.

## Metrics
- **Precision**: % of extracted goals that match ground truth.
- **Recall**: % of ground truth goals that were extracted.
- **Timeline Accuracy**: % of goals with correctly identified timeframes.

## Success Criteria
- Precision > 70%
- Recall > 60%
- Timeline Accuracy > 50%

## Test Cases
- TC-01: Short-term task completion goals.
- TC-02: Long-term project milestones.
- TC-03: Implicit goals from repeated actions.
- TC-04: Abandoned or superseded goals.

## Environment
- **Model**: nomic-embed-text (for extraction)
- **Subsystems**: Observer, Extractor, Knowledge Writer, Identity Graph.
