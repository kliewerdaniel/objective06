"""Generation Engine — generates text via ModelClient."""

from __future__ import annotations

from typing import Any


class GenerationEngine:
    def __init__(self, model_client: Any) -> None:
        self._model = model_client

    def generate(self, prompt: str, max_retries: int = 2) -> dict[str, Any]:
        last_error: str | None = None
        for attempt in range(max_retries):
            try:
                result = self._model.generate(prompt)
                text = result.get("text", "")
                return {
                    "text": text,
                    "model": result.get("model", ""),
                    "tokens": result.get("tokens", 0),
                    "duration_ms": result.get("total_duration_ms", 0),
                    "success": True,
                }
            except Exception as e:
                last_error = str(e)
        return {
            "text": "",
            "model": "",
            "tokens": 0,
            "duration_ms": 0,
            "success": False,
            "error": last_error,
        }
