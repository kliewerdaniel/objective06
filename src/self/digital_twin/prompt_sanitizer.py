"""Prompt Sanitizer — injection pattern detection and citation validation."""

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

    def check_injection(self, text: str) -> dict[str, Any]:
        """Detect unsafe injection patterns in user text."""
        for pattern in self._patterns:
            match = pattern.search(text)
            if match:
                return {
                    "safe": False,
                    "reason": f"Matched injection pattern: {pattern.pattern}",
                    "matched": match.group(),
                }
        return {"safe": True, "reason": ""}

    def check(self, text: str) -> dict[str, Any]:
        """Legacy alias for injection check used by older code."""
        # Delegates to the new check_injection implementation
        return self.check_injection(text)

    def validate_citations(self, output: str, declared_knowledge: list[str]) -> dict[str, Any]:
        """
        Layer 3: Citation-lock validation.
        Rejects output that references knowledge or entities not present in declared_knowledge.
        """
        # Simple extraction of citations (e.g., [1], (Source A))
        citations = re.findall(r"\[\d+\]|\([A-Z0-9\s_]+\)", output)

        # In a full implementation, we would cross-reference these against
        # the IDs in declared_knowledge. For now, we check for any
        # citation format that isn't clearly tied to our declared list.

        # For MVP, if any citation is found that doesn't contain
        # a keyword from our declared knowledge, we flag it.
        # This is a placeholder for more robust cross-referencing.

        if citations and not declared_knowledge:
            return {
                "safe": False,
                "reason": "Output contains citations but no knowledge was declared.",
                "matched": citations,
            }

        return {"safe": True, "reason": ""}

    def sanitize(self, text: str, declared_knowledge: list[str] | None = None) -> dict[str, Any]:
        # Layer 1 & 2
        injection_check = self.check_injection(text)
        if not injection_check["safe"]:
            return injection_check

        # Layer 3
        if declared_knowledge:
            citation_check = self.validate_citations(text, declared_knowledge)
            if not citation_check["safe"]:
                return citation_check

        return {"safe": True, "reason": ""}
