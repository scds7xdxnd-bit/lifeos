"""Semantic contracts for domains and events (Phase 2.5 freeze)."""

from __future__ import annotations

from dataclasses import dataclass

from lifeos.core.insights.contracts import CONFIDENCE_VOCABULARY


@dataclass(frozen=True)
class DomainSemanticContract:
    domain: str
    purpose: str
    asserts: str
    must_not_infer: str


@dataclass(frozen=True)
class EventSemanticContract:
    event_type: str
    meaning: str
    asserted_by: str
    certainty: str

    def __post_init__(self):
        if self.certainty not in CONFIDENCE_VOCABULARY:
            raise ValueError("invalid_confidence_vocabulary")


DOMAIN_SEMANTIC_CONTRACTS: dict[str, DomainSemanticContract] = {
    "auth": DomainSemanticContract(
        domain="auth",
        purpose="Authenticate identity and manage access state.",
        asserts="User identity and access changes explicitly requested or enforced.",
        must_not_infer="No inference about user intent beyond explicit requests.",
    ),
    "calendar": DomainSemanticContract(
        domain="calendar",
        purpose="Capture declared intentions and scheduled commitments.",
        asserts="User- or sync-declared events with time bounds.",
        must_not_infer="No guarantee that an event occurred; no behavioral certainty.",
    ),
    "finance": DomainSemanticContract(
        domain="finance",
        purpose="Record financial transactions and ledger state changes.",
        asserts="User-committed ledger/transaction facts.",
        must_not_infer="No inference about causality or intent beyond recorded fields.",
    ),
    "habits": DomainSemanticContract(
        domain="habits",
        purpose="Track repeated behaviors and their logs.",
        asserts="User-logged or inferred habit occurrences.",
        must_not_infer="No assumptions about streaks beyond recorded logs.",
    ),
    "health": DomainSemanticContract(
        domain="health",
        purpose="Record biometrics, workouts, and nutrition logs.",
        asserts="User-logged health records or inferred entries.",
        must_not_infer="No medical conclusions or diagnoses.",
    ),
    "skills": DomainSemanticContract(
        domain="skills",
        purpose="Track skill definitions and practice sessions.",
        asserts="User-logged practice activity and skill metadata.",
        must_not_infer="No proficiency claims beyond explicit metrics.",
    ),
    "projects": DomainSemanticContract(
        domain="projects",
        purpose="Track projects, tasks, and logged work sessions.",
        asserts="User-maintained project/task state changes.",
        must_not_infer="No performance judgments beyond recorded state.",
    ),
    "relationships": DomainSemanticContract(
        domain="relationships",
        purpose="Track people and interactions.",
        asserts="User-logged interaction facts and contact metadata.",
        must_not_infer="No subjective relationship judgments.",
    ),
    "journal": DomainSemanticContract(
        domain="journal",
        purpose="Capture private reflections and mood signals.",
        asserts="User-authored entries and stated mood/tags.",
        must_not_infer="No mental health diagnosis or hidden intent.",
    ),
    "inquiry": DomainSemanticContract(
        domain="inquiry",
        purpose="Capture user-scoped inquiry requests and deterministic evidence-based briefs.",
        asserts="Scoped inquiry request metadata, bounded brief generation, and explicit refine/view lifecycle state.",
        must_not_infer="No context-to-evidence promotion, no hidden causality, no autonomous actions.",
    ),
    "system": DomainSemanticContract(
        domain="system",
        purpose="Record system and workflow events required for audit.",
        asserts="Operational and workflow state changes.",
        must_not_infer="No user intent beyond explicit system actions.",
    ),
}


