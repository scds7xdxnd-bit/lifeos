"""Phase 3a.5 read-first UI checks for non-finance domain components."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

COMPONENT_ROOT = Path(__file__).resolve().parents[2] / "lifeos" / "templates" / "components"


def _html(path: str) -> str:
    return (COMPONENT_ROOT / path).read_text(encoding="utf-8")


def test_journal_entry_form_is_intent_gated():
    html = _html("journal_entry_form_v2.html")

    assert "Creation is intentional." in html
    assert 'id="{{ component_id }}-form-toggle"' in html
    assert re.search(r'id="{{ component_id }}-form"[^>]*display:\s*none', html)
    assert 'id="{{ component_id }}-login-hint"' in html
    assert "toggleBtn?.addEventListener('click'" in html
    assert "toggleBtn.textContent = isOpen ? 'New entry' : 'Hide entry form'" in html


def test_skills_dashboard_create_form_is_gated():
    html = _html("skills_dashboard.html")

    assert "Log practice only when intended." in html
    assert 'id="{{ component_id }}-create-toggle"' in html
    assert re.search(r'id="{{ component_id }}-create-form"[^>]*display:\s*none', html)
    assert 'id="{{ component_id }}-login-hint"' in html
    assert "createToggle?.addEventListener('click'" in html
    assert "createToggle.textContent = isOpen ? 'New skill' : 'Hide form'" in html


def test_relationships_dashboard_create_form_is_gated():
    html = _html("relationships_dashboard.html")

    assert "Reconnect cues are suggestions, not judgments." in html
    assert 'id="{{ component_id }}-create-toggle"' in html
    assert re.search(r'id="{{ component_id }}-create-form"[^>]*display:\s*none', html)
    assert 'id="{{ component_id }}-login-hint"' in html
    assert "createToggle?.addEventListener('click'" in html
    assert "createToggle.textContent = isOpen ? 'Add person' : 'Hide form'" in html
