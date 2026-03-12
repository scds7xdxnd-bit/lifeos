"""Phase 6 inquiry lifecycle semantics tests."""

from __future__ import annotations

from datetime import datetime

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def _create_user_with_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 6 Lifecycle",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase6-lifecycle-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_inquiry_lifecycle_emits_canonical_v1_events_only(app, client):
    with app.app_context():
        user, tokens = _create_user_with_tokens("phase6-lifecycle@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 80},
                user_id=user.id,
                created_at=datetime(2026, 1, 2, 7, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    created = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What changed in finance?",
            "domain": "finance",
            "cross_domain": False,
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-10",
            "as_of_ts": "2026-01-10T00:00:00",
            "context_text": "Need brief for weekly review",
        },
        headers=headers,
    )
    assert created.status_code == 201
    inquiry_id = created.get_json()["inquiry_id"]

    viewed = client.get(f"/api/v1/inquiries/{inquiry_id}", headers=headers)
    assert viewed.status_code == 200

    refined = client.post(
        f"/api/v1/inquiries/{inquiry_id}/refine",
        json={"context_text": "Updated context for follow-up"},
        headers=headers,
    )
    assert refined.status_code == 200

    with app.app_context():
        emitted = {
            row.event_type
            for row in EventRecord.query.filter_by(user_id=user.id).all()
            if row.event_type.startswith("inquiry.")
        }

    expected = {
        "inquiry.requested",
        "inquiry.context.submitted",
        "inquiry.brief.generated",
        "inquiry.brief.viewed",
        "inquiry.refined",
    }
    assert emitted == expected
    assert "inquiry.saved" not in emitted
