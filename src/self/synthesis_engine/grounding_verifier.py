"""Grounding Verifier — checks that summary claims are grounded in source data."""

from __future__ import annotations

import re
from typing import Any


class GroundingVerifier:
    def __init__(self) -> None:
        pass

    def verify(self, text: str, context: dict[str, Any]) -> dict[str, Any]:
        if not text:
            return {"grounded": False, "coverage": 0.0, "reason": "Empty text"}
        source_terms: set[str] = set()
        for e in context.get("events", []):
            event_type = e.get("event_type", "")
            if event_type:
                source_terms.add(event_type.lower())
            summary = e.get("payload", {}).get("summary", "")
            for word in summary.split():
                source_terms.add(word.lower())
        for k in context.get("knowledge", []):
            name = k.get("name", "")
            if name:
                source_terms.add(name.lower())
                for word in name.split():
                    source_terms.add(word.lower())
        for n in context.get("nodes", []):
            name = n.get("name", "")
            if name:
                source_terms.add(name.lower())
        sentences = re.split(r"(?<=[.!?])\s+", text)
        covered = 0
        total = len(sentences)
        for sentence in sentences:
            words = set(w.lower() for w in sentence.split() if len(w) > 3)
            if any(term in words for term in source_terms):
                covered += 1
        coverage = covered / total if total > 0 else 0.0
        threshold = 0.3
        return {
            "grounded": coverage >= threshold,
            "coverage": round(coverage, 2),
            "covered_sentences": covered,
            "total_sentences": total,
        }
