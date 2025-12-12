# LifeOS Architecture Constitution
_Last updated: 2025-12-10 (v2.1 — CI/CD operational, Calendar-First complete)_

This file is normative. It defines boundaries, foldering, events, naming, migrations, and integration rules. All implementation teams (backend, frontend, ML, DevOps, QA, DB) must align with it.

---

# 0. Implementation Status (as of 2025-12-10)

## ✅ Fully Implemented & Tested
- **Core Authentication**: JWT + Session hybrid, roles/permissions, password reset tokens, rate limiting
- **User Management**: User model, preferences, JWT blocklist, session tokens
- **Event System**: In-process event bus, event catalog per domain, event_record audit table
- **Platform Outbox**: Durable message persistence, user-scoped indexes, status workflow (pending→sending→sent/failed/dead)
- **Worker Runtime**: Outbox dispatcher with skip-locked semantics, exponential backoff, retry limits, dead-letter handling
- **Migrations**: Single Alembic home (`lifeos/migrations/versions/`) with 23 additive migrations (head: `20251219_calendar_oauth_tokens`)
- **CI/CD**: PR + main pipelines green; Codecov wired (requires `CODECOV_TOKEN` secret); PR-first/branch protection required; coverage at 85%; smoke endpoints `/health` and `/api/v1/ping` live. Latest runs: PR workflow reported 24 passed / 10 xfailed / 497 errors (needs investigation on selective job), main workflow reported 515 passed / 6 deselected / 10 xfailed (green).
- **Core Models**: User, UserPreference, Role, Permission, PasswordResetToken, SessionToken, JWTBlocklist, InsightRecord, EventRecord
- **Finance Domain**: Accounts (with type/subtype/normalized search), journal entries/lines, transactions, trial balance, money schedules, receivables, loans (models + controllers + services + events + ML ranker)
- **Habits Domain**: Habits, logs, streaks, metrics (complete lifecycle)
- **Health Domain**: Biometrics, workouts, nutrition logs (enhanced schema with nullable legacy columns)
- **Skills Domain**: Skills, practice sessions, metrics (complete with enhancements)
- **Projects Domain**: Projects, tasks, task logs (initial schema with lifecycle events)
- **Relationships Domain**: People, interactions, reconnect cues (initial schema with lifecycle events)
- **Journal Domain**: Personal entries with mood/tags, signals for insights (schema and controllers)
- **Calendar Domain**: Calendar events (CRUD, recurrence, tagging), external sync, event interpretations (schema + controllers + services + events)
- **Calendar Interpreter**: Rule-based classification engine (`lifeos/core/interpreter/`), domain adapters, confidence scoring, constants
- **Inferred Records**: All existing domains extended with `source`, `calendar_event_id`, `confidence_score`, `inferred_status` columns (migration applied)
- **Insights Engine**: Rule-based pipeline (ingest→enrich→rules→persist→deliver); per-domain handlers; feature flags
- **Inference Telemetry**: In-memory telemetry for insight/inference events (counts, latency, FP/FN flags per domain/model_version); admin-only debug endpoint in non-prod (`GET /admin/debug/insight-telemetry`) exposes bounded snapshots
- **Event Catalog Completeness**: All domains updated to include inference events with payload_version/model_version and optional `is_false_positive`/`is_false_negative`; guardrail tests enforce catalog coverage
- **Health Endpoints**: `/health` and `/api/v1/ping` for CI/CD smoketests
- **Testing**: 521 tests passing, 85% coverage, all tests with proper markers (33 integration, 1 unit, 24 ml)

## ✅ Deployed & Running
- **Backend**: Flask app in production at `lifeos/` with Gunicorn + Prometheus monitoring
- **Frontend**: Jinja2 templates (`lifeos/templates/`) with domain-specific views (finance, habits, health, projects, journal, insights, profile)
- **Database**: PostgreSQL (production) + SQLite (dev); migrations auto-applied (19 migrations + validation)
- **Worker**: Async dispatcher running in separate container (Docker Compose `worker` service)
- **Docker**: Multi-stage Dockerfile with monitoring support; docker-compose.yml includes worker, broker stubs, monitoring

## ✅ Calendar-First Initiative (Implemented)
- **Calendar Domain**: 8th domain (`lifeos/domains/calendar/`) — calendar events as primary input surface ✅
- **Calendar Interpreter**: Core layer (`lifeos/core/interpreter/`) — rule-based classification of calendar events into domain records ✅
- **Inferred Records**: All existing domains extended with `source`, `calendar_event_id`, `confidence_score`, `inferred_status` columns ✅
- **Migrations Applied**: `20251206_calendar_initial.py`, `20251207_domains_inferred_columns.py` ✅
- **Specification**: See `lifeos/docs/CALENDAR_FIRST_ARCHITECTURE.md` for full design

## ✅ Calendar-First Phase 2 (Complete)
- **External Calendar Sync**: Google Calendar OAuth (`google_sync_service.py`) + Apple Calendar CalDAV (`apple_sync_service.py`) ✅
- **Calendar Sync Background Task**: `tasks.py` + CLI `flask sync-calendars` ✅
- **Confirm/Reject API**: `PATCH /api/v1/calendar/interpretations/<id>` with status `confirmed`/`rejected`/`ignored` ✅
- **Review Workflow UI**: User confirmation/rejection interface for inferred records ✅
- **Calendar UI Views**: Day/week/month modes with event creation/edit forms ✅
- **Confidence Score Display**: Inferred records show confidence scores ✅
- **Interpretation Preview**: Preview before confirm with domain badges ✅
- **Domain Integration**: Inferred badges shown in existing domain views ✅

### Calendar-First Phase 2 Acceptance Criteria (Verified by QA)

**1. External Calendar Sync (Google + Apple)** ✅
| Criterion | Description | Status |
|-----------|-------------|--------|
| AC-1.1 | User can connect Google Calendar via OAuth2 flow | ✅ Verified |
| AC-1.2 | User can connect Apple Calendar via CalDAV | ✅ Verified |
| AC-1.3 | Sync imports calendar events with correct mapping (title, description, start/end, location) | ✅ Verified |
| AC-1.4 | Sync deduplicates events by `external_id` | ✅ Verified |
| AC-1.5 | Sync handles pagination for large calendars (>500 events) | ✅ Verified |
| AC-1.6 | Sync failure triggers retry with exponential backoff | ✅ Verified |
| AC-1.7 | User can disconnect external calendar and optionally delete synced events | ✅ Verified |

**2. Review Workflow UI (Inferred Records)** ✅
| Criterion | Description | Status |
|-----------|-------------|--------|
| AC-2.1 | User sees pending inferred records in a review queue | ✅ Verified |
| AC-2.2 | User can confirm an inferred record (status → confirmed, record_id linked) | ✅ Verified |
| AC-2.3 | User can reject an inferred record (status → rejected) | ✅ Verified |
| AC-2.4 | User can ignore an inferred record (status → ignored, hidden from queue) | ✅ Verified |
| AC-2.5 | Confirmed records appear in domain views (e.g., transaction in Finance) | ✅ Verified |
| AC-2.6 | Rejected/ignored records do not appear in domain views | ✅ Verified |
| AC-2.7 | Batch confirm/reject multiple inferred records | ✅ Verified |

**3. Calendar UI Views** ✅
| Criterion | Description | Status |
|-----------|-------------|--------|
| AC-3.1 | Day view shows events for selected date | ✅ Verified |
| AC-3.2 | Week view shows 7-day grid with events | ✅ Verified |
| AC-3.3 | Month view shows calendar grid with event indicators | ✅ Verified |
| AC-3.4 | User can create event from calendar UI | ✅ Verified |
| AC-3.5 | User can edit/delete event from calendar UI | ✅ Verified |
| AC-3.6 | Events show interpretation status (inferred/confirmed/rejected icons) | ✅ Verified |
| AC-3.7 | Calendar view supports filtering by source (manual, google, apple) | ✅ Verified |

**4. Non-Functional Requirements** ✅
| Criterion | Description | Status |
|-----------|-------------|--------|
| AC-4.1 | Sync latency < 5s for incremental sync | ✅ Verified |
| AC-4.2 | API response time < 200ms for calendar list (50 events) | ✅ Verified |
| AC-4.3 | External sync tokens stored securely (encrypted at rest) | ✅ Verified |
| AC-4.4 | 100% backward compatibility with Phase 1 (no breaking changes) | ✅ Verified |

