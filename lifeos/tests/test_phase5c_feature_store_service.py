from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timedelta

import pytest

from lifeos.core.feature_store import service as feature_store_service
from lifeos.core.feature_store.models import FeatureStoreEntry
from lifeos.core.feature_store.service import (
    FeatureWrite,
    build_feature_write,
    latest_feature,
    read_features,
    write_feature,
)
from lifeos.core.users.models import User


def _default_user_id() -> int:
    user = User.query.filter_by(email="test@example.com").first()
    assert user is not None
    return int(user.id)


def test_build_feature_write_coerces_types(app):
    now = datetime.utcnow()
    as_of = now - timedelta(minutes=5)
    user_id = _default_user_id()

    as_float = build_feature_write(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.dismissed.count",
        value="3.5",
        dtype="float",
        window="7d",
        as_of_ts=as_of,
        computed_at=now,
    )
    assert as_float.value == pytest.approx(3.5)

    as_int = build_feature_write(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.viewed.count",
        value="7",
        dtype="int",
        window="7d",
        as_of_ts=as_of,
        computed_at=now,
    )
    assert as_int.value == 7

    as_bool = build_feature_write(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.enabled",
        value=1,
        dtype="bool",
        window="1d",
        as_of_ts=as_of,
        computed_at=now,
    )
    assert as_bool.value is True

    as_str = build_feature_write(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.segment",
        value=100,
        dtype="str",
        window="1d",
        as_of_ts=as_of,
        computed_at=now,
    )
    assert as_str.value == "100"

    as_json = build_feature_write(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.metadata",
        value={"source": "phase5c", "count": 2},
        dtype="json",
        window="1d",
        as_of_ts=as_of,
        computed_at=now,
    )
    assert as_json.value == {"source": "phase5c", "count": 2}


def test_write_read_latest_and_upsert_behavior(app):
    user_id = _default_user_id()
    now = datetime.utcnow()
    as_of = now - timedelta(hours=1)

    first = build_feature_write(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.feedback_positive.count",
        value=2,
        dtype="int",
        window="7d",
        as_of_ts=as_of,
        computed_at=now,
        source_event_types=["insight_feedback_positive"],
    )
    first_entry = write_feature(first)
    assert first_entry.id is not None
    assert int(first_entry.value) == 2

    duplicate = build_feature_write(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.feedback_positive.count",
        value=9,
        dtype="int",
        window="7d",
        as_of_ts=as_of,
        computed_at=now,
    )
    duplicate_entry = write_feature(duplicate)
    assert duplicate_entry.id == first_entry.id
    assert int(duplicate_entry.value) == 2

    updated = replace(duplicate, value=11, upsert_safe=True)
    updated_entry = write_feature(updated)
    assert updated_entry.id == first_entry.id
    assert int(updated_entry.value) == 11

    newer = build_feature_write(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.feedback_positive.count",
        value=15,
        dtype="int",
        window="7d",
        as_of_ts=now,
        computed_at=now,
    )
    write_feature(newer)

    latest = latest_feature(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.feedback_positive.count",
    )
    assert latest is not None
    assert latest.as_of_ts == now
    assert int(latest.value) == 15

    windowed = read_features(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.feedback_positive.count",
        start_ts=as_of - timedelta(minutes=1),
        end_ts=now + timedelta(minutes=1),
    )
    assert [int(item.value) for item in windowed] == [15, 11]


@pytest.mark.parametrize(
    ("feature", "message"),
    [
        (
            FeatureWrite(
                user_id=0,
                entity_type="user",
                entity_id="1",
                feature_name="x",
                value=1,
                dtype="int",
                window="1d",
                as_of_ts=datetime.utcnow() - timedelta(minutes=2),
                computed_at=datetime.utcnow(),
                feature_version="1.0.0",
                source_event_types=[],
                provenance_ref={},
                backfill_policy="allowed",
                lifecycle_state="shadow",
            ),
            "invalid_user",
        ),
        (
            FeatureWrite(
                user_id=1,
                entity_type="",
                entity_id="1",
                feature_name="x",
                value=1,
                dtype="int",
                window="1d",
                as_of_ts=datetime.utcnow() - timedelta(minutes=2),
                computed_at=datetime.utcnow(),
                feature_version="1.0.0",
                source_event_types=[],
                provenance_ref={},
                backfill_policy="allowed",
                lifecycle_state="shadow",
            ),
            "invalid_entity",
        ),
        (
            FeatureWrite(
                user_id=1,
                entity_type="user",
                entity_id="1",
                feature_name="",
                value=1,
                dtype="int",
                window="1d",
                as_of_ts=datetime.utcnow() - timedelta(minutes=2),
                computed_at=datetime.utcnow(),
                feature_version="1.0.0",
                source_event_types=[],
                provenance_ref={},
                backfill_policy="allowed",
                lifecycle_state="shadow",
            ),
            "invalid_feature_name",
        ),
        (
            FeatureWrite(
                user_id=1,
                entity_type="user",
                entity_id="1",
                feature_name="x",
                value=1,
                dtype="int",
                window="1d",
                as_of_ts=datetime.utcnow() + timedelta(minutes=2),
                computed_at=datetime.utcnow(),
                feature_version="1.0.0",
                source_event_types=[],
                provenance_ref={},
                backfill_policy="allowed",
                lifecycle_state="shadow",
            ),
            "time_leakage",
        ),
        (
            FeatureWrite(
                user_id=1,
                entity_type="user",
                entity_id="1",
                feature_name="x",
                value=1,
                dtype="int",
                window="1d",
                as_of_ts=datetime.utcnow() - timedelta(minutes=2),
                computed_at=datetime.utcnow(),
                feature_version="1.0.0",
                source_event_types=[],
                provenance_ref={},
                backfill_policy="invalid",
                lifecycle_state="shadow",
            ),
            "invalid_backfill_policy",
        ),
        (
            FeatureWrite(
                user_id=1,
                entity_type="user",
                entity_id="1",
                feature_name="x",
                value=1,
                dtype="int",
                window="1d",
                as_of_ts=datetime.utcnow() - timedelta(minutes=2),
                computed_at=datetime.utcnow(),
                feature_version="1.0.0",
                source_event_types=[],
                provenance_ref={},
                backfill_policy="allowed",
                lifecycle_state="bad_state",
            ),
            "invalid_lifecycle_state",
        ),
        (
            FeatureWrite(
                user_id=1,
                entity_type="user",
                entity_id="1",
                feature_name="x",
                value=1,
                dtype="not_supported",
                window="1d",
                as_of_ts=datetime.utcnow() - timedelta(minutes=2),
                computed_at=datetime.utcnow(),
                feature_version="1.0.0",
                source_event_types=[],
                provenance_ref={},
                backfill_policy="allowed",
                lifecycle_state="shadow",
            ),
            "invalid_dtype",
        ),
    ],
)
def test_write_feature_validation_errors(feature: FeatureWrite, message: str):
    with pytest.raises(ValueError, match=message):
        write_feature(feature)


