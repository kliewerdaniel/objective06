"""Tests for the Evaluation subsystem."""

from __future__ import annotations

from src.self.evaluation import EvalSpec, Evaluation, builtin_specs
from src.self.evaluation.evaluation_runner import EvaluationRunner
from src.self.evaluation.ground_truth_manager import GroundTruthManager
from src.self.evaluation.metric_aggregator import MetricAggregator
from src.self.evaluation.report_generator import ReportGenerator


class FakeStorage:
    def __init__(self) -> None:
        self._data: dict[str, list[dict]] = {}

    def insert(self, record_type: str, record: dict) -> str:
        self._data.setdefault(record_type, []).append(record)
        return str(record["id"])

    def get(self, record_type: str, id: str) -> dict | None:
        for r in self._data.get(record_type, []):
            if r.get("id") == id:
                return dict(r)
        return None

    def query(self, record_type: str, spec: dict) -> list[dict]:
        records = self._data.get(record_type, [])
        result = list(records)
        for key, value in spec.items():
            if key in ("limit", "order_by", "offset"):
                continue
            result = [r for r in result if r.get(key) == value]
        limit = spec.get("limit", 100)
        return list(result[:limit])

    def update(self, record_type: str, id: str, changes: dict) -> bool:
        for r in self._data.get(record_type, []):
            if r.get("id") == id:
                r.update(changes)
                return True
        return False

    def delete(self, record_type: str, id: str) -> bool:
        records = self._data.get(record_type, [])
        self._data[record_type] = [r for r in records if r.get("id") != id]
        return True

    def count(self, record_type: str, filter: dict | None = None) -> int:
        if filter:
            records = self.query(record_type, filter)
        else:
            records = self._data.get(record_type, [])
        return len(records)


# --- EvalSpec ---


def test_eval_spec_creates_record() -> None:
    spec = EvalSpec(name="test_spec", category="capability")
    record = spec.to_record()
    assert record["name"] == "test_spec"
    assert record["category"] == "capability"
    assert record["pass_threshold"] == 0.8
    assert record["id"].startswith("ev_")
    assert "created_at" in record
    assert "updated_at" in record


def test_eval_spec_from_record() -> None:
    spec = EvalSpec(name="original", category="capability", pass_threshold=0.9)
    record = spec.to_record()
    restored = EvalSpec.from_record(record)
    assert restored.id == spec.id
    assert restored.name == "original"
    assert restored.pass_threshold == 0.9


def test_builtin_specs() -> None:
    specs = builtin_specs()
    names = [s.name for s in specs]
    assert len(specs) == 5
    assert "extract_belief" in names
    assert "detect_goal" in names
    assert "memory_retrieval" in names
    assert "entity_resolution" in names
    assert "persona_consistency" in names
    for s in specs:
        assert s.category == "capability"


# --- GroundTruthManager ---


def test_create_ground_truth() -> None:
    storage = FakeStorage()
    mgr = GroundTruthManager(storage)
    gid = mgr.create("spec_1", {"text": "hello"}, {"entities": ["greeting"]})
    assert gid.startswith("gt_")
    record = storage.get("ground_truth", gid)
    assert record is not None
    assert record["spec_id"] == "spec_1"


def test_ground_truth_list_for_spec() -> None:
    storage = FakeStorage()
    mgr = GroundTruthManager(storage)
    mgr.create("spec_a", {"x": 1}, {"y": 2})
    mgr.create("spec_a", {"x": 3}, {"y": 4})
    mgr.create("spec_b", {"x": 5}, {"y": 6})
    spec_a = mgr.list_for_spec("spec_a")
    assert len(spec_a) == 2
    spec_b = mgr.list_for_spec("spec_b")
    assert len(spec_b) == 1


def test_ground_truth_update_increments_version() -> None:
    storage = FakeStorage()
    mgr = GroundTruthManager(storage)
    gid = mgr.create("spec_1", {"in": 1}, {"out": 1})
    updated = mgr.update(gid, {"out": 2})
    assert updated is not None
    assert updated["version"] == 2
    record = storage.get("ground_truth", gid)
    assert record is not None
    assert record["expected_outputs"] == {"out": 2}


def test_ground_truth_deprecate() -> None:
    storage = FakeStorage()
    mgr = GroundTruthManager(storage)
    gid = mgr.create("spec_1", {"in": 1}, {"out": 1})
    assert mgr.deprecate(gid) is True
    record = storage.get("ground_truth", gid)
    assert record is not None
    assert record["deprecated"] is True


def test_ground_truth_deprecate_nonexistent() -> None:
    mgr = GroundTruthManager(FakeStorage())
    assert mgr.deprecate("nonexistent") is False


