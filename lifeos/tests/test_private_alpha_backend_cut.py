"""Private alpha backend cut tests."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from lifeos.core.auth.models import Role
from lifeos.core.auth.auth_service import issue_private_alpha_invite, issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.inquiry_service import InquiryBriefVersion
from lifeos.core.insights.substrate_models import UserFeedbackEvent
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


WAVE1_DOMAINS = ("calendar", "habits", "projects", "skills")
LIVE_ALPHA_PAIRS = ("projects_calendar_v1", "projects_skills_v1")


def _enable_private_alpha(
    app,
    *,
    history: bool = True,
    feedback: bool = True,
    technical_brief: bool = True,
    phase8: bool = True,
    phase9: bool = False,
) -> None:
    app.config["ENABLE_PRIVATE_ALPHA"] = True
    app.config["ALPHA_INVITE_ONLY"] = True
    app.config["ALPHA_MAX_USERS"] = 30
    app.config["ALPHA_VISIBLE_DOMAINS"] = WAVE1_DOMAINS
    app.config["ALPHA_ENABLED_CROSS_DOMAIN_PAIR_PROFILES"] = LIVE_ALPHA_PAIRS
    app.config["ALPHA_ENABLE_TECHNICAL_BRIEF"] = technical_brief
    app.config["ALPHA_ENABLE_HISTORY"] = history
    app.config["ALPHA_ENABLE_INQUIRY_FEEDBACK"] = feedback
    app.config["ALPHA_HIDE_DOMAIN_CRUD"] = True
    app.config["ALPHA_REQUIRE_DATA_READINESS"] = True
    app.config["ALPHA_ENABLE_CALENDAR_SYNC"] = True
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    app.config["ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES"] = phase8
    app.config["PHASE8_ENABLED_PAIR_PROFILES"] = LIVE_ALPHA_PAIRS
    app.config["ENABLE_PHASE9_TIMELINE_INTELLIGENCE"] = phase9
    app.config["PHASE9_ENABLED_TIMELINE_PROFILES"] = None
    app.config["ENABLE_PHASE10_INQUIRY_HUMANIZATION"] = False


def _prime_csrf(client, token: str = "alpha-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def _create_user_with_tokens(email: str, *, timezone: str = "UTC"):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Private Alpha",
            timezone=timezone,
        )
    )
    return user, issue_tokens(user)


def _add_event(user_id: int, event_type: str, created_at: datetime) -> None:
    db.session.add(EventRecord(event_type=event_type, payload={"seed": True}, user_id=user_id, created_at=created_at))
    db.session.commit()


def test_private_alpha_registration_requires_invite_and_enforces_cap(app, client):
    _enable_private_alpha(app)

    without_invite = client.post(
        "/auth/register",
        json={
            "email": "alpha-one@example.com",
            "password": "secret123",
            "full_name": "Alpha One",
            "timezone": "UTC",
        },
    )
    assert without_invite.status_code == 403
    assert without_invite.get_json()["error"] == "invite_required"

    with app.app_context():
        _, invite_token = issue_private_alpha_invite("alpha-one@example.com")

    first = client.post(
        "/auth/register",
        json={
            "email": "alpha-one@example.com",
            "password": "secret123",
            "full_name": "Alpha One",
            "timezone": "UTC",
            "invite_token": invite_token,
        },
    )
    assert first.status_code == 200
    assert first.get_json()["ok"] is True

    app.config["ALPHA_MAX_USERS"] = 1
    with app.app_context():
        _, second_invite = issue_private_alpha_invite("alpha-two@example.com")

    capped = client.post(
        "/auth/register",
        json={
            "email": "alpha-two@example.com",
            "password": "secret123",
            "full_name": "Alpha Two",
            "timezone": "UTC",
            "invite_token": second_invite,
        },
    )
    assert capped.status_code == 403
    assert capped.get_json()["error"] == "alpha_user_cap_reached"


def test_private_alpha_invite_states_invalid_expired_and_already_used(app, client):
    _enable_private_alpha(app)

    invalid = client.post(
        "/auth/register",
        json={
            "email": "alpha-invalid@example.com",
            "password": "secret123",
            "full_name": "Alpha Invalid",
            "timezone": "UTC",
            "invite_token": "not-a-valid-token",
        },
    )
    assert invalid.status_code == 403
    assert invalid.get_json()["error"] == "invite_invalid"

    with app.app_context():
        expired_invite, expired_token = issue_private_alpha_invite("alpha-expired@example.com")
        expired_invite.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db.session.add(expired_invite)
        db.session.commit()

    expired = client.post(
        "/auth/register",
        json={
            "email": "alpha-expired@example.com",
            "password": "secret123",
            "full_name": "Alpha Expired",
            "timezone": "UTC",
            "invite_token": expired_token,
        },
    )
    assert expired.status_code == 403
    assert expired.get_json()["error"] == "invite_expired"

    with app.app_context():
        used_invite, used_token = issue_private_alpha_invite("alpha-used@example.com")
        used_invite.accepted_at = datetime.utcnow() - timedelta(minutes=1)
        db.session.add(used_invite)
        db.session.commit()

    used = client.post(
        "/auth/register",
        json={
            "email": "alpha-used@example.com",
            "password": "secret123",
            "full_name": "Alpha Used",
            "timezone": "UTC",
            "invite_token": used_token,
        },
    )
    assert used.status_code == 403
    assert used.get_json()["error"] == "invite_already_used"


def test_private_alpha_domain_and_readiness_gating(app, client):
    _enable_private_alpha(app)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-gating@example.com")

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="alpha-gating"))
    blocked_domain = client.post(
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
    assert blocked_domain.status_code == 403
    assert blocked_domain.get_json()["error"] == "alpha_domain_not_visible"

    not_ready = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did my habits change?",
            "domain": "habits",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert not_ready.status_code == 403
    assert not_ready.get_json()["error"] == "alpha_readiness_not_met"
    assert not_ready.get_json()["details"]["ready"] is False

    with app.app_context():
        _add_event(user.id, "habits.habit.logged", datetime(2026, 3, 10, 9, 0, 0))

    ready = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did my habits change?",
            "domain": "habits",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert ready.status_code == 201
    brief = ready.get_json()["latest_brief"]
    assert brief["humanized_brief"] is not None
    assert brief["humanized_brief"]["metadata"]["technical_view_available"] is True


def test_private_alpha_hidden_and_non_alpha_domains_are_blocked(app, client):
    _enable_private_alpha(app)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-domains-blocked@example.com")
        _add_event(user.id, "calendar.event.created", datetime(2026, 3, 10, 9, 0, 0))

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="alpha-domains-blocked"))
    for domain in ("finance", "journal", "health", "relationships"):
        response = client.post(
            "/api/v1/inquiries",
            json={
                "question": f"What changed in {domain}?",
                "domain": domain,
                "cross_domain": False,
                "timeframe_start": "2026-03-01",
                "timeframe_end": "2026-03-14",
                "as_of_ts": "2026-03-14T23:00:00",
            },
            headers=headers,
        )
        assert response.status_code == 403
        assert response.get_json()["error"] == "alpha_domain_not_visible"


def test_private_alpha_hidden_domain_page_bypasses_for_admin_session(app, client):
    _enable_private_alpha(app)
    with app.app_context():
        admin = create_user(
            UserCreateRequest(
                email="alpha-admin@example.com",
                password="secret123",
                full_name="Alpha Admin",
                timezone="UTC",
            )
        )
        admin_role = Role.query.filter_by(name="admin").one()
        admin.roles.append(admin_role)
        db.session.commit()

    login = client.post(
        "/auth/login",
        json={"email": "alpha-admin@example.com", "password": "secret123"},
    )
    assert login.status_code == 200

    allowed = client.get("/finance")
    assert allowed.status_code != 404


def test_private_alpha_surface_gate_allows_finance_when_visible(app, client):
    _enable_private_alpha(app)
    app.config["ALPHA_VISIBLE_DOMAINS"] = (*WAVE1_DOMAINS, "finance")

    with app.app_context():
        _, tokens = _create_user_with_tokens("alpha-finance-visible@example.com")

    response = client.get(
        "/api/finance/accounts?per_page=1",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code != 404


def test_private_alpha_surface_gate_does_not_break_unblocked_api_paths(app, client):
    _enable_private_alpha(app)
    response = client.get("/api/habits")
    # Gate should allow this path through; auth then returns 401 for missing token.
    assert response.status_code == 401


def test_private_alpha_healthcheck_endpoint_remains_available(app, client):
    _enable_private_alpha(app)
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["ok"] is True
    assert payload.get("build_id")


def test_private_alpha_cross_domain_pair_gating(app, client):
    _enable_private_alpha(app)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-pairs@example.com")
        _add_event(user.id, "projects.task.completed", datetime(2026, 3, 10, 9, 0, 0))
        _add_event(user.id, "skills.practice.logged", datetime(2026, 3, 11, 9, 0, 0))
        _add_event(user.id, "calendar.event.created", datetime(2026, 3, 12, 9, 0, 0))

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="alpha-pairs"))
    blocked_pair = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did calendar and skills align?",
            "domains": ["calendar", "skills"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert blocked_pair.status_code == 403
    assert blocked_pair.get_json()["error"] == "alpha_pair_not_enabled"

    live_pair = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did projects and skills align?",
            "domains": ["projects", "skills"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert live_pair.status_code == 201
    assert live_pair.get_json()["latest_brief"]["domains"] == ["projects", "skills"]

    live_projects_calendar = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did projects and calendar align?",
            "domains": ["projects", "calendar"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert live_projects_calendar.status_code == 201
    assert sorted(live_projects_calendar.get_json()["latest_brief"]["domains"]) == ["calendar", "projects"]


def test_private_alpha_readiness_endpoint_guidance_and_ready_state(app, client):
    _enable_private_alpha(app)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-readiness-endpoint@example.com")

    auth_headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    not_ready = client.get("/api/v1/inquiries/readiness", headers=auth_headers)
    assert not_ready.status_code == 200
    payload = not_ready.get_json()["readiness"]
    assert payload["ready"] is False
    assert payload["blocking_reason"] == "alpha_readiness_not_met"
    assert "add recent records" in payload["next_step"].lower()

    with app.app_context():
        recent_event_ts = datetime.utcnow() - timedelta(days=1)
        _add_event(user.id, "projects.task.completed", recent_event_ts)

    ready = client.get("/api/v1/inquiries/readiness", headers=auth_headers)
    assert ready.status_code == 200
    ready_payload = ready.get_json()["readiness"]
    assert ready_payload["ready"] is True
    assert ready_payload["blocking_reason"] is None
    assert ready_payload["next_step"] is None


def test_private_alpha_history_and_refine_flow(app, client):
    _enable_private_alpha(app, history=True)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-history@example.com")
        _add_event(user.id, "projects.task.completed", datetime(2026, 3, 10, 9, 0, 0))

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="alpha-history"))
    created = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What changed in projects?",
            "domain": "projects",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert created.status_code == 201
    inquiry_id = created.get_json()["inquiry_id"]

    history = client.get("/api/v1/inquiries", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert history.status_code == 200
    assert history.get_json()["total"] == 1

    refined = client.post(
        f"/api/v1/inquiries/{inquiry_id}/refine",
        json={"question": "What changed in project completion?"},
        headers=headers,
    )
    assert refined.status_code == 200
    assert refined.get_json()["version_number"] == 2

    detail = client.get(
        f"/api/v1/inquiries/{inquiry_id}", headers={"Authorization": f"Bearer {tokens['access_token']}"}
    )
    assert detail.status_code == 200
    assert len(detail.get_json()["inquiry"]["versions"]) == 2

    app.config["ALPHA_ENABLE_HISTORY"] = False
    blocked_history = client.get("/api/v1/inquiries", headers={"Authorization": f"Bearer {tokens['access_token']}"})
    assert blocked_history.status_code == 404
    assert blocked_history.get_json()["error"] == "alpha_history_disabled"


def test_private_alpha_feedback_links_to_inquiry_version(app, client):
    _enable_private_alpha(app, feedback=True)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-feedback@example.com")
        _add_event(user.id, "calendar.event.created", datetime(2026, 3, 10, 9, 0, 0))

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="alpha-feedback"))
    created = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What changed in calendar commitments?",
            "domain": "calendar",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert created.status_code == 201
    body = created.get_json()
    inquiry_id = body["inquiry_id"]
    version_id = body["version_id"]
    brief_hash = body["latest_brief"]["humanized_brief"]["metadata"]["canonical_brief_hash"]
    humanization_version = body["latest_brief"]["humanized_brief"]["metadata"]["humanization_version"]

    feedback = client.post(
        f"/api/v1/inquiries/{inquiry_id}/feedback",
        json={
            "version_id": version_id,
            "feedback_type": "helpful",
            "surface": "humanized",
            "note": "Clear and grounded.",
        },
        headers=headers,
    )
    assert feedback.status_code == 201

    deduped = client.post(
        f"/api/v1/inquiries/{inquiry_id}/feedback",
        json={
            "version_id": version_id,
            "feedback_type": "helpful",
            "surface": "humanized",
            "note": "Clear and grounded.",
        },
        headers=headers,
    )
    assert deduped.status_code == 200
    assert deduped.get_json()["deduped"] is True

    with app.app_context():
        stored = UserFeedbackEvent.query.filter_by(user_id=user.id, feedback_type="helpful").one()
        assert stored.inquiry_id == inquiry_id
        assert stored.inquiry_version_id == version_id
        assert stored.payload["inquiry_id"] == inquiry_id
        assert stored.payload["version_id"] == version_id
        assert stored.payload["canonical_brief_hash"] == brief_hash
        assert stored.payload["humanization_version"] == humanization_version
        event = EventRecord.query.filter_by(user_id=user.id, event_type="inquiry.feedback.submitted").one()
        assert event.payload["feedback_type"] == "helpful"
        assert event.payload["version_id"] == version_id


def test_private_alpha_feedback_persistence_failure_is_retryable(app, client, monkeypatch):
    _enable_private_alpha(app, feedback=True)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-feedback-retry@example.com")
        _add_event(user.id, "projects.task.completed", datetime(2026, 3, 10, 9, 0, 0))

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="alpha-feedback-retry"))
    created = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What changed in projects?",
            "domain": "projects",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert created.status_code == 201
    inquiry_id = created.get_json()["inquiry_id"]
    version_id = created.get_json()["version_id"]

    def _boom():
        raise RuntimeError("commit failed")

    monkeypatch.setattr("lifeos.core.insights.inquiry_api_v1.db.session.commit", _boom)
    failed = client.post(
        f"/api/v1/inquiries/{inquiry_id}/feedback",
        json={"version_id": version_id, "feedback_type": "unclear", "surface": "humanized"},
        headers=headers,
    )
    assert failed.status_code == 503
    body = failed.get_json()
    assert body["error"] == "feedback_retryable_failure"
    assert body["retryable"] is True


def test_private_alpha_humanization_failure_falls_back_to_canonical(app, client, monkeypatch):
    _enable_private_alpha(app)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-fallback-humanization@example.com")
        _add_event(user.id, "skills.practice.logged", datetime(2026, 3, 10, 9, 0, 0))

    monkeypatch.setattr(
        "lifeos.core.insights.inquiry_service.humanize_inquiry_brief",
        lambda request: (_ for _ in ()).throw(RuntimeError("boom")),
    )
    headers = _headers(tokens["access_token"], _prime_csrf(client, token="alpha-humanization-fallback"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What changed in skills?",
            "domain": "skills",
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


def test_private_alpha_timeline_failure_falls_back_to_non_temporal_output(app, client, monkeypatch):
    _enable_private_alpha(app, phase9=True)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-fallback-timeline@example.com")
        now = datetime(2026, 3, 14, 9, 0, 0)
        _add_event(user.id, "habits.habit.logged", now - timedelta(days=7))
        _add_event(user.id, "habits.habit.logged", now - timedelta(days=1))

    monkeypatch.setattr(
        "lifeos.core.insights.inquiry_service.assemble_timeline_summary",
        lambda request: (_ for _ in ()).throw(RuntimeError("timeline down")),
    )
    headers = _headers(tokens["access_token"], _prime_csrf(client, token="alpha-timeline-fallback"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Did my habits pattern persist?",
            "domain": "habits",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    assert brief["timeline_metadata"] is None
    assert brief["findings"]


def test_private_alpha_technical_brief_flag_updates_humanized_metadata(app, client):
    _enable_private_alpha(app, technical_brief=False)
    with app.app_context():
        user, tokens = _create_user_with_tokens("alpha-technical-flag@example.com")
        _add_event(user.id, "calendar.event.created", datetime(2026, 3, 10, 9, 0, 0))

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="alpha-technical-flag"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "What changed in calendar commitments?",
            "domain": "calendar",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-14",
            "as_of_ts": "2026-03-14T23:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    humanized = response.get_json()["latest_brief"]["humanized_brief"]
    assert humanized is not None
    assert humanized["metadata"]["technical_view_available"] is False
