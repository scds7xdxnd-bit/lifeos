"""ML Phase 3a replay contract checks."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lifeos.core.events.semantic_contracts import EVENT_SEMANTIC_CONTRACTS
from lifeos.core.insights.ml.replay_contracts import GOLD_REPLAY_DATASETS

pytestmark = pytest.mark.unit


def test_gold_replay_dataset_spec_matches_file():
    spec = GOLD_REPLAY_DATASETS["gold_replay_dataset_v1"]
    dataset_path = Path(spec.dataset_path)
    if not dataset_path.is_absolute():
        dataset_path = Path(__file__).resolve().parents[2] / dataset_path
    assert dataset_path.exists()

    payload = json.loads(dataset_path.read_text())
    event_types = {evt.get("event_type") for evt in payload.get("events", [])}
    expected_insights = set(payload.get("expected_insights", []))

    assert event_types == set(spec.event_types)
    assert expected_insights == set(spec.expected_insight_types)


def test_gold_replay_dataset_events_are_semantically_contracted():
    spec = GOLD_REPLAY_DATASETS["gold_replay_dataset_v1"]
    missing = {evt for evt in spec.event_types if evt not in EVENT_SEMANTIC_CONTRACTS}
    assert missing == set()
