"""Phase 10 inquiry humanization integration tests."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.inquiry_humanization.adapters import resolve_adapter
from lifeos.core.insights.inquiry_humanization.terminology import simplify_text
from lifeos.core.insights.models import InquiryBriefVersion
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


FORBIDDEN_HUMANIZED_TOKENS = (
    "recommend",
    "should",
    "predict",
    "forecast",
    "assistant",
    "chat",
)


def _enable_phase10(app, *, timeline: bool = False) -> None:
    app.config["ENABLE_PHASE10_INQUIRY_HUMANIZATION"] = True
    app.config["ENABLE_PHASE9_TIMELINE_INTELLIGENCE"] = timeline
    app.config["PHASE9_ENABLED_TIMELINE_PROFILES"] = None


def _user_tokens(email: str, *, timezone: str = "UTC"):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 10 Humanization",
            timezone=timezone,
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase10-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_phase10_terminology_normalizes_case_and_spacing_variants():
    rendered = simplify_text("Canonical Records in the Selected Time Frame with Ledger cash flow notes.")
    lowered = rendered.lower()
    assert "saved records" in lowered
    assert "selected time range" in lowered
    assert "canonical records" not in lowered
    assert "selected time frame" not in lowered


def test_phase10_adapter_resolution_normalizes_domain_and_pair_keys():
    assert resolve_adapter({"lens": "DOMAIN", "domains": [" Habit "]}).key == "habits"
    assert (
        resolve_adapter({"lens": "Cross Domain", "domains": [" Relationships ", "Journal"]}).key
        == "journal__relationships"
    )


def test_phase10_humanized_brief_is_deterministic_and_keeps_canonical_hash(app, client):
    _enable_phase10(app)
    with app.app_context():
        user, tokens = _user_tokens("phase10-finance@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 45},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 2, 10, 0, 0),
                ),
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 60},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 5, 10, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase10-finance"))
    payload = {
        "question": "What does finance show this week?",
        "domain": "finance",
        "cross_domain": False,
        "timeframe_start": "2026-03-01",
        "timeframe_end": "2026-03-09",
        "as_of_ts": "2026-03-09T23:00:00",
    }
    first = client.post("/api/v1/inquiries", json=payload, headers=headers)
    second = client.post("/api/v1/inquiries", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200

    first_brief = first.get_json()["latest_brief"]
    second_brief = second.get_json()["latest_brief"]
    assert json.dumps(first_brief["humanized_brief"], sort_keys=True) == json.dumps(
        second_brief["humanized_brief"],
        sort_keys=True,
    )

    humanized = first_brief["humanized_brief"]
    assert humanized is not None
    assert humanized["metadata"]["humanization_version"] == "phase10_humanization_v1"
    assert humanized["metadata"]["technical_view_available"] is True
    assert humanized["answer"]["text"]

    with app.app_context():
        version = InquiryBriefVersion.query.filter_by(user_id=user.id).order_by(InquiryBriefVersion.id.desc()).first()
        assert version is not None
        assert humanized["metadata"]["canonical_brief_hash"] == version.brief_hash


def test_phase10_humanized_blocks_map_back_to_canonical_findings_and_limitations(app, client):
    _enable_phase10(app)
    with app.app_context():
        user, tokens = _user_tokens("phase10-habits@example.com")
        db.session.add(
            EventRecord(
                event_type="habits.habit.logged",
                payload={"habit_id": 1, "logged_date": "2026-03-07"},
                user_id=user.id,
                created_at=datetime(2026, 3, 7, 8, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase10-habits"))
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
    assert brief["limitation_items"]
    finding_ids = {item["finding_id"] for item in brief["findings"]}
    limitation_ids = {item["limitation_id"] for item in brief["limitation_items"]}

    humanized = brief["humanized_brief"]
    assert humanized is not None
    for section in humanized["sections"]:
        assert section["title"]
        assert section["blocks"]
        for block in section["blocks"]:
            assert block["source_finding_ids"] or block["source_limitation_ids"]
            assert set(block["source_finding_ids"]).issubset(finding_ids)
            assert set(block["source_limitation_ids"]).issubset(limitation_ids)
            if block["source_finding_ids"]:
                assert isinstance(block["evidence_refs"], list)
    assert set(humanized["answer"]["source_finding_ids"]).issubset(finding_ids)

    stands_out = next(section for section in humanized["sections"] if section["section_id"] == "what_stands_out")
    review_next = next(section for section in humanized["sections"] if section["section_id"] == "what_to_review_next")
    assert len(stands_out["blocks"]) == len(brief["findings"])
    assert len(review_next["blocks"]) == len(brief["limitation_items"])


def test_phase10_forbidden_rewrite_regression_preserves_confidence_and_avoids_pair_jargon(app, client):
    _enable_phase10(app, timeline=True)
    with app.app_context():
        user, tokens = _user_tokens("phase10-pair@example.com")
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

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase10-pair"))
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
    humanized = brief["humanized_brief"]
    assert humanized is not None

    canonical_confidence = {item["finding_id"]: item["confidence_label"] for item in brief["findings"]}
    rendered = (
        humanized["answer"]["text"]
        + " "
        + " ".join(block["text"] for section in humanized["sections"] for block in section["blocks"])
    )
    lowered = rendered.lower()
    for token in FORBIDDEN_HUMANIZED_TOKENS:
        assert token not in lowered
    assert "approved pair alignment" not in lowered
    assert "project work and skill practice" in lowered

    for section in humanized["sections"]:
        for block in section["blocks"]:
            if not block["confidence_label"] or not block["source_finding_ids"]:
                continue
            for finding_id in block["source_finding_ids"]:
                assert block["confidence_label"] == canonical_confidence[finding_id]


def test_phase10_event_payload_exposes_humanization_lineage(app, client):
    _enable_phase10(app)
    with app.app_context():
        user, tokens = _user_tokens("phase10-event@example.com")
        db.session.add(
            EventRecord(
                event_type="calendar.event.created",
                payload={"event_id": 1, "title": "Review", "start_time": "2026-04-08T09:00:00"},
                user_id=user.id,
                created_at=datetime(2026, 4, 8, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase10-event"))
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
    brief = response.get_json()["latest_brief"]
    metadata = brief["humanized_brief"]["metadata"]

    with app.app_context():
        event = (
            EventRecord.query.filter_by(user_id=user.id, event_type="inquiry.brief.generated")
            .order_by(EventRecord.id.desc())
            .first()
        )
        assert event is not None
        payload = event.payload or {}
        assert payload["canonical_brief_hash"] == metadata["canonical_brief_hash"]
        assert payload["humanization_version"] == metadata["humanization_version"]
        assert payload["humanized_brief_hash"] == metadata["humanized_brief_hash"]
        assert payload["technical_view_available"] is True
