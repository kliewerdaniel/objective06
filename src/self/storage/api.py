"""Storage API — the single interface all subsystems use for persistence."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Protocol


class QuerySpec(Protocol):
    id: str | None = None
    type: str | None = None
    source_kind: str | None = None
    entity_type: str | None = None
    time_start: str | None = None
    time_end: str | None = None
    actor: str | None = None
    action: str | None = None
    tags: list[str] | None = None
    limit: int = 100
    offset: int = 0


class StorageAPI(ABC):
    @abstractmethod
    def get(self, record_type: str, id: str) -> dict[str, Any] | None: ...

    @abstractmethod
    def query(self, record_type: str, spec: dict[str, Any]) -> list[dict[str, Any]]: ...

    @abstractmethod
    def insert(self, record_type: str, record: dict[str, Any]) -> str: ...

    @abstractmethod
    def update(self, record_type: str, id: str, changes: dict[str, Any]) -> bool: ...

    @abstractmethod
    def delete(self, record_type: str, id: str) -> bool: ...

    @abstractmethod
    def count(self, record_type: str, filter: dict[str, Any] | None = None) -> int: ...

    @abstractmethod
    def close(self) -> None: ...
