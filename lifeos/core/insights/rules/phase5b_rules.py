"""Phase 5b deterministic cross-domain insight rules."""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from typing import Dict, List

from flask import current_app

from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.feature_service import (
    compute_features_for_user,
    extract_event_features,
    resolve_event_date,
    store_features_daily,
)
from lifeos.core.insights.models import InsightRecord
from lifeos.core.insights.registry import InsightTypeDefinition, get_enabled_insight_definitions


def apply_rules(event: EventRecord) -> List[dict]:
    user_id = event.user_id
    if not user_id:
        return []
    if not _phase5b_enabled():
        return []

    definitions = list(get_enabled_insight_definitions(_safe_config()))
    if not definitions:
        return []

    end_date = resolve_event_date(event)
    if not end_date:
        return []

    max_window = max(definition.window_days for definition in definitions)
    window_start = end_date - timedelta(days=max_window - 1)

    features_by_date = compute_features_for_user(user_id, window_start, end_date)
    if event.id is None:
        _apply_event_features(features_by_date, end_date, extract_event_features(event))
    store_features_daily(user_id, features_by_date)

    insights: List[dict] = []
    for definition in definitions:
        snapshot = _aggregate_window_features(
            features_by_date,
            definition.required_features,
            end_date,
            definition.window_days,
        )
        if not definition.trigger(snapshot):
            continue
        if _is_duplicate_insight(user_id, definition, end_date):
            continue
        context = definition.context_builder(snapshot)
        context["window_days"] = definition.window_days
        context["window_end"] = end_date.isoformat()
        context["feature_snapshot"] = snapshot
        context["confidence"] = definition.confidence(snapshot)

        summary = _safe_format(definition.summary_template, context)
        detail = _safe_format(definition.detail_template, context)
        context["detail"] = detail

        insights.append(
            {
                "type": definition.insight_type,
                "message": summary,
                "severity": definition.severity,
                "priority": definition.priority(snapshot),
                "delivery_policy": definition.delivery_policy,
                "context": context,
            }
        )
    return insights


def _aggregate_window_features(
    features_by_date: Dict[date, Dict[str, float]],
    feature_keys: tuple[str, ...],
    end_date: date,
    window_days: int,
) -> Dict[str, float]:
    start_date = end_date - timedelta(days=window_days - 1)
    totals = {key: 0.0 for key in feature_keys}
    for feature_date, features in features_by_date.items():
        if feature_date < start_date or feature_date > end_date:
            continue
        for key in feature_keys:
            totals[key] = totals.get(key, 0.0) + float(features.get(key, 0.0))
    return totals


def _apply_event_features(
    features_by_date: Dict[date, Dict[str, float]],
    event_date: date,
    deltas: Dict[str, float],
) -> None:
    if not deltas:
        return
    bucket = features_by_date.setdefault(event_date, {})
    for key, value in deltas.items():
        bucket[key] = bucket.get(key, 0.0) + value


def _safe_format(template: str, context: Dict[str, object]) -> str:
    try:
        return template.format(**context)
    except KeyError:
        return template


def _phase5b_enabled() -> bool:
    try:
        return current_app.config.get("ENABLE_PHASE5B_INSIGHTS", True)
    except RuntimeError:
        return os.environ.get("ENABLE_PHASE5B_INSIGHTS", "true").lower() in ("1", "true", "yes")


def _safe_config():
    try:
        return current_app.config
    except RuntimeError:
        return None


def _is_duplicate_insight(user_id: int, definition: InsightTypeDefinition, window_end: date) -> bool:
    window_start = window_end - timedelta(days=definition.window_days - 1)
    start_dt = datetime.combine(window_start, datetime.min.time())
    records = (
        InsightRecord.query.filter_by(user_id=user_id, kind=definition.insight_type)
        .filter(InsightRecord.created_at >= start_dt)
        .all()
    )
    for rec in records:
        data = rec.data or {}
        if data.get("window_end") == window_end.isoformat() and data.get("window_days") == definition.window_days:
            return True
    return False


__all__ = ["apply_rules"]