def test_build_feature_write_rejects_invalid_dtype(app):
    user_id = _default_user_id()
    with pytest.raises(ValueError, match="invalid_dtype"):
        build_feature_write(
            user_id=user_id,
            entity_type="user",
            entity_id=str(user_id),
            feature_name="insight.invalid",
            value=1,
            dtype="unknown",
            window="1d",
            as_of_ts=datetime.utcnow(),
        )


def test_feature_store_module_exports():
    assert "FeatureStoreEntry" in feature_store_service.__all__
    assert "write_feature" in feature_store_service.__all__
    assert FeatureStoreEntry.__name__ == "FeatureStoreEntry"


def test_latest_feature_returns_none_when_missing(app):
    user_id = _default_user_id()
    missing = latest_feature(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        feature_name="insight.never.created",
    )
    assert missing is None


def test_read_features_filters_by_time_without_feature_name(app):
    user_id = _default_user_id()
    now = datetime.utcnow()
    older = now - timedelta(days=2)
    mid = now - timedelta(days=1)

    write_feature(
        build_feature_write(
            user_id=user_id,
            entity_type="user",
            entity_id=str(user_id),
            feature_name="insight.alpha",
            value=1,
            dtype="int",
            window="7d",
            as_of_ts=older,
            computed_at=now,
        )
    )
    write_feature(
        build_feature_write(
            user_id=user_id,
            entity_type="user",
            entity_id=str(user_id),
            feature_name="insight.beta",
            value=2,
            dtype="int",
            window="7d",
            as_of_ts=mid,
            computed_at=now,
        )
    )
    write_feature(
        build_feature_write(
            user_id=user_id,
            entity_type="user",
            entity_id=str(user_id),
            feature_name="insight.gamma",
            value=3,
            dtype="int",
            window="7d",
            as_of_ts=now,
            computed_at=now,
        )
    )

    rows = read_features(
        user_id=user_id,
        entity_type="user",
        entity_id=str(user_id),
        start_ts=mid,
        end_ts=now,
    )
    assert [row.feature_name for row in rows] == ["insight.gamma", "insight.beta"]


def test_write_feature_upsert_updates_metadata_fields(app):
    user_id = _default_user_id()
    now = datetime.utcnow()
    as_of = now - timedelta(minutes=30)

    first = write_feature(
        build_feature_write(
            user_id=user_id,
            entity_type="user",
            entity_id=str(user_id),
            feature_name="insight.metadata.check",
            value=1.5,
            dtype="float",
            window="30d",
            as_of_ts=as_of,
            computed_at=now,
            source_event_types=["event.a"],
            provenance_ref={"step": 1},
            backfill_policy="allowed",
            lifecycle_state="shadow",
        )
    )

    updated = write_feature(
        build_feature_write(
            user_id=user_id,
            entity_type="user",
            entity_id=str(user_id),
            feature_name="insight.metadata.check",
            value=3.25,
            dtype="float",
            window="30d",
            as_of_ts=as_of,
            computed_at=now + timedelta(minutes=1),
            source_event_types=["event.b", "event.c"],
            provenance_ref={"step": 2, "source": "qa"},
            backfill_policy="limited",
            lifecycle_state="active_ready",
            upsert_safe=True,
        )
    )

    assert updated.id == first.id
    assert float(updated.value) == pytest.approx(3.25)
    assert updated.source_event_types == ["event.b", "event.c"]
    assert updated.provenance_ref == {"step": 2, "source": "qa"}
    assert updated.backfill_policy == "limited"
    assert updated.lifecycle_state == "active_ready"
