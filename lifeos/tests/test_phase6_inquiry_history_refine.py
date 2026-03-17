"""Phase 6 inquiry history/version/refine tests."""

from __future__ import annotations

from datetime import datetime

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.models import InquiryBriefVersion
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


def _user_tokens(email: str):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 6 History",
            timezone="UTC",
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase6-history-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def test_refine_creates_new_version_and_preserves_prior_payload(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase6-history-a@example.com")
        db.session.add(
            EventRecord(
                event_type="projects.task.completed",
                payload={"task": "ship"},
                user_id=user.id,
                created_at=datetime(2026, 1, 2, 14, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client))
    created = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How are projects going?",
            "domain": "projects",
            "cross_domain": False,
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-10",
            "as_of_ts": "2026-01-10T00:00:00",
        },
        headers=headers,
    )
    assert created.status_code == 201
    body = created.get_json()
    inquiry_id = body["inquiry_id"]
    first_brief = body["latest_brief"]

    refined = client.post(
        f"/api/v1/inquiries/{inquiry_id}/refine",
        json={"context_text": "Need more precise project framing"},
        headers=headers,
    )
    assert refined.status_code == 200
    assert refined.get_json()["version_number"] == 2

    detail = client.get(f"/api/v1/inquiries/{inquiry_id}", headers=headers)
    assert detail.status_code == 200
    inquiry = detail.get_json()["inquiry"]
    versions = inquiry["versions"]
    assert len(versions) == 2
    assert versions[0]["version_number"] == 1
    assert versions[1]["version_number"] == 2
    assert versions[0]["brief"] == first_brief
    assert versions[1]["parent_version_id"] == versions[0]["id"]

    with app.app_context():
        db_versions = (
            InquiryBriefVersion.query.filter_by(inquiry_id=inquiry_id)
            .order_by(InquiryBriefVersion.version_number.asc())
            .all()
        )
        assert len(db_versions) == 2
        assert db_versions[1].parent_version_id == db_versions[0].id
        canonical_first_brief = dict(first_brief)
        canonical_first_brief.pop("humanized_brief", None)
        assert db_versions[0].brief_payload == canonical_first_brief
