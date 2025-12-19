# Event Semantics Freeze (Phase 2.5)

Canonical semantic meanings for event types. Every event used in insights must be defined here.

Format:
- event_type
- meaning
- asserted_by
- certainty (must use confidence vocabulary)

## Auth
- auth.user.registered: A user account was created. asserted_by=system, certainty=confirmed
- auth.user.username_reminder_requested: A username reminder was requested. asserted_by=user, certainty=confirmed
- auth.user.password_reset_requested: A password reset was requested. asserted_by=user, certainty=confirmed
- auth.user.password_reset_completed: A password reset was completed. asserted_by=system, certainty=confirmed
- auth.session.created: A session was created (contract only). asserted_by=system, certainty=informational
- auth.session.invalidated: A session was invalidated (contract only). asserted_by=system, certainty=informational
- auth.session.admin_reset: An admin reset invalidated sessions for a user. asserted_by=admin, certainty=confirmed

## Calendar
- calendar.event.created: A calendar event was created. asserted_by=user, certainty=confirmed
- calendar.event.updated: A calendar event was updated. asserted_by=user, certainty=confirmed
- calendar.event.deleted: A calendar event was deleted. asserted_by=user, certainty=confirmed
- calendar.event.synced: A calendar event was synced from an external provider. asserted_by=external_sync, certainty=informational
- calendar.interpretation.created: An interpreter suggested a domain record for a calendar event. asserted_by=system, certainty=needs_review
- calendar.interpretation.confirmed: A user confirmed an interpreted record. asserted_by=user, certainty=confirmed
- calendar.interpretation.rejected: A user rejected an interpreted record. asserted_by=user, certainty=confirmed

## Finance
- finance.account.created: A financial account was created. asserted_by=user, certainty=confirmed
- finance.account.category_updated: An account category assignment was changed. asserted_by=user, certainty=confirmed
- finance.transaction.created: A financial transaction was recorded. asserted_by=user, certainty=confirmed
- finance.transaction.inferred: A transaction was inferred from a calendar event. asserted_by=system, certainty=needs_review
- finance.journal.posted: A journal entry was posted to the ledger. asserted_by=system, certainty=confirmed
- finance.schedule.created: A financial schedule row was created. asserted_by=user, certainty=confirmed
- finance.schedule.updated: A financial schedule row was updated. asserted_by=user, certainty=confirmed
- finance.schedule.deleted: A financial schedule row was deleted. asserted_by=user, certainty=confirmed
- finance.schedule.recomputed: A schedule recomputation completed. asserted_by=system, certainty=informational
- finance.receivable.created: A receivable tracker was created. asserted_by=user, certainty=confirmed
- finance.receivable.entry_recorded: A receivable entry was recorded. asserted_by=user, certainty=confirmed
- finance.ml.suggest_accounts: An ML model suggested account matches. asserted_by=ml, certainty=suggested
- finance.ml.feedback: User feedback on ML suggestions was recorded. asserted_by=user, certainty=confirmed

## Habits
- habits.habit.created: A habit definition was created. asserted_by=user, certainty=confirmed
- habits.habit.updated: A habit definition was updated. asserted_by=user, certainty=confirmed
- habits.habit.deactivated: A habit was deactivated. asserted_by=user, certainty=confirmed
- habits.habit.logged: A habit occurrence was logged. asserted_by=user, certainty=confirmed
- habits.habit.deleted: A habit definition was deleted. asserted_by=user, certainty=confirmed
- habits.habit.inferred: A habit occurrence was inferred from a calendar event. asserted_by=system, certainty=needs_review

## Health
- health.biometric.logged: A biometric record was logged. asserted_by=user, certainty=confirmed
- health.workout.logged: A workout was logged. asserted_by=user, certainty=confirmed
- health.nutrition.logged: A nutrition log entry was recorded. asserted_by=user, certainty=confirmed
- health.metric.updated: A derived health metric was updated. asserted_by=system, certainty=informational
- health.meal.inferred: A meal entry was inferred from a calendar event. asserted_by=system, certainty=needs_review
- health.workout.inferred: A workout entry was inferred from a calendar event. asserted_by=system, certainty=needs_review

## Skills
- skills.skill.created: A skill definition was created. asserted_by=user, certainty=confirmed
- skills.skill.updated: A skill definition was updated. asserted_by=user, certainty=confirmed
- skills.skill.deleted: A skill definition was deleted. asserted_by=user, certainty=confirmed
- skills.practice.logged: A skill practice session was logged. asserted_by=user, certainty=confirmed
- skills.practice.inferred: A skill practice session was inferred from a calendar event. asserted_by=system, certainty=needs_review

## Projects
- projects.project.created: A project was created. asserted_by=user, certainty=confirmed
- projects.project.updated: A project was updated. asserted_by=user, certainty=confirmed
- projects.project.archived: A project was archived. asserted_by=user, certainty=confirmed
- projects.project.completed: A project was marked completed. asserted_by=user, certainty=confirmed
- projects.task.created: A project task was created. asserted_by=user, certainty=confirmed
- projects.task.updated: A project task was updated. asserted_by=user, certainty=confirmed
- projects.task.completed: A project task was completed. asserted_by=user, certainty=confirmed
- projects.task.logged: A project work log entry was recorded. asserted_by=user, certainty=confirmed
- projects.work_session.inferred: A project work session was inferred from a calendar event. asserted_by=system, certainty=needs_review

## Relationships
- relationships.person.created: A person record was created. asserted_by=user, certainty=confirmed
- relationships.person.updated: A person record was updated. asserted_by=user, certainty=confirmed
- relationships.person.deleted: A person record was deleted. asserted_by=user, certainty=confirmed
- relationships.interaction.logged: An interaction was logged. asserted_by=user, certainty=confirmed
- relationships.interaction.updated: An interaction was updated. asserted_by=user, certainty=confirmed
- relationships.interaction.inferred: An interaction was inferred from a calendar event. asserted_by=system, certainty=needs_review

## Journal
- journal.entry.created: A journal entry was created. asserted_by=user, certainty=confirmed
- journal.entry.updated: A journal entry was updated. asserted_by=user, certainty=confirmed
- journal.entry.deleted: A journal entry was deleted. asserted_by=user, certainty=confirmed

## ML Scope
- ML may only attach to inference events and ML feedback events defined in the semantic registry; no new event types are allowed without a contract update.
- Inference events must carry `model_version` and `payload_version` fields; these must be preserved through storage, replay, and projection.
- `status` and confidence vocabulary are semantic commitments: ML must not reinterpret or normalize them outside the defined labels.

## QA Scope
- Ensure every event in the event catalogs has a semantic contract and vice versa (no drift).
- Validate that each event uses the confidence vocabulary and matches the domain boundary.
- Confirm that insights only reference events defined here.
