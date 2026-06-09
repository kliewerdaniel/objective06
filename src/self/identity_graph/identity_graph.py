"""Identity Graph — facade over all identity graph components."""

from __future__ import annotations

from typing import Any

from .edge_store import EdgeStore
from .entity_resolver import EntityResolver
from .evolution_tracker import EvolutionTracker
from .merge_engine import MergeEngine
from .node_store import NodeStore
from .query_engine import QueryEngine
from .schema_registry import SchemaRegistry
from .temporal_index import TemporalIndex


class IdentityGraph:
    def __init__(self, storage: Any, audit_log: Any) -> None:
        self.schema_registry = SchemaRegistry()
        self.node_store = NodeStore(storage, self.schema_registry)
        self.edge_store = EdgeStore(storage, self.schema_registry)
        self.temporal_index = TemporalIndex(self.node_store, self.edge_store)
        self.resolver = EntityResolver(self.node_store, storage)
        self.merge_engine = MergeEngine(self.node_store, self.edge_store, storage, audit_log)
        self.evolution = EvolutionTracker(self.node_store, self.edge_store, storage)
        self.query_engine = QueryEngine(self.node_store, self.edge_store)

    def create_user(self, name: str) -> str:
        return self.node_store.create("user", name)

    def create_person(self, name: str, **attrs: Any) -> str:
        return self.node_store.create("person", name, attributes=attrs)

    def create_project(self, name: str, **attrs: Any) -> str:
        return self.node_store.create("project", name, attributes=attrs)
