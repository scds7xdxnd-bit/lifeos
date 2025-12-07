"""Placeholder closeness estimator."""

from __future__ import annotations

from typing import List


def estimate_closeness(interactions: List[str]) -> int:
    """Return a simple closeness score."""
    return min(len(interactions), 10)

