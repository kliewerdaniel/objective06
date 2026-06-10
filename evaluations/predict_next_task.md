# Evaluation: Predict Next Task

This evaluation measures the system's ability to predict user's next likely actions or interests.

## Purpose
To verify that the Persona Engine and Digital Twin can generate meaningful predictions about user behavior based on historical patterns and current context.

## Methodology
1. **Input Data**: Provide 30 days of user activity patterns including work schedules, tool usage, and project progressions.
2. **Prediction Request**: Request predictions for next likely actions, tools, or topics.
3. **Expected Output**: Ranked predictions with confidence scores that reflect actual user behavior.
4. **Ground Truth**: Actual user actions recorded in subsequent time period.

## Metrics
- **Precision@3**: Precision of top 3 predictions.
- **Hit Rate**: % of times actual action appears in top 5 predictions.
- **Confidence Calibration**: Correlation between confidence and actual occurrence.

## Success Criteria
- Precision@3 > 0.3
- Hit Rate > 0.5
- Confidence Calibration > 0.6

## Test Cases
- TC-01: Predict next tool usage based on project context.
- TC-02: Predict next topic of interest.
- TC-03: Predict next collaboration partner.
- TC-04: Predict task completion timeline.

## Environment
- **Model**: nomic-embed-text (for embeddings and predictions)
- **Subsystems**: Persona Engine, Identity Graph, Digital Twin, Memory.
