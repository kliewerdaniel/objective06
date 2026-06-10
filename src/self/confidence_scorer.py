"""Confidence Scorer — scores confidence of knowledge objects based on evidence."""

from __future__ import annotations

import logging
from typing import Any


class ConfidenceScorer:
    def __init__(self, storage: Any = None) -> None:
        self._storage = storage
        self._log = logging.getLogger("self.confidence_scorer")

    def score_from_logprobs(self, logprobs: list[float], threshold: float = -5.0) -> float:
        if not logprobs:
            return 0.0
        avg_logprob = sum(logprobs) / len(logprobs)
        normalized = max(0.0, min(1.0, (avg_logprob - threshold) / (-threshold)))
        return normalized

    def score_evidence_strength(
        self,
        source_count: int,
        consistency_score: float,
        recency_hours: float,
    ) -> float:
        source_factor = min(1.0, source_count / 5.0)
        consistency_factor = max(0.0, min(1.0, consistency_score))
        recency_factor = max(0.0, 1.0 - (recency_hours / 168.0))
        weighted = 0.4 * source_factor + 0.4 * consistency_factor + 0.2 * recency_factor
        return max(0.0, min(1.0, weighted))

    def score_knowledge_object(
        self,
        ko: dict[str, Any],
        logprobs: list[float] | None = None,
    ) -> dict[str, Any]:
        base_confidence = ko.get("confidence", 0.5)
        if logprobs:
            logprob_score = self.score_from_logprobs(logprobs)
        else:
            logprob_score = base_confidence

        provenance = ko.get("provenance", {})
        parent_ids = provenance.get("parent_ids", [])
        source_count = len(parent_ids) if parent_ids else 1

        consistency_score = 1.0
        recency_hours = 24.0

        evidence_score = self.score_evidence_strength(
            source_count=source_count,
            consistency_score=consistency_score,
            recency_hours=recency_hours,
        )

        final_score = 0.5 * logprob_score + 0.5 * evidence_score
        return {
            "ko_id": ko.get("id"),
            "original_confidence": base_confidence,
            "logprob_score": logprob_score,
            "evidence_score": evidence_score,
            "final_score": max(0.0, min(1.0, final_score)),
            "components": {
                "source_count": source_count,
                "consistency": consistency_score,
                "recency_hours": recency_hours,
            },
        }
