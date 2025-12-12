"""Utilities to surface inference feedback (FP/FN) for retraining."""

from __future__ import annotations

from typing import Dict, List, Optional

from lifeos.platform.outbox.models import OutboxMessage


def fetch_flagged_inference_events(
    domain: Optional[str] = None,
    model_version: Optional[str] = None,
    limit: int = 200,
) -> List[Dict]:
    """
    Return recent inference events marked as false positive/negative for retraining.

    Filters on event_type suffix `.inferred` and only returns payloads with
    `is_false_positive` or `is_false_negative` set.
    """
    query = OutboxMessage.query.filter(OutboxMessage.event_type.like("%.inferred"))
    if domain:
        query = query.filter(OutboxMessage.event_type.like(f"{domain}.%"))
    query = query.order_by(OutboxMessage.created_at.desc()).limit(limit)
    flagged: List[Dict] = []
    for msg in query.all():
        payload = msg.payload or {}
        if not payload:
            continue
        is_fp = bool(payload.get("is_false_positive"))
        is_fn = bool(payload.get("is_false_negative"))
        if not (is_fp or is_fn):
            continue
        if model_version and payload.get("model_version") != model_version:
            continue
        flagged.append(
            {
                "event_type": msg.event_type,
                "model_version": payload.get("model_version"),
                "is_false_positive": is_fp,
                "is_false_negative": is_fn,
                "payload_version": payload.get("payload_version"),
                "payload": payload,
                "created_at": msg.created_at.isoformat(),
            }
        )
    return flagged


__all__ = ["fetch_flagged_inference_events"]