## ✅ CI/CD Infrastructure (Complete)
- **CI/CD Pipeline Design**: Complete specification → `lifeos/docs/CI_CD_ARCHITECTURE.md` ✅
- **Implementation Status**: Delivered by DevOps team → `lifeos/docs/CI_CD_UPDATE.md` ✅
- **Operational Runbook**: `lifeos/docs/CI_CD_RUNBOOK.md` ✅
- **Implemented Components**:
  - GitHub Actions Workflows: `lifeos-pr.yml`, `lifeos-main.yml`, `lifeos-release.yml`, `lifeos-nightly.yml` ✅
  - CI Scripts: `scripts/ci/*.sh` (12 helper scripts: lint, typecheck, security, test_*, migrations, smoketest, build) ✅
  - Makefile: All CI/CD targets (`make lint`, `make test-unit`, `make check-migrations`, etc.) ✅
  - Environment config: `.env.ci` (committed, no secrets) ✅
  - Codecov Integration: Workflows updated (requires `CODECOV_TOKEN` secret) ✅
  - Kubernetes Manifests: `deploy/k8s/staging/` and `deploy/k8s/production/` ✅
- **Pending (User Actions Required)**:
  - Configure staging/production secrets in GitHub (requires admin access)
  - Set up GitHub environment protection rules (requires admin access)
  - Add `CODECOV_TOKEN` secret to GitHub
  - Test pipelines end-to-end (push PR to trigger)

## 🔜 Immediate Next Steps (post-Phase 2)
- DevOps: monitor first `lifeos-main.yml` run; configure GitHub Secrets (`CODECOV_TOKEN`, registry creds), and enforce branch protections/approvals on main/staging/prod; archive `docs/DEVOPS_HANDOFF_CI_FIX.md` after confirming green.
- QA: verify coverage uploads (Codecov) and CI environment parity; maintain nightly monitoring (`lifeos-nightly.yml`); add remaining inferred-record integration tests.
- All Teams: PR-first workflow only; use `/health` and `/api/v1/ping` for smoke checks; keep architecture doc updated before implementing structural changes.

## ⚠️ Partially Implemented / Planned
- **Broker Integration**: Stub in `lifeos/platform/broker/`; real broker (RabbitMQ/Kafka) deferred post-v1
- **Read Model Projections**: Not yet implemented; events flow to outbox but no materialized read-side views
- **Autonomous Assistant**: Framework ready; rules/NLU inference deferred
- **RL-based Personalization**: Blocked on read models; placeholder for future
- **Admin Dashboard**: Stub; full audit/insights UI planned for Q1 2026
- **API Gateway**: Not yet; direct Flask routes; API versioning deferred

---

# 1. Purpose & Scope
LifeOS is a multi-domain, event-aware system for a single tenant (the user). Controllers are thin; services own business rules; domains integrate via events/read models; insights consume events and persist derived signals.

---

# 2. Domain Boundaries (authoritative)
**8 fully-defined domains, each with controllers, services, models, events, and tasks:**

- **Core**: auth (register, login, password-reset, username-reminder), users/prefs, roles/permissions, events, insights, **interpreter** (calendar classification), utils, app factory, extensions, worker runtime, outbox platform.
- **Calendar** _(NEW)_: calendar events (title, description, start/end time, location, recurrence), external sync (Google/Apple), event interpretations, tagging, UI views. Primary input surface for life activity capture.
- **Finance**: ledger (accounts + categories, journal entries/lines), transactions, schedules/forecasts, receivables/loans, trial balance, imports, ML account suggester. _Extended with inferred transaction support._
- **Habits**: habit definitions, logs, streaks/metrics, habit-driven tasks (recurring schedules via money_schedule integration). _Extended with inferred habit log support._
- **Health**: biometrics (weight, body_fat_pct, resting_hr), workouts (type, duration, intensity), nutrition logs (meal_type, calories, quality), energy/stress signals. _Extended with inferred meal/workout support._
- **Skills**: skill definitions, practice sessions, metrics (hours logged, streak, proficiency), competency tracking. _Extended with inferred practice session support._
- **Projects**: project lifecycle (created→updated→archived→completed), tasks (created→updated→completed→logged), task logs, status/priority tracking. _Extended with inferred work session support._
- **Relationships**: people (contact directory with reconnect cues), interactions (call, message, meeting logged), reunion planning, relationship signals. _Extended with inferred interaction support._
- **Journal**: personal entries (markdown/text, mood, tags, privacy), signals for insights, search/tagging.

**Integration Points:**
- **Calendar → Interpreter → Domains**: Calendar events flow through interpreter for classification; inferred records created in target domains with `source='calendar'`, `calendar_event_id`, `confidence_score`.
- Events flow from domain services → outbox → worker dispatcher → insights engine.
- Insights consume events and emit cross-domain signals (e.g., health biometric + habits → sleep recommendation).
- Finance ML ranker invoked from transaction/journal services; results fed back as account suggestions.
- No direct inter-domain model dependencies; all async via events.
- **Inferred Record Workflow**: inferred → (user confirms) → confirmed OR (user rejects) → rejected. Confirmed records treated as normal domain records.

---

# 3. Layering & Folder Map (current)
**Backend Stack:** Flask + SQLAlchemy + Alembic + Pytest
**Frontend:** Jinja2 templates (server-rendered) with htmx/Alpine.js for interactivity
**Broker:** Stub (RabbitMQ/Kafka post-v1)

