"""Normalizer — produces canonical observation_event records from raw source data."""

from __future__ import annotations

import hashlib
import json
import time
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

ADAPTER_VERSION = "0.1.0"
SCHEMA_VERSION = "0.1.0"


def compute_content_hash(payload_data: dict[str, Any]) -> str:
    raw = json.dumps(payload_data, sort_keys=True, default=str)
    return f"sha256:{hashlib.sha256(raw.encode()).hexdigest()}"


def generate_event_id() -> str:
    return f"evt_{uuid4().hex}"


class Normalizer:
    def __init__(self, producer: str = "observer") -> None:
        self._producer = producer
        self._monotonic_base = time.monotonic_ns()

    def normalize(
        self,
        *,
        event_type: str,
        source_kind: str,
        source_identifier: str,
        adapter: str,
        actor_kind: str,
        actor_identifier: str,
        payload_summary: str,
        payload_data: dict[str, Any],
        subject_kind: str | None = None,
        subject_identifier: str | None = None,
        subject_attributes: dict[str, Any] | None = None,
        timestamp: str | None = None,
        tags: list[str] | None = None,
        parent_ids: list[str] | None = None,
        notes: str | None = None,
    ) -> dict[str, Any]:
        now_utc = datetime.now(UTC)
        event_id = generate_event_id()
        wall_time = timestamp or now_utc.isoformat()
        monotonic_ts = time.monotonic_ns()

        content_hash = compute_content_hash(payload_data)

        event = {
            "schema_version": SCHEMA_VERSION,
            "id": event_id,
            "event_type": event_type,
            "source": {
                "kind": source_kind,
                "identifier": source_identifier,
                "adapter": adapter,
                "adapter_version": ADAPTER_VERSION,
            },
            "timestamp": wall_time,
            "monotonic_ts": monotonic_ts,
            "observed_at": now_utc.isoformat(),
            "actor": {
                "kind": actor_kind,
                "identifier": actor_identifier,
            },
            "subject": {
                "kind": subject_kind or "",
                "identifier": subject_identifier or "",
                "attributes": subject_attributes or {},
            },
            "payload": {
                "summary": payload_summary,
                "data": payload_data,
                "entities": [],
                "language": None,
            },
            "content_hash": content_hash,
            "raw_ref": None,
            "tags": tags or [],
            "provenance": {
                "producer": f"observer.{adapter}",
                "producer_version": ADAPTER_VERSION,
                "produced_at": now_utc.isoformat(),
                "parent_ids": parent_ids or [],
                "model": None,
                "model_version": None,
                "prompt_template": None,
                "prompt_version": None,
                "confidence": 1.0,
                "notes": notes or "",
            },
        }
        return event
