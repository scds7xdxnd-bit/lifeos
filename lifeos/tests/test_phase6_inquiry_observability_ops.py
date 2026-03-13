"""Phase 6 focused inquiry ops observability checks."""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

import pytest

from lifeos import create_app
from lifeos.core.auth.auth_service import issue_tokens
from lifeos.core.events.event_models import EventRecord
from lifeos.core.observability.metrics import (
    record_timeline_blocked_claims,
    record_timeline_generated,
    record_timeline_replay_mismatch,
)
from lifeos.core.users.schemas import UserCreateRequest
from lifeos.core.users.services import create_user
from lifeos.extensions import db

pytestmark = pytest.mark.unit


REQUIRED_METRICS = [
    "lifeos_inquiry_created_total",
    "lifeos_inquiry_generated_total",
    "lifeos_inquiry_generated_by_domain_total",
    "lifeos_inquiry_viewed_total",
    "lifeos_inquiry_refined_total",
    "lifeos_inquiry_refined_by_domain_total",
    "lifeos_inquiry_generation_latency_seconds_bucket",
    "lifeos_inquiry_generation_latency_seconds_by_domain_bucket",
    "lifeos_inquiry_errors_total",
    "lifeos_inquiry_errors_by_domain_total",
    "lifeos_inquiry_empty_brief_total",
    "lifeos_inquiry_empty_brief_by_domain_total",
    "lifeos_inquiry_findings_by_domain_total",
    "lifeos_inquiry_findings_with_evidence_by_domain_total",
    "lifeos_inquiry_low_coverage_total",
    "lifeos_inquiry_low_coverage_by_domain_total",
    "lifeos_inquiry_refine_after_low_quality_total",
    "lifeos_inquiry_refine_after_low_quality_by_domain_total",
    "lifeos_inquiry_refine_after_low_coverage_total",
    "lifeos_inquiry_refine_after_low_coverage_by_domain_total",
    "lifeos_inquiry_quality_state_total",
    "lifeos_inquiry_quality_state_by_domain_total",
    "lifeos_inquiry_evidence_coverage_ratio",
    "lifeos_inquiry_blocked_claims_total",
    "lifeos_inquiry_blocked_claims_by_domain_total",
    "lifeos_inquiry_replay_mismatch_total",
    "lifeos_inquiry_replay_mismatch_by_domain_total",
    "lifeos_inquiry_productization_total",
    "lifeos_inquiry_productization_by_domain_total",
    "lifeos_inquiry_productization_latency_seconds_bucket",
    "lifeos_inquiry_productization_latency_seconds_by_domain_bucket",
    "lifeos_inquiry_productization_errors_total",
    "lifeos_inquiry_productization_errors_by_domain_total",
    "lifeos_inquiry_direct_answer_present_total",
    "lifeos_inquiry_direct_answer_present_by_domain_total",
    "lifeos_inquiry_answerability_total",
    "lifeos_inquiry_answerability_by_domain_total",
    "lifeos_inquiry_limitation_redundancy_removed_total",
    "lifeos_inquiry_limitation_redundancy_removed_by_domain_total",
    "lifeos_phase6_inquiry_migration_mismatch",
]


def _metric_value(payload: str, metric_name: str) -> float | None:
    match = re.search(rf"^{metric_name}(?:\{{[^}}]*\}})?\s+([0-9.eE+-]+)$", payload, re.M)
    return float(match.group(1)) if match else None


def _metric_sum(payload: str, metric_name: str) -> float:
    values = re.findall(rf"^{metric_name}(?:\{{[^}}]*\}})?\s+([0-9.eE+-]+)$", payload, re.M)
    return sum(float(item) for item in values)