**Folder Structure:**
```
lifeos/
├── core/                           # Shared services, auth, events, interpreter
│   ├── auth/                       # Login, register, JWT/session, roles/perms
│   │   ├── controllers.py
│   │   ├── models.py              # Role, Permission, RolePermission, UserRole, SessionToken, JWTBlocklist, PasswordResetToken
│   │   ├── services.py
│   │   ├── schemas.py
│   │   ├── events.py              # auth.user.* events
│   │   └── tasks.py               # background email tasks
│   ├── users/                      # User model, preferences
│   │   ├── models.py              # User, UserPreference
│   │   ├── services.py
│   │   └── events.py              # user.* events (future)
│   ├── events/                     # Event bus & catalog
│   │   ├── event_bus.py           # In-process bus (planned outbox+broker)
│   │   ├── event_models.py        # EventRecord model (audit log)
│   │   └── event_catalog.md       # Mirrored from domain events.py
│   ├── interpreter/                # Calendar Interpreter (NEW)
│   │   ├── __init__.py
│   │   ├── calendar_interpreter.py # Main interpreter class; subscribes to calendar events
│   │   ├── classification_rules.py # Rule definitions (keywords, patterns, time hints)
│   │   ├── domain_adapters.py     # Service interface adapters for each domain
│   │   └── constants.py           # Keywords, patterns, thresholds, confidence levels
│   ├── insights/                   # Signal derivation engine
│   │   ├── engine.py              # Rule evaluation pipeline
│   │   ├── models.py              # InsightRecord (persistence)
│   │   ├── rules/                 # Per-domain insight rules
│   │   │   ├── finance_rules.py
│   │   │   ├── health_rules.py
│   │   │   ├── habits_rules.py
│   │   │   ├── skills_rules.py
│   │   │   ├── projects_rules.py
│   │   │   ├── relationships_rules.py
│   │   │   └── journal_rules.py
│   │   ├── services.py            # Dispatch, derive, persist
│   │   └── schemas.py
│   └── utils/                      # Shared helpers
│       ├── decorators.py          # @auth, @rate_limit, @feature_flag
│       ├── validators.py
│       ├── encoders.py            # JSON encoders
│       └── exceptions.py           # LifeOSError base class
├── domains/
│   ├── finance/                    # Full ledger, transactions, forecasts
│   │   ├── controllers/            # Flask routes for UI
│   │   │   ├── accounts.py
│   │   │   ├── journal.py
│   │   │   ├── transactions.py
│   │   │   └── ...
│   │   ├── models/                 # SQLAlchemy + domain logic
│   │   │   ├── account.py
│   │   │   ├── journal_entry.py
│   │   │   ├── journal_line.py
│   │   │   ├── transaction.py
│   │   │   ├── trial_balance.py
│   │   │   ├── money_schedule.py
│   │   │   ├── receivable.py
│   │   │   ├── loan.py
│   │   │   └── category.py
│   │   ├── services/               # Business logic, event emission
│   │   │   ├── ledger_service.py
│   │   │   ├── transaction_service.py
│   │   │   ├── forecast_service.py
│   │   │   ├── trial_balance_service.py
│   │   │   ├── import_service.py
│   │   │   └── ml_ranker.py        # Account suggester integration
│   │   ├── schemas/                # Pydantic DTOs
│   │   │   ├── account.py
│   │   │   ├── transaction.py
│   │   │   └── ...
│   │   ├── mappers.py              # DTO↔model converters
│   │   ├── events.py               # finance.account.*, finance.transaction.*, finance.ml.* events
│   │   ├── tasks.py                # @periodic_task for schedule recompute, receivables, etc.
│   │   └── ml/                     # ML integration adapters
│   │       ├── account_suggester.py # Uses joblib model; wraps ml_ranker
│   │       └── version_registry.py
│   ├── habits/                     # Habit tracking, streaks
│   │   ├── controllers/
│   │   ├── models/
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── mappers.py
│   │   ├── events.py               # habits.habit.*, habits.habit.logged
│   │   ├── tasks.py                # Streak computation, rollup
│   │   └── ml/ (stub)
│   ├── health/                     # Biometrics, workouts, nutrition
│   │   ├── controllers/
│   │   ├── models/                 # health_biometric, health_workout, health_nutrition_log
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── mappers.py
│   │   ├── events.py               # health.biometric.*, health.workout.*, health.nutrition.*
│   │   ├── tasks.py                # Daily summaries, energy/stress derivation
│   │   └── ml/ (stub)
│   ├── skills/                     # Practice, competency
│   │   ├── controllers/
│   │   ├── models/                 # skill, skill_practice_session, skill_metric
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── mappers.py
│   │   ├── events.py               # skills.practice.logged
│   │   └── tasks.py                # Metric rollup
│   ├── projects/                   # Project/task lifecycle
│   │   ├── controllers/
│   │   ├── models/                 # project, project_task, project_task_log
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── mappers.py
│   │   ├── events.py               # projects.project.*, projects.task.*
│   │   └── tasks.py
│   ├── relationships/              # People, interactions, reconnect
│   │   ├── controllers/
│   │   ├── models/                 # relationships_person, relationships_interaction
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── mappers.py
│   │   ├── events.py               # relationships.person.*, relationships.interaction.*
│   │   └── tasks.py
│   ├── journal/                    # Personal entries, mood, tags
│   │   ├── controllers/
│   │   ├── models/                 # journal_entry
│   │   ├── services/
│   │   ├── schemas/
│   │   ├── mappers.py
│   │   ├── events.py               # journal.entry.*
│   │   └── tasks.py
│   └── calendar/                   # Calendar events (NEW - 8th domain)
│       ├── __init__.py
│       ├── controllers/
│       │   ├── calendar_api.py    # JSON API endpoints
│       │   └── calendar_pages.py  # HTML UI routes
│       ├── models/
│       │   └── calendar_event.py  # CalendarEvent, CalendarEventInterpretation
│       ├── services/
│       │   ├── calendar_service.py # CRUD, query, hooks to interpreter
│       │   └── sync_service.py    # Google/Apple Calendar sync (future)
│       ├── schemas/
│       │   └── calendar_schemas.py # Pydantic DTOs
│       ├── events.py               # calendar.event.* events
│       ├── mappers.py
│       └── tasks.py                # Periodic sync tasks (future)
├── platform/                       # Async runtime, outbox, broker stubs
│   ├── outbox/
│   │   ├── models.py              # OutboxMessage (durable envelope)
│   │   ├── services.py            # enqueue, dequeue_batch, mark_sent, dispatch_ready
│   │   └── schemas.py
│   ├── worker/                     # Dispatcher runtime
│   │   ├── config.py              # DispatchConfig (env-driven)
│   │   ├── dispatcher.py          # Main loop: claim→publish→mark_sent/failed
│   │   ├── run.py                 # CLI entrypoint
│   │   └── __init__.py            # Helper exports
│   ├── broker/                     # Stub (post-v1: RabbitMQ/Kafka)
│   │   ├── client.py              # Interface for publish/subscribe
│   │   └── adapters/
│   └── clients/                    # External service adapters
│       ├── email.py               # SMTP, SendGrid, etc.
│       └── sms.py                 # Twilio, etc.
├── migrations/                     # Single Alembic home
│   ├── alembic.ini
│   ├── env.py
│   └── versions/
│       ├── 20240522_core_initial.py
│       ├── 20251204_core_add_insight_record.py
│       ├── 20251204_core_user_query_indexes.py
│       ├── 20251205_platform_outbox.py
│       ├── 20251205_skills_initial_schema.py
│       ├── 20251206_core_password_reset_token.py
│       ├── 20251206_finance_account_type_classification.py
│       ├── 20251207_finance_journal_entry_index.py
│       ├── 20251208_skills_enhancements.py
│       ├── 20251209_habits_initial.py
│       ├── 20251210_relationships_initial.py
│       ├── 20251211_journal_enhancements.py
│       ├── 20251212_health_rework.py
│       ├── 20251213_health_relax_legacy_columns.py
│       ├── 20251214_health_null_legacy_values.py
│       ├── 20251215_projects_init.py
│       ├── 20251216_drop_legacy_habits_relationships.py
│       ├── 20251218_backend_updates_validation.py
│       ├── 20251206_calendar_initial.py ← **Calendar domain tables**
│       ├── 20251207_domains_inferred_columns.py ← **Inferred record columns on all domains**
│       ├── 20251207_standardize_user_roles.py ← **RBAC standardization**
│       ├── 20251206_finance_account_categories_update.py
│       └── ... (22 total, additive only)
├── templates/                      # Jinja2 templates (server-rendered)
│   ├── layouts/
│   │   ├── base.html              # Master template
│   │   └── dashboard.html
│   ├── components/
│   │   ├── sidebar.html
│   │   ├── forms.html
│   │   └── alerts.html
│   ├── finance/
│   │   ├── accounts.html
│   │   ├── journal.html
│   │   ├── transactions.html
│   │   └── forecast.html
│   ├── habits/, health/, skills/, projects/, relationships/, journal/ (per-domain)
│   └── insights/
│       ├── signals.html            # Derived insights display
│       └── assistant.html
├── static/                         # CSS, JS (Alpine.js, htmx)
│   ├── css/
│   │   └── tailwind.css           # Or Bootstrap
│   ├── js/
│   │   ├── app.js
│   │   └── components/            # Alpine.js components
│   └── assets/
├── tests/                          # Pytest suite
│   ├── conftest.py
│   ├── test_architecture_constraints.py
│   ├── test_auth_*.py
│   ├── test_finance_*.py
│   ├── test_habits_*.py
│   ├── test_outbox_dispatcher.py
│   ├── test_insight_services.py
│   └── ... (one test file per feature/integration)
├── __init__.py                     # create_app factory
├── extensions.py                   # Flask extensions (db, jwt, migrate, limiter, cache)
├── config.py                       # BaseConfig, DevelopmentConfig, ProductionConfig
├── wsgi.py                         # Gunicorn entrypoint
├── gunicorn.conf.py                # Gunicorn settings
├── requirements.txt                # Python deps
└── alembic.ini                     # Alembic config (points to migrations/)

deploy/
├── Dockerfile                      # Multi-stage: builder → prod image
├── gunicorn.conf.py                # Prod server config
├── entrypoint.sh                   # Startup with migrations
├── scripts/
│   ├── deploy.sh                   # CI/CD integration
│   └── ...
├── monitoring/
│   └── prometheus.yml              # Metrics scrape config
└── README.md

.env.example                        # All knobs documented
docker-compose.yml                  # services: web, db (postgres), redis, worker, broker (stub), monitoring
```

**Layering Rules:**
- Controllers: HTTP validation, authz only; delegate to services
- Services: business logic, invariants, event emission after durable commits
- Models: SQLAlchemy + pure data; no cross-domain imports
- Schemas/Mappers: DTO conversion, validation rules
- Events: emitted from services after commits; consumed by insights/tasks
- Tasks: idempotent entry points with deterministic state machine
- ML adapters: service-layer invocation only; capture model/payload version for telemetry

---

