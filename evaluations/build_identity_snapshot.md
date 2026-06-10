# Evaluation: Build Identity Snapshot

This evaluation measures the system's ability to construct a coherent identity snapshot from the identity graph.

## Purpose
To verify that the Identity Graph subsystem can produce accurate, complete snapshots of user identity entities and their relationships at a given point in time.

## Methodology
1. **Input Data**: Pre-populate the identity graph with 50 nodes (people, projects, tools, interests) and 75 edges representing relationships.
2. **Snapshot Request**: Request identity snapshots at various points in the temporal index.
3. **Expected Output**: Snapshots should contain all relevant entities and relationships active at the requested time.
4. **Ground Truth**: Manually annotated identity states at specific time points.

## Metrics
- **Entity Completeness**: % of expected entities present in snapshot.
- **Relationship Accuracy**: % of relationships correctly captured.
- **Temporal Accuracy**: % of snapshots correctly reflecting state at requested time.

## Success Criteria
- Entity Completeness > 85%
- Relationship Accuracy > 80%
- Temporal Accuracy > 90%

## Test Cases
- TC-01: Snapshot at current time.
- TC-02: Snapshot at historical time point.
- TC-03: Snapshot after entity merge.
- TC-04: Snapshot with soft-deleted entities.

## Environment
- **Storage**: DuckDB (graph storage)
- **Subsystems**: Identity Graph, Node Store, Edge Store, Temporal Index.
