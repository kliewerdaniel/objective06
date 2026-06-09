"""Prompt Sanitizer — injection pattern detection."""

from __future__ import annotations

import re
from typing import Any

INJECTION_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"forget\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+(instructions|directives)", re.IGNORECASE),
    re.compile(r"you\s+are\s+(now|not\s+an?\s+AI|a\s+free)", re.IGNORECASE),
    re.compile(r"system\s+(prompt|message|instruction)", re.IGNORECASE),
    re.compile(r"role.{0,10}system", re.IGNORECASE),
]


class PromptSanitizer:
    def __init__(self) -> None:
        self._patterns = INJECTION_PATTERNS

    def check(self, text: str) -> dict[str, Any]:
        for pattern in self._patterns:
            match = pattern.search(text)
            if match:
                return {
                    "safe": False,
                    "reason": f"Matched injection pattern: {pattern.pattern}",
                    "matched": match.group(),
                }
        return {"safe": True, "reason": ""}
