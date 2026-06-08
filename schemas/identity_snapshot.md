# Identity Snapshot Schema

An **identity snapshot** is a point-in-time capture of the user's identity representation. It is used for reflection, comparison, and continuity across different versions of the system or different hardware environments.

## Attributes

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | UUID | Unique identifier for the snapshot. |
| `timestamp` | Timestamp | The time the snapshot was taken. |
| `persona_vector_id` | UUID | Reference to the persona vector at the time of the snapshot. |
| `identity_graph_state` | Object | A serialized representation of the identity graph state (or a reference to a specific graph checkpoint). |
| `knowledge_objects` | Array(UUID) | A list of IDs of the knowledge objects that were considered relevant at the time of the snapshot. |
| `summary` | String | A human-readable summary of the user's identity at this point in time (produced by the Synthesis Engine). |
| `metadata` | Object | Optional metadata (e.g., "end of week", "project completion"). |

## Usage
Identity snapshots are intended to be used for:
- **Reflection**: Comparing "who I was then" vs "who I am now".
- **Migration**: Transporting the core identity state to a new installation.
- **Rollback**: Returning to a previous state of the identity representation.

## Example
```json
{
  "id": "...",
  "timestamp": "...",
  "persona_vector_id": "...",
  "identity_graph_state": {
    "nodes": [...],
    "edges": [...]
  },
  "knowledge_objects": ["...", "..."],
  "summary": "The user is currently focused on learning quantum computing and is actively building a personal portfolio.",
  "metadata": {
    "snapshot_type": "weekly_reflection"
  }
}
```
