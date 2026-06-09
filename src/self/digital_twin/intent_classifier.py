"""Intent Classifier — classify query intents."""

from __future__ import annotations

from typing import Any

INTENTS = [
    "factual_retrieval",
    "entity_exploration",
    "summary_request",
    "reflection_request",
    "prediction_request",
    "action_proposal",
    "meta_question",
    "conversation",
]


class IntentClassifier:
    def __init__(self, model_client: Any) -> None:
        self._model = model_client

    def classify(self, query: str) -> str:
        prompt = (
            f"Classify the following user query into exactly one of these intents: "
            f"{', '.join(INTENTS)}.\n\nQuery: {query}\n\nIntent:"
        )
        try:
            result = self._model.generate(prompt)
            text = result.get("text", "").strip().lower()
            for intent in INTENTS:
                if intent in text:
                    return intent
            return "conversation"
        except Exception:
            return "conversation"

    def confidence(self, query: str) -> float:
        prompt = (
            f"Rate your confidence (0.0 to 1.0) in understanding the following query. "
            f"Return only a number between 0 and 1.\n\nQuery: {query}\n\nConfidence:"
        )
        try:
            result = self._model.generate(prompt)
            text = result.get("text", "").strip()
            val = float(text)
            return max(0.0, min(1.0, val))
        except Exception:
            return 0.5
