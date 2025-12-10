"""Placeholder health risk estimator."""

from __future__ import annotations

from typing import Dict


def estimate_risk(biometrics: Dict[str, float]) -> str:
    score = sum(biometrics.values())
    if score > 500:
        return "high"
    if score > 200:
        return "medium"
    return "low"
