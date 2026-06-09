"""Model client — Ollama adapter for local inference."""

from __future__ import annotations

import logging
import time
from typing import Any

import requests


class ModelClient:
    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model: str = "nomic-embed-text",
        timeout: float = 60.0,
        max_retries: int = 3,
        retry_delay: float = 2.0,
        token_limit: int = 4096,
    ) -> None:
        self._base_url = base_url.rstrip("/")
        self._model = model
        self._timeout = timeout
        self._max_retries = max_retries
        self._retry_delay = retry_delay
        self._token_limit = token_limit
        self._log = logging.getLogger("self.model_client")

    @property
    def model_name(self) -> str:
        return self._model

    def generate(self, prompt: str, system: str | None = None) -> dict[str, Any]:
        body: dict[str, Any] = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": self._token_limit,
            },
        }
        if system:
            body["system"] = system

        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                resp = requests.post(
                    f"{self._base_url}/api/generate",
                    json=body,
                    timeout=self._timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                token_count = data.get("eval_count", 0)
                return {
                    "text": data.get("response", ""),
                    "model": self._model,
                    "tokens": token_count,
                    "total_duration_ms": data.get("total_duration", 0) / 1_000_000,
                }
            except requests.RequestException as e:
                last_error = e
                self._log.warning(
                    "Model request failed (attempt %d/%d): %s",
                    attempt + 1,
                    self._max_retries,
                    e,
                )
                if attempt < self._max_retries - 1:
                    time.sleep(self._retry_delay * (2**attempt))
        msg = f"Model request failed after {self._max_retries} retries"
        raise RuntimeError(msg) from last_error

    def embed(self, text: str) -> list[float]:
        body = {
            "model": self._model,
            "prompt": text,
        }
        try:
            resp = requests.post(
                f"{self._base_url}/api/embeddings",
                json=body,
                timeout=self._timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("embedding", [])
        except requests.RequestException as e:
            self._log.error("Embedding request failed: %s", e)
            return []

    def health(self) -> dict[str, Any]:
        try:
            resp = requests.get(
                f"{self._base_url}/api/tags",
                timeout=5.0,
            )
            if resp.status_code == 200:
                models = resp.json().get("models", [])
                available = any(m["name"].startswith(self._model) for m in models)
                return {"status": "ok", "model_available": available, "model": self._model}
            return {"status": "error", "message": f"HTTP {resp.status_code}"}
        except requests.RequestException as e:
            return {"status": "error", "message": str(e)}
