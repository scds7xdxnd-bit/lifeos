"""Canonical, versioned schemas for LifeOS ML inference events.

These Pydantic models define the emitted payloads for all cross-domain
`*.inferred` events. Producers should construct these models and emit
`model.to_payload()`; consumers should validate incoming payloads against the
same models instead of handling ad-hoc dictionaries.

False-positive/false-negative convention:
- Classification-style errors (e.g., predicted workout but user rejects) set `is_false_positive=True`.
- Structured/label corrections (e.g., model guessed category/record A, user corrected to B) set `is_false_negative=True`.
Both flags may be present if the prediction was wrong and user supplied the missing/correct target.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import AliasChoices, BaseModel, ConfigDict, Field


class _BaseInference(BaseModel):
    """Shared configuration for nested inference structures."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class TransactionInference(_BaseInference):
    """Structured transaction guess."""

    amount: Optional[float] = Field(default=None, description="Guessed amount (major units).")
    currency: Optional[str] = Field(default=None, description="ISO currency code if known (e.g., 'USD').")
    description: Optional[str] = Field(default=None, description="Normalized description or memo.")
    counterparty: Optional[str] = Field(default=None, description="Guessed counterparty/merchant.")
    category: Optional[str] = Field(default=None, description="Suggested category/label for reporting.")
    debit_account_id: Optional[int] = Field(default=None, description="Suggested debit account id.")
    credit_account_id: Optional[int] = Field(default=None, description="Suggested credit account id.")
    suggested_account_ids: Optional[List[int]] = Field(
        default=None,
        description="Ranked account candidates (IDs) for simplified posting flows.",
    )


class MealInference(_BaseInference):
    meal_type: Optional[str] = Field(default=None, description="Breakfast/lunch/dinner/snack.")
    items: Optional[List[str]] = Field(default=None, description="Free-text meal items or ingredients.")
    calories_est: Optional[float] = Field(default=None, description="Estimated calories (kcal).")
    macros: Optional[Dict[str, float]] = Field(default=None, description="Macro estimates keyed by protein/fat/carbs (grams).")


class WorkoutInference(_BaseInference):
    workout_type: Optional[str] = Field(default=None, description="Type (run, ride, lift, yoga, etc.).")
    duration_minutes: Optional[int] = Field(default=None, description="Duration in minutes.")
    intensity: Optional[str] = Field(default=None, description="Intensity bucket (easy/moderate/hard) or RPE string.")
    calories_est: Optional[float] = Field(default=None, description="Estimated calories (kcal).")


class HabitInference(_BaseInference):
    habit_name: Optional[str] = Field(default=None, description="Guessed habit name/title.")
    value: Optional[float] = Field(default=None, description="Numeric measurement for the habit (if applicable).")
    unit: Optional[str] = Field(default=None, description="Unit for value (e.g., minutes, pages, km).")
    note: Optional[str] = Field(default=None, description="Free-text note extracted from the source event.")
    logged_date: Optional[str] = Field(default=None, description="ISO date when the habit should be logged.")


class PracticeInference(_BaseInference):
    skill_name: Optional[str] = Field(default=None, description="Guessed skill/practice area.")
    duration_minutes: Optional[int] = Field(default=None, description="Duration in minutes.")
    intensity: Optional[int] = Field(default=None, description="Optional intensity/effort score (1-10).")
    notes: Optional[str] = Field(default=None, description="Free-text practice notes.")


class WorkSessionInference(_BaseInference):
    project_name: Optional[str] = Field(default=None, description="Guessed project name.")
    task_name: Optional[str] = Field(default=None, description="Guessed task or work item.")
    duration_minutes: Optional[int] = Field(default=None, description="Duration in minutes.")
    note: Optional[str] = Field(default=None, description="Notes or summary for the session.")


class InteractionInference(_BaseInference):
    person_name: Optional[str] = Field(default=None, description="Guessed contact/person involved.")
    interaction_type: Optional[str] = Field(default=None, description="Type (call, meeting, message, etc.).")
    method: Optional[str] = Field(default=None, description="Channel (phone, video, email, sms).")
    sentiment: Optional[str] = Field(default=None, description="Optional sentiment bucket.")
    notes: Optional[str] = Field(default=None, description="Notes or summary for the interaction.")


