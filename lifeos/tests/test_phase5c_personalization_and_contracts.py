from __future__ import annotations

import os

import pytest

import lifeos.core.insights.ml as ml
from lifeos.core.insights.personalization import personalization_enabled, rank_insights


def test_personalization_enabled_from_env(monkeypatch):
    monkeypatch.setenv("PERSONALIZATION_ENABLED", "true")
    assert personalization_enabled(config=None) is True

    monkeypatch.setenv("PERSONALIZATION_ENABLED", "false")
    assert personalization_enabled(config=None) is False


@pytest.mark.integration
def test_personalization_enabled_from_app_config(app):
    app.config["PERSONALIZATION_ENABLED"] = True
    assert personalization_enabled(app.config) is True

    app.config["PERSONALIZATION_ENABLED"] = False
    assert personalization_enabled(app.config) is False


@pytest.mark.integration
def test_rank_insights_noop_order_preserved(app):
    candidates = [{"id": 1}, {"id": 2}, {"id": 3}]

    app.config["PERSONALIZATION_ENABLED"] = False
    assert rank_insights(user_id=11, candidates=candidates) == candidates

    app.config["PERSONALIZATION_ENABLED"] = True
    assert rank_insights(user_id=11, candidates=candidates) == candidates


def test_stability_contract_exports_and_registration():
    contract = ml.get_phase3b1_stability_contract()
    assert contract.name == "phase_3b_1_stability_patch"
    assert contract.required_invariants

    listed = list(ml.list_stability_contracts())
    assert listed
    assert listed[0].name == contract.name

    assert "get_phase3b1_stability_contract" in ml.__all__
    assert "list_stability_contracts" in ml.__all__


def test_stability_contract_env_does_not_require_runtime(monkeypatch):
    monkeypatch.delenv("PERSONALIZATION_ENABLED", raising=False)
    assert os.environ.get("PERSONALIZATION_ENABLED") is None
    assert personalization_enabled(config={"PERSONALIZATION_ENABLED": False}) is False