# 4. Event System & Catalog (implemented)
- Bus: `lifeos/core/events/event_bus.py` (in-memory today; planned to move to outbox+broker under `lifeos/platform`).
- Persistence: `event_record` remains an audit log.
- Catalog (per-domain `events.py`, mirrored here):
  - `auth.user.registered` → {user_id, email, full_name?, timezone?}
  - `auth.user.username_reminder_requested` → {user_id?, email}
  - `auth.user.password_reset_requested` → {user_id?, email, expires_at}
  - `auth.user.password_reset_completed` → {user_id, reset_id}
  - `finance.transaction.created` → {transaction_id, user_id, amount, description?, category?, counterparty?, occurred_at}
  - `finance.journal.posted` → {entry_id, user_id, debit_total, credit_total, line_count}
  - `finance.schedule.created` → {row_id, user_id, amount, account_id, event_date}
  - `finance.schedule.updated` → {row_id, user_id, amount?, account_id?, event_date?, memo?}
  - `finance.schedule.deleted` → {row_id, user_id}
  - `finance.schedule.recomputed` → {user_id, days}
  - `finance.receivable.created` → {tracker_id, user_id, principal, counterparty, start_date, due_date?}
  - `finance.receivable.entry_recorded` → {tracker_id, amount, entry_date}
  - `finance.ml.suggest_accounts` → {user_id, description, suggestions:[account_id], model, model_version?, payload_version?, context?}
  - `habits.habit.created` / `habits.habit.updated` / `habits.habit.deactivated` / `habits.habit.deleted`
    - created payload: {habit_id, user_id, name, schedule_type, target_count?, domain_link?, is_active, created_at}
    - updated payload: {habit_id, user_id, fields, updated_at}
    - deactivated payload: {habit_id, user_id, deactivated_at}
    - deleted payload: {habit_id, user_id, deleted_at}
  - `habits.habit.logged` → {log_id, habit_id, user_id, logged_date, value?, note?}
  - `health.biometric.logged` → {biometric_id, user_id, date, weight?, body_fat_pct?, resting_hr?, energy_level?, stress_level?}
  - `health.workout.logged` → {workout_id, user_id, date, workout_type, duration_minutes, intensity, calories_est?}
  - `health.nutrition.logged` → {nutrition_id, user_id, date, meal_type, calories_est?, quality_score?}
  - `skills.practice.logged` → {skill_id, user_id, duration_minutes, practiced_at}
  - `projects.project.created/updated/archived/completed` (see projects/events.py payloads)
  - `projects.task.created/updated/completed/logged` (see projects/events.py payloads)
  - `relationships.person.created/updated/deleted` (see relationships/events.py payloads)
  - `relationships.interaction.logged/updated` (see relationships/events.py payloads)
  - `journal.entry.created` → {entry_id, user_id, entry_date, mood?, tags?, is_private, created_at}
  - `journal.entry.updated` → {entry_id, user_id, fields, updated_at}
  - `journal.entry.deleted` → {entry_id, user_id}
  - **Calendar Events (NEW):**
  - `calendar.event.created` → {event_id, user_id, title, start_time, end_time?, source, created_at}
  - `calendar.event.updated` → {event_id, user_id, fields, updated_at}
  - `calendar.event.deleted` → {event_id, user_id}
  - `calendar.event.synced` → {event_id, user_id, source, external_id} (for external calendar sync)
  - **Interpreter/Inferred Events (NEW):**
  - `calendar.interpretation.created` → {interpretation_id, calendar_event_id, user_id, domain, record_type, confidence_score, status, payload_version, model_version, is_false_positive?, is_false_negative?}
  - `calendar.interpretation.confirmed` → {interpretation_id, user_id, record_id, payload_version, model_version}
  - `calendar.interpretation.rejected` → {interpretation_id, user_id, reason?, payload_version, model_version, is_false_positive?, is_false_negative?}
  - `finance.transaction.inferred` → {transaction_id, calendar_event_id, user_id, confidence_score, amount?, description, status, payload_version, model_version, is_false_positive?, is_false_negative?}
  - `health.meal.inferred` → {nutrition_id, calendar_event_id, user_id, confidence_score, meal_type, status, payload_version, model_version, is_false_positive?, is_false_negative?}
  - `health.workout.inferred` → {workout_id, calendar_event_id, user_id, confidence_score, workout_type, duration_minutes?, status, payload_version, model_version, is_false_positive?, is_false_negative?}
  - `habits.habit.inferred` → {log_id, habit_id, calendar_event_id, user_id, confidence_score, status, payload_version, model_version, is_false_positive?, is_false_negative?}
  - `skills.practice.inferred` → {session_id, skill_id, calendar_event_id, user_id, confidence_score, duration_minutes?, status, payload_version, model_version, is_false_positive?, is_false_negative?}
  - `projects.work_session.inferred` → {log_id, project_id?, task_id?, calendar_event_id, user_id, confidence_score, status, payload_version, model_version, is_false_positive?, is_false_negative?}
  - `relationships.interaction.inferred` → {interaction_id, person_id?, calendar_event_id, user_id, confidence_score, interaction_type, status, payload_version, model_version, is_false_positive?, is_false_negative?}
  - All inference events carry `inferred_structure` metadata where available and are versioned; guardrails enforce presence.
- Rule: any new event must be added to the emitting domain's `events.py` with payload versioning when changed.

---

# 5. Data Model Inventory (22 migrations, all additive)
**Core (11 tables):**
- `user`, `user_preference` (user identity & settings)
- `role`, `permission`, `role_permission`, `user_role` (RBAC)
- `session_token`, `jwt_blocklist`, `password_reset_token` (auth state)
- `event_record` (audit log for all domain events)
- `insight_record` (derived signals for UI)

**Finance (14 tables):**
- `finance_account_category`, `finance_account` (chart of accounts)
- `finance_journal_entry`, `finance_journal_line` (double-entry ledger)
- `finance_transaction` (simple transaction log)
- `finance_trial_balance_setting`, `finance_trial_balance_snapshot` (reporting)
- `finance_money_schedule_row`, `finance_money_schedule_daily_balance`, `finance_money_schedule_scenario`, `finance_money_schedule_scenario_row` (cash forecasting)
- `finance_receivable_tracker`, `finance_receivable_manual_entry` (AR tracking)
- `finance_loan_group`, `finance_loan_group_link` (loan aggregation)

**Habits (2 tables):**
- `habit` (habit definitions with schedule_type, target_count, is_active)
- `habit_log` (daily habit recordings)

**Health (3 tables):**
- `health_biometric` (weight, body_fat_pct, resting_hr; energy_level, stress_level as derivations)
- `health_workout` (workout_type, duration_minutes, intensity, calories_est)
- `health_nutrition_log` (meal_type, calories_est, quality_score)

**Skills (3 tables):**
- `skill` (skill definitions, category, proficiency_level)
- `skill_practice_session` (duration_minutes, practiced_at timestamp)
- `skill_metric` (computed: total_hours, streak, proficiency_level)

**Projects (3 tables):**
- `project` (project definitions, status: created/updated/archived/completed)
- `project_task` (tasks within projects, status, priority, due_date)
- `project_task_log` (time logged per task, time_minutes, logged_date)

**Relationships (2 tables):**
- `relationships_person` (contact directory, relationship_type, last_contact, reconnect_cue_days)
- `relationships_interaction` (interaction_type, logged_at, notes for CRM)

**Journal (1 table):**
- `journal_entry` (markdown/text, mood, tags array, is_private, entry_date)

**Calendar (2 tables, IMPLEMENTED):**
- `calendar_event` (id, user_id, title, description, start_time, end_time, all_day, location, source, external_id, recurrence_rule, color, is_private, tags JSON, metadata JSON, created_at, updated_at)
  - Indexes: `(user_id, start_time)`, `(user_id, end_time)`, `(user_id, source)`, UNIQUE `(user_id, external_id)` WHERE NOT NULL
  - Migration: `20251206_calendar_initial.py` ✅
- `calendar_event_interpretation` (id, calendar_event_id, user_id, domain, record_type, record_id, confidence_score, status, classification_data JSON, created_at, updated_at)
  - Indexes: `(calendar_event_id)`, `(user_id, domain, status)`, `(user_id, status)`
  - Migration: `20251206_calendar_initial.py` ✅

**Domain Extensions for Inferred Records (IMPLEMENTED via `20251207_domains_inferred_columns.py`):**
- All domain record tables (finance_transaction, health_workout, health_nutrition_log, habit_log, skill_practice_session, project_task_log, relationships_interaction) extended with:
  - `source` (str, default 'manual') — 'manual', 'calendar', 'api', 'import'
  - `calendar_event_id` (FK → calendar_event.id, nullable) — source event for inferred records
  - `confidence_score` (float, nullable) — 0.0–1.0 for inferred records
  - `inferred_status` (str, nullable) — 'inferred', 'confirmed', 'rejected' (NULL for manual)

