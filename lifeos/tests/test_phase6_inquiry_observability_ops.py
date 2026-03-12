"""Phase 6 focused inquiry ops observability checks."""

from __future__ import annotations

import re
from datetime import datetime

import pytest

from lifeos import create_app
from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


REQUIRED_METRICS = [
    "lifeos_inquiry_created_total",
    "lifeos_inquiry_generated_total",
    "lifeos_inquiry_viewed_total",
    "lifeos_inquiry_refined_total",
    "lifeos_inquiry_generation_latency_seconds_bucket",
    "lifeos_inquiry_errors_total",
    "lifeos_inquiry_empty_brief_total",
    "lifeos_inquiry_evidence_coverage_ratio",
    "lifeos_phase6_inquiry_migration_mismatch",
]


def _metric_value(payload: str, metric_name: str) -> float | None:
    match = re.search(rf"^{metric_name}(?:\{{[^}}]*\}})?\s+([0-9.eE+-]+)$", payload, re.M)
    return float(match.group(1)) if match else None


def _prime_csrf(client, token: str = "phase6-observability-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def _user_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 6 Ops",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def test_phase6_metrics_exposed_on_metrics_endpoint(client):
    payload = client.get("/metrics").get_data(as_text=True)
    for metric in REQUIRED_METRICS:
        assert metric in payload


def test_phase6_metrics_increment_on_inquiry_flow(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase6-ops@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 44.25},
                user_id=user.id,
                created_at=datetime(2026, 3, 1, 12, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    create_resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How does recent finance activity look?",
            "domain": "finance",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-10",
            "as_of_ts": "2026-03-10T00:00:00",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    inquiry_id = create_resp.get_json()["inquiry_id"]

    detail_resp = client.get(f"/api/v1/inquiries/{inquiry_id}", headers=headers)
    assert detail_resp.status_code == 200

    refine_resp = client.post(
        f"/api/v1/inquiries/{inquiry_id}/refine",
        json={"context_text": "Need narrower expense focus"},
        headers=headers,
    )
    assert refine_resp.status_code == 200

    payload = client.get("/metrics").get_data(as_text=True)

    assert (_metric_value(payload, "lifeos_inquiry_created_total") or 0.0) >= 1.0
    assert (_metric_value(payload, "lifeos_inquiry_generated_total") or 0.0) >= 2.0
    assert (_metric_value(payload, "lifeos_inquiry_viewed_total") or 0.0) >= 1.0
    assert (_metric_value(payload, "lifeos_inquiry_refined_total") or 0.0) >= 1.0

    generation_hist_count = _metric_value(payload, "lifeos_inquiry_generation_latency_seconds_count")
    assert generation_hist_count is not None
    assert generation_hist_count >= 2.0

    evidence_ratio = _metric_value(payload, "lifeos_inquiry_evidence_coverage_ratio")
    assert evidence_ratio is not None
    assert 0.0 <= evidence_ratio <= 1.0


def test_production_defaults_keep_phase6_inquiry_disabled(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    app = create_app("production")
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/v1/inquiries" not in rules
    assert "/api/v1/inquiries/" not in rules
    assert app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] is False
