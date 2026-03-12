"""Phase 6 inquiry evidence mapping tests."""

from __future__ import annotations

from datetime import datetime

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InsightRecord
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def _user_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 6 Evidence",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase6-evidence-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_findings_have_resolvable_evidence_refs(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase6-evidence-a@example.com")
        event = EventRecord(
            event_type="finance.transaction.created",
            payload={"amount": 88},
            user_id=user.id,
            created_at=datetime(2026, 1, 2, 10, 0, 0),
        )
        db.session.add(event)
        db.session.flush()
        db.session.add(
            InsightRecord(
                user_id=user.id,
                event_id=event.id,
                event_type=event.event_type,
                kind="finance_spend",
                message="spent",
                severity="info",
                data={},
                created_at=datetime(2026, 1, 2, 10, 30, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What happened in finance?",
            "domain": "finance",
            "cross_domain": False,
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-10",
            "as_of_ts": "2026-01-10T00:00:00",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    findings = resp.get_json()["latest_brief"]["findings"]
    assert findings
    with app.app_context():
        for finding in findings:
            refs = finding["evidence_refs"]
            assert refs
            for ref in refs:
                kind = ref["source_kind"]
                if kind == "event_record":
                    row = EventRecord.query.get(ref["source_id"])
                    assert row is not None
                    assert row.event_type == ref["event_type"]
                elif kind == "insight_record":
                    row = InsightRecord.query.get(ref["source_id"])
                    assert row is not None
                    assert row.kind == ref["insight_type"]
                else:
                    assert kind == "read_model"
                    assert str(ref["source_ref"]).startswith("inquiry.event_count_projection:")


def test_cross_domain_findings_label_sources(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase6-evidence-b@example.com")
        db.session.add_all(
            [
                EventRecord(
                    event_type="finance.transaction.created",
                    payload={"amount": 42},
                    user_id=user.id,
                    created_at=datetime(2026, 1, 1, 8, 0, 0),
                ),
                EventRecord(
                    event_type="habits.habit.logged",
                    payload={"habit_id": 1},
                    user_id=user.id,
                    created_at=datetime(2026, 1, 2, 8, 0, 0),
                ),
            ]
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What is the cross-domain pattern?",
            "domains": ["finance", "habits"],
            "cross_domain": True,
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-10",
            "as_of_ts": "2026-01-10T00:00:00",
        },
        headers=headers,
    )
    assert resp.status_code == 201
    findings = resp.get_json()["latest_brief"]["findings"]
    cross = [item for item in findings if len(item["source_domains"]) > 1]
    assert cross
    selected = {"finance", "habits"}
    for finding in cross:
        assert set(finding["source_domains"]) == selected
        ref_domains = {ref.get("domain") for ref in finding["evidence_refs"] if ref.get("domain")}
        assert selected.issubset(ref_domains)
