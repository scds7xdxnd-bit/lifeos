"""Phase 9 deterministic fixture matrix tests."""

from __future__ import annotations

import json
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.insights.contracts import CONFIDENCE_VOCABULARY
from lifeos.core.timeline.semantics import build_window_spec
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit

FIXTURE_PATH = Path(__file__).resolve().parent / "fixtures" / "phase9_timeline_fixture_matrix.json"
MATRIX = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

FORBIDDEN_TEMPORAL_CLAIM_TOKENS = (
    "because",
    "caused",
    "therefore",
    "will likely",
    "predict",
    "forecast",
    "recommend",
    "diagnosis",
    "pathology",
    "treatment",
)

FORBIDDEN_UI_KEYS = {
    "messages",
    "assistant_reply",
    "conversation",
    "dashboard_panels",
    "kpi_tiles",
    "chart_series",
}


def _enable_phase9(app) -> None:
    app.config["ENABLE_PHASE9_TIMELINE_INTELLIGENCE"] = True
    app.config["PHASE9_ENABLED_TIMELINE_PROFILES"] = None


def _user_tokens(email: str, *, timezone: str = "UTC"):
    user = create_user(
        UserCreateRequest(
            email=email,
            password="secret123",
            full_name="Phase 9 Matrix",
            timezone=timezone,
        )
    )
    return user, issue_tokens(user)


def _prime_csrf(client, token: str = "phase9-matrix-csrf") -> str:
    with client.session_transaction() as sess:
        sess["_csrf_token"] = token
    return token


def _headers(access_token: str, csrf_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}", "X-CSRF-Token": csrf_token}


def _seed_events(user_id: int, events: list[dict]) -> None:
    for row in events:
        db.session.add(
            EventRecord(
                event_type=row["event_type"],
                payload=dict(row["payload"]),
                user_id=user_id,
                created_at=datetime.fromisoformat(row["created_at"]),
            )
        )
    db.session.commit()


def _request_payload(case: dict) -> dict:
    return dict(case["request"])


def _assert_no_forbidden_temporal_language(brief: dict) -> None:
    findings_blob = " ".join(str(item.get("claim") or "") for item in list(brief.get("findings") or []))
    direct_answer = str((brief.get("direct_answer") or {}).get("text") or "")
    lowered = f"{findings_blob} {direct_answer}".lower()
    for token in FORBIDDEN_TEMPORAL_CLAIM_TOKENS:
        assert token not in lowered


def _assert_confidence_vocab(brief: dict) -> None:
    for finding in list(brief.get("findings") or []):
        assert finding.get("confidence_label") in CONFIDENCE_VOCABULARY


def _assert_non_chat_ui_shape(brief: dict) -> None:
    assert "summary" in brief
    assert "findings" in brief
    assert "context_non_evidence" in brief
    assert "timeline_metadata" in brief
    assert "direct_answer" in brief
    assert "answerability" in brief
    assert FORBIDDEN_UI_KEYS.isdisjoint(brief.keys())
    for finding in list(brief.get("findings") or []):
        if finding.get("timeline_context"):
            assert finding.get("evidence_refs")


@pytest.mark.parametrize("case", MATRIX["history_cases"], ids=[row["name"] for row in MATRIX["history_cases"]])
def test_phase9_history_fixture_matrix_cases(app, client, case: dict):
    _enable_phase9(app)
    with app.app_context():
        user, tokens = _user_tokens(f"{case['name']}@example.com", timezone=case["timezone"])
        _seed_events(user.id, list(case["events"]))

    headers = _headers(tokens["access_token"], _prime_csrf(client, token=f"phase9-{case['name']}"))
    response = client.post("/api/v1/inquiries", json=_request_payload(case), headers=headers)
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    metadata = brief["timeline_metadata"]
    assert metadata is not None
    assert metadata["timeline_profile_id"] == case["expects"]["timeline_profile_id"]
    assert metadata["timeline_profile_version"] == "1.0.0"
    assert metadata["window_spec_token"]
    assert metadata["baseline_policy_token"] == "fixed_prior_windows_v1:b3"
    assert metadata["timeline_summary_hash"]
    assert metadata["evidence_manifest_hash"]
    assert metadata["timezone_token"] == case["timezone"]
    assert int(metadata.get("insufficiency_count") or 0) >= int(case["expects"]["insufficiency_min"])

    categories = {str(item.get("finding_category") or "") for item in list(brief.get("findings") or [])}
    if case["expects"]["requires_recurrence"]:
        assert "recurrence_observation" in categories
    else:
        assert "recurrence_observation" not in categories

    assert brief["answerability"]["classification"] in set(case["expects"]["allows_answerability"])

    as_of_ts = datetime.fromisoformat(case["request"]["as_of_ts"])
    for finding in list(brief.get("findings") or []):
        for ref in list(finding.get("evidence_refs") or []):
            if ref.get("source_kind") != "event_record":
                continue
            created = ref.get("created_at")
            if not created:
                continue
            assert datetime.fromisoformat(str(created)) <= as_of_ts

    _assert_no_forbidden_temporal_language(brief)
    _assert_confidence_vocab(brief)
    _assert_non_chat_ui_shape(brief)