def _metric_value_for_label(payload: str, metric_name: str, label_name: str, label_value: str) -> float | None:
    match = re.search(
        rf'^{metric_name}\{{[^}}]*{label_name}="{re.escape(label_value)}"[^}}]*\}}\s+([0-9.eE+-]+)$',
        payload,
        re.M,
    )
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
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_generated_by_domain_total", "domain", "finance") or 0.0
    ) >= 1.0
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_refined_by_domain_total", "domain", "finance") or 0.0
    ) >= 1.0
    assert (_metric_value(payload, "lifeos_inquiry_productization_total") or 0.0) >= 2.0
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_productization_by_domain_total", "domain", "finance") or 0.0
    ) >= 1.0
    productization_hist_count = _metric_value(payload, "lifeos_inquiry_productization_latency_seconds_count")
    assert productization_hist_count is not None
    assert productization_hist_count >= 2.0
    productization_hist_count_by_domain = _metric_value_for_label(
        payload,
        "lifeos_inquiry_productization_latency_seconds_by_domain_count",
        "domain",
        "finance",
    )
    assert productization_hist_count_by_domain is not None
    assert productization_hist_count_by_domain >= 2.0
    assert (_metric_value(payload, "lifeos_inquiry_direct_answer_present_total") or 0.0) >= 2.0
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_direct_answer_present_by_domain_total", "domain", "finance")
        or 0.0
    ) >= 1.0
    assert (_metric_sum(payload, "lifeos_inquiry_answerability_total") or 0.0) >= 2.0
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_answerability_by_domain_total", "domain", "finance") or 0.0
    ) >= 1.0
    assert (_metric_value(payload, "lifeos_inquiry_limitation_redundancy_removed_total") or 0.0) >= 0.0

    generation_hist_count = _metric_value(payload, "lifeos_inquiry_generation_latency_seconds_count")
    assert generation_hist_count is not None
    assert generation_hist_count >= 2.0
    generation_hist_count_by_domain = _metric_value_for_label(
        payload,
        "lifeos_inquiry_generation_latency_seconds_by_domain_count",
        "domain",
        "finance",
    )
    assert generation_hist_count_by_domain is not None
    assert generation_hist_count_by_domain >= 2.0

    evidence_ratio = _metric_value(payload, "lifeos_inquiry_evidence_coverage_ratio")
    assert evidence_ratio is not None
    assert 0.0 <= evidence_ratio <= 1.0


def test_phase61_refine_after_low_quality_metric_increments(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase61-ops@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 18.2},
                user_id=user.id,
                created_at=datetime(2026, 3, 3, 12, 0, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase61-ops-csrf"))
    create_resp = client.post(
        "/api/v1/inquiries",
        json={
            "question": "Compare finance and health for this week.",
            "domains": ["finance", "health"],
            "cross_domain": True,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-10",
            "as_of_ts": "2026-03-10T00:00:00",
        },
        headers=headers,
    )
    assert create_resp.status_code == 201
    inquiry_id = create_resp.get_json()["inquiry_id"]

    refine_resp = client.post(
        f"/api/v1/inquiries/{inquiry_id}/refine",
        json={"context_text": "narrow quality-check scope"},
        headers=headers,
    )
    assert refine_resp.status_code == 200

    payload = client.get("/metrics").get_data(as_text=True)
    assert (_metric_value(payload, "lifeos_inquiry_refined_total") or 0.0) >= 1.0
    assert (_metric_value(payload, "lifeos_inquiry_refine_after_low_quality_total") or 0.0) >= 1.0
    assert _metric_value(payload, "lifeos_inquiry_refine_after_low_coverage_total") is not None
    assert (
        _metric_value_for_label(
            payload,
            "lifeos_inquiry_refine_after_low_quality_by_domain_total",
            "domain",
            "cross_domain",
        )
        or 0.0
    ) >= 1.0
    assert "lifeos_inquiry_refine_after_low_coverage_by_domain_total" in payload
    assert _metric_sum(payload, "lifeos_inquiry_quality_state_total") >= 1.0
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_quality_state_by_domain_total", "domain", "cross_domain")
        or 0.0
    ) >= 1.0


def test_phase9_timeline_metrics_increment_when_enabled(app, client):
    labels = {
        "domain": "finance",
        "profile": "finance_timeline_v1",
        "profile_version": "1.0.0",
        "strategy": "phase9_timeline_v1",
        "strategy_version": "1.0.0",
        "expert_mode": True,
    }
    record_timeline_generated(
        latency_seconds=0.12,
        insufficiency_count=1,
        baseline_windows_available=2,
        **labels,
    )
    record_timeline_blocked_claims(1, **labels)
    record_timeline_replay_mismatch(**labels)

    payload = client.get("/metrics").get_data(as_text=True)
    assert (_metric_value_for_label(payload, "lifeos_timeline_profile_usage_total", "domain", "finance") or 0.0) >= 1.0
    timeline_latency_count = _metric_value_for_label(
        payload,
        "lifeos_timeline_generation_latency_seconds_count",
        "domain",
        "finance",
    )
    assert timeline_latency_count is not None
    assert timeline_latency_count >= 1.0
    baseline_count = _metric_value_for_label(
        payload,
        "lifeos_timeline_baseline_coverage_windows_count",
        "domain",
        "finance",
    )
    assert baseline_count is not None
    assert baseline_count >= 1.0
    assert (_metric_value_for_label(payload, "lifeos_timeline_insufficiency_total", "domain", "finance") or 0.0) >= 1.0
    assert (_metric_value_for_label(payload, "lifeos_timeline_blocked_claims_total", "domain", "finance") or 0.0) >= 1.0
    assert (
        _metric_value_for_label(payload, "lifeos_timeline_replay_mismatch_total", "domain", "finance") or 0.0
    ) >= 1.0


