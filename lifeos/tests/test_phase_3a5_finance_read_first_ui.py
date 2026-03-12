"""Phase 3a.5 finance read-first and intent-gated UI checks."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "lifeos" / "templates" / "finance"


def _html(path: str) -> str:
    return (TEMPLATE_ROOT / path).read_text(encoding="utf-8")


def _assert_hidden_panel(html: str, panel_id: str) -> None:
    assert re.search(rf'id="{panel_id}"[^>]*display:\s*none', html)


def test_accounts_read_first_and_gated_controls():
    html = _html("accounts.html")

    assert 'id="acct-review"' in html
    assert 'id="acct-filter-toggle"' in html
    assert 'id="acct-login-hint"' in html
    _assert_hidden_panel(html, "acct-filter-panel")
    _assert_hidden_panel(html, "cat-form-panel")

    assert "ensureAuth" in html
    assert "acctFilterPanel" in html
    assert "catFormPanel" in html
    assert "aria-expanded" in html


def test_trial_balance_read_first_toggles_and_gating():
    html = _html("trial_balance.html")

    assert 'id="tb-review"' in html
    assert 'id="tb-toggle-filters"' in html
    assert 'id="tb-period-toggle"' in html
    assert 'id="tb-monthly-toggle"' in html
    assert 'id="tb-cat-toggle"' in html
    assert 'id="tb-login-hint"' in html
    _assert_hidden_panel(html, "tb-filters")
    _assert_hidden_panel(html, "tb-period-controls")
    _assert_hidden_panel(html, "tb-monthly-controls")
    _assert_hidden_panel(html, "tb-cat-controls")

    assert "ensureAuth" in html
    assert "filterPanel" in html
    assert "periodPanel" in html
    assert "monthlyPanel" in html
    assert "catControls" in html


def test_receivables_intent_gated_forms_and_manage_controls():
    html = _html("receivables.html")

    assert 'id="recv-toggle-create"' in html
    assert 'id="recv-login-hint"' in html
    _assert_hidden_panel(html, "recv-create-panel")
    assert 'data-role="entry-form"' in html
    assert 'data-role="manage-only"' in html
    assert 'style="display:none; margin-top:0.75rem;"' in html

    assert "ensureAuth" in html
    assert "createPanel" in html
    assert "entry-form" in html
    assert "manage-only" in html


def test_forecast_intent_gated_schedule_and_horizon_controls():
    html = _html("forecast.html")

    assert 'id="sched-toggle-create"' in html
    assert 'id="sched-toggle-manage"' in html
    assert 'id="sched-login-hint"' in html
    _assert_hidden_panel(html, "sched-create-panel")
    _assert_hidden_panel(html, "forecast-controls")

    assert "ensureAuth" in html
    assert "createPanel" in html
    assert "manageToggle" in html
    assert "forecastControls" in html


def test_import_read_first_toggle_and_panel_gating():
    html = _html("import.html")

    assert 'id="import-toggle"' in html
    assert 'id="import-login-hint"' in html
    _assert_hidden_panel(html, "import-panel")

    assert "ensureAuth" in html
    assert "panel" in html
    assert "aria-expanded" in html


def test_dashboard_read_first_review_cta_and_login_gate():
    html = _html("dashboard.html")

    assert 'id="dash-review"' in html
    assert 'id="dash-login-hint"' in html
    assert "ensureAuth" in html


def test_transactions_routes_to_journal_review():
    html = _html("transactions.html")

    assert 'href="/finance/journal"' in html
    assert "Read-first view is now consolidated in Finance Journal." in html
