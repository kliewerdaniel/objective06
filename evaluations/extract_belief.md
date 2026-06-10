# Evaluation: Extract Belief

This evaluation measures the system's ability to extract belief knowledge objects from observation events.

## Purpose
To verify that the Extractor can correctly identify beliefs (opinions, preferences, stances) from raw events and produce well-structured knowledge objects with appropriate confidence scores.

## Methodology
1. **Input Data**: Provide a set of 30 observation events containing opinions, preferences, and stated beliefs.
2. **Expected Output**: The system should extract belief knowledge objects with name, description, content, and confidence fields populated.
3. **Ground Truth**: Manually annotated beliefs extracted from the same event set.

## Metrics
- **Precision**: % of extracted beliefs that match ground truth.
- **Recall**: % of ground truth beliefs that were extracted.
- **Confidence Calibration**: Correlation between confidence scores and actual accuracy.

## Success Criteria
- Precision > 75%
- Recall > 65%
- Confidence Calibration > 0.7

## Test Cases
- TC-01: Explicit opinion statements ("I prefer Python over JavaScript").
- TC-02: Implied preferences from behavior (frequently uses certain tools).
- TC-03: Stated goals and aspirations.
- TC-04: Contradictory beliefs across events.

## Environment
- **Model**: nomic-embed-text (for extraction)
- **Subsystems**: Observer, Extractor, Knowledge Writer.
