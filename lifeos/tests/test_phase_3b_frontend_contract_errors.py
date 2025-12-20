"""Phase 3b frontend contract error surfacing checks."""

from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

ROOT = Path(__file__).resolve().parents[2]


def _read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def _assert_contract_resolver(html: str) -> None:
    assert "resolveContractError" in html
    assert "read_only_violation" in html
    assert "contract_mismatch" in html
    assert "schema_mismatch" in html
    assert "Contract mismatch detected" in html
    assert "Read-only contract violation detected" in html


def test_insights_review_queue_contract_errors():
    html = _read("lifeos/templates/insights/index.html")
    _assert_contract_resolver(html)
    assert "/api/v1/insights/review" in html


def test_calendar_views_contract_errors():
    html = _read("lifeos/templates/calendar/index.html")
    _assert_contract_resolver(html)
    assert "resolveContractError(data, res)" in html


@pytest.mark.parametrize(
    "template_path",
    [
        "lifeos/templates/finance/journal.html",
        "lifeos/templates/finance/trial_balance.html",
        "lifeos/templates/finance/receivables.html",
        "lifeos/templates/finance/forecast.html",
    ],
)
def test_finance_read_surfaces_contract_errors(template_path: str):
    html = _read(template_path)
    _assert_contract_resolver(html)
    assert "resolveContractError" in html
