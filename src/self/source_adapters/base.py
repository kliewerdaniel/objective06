"""Base class for source adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseSourceAdapter(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @abstractmethod
    def poll(self) -> list[dict[str, Any]]: ...

    @abstractmethod
    def health(self) -> dict[str, Any]: ...

    @abstractmethod
    def start(self) -> None: ...

    @abstractmethod
    def stop(self) -> None: ...
