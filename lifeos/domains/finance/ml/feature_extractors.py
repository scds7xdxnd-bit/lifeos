"""Finance ML feature extraction."""

from __future__ import annotations

from typing import Dict


def extract_transaction_features(payload: Dict) -> Dict[str, float]:
    features: Dict[str, float] = {}
    amount = payload.get("amount")
    if amount is not None:
        try:
            features["amount"] = float(amount)
        except Exception:
            pass
    if payload.get("counterparty"):
        features["has_counterparty"] = 1.0
    return features

