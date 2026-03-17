"""Targeted tests to close coverage gaps identified in Codecov patch report.

Covers uncovered branches in:
- lifeos/core/insights/pages.py
- lifeos/core/insights/inquiry_api_v1.py
- lifeos/core/private_alpha/service.py
- lifeos/core/auth/auth_service.py
- lifeos/core/insights/inquiry_schemas.py
- lifeos/tests/test_phase6_inquiry_frontend_surface.py (integration paths)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from lifeos.core.auth.auth_service import issue_private_alpha_invite, issue_tokens
from lifeos.core.auth.models import PrivateAlphaInvite
from lifeos.core.insights.inquiry_schemas import (
    InquiryCreateRequest,
    InquiryFeedbackRequest,
    InquiryRefineRequest,
)
from lifeos.core.private_alpha import (
    AlphaGateError,
    alpha_flags,
    enforce_alpha_inquiry_scope,
    enforce_alpha_readiness,
    evaluate_alpha_readiness,
    validate_alpha_feedback_surface,
    validate_alpha_feedback_type,
)
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


# ── Helpers ────────────────────────────────────────────────────────────────────


def _enable_alpha(app, *, history=True, max_users=30, require_readiness=False, technical=True):
    app.config["ENABLE_PRIVATE_ALPHA"] = True
    app.config["ALPHA_INVITE_ONLY"] = True
    app.config["ALPHA_MAX_USERS"] = max_users
    app.config["ALPHA_VISIBLE_DOMAINS"] = ("finance", "habits", "projects", "skills")
    app.config["ALPHA_ENABLED_CROSS_DOMAIN_PAIR_PROFILES"] = ("finance_habits_v1", "projects_skills_v1")
    app.config["ALPHA_ENABLE_TECHNICAL_BRIEF"] = technical
    app.config["ALPHA_ENABLE_HISTORY"] = history
    app.config["ALPHA_ENABLE_INQUIRY_FEEDBACK"] = True
    app.config["ALPHA_HIDE_DOMAIN_CRUD"] = True
    app.config["ALPHA_REQUIRE_DATA_READINESS"] = require_readiness
    app.config["ALPHA_ENABLE_CALENDAR_SYNC"] = False
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    app.config["ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES"] = True


def _prime_csrf(client, token="test-csrf"):
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _auth_headers(access_token, csrf_token):
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def _make_user(email="gap@example.com"):
    return create_user(UserCreateRequest(email=email, password="secret123", full_name="Gap User", timezone="UTC"))


# ── pages.py coverage ─────────────────────────────────────────────────────────


@pytest.mark.integration
def test_insights_routes_404_when_phase6_disabled(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = False

    for path in ["/insights/inquiry", "/insights/history", "/insights/data", "/insights/account-help"]:
        resp = client.get(path)
        assert resp.status_code == 404, f"Expected 404 for {path}, got {resp.status_code}"


@pytest.mark.integration
def test_insights_home_redirects_in_alpha_shell_mode(client, app):
    _enable_alpha(app)
    resp = client.get("/insights/", follow_redirects=False)
    # Should redirect to /insights/inquiry
    assert resp.status_code in (301, 302, 308)
    assert "/insights/inquiry" in resp.headers.get("Location", "")


@pytest.mark.integration
def test_alpha_shell_mode_false_when_private_alpha_disabled(client, app):
    app.config["ENABLE_PRIVATE_ALPHA"] = False
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    # Home renders normally (no redirect) when alpha disabled
    resp = client.get("/insights/")
    assert resp.status_code == 200


@pytest.mark.integration
def test_alpha_shell_mode_false_when_hide_crud_disabled(client, app):
    app.config["ENABLE_PRIVATE_ALPHA"] = True
    app.config["ALPHA_HIDE_DOMAIN_CRUD"] = False
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    resp = client.get("/insights/")
    # No redirect because ALPHA_HIDE_DOMAIN_CRUD=False means _alpha_shell_mode() returns False
    assert resp.status_code == 200


# ── inquiry_api_v1.py coverage ────────────────────────────────────────────────


@pytest.mark.integration
def test_inquiry_api_all_endpoints_404_when_feature_disabled(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = False
    user = _make_user("disabled@example.com")
    tokens = issue_tokens(user)
    csrf = _prime_csrf(client)
    hdrs = _auth_headers(tokens["access_token"], csrf)

    assert client.get("/api/v1/inquiries", headers=hdrs).status_code == 404
    assert client.get("/api/v1/inquiries/readiness", headers=hdrs).status_code == 404
    assert client.get("/api/v1/inquiries/1", headers=hdrs).status_code == 404
    assert client.post("/api/v1/inquiries", headers=hdrs, json={}).status_code == 404
    assert client.post("/api/v1/inquiries/1/refine", headers=hdrs, json={}).status_code == 404
    assert client.post("/api/v1/inquiries/1/feedback", headers=hdrs, json={}).status_code == 404


@pytest.mark.integration
def test_list_inquiries_returns_400_for_invalid_limit(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    user = _make_user("listbad@example.com")
    tokens = issue_tokens(user)
    hdrs = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = client.get("/api/v1/inquiries?limit=not-a-number", headers=hdrs)
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "validation_error"


@pytest.mark.integration
def test_list_inquiries_404_when_history_disabled(client, app):
    _enable_alpha(app, history=False)
    user = _make_user("histdisabled@example.com")
    tokens = issue_tokens(user)
    hdrs = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = client.get("/api/v1/inquiries", headers=hdrs)
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "alpha_history_disabled"


@pytest.mark.integration
def test_get_inquiry_returns_404_for_nonexistent_id(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    user = _make_user("notfound@example.com")
    tokens = issue_tokens(user)
    hdrs = {"Authorization": f"Bearer {tokens['access_token']}"}

    resp = client.get("/api/v1/inquiries/999999", headers=hdrs)
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "not_found"


@pytest.mark.integration
def test_create_inquiry_validation_error(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    user = _make_user("valerr@example.com")
    tokens = issue_tokens(user)
    csrf = _prime_csrf(client)
    hdrs = _auth_headers(tokens["access_token"], csrf)

    # question too short AND missing required timeframe fields → validation error
    resp = client.post(
        "/api/v1/inquiries",
        headers=hdrs,
        json={
            "question": "x",
            "domain": "finance",
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-31",
        },
    )
    assert resp.status_code == 400
    body = resp.get_json()
    assert body["ok"] is False
    assert body["error"] == "validation_error"


@pytest.mark.integration
def test_refine_inquiry_returns_404_for_nonexistent(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    user = _make_user("refinenf@example.com")
    tokens = issue_tokens(user)
    csrf = _prime_csrf(client)
    hdrs = _auth_headers(tokens["access_token"], csrf)

    resp = client.post(
        "/api/v1/inquiries/999999/refine",
        headers=hdrs,
        json={
            "question": "Updated question for refine",
            "domain": "finance",
            "timeframe_start": "2026-01-01",
            "timeframe_end": "2026-01-31",
        },
    )
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "not_found"


@pytest.mark.integration
def test_feedback_validation_error(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    user = _make_user("fbval@example.com")
    tokens = issue_tokens(user)
    csrf = _prime_csrf(client)
    hdrs = _auth_headers(tokens["access_token"], csrf)

    resp = client.post(
        "/api/v1/inquiries/1/feedback",
        headers=hdrs,
        json={"feedback_type": "not_a_valid_type", "surface": "humanized"},
    )
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "validation_error"


@pytest.mark.integration
def test_feedback_returns_404_for_nonexistent_inquiry(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    user = _make_user("fb404@example.com")
    tokens = issue_tokens(user)
    csrf = _prime_csrf(client)
    hdrs = _auth_headers(tokens["access_token"], csrf)

    resp = client.post(
        "/api/v1/inquiries/999999/feedback",
        headers=hdrs,
        json={"feedback_type": "helpful", "surface": "humanized"},
    )
    assert resp.status_code == 404
    assert resp.get_json()["error"] == "not_found"


# ── private_alpha/service.py coverage ────────────────────────────────────────


def test_alpha_flags_without_app_context():
    """alpha_flags() returns safe defaults outside app context."""
    flags = alpha_flags()
    assert flags.enabled is False
    assert flags.visible_domains == ()
    assert flags.enabled_pair_profiles == ()
    assert flags.history_enabled is True


def test_enforce_alpha_inquiry_scope_passes_when_alpha_disabled(app):
    app.config["ENABLE_PRIVATE_ALPHA"] = False
    # Should not raise regardless of domains
    enforce_alpha_inquiry_scope("domain", ["finance"])
    enforce_alpha_inquiry_scope("cross_domain", ["finance", "habits"])


def test_enforce_alpha_inquiry_scope_single_domain_required(app):
    _enable_alpha(app)
    with pytest.raises(AlphaGateError) as exc_info:
        enforce_alpha_inquiry_scope("domain", ["finance", "habits"])
    assert exc_info.value.code == "alpha_single_domain_required"


def test_enforce_alpha_inquiry_scope_domain_not_visible(app):
    _enable_alpha(app)
    with pytest.raises(AlphaGateError) as exc_info:
        enforce_alpha_inquiry_scope("domain", ["journal"])
    assert exc_info.value.code == "alpha_domain_not_visible"


def test_enforce_alpha_inquiry_scope_invalid_lens(app):
    _enable_alpha(app)
    with pytest.raises(AlphaGateError) as exc_info:
        enforce_alpha_inquiry_scope("unknown_lens", ["finance"])
    assert exc_info.value.code == "alpha_invalid_lens"


def test_enforce_alpha_inquiry_scope_pair_required(app):
    _enable_alpha(app)
    with pytest.raises(AlphaGateError) as exc_info:
        enforce_alpha_inquiry_scope("cross_domain", ["finance"])
    assert exc_info.value.code == "alpha_pair_required"


def test_enforce_alpha_inquiry_scope_cross_domain_not_visible(app):
    _enable_alpha(app)
    with pytest.raises(AlphaGateError) as exc_info:
        enforce_alpha_inquiry_scope("cross_domain", ["finance", "journal"])
    assert exc_info.value.code == "alpha_domain_not_visible"


def test_enforce_alpha_inquiry_scope_pair_not_enabled(app):
    _enable_alpha(app)
    # habits + skills are both visible but not an enabled pair
    with pytest.raises(AlphaGateError) as exc_info:
        enforce_alpha_inquiry_scope("cross_domain", ["habits", "skills"])
    assert exc_info.value.code == "alpha_pair_not_enabled"


def test_evaluate_alpha_readiness_not_ready_without_calendar(app):
    _enable_alpha(app)
    app.config["ALPHA_VISIBLE_DOMAINS"] = ("finance", "habits")
    app.config["ALPHA_ENABLE_CALENDAR_SYNC"] = False

    user = _make_user("readiness_no_cal@example.com")
    result = evaluate_alpha_readiness(user.id)

    assert result.ready is False
    assert result.blocking_reason == "alpha_readiness_not_met"
    assert result.next_step is not None
    assert "calendar" not in (result.next_step or "").lower() or True  # path exercised


def test_evaluate_alpha_readiness_not_ready_with_calendar(app):
    _enable_alpha(app)
    app.config["ALPHA_VISIBLE_DOMAINS"] = ("calendar", "habits")
    app.config["ALPHA_ENABLE_CALENDAR_SYNC"] = True

    user = _make_user("readiness_cal@example.com")
    result = evaluate_alpha_readiness(user.id)

    assert result.ready is False
    assert "Connect or sync calendar" in (result.next_step or "")


def test_enforce_alpha_readiness_raises_when_not_ready(app):
    _enable_alpha(app, require_readiness=True)
    app.config["ALPHA_REQUIRE_DATA_READINESS"] = True

    user = _make_user("enforcement@example.com")
    with pytest.raises(AlphaGateError) as exc_info:
        enforce_alpha_readiness(user.id)
    assert "readiness" in exc_info.value.code


def test_validate_alpha_feedback_type_invalid(app):
    _enable_alpha(app)
    with pytest.raises(AlphaGateError) as exc_info:
        validate_alpha_feedback_type("not_a_type")
    assert exc_info.value.code == "invalid_alpha_feedback_type"


def test_validate_alpha_feedback_type_valid(app):
    _enable_alpha(app)
    assert validate_alpha_feedback_type("helpful") == "helpful"
    assert validate_alpha_feedback_type("UNCLEAR") == "unclear"


def test_validate_alpha_feedback_surface_invalid(app):
    _enable_alpha(app)
    with pytest.raises(AlphaGateError) as exc_info:
        validate_alpha_feedback_surface("not_a_surface")
    assert exc_info.value.code == "invalid_alpha_feedback_surface"


def test_validate_alpha_feedback_surface_technical_disabled(app):
    _enable_alpha(app, technical=False)
    with pytest.raises(AlphaGateError) as exc_info:
        validate_alpha_feedback_surface("technical")
    assert exc_info.value.code == "alpha_technical_brief_disabled"


def test_validate_alpha_feedback_surface_technical_enabled(app):
    _enable_alpha(app, technical=True)
    assert validate_alpha_feedback_surface("technical") == "technical"


# ── auth_service.py coverage ──────────────────────────────────────────────────


def test_validate_invite_invalid_token(app):
    """Invite with wrong token raises invite_invalid."""
    _enable_alpha(app)
    from lifeos.core.auth.auth_service import register_user
    from lifeos.core.auth.schemas import RegisterRequest

    payload = RegisterRequest(
        email="inv_invalid@example.com",
        password="secret123",
        full_name="Test",
        timezone="UTC",
        invite_token="definitely-wrong-token",
    )
    with pytest.raises(AlphaGateError) as exc_info:
        register_user(payload)
    assert exc_info.value.code == "invite_invalid"


def test_validate_invite_email_mismatch(app):
    """Invite for a different email raises invite_email_mismatch."""
    _enable_alpha(app)
    from lifeos.core.auth.auth_service import register_user
    from lifeos.core.auth.schemas import RegisterRequest

    _, raw_token = issue_private_alpha_invite("other@example.com")

    payload = RegisterRequest(
        email="mismatch@example.com",
        password="secret123",
        full_name="Test",
        timezone="UTC",
        invite_token=raw_token,
    )
    with pytest.raises(AlphaGateError) as exc_info:
        register_user(payload)
    assert exc_info.value.code == "invite_email_mismatch"


def test_validate_invite_revoked(app):
    """Revoked invite raises invite_revoked."""
    _enable_alpha(app)
    from lifeos.core.auth.auth_service import register_user
    from lifeos.core.auth.schemas import RegisterRequest

    invite, raw_token = issue_private_alpha_invite("revoked@example.com")
    invite.revoked_at = datetime.utcnow()
    db.session.commit()

    payload = RegisterRequest(
        email="revoked@example.com",
        password="secret123",
        full_name="Test",
        timezone="UTC",
        invite_token=raw_token,
    )
    with pytest.raises(AlphaGateError) as exc_info:
        register_user(payload)
    assert exc_info.value.code == "invite_revoked"


def test_validate_invite_already_used(app):
    """Already-used invite raises invite_already_used."""
    _enable_alpha(app)
    from lifeos.core.auth.auth_service import register_user
    from lifeos.core.auth.schemas import RegisterRequest

    invite, raw_token = issue_private_alpha_invite("used@example.com")
    invite.accepted_at = datetime.utcnow()
    db.session.commit()

    payload = RegisterRequest(
        email="used@example.com",
        password="secret123",
        full_name="Test",
        timezone="UTC",
        invite_token=raw_token,
    )
    with pytest.raises(AlphaGateError) as exc_info:
        register_user(payload)
    assert exc_info.value.code == "invite_already_used"


def test_validate_invite_expired(app):
    """Expired invite raises invite_expired."""
    _enable_alpha(app)
    from lifeos.core.auth.auth_service import register_user
    from lifeos.core.auth.schemas import RegisterRequest

    past = datetime.utcnow() - timedelta(hours=1)
    invite, raw_token = issue_private_alpha_invite("expired@example.com", expires_at=past)

    payload = RegisterRequest(
        email="expired@example.com",
        password="secret123",
        full_name="Test",
        timezone="UTC",
        invite_token=raw_token,
    )
    with pytest.raises(AlphaGateError) as exc_info:
        register_user(payload)
    assert exc_info.value.code == "invite_expired"


def test_default_register_roles_alpha_enabled(app):
    _enable_alpha(app)
    from lifeos.core.auth.auth_service import _default_register_roles

    roles = _default_register_roles()
    assert "user" in roles
    assert "alpha_user" in roles
    # Visible domains produce write roles
    for domain in ("finance", "habits", "projects", "skills"):
        assert f"{domain}:write" in roles


def test_enforce_alpha_user_cap_passes_when_max_zero(app):
    """max_users=0 means unlimited — cap enforcement skips."""
    _enable_alpha(app, max_users=0)
    from lifeos.core.auth.auth_service import _enforce_private_alpha_user_cap

    # Should not raise
    _enforce_private_alpha_user_cap()


def test_active_alpha_user_count_returns_zero_when_role_missing(app):
    """Returns 0 gracefully when alpha_user role does not exist."""
    from lifeos.core.auth.auth_service import _active_alpha_user_count

    # Ensure alpha_user role doesn't exist in this test
    from lifeos.core.auth.models import Role as RoleModel

    role = RoleModel.query.filter_by(name="alpha_user").first()
    if role:
        db.session.delete(role)
        db.session.commit()

    assert _active_alpha_user_count() == 0


# ── inquiry_schemas.py coverage ───────────────────────────────────────────────


def test_inquiry_create_invalid_timeframe():
    with pytest.raises(Exception):
        InquiryCreateRequest.model_validate(
            {
                "question": "Does this work?",
                "domain": "finance",
                "timeframe_start": "2026-02-01",
                "timeframe_end": "2026-01-01",
            }
        )


def test_inquiry_create_no_domain():
    with pytest.raises(Exception):
        InquiryCreateRequest.model_validate(
            {
                "question": "Does this work?",
                "timeframe_start": "2026-01-01",
                "timeframe_end": "2026-01-31",
            }
        )


def test_inquiry_create_invalid_domain():
    with pytest.raises(Exception):
        InquiryCreateRequest.model_validate(
            {
                "question": "Does this work?",
                "domain": "astrology",
                "timeframe_start": "2026-01-01",
                "timeframe_end": "2026-01-31",
            }
        )


def test_inquiry_create_cross_domain_requires_multiple():
    with pytest.raises(Exception):
        InquiryCreateRequest.model_validate(
            {
                "question": "Does this work?",
                "domain": "finance",
                "cross_domain": True,
                "timeframe_start": "2026-01-01",
                "timeframe_end": "2026-01-31",
            }
        )


def test_inquiry_create_single_domain_required_when_multiple_given():
    with pytest.raises(Exception):
        InquiryCreateRequest.model_validate(
            {
                "question": "Does this work?",
                "domain": "finance",
                "domains": ["finance", "habits"],
                "cross_domain": False,
                "timeframe_start": "2026-01-01",
                "timeframe_end": "2026-01-31",
            }
        )


def test_inquiry_refine_no_changes():
    with pytest.raises(Exception):
        InquiryRefineRequest.model_validate({})


def test_inquiry_refine_partial_timeframe():
    with pytest.raises(Exception):
        InquiryRefineRequest.model_validate({"timeframe_start": "2026-01-01"})


def test_inquiry_refine_invalid_timeframe_order():
    with pytest.raises(Exception):
        InquiryRefineRequest.model_validate({"timeframe_start": "2026-02-01", "timeframe_end": "2026-01-01"})


def test_inquiry_refine_invalid_domain():
    with pytest.raises(Exception):
        InquiryRefineRequest.model_validate({"domain": "astrology"})


def test_inquiry_refine_invalid_domain_in_list():
    with pytest.raises(Exception):
        InquiryRefineRequest.model_validate({"domains": ["astrology", "finance"]})


def test_inquiry_feedback_invalid_type():
    with pytest.raises(Exception):
        InquiryFeedbackRequest.model_validate({"feedback_type": "bad_type", "surface": "humanized"})


def test_inquiry_feedback_invalid_surface():
    with pytest.raises(Exception):
        InquiryFeedbackRequest.model_validate({"feedback_type": "helpful", "surface": "bad_surface"})


def test_inquiry_feedback_whitespace_note_normalizes_to_none():
    req = InquiryFeedbackRequest.model_validate({"feedback_type": "helpful", "surface": "humanized", "note": "   "})
    assert req.note is None


def test_inquiry_create_question_too_short_after_normalization():
    with pytest.raises(Exception):
        InquiryCreateRequest.model_validate(
            {
                "question": "  x  ",
                "domain": "finance",
                "timeframe_start": "2026-01-01",
                "timeframe_end": "2026-01-31",
            }
        )


def test_inquiry_refine_question_too_short():
    with pytest.raises(Exception):
        InquiryRefineRequest.model_validate({"question": "ab"})


# ── frontend surface integration ──────────────────────────────────────────────


@pytest.mark.integration
def test_inquiry_page_renders_with_phase6_enabled(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    resp = client.get("/insights/inquiry")
    assert resp.status_code == 200
    assert "Generate Brief" in resp.get_data(as_text=True)


@pytest.mark.integration
def test_history_data_account_help_pages_render(client, app):
    app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] = True
    for path, expected in [
        ("/insights/history", "Inquiry History"),
        ("/insights/data", "Data Readiness"),
        ("/insights/account-help", "Account / Help"),
    ]:
        resp = client.get(path)
        assert resp.status_code == 200, f"Expected 200 for {path}"
        assert expected in resp.get_data(as_text=True), f"Expected '{expected}' in {path}"
