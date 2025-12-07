"""Feature extraction from events and domain data."""

from __future__ import annotations

from typing import Dict

from lifeos.core.events.event_models import EventRecord


def extract_event_features(event: EventRecord) -> Dict[str, float]:
    """Return simple numeric features for ranking/ML."""
    payload = event.payload or {}
    features: Dict[str, float] = {}
    if "amount" in payload:
        try:
            features["amount"] = float(payload["amount"])
        except Exception:
            pass
    if "streak" in payload:
        try:
            features["streak"] = float(payload["streak"])
        except Exception:
            pass
    return features

