"""Stub habit prediction model."""

from __future__ import annotations

from typing import List


def predict_next_habits(history: List[str]) -> List[str]:
    """Return placeholder predicted habits."""
    return list(reversed(history))[:3]

