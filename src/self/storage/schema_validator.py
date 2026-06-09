"""Schema validation for SELF data records."""

from __future__ import annotations

from typing import Any


class SchemaValidationError(Exception):
    def __init__(self, message: str, record_type: str, errors: list[str]) -> None:
        self.record_type = record_type
        self.errors = errors
        super().__init__(f"{message}: {'; '.join(errors)}")


class SchemaValidator:
    REQUIRED_FIELDS: dict[str, set[str]] = {
        "observation_event": {
            "schema_version",
            "id",
            "event_type",
            "source",
            "timestamp",
            "observed_at",
            "actor",
            "payload",
            "provenance",
        },
        "knowledge_object": {
            "schema_version",
            "id",
            "type",
            "name",
            "confidence",
            "provenance",
        },
        "audit_log_entry": {
            "schema_version",
            "id",
            "timestamp",
            "actor",
            "action",
            "entity_type",
            "entity_id",
        },
        "event_log_entry": {
            "schema_version",
            "id",
            "event_id",
            "timestamp",
            "source_kind",
            "event_type",
            "content_hash",
        },
        "ingest_queue": {
            "schema_version",
            "id",
            "event_id",
            "event",
            "priority",
            "queued_at",
            "status",
        },
        "summary": {
            "schema_version",
            "id",
            "type",
            "content",
            "created_at",
        },
        "identity_node": {
            "schema_version",
            "id",
            "type",
            "name",
            "created_at",
            "updated_at",
            "valid_from",
        },
        "identity_edge": {
            "schema_version",
            "id",
            "type",
            "source_id",
            "target_id",
            "created_at",
            "valid_from",
        },
        "entity_resolution": {
            "schema_version",
            "id",
            "candidate_name",
            "resolved_node_id",
            "resolved_at",
        },
        "attribute_change": {
            "schema_version",
            "id",
            "entity_type",
            "entity_id",
            "attribute",
            "changed_at",
        },
        "persona_snapshot": {
            "schema_version",
            "id",
            "model_id",
            "vector",
            "timestamp",
        },
        "action_request": {
            "schema_version",
            "id",
            "capability",
            "params",
            "requested_by",
            "status",
            "sensitivity",
            "created_at",
            "updated_at",
        },
        "action_result": {
            "schema_version",
            "id",
            "request_id",
            "status",
            "executed_at",
        },
        "action_audit": {
            "schema_version",
            "id",
            "request_id",
            "step",
            "status",
            "timestamp",
        },
        "permission_grant": {
            "schema_version",
            "id",
            "user",
            "capability",
            "granted_at",
        },
        "auth_session": {
            "schema_version",
            "id",
            "user",
            "token_hash",
            "created_at",
            "expires_at",
        },
        "secret_record": {
            "schema_version",
            "id",
            "name",
            "encrypted_value",
            "created_at",
            "updated_at",
        },
        "evaluation_spec": {
            "schema_version",
            "id",
            "name",
            "category",
            "pass_threshold",
            "created_at",
            "updated_at",
        },
        "evaluation_run": {
            "schema_version",
            "id",
            "spec_id",
            "status",
            "started_at",
        },
        "evaluation_result": {
            "schema_version",
            "id",
            "run_id",
            "metric",
            "score",
            "passed",
            "recorded_at",
        },
        "evaluation_report": {
            "schema_version",
            "id",
            "run_ids",
            "summary",
            "markdown",
            "created_at",
        },
        "ground_truth": {
            "schema_version",
            "id",
            "spec_id",
            "inputs",
            "expected_outputs",
            "version",
            "created_at",
            "updated_at",
        },
    }

    VERSIONED_TYPES = {
        "observation_event",
        "knowledge_object",
        "audit_log_entry",
        "event_log_entry",
    }

    def validate(self, record_type: str, record: dict[str, Any]) -> None:
        errors: list[str] = []

        if record_type not in self.REQUIRED_FIELDS:
            errors.append(f"Unknown record type: {record_type}")

        if record_type in self.REQUIRED_FIELDS:
            for field in self.REQUIRED_FIELDS[record_type]:
                if field not in record or record[field] is None:
                    errors.append(f"Missing required field: {field}")

        if record_type in self.VERSIONED_TYPES:
            sv = record.get("schema_version")
            if not sv:
                errors.append("Missing schema_version for versioned type")

        if errors:
            raise SchemaValidationError(
                f"Schema validation failed for {record_type}",
                record_type,
                errors,
            )

    def is_valid(self, record_type: str, record: dict[str, Any]) -> bool:
        try:
            self.validate(record_type, record)
            return True
        except SchemaValidationError:
            return False