def test_production_defaults_keep_phase6_inquiry_disabled(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    app = create_app("production")
    rules = {rule.rule for rule in app.url_map.iter_rules()}
    assert "/api/v1/inquiries" not in rules
    assert "/api/v1/inquiries/" not in rules
    assert app.config["ENABLE_PHASE6_FOCUSED_INQUIRY"] is False


def test_phase7_domain_profile_labels_emit_for_expert_briefs(app, client):
    with app.app_context():
        user, tokens = _user_tokens("phase7-ops@example.com")
        db.session.add(
            EventRecord(
                event_type="finance.transaction.created",
                payload={"amount": 99.5},
                user_id=user.id,
                created_at=datetime(2026, 3, 5, 8, 30, 0),
            )
        )
        db.session.commit()

    headers = _headers(tokens["access_token"], _prime_csrf(client, token="phase7-ops-csrf"))
    response = client.post(
        "/api/v1/inquiries",
        json={
            "question": "How strong is finance signal quality this week?",
            "domain": "finance",
            "cross_domain": False,
            "timeframe_start": "2026-03-01",
            "timeframe_end": "2026-03-12",
            "as_of_ts": "2026-03-12T00:00:00",
        },
        headers=headers,
    )
    assert response.status_code == 201

    payload = client.get("/metrics").get_data(as_text=True)
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_generated_by_domain_total", "domain", "finance") or 0.0
    ) >= 1.0
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_generated_by_domain_total", "profile_version", "1.0.0") or 0.0
    ) >= 1.0
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_generated_by_domain_total", "strategy_version", "1.0.0") or 0.0
    ) >= 1.0
    assert (
        _metric_value_for_label(payload, "lifeos_inquiry_generated_by_domain_total", "expert_mode", "true") or 0.0
    ) >= 1.0


