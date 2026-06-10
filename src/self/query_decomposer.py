"""Query Decomposer — breaks complex queries into sub-queries."""

from __future__ import annotations

import re
from typing import Any


class QueryDecomposer:
    def __init__(self) -> None:
        self._complexity_threshold = 2

    def decompose(self, query: str) -> list[dict[str, Any]]:
        if not query or not query.strip():
            return []

        sub_queries = self._extract_sub_queries(query)
        if len(sub_queries) <= 1:
            return [
                {
                    "original": query,
                    "sub_queries": [query],
                    "intent": self._classify_intent(query),
                    "complexity": "simple",
                }
            ]

        return [
            {
                "original": query,
                "sub_queries": sub_queries,
                "intent": "complex",
                "complexity": "complex",
                "sub_intents": [self._classify_intent(sq) for sq in sub_queries],
            }
        ]

    def _extract_sub_queries(self, query: str) -> list[str]:
        pattern = r"\s+(?:and|also|additionally|furthermore|moreover)\s+"
        parts = re.split(pattern, query, flags=re.IGNORECASE)
        sub_queries = [p.strip() for p in parts if p.strip()]
        return sub_queries if len(sub_queries) > 1 else [query]

    def _classify_intent(self, query: str) -> str:
        query_lower = query.lower()
        factual_words = ["what", "when", "where", "who", "how", "tell", "show", "describe"]
        if any(w in query_lower for w in factual_words):
            return "factual"
        elif any(w in query_lower for w in ["project", "work", "task", "goal"]):
            return "entity"
        elif any(w in query_lower for w in ["think", "believe", "opinion", "feel"]):
            return "reflection"
        else:
            return "conversation"