def test_ground_truth_count() -> None:
    storage = FakeStorage()
    mgr = GroundTruthManager(storage)
    assert mgr.count() == 0
    mgr.create("s1", {}, {})
    mgr.create("s2", {}, {})
    assert mgr.count() == 2


# --- EvaluationRunner ---


def test_runner_requires_handler() -> None:
    storage = FakeStorage()
    spec = EvalSpec(name="no_handler", category="test")
    storage.insert("evaluation_spec", spec.to_record())
    runner = EvaluationRunner(storage)
    result = runner.run_spec(spec.id, [])
    assert result["ok"] is True
    assert result["passed"] is True


def test_runner_with_handler() -> None:
    storage = FakeStorage()
    spec = EvalSpec(name="echo_test", category="test", pass_threshold=0.5)
    storage.insert("evaluation_spec", spec.to_record())
    gt_id = storage.insert(
        "ground_truth",
        {
            "schema_version": "0.1.0",
            "id": "gt_1",
            "spec_id": spec.id,
            "inputs": {"value": 42},
            "expected_outputs": {"result": 42},
            "version": 1,
            "created_at": "now",
            "updated_at": "now",
            "deprecated": False,
        },
    )

    runner = EvaluationRunner(storage)
    runner.register("test_cap", lambda inputs: {"result": inputs.get("value")})
    spec_record = storage.get("evaluation_spec", spec.id)
    assert spec_record is not None
    spec_record["procedure"] = {"capability": "test_cap"}
    storage.update("evaluation_spec", spec.id, {"procedure": {"capability": "test_cap"}})

    ground_truths = [storage.get("ground_truth", gt_id)]
    result = runner.run_spec(spec.id, [ground_truths[0]])  # type: ignore[list-item]

    assert result["ok"] is True
    assert result["status"] in ("completed", "failed")
    assert "run_id" in result


def test_runner_stores_run_record() -> None:
    storage = FakeStorage()
    spec = EvalSpec(name="store_test", category="test")
    storage.insert("evaluation_spec", spec.to_record())
    runner = EvaluationRunner(storage)
    result = runner.run_spec(spec.id, [])
    run = storage.get("evaluation_run", result["run_id"])
    assert run is not None
    assert run["spec_id"] == spec.id
    assert run["status"] in ("completed", "failed")


# --- MetricAggregator ---


def test_aggregator_empty() -> None:
    agg = MetricAggregator(FakeStorage())
    result = agg.aggregate([])
    assert result["count"] == 0
    assert result["mean_score"] == 0.0
    assert result["pass_rate"] == 1.0


def test_aggregator_computes_scores() -> None:
    agg = MetricAggregator(FakeStorage())
    results = [
        {"metric": "precision", "score": 0.9, "passed": True},
        {"metric": "recall", "score": 0.7, "passed": True},
        {"metric": "accuracy", "score": 0.5, "passed": False},
    ]
    result = agg.aggregate(results)
    assert result["count"] == 3
    assert abs(result["mean_score"] - 0.7) < 0.001
    assert abs(result["pass_rate"] - 0.666) < 0.01
    assert "precision" in result["metrics"]
    assert result["metrics"]["precision"]["mean"] == 0.9


def test_aggregator_metrics_summary() -> None:
    agg = MetricAggregator(FakeStorage())
    results = [
        {"metric": "m1", "score": 0.8, "passed": True},
        {"metric": "m1", "score": 0.6, "passed": True},
        {"metric": "m2", "score": 0.9, "passed": True},
    ]
    result = agg.aggregate(results)
    assert result["metrics"]["m1"]["mean"] == 0.7
    assert result["metrics"]["m1"]["min"] == 0.6
    assert result["metrics"]["m1"]["max"] == 0.8


# --- ReportGenerator ---


def test_report_generates_markdown() -> None:
    storage = FakeStorage()
    spec = EvalSpec(name="report_test", category="test")
    storage.insert("evaluation_spec", spec.to_record())
    storage.insert(
        "evaluation_run",
        {
            "schema_version": "0.1.0",
            "id": "run_1",
            "spec_id": spec.id,
            "status": "completed",
            "started_at": "2025-01-01T00:00:00",
        },
    )
    storage.insert(
        "evaluation_result",
        {
            "schema_version": "0.1.0",
            "id": "res_1",
            "run_id": "run_1",
            "metric": "precision",
            "score": 0.95,
            "passed": True,
            "details": {},
            "recorded_at": "2025-01-01T00:00:00",
        },
    )

    gen = ReportGenerator(storage)
    result = gen.generate(["run_1"])
    assert result["ok"] is True
    assert result["id"].startswith("erep_")
    assert "# Evaluation Report" in result["markdown"]
    assert "report_test" in result["markdown"]
    assert "precision" in result["markdown"]
    assert "0.950" in result["markdown"]