def test_phase7_alert_rule_coverage_exists():
    rules_path = (
        Path(__file__).resolve().parents[1] / ".." / "deploy" / "monitoring" / "phase6-inquiry-alerts.yml"
    ).resolve()
    payload = rules_path.read_text(encoding="utf-8")
    required_tokens = (
        "lifeos:inquiry_error_rate_by_domain_profile:ratio",
        "lifeos:inquiry_empty_brief_rate_by_domain_profile:ratio",
        "lifeos:inquiry_low_coverage_rate_by_domain_profile:ratio",
        "lifeos:inquiry_refine_after_low_quality_rate_by_domain_profile:ratio",
        "lifeos:inquiry_refine_after_low_coverage_rate_by_domain_profile:ratio",
        "lifeos:inquiry_generation_latency_p95_by_domain_profile:seconds",
        "lifeos:inquiry_direct_answer_presence_rate:ratio",
        "lifeos:inquiry_direct_answer_presence_rate_by_domain_profile:ratio",
        "lifeos:inquiry_answerability_distribution:ratio",
        "lifeos:inquiry_answerability_distribution_by_domain_profile:ratio",
        "lifeos:inquiry_weak_answer_rate:ratio",
        "lifeos:inquiry_weak_answer_rate_by_domain_profile:ratio",
        "lifeos:inquiry_limitation_redundancy_rate:ratio",
        "lifeos:inquiry_limitation_redundancy_rate_by_domain_profile:ratio",
        "lifeos:inquiry_refine_after_weak_answer_lift:ratio",
        "lifeos:inquiry_refine_after_weak_answer_lift_by_domain_profile:ratio",
        "lifeos:inquiry_productization_latency_p95:seconds",
        "lifeos:inquiry_productization_latency_p95_by_domain_profile:seconds",
        "lifeos:inquiry_productization_error_rate:ratio",
        "lifeos:inquiry_productization_error_rate_by_domain_profile:ratio",
        "lifeos:inquiry_productization_replay_mismatch_count",
        "lifeos:inquiry_productization_replay_mismatch_count_by_domain_profile",
        "lifeos:timeline_profile_usage_rate_by_profile:per_second",
        "lifeos:timeline_generation_latency_p95_by_profile:seconds",
        "lifeos:timeline_error_rate_by_profile:ratio",
        "lifeos:timeline_insufficiency_rate_by_profile:ratio",
        "lifeos:timeline_baseline_coverage_avg_windows_by_profile",
        "lifeos:timeline_baseline_coverage_distribution_by_profile:ratio",
        "lifeos:timeline_blocked_claims_rate_by_profile:ratio",
        "lifeos:timeline_replay_mismatch_count_by_profile",
        "lifeos:timeline_replay_mismatch_rate_by_profile:ratio",
        "lifeos:timeline_output_presence_rate:ratio",
        "lifeos:timeline_output_presence_rate_by_domain:ratio",
        "Phase7DomainInquiryErrorRateHigh",
        "Phase7DomainInquiryLatencyHigh",
        "Phase7DomainInquiryEmptyBriefHigh",
        "Phase7DomainInquiryLowCoverageHigh",
        "Phase7DomainRefineAfterLowQualityHigh",
        "Phase7DomainProfileVersionUnexpected",
        "Phase71LaterWaveInquiryErrorRateHigh",
        "Phase71LaterWaveInquiryLatencyHigh",
        "Phase71LaterWaveInquiryEmptyBriefHigh",
        "Phase71LaterWaveInquiryLowCoverageHigh",
        "Phase71LaterWaveRefineAfterLowQualityHigh",
        "Phase71LaterWaveProfileVersionUnexpected",
        "Phase8CrossDomainPairErrorRateHigh",
        "Phase8CrossDomainPairLatencyHigh",
        "Phase8CrossDomainPairEmptyBriefHigh",
        "Phase8CrossDomainPairLowCoverageHigh",
        "Phase8CrossDomainPairRefineAfterLowCoverageHigh",
        "Phase8CrossDomainPairBlockedClaimsSpike",
        "Phase8CrossDomainPairReplayMismatchDetected",
        "Phase8CrossDomainPairProfileVersionUnexpected",
        "Phase81ProductizationErrorRateHigh",
        "Phase81ProductizationLatencyHigh",
        "Phase81WeakAnswerRateHigh",
        "Phase81DirectAnswerPresenceLow",
        "Phase81ProductizationReplayMismatchDetected",
        "Phase9TimelineGenerationLatencyHigh",
        "Phase9TimelineErrorRateHigh",
        "Phase9TimelineInsufficiencyRateHigh",
        "Phase9TimelineBlockedClaimsSpike",
        "Phase9TimelineReplayMismatchDetected",
        "Phase9TimelineOutputPresenceLow",
        "Phase9TimelineProfileVersionUnexpected",
        'domain=~"finance\\\\+habits|projects\\\\+skills|habits\\\\+journal|habits\\\\+health|calendar\\\\+projects|journal\\\\+relationships"',
        'domain=~"journal|relationships|health"',
        'domain=~"finance|habits|projects|skills|calendar|finance\\\\+habits|projects\\\\+skills|calendar\\\\+projects"',
        'phase: "8.1"',
        'phase: "9"',
    )
    for token in required_tokens:
        assert token in payload


def test_phase71_ops_runbook_exists_with_rollout_controls():
    runbook_path = (
        Path(__file__).resolve().parents[1] / "docs" / "ops" / "phase_7_1_later_wave_domain_expert_briefs_ops.md"
    )
    payload = runbook_path.read_text(encoding="utf-8")
    required_tokens = (
        "PHASE7_1_LATER_WAVE_ENABLED",
        "PHASE7_1_LATER_WAVE_DOMAINS",
        "PHASE7_1_EXPECT_PROFILE_VERSION",
        "PHASE7_1_EXPECT_STRATEGY_VERSION",
        "Phase71LaterWaveInquiryErrorRateHigh",
        "Phase71LaterWaveProfileVersionUnexpected",
    )
    for token in required_tokens:
        assert token in payload


