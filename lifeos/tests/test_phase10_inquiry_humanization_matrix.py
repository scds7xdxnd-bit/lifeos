"""Phase 10 QA matrix: deterministic humanization invariants and safety gates."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.inquiry_humanization import (
    HUMANIZATION_VERSION,
    HumanizationRequest,
    humanize_inquiry_brief,
    serialize_humanized_brief,
)
from lifeos.core.insights.inquiry_humanization.terminology import simplify_text
from lifeos.core.insights.models import InquiryBriefVersion
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "phase10_humanization_fixture_matrix.json"
MATRIX = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

FORBIDDEN_REWRITE_TOKENS = (
    "recommend",
    "should",
    "predict",
    "forecast",
    "cause",
    "because of",
    "diagnosis",
    "treatment",
    "assistant",
    "chat",
    "feels",
)


def _canonical_brief(
    *,
    claim: str,
    domain: str = "finance",
    domains: list[str] | None = None,
    lens: str = "domain",
) -> dict[str, object]:
    selected_domains = domains or [domain]
    finding = {
        "finding_id": "finding_1",
        "claim": claim,
        "finding_category": "signal",
        "confidence_label": "informational",
        "uncertainty_note": "Evidence is bounded to recorded events in this scope.",
        "source_domains": selected_domains,
        "evidence_refs": [
            {
                "source_kind": "event_record",
                "source_id": 1,
                "event_type": f"{selected_domains[0]}.event.created",
                "domain": selected_domains[0],
                "created_at": "2026-03-10T09:00:00",
            }
        ],
    }
    return {
        "summary": claim,
        "question": "What changed in this scope?",
        "lens": lens,
        "domains": selected_domains,
        "timeframe": {"start": "2026-03-01", "end": "2026-03-14"},
        "as_of_ts": "2026-03-14T23:00:00",
        "direct_answer": {"text": claim, "supporting_claims": [claim], "note": "Canonical answer."},
        "answerability": {
            "classification": "partial_answerable",
            "reason": "Coverage is mixed.",
            "evidence_coverage_ratio": 0.5,
            "supporting_finding_count": 1,
        },
        "findings": [finding],
        "limits": ["Sparse records in the selected timeframe."],
        "limitation_items": [{"limitation_id": "limitation_1", "text": "Sparse records in the selected timeframe."}],
    }


def _humanize(brief: dict[str, object], *, brief_hash: str = "hash_v1") -> dict[str, object]:
    return serialize_humanized_brief(
        humanize_inquiry_brief(
            HumanizationRequest(
                canonical_brief=brief,
                canonical_brief_hash=brief_hash,
            )
        )
    )


def _enable_phase10(app) -> None:
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    app.config["ENABLE_PHASE10_INQUIRY_HUMANIZATION"] = True
    app.config["ENABLE_PHASE9_TIMELINE_INTELLIGENCE"] = False


def _create_user_and_tokens(email: str, *, timezone: str = "UTC"):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 10 QA",
            timezone=timezone,
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase10-matrix-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {access_token}",
        "X-CSRF-Token": csrf_token,
    }


@pytest.mark.parametrize("case", MATRIX["terminology_cases"], ids=[row["name"] for row in MATRIX["terminology_cases"]])
def test_phase10_term_simplification_matrix(case: dict):
    rendered = simplify_text(case["text"])
    for token in case["expect_contains"]:
        assert token in rendered
    for token in case["expect_not_contains"]:
        assert token not in rendered


@pytest.mark.parametrize(
    "case",
    MATRIX["domain_adapter_cases"],
    ids=[row["name"] for row in MATRIX["domain_adapter_cases"]],
)
def test_phase10_domain_phrase_adapter_matrix(case: dict):
    brief = _canonical_brief(claim=case["claim"], domain=case["domain"], domains=[case["domain"]], lens="domain")
    humanized = _humanize(brief)
    rendered = " ".join(
        [humanized["answer"]["text"]]
        + [block["text"] for section in humanized["sections"] for block in section["blocks"]]
    ).lower()
    for token in case["expect_contains"]:
        assert token.lower() in rendered


@pytest.mark.parametrize(
    "case",
    MATRIX["pair_adapter_cases"],
    ids=[row["name"] for row in MATRIX["pair_adapter_cases"]],
)
def test_phase10_approved_pair_phrase_adapter_matrix(case: dict):
    claim = "Approved pair alignment was observed in the selected timeframe."
    brief = _canonical_brief(claim=claim, domains=case["domains"], lens="cross_domain")
    humanized = _humanize(brief)
    rendered = " ".join(
        [humanized["answer"]["text"]]
        + [block["text"] for section in humanized["sections"] for block in section["blocks"]]
    ).lower()
    assert case["expected_phrase"].lower() in rendered
    assert "approved pair alignment" not in rendered


def test_phase10_determinism_same_canonical_plus_version_same_humanized_hash():
    brief = _canonical_brief(claim="Ledger cashflow summary is stable.")
    first = _humanize(brief, brief_hash="canonical_hash_abc")
    second = _humanize(brief, brief_hash="canonical_hash_abc")
    assert json.dumps(first, sort_keys=True) == json.dumps(second, sort_keys=True)
    assert first["metadata"]["humanization_version"] == HUMANIZATION_VERSION
    assert first["metadata"]["humanized_brief_hash"] == second["metadata"]["humanized_brief_hash"]


def test_phase10_traceability_uncertainty_and_confidence_preserved():
    brief = _canonical_brief(claim="Ledger cashflow summary is stable.")
    humanized = _humanize(brief, brief_hash="canonical_hash_trace")

    canonical_finding_ids = {row["finding_id"] for row in brief["findings"]}
    canonical_limitation_ids = {row["limitation_id"] for row in brief["limitation_items"]}
    canonical_confidence = {row["finding_id"]: row["confidence_label"] for row in brief["findings"]}

    for section in humanized["sections"]:
        for block in section["blocks"]:
            assert set(block["source_finding_ids"]).issubset(canonical_finding_ids)
            assert set(block["source_limitation_ids"]).issubset(canonical_limitation_ids)
            if block["source_finding_ids"]:
                assert isinstance(block["evidence_refs"], list)
                assert len(block["evidence_refs"]) > 0
                if block["confidence_label"]:
                    for finding_id in block["source_finding_ids"]:
                        assert block["confidence_label"] == canonical_confidence[finding_id]

    review_section = next(item for item in humanized["sections"] if item["section_id"] == "what_to_review_next")
    assert len(review_section["blocks"]) == len(brief["limitation_items"])


def test_phase10_forbidden_rewrite_tokens_and_no_answerability_inflation():
    brief = _canonical_brief(claim="Ledger cashflow summary is stable.")
    humanized = _humanize(brief, brief_hash="canonical_hash_safe")
    rendered = " ".join(
        [humanized["answer"]["text"]]
        + [block["text"] for section in humanized["sections"] for block in section["blocks"]]
    ).lower()
    for token in FORBIDDEN_REWRITE_TOKENS:
        assert token not in rendered
    how_sure = next(item for item in humanized["sections"] if item["section_id"] == "how_sure_this_is")
    assert "Partially answerable" in how_sure["blocks"][0]["text"]


def test_phase10_fallback_to_canonical_when_humanization_disabled(app, client):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    app.config["ENABLE_PHASE10_INQUIRY_HUMANIZATION"] = False
    with app.app_context():
        user, tokens = _create_user_and_tokens("phase10-fallback@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 22},
                user_id=user.id,
                created_at=datetime(2026, 3, 5, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase10-fallback"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What changed in finance?",
            "domain": "finance",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    assert brief["humanized_brief"] is None
    assert brief["findings"]
    assert brief["answerability"]["classification"] in {"strong_answerable", "partial_answerable", "weak_answerable"}


def test_phase10_technical_view_accessible_with_humanized_default(app, client):
    _enable_phase10(app)
    user_id = None
    with app.app_context():
        user, tokens = _create_user_and_tokens("phase10-technical@example.com")
        user_id = user.id
        db.session.add(
            EventRecord(
                event_type="habits.habit.logged",
                payload={"habit_id": 1, "logged_date": "2026-03-10"},
                user_id=user.id,
                created_at=datetime(2026, 3, 10, 9, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase10-technical"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did my habit routine hold?",
            "domain": "habits",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    body = response.get_json()
    brief = body["latest_brief"]
    humanized = brief["humanized_brief"]
    assert humanized is not None
    assert humanized["metadata"]["technical_view_available"] is True
    assert brief["findings"]  # canonical view remains in the same response surface

    with app.app_context():
        stored = InquiryBriefVersion.query.filter_by(user_id=user_id).order_by(InquiryBriefVersion.id.desc()).first()
        assert stored is not None
        assert brief["answerability"] == stored.brief_payload["answerability"]
