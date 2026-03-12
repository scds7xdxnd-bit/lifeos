"""Phase 3a replay determinism tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from lifeos.core.insights.replay import ReplayEvent, replay_insights

pytestmark = pytest.mark.unit


def test_replay_is_deterministic():
    dataset_path = Path(__file__).resolve().parent / "data" / "gold_replay_dataset_v1.json"
    payload = json.loads(dataset_path.read_text())
    events = [
        ReplayEvent(
            event_type=item["event_type"],
            payload=item.get("payload") or {},
            user_id=item.get("user_id"),
        )
        for item in payload["events"]
    ]
    expected_types = payload["expected_insights"]

    first = replay_insights(events, include_cross_rules=False)
    second = replay_insights(events, include_cross_rules=False)

    assert [ins["type"] for ins in first] == expected_types
    assert first == second
