"""Tests for Model Client."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import requests

from self.model_client import ModelClient


@patch("self.model_client.requests.post")
def test_generate_success(mock_post: MagicMock) -> None:
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "response": '{"result": "ok"}',
        "eval_count": 42,
        "total_duration": 1_000_000_000,
    }
    client = ModelClient(base_url="http://test:11434", model="test-model")
    result = client.generate("test prompt")
    assert result["text"] == '{"result": "ok"}'
    assert result["tokens"] == 42
    assert result["model"] == "test-model"


@patch("self.model_client.requests.post")
def test_generate_retries(mock_post: MagicMock) -> None:
    mock_post.side_effect = requests.ConnectionError("refused")
    client = ModelClient(base_url="http://test:11434", max_retries=2, retry_delay=0.01)
    import pytest

    with pytest.raises(RuntimeError, match="failed after 2 retries"):
        client.generate("test")


@patch("self.model_client.requests.get")
def test_health_available(mock_get: MagicMock) -> None:
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "models": [{"name": "test-model"}],
    }
    client = ModelClient(model="test-model")
    health = client.health()
    assert health["status"] == "ok"
    assert health["model_available"] is True


@patch("self.model_client.requests.get")
def test_health_unavailable(mock_get: MagicMock) -> None:
    mock_get.side_effect = requests.ConnectionError("offline")
    client = ModelClient()
    health = client.health()
    assert health["status"] == "error"
