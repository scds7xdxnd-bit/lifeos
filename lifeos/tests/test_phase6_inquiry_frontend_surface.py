"""Phase 6 focused inquiry frontend surface checks."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "lifeos" / "templates" / "insights" / "inquiry.html"
INSIGHTS_PATH = ROOT / "lifeos" / "templates" / "insights" / "index.html"
BASE_PATH = ROOT / "lifeos" / "templates" / "layouts" / "base.html"
LOGIN_PATH = ROOT / "lifeos" / "templates" / "auth" / "login.html"


@pytest.mark.unit
def test_inquiry_template_has_canonical_page_hierarchy():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "Focused Inquiry" in html
    assert "Inquiry Setup" in html
    assert "Generated Brief" in html
    assert "Inquiry History" in html


@pytest.mark.unit
def test_insights_surface_has_explicit_new_inquiry_entry():
    html = INSIGHTS_PATH.read_text(encoding="utf-8")
    assert 'href="/insights/inquiry"' in html
    assert "New Inquiry" in html


@pytest.mark.unit
def test_inquiry_setup_block_enforces_required_scope_and_context_rules():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert 'id="inquiry-question"' in html
    assert 'id="inquiry-primary-domain"' in html
    assert 'id="inquiry-cross-domain"' in html
    assert 'id="inquiry-cross-domain-pair"' in html
    assert 'id="inquiry-domain-multi"' in html
    assert 'id="inquiry-context-panel" class="inquiry-context-panel" style="display:none;"' in html
    assert "Context (not evidence)" in html
    assert "Generate Brief" in html


@pytest.mark.unit
def test_inquiry_brief_surface_renders_summary_evidence_uncertainty_next_questions():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert 'id="inquiry-summary"' in html
    assert 'id="inquiry-direct-answer"' in html
    assert 'id="inquiry-direct-answer-support"' in html
    assert 'id="inquiry-answerability-pill"' in html
    assert 'id="inquiry-answerability-reason"' in html
    assert 'id="inquiry-timeline-block"' in html
    assert 'id="inquiry-timeline-meta"' in html
    assert 'id="inquiry-timeline-coverage"' in html
    assert 'id="inquiry-timeline-sections"' in html
    assert 'id="inquiry-bounded-patterns"' in html
    assert 'id="inquiry-domain-profile-summary"' in html
    assert 'id="inquiry-domain-categories"' in html
    assert 'id="inquiry-domain-safety-caution"' in html
    assert 'id="inquiry-findings"' in html
    assert 'id="inquiry-uncertainty"' in html
    assert 'id="inquiry-limits-meta"' in html
    assert 'id="inquiry-refine-guidance"' in html
    assert 'id="inquiry-next-questions"' in html
    assert 'id="inquiry-context-render"' in html


@pytest.mark.unit
def test_inquiry_quality_block_renders_secondary_coverage_and_guidance_fields():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "Quality & Coverage (secondary)" in html
    assert 'id="inquiry-quality-summary"' in html
    assert 'id="inquiry-quality-coverage"' in html
    assert 'id="inquiry-quality-gaps"' in html
    assert 'id="inquiry-quality-sparse"' in html
    assert 'id="inquiry-quality-guidance"' in html
    assert "renderQualityMetadata" in html


@pytest.mark.unit
def test_inquiry_quality_weak_state_exposes_refine_affordance_without_chat_patterns():
    html = TEMPLATE_PATH.read_text(encoding="utf-8").lower()

    assert 'id="inquiry-quality-refine-btn"' in html
    assert "qualityrefinebtn.addeventlistener('click'" in html
    assert "hydrateformfrominquiry(state.selectedinquiry)" in html
    assert "conversation_id" not in html
    assert "assistant_reply" not in html


@pytest.mark.unit
def test_inquiry_domain_expert_rendering_patterns_are_present_for_first_wave_domains():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "Domain Profile" in html
    assert "DOMAIN_REFINE_HINTS" in html
    assert "isExpertDomainProfile" in html
    assert "APPROVED_CROSS_DOMAIN_PAIRS" in html
    assert "finding_category" in html
    assert "relevance_reason" in html
    assert "Why this evidence matters" in html
    assert "renderDomainProfile(brief)" in html
    assert "renderFindings(nonTemporalFindings, brief)" in html


@pytest.mark.unit
def test_inquiry_later_wave_domain_rendering_patterns_and_safety_copy_are_present():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "journal: {" in html
    assert "relationships: {" in html
    assert "health: {" in html
    assert "reflection_cadence" in html
    assert "interaction_cadence" in html
    assert "metric_coverage" in html
    assert "renderDomainSafety(brief, findings)" in html
    assert "does not infer intent, emotion, or quality judgments" in html
    assert "does not provide diagnosis, treatment, or clinical conclusions" in html
    assert "Observed alignment in recorded data across" in html
    assert "Based on recorded events within the selected timeframe. Not causal proof." in html


@pytest.mark.unit
def test_cross_domain_pair_mode_is_explicit_and_approved_pairs_are_listed():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "Approved domain pair profile" in html
    assert "finance_habits_v1" in html
    assert "projects_skills_v1" in html
    assert "journal_habits_v1" in html
    assert "health_habits_v1" in html
    assert "projects_calendar_v1" in html
    assert "relationships_journal_v1" in html


@pytest.mark.unit
def test_inquiry_timeline_surface_renders_bounded_phase9_sections_without_dashboard_shift():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "Timeline Findings" in html
    assert "Change over time" in html
    assert "Compared with prior window" in html
    assert "Recurring pattern" in html
    assert "Stability / instability" in html
    assert "Recent or sustained" in html
    assert "Active window:" in html
    assert "Compared with:" in html
    assert "Insufficient history for full temporal interpretation in this scope." in html
    assert "renderTimelineMetadata(brief, temporalFindings)" in html
    assert "timeline_context" in html
    assert "timeline_metadata" in html
    assert "kpi_tiles" not in html.lower()
    assert "chart_series" not in html.lower()


@pytest.mark.unit
def test_inquiry_timeline_scope_gates_match_first_wave_phase9_policy():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "TIMELINE_FIRST_WAVE_DOMAINS" in html
    assert "'finance'" in html
    assert "'habits'" in html
    assert "'projects'" in html
    assert "'skills'" in html
    assert "'calendar'" in html
    assert "TIMELINE_FIRST_WAVE_APPROVED_PAIR_KEYS" in html
    assert "'finance__habits'" in html
    assert "'projects__skills'" in html
    assert "'projects__calendar'" in html


@pytest.mark.unit
def test_inquiry_frontend_flow_wires_create_detail_list_and_refine_endpoints():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "fetch('/api/v1/inquiries?limit=20&offset=0'" in html
    assert "fetch(`/api/v1/inquiries/${inquiryId}`" in html
    assert "'/api/v1/inquiries'" in html
    assert "`/api/v1/inquiries/${state.refineInquiryId}/refine`" in html
    assert "method: 'POST'" in html


@pytest.mark.unit
def test_inquiry_template_exposes_empty_and_error_states():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "No brief generated yet." in html
    assert "No inquiries yet." in html
    assert "No evidence found for this inquiry scope" in html
    assert "Invalid inquiry" in html
    assert "Generation failure" in html


@pytest.mark.unit
def test_inquiry_template_avoids_chatbot_patterns_and_keeps_primary_action_clear():
    html = TEMPLATE_PATH.read_text(encoding="utf-8").lower()

    banned_tokens = {
        "chat transcript",
        "assistant_reply",
        "conversation_id",
        "chat_messages",
        "prompt",
        "chat bubble",
    }
    for token in banned_tokens:
        assert token not in html

    assert "generate brief" in html
    assert "context (not evidence)" in html
    assert "direct answer" in html
    assert "answerability status" in html
    assert "what this means" in html


@pytest.mark.unit
def test_inquiry_template_wires_productization_sections_without_confidence_drift():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert "renderDirectAnswer(brief)" in html
    assert "renderAnswerability(brief)" in html
    assert "renderBoundedPatterns(brief)" in html
    assert "renderProductizedRefineGuidance(brief)" in html
    assert "Strongly answerable" in html
    assert "Partially answerable" in html
    assert "Weakly answerable" in html
    assert "No refine guidance was generated for this scope." in html
    assert "Derived from evidence-bounded findings only." in html


@pytest.mark.unit
def test_private_alpha_inquiry_surface_exposes_readiness_and_feedback_controls():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert 'id="inquiry-readiness-status"' in html
    assert "fetch('/api/v1/inquiries/readiness'" in html
    assert 'id="inquiry-feedback-block"' in html
    assert 'data-feedback-type="helpful"' in html
    assert 'id="inquiry-feedback-note"' in html
    assert "submitFeedback" in html
    assert "/api/v1/inquiries/${state.selectedInquiry.id}/feedback" in html


@pytest.mark.unit
def test_private_alpha_shell_navigation_and_invite_token_flow_tokens_exist():
    base_html = BASE_PATH.read_text(encoding="utf-8")
    login_html = LOGIN_PATH.read_text(encoding="utf-8")

    assert "/insights/inquiry" in base_html
    assert "/insights/history" in base_html
    assert "/insights/data" in base_html
    assert "/insights/account-help" in base_html
    assert "Invite token" in login_html
    assert "invite_token" in login_html
    assert "Need help with invite or access?" in login_html
    assert "LOGIN_REDIRECT_PATH" in login_html


@pytest.mark.integration
def test_inquiry_page_route_renders(client):
    resp = client.get("/insights/inquiry")

    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Focused Inquiry" in body
    assert "Generate Brief" in body


@pytest.mark.integration
def test_private_alpha_support_pages_render(client):
    history = client.get("/insights/history")
    data = client.get("/insights/data")
    account_help = client.get("/insights/account-help")

    assert history.status_code == 200
    assert data.status_code == 200
    assert account_help.status_code == 200
    assert "Inquiry History" in history.get_data(as_text=True)
    assert "Data Readiness" in data.get_data(as_text=True)
    assert "Need help with readiness or setup?" in data.get_data(as_text=True)
    assert "Account / Help" in account_help.get_data(as_text=True)
    assert "Support Path" in account_help.get_data(as_text=True)


@pytest.mark.integration
def test_private_alpha_shell_hides_broad_domain_nav(client):
    app = client.application
    old_private_alpha = app.config.get("ENABLE_PRIVATE_ALPHA", False)
    old_hide_domain_crud = app.config.get("ALPHA_HIDE_DOMAIN_CRUD", False)
    app.config["ENABLE_PRIVATE_ALPHA"] = True
    app.config["ALPHA_HIDE_DOMAIN_CRUD"] = True
    try:
        response = client.get("/insights/inquiry")
    finally:
        app.config["ENABLE_PRIVATE_ALPHA"] = old_private_alpha
        app.config["ALPHA_HIDE_DOMAIN_CRUD"] = old_hide_domain_crud

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "/insights/inquiry" in html
    assert "/insights/history" in html
    assert "/insights/data" in html
    assert "/insights/account-help" in html
    assert "/finance/" not in html
    assert "/journal/" not in html
    assert "/health/" not in html
    assert "/relationships/" not in html
