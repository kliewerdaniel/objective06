# Evaluation: Update Persona

This evaluation measures the system's ability to update the persona vector based on new knowledge objects.

## Purpose
To verify that the Persona Engine can incrementally update the persona vector while maintaining consistency and producing appropriate consistency scores for new knowledge.

## Methodology
1. **Input Data**: Start with an established persona vector (10+ updates) and provide 20 new knowledge objects.
2. **Update Process**: Update the persona vector with each knowledge object.
3. **Expected Output**: Updated vectors should show gradual drift while maintaining coherence; consistency scores should correlate with semantic similarity.
4. **Ground Truth**: Expected consistency scores based on manual assessment.

## Metrics
- **Vector Stability**: Cosine similarity between consecutive updates (should not fluctuate wildly).
- **Consistency Correlation**: Correlation between consistency scores and manual assessment.
- **Drift Rate**: Persona drift should be proportional to novelty of input.

## Success Criteria
- Vector Stability > 0.8 (consecutive vectors should be similar)
- Consistency Correlation > 0.7
- Drift Rate: 0.01-0.1 per update (not too fast, not too slow)

## Test Cases
- TC-01: Update with highly consistent knowledge.
- TC-02: Update with mildly novel knowledge.
- TC-03: Update with contradictory knowledge.
- TC-04: Multiple rapid updates.

## Environment
- **Model**: nomic-embed-text (for embeddings)
- **Subsystems**: Persona Engine, Embedding Computer, Persona Updater, Vector Store.
