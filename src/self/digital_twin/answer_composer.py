"""Answer Composer — compose grounded natural-language answers."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from .citation_tracker import CitationTracker


class AnswerComposer:
    def __init__(self, model_client: Any, citation_tracker: CitationTracker | None = None) -> None:
        self._model = model_client
        self._tracker = citation_tracker or CitationTracker()

    def compose(self, query: str, intent: str, route_result: dict[str, Any]) -> dict[str, Any]:
        aid = f"ans_{uuid4().hex}"
        source = route_result.get("source", "unknown")
        if source == "model":
            return self._compose_conversation(query, aid)
        if source == "system":
            return self._compose_system(query, route_result, aid)
        context = self._format_context(route_result)
        prompt = (
            f"Answer the user's query based ONLY on the provided context. "
            f"If the context does not contain the answer, say you cannot answer.\n\n"
            f"User query: {query}\n\n"
            f"Context: {context}\n\n"
            f"Answer the query using only the context. "
            f"Be concise. Mark uncertainty explicitly."
        )
        try:
            result = self._model.generate(prompt)
            text = result.get("text", "I cannot answer that question based on what I know.")
            self._build_citations(aid, text, route_result)
            return {
                "answer_id": aid,
                "text": text,
                "citations": self._tracker.format_citations(aid),
                "confidence": result.get("tokens", 0) / 100 if result.get("tokens", 0) > 0 else 0.5,
            }
        except Exception:
            return {
                "answer_id": aid,
                "text": "I cannot answer that question right now.",
                "citations": "",
                "confidence": 0.0,
            }

    def _compose_conversation(self, query: str, aid: str) -> dict[str, Any]:
        prompt = f"The user says: {query}\n\nRespond naturally and conversationally."
        try:
            result = self._model.generate(prompt)
            return {
                "answer_id": aid,
                "text": result.get("text", ""),
                "citations": "",
                "confidence": 0.8,
            }
        except Exception:
            return {
                "answer_id": aid,
                "text": "I'm here to help.",
                "citations": "",
                "confidence": 0.5,
            }

    def _compose_system(self, query: str, route_result: dict[str, Any], aid: str) -> dict[str, Any]:
        ctx = route_result.get("context", {})
        turn_count = ctx.get("turn_count", 0)
        entities = ctx.get("entities", [])
        text = f"I know about you from our conversation so far. We've had {turn_count} turns. "
        if entities:
            text += f"I know about: {', '.join(entities)}."
        else:
            text += "I'm still getting to know you."
        return {"answer_id": aid, "text": text, "citations": "", "confidence": 0.9}

    def _format_context(self, route_result: dict[str, Any]) -> str:
        parts: list[str] = []
        if "events" in route_result:
            for e in route_result["events"][:5]:
                parts.append(f"Event: {e.get('event_type', 'unknown')} at {e.get('timestamp', '')}")
        if "knowledge" in route_result:
            for k in route_result["knowledge"][:5]:
                parts.append(f"Knowledge: {k.get('name', '')} — {k.get('description', '')}")
        if "nodes" in route_result:
            for n in route_result["nodes"][:5]:
                parts.append(f"Entity: {n.get('name', '')} (type: {n.get('type', '')})")
        return "\n".join(parts) or "No relevant context found."

    def _build_citations(self, aid: str, text: str, route_result: dict[str, Any]) -> None:
        if "events" in route_result:
            for e in route_result["events"][:5]:
                self._tracker.add_assertion(aid, e.get("event_type", ""), [e.get("id", "")])
        if "knowledge" in route_result:
            for k in route_result["knowledge"][:5]:
                self._tracker.add_assertion(aid, k.get("name", ""), [k.get("id", "")])
