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

## Inquiry Brief Contracts (Focused Inquiry v1)
- focused_inquiry_domain_brief
  - Description: A scoped inquiry brief generated from one domain lens.
  - Required evidence: Contract-safe records/events/read models within selected domain and timeframe.
  - Disallowed evidence: user-provided context as sole proof; events outside selected timeframe.
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_cross_domain_brief
  - Description: A scoped inquiry brief generated from explicitly selected cross-domain lenses.
  - Required evidence: Contract-safe records/events/read models from each selected domain.
  - Disallowed evidence: Unselected domains; inferred causality without traceable evidence; user context as factual evidence.
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

## Domain Expert Brief Contracts (Phase 7 / 7.1)
- focused_inquiry_finance_expert_brief
  - Description: Deterministic finance-focused expert brief with finance-specific finding categories.
  - Required evidence: finance.transaction.created, finance.journal.posted, finance.schedule.recomputed
  - Disallowed evidence: user context as sole proof; unsupported causal claims
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_habits_expert_brief
  - Description: Deterministic habits-focused expert brief with adherence/cadence framing.
  - Required evidence: habits.habit.logged
  - Disallowed evidence: habits.habit.inferred as confirmed fact
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_projects_expert_brief
  - Description: Deterministic projects-focused expert brief with throughput/slippage framing.
  - Required evidence: projects.task.completed, projects.task.logged
  - Disallowed evidence: unsupported performance judgments
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_skills_expert_brief
  - Description: Deterministic skills-focused expert brief with practice cadence framing.
  - Required evidence: skills.practice.logged
  - Disallowed evidence: unsupported proficiency assertions
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_journal_expert_brief
  - Description: Deterministic journal-focused expert brief using explicit reflective signals.
  - Required evidence: journal.entry.created, journal.entry.updated
  - Disallowed evidence: psychological diagnosis, hidden-intent inference
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_relationships_expert_brief
  - Description: Deterministic relationships-focused expert brief using interaction cadence evidence.
  - Required evidence: relationships.interaction.logged, relationships.interaction.updated
  - Disallowed evidence: relationship quality judgments, inferred intent/emotion of others
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_health_expert_brief
  - Description: Deterministic health-focused expert brief using descriptive metric trends only.
  - Required evidence: health.biometric.logged, health.metric.updated
  - Disallowed evidence: diagnosis, treatment recommendation, clinical framing
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

## Cross-Domain Expert Brief Contracts (Phase 8)
- focused_inquiry_finance_habits_cross_brief
  - Description: Deterministic cross-domain brief for Finance + Habits alignment patterns.
  - Required evidence: finance.transaction.created, habits.habit.logged
  - Disallowed evidence: unsupported causality, psychological interpretation
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_projects_skills_cross_brief
  - Description: Deterministic cross-domain brief for Projects + Skills alignment patterns.
  - Required evidence: projects.task.completed, projects.task.logged, skills.practice.logged
  - Disallowed evidence: unsupported performance inference outside explicit records
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_journal_habits_cross_brief
  - Description: Deterministic cross-domain brief for Journal + Habits co-occurrence and timing.
  - Required evidence: journal.entry.created, habits.habit.logged
  - Disallowed evidence: psychological diagnosis, hidden-intent inference
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_health_habits_cross_brief
  - Description: Deterministic cross-domain brief for Health + Habits trend alignment.
  - Required evidence: health.biometric.logged, health.metric.updated, habits.habit.logged
  - Disallowed evidence: diagnosis, treatment recommendation, clinical framing
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_projects_calendar_cross_brief
  - Description: Deterministic cross-domain brief for Projects + Calendar temporal alignment.
  - Required evidence: projects.task.completed, projects.task.logged, calendar.event.created
  - Disallowed evidence: unsupported causality and free-form narrative inference
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

- focused_inquiry_relationships_journal_cross_brief
  - Description: Deterministic cross-domain brief for Relationships + Journal cadence/reflection alignment.
  - Required evidence: relationships.interaction.logged, relationships.interaction.updated, journal.entry.created
  - Disallowed evidence: relationship quality judgments, inferred intent/emotion of other people
  - Confidence bands: informational, needs_review
  - Allowed actions: display, refine_only

## ML Scope
- Insight contracts are binding for ML evaluation: evidence used for training/eval must be a subset of Required evidence and must exclude Disallowed evidence.
- Confidence bands define allowable system behaviors; ML outputs must never exceed the contract (e.g., review_only remains review_only).
- Insight generation remains rule-based in Phase 2.5; ML may only log metadata for future use.

## QA Scope
- Verify each insight references valid event semantics only (required/disallowed evidence).
- Enforce review_only routing for any needs_review confidence band or uncertain evidence.
- Ensure allowed actions do not exceed contract behavior.
