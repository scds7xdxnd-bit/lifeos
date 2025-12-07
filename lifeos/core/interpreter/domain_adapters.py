"""Domain adapters for creating inferred records from calendar events."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from lifeos.core.interpreter.constants import (
    DOMAIN_FINANCE,
    DOMAIN_HABITS,
    DOMAIN_HEALTH,
    DOMAIN_PROJECTS,
    DOMAIN_RELATIONSHIPS,
    DOMAIN_SKILLS,
    RECORD_TYPE_HABIT_LOG,
    RECORD_TYPE_INTERACTION,
    RECORD_TYPE_MEAL,
    RECORD_TYPE_PRACTICE,
    RECORD_TYPE_TRANSACTION,
    RECORD_TYPE_WORK_SESSION,
    RECORD_TYPE_WORKOUT,
)


class DomainAdapter(ABC):
    """Base class for domain service adapters."""

    @abstractmethod
    def create_inferred_record(
        self,
        user_id: int,
        calendar_event_id: int,
        confidence_score: float,
        extracted_data: dict,
        event_start_time: datetime,
    ) -> Optional[int]:
        """
        Create an inferred record in the domain.
        
        Returns record ID or None if creation failed.
        """
        raise NotImplementedError


class FinanceTransactionAdapter(DomainAdapter):
    """Adapter for finance domain inferred transactions."""

    def create_inferred_record(
        self,
        user_id: int,
        calendar_event_id: int,
        confidence_score: float,
        extracted_data: dict,
        event_start_time: datetime,
    ) -> Optional[int]:
        from lifeos.domains.finance.services.inferred_service import (
            create_inferred_transaction,
        )

        return create_inferred_transaction(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            description=extracted_data.get("description"),
            amount=extracted_data.get("amount"),
            counterparty=extracted_data.get("counterparty"),
            occurred_at=event_start_time,
        )


class HealthMealAdapter(DomainAdapter):
    """Adapter for health meal logging."""

    def create_inferred_record(
        self,
        user_id: int,
        calendar_event_id: int,
        confidence_score: float,
        extracted_data: dict,
        event_start_time: datetime,
    ) -> Optional[int]:
        from lifeos.domains.health.services.inferred_service import (
            log_inferred_meal,
        )

        return log_inferred_meal(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            meal_type=extracted_data.get("meal_type"),
            items=extracted_data.get("items"),
            logged_at=event_start_time,
        )


class HealthWorkoutAdapter(DomainAdapter):
    """Adapter for health workout logging."""

    def create_inferred_record(
        self,
        user_id: int,
        calendar_event_id: int,
        confidence_score: float,
        extracted_data: dict,
        event_start_time: datetime,
    ) -> Optional[int]:
        from lifeos.domains.health.services.inferred_service import (
            log_inferred_workout,
        )

        return log_inferred_workout(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            workout_type=extracted_data.get("workout_type"),
            duration_minutes=extracted_data.get("duration_minutes"),
            intensity=extracted_data.get("intensity", "medium"),
            logged_at=event_start_time,
        )


class HabitsAdapter(DomainAdapter):
    """Adapter for habits logging."""

    def create_inferred_record(
        self,
        user_id: int,
        calendar_event_id: int,
        confidence_score: float,
        extracted_data: dict,
        event_start_time: datetime,
    ) -> Optional[int]:
        from lifeos.domains.habits.services.inferred_service import (
            log_inferred_habit,
        )

        return log_inferred_habit(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            habit_name=extracted_data.get("habit_name"),
            value=extracted_data.get("value"),
            note=extracted_data.get("note"),
            logged_date=event_start_time.date(),
        )


class SkillsAdapter(DomainAdapter):
    """Adapter for skills practice logging."""

    def create_inferred_record(
        self,
        user_id: int,
        calendar_event_id: int,
        confidence_score: float,
        extracted_data: dict,
        event_start_time: datetime,
    ) -> Optional[int]:
        from lifeos.domains.skills.services.inferred_service import (
            log_inferred_practice,
        )

        return log_inferred_practice(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            skill_name=extracted_data.get("skill_name"),
            duration_minutes=extracted_data.get("duration_minutes", 0),
            notes=extracted_data.get("notes"),
            practiced_at=event_start_time,
        )


class ProjectsAdapter(DomainAdapter):
    """Adapter for projects work session logging."""

    def create_inferred_record(
        self,
        user_id: int,
        calendar_event_id: int,
        confidence_score: float,
        extracted_data: dict,
        event_start_time: datetime,
    ) -> Optional[int]:
        from lifeos.domains.projects.services.inferred_service import (
            log_inferred_work_session,
        )

        return log_inferred_work_session(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            project_name=extracted_data.get("project_name"),
            task_name=extracted_data.get("task_name"),
            duration_minutes=extracted_data.get("duration_minutes"),
            note=extracted_data.get("notes"),
            logged_at=event_start_time,
        )


class RelationshipsAdapter(DomainAdapter):
    """Adapter for relationships interaction logging."""

    def create_inferred_record(
        self,
        user_id: int,
        calendar_event_id: int,
        confidence_score: float,
        extracted_data: dict,
        event_start_time: datetime,
    ) -> Optional[int]:
        from lifeos.domains.relationships.services.inferred_service import (
            log_inferred_interaction,
        )

        return log_inferred_interaction(
            user_id=user_id,
            calendar_event_id=calendar_event_id,
            confidence_score=confidence_score,
            person_name=extracted_data.get("person_name"),
            method=extracted_data.get("method"),
            notes=extracted_data.get("notes"),
            logged_at=event_start_time,
        )


# Adapter registry
DOMAIN_ADAPTERS = {
    (DOMAIN_FINANCE, RECORD_TYPE_TRANSACTION): FinanceTransactionAdapter(),
    (DOMAIN_HEALTH, RECORD_TYPE_MEAL): HealthMealAdapter(),
    (DOMAIN_HEALTH, RECORD_TYPE_WORKOUT): HealthWorkoutAdapter(),
    (DOMAIN_HABITS, RECORD_TYPE_HABIT_LOG): HabitsAdapter(),
    (DOMAIN_SKILLS, RECORD_TYPE_PRACTICE): SkillsAdapter(),
    (DOMAIN_PROJECTS, RECORD_TYPE_WORK_SESSION): ProjectsAdapter(),
    (DOMAIN_RELATIONSHIPS, RECORD_TYPE_INTERACTION): RelationshipsAdapter(),
}


def get_adapter(domain: str, record_type: str) -> Optional[DomainAdapter]:
    """Get the adapter for a domain/record_type combination."""
    return DOMAIN_ADAPTERS.get((domain, record_type))
