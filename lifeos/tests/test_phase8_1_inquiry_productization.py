"""Phase 8.1 inquiry productization integration tests."""

from __future__ import annotations

import json
from datetime import datetime

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit

ALLOWED_ANSWERABILITY = {"strong_answerable", "partial_answerable", "weak_answerable"}


def _user_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 8.1 Productization",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase8-1-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_productized_brief_fields_exist_and_are_deterministic(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase81-productization-a@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 130},
                user_id=user.id,
                created_at=datetime(2026, 3, 8, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
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
    assert json.dumps(first_brief, sort_keys=True) == json.dumps(second_brief, sort_keys=True)

    assert "direct_answer" in first_brief
    assert "answerability" in first_brief
    assert "refine_guidance" in first_brief
    assert "bounded_patterns" in first_brief
    assert "productization_metadata" in first_brief
    assert first_brief["answerability"]["classification"] in ALLOWED_ANSWERABILITY
    assert first_brief["direct_answer"]["text"]
    assert first_brief["direct_answer"]["supporting_claims"]
    assert first_brief["refine_guidance"]
    assert any("Likely gain:" in item for item in first_brief["refine_guidance"])
    assert first_brief["productization_metadata"]["version"] == "phase8_1_productization_v1"
    assert (
        first_brief["productization_metadata"]["limitation_count_before"]
        >= first_brief["productization_metadata"]["limitation_count_after"]
    )
    assert "messages" not in first_brief
    assert "assistant_reply" not in first_brief
    for idx, finding in enumerate(first_brief["findings"], start=1):
        assert finding["relevance_rank"] == idx
        assert finding["relevance_reason"]
        assert finding["evidence_refs"]


def test_productized_cross_domain_brief_preserves_evidence_and_no_causal_overreach(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase81-productization-b@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 80},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 3, 10, 0, 0),
                ),
                EventRecord(
                    event_type="habits.habit.logged",
                    payload={"habit_id": 1},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 4, 10, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase8-1-cross"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How do finance and habits align?",
            "domains": ["finance", "habits"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-09",
            "as_of_ts": "2026-03-09T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    selected = {"finance", "habits"}
    for finding in brief["findings"]:
        assert set(finding["source_domains"]) == selected
        ref_domains = {item.get("domain") for item in finding["evidence_refs"] if item.get("domain")}
        assert selected.issubset(ref_domains)

    direct_text = str(brief["direct_answer"]["text"]).lower()
    for token in ("caused", "because", "therefore", "diagnosis", "treatment"):
        assert token not in direct_text

    metadata = brief["productization_metadata"]
    assert metadata["limitation_count_before"] >= metadata["limitation_count_after"]
    assert metadata["limitation_redundancy_removed"] >= 0


def test_productization_keeps_context_non_evidence_and_out_of_direct_answer(app, client):
    context_text = "UNSUPPORTED_CONTEXT_ONLY_987"
    with app.app_context():
        user, tokens = _user_tokens("phase81-productization-context@example.com")
        db.session.add(
            EventRecord(
                event_type="journal.entry.created",
                payload={"title": "weekly note"},
                user_id=user.id,
                created_at=datetime(2026, 3, 2, 10, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase8-1-context"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What changed in journal?",
            "domain": "journal",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-09",
            "as_of_ts": "2026-03-09T23:00:00",
            "context_text": context_text,
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    assert brief["context_non_evidence"]["label"] == "Context (not evidence)"
    assert brief["context_non_evidence"]["text"] == context_text
    assert context_text not in str(brief["direct_answer"]["text"])
    evidence_blob = json.dumps([finding["evidence_refs"] for finding in brief["findings"]], sort_keys=True)
    assert context_text not in evidence_blob


def test_productization_metrics_are_exposed(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase81-productization-c@example.com")
        db.session.add(
            EventRecord(
                event_type="projects.task.completed",
                payload={"task": "integration"},
                user_id=user.id,
                created_at=datetime(2026, 3, 2, 10, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase8-1-metrics"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How did projects progress?",
            "domain": "projects",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-09",
            "as_of_ts": "2026-03-09T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    metrics_payload = client.get("/metrics").get_data(as_text=True)
    assert "lifeos_inquiry_productization_total" in metrics_payload
    assert "lifeos_inquiry_productization_latency_seconds_bucket" in metrics_payload
    assert "lifeos_inquiry_direct_answer_present_total" in metrics_payload
    assert "lifeos_inquiry_answerability_total" in metrics_payload
    assert "lifeos_inquiry_limitation_redundancy_removed_total" in metrics_payload
    assert "lifeos_inquiry_productization_by_domain_total" in metrics_payload
    assert "lifeos_inquiry_productization_latency_seconds_by_domain_bucket" in metrics_payload
    assert "lifeos_inquiry_answerability_by_domain_total" in metrics_payload