class InferenceEventBase(BaseModel):
    """Common fields for all ML inference events."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    event_name: str = Field(description="Fully-qualified event name, e.g., finance.transaction.inferred.")
    user_id: Union[int, str] = Field(description="User/tenant identifier.")
    status: Literal["inferred", "confirmed", "rejected", "ambiguous", "ignored"] = Field(
        default="inferred",
        description="Lifecycle status for the inference.",
    )
    payload_version: Union[str, int] = Field(
        default="v1",
        description="Schema payload version; bump when fields change (semantic or integer).",
    )
    model_version: Optional[str] = Field(default=None, description="Emitting model artifact/version hash.")
    is_false_positive: Optional[bool] = Field(
        default=None,
        description="True when the model predicted a class/entity that was later rejected or corrected.",
    )
    is_false_negative: Optional[bool] = Field(
        default=None,
        description="True when the model missed or mis-assigned the target and the user supplied the correct one.",
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        validation_alias=AliasChoices("confidence", "confidence_score"),
        serialization_alias="confidence_score",
        description="Top-level confidence in the inference (0-1).",
    )
    label_confidences: Optional[Dict[str, float]] = Field(
        default=None,
        description="Optional per-label confidences (0-1) keyed by label name.",
    )
    context: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Optional context (e.g., source model metadata, features, request ids).",
    )

    def to_payload(self) -> Dict[str, Any]:
        """Return a dict suitable for event emission."""
        return self.model_dump(by_alias=True, exclude_none=True)


class FinanceTransactionInferenceEvent(InferenceEventBase):
    event_name: Literal["finance.transaction.inferred"] = "finance.transaction.inferred"
    calendar_event_id: Union[int, str] = Field(
        description="Source calendar event id the transaction was inferred from.",
    )
    transaction_id: Optional[int] = Field(
        default=None,
        description="Created transaction id (if persisted).",
    )
    inferred: TransactionInference = Field(
        default_factory=TransactionInference,
        validation_alias=AliasChoices("inferred", "inferred_structure"),
        serialization_alias="inferred_structure",
        description="Structured transaction guess.",
    )


class HealthMealInferenceEvent(InferenceEventBase):
    event_name: Literal["health.meal.inferred"] = "health.meal.inferred"
    calendar_event_id: Union[int, str] = Field(description="Source calendar event id.")
    nutrition_id: Optional[int] = Field(default=None, description="Created nutrition log id (if persisted).")
    inferred: MealInference = Field(
        default_factory=MealInference,
        validation_alias=AliasChoices("inferred", "inferred_structure", "inferred_labels"),
        serialization_alias="inferred_structure",
        description="Meal classification and estimates.",
    )


class HealthWorkoutInferenceEvent(InferenceEventBase):
    event_name: Literal["health.workout.inferred"] = "health.workout.inferred"
    calendar_event_id: Union[int, str] = Field(description="Source calendar event id.")
    workout_id: Optional[int] = Field(default=None, description="Created workout id (if persisted).")
    inferred: WorkoutInference = Field(
        default_factory=WorkoutInference,
        validation_alias=AliasChoices("inferred", "inferred_structure", "inferred_labels"),
        serialization_alias="inferred_structure",
        description="Workout classification and estimates.",
    )


class HabitsHabitInferenceEvent(InferenceEventBase):
    event_name: Literal["habits.habit.inferred"] = "habits.habit.inferred"
    calendar_event_id: Union[int, str] = Field(description="Source calendar event id.")
    habit_id: Optional[int] = Field(default=None, description="Created habit id (if persisted).")
    log_id: Optional[int] = Field(default=None, description="Created habit log id (if persisted).")
    inferred: HabitInference = Field(
        default_factory=HabitInference,
        validation_alias=AliasChoices("inferred", "inferred_structure", "inferred_labels"),
        serialization_alias="inferred_structure",
        description="Habit classification and measured value.",
    )


class SkillsPracticeInferenceEvent(InferenceEventBase):
    event_name: Literal["skills.practice.inferred"] = "skills.practice.inferred"
    calendar_event_id: Union[int, str] = Field(description="Source calendar event id.")
    skill_id: Optional[int] = Field(default=None, description="Created skill id (if persisted).")
    session_id: Optional[int] = Field(default=None, description="Created practice session id (if persisted).")
    inferred: PracticeInference = Field(
        default_factory=PracticeInference,
        validation_alias=AliasChoices("inferred", "inferred_structure", "inferred_labels"),
        serialization_alias="inferred_structure",
        description="Practice classification and duration.",
    )


class ProjectsWorkSessionInferenceEvent(InferenceEventBase):
    event_name: Literal["projects.work_session.inferred"] = "projects.work_session.inferred"
    calendar_event_id: Union[int, str] = Field(description="Source calendar event id.")
    project_id: Optional[int] = Field(default=None, description="Mapped project id (if known).")
    task_id: Optional[int] = Field(default=None, description="Mapped task id (if known).")
    log_id: Optional[int] = Field(default=None, description="Created work session log id (if persisted).")
    inferred: WorkSessionInference = Field(
        default_factory=WorkSessionInference,
        validation_alias=AliasChoices("inferred", "inferred_structure", "inferred_labels"),
        serialization_alias="inferred_structure",
        description="Work session classification and duration.",
    )


class RelationshipsInteractionInferenceEvent(InferenceEventBase):
    event_name: Literal["relationships.interaction.inferred"] = "relationships.interaction.inferred"
    calendar_event_id: Union[int, str] = Field(description="Source calendar event id.")
    interaction_id: Optional[int] = Field(default=None, description="Created interaction id (if persisted).")
    person_id: Optional[int] = Field(default=None, description="Mapped person id (if known).")
    inferred: InteractionInference = Field(
        default_factory=InteractionInference,
        validation_alias=AliasChoices("inferred", "inferred_structure", "inferred_labels"),
        serialization_alias="inferred_structure",
        description="Interaction classification and notes.",
    )


INFERENCE_EVENT_MODELS = {
    "finance.transaction.inferred": FinanceTransactionInferenceEvent,
    "health.meal.inferred": HealthMealInferenceEvent,
    "health.workout.inferred": HealthWorkoutInferenceEvent,
    "habits.habit.inferred": HabitsHabitInferenceEvent,
    "skills.practice.inferred": SkillsPracticeInferenceEvent,
    "projects.work_session.inferred": ProjectsWorkSessionInferenceEvent,
    "relationships.interaction.inferred": RelationshipsInteractionInferenceEvent,
}

__all__ = [
    "InferenceEventBase",
    "FinanceTransactionInferenceEvent",
    "HealthMealInferenceEvent",
    "HealthWorkoutInferenceEvent",
    "HabitsHabitInferenceEvent",
    "SkillsPracticeInferenceEvent",
    "ProjectsWorkSessionInferenceEvent",
    "RelationshipsInteractionInferenceEvent",
    "INFERENCE_EVENT_MODELS",
    "TransactionInference",
    "MealInference",
    "WorkoutInference",
    "HabitInference",
    "PracticeInference",
    "WorkSessionInference",
    "InteractionInference",
]
