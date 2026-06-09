"""Citation Tracker — map assertions to source records."""

from __future__ import annotations

from typing import Any
from uuid import uuid4


class CitationTracker:
    def __init__(self) -> None:
        self._citations: dict[str, list[dict[str, Any]]] = {}

    def add_assertion(self, answer_id: str, assertion: str, source_ids: list[str]) -> str:
        cid = f"cit_{uuid4().hex}"
        self._citations.setdefault(answer_id, []).append(
            {"id": cid, "assertion": assertion, "source_ids": source_ids}
        )
        return cid

    def get_citations(self, answer_id: str) -> list[dict[str, Any]]:
        return self._citations.get(answer_id, [])

    def format_citations(self, answer_id: str) -> str:
        citations = self.get_citations(answer_id)
        if not citations:
            return ""
        parts: list[str] = []
        for i, c in enumerate(citations, 1):
            ids = ", ".join(c["source_ids"])
            parts.append(f"[{i}] {c['assertion'][:80]}... → {ids}")
        return "\n".join(parts)
