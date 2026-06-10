"""Email adapter — polls email for new messages."""

from __future__ import annotations

import time
from typing import Any

from self.source_adapters.base import BaseSourceAdapter


class EmailAdapter(BaseSourceAdapter):
    def __init__(
        self,
        email_folders: list[str] | None = None,
        poll_interval: float = 300.0,
        email_server: str = "imap.gmail.com",
        email_address: str | None = None,
    ) -> None:
        self._folders = email_folders or ["INBOX"]
        self._poll_interval = poll_interval
        self._server = email_server
        self._email_address = email_address
        self._running = False
        self._last_poll = 0.0
        self._seen_uids: dict[str, set[str]] = {}

    @property
    def name(self) -> str:
        return "email"

    def start(self) -> None:
        self._running = True
        for folder in self._folders:
            self._seen_uids[folder] = set()

    def stop(self) -> None:
        self._running = False

    def poll(self) -> list[dict[str, Any]]:
        now = time.time()
        if now - self._last_poll < self._poll_interval:
            return []
        self._last_poll = now

        events: list[dict[str, Any]] = []
        for folder in self._folders:
            folder_events = self._poll_folder(folder)
            events.extend(folder_events)
        return events

    def health(self) -> dict[str, Any]:
        return {
            "status": "running" if self._running else "stopped",
            "folders": self._folders,
            "server": self._server,
            "last_poll": self._last_poll,
        }

    def _poll_folder(self, folder: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        messages = self._fetch_messages(folder)
        seen = self._seen_uids.get(folder, set())
        for msg_id, msg in messages.items():
            if msg_id not in seen:
                event = self._make_event(folder, msg_id, msg)
                events.append(event)
                seen.add(msg_id)
        self._seen_uids[folder] = seen
        return events

    def _fetch_messages(self, folder: str) -> dict[str, dict[str, Any]]:
        messages: dict[str, dict[str, Any]] = {}
        for i in range(3):
            msg_id = f"{folder}_msg_{i}"
            messages[msg_id] = {
                "subject": f"Email {i} in {folder}",
                "from": f"sender{i}@example.com",
                "date": "2024-01-01T00:00:00Z",
                "body_preview": f"This is email {i} from {folder}",
            }
        return messages

    def _make_event(
        self,
        folder: str,
        msg_id: str,
        msg: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "event_type": "email.received",
            "source_kind": "email",
            "source_identifier": f"{self._server}/{folder}",
            "adapter": "email",
            "actor_kind": "user",
            "actor_identifier": msg.get("from", "unknown"),
            "payload_summary": msg.get("subject", "New email"),
            "payload_data": {
                "folder": folder,
                "message_id": msg_id,
                "subject": msg.get("subject", ""),
                "from": msg.get("from", ""),
                "date": msg.get("date", ""),
                "body_preview": msg.get("body_preview", ""),
            },
            "subject_kind": "email_message",
            "subject_identifier": msg_id,
            "tags": ["email", folder.lower()],
        }
