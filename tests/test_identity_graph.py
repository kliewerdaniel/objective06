"""Tests for Identity Graph."""

from __future__ import annotations

from self.identity_graph import (
    EdgeStore,
    EntityResolver,
    EvolutionTracker,
    IdentityGraph,
    MergeEngine,
    NodeStore,
    QueryEngine,
    SchemaRegistry,
    TemporalIndex,
)


class MockStorage:
    def __init__(self) -> None:
        self._records: dict[str, list[dict]] = {}

    def insert(self, rt: str, r: dict) -> str:
        self._records.setdefault(rt, []).append(r)
        return str(r["id"])

    def get(self, rt: str, rid: str) -> dict | None:
        for r in self._records.get(rt, []):
            if r["id"] == rid:
                return dict(r)
        return None

    def query(self, rt: str, spec: dict | None = None) -> list[dict]:
        if not spec:
            return list(self._records.get(rt, []))
        results = list(self._records.get(rt, []))
        for key, value in spec.items():
            if key in ("limit", "offset", "order_by"):
                continue
            results = [r for r in results if r.get(key) == value]
        limit = spec.get("limit", len(results)) if spec else len(results)
        return results[:limit]

    def update(self, rt: str, rid: str, changes: dict) -> bool:
        for r in self._records.get(rt, []):
            if r["id"] == rid:
                r.update(changes)
                return True
        return False

    def count(self, rt: str) -> int:
        return len(self._records.get(rt, []))


class MockAuditLog:
    def __init__(self) -> None:
        self.entries: list[dict] = []

    def append(self, **kw: dict) -> None:
        self.entries.append(kw)


# --- Schema Registry ---


def test_schema_registry() -> None:
    sr = SchemaRegistry()
    assert sr.is_valid_node_type("person")
    assert sr.is_valid_node_type("project")
    assert not sr.is_valid_node_type("nonexistent")
    assert sr.is_valid_edge_type("knows")
    assert sr.is_valid_edge_type("custom_my_edge")
    assert "person" in sr.list_node_types()
    assert "knows" in sr.list_edge_types()
    sr.register_node_type("custom_node")
    assert sr.is_valid_node_type("custom_node")


# --- Node Store ---


def test_create_node() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    nid = ns.create("person", "Alice")
    assert nid.startswith("id_")
    node = ns.get(nid)
    assert node is not None
    assert node["name"] == "Alice"
    assert node["type"] == "person"


def test_find_node_by_name() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    ns.create("person", "Bob")
    results = ns.find_by_name("Bob")
    assert len(results) == 1
    results = ns.find_by_name("nobody")
    assert len(results) == 0


def test_find_node_by_type() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    ns.create("person", "A")
    ns.create("project", "B")
    assert len(ns.find_by_type("person")) == 1
    assert len(ns.find_by_type("project")) == 1


def test_delete_node_soft() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    nid = ns.create("person", "Test")
    assert ns.delete(nid) is True
    node = ns.get(nid)
    assert node is not None
    assert node["deprecated"] is True


def test_invalid_node_type() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    import pytest

    with pytest.raises(ValueError, match="Invalid node type"):
        ns.create("invalid_type", "X")


# --- Edge Store ---


def test_create_edge() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    es = EdgeStore(storage, sr)
    eid = es.create("knows", "id_a", "id_b")
    assert eid.startswith("ed_")
    edge = es.get(eid)
    assert edge is not None
    assert edge["type"] == "knows"
    assert edge["source_id"] == "id_a"
    assert edge["target_id"] == "id_b"


def test_find_edges_by_source() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    es = EdgeStore(storage, sr)
    es.create("knows", "a", "b")
    es.create("knows", "a", "c")
    assert len(es.find_by_source("a")) == 2
    assert len(es.find_by_source("x")) == 0


def test_find_between() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    es = EdgeStore(storage, sr)
    es.create("knows", "a", "b")
    es.create("knows", "a", "c")
    assert len(es.find_between("a", "b")) == 1


# --- Temporal Index ---


def test_temporal_as_of() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    es = EdgeStore(storage, sr)
    ti = TemporalIndex(ns, es)
    ns.create("person", "Alice")
    ts = "2100-01-01T00:00:00"
    results = ti.as_of(ts)
    assert len(results) == 1


# --- Entity Resolver ---


def test_entity_resolver() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    ns.create("person", "Alice Johnson")
    resolver = EntityResolver(ns, storage)
    resolved = resolver.resolve("Alice Johnson")
    assert resolved is not None
    assert resolved["name"] == "Alice Johnson"
    resolved_wrong = resolver.resolve("Nonexistent Person")
    assert resolved_wrong is None


def test_find_candidates() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    ns.create("person", "Alice Johnson")
    resolver = EntityResolver(ns, storage)
    candidates = resolver.find_candidates("Alice", "person")
    assert len(candidates) >= 1


# --- Merge Engine ---


def test_merge_nodes() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    es = EdgeStore(storage, sr)
    audit = MockAuditLog()
    me = MergeEngine(ns, es, storage, audit)
    a_id = ns.create("person", "Alice")
    b_id = ns.create("person", "Alicia")
    es.create("knows", a_id, "some_other")
    result = me.merge(a_id, b_id, reason="Same person")
    assert result is True
    merged = ns.get(b_id)
    assert merged["deprecated"] is True
    assert merged["superseded_by"] == a_id
    assert len(audit.entries) >= 1


# --- Evolution Tracker ---


def test_evolution_tracker() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    es = EdgeStore(storage, sr)
    et = EvolutionTracker(ns, es, storage)
    cid = et.record_change("identity_node", "id_001", "name", "Old", "New", "Updated")
    assert cid.startswith("ch_")
    history = et.history("id_001")
    assert len(history) == 1


# --- Query Engine ---


def test_find_neighbors() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    es = EdgeStore(storage, sr)
    a = ns.create("person", "Alice")
    b = ns.create("person", "Bob")
    c = ns.create("person", "Charlie")
    es.create("knows", a, b)
    es.create("knows", a, c)
    qe = QueryEngine(ns, es)
    neighbors = qe.find_neighbors(a)
    assert len(neighbors) == 2


def test_count_by_type() -> None:
    storage = MockStorage()
    sr = SchemaRegistry()
    ns = NodeStore(storage, sr)
    ns.create("person", "A")
    ns.create("person", "B")
    ns.create("project", "C")
    qe = QueryEngine(ns, EdgeStore(storage, sr))
    assert qe.count_by_type("person") == 2
    assert qe.count_by_type("project") == 1


# --- Facade ---


def test_identity_graph_facade() -> None:
    storage = MockStorage()
    audit = MockAuditLog()
    ig = IdentityGraph(storage, audit)
    uid = ig.create_user("me")
    assert uid.startswith("id_")
    pid = ig.create_person("Alice", title="Engineer")
    assert pid.startswith("id_")
    prj = ig.create_project("Project X")
    assert prj.startswith("id_")
