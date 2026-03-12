"""Phase 6 focused inquiry frontend surface checks."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "lifeos" / "templates" / "insights" / "inquiry.html"
INSIGHTS_PATH = ROOT / "lifeos" / "templates" / "insights" / "index.html"


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
    assert 'id="inquiry-domain-multi"' in html
    assert 'id="inquiry-context-panel" class="inquiry-context-panel" style="display:none;"' in html
    assert "Context (not evidence)" in html
    assert "Generate Brief" in html


@pytest.mark.unit
def test_inquiry_brief_surface_renders_summary_evidence_uncertainty_next_questions():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")

    assert 'id="inquiry-summary"' in html
    assert 'id="inquiry-findings"' in html
    assert 'id="inquiry-uncertainty"' in html
    assert 'id="inquiry-next-questions"' in html
    assert 'id="inquiry-context-render"' in html


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


@pytest.mark.integration
def test_inquiry_page_route_renders(client):
    resp = client.get("/insights/inquiry")

    assert resp.status_code == 200
    body = resp.get_data(as_text=True)
    assert "Focused Inquiry" in body
    assert "Generate Brief" in body
