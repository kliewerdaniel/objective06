"""Digital Twin — conversational facade."""

from __future__ import annotations

from typing import Any

from .answer_composer import AnswerComposer
from .citation_tracker import CitationTracker
from .intent_classifier import IntentClassifier
from .prompt_sanitizer import PromptSanitizer
from .query_intake import QueryIntake
from .query_router import QueryRouter
from .session_manager import SessionManager


class DigitalTwin:
    def __init__(
        self, memory: Any, model_client: Any, identity_graph: Any, persona_engine: Any
    ) -> None:
        self._session_manager = SessionManager()
        self._sanitizer = PromptSanitizer()
        self._intake = QueryIntake(self._session_manager, self._sanitizer)
        self._classifier = IntentClassifier(model_client)
        self._router = QueryRouter(memory, identity_graph, persona_engine, model_client)
        self._tracker = CitationTracker()
        self._composer = AnswerComposer(model_client, self._tracker)

    def ask(self, query: str, session_id: str = "") -> dict[str, Any]:
        result = self._intake.receive(query, session_id)
        if not result.get("ok", False):
            return result
        sid = result["session_id"]
        intent = self._classifier.classify(query)
        conf = self._classifier.confidence(query)
        if conf < 0.3:
            intent = "conversation"
        session = self._session_manager.get_session(sid)
        route_result = self._router.route(intent, query, (session or {}).get("context"))
        answer = self._composer.compose(query, intent, route_result)
        answer["intent"] = intent
        answer["session_id"] = sid
        self._session_manager.add_turn(sid, query, answer)
        return answer
