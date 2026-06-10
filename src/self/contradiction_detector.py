"""Contradiction Detector — detects contradictions in knowledge objects."""

from __future__ import annotations

import logging
from typing import Any


class ContradictionDetector:
    def __init__(self, storage: Any = None) -> None:
        self._storage = storage
        self._log = logging.getLogger("self.contradiction_detector")

    def detect_contradictions(
        self,
        knowledge_objects: list[dict[str, Any]],
        threshold: float = 0.7,
    ) -> list[dict[str, Any]]:
        contradictions = []
        for i, ko_a in enumerate(knowledge_objects):
            for ko_b in knowledge_objects[i + 1 :]:
                if self._are_contradictory(ko_a, ko_b, threshold):
                    contradictions.append(
                        {
                            "ko_a": ko_a.get("id"),
                            "ko_b": ko_b.get("id"),
                            "type": "contradiction",
                            "confidence": self._contradiction_confidence(ko_a, ko_b),
                            "details": self._contradiction_details(ko_a, ko_b),
                        }
                    )
        return contradictions

    def _are_contradictory(
        self,
        ko_a: dict[str, Any],
        ko_b: dict[str, Any],
        threshold: float,
    ) -> bool:
        type_a = ko_a.get("type", "")
        type_b = ko_b.get("type", "")
        if type_a != type_b:
            return False
        name_a = ko_a.get("name", "").lower()
        name_b = ko_b.get("name", "").lower()
        if name_a != name_b:
            return False
        confidence_a = ko_a.get("confidence", 0.5)
        confidence_b = ko_b.get("confidence", 0.5)
        if abs(confidence_a - confidence_b) < threshold:
            return False
        return self._semantic_conflict(ko_a, ko_b)

    def _semantic_conflict(
        self,
        ko_a: dict[str, Any],
        ko_b: dict[str, Any],
    ) -> bool:
        desc_a = ko_a.get("description", "").lower()
        desc_b = ko_b.get("description", "").lower()
        negation_words = ["not", "never", "no", "always", "must", "should"]
        for word in negation_words:
            if word in desc_a and word not in desc_b:
                return True
            if word not in desc_a and word in desc_b:
                return True
        return False

    def _contradiction_confidence(
        self,
        ko_a: dict[str, Any],
        ko_b: dict[str, Any],
    ) -> float:
        conf_a = ko_a.get("confidence", 0.5)
        conf_b = ko_b.get("confidence", 0.5)
        return abs(conf_a - conf_b)

    def _contradiction_details(
        self,
        ko_a: dict[str, Any],
        ko_b: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "name": ko_a.get("name", ""),
            "confidence_a": ko_a.get("confidence", 0.5),
            "confidence_b": ko_b.get("confidence", 0.5),
            "description_a": ko_a.get("description", "")[:100],
            "description_b": ko_b.get("description", "")[:100],
        }
