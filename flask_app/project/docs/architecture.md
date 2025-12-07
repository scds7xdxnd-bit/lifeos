# LifeOS Architecture Constitution
_Last updated: {{YYYY-MM-DD}}_

## Purpose & Scope
LifeOS is a multi-domain, event-aware system centered on a user tenant. This document is the normative source for boundaries, foldering, events, naming, and migration strategy. Controllers stay thin; services own business rules; domains integrate via events or read models.

## Domain Boundaries (authoritative list)
- Core: auth, users/prefs, events, insights, utils, app factory, extensions.
- Finance: ledger (accounts, journal entries/lines), transactions, schedules/forecasts, receivables/loans, trial balance.
- Habits: habits and logs.
- Health: biometrics, workouts, nutrition logs.
- Skills: skills, practice sessions, skill metrics.
- Projects: projects, tasks, task logs.
- Relationships: reserved domain; no coupling until defined.

## Layering & Folder Map
- Controllers (presentation): `lifeos/core/**/controllers`, `lifeos/domains/<domain>/controllers`, Jinja under `lifeos/templates`; static under `lifeos/static`.
- Services (business logic): `lifeos/core/**/services`, `lifeos/domains/<domain>/services`.
- Models (persistence): `lifeos/core/**/models`, `lifeos/domains/<domain>/models`; SQLAlchemy only.
- Schemas/DTOs: `lifeos/domains/<domain>/schemas`.
- Events: `lifeos/core/events/*`; per-domain catalog lives in `lifeos/domains/<domain>/events.py` (add if missing).
- Insights: `lifeos/core/insights/*` (rules, engine, services).
- Tasks/background: `lifeos/domains/<domain>/tasks`.
- ML adapters: `lifeos/domains/<domain>/ml`.
- Migrations: single Alembic home at `lifeos/migrations`.
- Future infra: `lifeos/platform/{bus,outbox,worker,clients}` to house broker/outbox/clients when introduced.

## Dependency Rules
- Controllers → services → models. Controllers never touch models directly.
- Domains may depend on core; domains must not import each other—use events or read models/projections.
- ML only through services; no controller → ML direct calls.
- DTO mapping belongs in `mappers.py` per domain (add alongside schemas); avoid cyclic imports.

## Event Catalog (name → payload contract)
- finance.transaction.created → {transaction_id, user_id, amount, description?, category?, counterparty?, occurred_at}
- finance.journal.posted → {entry_id, user_id, debit_total, credit_total, line_count}
- finance.schedule.created → {row_id, user_id, amount, account_id, event_date}
- finance.schedule.updated → {row_id, user_id, amount?, account_id?, event_date?, memo?}
- finance.schedule.deleted → {row_id, user_id}
- finance.schedule.recomputed → {user_id, days}
- finance.receivable.created → {tracker_id, user_id, principal, counterparty, start_date, due_date?}
- finance.receivable.entry_recorded → {tracker_id, amount, entry_date}
- finance.ml.suggest_accounts → {user_id, description, suggestions:[account_id], model}
- habits.habit.logged → {habit_id, user_id, date, value}
- health.metric.updated → {user_id, metric, value, recorded_at}
- skills.practice.logged → {skill_id, user_id, duration_minutes, practiced_at}
- projects.task.completed → {task_id, project_id, user_id, completed_at}
(Any new event must be added to the emitting domain’s `events.py` with versioned payload docs.)

## Data Model Inventory (current tables/aggregates)
- Core: user, user_preference, role, permission, role_permission, user_role, session_token, jwt_blocklist, event_record, insight_record.
- Finance: finance_account_category, finance_account, finance_journal_entry, finance_journal_line, finance_transaction, finance_trial_balance_setting, finance_money_schedule_row, finance_money_schedule_daily_balance, finance_money_schedule_scenario, finance_money_schedule_scenario_row, finance_receivable_tracker, finance_receivable_manual_entry, finance_loan_group, finance_loan_group_link.
- Habits: habit, habit_log.
- Health: health_biometric, health_workout, health_nutrition_log.
- Skills: skill, skill_practice_session, skill_metric.
- Projects: project, project_task, project_task_log.
- Relationships: none yet (reserved).

## Interaction Contracts
- Controllers validate/authz, then call services with primitives/DTOs; serialization via schemas.
- Services own orchestration, invariants, event emission (`event_service.log_event` after durable commit).
- Models hold persistence and simple helpers only; no cross-domain logic.
- Tasks wrap service calls; must be idempotent and safe to retry.

## Insights Engine
- Subscribes to the event catalog above via `core/events/event_bus.py`.
- Pipeline: ingest event → optional enrichment (recent events, user prefs) → rules per domain (`core/insights/rules/*`) → persist via `insight_record` → delivered to UI/notifications.
- Rules must be deterministic, stateless, and feature-flagged when risky.

## Naming Conventions
- Events: `domain.resource.action[.variant]` (lowercase, dot-separated).
- Migrations: `<timestamp>_<domain>_<short_action>.py` (e.g., `20240301_finance_add_trial_balance.py`).
- Tasks: `domains.<domain>.tasks.<action>.run`.
- Tables: prefix with domain for non-core (`finance_*`, `health_*`, etc.); core tables unprefixed.
- Paths: keep existing layout under `lifeos/core` and `lifeos/domains`.

## Schema Evolution & Migrations
- Single Alembic at `lifeos/migrations`; autogenerate, then review.
- Default additive (nullable/defaulted columns, new tables). Destructive changes require two-phase (shadow + backfill + swap).
- Domain-owned tables: domain team authors migration; core-owned tables: core.
- Backfills belong in scripts/management tasks, not long Alembic steps.
- Indexes: always include `user_id` plus primary query dimension (date/event_type/etc.) for high-volume tables.

## Background Workers
- Tasks live per domain; entrypoint `run(user_id|payload)`; ensure idempotency and retry safety.
- Shared runtime (today in-process; future `platform/worker` with queue + outbox).
- Long jobs must checkpoint and emit telemetry.

## Integration & External Clients
- External services wrapped under `platform/clients/*` (future) or domain `ml` adapters via services only.
- Event delivery to move toward outbox + broker (Redis/Kafka) when available; keep `EventRecord` as audit log.

## Security & Auth
- JWT + session hybrid; roles/permissions in core; controllers enforce authz.
- CSRF via core; rate limiting via limiter; secrets via env.

## Testing
- Mirror module structure under `tests`; include unit (services/rules), integration (workflows), migrations, and ML ranking/feedback tests where applicable.

## RACI: Ownership & Accountability
- Core (auth, users, events, insights, utils)
  - Responsible: Core team; Accountable: Core Lead; Consulted: Domain leads; Informed: Platform.
- Domains (finance, habits, health, skills, projects, relationships)
  - Responsible: Domain team/lead; Accountable: Domain Eng/Product Lead; Consulted: Core, Platform; Informed: Other domain leads.
- Platform (bus/outbox, worker runtime, clients, CI/CD, observability)
  - Responsible: Platform/SRE; Accountable: Platform Lead; Consulted: Core, Domains; Informed: All teams.
- Migrations & Schema Evolution
  - Responsible: Table-owning domain; Core for shared tables; Accountable: respective leads; Consulted: Platform, Insights; Informed: All teams.
- Events & Contracts
  - Responsible: Emitting domain; Accountable: Emitting domain lead; Consulted: Core (bus/outbox), Insights, Platform; Informed: Consumers.
- Background Tasks
  - Responsible: Domain (logic) + Platform (runtime); Accountable: Domain lead (logic) / Platform lead (runtime); Consulted: Core (auth/perm), Observability; Informed: Impacted domains.