@pytest.mark.parametrize(
    "case",
    MATRIX["window_semantics_cases"],
    ids=[row["name"] for row in MATRIX["window_semantics_cases"]],
)
def test_phase9_window_semantics_fixture_matrix(case: dict):
    spec = build_window_spec(
        timeframe_start=datetime.fromisoformat(case["timeframe_start"]),
        timeframe_end=datetime.fromisoformat(case["timeframe_end"]),
        as_of_ts=datetime.fromisoformat(case["as_of_ts"]),
        timezone_token=case["timezone_token"],
        baseline_window_count=int(case["baseline_window_count"]),
    )
    assert spec.duration_days == int(case["expected_duration_days"])
    assert len(spec.baseline_windows) == int(case["baseline_window_count"])
    assert spec.active_window is not None
    assert spec.prior_window is not None
    active_days = (spec.active_window.end_local_date - spec.active_window.start_local_date).days
    prior_days = (spec.prior_window.end_local_date - spec.prior_window.start_local_date).days
    assert active_days == spec.duration_days
    assert prior_days == spec.duration_days
    for token in case["token_contains"]:
        assert token in spec.token
    for window in spec.baseline_windows:
        span = (window.end_local_date - window.start_local_date).days
        assert span == spec.duration_days
    as_of_date = datetime.fromisoformat(case["as_of_ts"]).date()
    assert spec.active_window.end_local_date <= as_of_date + timedelta(days=1)


@pytest.mark.parametrize("case", MATRIX["pair_cases"], ids=[row["name"] for row in MATRIX["pair_cases"]])
def test_phase9_approved_pair_temporal_persistence_matrix(app, client, case: dict):
    _enable_phase9(app)
    with app.app_context():
        user, tokens = _user_tokens(f"{case['name']}@example.com", timezone=case["timezone"])
        _seed_events(user.id, list(case["events"]))

    headers = _headers(tokens["access_token"], _prime_csrf(client, token=f"phase9-pair-{case['name']}"))
    response = client.post("/api/v1/inquiries", json=_request_payload(case), headers=headers)
    assert response.status_code == 201
    brief = response.get_json()["latest_brief"]
    metadata = brief["timeline_metadata"]
    assert metadata is not None
    assert metadata["timeline_profile_id"] == case["expects"]["timeline_profile_id"]
    required_domains = set(case["expects"]["required_domains"])

    temporal_findings = [
        finding
        for finding in list(brief.get("findings") or [])
        if finding.get("finding_category") == case["expects"]["required_category"] and finding.get("timeline_context")
    ]
    assert temporal_findings
    for finding in temporal_findings:
        assert set(finding.get("source_domains") or []) == required_domains
        refs = list(finding.get("evidence_refs") or [])
        ref_domains = {ref.get("domain") for ref in refs if ref.get("domain")}
        assert required_domains.issubset(ref_domains)

    _assert_no_forbidden_temporal_language(brief)
    _assert_confidence_vocab(brief)


def test_phase9_timezone_boundary_changes_replay_identity(app, client):
    _enable_phase9(app)
    with app.app_context():
        tokyo_user, tokyo_tokens = _user_tokens("phase9-timezone-tokyo@example.com", timezone="Asia/Tokyo")
        honolulu_user, honolulu_tokens = _user_tokens(
            "phase9-timezone-honolulu@example.com",
            timezone="Pacific/Honolulu",
        )
        seed = [
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 25, "occurred_at": "2026-03-01T00:30:00+00:00"},
                user_id=tokyo_user.id,
                created_at=datetime(2026, 3, 1, 0, 30, 0),
            ),
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 25, "occurred_at": "2026-03-01T00:30:00+00:00"},
                user_id=honolulu_user.id,
                created_at=datetime(2026, 3, 1, 0, 30, 0),
            ),
        ]
        db.session.add_all(seed)
        db.session.commit()

    payload = {
        "question": "How has finance changed over time?",
        "domain": "finance",
        "cross_domain": False,
        "timeframe_start": "2026-03-01",
        "timeframe_end": "2026-03-07",
        "as_of_ts": "2026-03-07T23:00:00",
    }
    tokyo_resp = client.post(
        "/api/v1/inquiries",
        json=payload,
        headers=_headers(tokyo_tokens["access_token"], _prime_csrf(client, token="phase9-tz-tokyo")),
    )
    honolulu_resp = client.post(
        "/api/v1/inquiries",
        json=payload,
        headers=_headers(honolulu_tokens["access_token"], _prime_csrf(client, token="phase9-tz-honolulu")),
    )
    assert tokyo_resp.status_code == 201
    assert honolulu_resp.status_code == 201
    tokyo = tokyo_resp.get_json()["latest_brief"]["timeline_metadata"]
    honolulu = honolulu_resp.get_json()["latest_brief"]["timeline_metadata"]
    assert tokyo["timezone_token"] == "Asia/Tokyo"
    assert honolulu["timezone_token"] == "Pacific/Honolulu"
    assert tokyo["window_spec_token"] != honolulu["window_spec_token"]
    assert tokyo["timeline_summary_hash"] != honolulu["timeline_summary_hash"]