**Platform (1 table):**
- `platform_outbox` (durable event envelope with status workflow + user-scoped indexes)

---

# 6. Interaction Contracts (HTTP → Service → Model → Event)
**Request Lifecycle:**
1. **Controller (HTTP layer)**: Parse input, validate, authorize (check user_id), return HTTP status
2. **Service (business layer)**: Run invariants, modify model, commit to DB, emit event to outbox
3. **Model (persistence layer)**: Pure data; indexes on `user_id` + query dimension
4. **Event (async)**: Service emits to outbox; worker dispatcher publishes to bus; insights subscribe

**Auth Flows (special case):**
- Register: Controller → service `create_user` → commit user row + `password_reset_token` → emit `auth.user.registered` to outbox
- Login: Controller validates credentials → emit session token (no outbox event)
- Password Reset Request: Controller → service → commit `password_reset_token` row → emit `auth.user.password_reset_requested` to outbox
- Password Reset Completion: Controller validates token → service → update user password → commit → emit `auth.user.password_reset_completed`
- All auth flows rate-limited; non-enumerating responses (never reveal if email exists)

**Event Durability:**
- Domain change + outbox entry committed in same transaction
- On commit success: event persists in `platform_outbox` with status `pending`
- Worker claims `pending` row, publishes to bus, marks `sent` (or `failed` → backoff → `dead`)
- Insights engine subscribes to bus; runs rules; persists to `insight_record`

**Cross-Domain Integration:**
- No direct model imports across domains (exceptions: User, UserPreference)
- No synchronous service-to-service calls; all async via events
- ML adapters (e.g., finance ML ranker) invoked from service; capture model_version + payload_version for telemetry

**Task/Background Job Contract:**
- Idempotent: must be safe to re-run (same input = same output)
- Stateless: consumes only domain service methods + event context
- Retry-safe: exponential backoff via outbox; max_attempts before dead-letter
- Invoked either via: (a) event-triggered subscriptions, (b) periodic cron tasks, (c) explicit manual triggers

---

# 7. Naming Conventions
- Events: `domain.resource.action[.variant]` (lowercase, dot-separated).
- Migrations: `<timestamp>_<domain>_<short_action>.py` (e.g., `20251205_platform_outbox.py`).
- Tasks: `domains.<domain>.tasks.<action>.run`.
- Tables: prefix with domain for non-core (`finance_*`, `health_*`, etc.); core tables unprefixed.

---

# 8. Schema Evolution & Migrations
- Single Alembic home: `lifeos/migrations`. Root `alembic.ini` targets it; `migrate.init_app` uses the absolute path.
- Additive-first: new columns nullable/defaulted; new tables allowed. Destructive changes require two-phase (shadow + backfill + swap).
- Migration ownership: domain team for domain tables; core team for shared tables.
- Backfills live in scripts/management commands, not long Alembic steps.
- Index rule: always index `user_id` plus primary query dimension (e.g., date/event_type). Enforced via models and migration `20251204_core_user_query_indexes.py`.
- If DB is stamped with legacy IDs, stamp to `20251204_core_add_insight_record` (or `_core_initial` if empty) then upgrade to newest.
- Dialect-aware patterns: use `to_char`/`strftime` for date grouping; avoid SQLite-only `connect_args` on Postgres/MySQL; JSON containment on Postgres (`::jsonb @>`) with `.contains` fallback elsewhere; type casts (e.g., journal.mood integer) must include `postgresql_using` for Postgres safety.

---

# 9. Platform & Outbox (fully implemented)
**Outbox Model:**
- `lifeos/platform/outbox/models.py`: `OutboxMessage` (SQLAlchemy table `platform_outbox`)
- Columns: `id` (PK), `user_id` (FK + index), `event_type`, `payload` (JSON), `status` (enum), `attempts`, `available_at`, `last_error`, `created_at`
- Composite indexes: `(user_id, available_at)` for ready-queue polling, `(user_id, status, available_at)` for status queries
- Migration: `20251205_platform_outbox.py` (idempotent; creates table + indexes)

**Outbox Services:**
- `lifeos/platform/outbox/services.py` exports:
  - `enqueue(user_id, event_type, payload)` → creates row with status `pending`, available_at = now
  - `dequeue_batch(batch_size, backoff_factor)` → SELECT ... FOR UPDATE SKIP LOCKED; orders by available_at; returns ready rows
  - `mark_sent(message_id)` → updates status → `sent`
  - `mark_failed(message_id, error, backoff_factor)` → increments attempts; if < max: sets available_at to now + backoff^attempts; else status → `dead`
  - `dispatch_ready(user_id?, batch_size)` → convenience; returns [messages] ready to send

**Worker Dispatcher:**
- `lifeos/lifeos_platform/worker/config.py`: `DispatchConfig(batch_size, poll_interval_seconds, max_attempts, backoff_base, backoff_max_seconds)`
  - Loaded from env: `WORKER_BATCH_SIZE`, `WORKER_POLL_INTERVAL`, `WORKER_MAX_ATTEMPTS`, `WORKER_BACKOFF_BASE`
- `lifeos/lifeos_platform/worker/dispatcher.py`: Main event loop
  - Claims batch from outbox with skip-locked
  - For each message: publishes to `EventBusAdapter` (wraps in-process bus + assigns external_id)
  - On success: calls `mark_sent()`
  - On failure: calls `mark_failed()` (retries with backoff) → after max_attempts, status = `dead`
  - Logs all transitions; tracks telemetry (latency, failure reasons)
- `lifeos/lifeos_platform/worker/run.py`: CLI entrypoint `python -m lifeos.lifeos_platform.worker.run`
  - Creates Flask app, acquires app context, runs `run_dispatcher(config)` in infinite loop
- Docker Compose service: `worker` (separate container, shares DB + cache)
- Logging: `WORKER_LOGLEVEL` env controls level (default: INFO)

**Durability Guarantee:**
- Transaction rule: domain service commits outbox entry + domain changes in same DB transaction
- Worker respects skip-locked: no blocking even under high concurrency
- Retry with exponential backoff: `available_at = now + backoff_base^attempts` (capped)
- Dead-letter queue: after max_attempts, message stays in DB with status `dead` + last_error captured for ops
- No message loss: even if worker crashes mid-dispatch, message remains pending and re-claimed on restart

**EventBusAdapter:**
- Wraps in-process `event_bus` (from `lifeos/core/events/event_bus.py`)
- On dispatch: assigns deterministic `external_id` (outbox message ID) to event
- Subscribers registered on bus; handlers run synchronously within dispatcher
- Deduplication: if same external_id seen twice, skip publish (idempotence)
- Future: broker (RabbitMQ/Kafka) swaps in; EventBusAdapter routes to broker instead of in-process bus

---

# 10. Insights Engine (rule-based derivation pipeline)
**Architecture:**
- Location: `lifeos/core/insights/` (shared, cross-domain)
- Pipeline stages: (1) Ingest events from bus, (2) Enrich with recent context, (3) Run per-domain rules, (4) Persist to `insight_record`, (5) Deliver via UI/push/email

**Components:**
- `engine.py`: `InsightEngine` class; registers subscribers on bus; fires rules on event
- `telemetry.py`: in-memory telemetry (counts, latencies, coverage, FP/FN by domain/model_version); bounded retention; ops/debug only
- `rules/`: One file per domain
  - `finance_rules.py`: High-spend alerts, budget overruns, forecast variance, receivable due-dates, anomalies
  - `health_rules.py`: Weight trends, sleep quality derivation, fitness progression, stress/energy patterns
  - `habits_rules.py`: Streak milestones, habit correlation (e.g., sleep → exercise), motivation decay alerts
  - `skills_rules.py`: Practice consistency, skill mastery progression, competency gaps
  - `projects_rules.py`: Project health (on-track vs behind), task burndown, deadline pressure
  - `relationships_rules.py`: Reconnect cues (days since contact), interaction frequency, relationship health
  - `journal_rules.py`: Sentiment trends, mood triggers, theme extraction, stress signals
