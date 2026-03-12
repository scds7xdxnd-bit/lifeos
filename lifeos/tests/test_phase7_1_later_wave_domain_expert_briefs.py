"""Phase 7.1 later-wave domain expert briefs tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.contracts import CONFIDENCE_VOCABULARY
from lifeos.core.insights.inquiry_strategies import get_domain_strategy
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "phase7_1_later_wave_domain_expert_briefs_golden.json"


def _load_golden() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _user_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 7.1 Expert",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase7-1-expert-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


@pytest.mark.parametrize(
    ("domain", "event_type"),
    [
        ("journal", "journal.entry.created"),
        ("relationships", "relationships.interaction.logged"),
        ("health", "health.metric.updated"),
    ],
)
def test_later_wave_domains_use_expert_profile_safely(app, client, domain: str, event_type: str):
    golden = _load_golden()[domain]
    with app.app_context():
        user, tokens = _user_tokens(f"phase71-{domain}@example.com")
        db.session.add(
            EventRecord(
                event_type=event_type,
                payload={"value": 1, "mood": "neutral", "tags": ["focus"]},
                user_id=user.id,
                created_at=datetime(2026, 4, 1, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": f"What changed in {domain} this week?",
            "domain": domain,
            "cross_domain": False,
            "timeframe_start": "2026-04-01",
            "timeframe_end": "2026-04-07",
            "as_of_ts": "2026-04-07T23:00:00",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    brief = resp.get_json()["latest_brief"]
    profile = brief["brief_profile"]
    strategy = get_domain_strategy(domain)
    assert strategy is not None
    assert profile["expert_mode"] is golden["brief_profile"]["expert_mode"]
    assert profile["profile"] == golden["brief_profile"]["profile"]
    assert profile["profile_version"] == golden["brief_profile"]["profile_version"]
    assert profile["strategy"] == golden["brief_profile"]["strategy"]
    assert profile["strategy_version"] == golden["brief_profile"]["strategy_version"]
    assert profile["domain"] == golden["brief_profile"]["domain"]

    allowed_categories = set(golden["allowed_finding_categories"])
    assert set(profile["finding_categories"]).issubset(allowed_categories)
    for finding in brief["findings"]:
        assert finding["finding_category"] in allowed_categories
        assert finding["confidence_label"] in CONFIDENCE_VOCABULARY

    finding_uncertainty_notes = {str(item.get("uncertainty_note") or "") for item in brief["findings"]}
    limits = set(brief["limits"])
    for limitation in golden["limitation_language"]:
        assert limitation in finding_uncertainty_notes or any(limitation in item for item in limits)
    for guidance in golden["required_refine_guidance"]:
        assert guidance in brief["quality_metadata"]["refine_guidance"]


def test_later_wave_expert_output_is_deterministic(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase71-determinism@example.com")
        db.session.add(
            EventRecord(
                event_type="journal.entry.created",
                payload={"text": "Weekly reflection", "tags": ["focus"], "mood": "calm"},
                user_id=user.id,
                created_at=datetime(2026, 4, 2, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    payload = {
        "question": "How did journal activity look this week?",
        "domain": "journal",
        "cross_domain": False,
        "timeframe_start": "2026-04-01",
        "timeframe_end": "2026-04-07",
        "as_of_ts": "2026-04-07T23:00:00",
    }
    first = client.post("/api/v1/inquiries", json=payload, headers=headers)
    second = client.post("/api/v1/inquiries", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200
    assert json.dumps(first.get_json()["latest_brief"], sort_keys=True) == json.dumps(
        second.get_json()["latest_brief"], sort_keys=True
    )


@pytest.mark.parametrize(
    ("domain", "event_type", "event_payload"),
    [
        ("journal", "journal.entry.created", {"text": "Weekly reflection", "tags": ["focus"], "mood": "calm"}),
        ("relationships", "relationships.interaction.logged", {"person_id": 9, "method": "message"}),
        ("health", "health.metric.updated", {"metric": "weight", "value": 72.5}),
    ],
)
def test_later_wave_expert_output_is_deterministic_per_domain(
    app,
    client,
    domain: str,
    event_type: str,
    event_payload: dict,
):
    with app.app_context():
        user, tokens = _user_tokens(f"phase71-determinism-{domain}@example.com")
        db.session.add(
            EventRecord(
                event_type=event_type,
                payload=event_payload,
                user_id=user.id,
                created_at=datetime(2026, 4, 2, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token=f"phase71-det-{domain}"))
    payload = {
        "question": f"How does {domain} look this week?",
        "domain": domain,
        "cross_domain": False,
        "timeframe_start": "2026-04-01",
        "timeframe_end": "2026-04-07",
        "as_of_ts": "2026-04-07T23:00:00",
    }
    first = client.post("/api/v1/inquiries", json=payload, headers=headers)
    second = client.post("/api/v1/inquiries", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200
    first_brief = first.get_json()["latest_brief"]
    second_brief = second.get_json()["latest_brief"]
    assert json.dumps(first_brief, sort_keys=True) == json.dumps(second_brief, sort_keys=True)
    assert first_brief["brief_profile"]["domain"] == domain


@pytest.mark.parametrize(
    ("domain", "event_type", "event_payload"),
    [
        ("journal", "journal.entry.created", {"text": "Journal check-in", "tags": ["calm"], "mood": "neutral"}),
        ("relationships", "relationships.interaction.logged", {"person_id": 2, "method": "call"}),
        ("health", "health.metric.updated", {"metric": "sleep_hours", "value": 7.2}),
    ],
)
def test_later_wave_forbidden_claims_are_hard_blocked(
    app,
    client,
    domain: str,
    event_type: str,
    event_payload: dict,
):
    golden = _load_golden()[domain]
    with app.app_context():
        user, tokens = _user_tokens(f"phase71-guardrail-{domain}@example.com")
        db.session.add(
            EventRecord(
                event_type=event_type,
                payload=event_payload,
                user_id=user.id,
                created_at=datetime(2026, 4, 2, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": f"What does {domain} show this week?",
            "domain": domain,
            "cross_domain": False,
            "timeframe_start": "2026-04-01",
            "timeframe_end": "2026-04-07",
            "as_of_ts": "2026-04-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    for finding in brief["findings"]:
        claim = finding["claim"].lower()
        for token in golden["forbidden_claim_tokens"]:
            assert token not in claim
        assert finding["confidence_label"] in CONFIDENCE_VOCABULARY


def test_later_wave_context_remains_non_evidence_and_not_promoted(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase71-context-safety@example.com")
        db.session.add(
            EventRecord(
                event_type="journal.entry.created",
                payload={"text": "brief reflection", "tags": ["focus"], "mood": "steady"},
                user_id=user.id,
                created_at=datetime(2026, 4, 3, 9, 0, 0),
            )
        )
        db.session.commit()

    context_text = "I might have hidden intent patterns and should be diagnosed."
    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase71-context-csrf"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How does journal look?",
            "domain": "journal",
            "cross_domain": False,
            "timeframe_start": "2026-04-01",
            "timeframe_end": "2026-04-07",
            "as_of_ts": "2026-04-07T23:00:00",
            "context_text": context_text,
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    assert brief["context_non_evidence"]["label"] == "Context (not evidence)"
    assert brief["context_non_evidence"]["text"] == context_text

    lowered_context = context_text.lower()
    for finding in brief["findings"]:
        assert lowered_context not in str(finding.get("claim") or "").lower()
        for ref in finding.get("evidence_refs") or []:
            assert lowered_context not in json.dumps(ref, sort_keys=True).lower()


def test_cross_domain_paths_remain_generic_in_later_wave_phase(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase71-cross@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="journal.entry.created",
                    payload={"text": "check-in"},
                    user_id=user.id,
                    created_at=datetime(2026, 4, 1, 9, 0, 0),
                ),
                EventRecord(
                    event_type="health.metric.updated",
                    payload={"metric": "sleep_hours", "value": 7},
                    user_id=user.id,
                    created_at=datetime(2026, 4, 2, 9, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Compare journal and health.",
            "domains": ["journal", "health"],
            "cross_domain": True,
            "timeframe_start": "2026-04-01",
            "timeframe_end": "2026-04-07",
            "as_of_ts": "2026-04-07T23:00:00",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    profile = resp.get_json()["latest_brief"]["brief_profile"]
    assert profile["expert_mode"] is False
    assert profile["profile"] == "generic_inquiry_brief"
    assert profile["strategy"] == "generic_rules_v1"


@pytest.mark.parametrize(
    "domain,event_type",
    [
        ("journal", "journal.entry.created"),
        ("relationships", "relationships.interaction.logged"),
        ("health", "health.metric.updated"),
    ],
)
def test_later_wave_domains_emit_domain_labeled_metrics(app, client, domain: str, event_type: str):
    with app.app_context():
        user, tokens = _user_tokens(f"phase71-metrics-{domain}@example.com")
        db.session.add(
            EventRecord(
                event_type=event_type,
                payload={"value": 1},
                user_id=user.id,
                created_at=datetime(2026, 4, 4, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token=f"phase71-metrics-{domain}"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": f"What changed in {domain}?",
            "domain": domain,
            "cross_domain": False,
            "timeframe_start": "2026-04-01",
            "timeframe_end": "2026-04-07",
            "as_of_ts": "2026-04-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    metrics_payload = client.get("/metrics").get_data(as_text=True)
    assert f'lifeos_inquiry_generated_by_domain_total{{domain="{domain}"' in metrics_payload
