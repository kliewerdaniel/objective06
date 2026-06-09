"""Onboarding flow for first-run setup."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel


class OnboardingData(BaseModel):
    role: str
    top_interests: list[str]
    top_projects: list[str]
    free_form: str


class OnboardingFlow:
    def __init__(self, storage: Any, persona_engine: Any | None = None) -> None:
        self._storage = storage
        self._persona_engine = persona_engine

    def collect_self_description(
        self,
        role: str,
        interests: list[str],
        projects: list[str],
        free_form: str,
    ) -> dict[str, Any]:
        onboarding_data = OnboardingData(
            role=role,
            top_interests=interests,
            top_projects=projects,
            free_form=free_form,
        )

        event: dict[str, Any] = {
            "schema_version": "0.1.0",
            "id": f"evt_{uuid4().hex}",
            "event_type": "system.onboarding",
            "source": {
                "kind": "system",
                "identifier": "self",
                "adapter": "onboarding",
                "adapter_version": "0.1.0",
            },
            "timestamp": datetime.now(UTC).isoformat(),
            "monotonic_ts": int(datetime.now(UTC).timestamp() * 1_000_000),
            "observed_at": datetime.now(UTC).isoformat(),
            "actor": {"kind": "user", "identifier": "user"},
            "subject": {"kind": "onboarding", "identifier": "self_description"},
            "payload": {
                "summary": "User onboarding self-description",
                "data": onboarding_data.model_dump(),
            },
            "content_hash": "",
            "tags": ["onboarding", "system"],
            "provenance": {
                "producer": "onboarding_flow",
                "producer_version": "0.1.0",
                "produced_at": datetime.now(UTC).isoformat(),
                "parent_ids": [],
                "confidence": 1.0,
            },
        }

        raw = json.dumps(event["payload"]["data"], sort_keys=True, default=str)
        event["content_hash"] = f"sha256:{hashlib.sha256(raw.encode()).hexdigest()}"

        self._storage.insert("observation_event", event)
        return event

    @staticmethod
    def needs_onboarding(storage: Any) -> bool:
        result = storage.query("observation_event", {"event_type": "system.onboarding", "limit": 1})
        return len(result) == 0

    @staticmethod
    def should_defer_synthesis(storage: Any) -> bool:
        result = storage.query("observation_event", {"limit": 1000})
        return len(result) < 100