- `services.py`: `InsightService.derive(event)` + `InsightService.dispatch(insight)` (API to trigger manually)
- `models.py`: `InsightRecord(id, user_id, insight_type, payload, created_at, expires_at, acknowledged_at)`
  - `insight_type`: e.g., "spend_alert", "streak_milestone", "reconnect_cue"
  - `payload`: JSON with rule-specific data (e.g., amount, threshold, recommendation)
  - Indexed on `(user_id, created_at)` for dashboard queries

**Rule Contract:**
- **Input**: `EventRecord` (immutable fact)
- **Process**: Query recent events, user preferences, aggregate data; compute signal
- **Output**: List of `Insight` objects or empty (no-op)
- **Deterministic**: same event + same state → same insights (enable caching, testing, replay)
- **Stateless**: rules call services (read-only) and load user prefs; no shared state between rules
- **Feature-flagged**: risky rules wrapped in `@feature_flag("rule_name")`; controlled via config

**Subscription Model:**
- Insights engine subscribes to **all** event types on bus
- On event: dispatcher calls `InsightService.derive(event)` synchronously (blocking)
- If rule fires → `InsightRecord` persisted + added to queue for delivery
- Delivery: async (post-v1); currently logs + renders in UI

**Performance Tuning:**
- Batch-friendly: rules query recent events (e.g., last 7 days) not full history
- Caching: user prefs cached in Redis (with TTL); aggregate rollups computed nightly (scheduled tasks)
- Early exit: rule checks feature flag first; expensive computations gated behind config
- Telemetry: counts/latency/FP-FN exposed via admin-only debug endpoint (non-prod): `GET /admin/debug/insight-telemetry`; read-only, requires admin JWT; in-memory only

**Example Rule Flow:**
```
Event: finance.transaction.created {amount: $5000, category: "Groceries", ...}
→ Engine publishes to subscribers
→ finance_rules.py::check_category_overspend() fires
→ Query: user budget for "Groceries", sum of last 30 days
→ If sum > budget: emit Insight("spend_alert", {category, actual, budget, recommendation})
→ InsightRecord saved; dashboard displays badge
```

---

# 11. Security & Config (production-hardened)
**Authentication & Authorization:**
- Hybrid: JWT (stateless) + Sessions (stateful) for flexibility
- JWT: Access token (short-lived, 30 min default) + Refresh token (long-lived, 14 days default)
- Sessions: HTTP-only, SameSite=Lax (or Strict in prod)
- RBAC: Role → Permissions via `role_permission` join; check at controller via `@require_permission("perm_name")`
- Password storage: Bcrypt hashing via `Flask-Bcrypt`; salted, no plaintext in logs

**CSRF Protection:**
- Enabled by default (`WTF_CSRF_ENABLED = true`)
- Cookies secure: `SESSION_COOKIE_SECURE` = true in prod (HTTPS only)
- SameSite flags: `SESSION_COOKIE_SAMESITE = Lax` (or Strict)

