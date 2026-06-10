# ADR-0002: Graph Substrate Selection

## Status
Accepted (supersedes implicit Kuzu default)

## Context
The original Kuzu embedded graph database was archived in October 2025.
Its on-disk format was never stable across minor releases, directly
violating SELF's Article IX (Continuity) requirement.

**Revision 1.1** (2026-06-10)
- Updated language to reflect LadybugDB as the default with Neo4j as enterprise fallback.
- KuzuDB is archived; LadybugDB is the community-designated successor.

## Decision
LadybugDB (github.com/LadybugDB/ladybug) is the default graph substrate.
It is the community-designated successor to Kuzu, retains Cypher, columnar
storage, vector indices, and a permissive MIT licence. Neo4j Community
Edition remains the supported alternative for users who require a
client-server model or enterprise support.

## Consequences
- LadybugDB's storage format stability must be verified before each SELF
  minor release and documented in the changelog.
- If LadybugDB's development ceases, the fallback is Neo4j Community
  Edition. A migration path between the two must be maintained.

## Compliance
Directly supports Article IX §1 (data formats outlive code) and
Article II §1 (local-first).
