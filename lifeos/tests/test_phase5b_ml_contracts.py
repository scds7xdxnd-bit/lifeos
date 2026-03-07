"""Phase 5b ML contract alignment tests."""

from __future__ import annotations

import pytest

from lifeos.core.insights.ml.phase5b_contracts import alignment_report

pytestmark = pytest.mark.unit


def test_phase5b_ml_contract_alignment_report_is_clean():
    report = alignment_report()
    assert report["missing_feature_contracts"] == []
    assert report["extra_feature_contracts"] == []
    assert report["missing_insight_contracts"] == []
    assert report["extra_insight_contracts"] == []
    assert report["invalid_window_days"] == {}
    assert report["invalid_delivery_policies"] == {}
    assert report["invalid_severities"] == {}
