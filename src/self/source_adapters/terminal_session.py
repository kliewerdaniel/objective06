"""Terminal Session adapter — monitors terminal sessions for activity."""

from __future__ import annotations

import time
from typing import Any

from self.source_adapters.base import BaseSourceAdapter


class TerminalSessionAdapter(BaseSourceAdapter):
    def __init__(
        self,
        poll_interval: float = 10.0,
        max_history: int = 100,
    ) -> None:
        self._poll_interval = poll_interval
        self._max_history = max_history
        self._running = False
        self._last_poll = 0.0
        self._seen_commands: set[str] = set()
        self._command_history: list[dict[str, Any]] = []

    @property
    def name(self) -> str:
        return "terminal"

    def start(self) -> None:
        self._running = True
        self._seen_commands = set()
        self._command_history = []

    def stop(self) -> None:
        self._running = False

    def poll(self) -> list[dict[str, Any]]:
        now = time.time()
        if now - self._last_poll < self._poll_interval:
            return []
        self._last_poll = now

        events: list[dict[str, Any]] = []
        new_commands = self._fetch_new_commands()
        for cmd_id, cmd in new_commands.items():
            if cmd_id not in self._seen_commands:
                event = self._make_event(cmd_id, cmd)
                events.append(event)
                self._seen_commands.add(cmd_id)
                self._command_history.append(cmd)
                if len(self._command_history) > self._max_history:
                    self._command_history.pop(0)
        return events

    def health(self) -> dict[str, Any]:
        return {
            "status": "running" if self._running else "stopped",
            "last_poll": self._last_poll,
            "commands_tracked": len(self._command_history),
        }

    def _fetch_new_commands(self) -> dict[str, dict[str, Any]]:
        commands: dict[str, dict[str, Any]] = {}
        for i in range(2):
            cmd_id = f"cmd_{int(time.time())}_{i}"
            commands[cmd_id] = {
                "command": f"echo 'command {i}'",
                "working_directory": "/home/user",
                "exit_code": 0,
                "timestamp": "2024-01-01T00:00:00Z",
                "duration_ms": 100 + i * 50,
            }
        return commands

    def _make_event(
        self,
        cmd_id: str,
        cmd: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "event_type": "terminal.command",
            "source_kind": "terminal",
            "source_identifier": "session",
            "adapter": "terminal_session",
            "actor_kind": "user",
            "actor_identifier": "terminal.user",
            "payload_summary": cmd.get("command", "Terminal command"),
            "payload_data": {
                "command_id": cmd_id,
                "command": cmd.get("command", ""),
                "working_directory": cmd.get("working_directory", ""),
                "exit_code": cmd.get("exit_code", 0),
                "timestamp": cmd.get("timestamp", ""),
                "duration_ms": cmd.get("duration_ms", 0),
            },
            "subject_kind": "command",
            "subject_identifier": cmd_id,
            "tags": ["terminal", "command"],
        }
