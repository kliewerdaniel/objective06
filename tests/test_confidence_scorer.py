"""Tests for confidence_scorer module."""

from __future__ import annotations

from self.confidence_scorer import ConfidenceScorer


def test_score_from_logprobs_empty() -> None:
    scorer = ConfidenceScorer()
    score = scorer.score_from_logprobs([])
    assert score == 0.0


def test_score_from_logprobs_high_confidence() -> None:
    scorer = ConfidenceScorer()
    logprobs = [-1.0, -1.5, -2.0]
    score = scorer.score_from_logprobs(logprobs)
    assert 0.0 < score <= 1.0


def test_score_from_logprobs_low_confidence() -> None:
    scorer = ConfidenceScorer()
    logprobs = [-10.0, -12.0, -15.0]
    score = scorer.score_from_logprobs(logprobs)
    assert 0.0 <= score < 1.0


def test_score_evidence_strength_multiple_sources() -> None:
    scorer = ConfidenceScorer()
    score = scorer.score_evidence_strength(
        source_count=5,
        consistency_score=0.9,
        recency_hours=12.0,
    )
    assert 0.0 <= score <= 1.0


def test_score_evidence_strength_single_source() -> None:
    scorer = ConfidenceScorer()
    score = scorer.score_evidence_strength(
        source_count=1,
        consistency_score=0.5,
        recency_hours=168.0,
    )
    assert 0.0 <= score <= 1.0


def test_score_knowledge_object() -> None:
    scorer = ConfidenceScorer()
    ko = {
        "id": "ko_test",
        "confidence": 0.7,
        "provenance": {
            "parent_ids": ["evt_1", "evt_2"],
        },
    }
    result = scorer.score_knowledge_object(ko)
    assert result["ko_id"] == "ko_test"
    assert result["original_confidence"] == 0.7
    assert 0.0 <= result["final_score"] <= 1.0
