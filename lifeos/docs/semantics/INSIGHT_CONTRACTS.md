# Insight Contracts (Phase 2.5)

Canonical insight definitions. No insight exists without a contract.

Format:
- Insight name
- Description (human-legible)
- Required evidence (events/domains)
- Disallowed evidence
- Confidence bands (uses confidence vocabulary)
- Allowed actions

## Finance
- finance_spend
  - Description: A spending transaction was recorded; surfaced as informational.
  - Required evidence: finance.transaction.created
  - Disallowed evidence: —
  - Confidence bands: informational
  - Allowed actions: display

- journal_posted
  - Description: A journal entry was posted to the ledger.
  - Required evidence: finance.journal.posted
  - Disallowed evidence: —
  - Confidence bands: informational
  - Allowed actions: display

## Habits
- habit_progress
  - Description: A habit log was recorded and can be summarized.
  - Required evidence: habits.habit.logged
  - Disallowed evidence: habits.habit.inferred
  - Confidence bands: informational, needs_review (inferred only)
  - Allowed actions: display, review_only

## Projects
- project_task_done
  - Description: A project task completion was recorded.
  - Required evidence: projects.task.completed, projects.task.logged
  - Disallowed evidence: —
  - Confidence bands: informational
  - Allowed actions: display

## Skills
- skill_practice
  - Description: A skill practice session was logged.
  - Required evidence: skills.practice.logged
  - Disallowed evidence: skills.practice.inferred
  - Confidence bands: informational, needs_review (inferred only)
  - Allowed actions: display, review_only

## Health
- health_metric
  - Description: A health metric update was recorded.
  - Required evidence: health.metric.updated, health.biometric.logged
  - Disallowed evidence: —
  - Confidence bands: informational
  - Allowed actions: display

## Cross-Domain (Rule-based)
- finance_sleep_spend
  - Description: Cross-domain note linking finance and rest patterns.
  - Required evidence: finance.transaction.created, health.biometric.logged
  - Disallowed evidence: calendar.event.created
  - Confidence bands: needs_review
  - Allowed actions: review_only

- habit_project_synergy
  - Description: Cross-domain note linking habits to project outcomes.
  - Required evidence: habits.habit.logged, projects.task.completed
  - Disallowed evidence: calendar.event.created
  - Confidence bands: needs_review
  - Allowed actions: review_only

- skill_mood_uplift
  - Description: Cross-domain note linking skill practice and mood signals.
  - Required evidence: skills.practice.logged, journal.entry.created
  - Disallowed evidence: calendar.event.created
  - Confidence bands: needs_review
  - Allowed actions: review_only

## ML Scope
- Insight contracts are binding for ML evaluation: evidence used for training/eval must be a subset of Required evidence and must exclude Disallowed evidence.
- Confidence bands define allowable system behaviors; ML outputs must never exceed the contract (e.g., review_only remains review_only).
- Insight generation remains rule-based in Phase 2.5; ML may only log metadata for future use.

## QA Scope
- Verify each insight references valid event semantics only (required/disallowed evidence).
- Enforce review_only routing for any needs_review confidence band or uncertain evidence.
- Ensure allowed actions do not exceed contract behavior.
