"""Source adapters for the Observer subsystem."""

from __future__ import annotations

from .base import BaseSourceAdapter
from .browser_history import BrowserHistoryAdapter
from .calendar_adapter import CalendarAdapter
from .email_adapter import EmailAdapter
from .filesystem import FilesystemWatcher
from .git_adapter import GitPollingAdapter
from .github_poller import GitHubPoller
from .rss_feed import RSSFeedAdapter
from .terminal_session import TerminalSessionAdapter

__all__ = [
    "BaseSourceAdapter",
    "BrowserHistoryAdapter",
    "CalendarAdapter",
    "EmailAdapter",
    "FilesystemWatcher",
    "GitPollingAdapter",
    "GitHubPoller",
    "RSSFeedAdapter",
    "TerminalSessionAdapter",
]