def test_phase8_ops_runbook_exists_with_rollout_controls():
    runbook_path = (
        Path(__file__).resolve().parents[1] / "docs" / "ops" / "phase_8_cross_domain_inquiry_expansion_ops.md"
    )
    payload = runbook_path.read_text(encoding="utf-8")
    required_tokens = (
        "ENABLE_PHASE8_CROSS_DOMAIN_PAIR_PROFILES",
        "PHASE8_ENABLED_PAIR_PROFILES",
        "PHASE8_CROSS_DOMAIN_ENABLED",
        "PHASE8_PAIR_PROFILES",
        "PHASE8_EXPECT_PROFILE_VERSION",
        "PHASE8_EXPECT_STRATEGY_VERSION",
        "Phase8CrossDomainPairErrorRateHigh",
        "Phase8CrossDomainPairBlockedClaimsSpike",
        "Phase8CrossDomainPairReplayMismatchDetected",
    )
    for token in required_tokens:
        assert token in payload


def test_phase8_rollout_scripts_include_pair_controls():
    phase6_script = (
        Path(__file__).resolve().parents[1] / ".." / "scripts" / "ops" / "phase6_inquiry_rollout_check.sh"
    ).resolve()
    payload = phase6_script.read_text(encoding="utf-8")
    required_tokens = (
        "PHASE8_CROSS_DOMAIN_ENABLED",
        "PHASE8_PAIR_PROFILES",
        "PHASE8_EXPECT_PROFILE_VERSION",
        "PHASE8_EXPECT_STRATEGY_VERSION",
        "PHASE8_1_PRODUCTIZATION_ENABLED",
        "PHASE8_1_EXPECT_PRODUCTIZATION_VERSION",
        "PHASE8_1_CANARY_PROFILE",
        "PHASE8_1_CANARY_MIN_DIRECT_ANSWER_RATE",
        "PHASE8_1_CANARY_MAX_WEAK_RATE",
        "PHASE9_TIMELINE_ENABLED",
        "PHASE9_FIRST_WAVE_DOMAINS",
        "PHASE9_APPROVED_PAIR_DOMAINS",
        "PHASE9_EXPECTED_PROFILES",
        "PHASE9_EXPECT_PROFILE_VERSION",
        "PHASE9_EXPECT_STRATEGY_VERSION",
        "PHASE9_CANARY_DOMAIN",
        "PHASE9_CANARY_MAX_INSUFFICIENCY_RATE",
        "PHASE9_CANARY_MAX_LATENCY_P95",
        "PHASE9_CANARY_MAX_BLOCKED_CLAIMS_RATE",
        "PHASE9_CANARY_MAX_REPLAY_MISMATCH_COUNT",
        "lifeos_inquiry_blocked_claims_total",
        "lifeos_inquiry_replay_mismatch_total",
        "lifeos_inquiry_productization_total",
        "lifeos_inquiry_direct_answer_present_total",
        "lifeos_inquiry_answerability_total",
        "lifeos_inquiry_limitation_redundancy_removed_total",
        "lifeos:inquiry_replay_mismatch_rate_by_domain_profile:ratio",
        "lifeos:inquiry_direct_answer_presence_rate_by_domain_profile:ratio",
        "lifeos:inquiry_weak_answer_rate_by_domain_profile:ratio",
        "lifeos:inquiry_productization_error_rate_by_domain_profile:ratio",
        "lifeos:inquiry_productization_replay_mismatch_count_by_domain_profile",
        "lifeos_timeline_profile_usage_total",
        "lifeos_timeline_generation_latency_seconds_bucket",
        "lifeos_timeline_insufficiency_total",
        "lifeos_timeline_baseline_coverage_windows_bucket",
        "lifeos_timeline_blocked_claims_total",
        "lifeos_timeline_replay_mismatch_total",
        "lifeos:timeline_generation_latency_p95_by_profile:seconds",
        "lifeos:timeline_insufficiency_rate_by_profile:ratio",
        "lifeos:timeline_baseline_coverage_avg_windows_by_profile",
        "lifeos:timeline_blocked_claims_rate_by_profile:ratio",
        "lifeos:timeline_replay_mismatch_count_by_profile",
        "lifeos:timeline_output_presence_rate_by_domain:ratio",
    )
    for token in required_tokens:
        assert token in payload

    phase8_script = (
        Path(__file__).resolve().parents[1] / ".." / "scripts" / "ops" / "phase8_cross_domain_rollout_check.sh"
    ).resolve()
    phase8_payload = phase8_script.read_text(encoding="utf-8")
    assert "phase6_inquiry_rollout_check.sh" in phase8_payload

    phase81_script = (
        Path(__file__).resolve().parents[1]
        / ".."
        / "scripts"
        / "ops"
        / "phase8_1_inquiry_productization_rollout_check.sh"
    ).resolve()
    phase81_payload = phase81_script.read_text(encoding="utf-8")
    assert "PHASE8_1_PRODUCTIZATION_ENABLED" in phase81_payload
    assert "PHASE8_1_EXPECT_PRODUCTIZATION_VERSION" in phase81_payload
    assert "phase6_inquiry_rollout_check.sh" in phase81_payload

    phase9_script = (
        Path(__file__).resolve().parents[1] / ".." / "scripts" / "ops" / "phase9_timeline_rollout_check.sh"
    ).resolve()
    phase9_payload = phase9_script.read_text(encoding="utf-8")
    assert "PHASE9_TIMELINE_ENABLED" in phase9_payload
    assert "PHASE9_EXPECTED_PROFILES" in phase9_payload
    assert "phase6_inquiry_rollout_check.sh" in phase9_payload

    snapshot_script = (
        Path(__file__).resolve().parents[1] / ".." / "scripts" / "ops" / "phase8_1_inquiry_productization_snapshot.sh"
    ).resolve()
    snapshot_payload = snapshot_script.read_text(encoding="utf-8")
    assert "lifeos:inquiry_direct_answer_presence_rate:ratio" in snapshot_payload
    assert "lifeos:inquiry_weak_answer_rate:ratio" in snapshot_payload
    assert "lifeos:inquiry_productization_error_rate:ratio" in snapshot_payload

    phase9_snapshot_script = (
        Path(__file__).resolve().parents[1] / ".." / "scripts" / "ops" / "phase9_timeline_snapshot.sh"
    ).resolve()
    phase9_snapshot_payload = phase9_snapshot_script.read_text(encoding="utf-8")
    assert "lifeos:timeline_output_presence_rate:ratio" in phase9_snapshot_payload
    assert "lifeos:timeline_generation_latency_p95_by_profile:seconds" in phase9_snapshot_payload
    assert "lifeos:timeline_replay_mismatch_count_by_profile" in phase9_snapshot_payload


