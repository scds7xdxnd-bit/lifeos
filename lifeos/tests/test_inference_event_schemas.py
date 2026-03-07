"""Smoke tests for ML inference event schemas."""

from __future__ import annotations

from lifeos.core.insights.ml.event_schemas import (
    FinanceTransactionInferenceEvent,
    HabitsHabitInferenceEvent,
    HealthMealInferenceEvent,
    HealthWorkoutInferenceEvent,
    ProjectsWorkSessionInferenceEvent,
    RelationshipsInteractionInferenceEvent,
    SkillsPracticeInferenceEvent,
)


def test_finance_transaction_inference_payload_aliases():
    evt = FinanceTransactionInferenceEvent(
        user_id=1,
        calendar_event_id=99,
        transaction_id=123,
        confidence=0.9,
        status="inferred",
        model_version="finance-ranker-v1",
        inferred={"amount": 42.5, "description": "Coffee", "currency": "USD"},
        is_false_positive=True,
    )
    payload = evt.to_payload()
    assert payload["event_name"] == "finance.transaction.inferred"
    assert payload["payload_version"] == "v1"
    assert payload["status"] == "inferred"
    assert payload["is_false_positive"] is True
    assert payload["confidence_score"] == 0.9
    assert payload["inferred_structure"]["amount"] == 42.5
    assert payload["inferred_structure"]["currency"] == "USD"


def test_health_meal_inference_payload():
    evt = HealthMealInferenceEvent(
        user_id="user-1",
        calendar_event_id="cal-1",
        confidence=0.76,
        status="inferred",
        inferred={
            "meal_type": "lunch",
            "items": ["salad", "water"],
            "calories_est": 450,
        },
    )
    payload = evt.to_payload()
    assert payload["event_name"] == "health.meal.inferred"
    assert payload["status"] == "inferred"
    assert payload["confidence_score"] == 0.76
    assert payload["inferred_structure"]["meal_type"] == "lunch"
    assert payload["inferred_structure"]["items"] == ["salad", "water"]


def test_health_workout_inference_payload():
    evt = HealthWorkoutInferenceEvent(
        user_id=2,
        calendar_event_id=5,
        confidence=0.82,
        inferred={
            "workout_type": "run",
            "duration_minutes": 30,
            "intensity": "moderate",
        },
    )
    payload = evt.to_payload()
    assert payload["event_name"] == "health.workout.inferred"
    assert payload["inferred_structure"]["workout_type"] == "run"
    assert payload["inferred_structure"]["duration_minutes"] == 30


def test_habits_inference_payload():
    evt = HabitsHabitInferenceEvent(
        user_id=3,
        calendar_event_id=7,
        confidence=0.7,
        inferred={"habit_name": "reading", "value": 20, "unit": "minutes"},
    )
    payload = evt.to_payload()
    assert payload["event_name"] == "habits.habit.inferred"
    assert payload["inferred_structure"]["habit_name"] == "reading"


def test_skills_inference_payload():
    evt = SkillsPracticeInferenceEvent(
        user_id=4,
        calendar_event_id=8,
        confidence=0.88,
        inferred={"skill_name": "piano", "duration_minutes": 45, "intensity": 6},
    )
    payload = evt.to_payload()
    assert payload["event_name"] == "skills.practice.inferred"
    assert payload["inferred_structure"]["skill_name"] == "piano"
    assert payload["inferred_structure"]["duration_minutes"] == 45


def test_projects_inference_payload():
    evt = ProjectsWorkSessionInferenceEvent(
        user_id=5,
        calendar_event_id=10,
        confidence=0.66,
        inferred={
            "project_name": "Roadmap",
            "task_name": "Write RFC",
            "duration_minutes": 60,
        },
    )
    payload = evt.to_payload()
    assert payload["event_name"] == "projects.work_session.inferred"
    assert payload["inferred_structure"]["project_name"] == "Roadmap"
    assert payload["inferred_structure"]["task_name"] == "Write RFC"


def test_relationships_inference_payload():
    evt = RelationshipsInteractionInferenceEvent(
        user_id=6,
        calendar_event_id=12,
        confidence=0.73,
        inferred={
            "person_name": "Alex",
            "interaction_type": "call",
            "method": "phone",
            "sentiment": "positive",
        },
    )
    payload = evt.to_payload()
    assert payload["event_name"] == "relationships.interaction.inferred"
    assert payload["inferred_structure"]["person_name"] == "Alex"
    assert payload["inferred_structure"]["interaction_type"] == "call"
