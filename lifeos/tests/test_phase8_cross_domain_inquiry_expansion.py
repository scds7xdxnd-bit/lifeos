"""Phase 8 cross-domain inquiry expansion tests."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.inquiry_cross_domain.pairs.base import ALLOWED_CROSS_DOMAIN_CLAIM_CATEGORIES
from lifeos.core.insights.inquiry_cross_domain.registry import CROSS_DOMAIN_STRATEGY_REGISTRY
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "phase8_cross_domain_pair_profiles_golden.json"

PAIR_EVENT_TYPES: dict[tuple[str, str], tuple[str, str]] = {
    ("calendar", "projects"): ("projects.task.completed", "calendar.event.created"),
    ("finance", "habits"): ("finance.transaction.created", "habits.habit.logged"),
    ("habits", "health"): ("health.metric.updated", "habits.habit.logged"),
    ("habits", "journal"): ("journal.entry.created", "habits.habit.logged"),
    ("journal", "relationships"): ("relationships.interaction.logged", "journal.entry.created"),
    ("projects", "skills"): ("projects.task.completed", "skills.practice.logged"),
}

_SOURCE_KIND_PRIORITY = {
    "event_record": 0,
    "insight_record": 1,
    "read_model": 2,
}

FORBIDDEN_CLAIM_CLASS_TOKENS = (
    "diagnosis",
    "treatment",
    "therapy",
    "psychological",
    "moral",
    "intent",
    "caused",
    "because",
    "clinical",
)


def _load_golden() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def _pair_key(domains: tuple[str, str]) -> str:
    return "__".join(sorted(domains))


def _user_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 8 Cross Domain",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase8-cross-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def _seed_pair_events(user_id: int, domains: tuple[str, str]) -> None:
    event_a, event_b = PAIR_EVENT_TYPES[tuple(sorted(domains))]
    db.session.add_all(
        [
            EventRecord(
                event_type=event_a,
                payload={"value": 1},
                user_id=user_id,
                created_at=datetime(2026, 3, 1, 8, 0, 0),
            ),
            EventRecord(
                event_type=event_b,
                payload={"value": 1},
                user_id=user_id,
                created_at=datetime(2026, 3, 2, 9, 0, 0),
            ),
        ]
    )


def test_registry_contains_all_approved_pairs():
    approved_pairs = {
        ("calendar", "projects"),
        ("finance", "habits"),
        ("habits", "health"),
        ("habits", "journal"),
        ("journal", "relationships"),
        ("projects", "skills"),
    }
    for pair in approved_pairs:
        profile = CROSS_DOMAIN_STRATEGY_REGISTRY.get(pair)
        assert profile is not None
        assert tuple(sorted(profile.domains)) == pair
        assert profile.profile.endswith("_v1")
        fixture = _load_golden()[_pair_key(pair)]
        assert profile.profile == fixture["brief_profile"]["profile"]
        assert profile.profile_version == fixture["brief_profile"]["profile_version"]
        assert profile.strategy == fixture["brief_profile"]["strategy"]
        assert profile.strategy_version == fixture["brief_profile"]["strategy_version"]
        assert profile.domain == fixture["brief_profile"]["domain"]


@pytest.mark.parametrize("domains", sorted(PAIR_EVENT_TYPES.keys()))
def test_approved_pairs_are_deterministic_and_profiled(app, client, domains: tuple[str, str]):
    domain_a, domain_b = domains
    fixture = _load_golden()[_pair_key(domains)]
    with app.app_context():
        user, tokens = _user_tokens(f"phase8-det-{domain_a}-{domain_b}@example.com")
        _seed_pair_events(user.id, domains)
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token=f"phase8-det-{domain_a}-{domain_b}"))
    payload = {
        "question": f"How do {domain_a} and {domain_b} align?",
        "domains": [domain_a, domain_b],
        "cross_domain": True,
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

    brief = first.get_json()["latest_brief"]
    profile = CROSS_DOMAIN_STRATEGY_REGISTRY.get(domains)
    assert profile is not None
    brief_profile = brief["brief_profile"]
    fixture_profile = fixture["brief_profile"]
    assert brief_profile["profile"] == fixture_profile["profile"] == profile.profile
    assert brief_profile["profile_version"] == fixture_profile["profile_version"] == profile.profile_version
    assert brief_profile["strategy"] == fixture_profile["strategy"] == profile.strategy
    assert brief_profile["strategy_version"] == fixture_profile["strategy_version"] == profile.strategy_version
    assert brief_profile["domain"] == fixture_profile["domain"] == profile.domain
    assert brief_profile["expert_mode"] is fixture_profile["expert_mode"]
    assert set(brief["brief_profile"]["finding_categories"]).issubset(set(fixture["allowed_finding_categories"]))
    for required in fixture["required_refine_guidance"]:
        assert required in brief["quality_metadata"]["refine_guidance"]
    for limitation in fixture["limitation_language"]:
        assert any(limitation in item for item in brief["limits"])

    selected = set(domains)
    for finding in brief["findings"]:
        assert finding["finding_category"] in ALLOWED_CROSS_DOMAIN_CLAIM_CATEGORIES
        assert set(finding["source_domains"]) == selected
        refs = finding["evidence_refs"]
        assert refs == sorted(
            refs,
            key=lambda item: (
                str(item.get("created_at") or ""),
                _SOURCE_KIND_PRIORITY.get(str(item.get("source_kind") or ""), 99),
                int(item.get("source_id") or 0),
                str(item.get("source_ref") or ""),
            ),
        )
        ref_domains = {ref.get("domain") for ref in refs if ref.get("domain")}
        assert selected.issubset(ref_domains)
        claim = str(finding.get("claim") or "").lower()
        for token in FORBIDDEN_CLAIM_CLASS_TOKENS:
            assert token not in claim


def test_unsupported_pair_falls_back_to_generic_profile(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase8-fallback@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 15},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 1, 8, 0, 0),
                ),
                EventRecord(
                    event_type="projects.task.completed",
                    payload={"task": "alpha"},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 2, 8, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Compare finance and projects.",
            "domains": ["finance", "projects"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    profile = response.get_json()["latest_brief"]["brief_profile"]
    assert profile["profile"] == "generic_inquiry_brief"
    assert profile["expert_mode"] is False


def test_pair_profile_emits_coverage_gap_when_one_domain_has_no_evidence(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase8-coverage-gap@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 42},
                user_id=user.id,
                created_at=datetime(2026, 3, 1, 8, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase8-coverage-gap"))
    response = client.post(
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
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    assert brief["brief_profile"]["profile"] == "finance_habits_v1"
    coverage_finding = next((f for f in brief["findings"] if f["finding_category"] == "coverage_gap"), None)
    assert coverage_finding is not None
    assert coverage_finding["confidence_label"] == "needs_review"
    assert set(coverage_finding["source_domains"]) == {"finance", "habits"}


def test_cross_domain_requires_exact_two_domains_for_pair_activation(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase8-exact-two@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 10},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 1, 8, 0, 0),
                ),
                EventRecord(
                    event_type="habits.habit.logged",
                    payload={"habit_id": 3},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 2, 8, 0, 0),
                ),
                EventRecord(
                    event_type="projects.task.completed",
                    payload={"task": "scope"},
                    user_id=user.id,
                    created_at=datetime(2026, 3, 3, 8, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase8-three-domains"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Compare finance habits and projects.",
            "domains": ["finance", "habits", "projects"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    profile = response.get_json()["latest_brief"]["brief_profile"]
    assert profile["profile"] == "generic_inquiry_brief"
    assert profile["expert_mode"] is False


@pytest.mark.parametrize("domains", sorted(PAIR_EVENT_TYPES.keys()))
def test_forbidden_claim_tokens_are_blocked_for_each_pair(app, client, domains: tuple[str, str]):
    domain_a, domain_b = domains
    profile = CROSS_DOMAIN_STRATEGY_REGISTRY.get(domains)
    fixture = _load_golden()[_pair_key(domains)]
    assert profile is not None
    with app.app_context():
        user, tokens = _user_tokens(f"phase8-guard-{domain_a}-{domain_b}@example.com")
        _seed_pair_events(user.id, domains)
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token=f"phase8-guard-{domain_a}-{domain_b}"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": f"Assess {domain_a} and {domain_b}.",
            "domains": [domain_a, domain_b],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    for finding in brief["findings"]:
        claim = str(finding.get("claim") or "").lower()
        for token in profile.forbidden_claim_tokens + tuple(fixture["forbidden_claim_tokens"]):
            assert token.lower() not in claim
        for token in FORBIDDEN_CLAIM_CLASS_TOKENS:
            assert token not in claim


def test_cross_domain_brief_payload_remains_structured_and_non_chat(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase8-non-chat@example.com")
        _seed_pair_events(user.id, ("finance", "habits"))
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase8-non-chat"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How do finance and habits align?",
            "domains": ["finance", "habits"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    assert brief.get("summary")
    assert isinstance(brief.get("findings"), list)
    assert isinstance(brief.get("context_non_evidence"), dict)
    assert isinstance(brief.get("quality_metadata"), dict)
    assert "messages" not in brief
    assert "assistant_reply" not in brief
    assert brief["context_non_evidence"]["label"] == "Context (not evidence)"


def test_single_domain_flow_remains_unchanged(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase8-single-domain-regression@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 25},
                user_id=user.id,
                created_at=datetime(2026, 3, 4, 8, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase8-single-domain"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How did finance look this week?",
            "domain": "finance",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-07",
            "as_of_ts": "2026-03-07T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    profile = response.get_json()["latest_brief"]["brief_profile"]
    assert profile["profile"] == "finance_domain_expert_brief"
    assert profile["expert_mode"] is True
