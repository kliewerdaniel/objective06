# Identity Graph Subsystem

> The Identity Graph is the temporal, typed, attributed graph of entities and relationships that defines the user's evolving identity. It is the structured memory of "who, what, where, when, why."

---

## Purpose

The Identity Graph is SELF's representation of the entities in the user's life and the relationships between them. It is a temporal graph: nodes and edges have lifetimes. The user is the root node. People, projects, organizations, tools, concepts, and places are other nodes. Relationships connect them.

The Identity Graph is the canonical source for structured queries about the user's identity. "Who is the user working with on project X?" "What did the user believe about topic Y a year ago?" "How has the user's relationship with organization Z changed?" — all of these are graph queries.

## Responsibilities

- Maintaining nodes for the user, people, projects, organizations, tools, concepts, places, and other entity types.
- Maintaining edges for relationships between nodes, with types and weights.
- Tracking temporal validity of nodes and edges.
- Supporting entity resolution (merging duplicates, splitting conflated entities).
- Supporting graph queries by pattern, by time, and by neighborhood.
- Supporting evolution queries (how has this node changed over time?).
- Exposing a stable query interface to other subsystems.

## Inputs

- Entity extraction results from the Extractor.
- Observation events (for entity discovery).
- Manual user edits (e.g., "merge these two nodes").
- Configuration for entity types and edge types.

## Outputs

- Graph nodes and edges persisted to Memory.
- Query results: nodes, edges, paths, neighborhoods, evolution histories.
- Updates to the persona engine (when significant changes occur).
- Metrics: node count, edge count, query latency, merge events.

## Dependencies

| Dependency | Type | Purpose |
| --- | --- | --- |
| Memory | Required | Persistence. |
| Extractor | Required | Entity and edge proposals. |
| Storage (Kuzu or Neo4j) | Required | Graph query engine. |
| Orchestration | Required | Scheduling of maintenance tasks. |
| Security | Required | Access control. |

## Internal Components

### Node Store

Stores identity nodes. Each node has:

- A stable ID.
- A type (User, Person, Project, Organization, Tool, Concept, Place, etc.).
- A name and aliases.
- A set of attributes (key-value).
- Temporal validity (created, deprecated, superseded by).
- Provenance.

### Edge Store

Stores edges between nodes. Each edge has:

- A stable ID.
- A source and target node.
- A type (works_on, knows, believes, uses, located_in, etc.).
- A weight (strength of the relationship).
- Temporal validity.
- Provenance.

### Temporal Index

Indexes nodes and edges by their temporal validity. The temporal index supports:

- "As of time T" queries: what was true at time T?
- "During range [T1, T2]" queries: what was true at any point in the range?
- "Since time T" queries: what has been true since T?
- "Changed at time T" queries: what changed at T?

### Entity Resolver

Resolves candidate entities to existing nodes. The resolver:

- Uses string similarity, embedding similarity, and structural features.
- Considers context (other entities in the same event).
- Supports manual confirmation for ambiguous cases.
- Records resolution decisions with provenance.

### Merge Engine

Merges two nodes that are determined to be the same entity. The merge engine:

- Preserves all provenance from both sides.
- Updates all references (edges) to point to the merged node.
- Records the merge in the audit log.
- Is reversible (with operator assistance) for a configurable window.

### Evolution Tracker

Tracks how nodes and edges have changed over time. The evolution tracker:

- Records all attribute changes with timestamps and reasons.
- Supports "diff" queries between two time points.
- Supports "history" queries for a node or edge.

### Query Engine

Translates high-level graph queries into storage-level operations. The query engine:

- Supports pattern matching, path finding, neighborhood queries.
- Supports temporal scoping.
- Supports aggregations (counts, sums, weights).
- Enforces query budgets.

### Schema Registry

Defines valid node types, edge types, and attribute keys. The schema registry:

- Is versioned.
- Is extensible (new types can be added without breaking old data).
- Is the authoritative source for graph schema validation.

## Data Contracts

The Identity Graph implements the storage and query half of:

- `schemas/identity_node.md`
- `schemas/relationship.md`

It also produces:

- `graph_diff` records (changes to the graph).
- `entity_merge` records.

The Identity Graph exposes a query interface. Direct database access from other subsystems is prohibited.

## Node Types

The following node types are defined in the initial schema. Additional types can be added through the schema registry.

- `User` — the user themselves. Exactly one instance, special-cased.
- `Person` — another human the user interacts with.
- `Project` — a project the user is working on or has worked on.
- `Organization` — a company, group, institution.
- `Tool` — a software tool, library, framework, or service.
- `Concept` — an idea, topic, or field of knowledge.
- `Place` — a physical or virtual location.
- `Event` — a significant occurrence.
- `Artifact` — a file, document, or other created work.
- `Goal` — a goal the user is pursuing (specialized node, also a knowledge object subtype).
- `Interest` — an interest the user has (specialized node).
- `Belief` — a belief the user holds (specialized node).

## Edge Types

- `knows` — Person-Person.
- `works_on` — Person-Project, Person-Organization.
- `member_of` — Person-Organization.
- `part_of` — Project-Project, Project-Organization.
- `uses` — Person-Tool.
- `related_to` — Concept-Concept.
- `located_in` — Person/Organization-Place.
- `participated_in` — Person-Event.
- `created` — Person-Artifact.
- `believes` — Person-Belief.
- `pursues` — Person-Goal.
- `interested_in` — Person-Interest.
- `knows_about` — Person-Concept.
- `custom_*` — extensible prefix for domain-specific edges.

## Failure Modes

| Failure | Detection | Response |
| --- | --- | --- |
| Entity resolution ambiguous | Multiple candidates | Surface to user. |
| Merge conflict | Conflicting attributes | Prefer the most recent, log. |
| Query timeout | Watchdog | Return partial result, log. |
| Schema violation | Validator | Reject, log. |
| Storage corruption | Integrity check | Rebuild from provenance chain. |
| Cycle in temporal validity | Validator | Reject, log. |

## Metrics

- `identity_graph.node_count` (by type)
- `identity_graph.edge_count` (by type)
- `identity_graph.query_latency_ms`
- `identity_graph.entity_resolutions.total` (by outcome)
- `identity_graph.merges.total`
- `identity_graph.temporal_query_count`

## Future Evolution

- **Probabilistic edges.** Edges with explicit uncertainty.
- **Hyperedges.** Edges connecting more than two nodes.
- **Graph embeddings.** Learned embeddings of nodes for similarity.
- **Cross-graph queries.** Federated queries across multiple SELF installations (for shared users, e.g., collaborators).
- **Automated ontology learning.** Discover new node and edge types from data.

## Edge Cases

- **Disappearing entities.** When an entity is no longer mentioned, the graph keeps it with a "last seen" timestamp.
- **Identity changes.** When a person changes their name, the node keeps the old name as an alias.
- **Conflicting relationships.** When the user has conflicting relationships with the same entity, both are recorded.
- **Bot / service entities.** Services and bots are modeled as Person or Tool nodes depending on context.
- **Self-referential edges.** The User node can have edges to itself (e.g., `User believes X`).

## Acceptance Criteria for "Identity Graph is Complete"

1. All defined node and edge types can be created and queried.
2. Temporal queries return correct results.
3. Entity resolution correctly merges repeated entities in evaluation.
4. Evolution queries return complete change histories.
5. The graph survives a model change and can be re-evaluated.
6. Evaluation: `evaluations/build_identity_snapshot.md` passes.
