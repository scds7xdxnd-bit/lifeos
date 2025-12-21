"""Placeholder project estimator."""

from __future__ import annotations


def estimate_completion(tasks_completed: int, tasks_total: int) -> float:
    if tasks_total == 0:
        return 0.0
    return round((tasks_completed / tasks_total) * 100, 2)