def test_phase81_ops_runbook_exists_with_rollout_controls():
    runbook_path = Path(__file__).resolve().parents[1] / "docs" / "ops" / "phase_8_1_inquiry_productization_ops.md"
    payload = runbook_path.read_text(encoding="utf-8")
    required_tokens = (
        "PHASE8_1_PRODUCTIZATION_ENABLED",
        "PHASE8_1_EXPECT_PRODUCTIZATION_VERSION",
        "PHASE8_1_CANARY_PROFILE",
        "PHASE8_1_CANARY_MIN_DIRECT_ANSWER_RATE",
        "PHASE8_1_CANARY_MAX_WEAK_RATE",
        "lifeos:inquiry_direct_answer_presence_rate:ratio",
        "lifeos:inquiry_weak_answer_rate:ratio",
        "lifeos:inquiry_productization_error_rate:ratio",
        "lifeos:inquiry_productization_replay_mismatch_count",
        "Phase81ProductizationErrorRateHigh",
        "Phase81ProductizationLatencyHigh",
        "Phase81WeakAnswerRateHigh",
        "Phase81DirectAnswerPresenceLow",
        "Phase81ProductizationReplayMismatchDetected",
    )
    for token in required_tokens:
        assert token in payload


def test_phase9_ops_runbook_exists_with_rollout_controls():
    runbook_path = (
        Path(__file__).resolve().parents[1] / "docs" / "ops" / "phase_9_timeline_intelligence_foundations_ops.md"
    )
    payload = runbook_path.read_text(encoding="utf-8")
    required_tokens = (
        "ENABLE_PHASE9_TIMELINE_INTELLIGENCE",
        "PHASE9_ENABLED_TIMELINE_PROFILES",
        "PHASE9_TIMELINE_ENABLED",
        "PHASE9_FIRST_WAVE_DOMAINS",
        "PHASE9_APPROVED_PAIR_DOMAINS",
        "PHASE9_EXPECTED_PROFILES",
        "PHASE9_EXPECT_PROFILE_VERSION",
        "PHASE9_EXPECT_STRATEGY_VERSION",
        "Phase9TimelineGenerationLatencyHigh",
        "Phase9TimelineErrorRateHigh",
        "Phase9TimelineInsufficiencyRateHigh",
        "Phase9TimelineBlockedClaimsSpike",
        "Phase9TimelineReplayMismatchDetected",
        "Phase9TimelineOutputPresenceLow",
        "Phase9TimelineProfileVersionUnexpected",
        "phase9_timeline_rollout_check.sh",
        "phase9_timeline_snapshot.sh",
    )
    for token in required_tokens:
        assert token in payload
