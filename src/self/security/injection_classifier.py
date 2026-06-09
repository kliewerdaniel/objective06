"""Injection Classifier — scores untrusted input for prompt injection likelihood."""

from __future__ import annotations

import re
from typing import Any

INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(
        r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|directives|commands)", re.IGNORECASE
    ),
    re.compile(
        r"forget\s+(all\s+)?(previous|prior)\s+(instructions|directives|commands)", re.IGNORECASE
    ),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|directives)", re.IGNORECASE),
    re.compile(r"you\s+are\s+(now|not\s+an?\s+AI|a\s+free|required\s+to)", re.IGNORECASE),
    re.compile(r"system\s+(prompt|message|instruction)", re.IGNORECASE),
    re.compile(r"role.{0,10}system", re.IGNORECASE),
    re.compile(r"override\s+(all\s+)?(previous|prior)", re.IGNORECASE),
    re.compile(r"output\s+your\s+(prompt|instructions|system\s+message)", re.IGNORECASE),
    re.compile(r"print\s+your\s+(prompt|instructions)", re.IGNORECASE),
    re.compile(r"reveal\s+your\s+(prompt|instructions)", re.IGNORECASE),
]


class InjectionClassifier:
    def __init__(self) -> None:
        self._patterns = INJECTION_PATTERNS

    def score(self, text: str) -> dict[str, Any]:
        if not text:
            return {"score": 0.0, "flagged": False, "matches": []}
        matches: list[str] = []
        for pattern in self._patterns:
            if pattern.search(text):
                matches.append(pattern.pattern)
        score = min(1.0, len(matches) * 0.35)
        return {"score": score, "flagged": score >= 0.35, "matches": matches}
