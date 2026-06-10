# Evaluation: Knowledge Synthesis

This evaluation measures the system's ability to generate coherent summaries from accumulated knowledge.

## Purpose
To verify that the Synthesis Engine can produce accurate, well-grounded summaries that correctly synthesize information from multiple sources.

## Methodology
1. **Input Data**: Provide 7 days of simulated activity including 100 events, 30 knowledge objects, and 10 identity graph entities.
2. **Synthesis Request**: Request daily, weekly, and topic-based summaries.
3. **Expected Output**: Summaries should accurately reflect the input data with proper citations.
4. **Ground Truth**: Manually written summaries based on the same input data.

## Metrics
- **Factual Accuracy**: % of statements in summary that are supported by source data.
- **Coverage**: % of key topics/activities covered in summary.
- **Grounding Score**: % of claims with proper source citations.

## Success Criteria
- Factual Accuracy > 85%
- Coverage > 70%
- Grounding Score > 80%

## Test Cases
- TC-01: Daily summary of active day.
- TC-02: Weekly summary with diverse activities.
- TC-03: Topic-specific summary (e.g., "Python development").
- TC-04: Summary with minimal activity.

## Environment
- **Model**: nomic-embed-text (for generation)
- **Subsystems**: Synthesis Engine, Memory, Identity Graph, Content Aggregator.
