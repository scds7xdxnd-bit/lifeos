from __future__ import annotations

import sys
from datetime import date, datetime, timedelta

import pytest

from lifeos.core.events.event_models import EventRecord
from lifeos.core.feature_store.models import FeatureStoreEntry
from lifeos.core.insights.models import InsightRecord
from lifeos.core.users.models import User
from lifeos.extensions import db
from scripts.ops import phase5c_feature_runner as feature_runner
from scripts.ops import phase5c_personalization_noop_check as noop_check


pytestmark = pytest.mark.integration


def _default_user() -> User:
    user = User.query.filter_by(email="test@example.com").first()
    assert user is not None
    return user


def test_feature_runner_canonical_and_aggregation_helpers():
    class DummyEvent:
        def __init__(self, event_type: str, payload: dict, event_id: int):
            self.event_type = event_type
            self.payload = payload
            self.id = event_id

    assert feature_runner._canonical_event_type(DummyEvent("insight_viewed", {}, 1)) == "insight_viewed"
    assert (
        feature_runner._canonical_event_type(DummyEvent("insights.action", {"action": "dismiss"}, 2))
        == "insight_dismissed"
    )
    assert feature_runner._canonical_event_type(DummyEvent("unknown", {}, 3)) is None

    events = [
        DummyEvent("insight_viewed", {}, 11),
        DummyEvent("insights.action", {"action": "dismissed"}, 12),
        DummyEvent("insights.action", {"action": "dismissed"}, 13),
    ]
    counts = feature_runner._aggregate_events(events)
    assert counts["insight_viewed"]["count"] == 1
    assert counts["insight_dismissed"]["count"] == 2
    assert sorted(counts["insight_dismissed"]["event_ids"]) == [12, 13]

    provenance = feature_runner._provenance(counts["insight_dismissed"])
    assert provenance["event_count"] == 2
    assert "event_ids_hash" in provenance

    start = date(2026, 1, 1)
    end = date(2026, 1, 3)
    assert list(feature_runner._date_range(start, end)) == [
        date(2026, 1, 1),
        date(2026, 1, 2),
        date(2026, 1, 3),
    ]

    start_ts, end_ts = feature_runner._window_bounds(date(2026, 2, 10), 7)
    assert start_ts.date() == date(2026, 2, 4)
    assert end_ts.date() == date(2026, 2, 10)


def test_feature_runner_main_end_to_end(app, monkeypatch, capsys):
    user = _default_user()
    created_at = datetime.combine(date.today(), datetime.min.time()) + timedelta(hours=10)
    db.session.add(
        EventRecord(
            user_id=user.id,
            event_type="insights.action",
            payload={"action": "dismiss"},
            created_at=created_at,
        )
    )
    db.session.add(
        EventRecord(
            user_id=user.id,
            event_type="insight_feedback_positive",
            payload={"source": "test"},
            created_at=created_at + timedelta(minutes=1),
        )
    )
    db.session.commit()

    monkeypatch.setattr(feature_runner, "create_app", lambda: app)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "phase5c_feature_runner.py",
            "--mode",
            "both",
            "--window-days",
            "1",
            "--as-of",
            date.today().isoformat(),
            "--user-id",
            str(user.id),
            "--verify",
        ],
    )

    feature_runner.main()
    output = capsys.readouterr().out
    assert "phase5c: verification mismatches=" in output
    assert "phase5c: users=1" in output

    stored = FeatureStoreEntry.query.filter_by(user_id=user.id).all()
    names = {row.feature_name for row in stored}
    assert "insight.dismissed.count" in names
    assert "insight.feedback_positive.count" in names


def test_personalization_noop_check_reports_pass(app, monkeypatch, capsys):
    user = _default_user()
    now = datetime.utcnow()
    db.session.add(
        InsightRecord(
            user_id=user.id,
            event_type="insight.test",
            kind="phase5c.test",
            message="A",
            priority=60,
            confidence_band="informational",
            created_at=now,
        )
    )
    db.session.add(
        InsightRecord(
            user_id=user.id,
            event_type="insight.test",
            kind="phase5c.test",
            message="B",
            priority=55,
            confidence_band="informational",
            created_at=now - timedelta(minutes=1),
        )
    )
    db.session.commit()

    monkeypatch.setattr(noop_check, "create_app", lambda: app)
    monkeypatch.setattr(
        sys,
        "argv",
        ["phase5c_personalization_noop_check.py", "--user-id", str(user.id), "--limit", "10"],
    )
    noop_check.main()
    output = capsys.readouterr().out
    assert "phase5c: personalization no-op verified (PASS)" in output


def test_personalization_noop_check_handles_empty_state(app, monkeypatch, capsys):
    monkeypatch.setattr(noop_check, "create_app", lambda: app)
    monkeypatch.setattr(sys, "argv", ["phase5c_personalization_noop_check.py", "--limit", "5"])
    noop_check.main()
    output = capsys.readouterr().out
    assert "phase5c: no insights found for check" in output
