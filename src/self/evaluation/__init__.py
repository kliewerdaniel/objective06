"""Evaluation subsystem — metrics, benchmarks, and regression detection."""

from __future__ import annotations

from .eval_spec import EvalSpec, builtin_specs
from .evaluation import Evaluation
from .evaluation_runner import EvaluationRunner
from .ground_truth_manager import GroundTruthManager
from .metric_aggregator import MetricAggregator
from .report_generator import ReportGenerator

__all__ = [
    "Evaluation",
    "EvalSpec",
    "builtin_specs",
    "EvaluationRunner",
    "GroundTruthManager",
    "MetricAggregator",
    "ReportGenerator",
]
