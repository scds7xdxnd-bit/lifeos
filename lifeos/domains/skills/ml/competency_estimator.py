"""Placeholder competency estimator."""

from __future__ import annotations

from typing import Dict


def estimate_level(metrics: Dict[str, float]) -> str:
    score = sum(metrics.values())
    if score > 100:
        return "expert"
    if score > 50:
        return "intermediate"
    return "beginner"
