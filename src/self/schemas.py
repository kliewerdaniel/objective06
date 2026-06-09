"""Core schema definitions for SELF data types."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, model_validator


class Provenance(BaseModel):
    producer: str
    producer_version: str
    produced_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    parent_ids: list[str] = Field(default_factory=list)
    model: str | None = None
    model_version: str | None = None
    prompt_template: str | None = None
    prompt_version: str | None = None
    confidence: float | None = None
    notes: str | None = None


class Source(BaseModel):
    kind: str
    identifier: str
    adapter: str
    adapter_version: str


class Actor(BaseModel):
    kind: str  # "user", "system", "service", "external"
    identifier: str


class Subject(BaseModel):
    kind: str
    identifier: str
    attributes: dict[str, Any] = Field(default_factory=dict)


class EntityHint(BaseModel):
    name: str
    type: str | None = None
    span: dict[str, int] | None = None


class Payload(BaseModel):
    summary: str
    data: dict[str, Any] = Field(default_factory=dict)
    entities: list[EntityHint] = Field(default_factory=list)
    language: str | None = None


class ObservationEvent(BaseModel):
    schema_version: str = "0.1.0"
    id: str = Field(default_factory=lambda: f"evt_{uuid4().hex}")
    event_type: str
    source: Source
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    monotonic_ts: int = Field(
        default_factory=lambda: int(datetime.now(UTC).timestamp() * 1_000_000)
    )
    observed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor: Actor
    subject: Subject | None = None
    payload: Payload
    content_hash: str = ""
    raw_ref: str | None = None
    tags: list[str] = Field(default_factory=list)
    provenance: Provenance

    @model_validator(mode="after")
    def _ensure_hash(self) -> ObservationEvent:
        if not self.content_hash and self.payload:
            import hashlib
            import json

            raw = json.dumps(self.payload.data, sort_keys=True, default=str)
            self.content_hash = f"sha256:{hashlib.sha256(raw.encode()).hexdigest()}"
        return self


class KnowledgeObject(BaseModel):
    schema_version: str = "0.1.0"
    id: str = Field(default_factory=lambda: f"ko_{uuid4().hex}")
    type: str  # "belief", "goal", "project", "interest", "relationship", "entity"
    name: str
    description: str = ""
    attributes: dict[str, Any] = Field(default_factory=dict)
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    provenance: Provenance
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    deprecated: bool = False
    superseded_by: str | None = None


class AuditLogEntry(BaseModel):
    schema_version: str = "0.1.0"
    id: str = Field(default_factory=lambda: f"aud_{uuid4().hex}")
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    actor: str  # subsystem or user ID
    action: str  # "create", "update", "delete", "access", "auth", "error"
    entity_type: str  # e.g., "observation_event", "knowledge_object"
    entity_id: str
    before_hash: str | None = None
    after_hash: str | None = None
    reason: str | None = None
    prev_hash: str | None = None  # SHA-256 of previous entry for chain integrity
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_canonical_json(self) -> str:
        import json

        return json.dumps(
            self.model_dump(mode="json", exclude={"prev_hash"}),
            sort_keys=True,
            default=str,
        )


class EventLogEntry(BaseModel):
    schema_version: str = "0.1.0"
    id: str = Field(default_factory=lambda: f"el_{uuid4().hex}")
    event_id: str  # reference to observation_event.id
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    source_kind: str
    event_type: str
    content_hash: str
    raw_payload_ref: str | None = None
