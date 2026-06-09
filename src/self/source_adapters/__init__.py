"""Source adapters for the Observer subsystem."""

from __future__ import annotations

from .base import BaseSourceAdapter
from .filesystem import FilesystemWatcher
from .git_adapter import GitPollingAdapter

__all__ = [
    "BaseSourceAdapter",
    "FilesystemWatcher",
    "GitPollingAdapter",
]
