"""Phase 9 timeline intelligence integration tests."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InquiryRequest
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def _enable_phase9(app) -> None:
    app.config["ENABLE_PHASE9_TIMELINE_INTELLIGENCE"] = True
    app.config["PHASE9_ENABLED_TIMELINE_PROFILES"] = None


def _user_tokens(email: str, *, timezone: str = "UTC"):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 9 Timeline",
            timezone=timezone,
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase9-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_phase9_finance_timeline_metadata_is_deterministic_and_replay_safe(app, client):
    _enable_phase9(app)
    with app.app_context():
        user, tokens = _user_tokens("phase9-finance@example.com", timezone="Asia/Seoul")
        db.session.add_all(
            [
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 40, "occurred_at": "2026-02-01T09:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 2, 1, 9, 0, 0),
                ),
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 50, "occurred_at": "2026-02-08T09:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 2, 8, 9, 0, 0),
                ),
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 60, "occurred_at": "2026-02-15T09:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 2, 15, 9, 0, 0),
                ),
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 80, "occurred_at": "2026-02-22T09:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 2, 22, 9, 0, 0),
                ),
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 999, "occurred_at": "2026-02-25T09:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 1, 0, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase9-finance"))
    payload = {
        "question": "How has finance changed over time?",
        "domain": "finance",
        "cross_domain": False,
        "timeframe_start": "2026-02-22",
        "timeframe_end": "2026-02-28",
        "as_of_ts": "2026-02-28T23:00:00",
    }
    first = client.post("/api/v1/inquiries", json=payload, headers=headers)
    second = client.post("/api/v1/inquiries", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200
    first_brief = first.get_json()["latest_brief"]
    second_brief = second.get_json()["latest_brief"]
    assert json.dumps(first_brief, sort_keys=True) == json.dumps(second_brief, sort_keys=True)

    metadata = first_brief["timeline_metadata"]
    assert metadata["timeline_profile_id"] == "finance_timeline_v1"
    assert metadata["timeline_profile_version"] == "1.0.0"
    assert metadata["timeline_engine_version"] == "phase9_timeline_engine_v1"
    assert metadata["timezone_token"] == "Asia/Seoul"
    assert metadata["window_spec_token"]
    assert metadata["active_window_token"]
    assert metadata["comparison_window_token"]
    assert metadata["baseline_policy_token"] == "fixed_prior_windows_v1:b3"
    assert metadata["evidence_manifest_hash"]
    assert metadata["timeline_summary_hash"]
    assert metadata["comparison_coverage"]["baseline_windows_available"] == 3

    timeline_findings = [finding for finding in first_brief["findings"] if finding.get("timeline_context")]
    assert timeline_findings
    assert any(finding["finding_category"] == "recurrence_observation" for finding in timeline_findings)
    assert all(
        ref.get("source_id") != 5
        for finding in timeline_findings
        for ref in finding["evidence_refs"]
        if ref.get("source_kind") == "event_record"
    )

    with app.app_context():
        inquiry = InquiryRequest.query.filter_by(user_id=user.id).order_by(InquiryRequest.id.desc()).first()
        assert inquiry is not None
        assert inquiry.normalized_payload["timezone_token"] == "Asia/Seoul"
        assert inquiry.normalized_payload["timeline_profile_token"] == "finance_timeline_v1:1.0.0"


def test_phase9_sparse_history_emits_insufficiency_for_habits(app, client):
    _enable_phase9(app)
    with app.app_context():
        user, tokens = _user_tokens("phase9-habits@example.com")
        db.session.add(
            EventRecord(
                event_type="habits.habit.logged",
                payload={"habit_id": 1, "logged_date": "2026-03-07"},
                user_id=user.id,
                created_at=datetime(2026, 3, 7, 8, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase9-habits"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did my habit pattern persist?",
            "domain": "habits",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    metadata = brief["timeline_metadata"]
    assert metadata["timeline_profile_id"] == "habits_timeline_v1"
    assert metadata["insufficiency_count"] >= 1
    assert any("insufficient" in item.lower() for item in brief["limits"])
    assert not any(finding["finding_category"] == "recurrence_observation" for finding in brief["findings"])
    assert all(finding.get("evidence_refs") for finding in brief["findings"] if finding.get("timeline_context"))


def test_phase9_no_history_suppresses_unproven_timeline_claims(app, client):
    _enable_phase9(app)
    with app.app_context():
        _, tokens = _user_tokens("phase9-no-history@example.com")

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase9-no-history"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did my habit pattern persist?",
            "domain": "habits",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    assert not any(
        finding["finding_category"] == "baseline_relative_change" and finding.get("timeline_context")
        for finding in brief["findings"]
    )
    assert any("suppressed because canonical evidence provenance is absent" in item for item in brief["limits"])
    assert all(finding.get("evidence_refs") for finding in brief["findings"] if finding.get("timeline_context"))


def test_phase9_first_wave_pair_persistence_uses_shared_timeline_metadata(app, client):
    _enable_phase9(app)
    with app.app_context():
        user, tokens = _user_tokens("phase9-pair@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="projects.task.completed",
                    payload={"task_id": 1, "completed_at": "2026-03-01T09:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 1, 9, 0, 0),
                ),
                EventRecord(
                    event_type="skills.practice.logged",
                    payload={"skill_id": 1, "practiced_at": "2026-03-02T09:00:00", "duration_minutes": 30},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 2, 9, 0, 0),
                ),
                EventRecord(
                    event_type="projects.task.completed",
                    payload={"task_id": 2, "completed_at": "2026-03-08T09:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 8, 9, 0, 0),
                ),
                EventRecord(
                    event_type="skills.practice.logged",
                    payload={"skill_id": 1, "practiced_at": "2026-03-09T09:00:00", "duration_minutes": 45},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 9, 9, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase9-pair"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did projects and skills stay aligned over time?",
            "domains": ["projects", "skills"],
            "cross_domain": True,
            "timeframe_start": "2026-03-08",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    assert brief["brief_profile"]["profile"] == "projects_skills_v1"
    assert brief["timeline_metadata"]["timeline_profile_id"] == "projects_skills_timeline_v1"
    assert any(
        finding["finding_category"] == "approved_pair_alignment_persistence" and finding.get("timeline_context")
        for finding in brief["findings"]
    )


def test_phase9_later_wave_domains_and_pairs_remain_gated(app, client):
    _enable_phase9(app)
    with app.app_context():
        user, tokens = _user_tokens("phase9-gated@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="health.metric.updated",
                    payload={"recorded_at": "2026-03-01T08:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 1, 8, 0, 0),
                ),
                EventRecord(
                    event_type="habits.habit.logged",
                    payload={"habit_id": 1, "logged_date": "2026-03-01"},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 1, 8, 30, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase9-gated"))
    health_resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How is health changing over time?",
            "domain": "health",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    pair_resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did health and habits align over time?",
            "domains": ["health", "habits"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert health_resp.status_code == 201
    assert pair_resp.status_code == 201
    assert health_resp.get_json()["latest_brief"]["timeline_metadata"] is None
    assert pair_resp.get_json()["latest_brief"]["timeline_metadata"] is None


def test_phase9_metrics_and_event_payloads_are_exposed(app, client):
    _enable_phase9(app)
    with app.app_context():
        user, tokens = _user_tokens("phase9-metrics@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="calendar.event.created",
                    payload={"event_id": 1, "title": "Sprint", "start_time": "2026-04-01T09:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 4, 1, 9, 0, 0),
                ),
                EventRecord(
                    event_type="calendar.event.created",
                    payload={"event_id": 2, "title": "Sprint", "start_time": "2026-04-08T09:00:00"},
                    user_id=user.id,
                    created_at=datetime(2026, 4, 8, 9, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase9-metrics"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What changed in calendar commitments?",
            "domain": "calendar",
            "cross_domain": False,
            "timeframe_start": "2026-04-08",
            "timeframe_end": "2026-04-14",
            "as_of_ts": "2026-04-14T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    metrics_payload = client.get("/metrics").get_data(as_text=True)
    assert "lifeos_timeline_profile_usage_total" in metrics_payload
    assert "lifeos_timeline_generation_latency_seconds_bucket" in metrics_payload
    assert "lifeos_timeline_insufficiency_total" in metrics_payload
    assert "lifeos_timeline_baseline_coverage_windows_bucket" in metrics_payload
    assert "lifeos_timeline_blocked_claims_total" in metrics_payload
    assert "lifeos_timeline_replay_mismatch_total" in metrics_payload

    with app.app_context():
        event = (
            EventRecord.query.filter_by(user_id=user.id, event_type="inquiry.brief.generated")
            .order_by(EventRecord.id.desc())
            .first()
        )
        assert event is not None
        payload = event.payload or {}
        assert payload["timeline_profile_id"] == "calendar_timeline_v1"
        assert payload["timeline_profile_version"] == "1.0.0"
        assert payload["timeline_engine_version"] == "phase9_timeline_engine_v1"
        assert payload["window_spec_token"]
        assert payload["active_window_token"]
        assert payload["comparison_window_token"]
        assert payload["baseline_policy_token"] == "fixed_prior_windows_v1:b3"
        assert payload["timezone_token"] == "UTC"
        assert payload["evidence_manifest_hash"]
        assert payload["timeline_summary_hash"]
