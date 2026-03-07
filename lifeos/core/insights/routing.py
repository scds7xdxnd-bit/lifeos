"""Confidence routing enforcement (Phase 3a)."""

from __future__ import annotations

from typing import Optional, Tuple

from lifeos.core.insights.contracts import get_insight_contract


def resolve_confidence_band(
    insight_type: str,
    event_type: str,
    severity: Optional[str] = None,
    context: Optional[dict] = None,
) -> str:
    """Resolve the confidence band for an insight deterministically."""
    contract = get_insight_contract(insight_type)
    if not contract:
        return "informational"

    bands = list(contract.confidence_bands.keys())
    context = context or {}

    is_inferred = event_type.endswith(".inferred") or (str(context.get("status") or "").lower() == "inferred")
    if is_inferred and "needs_review" in bands:
        return "needs_review"

    if severity and severity.lower() in {"warning", "high"} and "suggested" in bands:
        return "suggested"

    if "informational" in bands:
        return "informational"

    return bands[0] if bands else "informational"


def resolve_routing(confidence_band: str) -> str:
    """Map confidence band to routing behavior."""
    if confidence_band == "needs_review":
        return "review_only"
    if confidence_band == "suggested":
        return "suggestion"
    if confidence_band == "confirmed":
        return "highlight"
    return "display"


def enforce_confidence_routing(
    insight_type: str,
    event_type: str,
    severity: Optional[str] = None,
    context: Optional[dict] = None,
) -> Tuple[str, str]:
    """Return (confidence_band, routing) for an insight."""
    band = resolve_confidence_band(insight_type, event_type, severity=severity, context=context)
    routing = resolve_routing(band)
    return band, routing


__all__ = ["resolve_confidence_band", "resolve_routing", "enforce_confidence_routing"]
