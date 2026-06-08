# ADR-0003: Embedding Model Default

## Status
Accepted

## Context
Persona vectors computed by different embedding models occupy incomparable
vector spaces. Mixing models without explicit lineage tracking silently
corrupts similarity scores and persona trajectories.

## Decision
The default embedding model is `nomic-embed-text` (768 dimensions) served
via Ollama. It is fully local, MIT-licensed, and fits within 4 GB RAM.
`mxbai-embed-large` (1024 dims) is the upgrade path for users with 8+ GB RAM.
All vectors are tagged with a `model_lineage_id`. Cross-lineage similarity
computations are prohibited at the storage layer.

## Consequences
A model swap triggers a full re-embedding pass. Until that pass completes,
the system operates in degraded mode: the persona engine reads from the last
complete lineage and queues new updates.

## Compliance
Supports Article VI (Model Independence) and Article V (Provenance).