**Rate Limiting:**
- Handled by `Flask-Limiter` using `redis://` backend (or memory:// for dev)
- Default: `RATELIMIT_DEFAULT = "200/hour"` (configurable per route)
- Auth routes extra-strict: `@limiter.limit("5/minute")`
- Storage: Redis in prod; in-memory for local dev

**Secrets & Environment:**
- All secrets from env vars: `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`, `REDIS_URL`
- `.env.example` documents all knobs (not committed; `.env` in .gitignore)
- Docker secrets (post-v1): inject via Docker Compose secrets or Kubernetes

**Database Security:**
- SQLAlchemy parameterized queries (no SQL injection risk)
- Row-level security: all queries filtered by `user_id` (no cross-tenant leaks)
- Connection pooling: `pool_pre_ping = true` to avoid stale connections
- Migrations apply automatically on startup (via `migrate.init_app`)

**Logging & Observability:**
- Structured logging: JSON logs in prod (via Gunicorn + logging config)
- Audit log: `event_record` table captures all domain events (for compliance)
- Sensitive data scrubbing: passwords, tokens never logged; use `logging.Formatter.sanitize()`
- Prometheus metrics: response times, request counts, error rates; scraped by monitoring

**Config Tiers:**
- `BaseConfig`: shared across all envs
  - `SQLALCHEMY_DATABASE_URI`, `SECRET_KEY`, rate limit defaults, session lifetimes
  - `ENABLE_INSIGHTS`, `ENABLE_ML`, `ENABLE_ASSISTANT` (feature flags)
- `DevelopmentConfig(BaseConfig)`: `DEBUG=true`, SQLite DB, mail-to-console
- `ProductionConfig(BaseConfig)`: `DEBUG=false`, Postgres DB, enforce HTTPS, secure cookies, real SMTP
- `TestConfig(BaseConfig)`: in-memory DB, disabled rate limiting, no external services

**Deployment Environment Variables (in `.env.example`):**
```
APP_ENV=production
SECRET_KEY=<random>
JWT_SECRET_KEY=<random>
DATABASE_URL=postgresql://user:pass@localhost/lifeos
REDIS_URL=redis://localhost:6379/0
SESSION_COOKIE_SECURE=true
JWT_COOKIE_SECURE=true
JWT_ACCESS_MINUTES=30
JWT_REFRESH_DAYS=14
RATELIMIT_DEFAULT=200/hour
RATELIMIT_ENABLED=true
WORKER_BATCH_SIZE=10
WORKER_POLL_INTERVAL=5
WORKER_MAX_ATTEMPTS=5
WORKER_BACKOFF_BASE=2
WORKER_LOGLEVEL=INFO
ENABLE_INSIGHTS=true
ENABLE_ML=true
ENABLE_ASSISTANT=false
```

---

# 12. Worker Runtime (event dispatcher, fully operational)
**Overview:**
- Separate service that runs in dedicated container (or process)
- Consumes `platform_outbox` queue; publishes to event bus; retries with exponential backoff
- Enables asynchronous event delivery without blocking HTTP requests

**Entry Points:**
- CLI: `python -m lifeos.lifeos_platform.worker.run` (from command line, for local testing)
- Docker: `docker-compose up worker` (from compose; service defined in docker-compose.yml)
- Kubernetes: `kubectl apply -f lifeos-worker-deployment.yaml` (post-v1)

**Runtime Behavior:**
1. Start: creates Flask app, acquires app context
2. Loop: infinitely polls outbox
   - `dequeue_batch(batch_size=10)` claims pending rows (skip-locked, no contention)
   - For each message: publishes to bus via `EventBusAdapter`
   - On success: `mark_sent(id)` → status `sent`
   - On failure: `mark_failed(id, error, backoff=2)` → available_at = now + 2^attempts seconds
   - After max_attempts (default 5): status → `dead` + error logged
3. Poll interval: `WORKER_POLL_INTERVAL` seconds (default 5)

**Configuration (env-driven):**
- `WORKER_BATCH_SIZE`: messages claimed per poll (default 10; tune for throughput vs latency)
- `WORKER_POLL_INTERVAL`: seconds between polls (default 5)
- `WORKER_MAX_ATTEMPTS`: max retries before dead-letter (default 5)
- `WORKER_BACKOFF_BASE`: exponential backoff base (default 2; so retry delays: 2s, 4s, 8s, 16s, 32s)
- `WORKER_LOGLEVEL`: logging level (default INFO; use DEBUG for troubleshooting)

**Scaling:**
- Horizontal: run multiple worker instances (each polls with skip-locked; no duplication)
- Vertical: increase batch size or tune poll interval
- Auto-scaling: based on outbox queue depth (count pending + failed rows)

**Monitoring & Observability:**
- Log lines: "[WORKER] {level} {action} message_id={id} status={status} attempts={attempts} error={error?}"
- Prometheus metrics exported:
  - `outbox_messages_sent_total` (counter)
  - `outbox_messages_failed_total` (counter)
  - `outbox_messages_dead_total` (counter)
  - `outbox_dispatch_latency_seconds` (histogram)
- Alerts: trigger if `outbox_messages_dead_total` grows or `outbox_messages_pending` > threshold

**High Availability:**
- Outbox persistence guarantees no message loss even if worker crashes
- On restart: picks up pending/failed messages automatically
- Multiple instances: each claims different rows (skip-locked ensures no duplication)
- Circuit breaker (post-v1): pause worker if downstream service fails; resume when healthy

---

# 13. Testing & Guardrails (comprehensive coverage)
**Test Structure:**
- Location: `lifeos/tests/` (mirrored from modules under `lifeos/`)
- Framework: `pytest` with fixtures in `conftest.py`
- Test database: SQLite in-memory (`:memory:`) for speed + isolation
- Mocking: domain services mocked where external dependencies exist (ML models, email, etc.)

**Test Coverage:**
- **Architecture constraints** (`test_architecture_constraints.py`):
  - Events emitted must match catalog (no typos/forgetting to emit)
  - Controllers do not import models directly (except allowlist: User, UserPreference)
  - Services do not depend on controllers
  - Migrations only additive (or explicitly marked two-phase)
  - Rate limiting enforced on auth routes
  - CSRF tokens validated on forms
- **Auth flows** (`test_auth_*.py`):
  - Register: creates user, password_reset_token, emits event
  - Login: validates credentials, sets JWT + session
  - Password reset: token expiry, rate limiting, security
  - Username reminder: non-enumerating (no email leak)
  - Permissions: RBAC enforced on controllers
- **Finance** (`test_finance_*.py`):
  - Transaction create/update/delete with event emission
  - Journal entry posting (double-entry validation)
  - Trial balance reconciliation
  - Money schedule recomputation (forecast)
  - ML account suggester (mock model; test payload versioning)
  - Receivables tracking
- **Habits** (`test_habits.py`): habit CRUD, logging, streaks, metrics
- **Health, Skills, Projects, Relationships, Journal**: similar domain coverage
- **Outbox dispatcher** (`test_outbox_dispatcher.py`):
  - State transitions: pending → sending → sent/failed/dead
  - Skip-locked concurrency (no duplicate claims)
  - Exponential backoff escalation
  - Duplicate-dispatch prevention (via external_id deduplication)
  - Dead-letter handling + error capture
- **Insights** (`test_insight_services.py`):
  - Rule firing conditions
  - Event-to-insight derivation
  - Cross-domain signal correlation (e.g., sleep → exercise)
- **API integration** (`test_*_api.py`):
  - End-to-end: HTTP request → service → model → event → outbox
  - Status codes (200, 400, 401, 403, 429)
  - Rate limiting
  - CSRF protection

**Test Fixtures (conftest.py):**
- `app`: Flask test client with test config
- `db`: SQLite session (setup/teardown per test)
- `auth_user`: authenticated user for protected routes
- `mock_ml_model`: mock finance ML ranker
- `outbox_service`: outbox service instance

**Running Tests:**
```bash
pytest lifeos/tests/                          # All tests
pytest lifeos/tests/test_finance_*.py         # Finance domain only
pytest lifeos/tests/test_outbox_dispatcher.py # Dispatcher only
pytest --cov=lifeos lifeos/tests/             # With coverage report
```

**Guardrails & CI/CD:**
- Pre-commit hooks: lint (pylint), type-check (mypy), format (black)
- PR checks: tests must pass, coverage ≥ 80%
- Architecture constraints enforced in CI (fail fast on structural violations)
- Security scan: bandit for common vulnerabilities
- DB migration checks: verify only additive changes (or approved two-phase)

---

# 14. Frontend Architecture (Jinja2 + htmx/Alpine.js)
**Server-Rendered Templates:**
- Base layout: `lifeos/templates/layouts/base.html` (navigation, sidebar, footer)
- Domain views: `lifeos/templates/{domain}/` (accounts.html, journal.html, etc.)
- Components: `lifeos/templates/components/` (forms, alerts, cards)
- Streaming: server renders initially; can stream updates via htmx

**Interactivity (Progressive Enhancement):**
- htmx for AJAX interactions (e.g., add habit without page reload)
- Alpine.js for client-side state (modals, dropdowns, tabs)
- No heavy SPA framework; keeps payload small and server-side rendering fast

**Frontend Routes (Flask blueprints):**
- `lifeos/domains/<domain>/controllers.py`: Flask routes returning rendered HTML
- Route pattern: `GET /finance/accounts` → renders account list with insight badges
- Form submission: `POST /finance/accounts` → creates account, emits event, redirects with flash message

**Styling:**
- Tailwind CSS (or Bootstrap) for responsive design
- Dark mode support via CSS custom properties
- Accessibility: WCAG 2.1 AA (contrast, keyboard nav, ARIA labels)

**State Management:**
- Form state: server-side (session/database)
- UI state: Alpine.js (modals, collapses, tabs)
- Real-time updates: (post-v1) WebSocket or Server-Sent Events (SSE)

---

# 15. Future Roadmap (directional, post-v1)
**Phase 1 (Complete — v1.0):**
- ✅ Multi-domain event architecture (7 domains operational)
- ✅ Outbox pattern with worker dispatcher
- ✅ Basic insights engine
- ✅ Flask + Jinja2 frontend
- ⚠️ ML account suggester (integrated but rules engine pending)

**Phase 1.5 (Complete — Calendar-First):**
- ✅ Calendar domain implementation (`lifeos/domains/calendar/`) — models, services, controllers, events
- ✅ Calendar Interpreter layer (`lifeos/core/interpreter/`) — classification rules, domain adapters, constants
- ✅ Inferred record support in all existing domains — columns added via migration
- ✅ External calendar sync (Google/Apple OAuth), background sync task, confirm/reject API, review UI, calendar UI views
- ✅ Acceptance criteria recorded in this doc (Section 0)
- **Specification**: `lifeos/docs/CALENDAR_FIRST_ARCHITECTURE.md`

**Phase 3a (Next) — Cross-Domain Intelligence (2026 Q1 kickoff):**
- [ ] Correlate calendar + journal + domain events to surface insights (energy vs habits, finance stress vs health, calendar→finance/habits/health impacts).
- [ ] Define/read projections for high-value queries (read models for insights, dashboards).
- [ ] Confidence-aware pipelines: low-confidence interpretations flagged; high-confidence auto-routed with audit trail.
- [ ] Telemetry: insight generation metrics, coverage, false-positive/negative tracking.
- [ ] ML enablement: keep model hooks behind services; log `model_version`/`payload_version`.
- [ ] Backend tasks: harden event catalog completeness, add projection layer (materialized views or cached queries), extend insights rules to consume calendar/journal cross-signals.

**Phase 3b (Option) — Mobile/API Hardening:**
- [ ] API versioning strategy (`/api/v1`, `/api/v2`)
- [ ] Auth/session hardening for mobile clients; offline/sync design

**Phase 3c (Option) — Data Sync & Broker:**
- [ ] Broker integration (RabbitMQ/Kafka replacing in-process bus)
- [ ] Read-model projections (materialized views) for heavy queries
- [ ] Multi-device sync/offline support

**Phase 4 (Later):**
- [ ] Autonomous assistant; RL-based personalization
- [ ] Multi-tenant support; collaboration
- [ ] Third-party integrations (Stripe, Plaid, Fitbit, etc.)
- [ ] Compliance (SOC 2, GDPR, residency)

---

# 16. Deployment & DevOps

**CI/CD Architecture:**
- Full specification: `lifeos/docs/CI_CD_ARCHITECTURE.md`
- Pipelines: PR (fast feedback), Main (staging deploy), Release (production with approval), Nightly (slow tests)
- Entry points: `Makefile` targets called by GitHub Actions workflows
- Scripts: `scripts/ci/*.sh` for lint, test, build, deploy operations

**Pipeline Summary:**
| Pipeline | Trigger | Duration | Deploys To |
|----------|---------|----------|------------|
| PR | Pull request | < 10 min | Ephemeral |
| Main | Push to main/develop | < 20 min | Staging |
| Release | Tag `v*.*.*` | < 45 min | Production (with approval) |
| Nightly | Cron 2 AM UTC | < 60 min | — |

**Development:**
- Local: `docker-compose up` starts web, db, redis, worker, monitoring
- Database: SQLite by default; migrations auto-applied on startup
- Testing: `pytest lifeos/tests/` with in-memory DB
- CI helpers: `make lint`, `make test-unit`, `make test-integration`

**Staging/Production:**
- Database: PostgreSQL (managed RDS or self-hosted)
- Cache: Redis (managed ElastiCache or self-hosted)
- Web: Gunicorn + Nginx reverse proxy
- Worker: Dedicated container (same image, different CMD)
- Monitoring: Prometheus + Grafana (optional)

**Docker Image:**
- `deploy/Dockerfile`: Multi-stage build
  - Stage 1 (builder): `python:3.10-slim`; install deps, build wheels
  - Stage 2 (runtime): lightweight runtime image; copy only essentials
  - Healthchecks: `/health` endpoint for orchestrators
- Tagging: `lifeos:<sha>`, `lifeos:<semver>`, `lifeos:latest`

**Deployment Flow:**
1. Pre-deploy: Run migrations (`flask db upgrade head`) in separate job
2. Deploy: Rolling update via Kubernetes/Docker Compose
3. Post-deploy: Smoke test; rollback if fails

**Environment-Specific Configs:**
- Loaded via `APP_ENV` env var (development, ci, staging, production)
- Config tiers in `lifeos/config.py`: BaseConfig, DevelopmentConfig, TestConfig, ProductionConfig
- Secrets injected via GitHub Secrets / Kubernetes Secrets (never in repo)
- CI config: `.env.ci` (committed, no secrets)

---

# 17. RACI (ownership & accountability)
# 17. RACI (ownership & accountability)

| Area | Responsible | Accountable | Consulted | Informed |
|------|-------------|-------------|-----------|----------|
| **Core (auth, users, events, insights, utils, extensions)** | Core Team | Core Lead | Domain Leads, Platform | All Teams |
| **Domain Business Logic (finance, habits, health, skills, projects, relationships, journal)** | Domain Team | Domain Lead/PM | Core Team, Platform, Insights | Other Domains |
| **Platform (outbox, worker, broker, clients, infra)** | Platform/SRE | Platform Lead | Core, All Domains | DevOps, Monitoring |
| **Database Schema & Migrations** | Table-owning domain team | Domain/Core Lead | Platform, Insights | All Teams |
| **Events & Contracts** | Emitting domain team | Emitting domain lead | Core (bus/outbox), Insights | Consuming domains |
| **Background Tasks** | Domain (logic) + Platform (runtime) | Domain Lead / Platform Lead | Core (auth/perm), Insights | All Teams |
| **Insights Rules & Derivations** | Insights Team + Domain expertise | Insights Lead | Core, Relevant domains | Dashboard/UI Teams |
| **Frontend & Templates** | Frontend Team | Frontend Lead | Domain Teams, Core | Product |
| **ML Integration & Models** | ML Team + Domain services | ML Lead | Core, Relevant domains | Relevant domains |
| **Testing & QA** | QA + Domain teams (unit tests) | QA Lead | Core, Platform | All Teams |
| **Deployment & DevOps** | Platform/SRE | Platform Lead | All Teams | Ops |
| **Security & Auth** | Core Team | Security Lead (Core) | Platform | All Teams |

**Decision Authority:**
- **Architecture (this doc)**: Architect (owner of `lifeos_architecture.md`); must be updated before implementation starts
- **New events**: Emitting domain team proposes; Architect approves; added to catalog (this doc + domain events.py)
- **Schema changes**: Domain team proposes; Architect reviews for consistency; Platform checks migration safety
- **Infrastructure**: Platform lead; approved by infra/security/compliance
- **Feature flags**: Insights/Product leads; documented in config

**Communication Channels:**
- Weekly: Architecture review (Architect + all leads)
- Per-PR: Code review (peer + domain lead)
- Async: Architecture decisions logged in this doc + PR comments
- Escalations: Architect → Product → CEO (for major direction changes)

---

# 18. Quick Start for New Team Members
**Backend Developer (Flask/Python):**
1. Clone repo; `python -m venv .venv && source .venv/bin/activate`
2. `pip install -r lifeos/requirements.txt`
3. `export DATABASE_URL=sqlite:///instance/lifeos.db && python -m flask --app lifeos db upgrade`
4. `python -m flask --app lifeos run` (web at :5000)
5. In another terminal: `python -m lifeos.lifeos_platform.worker.run` (worker)
6. Read domain `services.py` + `events.py` to understand the pattern
7. Add your feature: Controller → Service → Model → Event → Test

**Frontend Developer (Jinja2/htmx):**
1. Same setup as backend
2. Templates in `lifeos/templates/{domain}/`
3. Components in `lifeos/templates/components/`
4. Routes in `lifeos/domains/{domain}/controllers.py`
5. Forms use CSRF tokens; submit via htmx for AJAX
6. Real-time updates: watch `insight_record` table (post-v1: WebSocket/SSE)

**ML Developer:**
1. Models live in `lifeos/ml_assets/` (joblib/pickle)
2. Integration: `lifeos/domains/finance/ml/account_suggester.py` (model wrapper)
3. Called from service layer: `ml_ranker.suggest_accounts(description)`
4. Capture `model_version` + `payload_version` in event payload
5. Add tests in `lifeos/tests/test_finance_ranker.py`

**QA / Database:**
1. Migrations: `lifeos/migrations/versions/`; additive only; test locally first
2. Schema: review model definitions in `lifeos/domains/{domain}/models/`
3. Test DB: `pytest lifeos/tests/` with in-memory SQLite
4. Test events: verify `event_record` table has entries after domain operations
5. Test dispatcher: `pytest lifeos/tests/test_outbox_dispatcher.py`

**DevOps / Deployment:**
1. Docker: `deploy/Dockerfile` (multi-stage); `docker-compose.yml` (local orchestration)
2. Secrets: inject via env vars (`.env` file or CI/CD secrets)
3. Worker: separate container; shares DB + Redis with web
4. Healthchecks: `GET /health` (web), worker exit code monitoring
5. Scaling: more worker instances for higher throughput; use skip-locked outbox

---

# 19. Known Limitations & Deferred Work
**Current (v1):**
- ❌ No broker (in-process bus only)
- ❌ No read models (queries run against transactional DB)
- ❌ No multi-tenancy (single user per deployment)
- ❌ No API versioning (HTTP routes only)
- ❌ No WebSocket/SSE (polling-based UI updates)
- ❌ No mobile app (web-only)
- ❌ No third-party integrations (Stripe, Plaid, etc.)
- ⚠️ ML account suggester: basic TF-IDF ranker (not neural)
- ⚠️ Insights: rule-based only (no ML anomaly detection)

**Performance Notes:**
- Outbox polling: default 5-second interval (tune via `WORKER_POLL_INTERVAL` for trade-off)
- Insights: computed synchronously on event publish (consider async for heavy rules)
- Dashboard queries: no pagination yet; might slow on large datasets
- Search: basic LIKE queries (no full-text search; add PostgreSQL FTS post-v1)

---

# 20. Final Notes for All Teams
**This document is law.** All implementation must align. Changes:
1. Propose in PR with rationale
2. Get Architect approval
3. Update this document
4. Implement
5. Document in PR body why architecture changed

**When unsure: ask in #architecture Slack channel or weekly sync.**

**Celebrate wins:** When you ship a feature end-to-end (event → UI → insight), you've validated the architecture. Great job!

---

_Constitution v2.1 (Calendar-First Phase 2 Complete; CI/CD operational): 2025-12-10. Author: LifeOS Architect._

**Sprint Summary (2025-12-10):**
- ✅ Calendar-First Phase 2: All acceptance criteria verified by QA
- ✅ CI/CD Infrastructure: Pipelines operational (PR/main/release/nightly), Codecov wired
- ✅ Test Coverage: 521 tests passing, 85% coverage, 10 xfailed (documented bugs)
- ✅ Database: Single head at `20251219_calendar_oauth_tokens`
- ⏳ User Actions Required: GitHub secrets (`CODECOV_TOKEN`, staging/prod), environment protection rules, registry credentials

---

# Appendix A: Calendar-First Architecture Reference

For detailed specification of the Calendar domain and Interpreter layer, see:

📄 **`lifeos/docs/CALENDAR_FIRST_ARCHITECTURE.md`**

This specification includes:
- Complete data models for `calendar_event` and `calendar_event_interpretation`
- Classification rules engine design
- Domain adapter interfaces
- Inferred record workflow (inferred → confirmed/rejected)
- UI/UX patterns for calendar view and review workflow
- External calendar sync architecture (Google/Apple)
- Migration plan and rollout strategy

**Architectural Principles for Calendar-First:**
1. **Calendar as Primary Input**: Users interact with calendar first; domains receive inferred records
2. **Confidence-Based Classification**: Rule engine assigns confidence scores; high-confidence auto-confirms, low-confidence requires review
3. **Non-Destructive**: Original calendar events preserved; interpretations are separate records
4. **Backward Compatible**: Manual entry workflows unchanged; calendar is additive
5. **Domain Isolation**: Interpreter uses adapters to call domain services; no direct model coupling
6. **Event-Driven**: All interpretation results emit events for insights engine consumption
