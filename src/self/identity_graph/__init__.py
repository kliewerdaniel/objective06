"""Identity Graph — temporal entity model for SELF."""

from __future__ import annotations

from .edge_store import EdgeStore
from .entity_resolver import EntityResolver
from .evolution_tracker import EvolutionTracker
from .identity_graph import IdentityGraph
from .merge_engine import MergeEngine
from .node_store import NodeStore
from .query_engine import QueryEngine, QueryPattern
from .schema_registry import EDGE_TYPES, NODE_TYPES, SchemaRegistry
from .temporal_index import TemporalIndex

__all__ = [
    "IdentityGraph",
    "NodeStore",
    "EdgeStore",
    "SchemaRegistry",
    "NODE_TYPES",
    "EDGE_TYPES",
    "TemporalIndex",
    "EntityResolver",
    "MergeEngine",
    "EvolutionTracker",
    "QueryEngine",
    "QueryPattern",
]
