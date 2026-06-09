"""Git polling adapter — watches repos for new commits via reflog."""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from typing import Any

from self.source_adapters.base import BaseSourceAdapter


class GitPollingAdapter(BaseSourceAdapter):
    def __init__(self, repos: list[str], poll_interval: float = 10.0) -> None:
        self._repos = [Path(r).resolve() for r in repos]
        self._poll_interval = poll_interval
        self._last_hashes: dict[str, str] = {}
        self._running = False
        self._last_poll = 0.0

    @property
    def name(self) -> str:
        return "git"

    def start(self) -> None:
        self._running = True
        for repo in self._repos:
            head = self._get_head(repo)
            if head:
                self._last_hashes[str(repo)] = head

    def stop(self) -> None:
        self._running = False

    def poll(self) -> list[dict[str, Any]]:
        now = time.time()
        if now - self._last_poll < self._poll_interval:
            return []
        self._last_poll = now
        events: list[dict[str, Any]] = []
        for repo in self._repos:
            key = str(repo)
            current_head = self._get_head(repo)
            if current_head is None:
                continue
            old_head = self._last_hashes.get(key)
            if old_head is not None and current_head != old_head:
                commits = self._get_commits_between(repo, old_head, current_head)
                for commit_hash, commit_data in commits:
                    events.append(self._make_event(repo, commit_hash, commit_data))
            self._last_hashes[key] = current_head
        return events

    def health(self) -> dict[str, Any]:
        return {
            "status": "running" if self._running else "stopped",
            "repos": [str(r) for r in self._repos],
            "last_poll": self._last_poll,
        }

    def _get_head(self, repo: Path) -> str | None:
        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(repo),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return None

    def _get_commits_between(
        self, repo: Path, old_hash: str, new_hash: str
    ) -> list[tuple[str, dict[str, Any]]]:
        try:
            result = subprocess.run(
                ["git", "log", "--oneline", "--format=%H|%ct|%s", f"{old_hash}..{new_hash}"],
                cwd=str(repo),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode != 0 or not result.stdout.strip():
                return [(new_hash, self._get_commit_details(repo, new_hash))]
            commits = []
            for line in result.stdout.strip().split("\n"):
                parts = line.split("|", 2)
                if len(parts) == 3:
                    commits.append(
                        (
                            parts[0],
                            {
                                "hash": parts[0],
                                "timestamp": parts[1],
                                "message": parts[2],
                            },
                        )
                    )
            return commits
        except (subprocess.SubprocessError, FileNotFoundError):
            return []

    def _get_commit_details(self, repo: Path, commit_hash: str) -> dict[str, Any]:
        try:
            result = subprocess.run(
                ["git", "log", "-1", "--format=%H|%ct|%s|%an|%ae", commit_hash],
                cwd=str(repo),
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split("|", 4)
                if len(parts) == 5:
                    return {
                        "hash": parts[0],
                        "timestamp": parts[1],
                        "message": parts[2],
                        "author": parts[3],
                        "author_email": parts[4],
                    }
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
        return {"hash": commit_hash, "message": "", "timestamp": ""}

    def _make_event(
        self, repo: Path, commit_hash: str, commit_data: dict[str, Any]
    ) -> dict[str, Any]:
        msg = commit_data.get("message", "")
        msg_excerpt = msg[:80] if msg else ""
        return {
            "event_type": "git.commit",
            "source_kind": "git",
            "source_identifier": str(repo),
            "adapter": "git_poller",
            "actor_kind": "user",
            "actor_identifier": commit_data.get("author", "unknown"),
            "payload_summary": f"Commit {commit_hash[:8]}: {msg_excerpt}",
            "payload_data": {
                "hash": commit_hash,
                "message": msg,
                "author": commit_data.get("author", ""),
                "author_email": commit_data.get("author_email", ""),
                "timestamp": commit_data.get("timestamp", ""),
                "repo": str(repo),
            },
            "subject_kind": "commit",
            "subject_identifier": commit_hash,
            "tags": ["git"],
        }
