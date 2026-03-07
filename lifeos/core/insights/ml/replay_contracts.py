"""Phase 3a ML replay structures (contracts only, no runtime logic)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass(frozen=True)
class ReplayDeterminismContract:
    """Defines determinism expectations for ML-relevant insight replay."""

    name: str
    description: str
    required_event_fields: List[str]
    required_insight_fields: List[str]
    payload_version_required: bool = True
    model_version_required: bool = True


@dataclass(frozen=True)
class GoldReplayDatasetSpec:
    """Describes a gold replay dataset used to validate determinism."""

    version: str
    dataset_path: str
    event_types: List[str]
    expected_insight_types: List[str]
    notes: Optional[str] = None


REPLAY_DETERMINISM_CONTRACTS: dict[str, ReplayDeterminismContract] = {
    "insight_replay_v1": ReplayDeterminismContract(
        name="insight_replay_v1",
        description="Insight replay must preserve semantic fields and confidence routing deterministically.",
        required_event_fields=[
            "event_type",
            "user_id",
            "payload",
            "created_at",
        ],
        required_insight_fields=[
            "insight_type",
            "message",
            "confidence_band",
            "routing",
            "source_event_type",
            "source_event_id",
        ],
    ),
}


GOLD_REPLAY_DATASETS: dict[str, GoldReplayDatasetSpec] = {
    "gold_replay_dataset_v1": GoldReplayDatasetSpec(
        version="v1",
        dataset_path="lifeos/tests/data/gold_replay_dataset_v1.json",
        event_types=[
            "finance.transaction.created",
            "finance.journal.posted",
            "habits.habit.logged",
            "health.metric.updated",
            "skills.practice.logged",
            "projects.task.completed",
        ],
        expected_insight_types=[
            "finance_spend",
            "journal_posted",
            "habit_progress",
            "health_metric",
            "skill_practice",
            "project_task_done",
        ],
        notes="Gold dataset used to validate replay determinism and confidence routing.",
    ),
}


def get_replay_determinism_contract(name: str) -> ReplayDeterminismContract | None:
    return REPLAY_DETERMINISM_CONTRACTS.get(name)


def list_replay_determinism_contracts() -> Iterable[ReplayDeterminismContract]:
    return REPLAY_DETERMINISM_CONTRACTS.values()


def get_gold_replay_dataset(name: str) -> GoldReplayDatasetSpec | None:
    return GOLD_REPLAY_DATASETS.get(name)


def list_gold_replay_datasets() -> Iterable[GoldReplayDatasetSpec]:
    return GOLD_REPLAY_DATASETS.values()


__all__ = [
    "ReplayDeterminismContract",
    "GoldReplayDatasetSpec",
    "REPLAY_DETERMINISM_CONTRACTS",
    "GOLD_REPLAY_DATASETS",
    "get_replay_determinism_contract",
    "list_replay_determinism_contracts",
    "get_gold_replay_dataset",
    "list_gold_replay_datasets",
]
