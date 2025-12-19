"""QA guardrails for Calendar Event Creation UX in the calendar template."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

TEMPLATE_PATH = Path(__file__).resolve().parents[2] / "lifeos" / "templates" / "calendar" / "index.html"


def _template_html() -> str:
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def test_when_block_has_required_inputs():
    html = _template_html()

    assert 'id="cal-event-date"' in html
    assert 'id="cal-event-start-time"' in html
    assert 'label for="cal-event-date">When' in html

    assert re.search(r'<input[^>]*id="cal-event-date"[^>]*required', html)
    assert re.search(r'<input[^>]*id="cal-event-start-time"[^>]*required', html)
    assert re.search(r'id="cal-event-end-controls"[^>]*display:\s*none', html)
    assert 'id="cal-event-end-toggle"' in html
    assert 'id="cal-event-end-preview"' in html


def test_duration_presets_and_default_duration():
    html = _template_html()

    for duration in ("15", "30", "45", "60"):
        assert f'data-duration="{duration}"' in html
    assert "DEFAULT_DURATION_MINUTES = 60" in html
    assert 'id="cal-event-duration"' in html


def test_color_palette_has_ten_swatches_and_default_is_curated():
    html = _template_html()

    swatches = re.findall(r'class="cal-color-swatch"', html)
    assert len(swatches) == 10

    palette = {color.lower() for color in re.findall(r'data-color="(#[0-9a-fA-F]{6})"', html)}
    default_match = re.search(r'id="cal-event-color"[^>]*value="(#[0-9a-fA-F]{6})"', html)
    assert default_match
    assert default_match.group(1).lower() in palette


def test_advanced_section_is_hidden_and_contains_optional_fields():
    html = _template_html()

    assert 'id="cal-event-advanced-toggle"' in html
    assert re.search(r'id="cal-event-advanced"[^>]*display:\s*none', html)
    assert 'id="cal-event-location"' in html
    assert 'id="cal-event-description"' in html
    assert 'id="cal-event-tags"' in html
    assert 'id="cal-event-private"' in html


def test_locale_time_formatting_and_validation_are_present():
    html = _template_html()

    assert "toLocaleTimeString" in html
    assert "hour12: true" in html
    assert "TIME_STEP_MINUTES = 15" in html
    assert "End time must be after start time" in html
    assert 'id="cal-time-options"' in html
