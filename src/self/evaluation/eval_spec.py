"""Evaluation specification — defines what to evaluate and how to score it."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4


class EvalSpec:
    def __init__(
        self,
        name: str,
        category: str,
        description: str = "",
        inputs: dict[str, Any] | None = None,
        procedure: dict[str, Any] | None = None,
        expected_outputs: dict[str, Any] | None = None,
        scoring_criteria: dict[str, Any] | None = None,
        pass_threshold: float = 0.8,
    ) -> None:
        self.id = f"ev_{uuid4().hex}"
        self.name = name
        self.category = category
        self.description = description
        self.inputs = inputs or {}
        self.procedure = procedure or {}
        self.expected_outputs = expected_outputs or {}
        self.scoring_criteria = scoring_criteria or {}
        self.pass_threshold = pass_threshold

    def to_record(self) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        return {
            "schema_version": "0.1.0",
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "inputs": self.inputs,
            "procedure": self.procedure,
            "expected_outputs": self.expected_outputs,
            "scoring_criteria": self.scoring_criteria,
            "pass_threshold": self.pass_threshold,
            "created_at": now,
            "updated_at": now,
        }

    @staticmethod
    def from_record(record: dict[str, Any]) -> EvalSpec:
        spec = EvalSpec(
            name=record["name"],
            category=record["category"],
            description=record.get("description", ""),
            inputs=record.get("inputs", {}),
            procedure=record.get("procedure", {}),
            expected_outputs=record.get("expected_outputs", {}),
            scoring_criteria=record.get("scoring_criteria", {}),
            pass_threshold=record.get("pass_threshold", 0.8),
        )
        spec.id = record["id"]
        return spec


def builtin_specs() -> list[EvalSpec]:
    return [
        EvalSpec(
            name="extract_belief",
            category="capability",
            description="Measure extraction precision and recall for belief objects",
            procedure={"capability": "extraction", "prompt": "extract_belief"},
            scoring_criteria={
                "precision": {"weight": 1.0, "higher_is_better": True},
                "recall": {"weight": 1.0, "higher_is_better": True},
            },
            pass_threshold=0.7,
        ),
        EvalSpec(
            name="detect_goal",
            category="capability",
            description="Measure goal detection accuracy from observation events",
            procedure={"capability": "extraction", "prompt": "detect_goal"},
            scoring_criteria={
                "precision": {"weight": 1.0, "higher_is_better": True},
                "recall": {"weight": 1.0, "higher_is_better": True},
            },
            pass_threshold=0.7,
        ),
        EvalSpec(
            name="memory_retrieval",
            category="capability",
            description="Measure semantic search recall and precision in Memory",
            procedure={"capability": "memory", "operation": "semantic_search"},
            scoring_criteria={
                "recall_at_k": {"weight": 1.0, "higher_is_better": True},
                "precision_at_k": {"weight": 1.0, "higher_is_better": True},
            },
            pass_threshold=0.6,
        ),
        EvalSpec(
            name="entity_resolution",
            category="capability",
            description="Measure entity resolution accuracy in Identity Graph",
            procedure={"capability": "identity_graph", "operation": "resolve"},
            scoring_criteria={
                "accuracy": {"weight": 1.0, "higher_is_better": True},
            },
            pass_threshold=0.8,
        ),
        EvalSpec(
            name="persona_consistency",
            category="capability",
            description="Measure persona vector consistency score stability",
            procedure={"capability": "persona_engine", "operation": "score_consistency"},
            scoring_criteria={
                "consistency": {"weight": 1.0, "higher_is_better": True},
            },
            pass_threshold=0.5,
        ),
    ]
