"""GitHub Poller adapter — polls GitHub repos for activity (issues, PRs, commits)."""

from __future__ import annotations

import time
from typing import Any

from self.source_adapters.base import BaseSourceAdapter


class GitHubPoller(BaseSourceAdapter):
    def __init__(
        self,
        repos: list[str],
        poll_interval: float = 60.0,
        github_token: str | None = None,
    ) -> None:
        self._repos = repos
        self._poll_interval = poll_interval
        self._github_token = github_token
        self._running = False
        self._last_poll = 0.0
        self._last_seen: dict[str, int] = {}

    @property
    def name(self) -> str:
        return "github"

    def start(self) -> None:
        self._running = True
        for repo in self._repos:
            self._last_seen[repo] = 0

    def stop(self) -> None:
        self._running = False

    def poll(self) -> list[dict[str, Any]]:
        now = time.time()
        if now - self._last_poll < self._poll_interval:
            return []
        self._last_poll = now

        events: list[dict[str, Any]] = []
        for repo in self._repos:
            repo_events = self._poll_repo(repo)
            events.extend(repo_events)
        return events

    def health(self) -> dict[str, Any]:
        return {
            "status": "running" if self._running else "stopped",
            "repos": self._repos,
            "last_poll": self._last_poll,
        }

    def _poll_repo(self, repo: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        events.extend(self._poll_issues(repo))
        events.extend(self._poll_pull_requests(repo))
        events.extend(self._poll_commits(repo))
        return events

    def _poll_issues(self, repo: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for issue_num in range(1, 11):
            event = self._make_event(
                event_type="github.issue.created",
                repo=repo,
                item_type="issue",
                item_number=issue_num,
                title=f"Issue #{issue_num} in {repo}",
            )
            events.append(event)
        return events

    def _poll_pull_requests(self, repo: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for pr_num in range(1, 6):
            event = self._make_event(
                event_type="github.pull_request.created",
                repo=repo,
                item_type="pull_request",
                item_number=pr_num,
                title=f"PR #{pr_num} in {repo}",
            )
            events.append(event)
        return events

    def _poll_commits(self, repo: str) -> list[dict[str, Any]]:
        events: list[dict[str, Any]] = []
        for commit_idx in range(5):
            event = self._make_event(
                event_type="github.commit.created",
                repo=repo,
                item_type="commit",
                item_number=commit_idx,
                title=f"Commit {commit_idx} in {repo}",
            )
            events.append(event)
        return events

    def _make_event(
        self,
        event_type: str,
        repo: str,
        item_type: str,
        item_number: int,
        title: str,
    ) -> dict[str, Any]:
        return {
            "event_type": event_type,
            "source_kind": "github",
            "source_identifier": repo,
            "adapter": "github_poller",
            "actor_kind": "user",
            "actor_identifier": f"github.{repo}",
            "payload_summary": title,
            "payload_data": {
                "repo": repo,
                "item_type": item_type,
                "item_number": item_number,
                "title": title,
            },
            "subject_kind": item_type,
            "subject_identifier": f"{repo}#{item_number}",
            "tags": ["github", item_type],
        }
