"""Phase 10 UI contract checks for humanized default + technical accessibility."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
TEMPLATE_PATH = ROOT / "lifeos" / "templates" / "insights" / "inquiry.html"


@pytest.mark.unit
def test_phase10_ui_uses_humanized_brief_as_default_surface():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "humanized_brief" in html


@pytest.mark.unit
def test_phase10_ui_keeps_technical_brief_accessible_in_same_surface():
    html = TEMPLATE_PATH.read_text(encoding="utf-8")
    assert "Technical brief" in html
    assert "technical_view_available" in html


@pytest.mark.unit
def test_phase10_ui_remains_non_chat_and_read_first():
    html = TEMPLATE_PATH.read_text(encoding="utf-8").lower()
    assert "chat transcript" not in html
    assert "assistant_reply" not in html
    assert "conversation_id" not in html
    assert "summary" in html
    assert "evidence" in html
