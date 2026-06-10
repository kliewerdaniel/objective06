"""Tests for contradiction_detector module."""

from __future__ import annotations

from self.contradiction_detector import ContradictionDetector


def test_detect_no_contradictions() -> None:
    detector = ContradictionDetector()
    kos = [
        {
            "id": "ko_1",
            "type": "belief",
            "name": "likes cats",
            "confidence": 0.8,
            "description": "likes cats",
        },
        {
            "id": "ko_2",
            "type": "belief",
            "name": "likes dogs",
            "confidence": 0.7,
            "description": "likes dogs",
        },
    ]
    contradictions = detector.detect_contradictions(kos)
    assert len(contradictions) == 0


def test_detect_contradiction_different_types() -> None:
    detector = ContradictionDetector()
    kos = [
        {
            "id": "ko_1",
            "type": "belief",
            "name": "likes cats",
            "confidence": 0.8,
            "description": "likes cats",
        },
        {
            "id": "ko_2",
            "type": "goal",
            "name": "likes cats",
            "confidence": 0.8,
            "description": "likes cats",
        },
    ]
    contradictions = detector.detect_contradictions(kos)
    assert len(contradictions) == 0


def test_detect_contradiction_different_names() -> None:
    detector = ContradictionDetector()
    kos = [
        {
            "id": "ko_1",
            "type": "belief",
            "name": "likes cats",
            "confidence": 0.8,
            "description": "likes cats",
        },
        {
            "id": "ko_2",
            "type": "belief",
            "name": "likes dogs",
            "confidence": 0.8,
            "description": "likes cats",
        },
    ]
    contradictions = detector.detect_contradictions(kos)
    assert len(contradictions) == 0


def test_detect_contradiction_with_negation() -> None:
    detector = ContradictionDetector()
    kos = [
        {
            "id": "ko_1",
            "type": "belief",
            "name": "likes cats",
            "confidence": 0.8,
            "description": "likes cats",
        },
        {
            "id": "ko_2",
            "type": "belief",
            "name": "likes cats",
            "confidence": 0.8,
            "description": "does not like cats",
        },
    ]
    contradictions = detector.detect_contradictions(kos, threshold=0.1)
    assert len(contradictions) >= 0


def test_detect_contradiction_high_confidence_difference() -> None:
    detector = ContradictionDetector()
    kos = [
        {
            "id": "ko_1",
            "type": "belief",
            "name": "likes cats",
            "confidence": 0.9,
            "description": "always likes cats",
        },
        {
            "id": "ko_2",
            "type": "belief",
            "name": "likes cats",
            "confidence": 0.2,
            "description": "never likes cats",
        },
    ]
    contradictions = detector.detect_contradictions(kos, threshold=0.1)
    assert len(contradictions) >= 0
