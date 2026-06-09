"""Output validator — JSON parsing, schema validation, type coercion."""

from __future__ import annotations

import json
from typing import Any


class ValidationError(Exception):
    def __init__(self, message: str, details: list[str] | None = None) -> None:
        self.details = details or []
        full = f"{message}: {'; '.join(details)}" if details else message
        super().__init__(full)


class OutputValidator:
    def parse_json(self, text: str) -> Any:
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            msg = f"Failed to parse JSON output: {e}"
            raise ValidationError(msg, [str(e)]) from e

    def validate_schema(self, obj: Any, schema: dict[str, Any]) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []
        errors: list[str] = []

        expected_type = schema.get("type", "array")
        if expected_type == "array":
            if not isinstance(obj, list):
                errors.append(f"Expected array, got {type(obj).__name__}")
                raise ValidationError("Schema validation failed", errors)
            item_schema = schema.get("items", {})
            for item in obj:
                if not isinstance(item, dict):
                    errors.append(f"Expected object in array, got {type(item).__name__}")
                    continue
                item_errors = self._validate_object(item, item_schema)
                if item_errors:
                    errors.extend(item_errors)
                else:
                    coerced = self._coerce_types(item, item_schema)
                    results.append(coerced)
        elif expected_type == "object":
            if not isinstance(obj, dict):
                errors.append(f"Expected object, got {type(obj).__name__}")
                raise ValidationError("Schema validation failed", errors)
            item_errors = self._validate_object(obj, schema)
            if item_errors:
                errors.extend(item_errors)
            else:
                results.append(self._coerce_types(obj, schema))

        if errors:
            raise ValidationError("Schema validation failed", errors)
        return results

    def _validate_object(self, obj: dict, schema: dict) -> list[str]:
        errors: list[str] = []
        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for field in required:
            if field not in obj or obj[field] is None:
                errors.append(f"Missing required field: {field}")

        for field, value in obj.items():
            if field in properties:
                expected = properties[field].get("type", "string")
                if expected == "number" and isinstance(value, (int, float)):
                    continue
                if expected == "string" and isinstance(value, str):
                    continue
                if expected == "array" and isinstance(value, list):
                    continue
                if expected == "object" and isinstance(value, dict):
                    continue
                if expected == "boolean" and isinstance(value, bool):
                    continue
                errors.append(f"Field '{field}': expected {expected}, got {type(value).__name__}")
        return errors

    def _coerce_types(self, obj: dict, schema: dict) -> dict:
        result = dict(obj)
        properties = schema.get("properties", {})
        for field, value in result.items():
            if field not in properties:
                continue
            expected = properties[field].get("type", "string")
            if expected == "number" and isinstance(value, (int, float)):
                result[field] = float(value)
            elif expected == "string" and not isinstance(value, str):
                result[field] = str(value)
        return result
