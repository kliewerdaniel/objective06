"""Tests for summary_scheduler module."""

from __future__ import annotations

from self.summary_scheduler import SummaryScheduler


def test_add_schedule() -> None:
    scheduler = SummaryScheduler()
    schedule = scheduler.add_schedule("daily_summary", "daily", "daily")
    assert schedule["name"] == "daily_summary"
    assert schedule["cadence"] == "daily"
    assert schedule["enabled"] is True


def test_remove_schedule() -> None:
    scheduler = SummaryScheduler()
    scheduler.add_schedule("daily_summary", "daily", "daily")
    result = scheduler.remove_schedule("daily_summary")
    assert result is True
    assert scheduler.get_schedule("daily_summary") is None


def test_enable_disable_schedule() -> None:
    scheduler = SummaryScheduler()
    scheduler.add_schedule("daily_summary", "daily", "daily")
    scheduler.disable_schedule("daily_summary")
    schedule = scheduler.get_schedule("daily_summary")
    assert schedule["enabled"] is False
    scheduler.enable_schedule("daily_summary")
    schedule = scheduler.get_schedule("daily_summary")
    assert schedule["enabled"] is True


def test_list_schedules() -> None:
    scheduler = SummaryScheduler()
    scheduler.add_schedule("daily", "daily", "daily")
    scheduler.add_schedule("weekly", "weekly", "weekly")
    schedules = scheduler.list_schedules()
    assert len(schedules) == 2


def test_get_due_schedules() -> None:
    scheduler = SummaryScheduler()
    scheduler.add_schedule("daily", "daily", "daily")
    due = scheduler.get_due_schedules()
    assert len(due) == 1
    assert due[0]["name"] == "daily"


def test_mark_run() -> None:
    scheduler = SummaryScheduler()
    scheduler.add_schedule("daily", "daily", "daily")
    scheduler.mark_run("daily")
    schedule = scheduler.get_schedule("daily")
    assert schedule["last_run"] is not None