EVENT_SEMANTIC_CONTRACTS: dict[str, EventSemanticContract] = {
    # Auth
    "auth.user.registered": EventSemanticContract(
        event_type="auth.user.registered",
        meaning="A user account was created.",
        asserted_by="system",
        certainty="confirmed",
    ),
    "auth.user.username_reminder_requested": EventSemanticContract(
        event_type="auth.user.username_reminder_requested",
        meaning="A username reminder was requested.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "auth.user.password_reset_requested": EventSemanticContract(
        event_type="auth.user.password_reset_requested",
        meaning="A password reset was requested.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "auth.user.password_reset_completed": EventSemanticContract(
        event_type="auth.user.password_reset_completed",
        meaning="A password reset was completed.",
        asserted_by="system",
        certainty="confirmed",
    ),
    "auth.session.created": EventSemanticContract(
        event_type="auth.session.created",
        meaning="A session was created (contract only).",
        asserted_by="system",
        certainty="informational",
    ),
    "auth.session.invalidated": EventSemanticContract(
        event_type="auth.session.invalidated",
        meaning="A session was invalidated (contract only).",
        asserted_by="system",
        certainty="informational",
    ),
    "auth.session.admin_reset": EventSemanticContract(
        event_type="auth.session.admin_reset",
        meaning="An admin reset invalidated sessions for a user.",
        asserted_by="admin",
        certainty="confirmed",
    ),
    # Calendar
    "calendar.event.created": EventSemanticContract(
        event_type="calendar.event.created",
        meaning="A calendar event was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "calendar.event.updated": EventSemanticContract(
        event_type="calendar.event.updated",
        meaning="A calendar event was updated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "calendar.event.deleted": EventSemanticContract(
        event_type="calendar.event.deleted",
        meaning="A calendar event was deleted.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "calendar.event.synced": EventSemanticContract(
        event_type="calendar.event.synced",
        meaning="A calendar event was synced from an external provider.",
        asserted_by="external_sync",
        certainty="informational",
    ),
    "calendar.interpretation.created": EventSemanticContract(
        event_type="calendar.interpretation.created",
        meaning="An interpreter suggested a domain record for a calendar event.",
        asserted_by="system",
        certainty="needs_review",
    ),
    "calendar.interpretation.confirmed": EventSemanticContract(
        event_type="calendar.interpretation.confirmed",
        meaning="A user confirmed an interpreted record.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "calendar.interpretation.rejected": EventSemanticContract(
        event_type="calendar.interpretation.rejected",
        meaning="A user rejected an interpreted record.",
        asserted_by="user",
        certainty="confirmed",
    ),
    # Finance
    "finance.account.created": EventSemanticContract(
        event_type="finance.account.created",
        meaning="A financial account was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "finance.account.category_updated": EventSemanticContract(
        event_type="finance.account.category_updated",
        meaning="An account category assignment was changed.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "finance.transaction.created": EventSemanticContract(
        event_type="finance.transaction.created",
        meaning="A financial transaction was recorded.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "finance.transaction.inferred": EventSemanticContract(
        event_type="finance.transaction.inferred",
        meaning="A transaction was inferred from a calendar event.",
        asserted_by="system",
        certainty="needs_review",
    ),
    "finance.journal.posted": EventSemanticContract(
        event_type="finance.journal.posted",
        meaning="A journal entry was posted to the ledger.",
        asserted_by="system",
        certainty="confirmed",
    ),
    "finance.schedule.created": EventSemanticContract(
        event_type="finance.schedule.created",
        meaning="A financial schedule row was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "finance.schedule.updated": EventSemanticContract(
        event_type="finance.schedule.updated",
        meaning="A financial schedule row was updated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "finance.schedule.deleted": EventSemanticContract(
        event_type="finance.schedule.deleted",
        meaning="A financial schedule row was deleted.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "finance.schedule.recomputed": EventSemanticContract(
        event_type="finance.schedule.recomputed",
        meaning="A schedule recomputation completed.",
        asserted_by="system",
        certainty="informational",
    ),
    "finance.receivable.created": EventSemanticContract(
        event_type="finance.receivable.created",
        meaning="A receivable tracker was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "finance.receivable.entry_recorded": EventSemanticContract(
        event_type="finance.receivable.entry_recorded",
        meaning="A receivable entry was recorded.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "finance.ml.suggest_accounts": EventSemanticContract(
        event_type="finance.ml.suggest_accounts",
        meaning="An ML model suggested account matches.",
        asserted_by="ml",
        certainty="suggested",
    ),
    "finance.ml.feedback": EventSemanticContract(
        event_type="finance.ml.feedback",
        meaning="User feedback on ML suggestions was recorded.",
        asserted_by="user",
        certainty="confirmed",
    ),
    # Habits
    "habits.habit.created": EventSemanticContract(
        event_type="habits.habit.created",
        meaning="A habit definition was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "habits.habit.updated": EventSemanticContract(
        event_type="habits.habit.updated",
        meaning="A habit definition was updated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "habits.habit.deactivated": EventSemanticContract(
        event_type="habits.habit.deactivated",
        meaning="A habit was deactivated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "habits.habit.logged": EventSemanticContract(
        event_type="habits.habit.logged",
        meaning="A habit occurrence was logged.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "habits.habit.deleted": EventSemanticContract(
        event_type="habits.habit.deleted",
        meaning="A habit definition was deleted.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "habits.habit.inferred": EventSemanticContract(
        event_type="habits.habit.inferred",
        meaning="A habit occurrence was inferred from a calendar event.",
        asserted_by="system",
        certainty="needs_review",
    ),
    # Health
    "health.biometric.logged": EventSemanticContract(
        event_type="health.biometric.logged",
        meaning="A biometric record was logged.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "health.workout.logged": EventSemanticContract(
        event_type="health.workout.logged",
        meaning="A workout was logged.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "health.nutrition.logged": EventSemanticContract(
        event_type="health.nutrition.logged",
        meaning="A nutrition log entry was recorded.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "health.metric.updated": EventSemanticContract(
        event_type="health.metric.updated",
        meaning="A derived health metric was updated.",
        asserted_by="system",
        certainty="informational",
    ),
    "health.meal.inferred": EventSemanticContract(
        event_type="health.meal.inferred",
        meaning="A meal entry was inferred from a calendar event.",
        asserted_by="system",
        certainty="needs_review",
    ),
    "health.workout.inferred": EventSemanticContract(
        event_type="health.workout.inferred",
        meaning="A workout entry was inferred from a calendar event.",
        asserted_by="system",
        certainty="needs_review",
    ),
    # Skills
    "skills.skill.created": EventSemanticContract(
        event_type="skills.skill.created",
        meaning="A skill definition was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "skills.skill.updated": EventSemanticContract(
        event_type="skills.skill.updated",
        meaning="A skill definition was updated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "skills.skill.deleted": EventSemanticContract(
        event_type="skills.skill.deleted",
        meaning="A skill definition was deleted.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "skills.practice.logged": EventSemanticContract(
        event_type="skills.practice.logged",
        meaning="A skill practice session was logged.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "skills.practice.inferred": EventSemanticContract(
        event_type="skills.practice.inferred",
        meaning="A skill practice session was inferred from a calendar event.",
        asserted_by="system",
        certainty="needs_review",
    ),
    # Projects
    "projects.project.created": EventSemanticContract(
        event_type="projects.project.created",
        meaning="A project was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "projects.project.updated": EventSemanticContract(
        event_type="projects.project.updated",
        meaning="A project was updated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "projects.project.archived": EventSemanticContract(
        event_type="projects.project.archived",
        meaning="A project was archived.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "projects.project.completed": EventSemanticContract(
        event_type="projects.project.completed",
        meaning="A project was marked completed.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "projects.task.created": EventSemanticContract(
        event_type="projects.task.created",
        meaning="A project task was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "projects.task.updated": EventSemanticContract(
        event_type="projects.task.updated",
        meaning="A project task was updated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "projects.task.completed": EventSemanticContract(
        event_type="projects.task.completed",
        meaning="A project task was completed.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "projects.task.logged": EventSemanticContract(
        event_type="projects.task.logged",
        meaning="A project work log entry was recorded.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "projects.work_session.inferred": EventSemanticContract(
        event_type="projects.work_session.inferred",
        meaning="A project work session was inferred from a calendar event.",
        asserted_by="system",
        certainty="needs_review",
    ),
    # Relationships
    "relationships.person.created": EventSemanticContract(
        event_type="relationships.person.created",
        meaning="A person record was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "relationships.person.updated": EventSemanticContract(
        event_type="relationships.person.updated",
        meaning="A person record was updated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "relationships.person.deleted": EventSemanticContract(
        event_type="relationships.person.deleted",
        meaning="A person record was deleted.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "relationships.interaction.logged": EventSemanticContract(
        event_type="relationships.interaction.logged",
        meaning="An interaction was logged.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "relationships.interaction.updated": EventSemanticContract(
        event_type="relationships.interaction.updated",
        meaning="An interaction was updated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "relationships.interaction.inferred": EventSemanticContract(
        event_type="relationships.interaction.inferred",
        meaning="An interaction was inferred from a calendar event.",
        asserted_by="system",
        certainty="needs_review",
    ),
    # Journal
    "journal.entry.created": EventSemanticContract(
        event_type="journal.entry.created",
        meaning="A journal entry was created.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "journal.entry.updated": EventSemanticContract(
        event_type="journal.entry.updated",
        meaning="A journal entry was updated.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "journal.entry.deleted": EventSemanticContract(
        event_type="journal.entry.deleted",
        meaning="A journal entry was deleted.",
        asserted_by="user",
        certainty="confirmed",
    ),
    # Inquiry
    "inquiry.requested": EventSemanticContract(
        event_type="inquiry.requested",
        meaning="A user requested a scoped inquiry brief.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "inquiry.context.submitted": EventSemanticContract(
        event_type="inquiry.context.submitted",
        meaning="User-provided context text was submitted for an inquiry.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "inquiry.brief.generated": EventSemanticContract(
        event_type="inquiry.brief.generated",
        meaning="The system generated an inquiry brief from bounded evidence.",
        asserted_by="system",
        certainty="informational",
    ),
    "inquiry.brief.viewed": EventSemanticContract(
        event_type="inquiry.brief.viewed",
        meaning="A user opened an inquiry brief.",
        asserted_by="user",
        certainty="confirmed",
    ),
    "inquiry.refined": EventSemanticContract(
        event_type="inquiry.refined",
        meaning="A user refined inquiry scope/timeframe/context and requested regeneration.",
        asserted_by="user",
        certainty="confirmed",
    ),
}


__all__ = [
    "DomainSemanticContract",
    "EventSemanticContract",
    "DOMAIN_SEMANTIC_CONTRACTS",
    "EVENT_SEMANTIC_CONTRACTS",
]
