"""Lightweight DOM harness for finance toggle state transitions (Phase 3a.5)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "lifeos" / "templates" / "finance"


@dataclass
class PanelState:
    display: str
    display_mode: str


@dataclass
class ButtonState:
    text: str
    aria_expanded: str = "false"


def _html(path: str) -> str:
    return (TEMPLATE_ROOT / path).read_text(encoding="utf-8")


def _panel_state(html: str, panel_id: str, default_mode: str = "block") -> PanelState:
    match = re.search(rf'id="{panel_id}"[^>]*>', html)
    assert match, f"panel {panel_id} not found"
    tag = match.group(0)
    display_match = re.search(r"display:\s*([^;]+)", tag)
    display = display_match.group(1).strip() if display_match else "block"
    mode_match = re.search(r'data-display="([^"]+)"', tag)
    display_mode = mode_match.group(1) if mode_match else default_mode
    return PanelState(display=display, display_mode=display_mode)


def _toggle_texts(html: str, toggle_var: str) -> tuple[str, str]:
    line_pattern = re.compile(r"textContent\s*=\s*.*?\?\s*['\"]([^'\"]+)['\"]\s*:\s*['\"]([^'\"]+)['\"]")
    for line in html.splitlines():
        if f"{toggle_var}.textContent" not in line:
            continue
        match = line_pattern.search(line)
        if match:
            return match.group(1), match.group(2)
    raise AssertionError(f"toggle text update for {toggle_var} not found")


def _assert_aria_expanded_updates(html: str, toggle_var: str) -> None:
    if f"{toggle_var}.setAttribute('aria-expanded'" in html:
        return
    uses_toggle_panel = "togglePanel" in html and f"togglePanel({toggle_var}," in html
    has_toggle_panel_update = "btn.setAttribute('aria-expanded'" in html
    assert uses_toggle_panel and has_toggle_panel_update


def _simulate_toggle(panel: PanelState, button: ButtonState) -> None:
    is_open = panel.display != "none"
    panel.display = "none" if is_open else panel.display_mode
    button.aria_expanded = str(not is_open).lower()


def test_import_toggle_transition():
    html = _html("import.html")
    panel = _panel_state(html, "import-panel")
    button = ButtonState(text="Start import")
    closed_label, open_label = _toggle_texts(html, "toggleBtn")
    _assert_aria_expanded_updates(html, "toggleBtn")

    assert panel.display == "none"
    _simulate_toggle(panel, button)
    button.text = open_label
    assert panel.display == "block"
    assert button.aria_expanded == "true"
    assert button.text == "Hide form"

    _simulate_toggle(panel, button)
    button.text = closed_label
    assert panel.display == "none"
    assert button.aria_expanded == "false"
    assert button.text == "Start import"


def test_receivables_create_toggle_transition():
    html = _html("receivables.html")
    panel = _panel_state(html, "recv-create-panel")
    button = ButtonState(text="New tracker")
    closed_label, open_label = _toggle_texts(html, "createToggle")
    _assert_aria_expanded_updates(html, "createToggle")

    assert panel.display == "none"
    _simulate_toggle(panel, button)
    button.text = open_label
    assert panel.display == "block"
    assert button.aria_expanded == "true"
    assert button.text == "Hide form"

    _simulate_toggle(panel, button)
    button.text = closed_label
    assert panel.display == "none"
    assert button.aria_expanded == "false"
    assert button.text == "New tracker"


def test_forecast_create_and_manage_toggle_transitions():
    html = _html("forecast.html")
    create_panel = _panel_state(html, "sched-create-panel")
    create_btn = ButtonState(text="New schedule")
    closed_label, open_label = _toggle_texts(html, "createToggle")
    _assert_aria_expanded_updates(html, "createToggle")

    assert create_panel.display == "none"
    _simulate_toggle(create_panel, create_btn)
    create_btn.text = open_label
    assert create_panel.display == "block"
    assert create_btn.aria_expanded == "true"
    assert create_btn.text == "Hide form"

    _simulate_toggle(create_panel, create_btn)
    create_btn.text = closed_label
    assert create_panel.display == "none"
    assert create_btn.aria_expanded == "false"
    assert create_btn.text == "New schedule"

    _assert_aria_expanded_updates(html, "manageToggle")
    assert "Done managing" in html
    assert "Manage rows" in html


def test_accounts_filter_and_category_toggle_transitions():
    html = _html("accounts.html")
    filter_panel = _panel_state(html, "acct-filter-panel", default_mode="flex")
    filter_btn = ButtonState(text="Filter")
    _assert_aria_expanded_updates(html, "acctFilterToggle")

    assert filter_panel.display == "none"
    _simulate_toggle(filter_panel, filter_btn)
    assert filter_panel.display == "flex"
    assert filter_btn.aria_expanded == "true"
    _simulate_toggle(filter_panel, filter_btn)
    assert filter_panel.display == "none"
    assert filter_btn.aria_expanded == "false"

    cat_panel = _panel_state(html, "cat-form-panel")
    cat_btn = ButtonState(text="Create category")
    closed_label, open_label = _toggle_texts(html, "catToggle")
    _assert_aria_expanded_updates(html, "catToggle")

    _simulate_toggle(cat_panel, cat_btn)
    cat_btn.text = open_label
    assert cat_panel.display == "block"
    assert cat_btn.text == "Hide form"
    _simulate_toggle(cat_panel, cat_btn)
    cat_btn.text = closed_label
    assert cat_panel.display == "none"
    assert cat_btn.text == "Create category"


def test_trial_balance_toggle_panels_use_aria_expanded():
    html = _html("trial_balance.html")
    for toggle_var in ("filterToggle", "catToggle", "periodToggle", "monthlyToggle"):
        _assert_aria_expanded_updates(html, toggle_var)