def test_report_list() -> None:
    storage = FakeStorage()
    gen = ReportGenerator(storage)
    gen.generate([], {"run_count": 0})
    gen.generate([], {"run_count": 0})
    reports = gen.list_reports()
    assert len(reports) == 2


def test_report_get() -> None:
    storage = FakeStorage()
    gen = ReportGenerator(storage)
    result = gen.generate([], {"run_count": 0})
    fetched = gen.get(result["id"])
    assert fetched is not None
    assert fetched["id"] == result["id"]


# --- Evaluation facade ---


def test_evaluation_register_spec() -> None:
    storage = FakeStorage()
    ev = Evaluation(storage)
    spec = EvalSpec(name="facade_test", category="test")
    sid = ev.register_spec(spec)
    fetched = ev.get_spec(sid)
    assert fetched is not None
    assert fetched["name"] == "facade_test"


def test_evaluation_register_builtins() -> None:
    storage = FakeStorage()
    ev = Evaluation(storage)
    ids = ev.register_builtins()
    assert len(ids) == 5


def test_evaluation_builtins_idempotent() -> None:
    storage = FakeStorage()
    ev = Evaluation(storage)
    ev.register_builtins()
    ids2 = ev.register_builtins()
    assert len(ids2) == 0


def test_evaluation_list_specs() -> None:
    storage = FakeStorage()
    ev = Evaluation(storage)
    ev.register_spec(EvalSpec(name="s1", category="c1"))
    ev.register_spec(EvalSpec(name="s2", category="c2"))
    specs = ev.list_specs()
    assert len(specs) == 2


def test_evaluation_create_ground_truth() -> None:
    storage = FakeStorage()
    ev = Evaluation(storage)
    spec = EvalSpec(name="gt_test", category="test")
    sid = ev.register_spec(spec)
    gid = ev.create_ground_truth(sid, {"input": 1}, {"output": 2})
    assert gid.startswith("gt_")
    record = ev.ground_truth.get(gid)
    assert record is not None


def test_evaluation_generate_report() -> None:
    storage = FakeStorage()
    ev = Evaluation(storage)
    spec = EvalSpec(name="report_test", category="test")
    sid = ev.register_spec(spec)
    gt_id = ev.create_ground_truth(sid, {"x": 1}, {"y": 2})
    ev.register_handler("handler", lambda inputs: {"y": inputs.get("x")})
    ev._specs[sid].procedure = {"capability": "handler"}  # type: ignore[assignment]
    ev._storage.update("evaluation_spec", sid, {"procedure": {"capability": "handler"}})

    run_result = ev.run(sid, [gt_id])
    assert run_result["ok"] is True

    report = ev.generate_report([run_result["run_id"]])
    assert report["ok"] is True
    assert "markdown" in report


def test_evaluation_run_all() -> None:
    storage = FakeStorage()
    ev = Evaluation(storage)
    ev.register_spec(EvalSpec(name="a", category="test"))
    ev.register_spec(EvalSpec(name="b", category="test"))
    results = ev.run_all()
    assert len(results) == 2


# --- Scoring helpers ---


def test_precision_empty_actual() -> None:
    from src.self.evaluation.evaluation_runner import EvaluationRunner

    assert EvaluationRunner._precision(set(), {"a"}) == 1.0


def test_precision_perfect() -> None:
    from src.self.evaluation.evaluation_runner import EvaluationRunner

    assert EvaluationRunner._precision({"a", "b"}, {"a", "b"}) == 1.0


def test_precision_partial() -> None:
    from src.self.evaluation.evaluation_runner import EvaluationRunner

    assert EvaluationRunner._precision({"a", "b", "c"}, {"a"}) == 1.0 / 3.0


def test_recall_empty_expected() -> None:
    from src.self.evaluation.evaluation_runner import EvaluationRunner

    assert EvaluationRunner._recall({"a"}, set()) == 1.0


def test_recall_partial() -> None:
    from src.self.evaluation.evaluation_runner import EvaluationRunner

    assert EvaluationRunner._recall({"a"}, {"a", "b"}) == 0.5


def test_accuracy_identical() -> None:
    from src.self.evaluation.evaluation_runner import EvaluationRunner

    assert EvaluationRunner._accuracy({"a", "b"}, {"a", "b"}) == 1.0


def test_accuracy_scalar() -> None:
    from src.self.evaluation.evaluation_runner import EvaluationRunner

    assert EvaluationRunner._accuracy(42, 42) == 1.0
    assert EvaluationRunner._accuracy(42, 43) == 0.0
