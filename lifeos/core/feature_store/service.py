"""Feature store service helpers (Phase 5c readiness)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Iterable, Optional, Sequence

from lifeos.core.feature_store.models import FeatureStoreEntry
from lifeos.extensions import db

ALLOWED_DTYPES = {"float", "int", "bool", "str", "json"}
ALLOWED_LIFECYCLE_STATES = {"proposed", "shadow", "active_ready", "deprecated", "removed"}
ALLOWED_BACKFILL_POLICIES = {"allowed", "disallowed", "limited"}


@dataclass(frozen=True)
class FeatureWrite:
    user_id: int
    entity_type: str
    entity_id: str
    feature_name: str
    value: object
    dtype: str
    window: str
    as_of_ts: datetime
    computed_at: datetime
    feature_version: str
    source_event_types: Sequence[str]
    provenance_ref: dict
    backfill_policy: str
    lifecycle_state: str
    upsert_safe: bool = False


def write_feature(feature: FeatureWrite) -> FeatureStoreEntry:
    _validate_feature(feature)
    existing = FeatureStoreEntry.query.filter_by(
        user_id=feature.user_id,
        entity_type=feature.entity_type,
        entity_id=feature.entity_id,
        feature_name=feature.feature_name,
        as_of_ts=feature.as_of_ts,
        feature_version=feature.feature_version,
    ).first()
    if existing and not feature.upsert_safe:
        return existing
    if existing:
        existing.value = feature.value
        existing.dtype = feature.dtype
        existing.window = feature.window
        existing.computed_at = feature.computed_at
        existing.source_event_types = list(feature.source_event_types or [])
        existing.provenance_ref = feature.provenance_ref or {}
        existing.backfill_policy = feature.backfill_policy
        existing.lifecycle_state = feature.lifecycle_state
        db.session.add(existing)
        db.session.commit()
        return existing

    entry = FeatureStoreEntry(
        user_id=feature.user_id,
        entity_type=feature.entity_type,
        entity_id=feature.entity_id,
        feature_name=feature.feature_name,
        value=feature.value,
        dtype=feature.dtype,
        window=feature.window,
        computed_at=feature.computed_at,
        as_of_ts=feature.as_of_ts,
        feature_version=feature.feature_version,
        source_event_types=list(feature.source_event_types or []),
        provenance_ref=feature.provenance_ref or {},
        backfill_policy=feature.backfill_policy,
        lifecycle_state=feature.lifecycle_state,
    )
    db.session.add(entry)
    db.session.commit()
    return entry


def read_features(
    *,
    user_id: int,
    entity_type: str,
    entity_id: str,
    feature_name: str | None = None,
    start_ts: Optional[datetime] = None,
    end_ts: Optional[datetime] = None,
) -> list[FeatureStoreEntry]:
    query = FeatureStoreEntry.query.filter_by(user_id=user_id, entity_type=entity_type, entity_id=entity_id)
    if feature_name:
        query = query.filter(FeatureStoreEntry.feature_name == feature_name)
    if start_ts is not None:
        query = query.filter(FeatureStoreEntry.as_of_ts >= start_ts)
    if end_ts is not None:
        query = query.filter(FeatureStoreEntry.as_of_ts <= end_ts)
    return query.order_by(FeatureStoreEntry.as_of_ts.desc()).all()


def latest_feature(
    *,
    user_id: int,
    entity_type: str,
    entity_id: str,
    feature_name: str,
) -> FeatureStoreEntry | None:
    return (
        FeatureStoreEntry.query.filter_by(
            user_id=user_id,
            entity_type=entity_type,
            entity_id=entity_id,
            feature_name=feature_name,
        )
        .order_by(FeatureStoreEntry.as_of_ts.desc())
        .first()
    )


def _validate_feature(feature: FeatureWrite) -> None:
    if not feature.user_id:
        raise ValueError("invalid_user")
    if not feature.entity_type or not feature.entity_id:
        raise ValueError("invalid_entity")
    if not feature.feature_name:
        raise ValueError("invalid_feature_name")
    if feature.dtype not in ALLOWED_DTYPES:
        raise ValueError("invalid_dtype")
    if feature.lifecycle_state not in ALLOWED_LIFECYCLE_STATES:
        raise ValueError("invalid_lifecycle_state")
    if feature.backfill_policy not in ALLOWED_BACKFILL_POLICIES:
        raise ValueError("invalid_backfill_policy")
    if feature.as_of_ts > feature.computed_at:
        raise ValueError("time_leakage")
    _coerce_value(feature.dtype, feature.value)


def _coerce_value(dtype: str, value: object) -> object:
    if dtype == "float":
        return float(value)
    if dtype == "int":
        return int(value)
    if dtype == "bool":
        return bool(value)
    if dtype == "str":
        return str(value)
    if dtype == "json":
        return value
    raise ValueError("invalid_dtype")


def build_feature_write(
    *,
    user_id: int,
    entity_type: str,
    entity_id: str,
    feature_name: str,
    value: object,
    dtype: str,
    window: str,
    as_of_ts: datetime,
    computed_at: Optional[datetime] = None,
    feature_version: str = "1.0.0",
    source_event_types: Optional[Iterable[str]] = None,
    provenance_ref: Optional[dict] = None,
    backfill_policy: str = "allowed",
    lifecycle_state: str = "shadow",
    upsert_safe: bool = False,
) -> FeatureWrite:
    computed_at = computed_at or datetime.utcnow()
    coerced_value = _coerce_value(dtype, value)
    return FeatureWrite(
        user_id=user_id,
        entity_type=entity_type,
        entity_id=str(entity_id),
        feature_name=feature_name,
        value=coerced_value,
        dtype=dtype,
        window=window,
        as_of_ts=as_of_ts,
        computed_at=computed_at,
        feature_version=feature_version,
        source_event_types=list(source_event_types or []),
        provenance_ref=provenance_ref or {},
        backfill_policy=backfill_policy,
        lifecycle_state=lifecycle_state,
        upsert_safe=upsert_safe,
    )


__all__ = [
    "FeatureStoreEntry",
    "FeatureWrite",
    "build_feature_write",
    "latest_feature",
    "read_features",
    "write_feature",
]
