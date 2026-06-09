"""Tests for Output Validator."""

from __future__ import annotations

from self.output_validator import OutputValidator, ValidationError


def test_parse_valid_json() -> None:
    v = OutputValidator()
    result = v.parse_json('[{"content": "test", "confidence": 0.9}]')
    assert result == [{"content": "test", "confidence": 0.9}]


def test_parse_invalid_json() -> None:
    v = OutputValidator()
    import pytest

    with pytest.raises(ValidationError):
        v.parse_json("{bad json")


def test_validate_array_schema() -> None:
    v = OutputValidator()
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["content"],
            "properties": {
                "content": {"type": "string"},
                "confidence": {"type": "number"},
            },
        },
    }
    data = [{"content": "hello", "confidence": 0.8}]
    result = v.validate_schema(data, schema)
    assert len(result) == 1
    assert result[0]["content"] == "hello"
    assert result[0]["confidence"] == 0.8


def test_validate_missing_required() -> None:
    v = OutputValidator()
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "required": ["content"],
            "properties": {"content": {"type": "string"}},
        },
    }
    import pytest

    with pytest.raises(ValidationError):
        v.validate_schema([{"confidence": 0.9}], schema)


def test_type_coercion() -> None:
    v = OutputValidator()
    schema = {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "value": {"type": "number"},
            },
        },
    }
    data = [{"value": 42}]
    result = v.validate_schema(data, schema)
    assert result[0]["value"] == 42.0


def test_not_an_array() -> None:
    v = OutputValidator()
    import pytest

    with pytest.raises(ValidationError, match="Expected array"):
        v.validate_schema("not array", {"type": "array"})
