"""Phase 7 domain expert briefs tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.contracts import CONFIDENCE_VOCABULARY
from lifeos.core.insights.inquiry_strategies import get_first_wave_strategy
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "phase7_domain_expert_briefs_golden.json"


def _load_golden() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _user_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 7 Expert",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase7-expert-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


@pytest.mark.parametrize(
    ("domain", "event_type"),
    [
        ("finance", "finance.transaction.created"),
        ("habits", "habits.habit.logged"),
        ("projects", "projects.task.completed"),
        ("skills", "skills.practice.logged"),
    ],
)
def test_first_wave_domains_use_expert_profile_and_categories(
    app,
    client,
    domain: str,
    event_type: str,
):
    golden = _load_golden()[domain]
    with app.app_context():
        user, tokens = _user_tokens(f"phase7-{domain}@example.com")
        db.session.add(
            EventRecord(
                event_type=event_type,
                payload={"value": 1},
                user_id=user.id,
                created_at=datetime(2026, 3, 1, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": f"What is the latest {domain} signal?",
            "domain": domain,
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    brief = resp.get_json()["latest_brief"]
    profile = brief["brief_profile"]
    strategy = get_first_wave_strategy(domain)
    assert strategy is not None
    assert profile["expert_mode"] is golden["brief_profile"]["expert_mode"]
    assert profile["profile"] == golden["brief_profile"]["profile"]
    assert profile["profile_version"] == golden["brief_profile"]["profile_version"]
    assert profile["strategy_version"] == golden["brief_profile"]["strategy_version"]
    assert profile["domain"] == golden["brief_profile"]["domain"]
    assert profile["strategy"] == golden["brief_profile"]["strategy"]

    categories = set(golden["allowed_finding_categories"])
    observed_categories = set(profile["finding_categories"])
    assert observed_categories
    assert observed_categories.issubset(categories)
    assert strategy.coverage_category in observed_categories
    for finding in brief["findings"]:
        assert finding["finding_category"] in categories
        assert finding["confidence_label"] in CONFIDENCE_VOCABULARY

    finding_uncertainty_notes = {str(item.get("uncertainty_note") or "") for item in brief["findings"]}
    limits = set(brief["limits"])
    for limitation in golden["limitation_language"]:
        assert limitation in finding_uncertainty_notes or any(limitation in item for item in limits)
    for guidance in golden["required_refine_guidance"]:
        assert guidance in brief["quality_metadata"]["refine_guidance"]
    assert tuple(strategy.forbidden_claim_tokens) == tuple(golden["forbidden_claim_tokens"])


def test_domain_expert_brief_is_deterministic_for_same_input_and_as_of(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase7-determinism@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.journal.posted",
                payload={"debit_total": 100, "credit_total": 100},
                user_id=user.id,
                created_at=datetime(2026, 3, 2, 10, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    payload = {
        "question": "How does finance look this week?",
        "domain": "finance",
        "cross_domain": False,
        "timeframe_start": "2026-03-01",
        "timeframe_end": "2026-03-07",
        "as_of_ts": "2026-03-07T23:00:00",
    }
    first = client.post("/api/v1/inquiries", json=payload, headers=headers)
    second = client.post("/api/v1/inquiries", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200
    assert json.dumps(first.get_json()["latest_brief"], sort_keys=True) == json.dumps(
        second.get_json()["latest_brief"], sort_keys=True
    )


def test_cross_domain_inquiry_keeps_generic_profile_no_expert_leak(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase7-cross@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 30},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 2, 10, 0, 0),
                ),
                EventRecord(
                    event_type="habits.habit.logged",
                    payload={"habit_id": 5},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 3, 10, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Compare finance and habits.",
            "domains": ["finance", "habits"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    brief = resp.get_json()["latest_brief"]
    profile = brief["brief_profile"]
    assert profile["expert_mode"] is False
    assert profile["profile"] == "generic_inquiry_brief"
    assert profile["strategy"] == "generic_rules_v1"


def test_first_wave_claims_do_not_emit_forbidden_claim_types(app, client):
    golden = _load_golden()["skills"]
    with app.app_context():
        user, tokens = _user_tokens("phase7-guardrail@example.com")
        db.session.add(
            EventRecord(
                event_type="skills.practice.logged",
                payload={"minutes": 45},
                user_id=user.id,
                created_at=datetime(2026, 3, 4, 10, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How is skills practice this week?",
            "domain": "skills",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    strategy = get_first_wave_strategy("skills")
    assert strategy is not None
    for finding in brief["findings"]:
        claim = finding["claim"].lower()
        for token in golden["forbidden_claim_tokens"]:
            assert token not in claim
