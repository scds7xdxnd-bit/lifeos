# LifeOS Architecture Constitution
_Last updated: 2026-03-22 (v2.27 — Phase 12d docs alignment: scheduled_time migration id fix, mobile detail drawer status, native preferred-time input + localized preview)_

This file is normative. It defines boundaries, foldering, events, naming, migrations, and integration rules. All implementation teams (backend, frontend, ML, DevOps, QA, DB) must align with it.

---

# 0. Implementation Status (as of 2026-03-13)

## ✅ Fully Implemented & Tested
- **Core Authentication**: JWT + Session hybrid, roles/permissions, password reset tokens, rate limiting
- **User Management**: User model, preferences, JWT blocklist, session tokens
- **Event System**: In-process event bus, event catalog per domain, event_record audit table
- **Platform Outbox**: Durable message persistence, user-scoped indexes, status workflow (pending→sending→sent/failed/dead)
- **Worker Runtime**: Outbox dispatcher with skip-locked semantics, exponential backoff, retry limits, dead-letter handling
- **Migrations**: Single Alembic home (`lifeos/migrations/versions/`) with additive migrations (head: `20251224_insight_feed_indexes`)
- **CI/CD**: PR + main pipelines green; Codecov wired (requires `CODECOV_TOKEN` secret); PR-first/branch protection required; coverage threshold enforced in CI; smoke endpoints `/health` and `/api/v1/ping` live.
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
- **Testing**: Test suite passing with documented marker discipline (`integration`, `unit`, `ml`) and CI coverage gates.
- **Documentation Governance**: UI/UX Constitution is binding (`lifeos/docs/ui_ux_constitution.md`); Tasks Hub at `lifeos/docs/tasks/` with `archive/` for completed cross-team handoffs; semantics canon published under `lifeos/docs/semantics/`.
- **Phase 2.5 Semantic Contract Freeze**: Complete; canonical references in `lifeos/docs/semantics/` are binding for Phase 3a and beyond.
- **Phase 3a Cross-Domain Intelligence Hardening**: Complete; replay determinism, confidence routing, and governance tests enforced. Telemetry checks require admin `AUTH_TOKEN`.
- **Phase 3a.5 Domain UX & Semantic Surface Alignment**: Complete; DSDs approved, read/write boundaries and interaction patterns normalized, finance surfaces aligned to read-first intent.
- **Phase 3b Interface & Contract Hardening**: Complete; versioned API contracts, read-only guardrails, DSD alignment tests, and SLO alerts enforced.
- **Phase 3b.1 Stability Patch & Verification**: Complete; journal write, finance account search, and schedule/forecast regressions fixed and verified; mini soak clean; Phase 3b formally closed.
- **Phase 3c-1 Read & Throughput Scaling**: Complete; read-through cache, cache observability, read-load verification, and invalidation audit completed; Phase 4 unblocked.
- **Phase 4 Calendar Time-Canvas UI**: Verification-complete; feature-flagged calendar time-canvas renderer aligned to Apple-style interaction grammar with snapshots and QA sign-off.
- **Phase 5a Insight Substrate & Proposal Infrastructure**: Complete; timeline ingestion, proposal interpretations, review/correction flow, and QA lifecycle verification complete.
- **Phase 5b Deterministic Cross-Domain Insights**: Complete; feature computation, insight registry, rule emission, feed visibility, and feedback capture verified; QA sign-off recorded.
- **Phase 6 Focused Inquiry v1**: Complete; deterministic evidence-based inquiry flow with lifecycle semantics, confidence/uncertainty output, and replay-safe brief generation.
- **Phase 6.1 Focused Inquiry Quality Hardening**: Complete; inquiry quality transparency, deterministic refine guidance, and quality observability gates verified.
- **Phase 7 Domain Expert Briefs (First-wave)**: Complete; deterministic domain expert strategies shipped for finance/habits/projects/skills with profile/version metadata and QA governance sign-off.
- **Phase 7.1 Later-Wave Domain Expert Briefs**: Complete; deterministic domain expert strategies shipped for journal/relationships/health with semantic guardrails and QA sign-off.
- **Phase 8 Cross-Domain Inquiry Expansion**: Complete; deterministic pair-profile synthesis shipped with safety taxonomy, replay determinism, and per-pair observability gates.
- **Phase 8.1 Inquiry Productization and Decision-Useful Briefs**: Complete; direct-answer shaping, deterministic evidence relevance ordering, answerability metadata, and concise limitation/refine guidance verified without expanding inference breadth.
- **Phase 9 Timeline Intelligence Foundations**: Complete; deterministic temporal pattern interpretation shipped with replay-stable windowing, baseline/version metadata, and approved-pair persistence support without introducing causal or predictive claims.
- **Phase 11 First-Run Onboarding**: In progress; first-run onboarding wizard (domain selection, calendar source, animated processing, calendar redirect) using UserPreference storage. No migration required.
- **Phase 12 Habit UX & Analytics**: In progress; Phase 12a–c complete (card UX fixes, streak engine, engagement layer). Phase 12d detailed and ready: HAB-022 (card polish), HAB-007 (master-detail), HAB-012 (time-aware cues), HAB-016 (ML prediction), HAB-018–020 (QA/CI/monitoring). Uses migration `20260322_habit_scheduled_time` for precise habit cue timing, plus new frontend components and ML baseline implementation.
- **Phase 12 Skills Training v2 (Phase 2)**: In progress; overview cards now support deterministic progress states with legacy fallback, and path/action flow rollout has started behind `ENABLE_PHASE12_SKILLS_GOALS` and `ENABLE_PHASE12_SKILLS_PATH`.

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
- **Implementation Status**: Delivered by DevOps team → `lifeos/docs/archive/CI_CD_UPDATE.md` ✅
- **Operational Runbook**: `lifeos/docs/CI_CD_RUNBOOK.md` ✅
- **Implemented Components**:
  - GitHub Actions Workflows: `lifeos-pr.yml`, `lifeos-main.yml`, `lifeos-release.yml`, `lifeos-nightly.yml` ✅
  - CI Scripts: `scripts/ci/*.sh` (12 helper scripts: lint, typecheck, security, test_*, migrations, smoketest, build) ✅
  - Makefile: All CI/CD targets (`make lint`, `make test-unit`, `make check-migrations`, etc.) ✅
  - Environment config: `.env.ci` (committed, no secrets) ✅
  - Codecov Integration: Workflows updated (requires `CODECOV_TOKEN` secret) ✅
  - Kubernetes Manifests: `deploy/k8s/staging/` and `deploy/k8s/production/` ✅
- **Auto-Deploy (2026-03-21)**:
  - `lifeos-main.yml` deploys backend to Fly.io automatically on push to `main` via `superfly/flyctl-actions` ✅
  - Post-deploy health check smoke test against `/health` (5 retries, 10s interval) ✅
  - Requires `FLY_API_TOKEN` secret in GitHub (configured) ✅
  - Frontend (Next.js) auto-deploys to Vercel on merge to `main` (Vercel Git integration) ✅
- **Removed Legacy Workflows (2026-03-21)**:
  - `ci.yml` deleted — was deprecated, superseded by `lifeos-pr.yml` + `lifeos-main.yml`
  - `deploy.yml` deleted — was a stub with no real deploy logic

## 🆕 Session Lifecycle Scaffold (Phase 3b½ — structure-only; login issue quarantined)
- **Scope**: Add interface-only session lifecycle skeleton (session vs user vs future device identity), admin reset contract, and event shapes without changing current auth behavior.
- **Allowed Implementation Now**: Minimal `admin_reset` path plus optional DB-level session reset script for ops; all other files remain interfaces/stubs until Phase 3c.
- **Events (contracts only)**: `auth.session.created`, `auth.session.invalidated`, `auth.session.admin_reset` with payloads `{session_id, user_id, device_id? (stub), reason?}`; no emitters wired yet.
- **Deferral Statement**: “This login issue is quarantined by design. A minimal reset exists; full resolution belongs to Phase 3c.” Use this to justify deferring behavioral fixes.
- **Explicit Non-Goals (Phase 3c)**: No device fingerprinting, no token/cookie changes, no multi-device sync/offline behavior, no client/browser heuristics.

## 🔜 Immediate Next Steps (post-Phase 2)
- DevOps: monitor first `lifeos-main.yml` run; configure GitHub Secrets (`CODECOV_TOKEN`, registry creds), and enforce branch protections/approvals on main/staging/prod; archive `docs/DEVOPS_HANDOFF_CI_FIX.md` after confirming green.
- QA: verify coverage uploads (Codecov) and CI environment parity; maintain nightly monitoring (`lifeos-nightly.yml`); add remaining inferred-record integration tests.
- All Teams: PR-first workflow only; use `/health` and `/api/v1/ping` for smoke checks; keep architecture doc updated before implementing structural changes.

## 🎯 Current Phase Focus
- Active: Private alpha cut implementation with Phase 10 humanization as a launch gate.
- Deferred: public signup, broad domain exposure, recommendation layer, causal explanation layer, predictive / forecasting foundations, and Phase 3c-2 transport scaling (trigger-based).
- Forbidden in current window: omniscient assistant behavior, assistant-chat UX, runtime ML decisioning, autonomous action, hidden personalization, semantic drift, public-scale complexity, causal overreach, and predictive modeling.

## ✅ Auth & CSRF Hardening (2026-03-21)
- **CSRF bypass for JWT requests**: `@csrf_protected` decorator skips session-based CSRF validation when a valid `Authorization: Bearer` header is present. JWT-authenticated requests are inherently CSRF-safe (the `Authorization` header cannot be set by cross-origin form submissions; it requires JavaScript, which is bound by CORS). Session-only requests still require session-based CSRF validation.
- **Frontend credentials mode**: API client uses `credentials: 'omit'` to prevent sending session cookies alongside JWT tokens (avoids mixed-auth 403 from `_reject_mixed_auth()` guard).
- **CORS origin**: `CORS_ORIGINS` in production includes `https://lifeos-wine.vercel.app` (Vercel frontend), `https://lifeos-black-pond-2352.fly.dev` (Fly.io backend), and localhost dev origins.

## ✅ Phase 3b API Hardening (Complete — prior milestone)
- `/api/v1` namespace added without breaking legacy routes.
- Auth endpoints: `/api/v1/auth/login`, `/api/v1/auth/refresh` return access/refresh tokens, CSRF token, and user payload; Bearer + CSRF supported.
- Insights feed: `/api/v1/insights/feed` with validated filters (domain, severity, date range, status) and consistent pagination metadata; user-scoped and includes source event metadata.
- Client-friendly responses: finance account search, trial balance, and journal list return HTTP 200 with empty payloads/metadata on invalid/empty queries rather than 400; pagination metadata always present.
- Tests: suite green; expected xfails track known gaps outside these changes.

## ⚠️ Partially Implemented / Planned
- **Session Lifecycle Scaffold**: Interface-only `core/auth/session_*`, `device.py`, `constants.py`, `admin_controllers.py`, and session event contracts. Only minimal `admin_reset` path + optional DB reset script may be implemented now; broader behavior deferred to Phase 3c.
- **Broker Integration**: Stub in `lifeos/lifeos_platform/broker/`; real broker (RabbitMQ/Kafka) deferred post-v1
- **Read Model Projections**: Partial; read-only projections exist for insights/review, broader domain projections remain pending
- **Autonomous Assistant**: Framework ready; rules/NLU inference deferred
- **RL-based Personalization**: Blocked on read models; placeholder for future
- **Admin Dashboard**: Stub; full audit/insights UI planned for Q1 2026
- **API Gateway**: Not yet; direct Flask routes; API versioning deferred

---

# 1. Purpose & Scope
LifeOS is a multi-domain, event-aware system for a single tenant (the user). Controllers are thin; services own business rules; domains integrate via events/read models; insights consume events and persist derived signals.

---

# 2. Domain Boundaries (authoritative)
**8 fully-defined domains, each with controllers, services, models, events, and domain-specific background jobs where applicable:**

- **Core**: auth (register, login, password-reset, username-reminder, session lifecycle scaffold + admin reset contract), users/prefs, roles/permissions, events, insights, **interpreter** (calendar classification), utils, app factory, extensions, worker runtime, outbox platform.
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
│   ├── admin/                      # Admin controllers
│   ├── auth/                       # Auth (api_v1, auth_service, controllers, csrf, password, models, schemas, events)
│   ├── events/                     # Event bus + event models/services
│   ├── insights/                   # Engine, rules, telemetry, ML helpers, API controllers
│   ├── interpreter/                # Calendar interpreter + inference emitter
│   ├── users/                      # User models/preferences/services
│   └── utils/                      # Decorators, pagination, strings, time, validation
├── domains/                        # Domain modules
│   ├── calendar/                   # Controllers, models, services, schemas, events, ml
│   ├── finance/
│   ├── habits/
│   ├── health/
│   ├── journal/
│   ├── projects/
│   ├── relationships/
│   └── skills/
├── lifeos_platform/                # Async runtime, outbox, broker stubs, clients
├── readmodels/                     # Read model scaffolding (contracts, registry, runners, projections)
├── migrations/                     # Alembic home (env.py, script.py.mako, versions/, README.md)
├── docs/                           # Architecture, runbooks, UI/UX constitution, semantics, tasks hub
│   ├── lifeos_architecture.md
│   ├── AUTH_COPY_LAYOUT_RULES.md
│   ├── ui_ux_constitution.md
│   ├── semantics/
│   │   ├── DOMAIN_SEMANTIC_CONTRACTS.md
│   │   ├── EVENT_SEMANTICS_FREEZE.md
│   │   ├── INSIGHT_CONTRACTS.md
│   │   └── CONFIDENCE_VOCABULARY.md
│   ├── tasks/
│   │   ├── README.md
│   │   ├── calendar_event_creation_ux_ops.md
│   │   ├── calendar_subsystem_refactor_ops.md
│   │   ├── phase_3a_cross_domain_intelligence_hardening_ops.md
│   │   ├── phase_3b_interface_contract_hardening_ops.md
│   │   ├── phase_6_focused_inquiry_v1.md
│   │   ├── phase_6_1_focused_inquiry_quality_hardening.md
│   │   ├── phase_7_domain_expert_briefs.md
│   │   ├── phase_7_1_later_wave_domain_expert_briefs.md
│   │   ├── phase_8_cross_domain_inquiry_expansion.md
│   │   ├── phase_8_1_inquiry_productization.md
│   │   ├── phase_9_timeline_intelligence_foundations.md
│   │   ├── phase_10_insight_humanization_layer.md
│   │   ├── private_alpha_architecture_cut.md
│   │   └── archive/
│   │       ├── calendar_subsystem_refactor.md
│   │       ├── calendar_subsystem_refactor_ops.md
│   │       ├── calendar_event_creation_ux_handoff.md
│   │       ├── auth_experience_refactor.md
│   │       ├── ux_alignment_sprint_phase1.md
│   │       ├── phase_2_5_semantic_insight_contract_freeze.md
│   │       ├── phase_3a_cross_domain_intelligence_hardening.md
│   │       ├── phase_3a_5_domain_ux_semantic_surface_alignment.md
│   │       ├── phase_3a_5_dsd_checklist.md
│   │       ├── phase_3a_5_dsds.md
│   │       └── phase_3b_interface_contract_hardening.md
│   ├── prompts/
│   └── archive/
├── templates/                      # Jinja2 templates
│   ├── calendar/
│   ├── components/
│   ├── finance/
│   ├── habits/
│   ├── health/
│   ├── insights/
│   ├── journal/
│   ├── layouts/
│   ├── profile/
│   ├── projects/
│   ├── relationships/
│   └── skills/
├── static/                         # CSS/JS assets
│   ├── css/
│   ├── images/
│   └── js/
├── tests/                          # Pytest suite
├── __init__.py                     # create_app factory
├── cleaner.py
├── config.py                       # BaseConfig, DevelopmentConfig, ProductionConfig
├── extensions.py                   # Flask extensions (db, jwt, migrate, limiter, cache)
├── gunicorn.conf.py
├── requirements.txt
├── wsgi.py
└── alembic.ini

deploy/
├── Dockerfile
├── gunicorn.conf.py
├── scripts/
│   ├── entrypoint.sh
│   └── deploy.sh
├── monitoring/
│   └── prometheus.yml
└── README.md

.env.example                        # All knobs documented
docker-compose.yml                  # services: web, db (postgres), redis, worker, broker (stub), monitoring
```

Planned (not yet in repo; Phase 3c or approved interim hygiene):
- `lifeos/core/auth/admin_controllers.py`, `session_services.py`, `session_repository.py`, `session_read_models.py`, `session_models.py`, `device.py`, `session_events.py`, `constants.py`, `tasks.py`

Planned (approved, not yet in repo; Phase 9 timeline intelligence):
- `lifeos/core/timeline/` with `semantics.py`, `contracts.py`, `registry.py`, `feature_builder.py`, `window_comparator.py`, `baseline_estimator.py`, `recurrence_engine.py`, `drift_detector.py`, `summary_assembler.py`, and `adapters/`

Planned (approved, not yet in repo; Phase 10 humanization):
- `lifeos/core/insights/inquiry_humanization/` with `contracts.py`, `phrasebook.py`, `terminology.py`, `structure_compressor.py`, `section_prioritizer.py`, `duplication_reducer.py`, `evidence_explainer.py`, `assembler.py`, and `adapters/`

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
- Bus: `lifeos/core/events/event_bus.py` (in-memory today; planned to move to outbox+broker under `lifeos/lifeos_platform`).
- Persistence: `event_record` remains an audit log.
- Catalog (per-domain `events.py`, mirrored here):
  - `auth.user.registered` → {user_id, email, full_name?, timezone?}
  - `auth.user.username_reminder_requested` → {user_id?, email}
  - `auth.user.password_reset_requested` → {user_id?, email, expires_at}
  - `auth.user.password_reset_completed` → {user_id, reset_id}
  - `auth.session.created` (contract only) → {session_id, user_id, device_id? (stub), created_at}
  - `auth.session.invalidated` (contract only) → {session_id, user_id, device_id? (stub), invalidated_at, reason?}
  - `auth.session.admin_reset` (contract only) → {user_id, session_scope ('single'|'all'), session_id?, device_id? (stub), reason, initiated_by_admin_id?, reset_at}; payload frozen for audit/replay; no device fingerprinting implied; admin action carries no confidence score (explicit intent, not inference)
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
  - `habits.stat.recomputed` → {habit_id, user_id, current_streak, longest_streak, completion_rate_30d, total_logs, payload_version} _(Phase 12)_
  - `habits.habit.streak_milestone` → {habit_id, user_id, streak_length, milestone_type (7|30|100), achieved_at, payload_version} _(Phase 12)_
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

# 4.1 Auth & Session Structural Scaffold (Phase 3b½ — structure-only)
**Purpose:** Separate user identity, session lifecycle, and future device identity so admins/devs can reset sessions without altering auth semantics; quarantine the login issue until Phase 3c while preserving replay/audit guarantees.

**Scope (structure, no behavior change):**
- Components: `session_models.py` (identity + lifecycle states), `session_services.py` (interfaces: create/invalidate/invalidate_all_for_user/admin_reset), `session_events.py` (contracts), `session_repository.py` (persistence contract), `session_read_models.py` (projection-only, replayable, never for authz), `device.py` (stub identity placeholder), `constants.py` (states: active, invalidated, expired, admin_reset), `admin_controllers.py` (admin-only endpoint contract), `tasks.queue_session_admin_reset` (interface hook only), `schemas.py` (session payload DTOs aligned with events; no device fingerprinting).
- Documentation: event catalog remains in this document (Section 4); a standalone `lifeos/core/events/event_catalog.md` is planned but not yet in repo.
- Component responsibilities: `session_models.py` defines session identity boundaries and lifecycle envelope; `session_services.py` owns lifecycle contracts compatible with replay; `session_events.py` fixes event shapes for auditability; `session_repository.py` remains pure data access; `session_read_models.py` are projection-only surfaces; `device.py` anchors deferred device identity without implying fingerprinting or sync.
- Events: contract-only `auth.session.created`, `auth.session.invalidated`, `auth.session.admin_reset`; payloads include `{session_id, user_id, device_id? (stub), reason?}` with frozen audit semantics; admin_reset carries no confidence field (explicit human intent).
- Read-model rule: session read models are replay-safe projections only; never used for authorization decisions.

**What is allowed now (minimal):**
- Implement the smallest viable `admin_reset` path plus an optional DB-level session reset script for ops. No other code paths change; emitters may remain unwired.
- No token/cookie changes, no device fingerprinting, no browser heuristics, no UI work.
- Deferral statement for contributors: “This login issue is quarantined by design. A minimal reset exists; full resolution belongs to Phase 3c.”
- Note: session_* files listed above are planned structure-only and are not yet present in the repo; add them when Phase 3c (or approved interim hygiene work) begins.

**Explicit non-goals until Phase 3c:**
- No multi-device sync or coherence, no offline writes, no CRDT/conflict handling.
- No device identity policy (user-declared vs cryptographic vs platform-provided) and no fingerprinting commitment.
- No auth token format/cookie changes; no client/browser heuristics; no UI surfaces.
- State space fixed to {active, invalidated, expired, admin_reset}; do not add enums until Phase 3c.

**Extension points reserved for Phase 3c:**
- Optional `device_id` FK on session records.
- Projection hydrators for device-aware session dashboards.
- Background cleanup/TTL task implementations.

**Cross-team handoff (structure first):**
- DB: `auth_session` table exists (migration `20251221_auth_session_table.py`) with `session_id`, `user_id`, `lifecycle_state`, `created_at`, `invalidated_at`, optional `device_id` nullable stub. Do not alter existing auth tables or token semantics; keep device_id nullable.
- Backend: land interface files and admin_reset contract only; avoid wiring emitters or token changes. Treat repository/read-model layers as contracts, not implementations.
- QA: design contract-level tests for session lifecycle events and admin reset flows (replay and projection determinism). Do not simulate multi-device/offline or modify auth tokens.
- Frontend: no UI work now; align on future admin-only endpoint contract when backend enables it.
- ML: no action; note future device context may feed risk models; do not ship fingerprinting or behavioral models.
- DevOps/Platform: plan observability hooks for new session events and ensure worker/outbox pipelines can handle them when wired; define admin-only access control for reset endpoints; keep migrations additive-only.
- Cultural guardrail: prioritize structure-first; resist “just fix the login bug”; use the deferral statement until Phase 3c implementation.

**Problem vs non-problem clarity:**
- Solved now: clear separation of identities and lifecycle contracts enabling admin/dev-driven resets without new semantics.
- Not solved now: device coherence, offline, sync/merge logic, or any change to current login/session behavior.

**Admin Reset Design (structure-only, hygiene):**
- Problem: stale or incompatible server-side session/auth state across browsers; known issue quarantined until Phase 3c.
- Intent: provide a minimal, explicit admin/dev-only reset to recover state without altering auth semantics, device policy, or tokens; maintain replay/auditability.
- Solution (structure):
  - Boundary: `core/auth` owns the contract; exposed via `admin_controllers.py` (admin-only) invoking `SessionLifecycleService.admin_reset(user_id, scope, reason, initiated_by_admin_id?)`.
  - Services: `SessionLifecycleService` defines `admin_reset` (idempotent; invalidates all sessions for user or targeted session_id); `SessionQueryService` may surface current session state for admin review (read-only).
  - Repository: `session_repository.py` contract to mark sessions `admin_reset`/`invalidated`; pure data access; no heuristics.
  - Events: `auth.session.admin_reset` contract (see catalog) emitted upon completion; no confidence field; explicit human action.
  - Authorization: limited to admin/dev roles (conceptual); no end-user surface; enforced at controller layer with existing authz primitives.
  - Read models: optional projection surfaces may reflect session states; never used for authz; replay-safe.

**DB-level reset strategy (conceptual, additive-friendly):**
- Scope: one user per invocation; no truncation; no cascading deletes.
- Tables affected (conceptual): existing `session_token` rows (and `auth_session` where present) marked `invalidated_at=now`, `lifecycle_state='admin_reset'`; `jwt_blocklist` may be appended with relevant tokens if present; user row untouched.
- Operations: idempotent by filtering on `user_id` and states ≠ already `admin_reset`/`invalidated`; repeated runs yield no further effect.
- Audit/replay: emit `auth.session.admin_reset` after DB mutation; ensure outbox entry is durably written. Read models, if present, replay this event to converge.
- Reversible in intent: does not delete user; only invalidates session state. Recovery is via normal login afterward.
- Safety: additive-only migrations; no schema change required now. `auth_session` follows the same invalidation semantics.

**Invariants after admin_reset:**
- User identity remains intact; no deletion or mutation of `user`.
- No silent data loss: sessions are marked/reset, not dropped; history/audit preserved.
- Auth guarantees are not weakened: tokens are not broadened; reset removes access rather than loosening checks.
- Replay deterministic: event + DB mutation order is consistent; read models converge by replaying `auth.session.admin_reset`.
- Read models are advisory only and never used for authz; session checks remain server-side on canonical state.

**Non-goals (intentional deferral to Phase 3c):**
- No device identity or browser heuristics; `device_id` remains nullable stub.
- No token/cookie format changes.
- No multi-device coherence or offline semantics.
- No user-facing UX changes; no automatic triggers; no broad session TTL redesign.

**Backend handoff (do now vs defer):**
- Implement now: `SessionLifecycleService.admin_reset` contract, admin-only controller entrypoint (stub), repository method to mark sessions invalidated/admin_reset, outbox emission of `auth.session.admin_reset`, and a minimal DB-level reset script/CLI for single-user scope. Ensure idempotency and audit logging.
- Keep interface-only: session read models, device identity types, hydrators, background cleanup/TTL tasks.
- Defer: any token/cookie changes, device_id enforcement, UI surfaces, multi-device/offline logic, browser detection.
- Do not “improve” by adding heuristics, auto-triggers, or client changes; this is hygiene only.

---

# 5. Data Model Inventory (additive migrations)
**Core (12 tables, additive):**
- `user`, `user_preference` (user identity & settings)
- `role`, `permission`, `role_permission`, `user_role` (RBAC)
- `session_token`, `jwt_blocklist`, `password_reset_token` (auth state)
- `event_record` (audit log for all domain events)
- `insight_record` (derived signals for UI)
- `auth_session` (immutable `session_id`, `user_id`, `lifecycle_state` in {active, invalidated, expired, admin_reset}, `created_at`, `invalidated_at`, optional `device_id` nullable stub; migration `20251221_auth_session_table.py`).

**Finance (14 tables):**
- `finance_account_category`, `finance_account` (chart of accounts)
- `finance_journal_entry`, `finance_journal_line` (double-entry ledger)
- `finance_transaction` (simple transaction log)
- `finance_trial_balance_setting`, `finance_trial_balance_snapshot` (reporting)
- `finance_money_schedule_row`, `finance_money_schedule_daily_balance`, `finance_money_schedule_scenario`, `finance_money_schedule_scenario_row` (cash forecasting)
- `finance_receivable_tracker`, `finance_receivable_manual_entry` (AR tracking)
- `finance_loan_group`, `finance_loan_group_link` (loan aggregation)

**Habits (3 tables):**
- `habit` (habit definitions with schedule_type, target_count, is_active, scheduled_time)
  - Phase 12 addition: `scheduled_time` (time, nullable) — precise time for time-aware cues; coexists with existing `time_of_day` (varchar)
- `habit_log` (daily habit recordings)
- `habit_stat` (materialized statistics, Phase 12)
  - id (PK), habit_id (FK → habits_habit.id, unique, indexed), user_id (FK → user.id, indexed)
  - current_streak (integer, default 0), longest_streak (integer, default 0)
  - completion_rate_30d (float, nullable, 0.0–1.0), total_logs (integer, default 0)
  - last_logged_at (date, nullable), updated_at (timestamp, auto-update)
  - Recomputed on every log create/delete via service layer; serves frontend detail panel and ML feature extraction
  - Index: `(user_id)` for dashboard queries

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
- Login: Controller validates credentials → emit session token (no outbox event). Session events are contracts only until Phase 3c; current behavior unchanged.
- Session lifecycle contract (structure-only): `SessionLifecycleService` (create, invalidate, invalidate_all_for_user, admin_reset) + `SessionQueryService`; `session_read_models` are replay-only and never used for authz; optional `device_id` is a stub (no fingerprinting).
- Admin reset guardrails: Only minimal `admin_reset` path + optional DB-level session reset script may be implemented now to quarantine login issues. No token/cookie changes, no browser heuristics, no new device identity policy until Phase 3c.
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
- `auth_session` migration is additive and present (`20251221_auth_session_table.py`); `device_id` remains nullable stub.
- Migration ownership: domain team for domain tables; core team for shared tables.
- Backfills live in scripts/management commands, not long Alembic steps.
- Index rule: always index `user_id` plus primary query dimension (e.g., date/event_type). Enforced via models and migration `20251204_core_user_query_indexes.py`.
- If DB is stamped with legacy IDs, stamp to `20251204_core_add_insight_record` (or `_core_initial` if empty) then upgrade to newest.
- Dialect-aware patterns: use `to_char`/`strftime` for date grouping; avoid SQLite-only `connect_args` on Postgres/MySQL; JSON containment on Postgres (`::jsonb @>`) with `.contains` fallback elsewhere; type casts (e.g., journal.mood integer) must include `postgresql_using` for Postgres safety.

---

# 9. Platform & Outbox (fully implemented)
**Outbox Model:**
- `lifeos/lifeos_platform/outbox/models.py`: `OutboxMessage` (SQLAlchemy table `platform_outbox`)
- Columns: `id` (PK), `user_id` (FK + index), `event_type`, `payload` (JSON), `status` (enum), `attempts`, `available_at`, `last_error`, `created_at`
- Composite indexes: `(user_id, available_at)` for ready-queue polling, `(user_id, status, available_at)` for status queries
- Migration: `20251205_platform_outbox.py` (idempotent; creates table + indexes)

**Outbox Services:**
- `lifeos/lifeos_platform/outbox/services.py` exports:
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
- API v1 feed: `/api/v1/insights/feed` returns paginated, user-scoped insights with filters (domain, severity, status, date range) using `InsightsFeedQuery`; status filtering is applied from insight data (`status`/`inference_status`) in-memory for DB portability.

**Performance Tuning:**
- Batch-friendly: rules query recent events (e.g., last 7 days) not full history
- Caching: user prefs cached in Redis (with TTL); aggregate rollups computed nightly (scheduled tasks)
- Early exit: rule checks feature flag first; expensive computations gated behind config
- Telemetry: counts/latency/FP-FN exposed via admin-only debug endpoint (non-prod): `GET /admin/debug/insight-telemetry`; read-only, requires admin JWT; in-memory only

# 10.1 Read Model Constitution (binding)
- Purpose: answer queries the transactional model is not optimized for; never enforce business rules or accept user writes.
- Source of truth: derived exclusively from events; controllers/services never write them; backfills via event replay only.
- Taxonomy: Snapshots (current best-known state, idempotent, 1 row/user/key), Timeline (append-only, time-indexed, immutable), Aggregates (windowed, re-computable, explicit bounds).
- Placement: future `lifeos/readmodels/<domain>/`; not inside domains; prevents leakage and clarifies ownership.
- Contracts: each read model declares consumed events, replay start version, idempotency key, and rebuild strategy; if not rebuildable deterministically, it is invalid.
- Storage: SQL/views/Redis/etc. allowed; schema contract must be documented independent of storage.
- Forbidden: joining transactional tables in builders; controllers writing read models; read models emitting domain events; mutating confidence/inference status; permission logic in read models.

# 10.2 Confidence Semantics (binding)
- Confidence is historical, immutable: answers “how certain was the system at inference time?”
- Layers: Interpreter confidence (`confidence_score`, set once); Inference status (`inferred|confirmed|rejected|ignored`, user actions only, does not change score); Insight confidence (derived reliability over time, contextual).
- Immutability: `confidence_score`, `classification_data`, calendar_event links, FP/FN flags never mutate; `inferred_status` changes only via user actions/events.
- FP/FN: FP = inferred then user rejected; FN = system missed, user created manually; flags are append-only and include `model_version` and `payload_version`.
- Auto-confirm (future): explicit thresholds, domain-specific allowed, audit trail required; user override always wins; auto-confirm is routing only, not truth rewriting.
- No confidence decay/post-hoc smoothing; temporal relevance handled by insights, not by mutating confidence.

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
- API v1 auth: `/api/v1/auth/login` and `/api/v1/auth/refresh` return access/refresh + CSRF token + user; Bearer + CSRF headers supported; JWT_TOKEN_LOCATION includes headers/cookies

**CSRF Protection:**
- Enabled by default (`WTF_CSRF_ENABLED = true`)
- Cookies secure: `SESSION_COOKIE_SECURE` = true in prod (HTTPS only)
- SameSite flags: `SESSION_COOKIE_SAMESITE = Lax` (or Strict)
- Binding environment policy: see `lifeos/docs/ops/environment_cookie_security_policy.md` (development HTTP with `SESSION_COOKIE_SECURE=false`; production HTTPS with `SESSION_COOKIE_SECURE=true`; `HttpOnly` + `SameSite=Lax` required).

**Auth & CSRF Authority Note (Binding):**
- **Canonical CSRF source:** the server-issued, session-bound CSRF token (WTF/Flask session). This is the only valid authority.
- **Forbidden CSRF sources:** localStorage/sessionStorage, client-generated tokens, cached/overridden meta tags, or any token not minted by the current server session.
- **Invariant:** `X-CSRF-Token` (or equivalent header) **must equal** the session CSRF token for the active session. Mismatch == 403.

**Secret Stability (Binding):**
- **Must be fixed per environment:** `SECRET_KEY`, `JWT_SECRET_KEY` (and any explicit CSRF secret if configured).
- **Forbidden:** randomizing these on restart while keeping cookies/sessions alive. Rotation requires coordinated cookie invalidation and re-login.

**Build Identity (Required Observability):**
- Backend **must expose build identity** (commit SHA) in a stable location (e.g., `/health` response or `X-LifeOS-Build` header) to detect build drift.

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

# 14. Frontend Architecture

## 14a. Next.js Frontend (`frontend/`)

The primary frontend is a Next.js 16 + React 19 + TypeScript application.

**Folder Structure:**
```
frontend/
├── app/                    # Next.js App Router
│   ├── (app)/              # Protected routes (calendar, habits, projects, skills, insights)
│   ├── (auth)/             # Auth routes (login)
│   ├── layout.tsx          # Root layout (fonts, providers)
│   ├── providers.tsx       # React Query, auth context
│   └── globals.css         # Tailwind base styles
├── components/
│   ├── landing/            # Landing page (inline styles + design tokens)
│   │   ├── sections/       # NavBar, Hero, Features, InquiryDemo, SocialProof, Waitlist, Footer
│   │   ├── components/     # Button, Card, GlassContainer, MicroLabel, Motion
│   │   ├── hooks/          # useBreakpoint (responsive)
│   │   ├── assets/         # Illustration SVGs
│   │   ├── tokens.ts       # Design tokens (colors, fonts, shadows, spacing, etc.)
│   │   └── translations.ts # EN + ZH i18n with typed interfaces
│   ├── shell/              # App shell (sidebar, top bar)
│   └── ui/                 # shadcn/ui component library
└── lib/
    ├── api/                # Fetch wrappers, API client
    ├── auth/               # Auth context, token management
    └── utils.ts            # Common utilities
```

**Stack:** Next.js 16, React 19, TypeScript, Tailwind CSS v4 + PostCSS, React Query v5, shadcn/ui + Base UI, lucide-react.

**Landing Page Pattern:** Uses inline React styles + centralized design tokens (`tokens.ts`) — NOT Tailwind. Responsive via `useBreakpoint()` hook (mobile ≤639px, tablet 640–1023px, desktop 1024px+). i18n via `translations.ts` (EN + ZH). See `DESIGN.md` §6 for full responsive spec.

**App Pages Pattern:** Uses Tailwind CSS + shadcn/ui. API client in `lib/api/`, React Query for server state. Auth via custom JWT/cookie flow (future Clerk migration planned — AuthContext must stay swappable).

**Auth:** JWT (API) + Session (cookies) + CSRF. Protected routes in `(app)/` group, auth routes in `(auth)/`.

## 14b. Legacy Jinja2 Frontend (`lifeos/templates/`)

Server-rendered templates still exist for the original Flask-based UI:
- Base layout: `lifeos/templates/layouts/base.html`
- Domain views: `lifeos/templates/{domain}/`
- Components: `lifeos/templates/components/`
- Interactivity: htmx for AJAX, Alpine.js for client-side state

**Note:** The Next.js frontend is the primary frontend. Jinja2 templates are retained for backward compatibility during migration.

**Styling (both frontends):**
- Design system: "The Botanical Editorial" (see `DESIGN.md`)
- Accessibility: WCAG 2.1 AA (contrast, keyboard nav, ARIA labels)

---

# 15. Future Roadmap (directional, post-v1)
- **Phase 1 (Complete — v1.0):**
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

**Phase 3a (Complete) — Cross-Domain Intelligence (formalization/hardening):**
- ✅ Correlate calendar + journal + domain events to surface insights using existing interpreter/events/rules.
- ✅ Define/read projections for high-value queries as read-only, conservative surfaces; no full CQRS infra.
- ✅ Confidence-aware pipelines: low-confidence interpretations flagged; high-confidence routed with audit trail; no autonomous action without explicit user confirmation.
- ✅ Telemetry: insight generation metrics, coverage, false-positive/negative tracking.
- ✅ ML enablement: keep model hooks behind services; log `model_version`/`payload_version`.
- ✅ Backend tasks: harden event catalog completeness; extend insights rules to consume calendar/journal cross-signals; replay-safe projections only.

**Phase 3b (Complete) — Interface & Contract Hardening:**
- ✅ Versioned response schemas for read surfaces (insights, review queue, calendar views/ledger, finance read APIs)
- ✅ Read-only guardrails enforced with contract tests
- ✅ DSD alignment enforced in CI
- ✅ SLOs defined with alerts; metrics exposed via `/metrics`

**Phase 3c (Option) — Scaling Track (split by trigger):**
- **Phase 3c-1 — Read & Throughput Scaling (trigger: slow dashboards/insight cost growth/background load):**
  - [ ] Materialized views or cached projections for heavy queries
  - [ ] Redis-backed query results where justified
- **Phase 3c-2 — Event Transport Scaling (trigger: multiple workers/fan-out cost/retry-DLQ pressure):**
  - [ ] Broker integration (RabbitMQ/Kafka) and outbox→broker bridge
  - [ ] DLQ/throughput tuning
- **Phase 3c-3 — Multi-Device & Session Realization (trigger: active multi-device use/offline conflicts/mobile clients):**
  - [ ] Implement session lifecycle stack: wire events/repository/read models, optional `device_id` FK, TTL/cleanup tasks, admin reset flows
  - [ ] Token/cookie redesign only with legal/security sign-off

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
1. Pre-deploy: Run migrations (`python -m flask --app lifeos.wsgi:app db upgrade head`) in separate job
2. Deploy: Rolling update via Kubernetes/Docker Compose
3. Post-deploy: Smoke test; rollback if fails

**Environment-Specific Configs:**
- Loaded via `APP_ENV` env var (development, ci, staging, production)
- Config tiers in `lifeos/config.py`: BaseConfig, DevelopmentConfig, TestConfig, ProductionConfig
- Secrets injected via GitHub Secrets / Kubernetes Secrets (never in repo)
- CI config: `.env.ci` (committed, no secrets)

---

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
- ❌ No native mobile app (web-only; landing page is responsive across mobile/tablet/desktop)
- ❌ No third-party integrations (Stripe, Plaid, etc.)
- ⚠️ Session lifecycle scaffold only: admin_reset path minimal; no device identity policy, no session read models used for authz, no multi-device/offline coherence. Login issue quarantined until Phase 3c.
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

_Constitution v2.22 (Section 14 rewritten for Next.js frontend + responsive landing page): 2026-03-20. Author: LifeOS Architect._

**Sprint Summary:**
- ✅ Phase 2.5 semantic contract freeze completed; canon published under `lifeos/docs/semantics/`
- ✅ Phase 2.5 task archived; semantic/insight contract registries enforced by tests
- ✅ Tasks Hub active with archived UX alignment and auth refactor tasks
- ✅ Session lifecycle scaffold remains interface-only; admin reset minimal path allowed; login issue quarantined to Phase 3c
- ✅ Phase 3b.1 stabilization gate complete; mini soak clean; Phase 3b formally closed
- ✅ Phase 3c-1 read scaling complete; cache strategy Option A verified; read-load verification passed
- ✅ Phase 4 calendar time-canvas UI verification complete; snapshots captured; QA sign-off recorded
- 🟡 Phase 3c-2 trigger assessment opened; broker scaling pending signal validation
- ✅ Phase 5a complete: timeline ingestion, proposal interpretations, review/correction flow, and QA lifecycle verification complete
- ✅ Phase 5b complete: deterministic cross-domain insight rules, feature computation, feed visibility, and feedback capture verified

**Phase Summary:**
- ✅ Phase 3a complete: deterministic replay harness + gold dataset, confidence routing enforcement, read-only projections, governance tests
- ✅ Phase 3a.5 complete: DSDs approved across all domains; read-first patterns enforced; finance surfaces stabilized
- ✅ QA sweep green; telemetry smoke check requires admin `AUTH_TOKEN`
- ✅ Phase 3b complete: versioned API contracts, read-only guardrails, DSD alignment tests, SLOs and alerts live
- ✅ Phase 3b ops checks green; /metrics exposes Phase 3b SLO metrics; contract smoke tests green
- ✅ Phase 3b.1 complete: core write-path regressions fixed; verification mini soak clean; Phase 3b formally closed
- ✅ Phase 3c-1 complete: read-through cache and observability in place; read-load harness clean; cache invalidation audit complete
- ✅ Phase 4 verification-complete: calendar time-canvas UI delivered under feature flag; QA snapshots captured; metrics remained green
- 🟡 Phase 3c-2 assessment opened: collecting outbox and dispatch telemetry before broker selection
- ✅ Phase 5a complete: proposal substrate shipped; proposals endpoint fixed; QA lifecycle tests green
- ✅ Phase 5b complete: rule-based insights emitted and verified; Phase 5c entry gate eligible
- ✅ Phase 6 complete: focused inquiry flow delivered with deterministic evidence-based briefs
- ✅ Phase 6.1 complete: inquiry quality hardening delivered and QA-approved
- ✅ Phase 7 complete (first-wave): deterministic domain expert briefs for finance/habits/projects/skills
- ✅ Phase 7.1 complete (later-wave): deterministic domain expert briefs for journal/relationships/health with safety guardrails
- ✅ Phase 8 complete: deterministic cross-domain inquiry synthesis for approved domain pairs
- ✅ Phase 8.1 complete: inquiry productization delivered with decision-useful direct answers and answerability metadata
- ✅ Phase 9 complete: deterministic timeline intelligence delivered with replay-safe temporal interpretation and metadata
- 🟡 Private alpha cut ratified: launch scope narrowed to inquiry-first, invite-only operation with humanized default output and wave-gated domains

---

# 21. Focused Inquiry v1 (Constitutional Decision, Binding)

Focused Inquiry v1 is the foundational inquiry feature introduced after Phase 5c readiness. It is defined as a user-initiated, scoped, evidence-based brief generator and must preserve existing semantic law.

## 21.1 Product Position
- LifeOS is a personal evidence-based inquiry system, not a generic chatbot, not a dashboard-first tracker, and not an omniscient assistant.
- Focused Inquiry v1 is the first intentional surface for "ask one question, get one bounded brief."
- Domain expertise remains bounded. Cross-domain synthesis is allowed only when contract-safe evidence exists.

## 21.2 Hard Guardrails
- No autonomous actions, no hidden ranking changes, no speculative psychology.
- No user-provided context may be promoted into system evidence without independent support from canonical records.
- No schema or contract reinterpretation outside semantically frozen vocabularies.
- UI interaction remains calm-first and read-first; this feature must not collapse into chat loops or dashboard density.

## 21.3 Canonical Output Form
- Output is a brief, not a conversation transcript.
- Every finding must show: claim, evidence references, confidence label, and uncertainty note (if applicable).
- Evidence references must resolve to canonical domain events, records, read models, or existing insight artifacts.

## 21.4 Routing Model
- Inquiry requests route to a bounded domain lens (finance, health, habits, skills, projects, relationships, journal, calendar) or an explicitly cross-domain lens.
- Cross-domain lenses must explicitly list participating domains and evidence links used in synthesis.

## 21.5 System Behavior Requirements
- Deterministic generation for the same inputs (scope, timeframe, evidence state, context text).
- Replay-safe derivation; no hidden mutable state in brief assembly.
- Read-through caching allowed for inquiry reads only, with explicit invalidation on source-change events.
- Observability must include inquiry requested/generated/viewed/refined counters and latency histograms.

## 21.6 Constitutional References
- UI behavior is governed by `lifeos/docs/ui_ux_constitution.md`.
- Semantic and evidence boundaries are governed by:
  - `lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md`
  - `lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md`
  - `lifeos/docs/semantics/INSIGHT_CONTRACTS.md`
  - `lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md`
- Execution brief: `lifeos/docs/tasks/phase_6_focused_inquiry_v1.md`.

---

# 22. Phase 7.1 Later-Wave Domain Expert Briefs (Constitutional Decision, Binding)

Phase 7.1 extends deterministic domain expert brief coverage to higher-semantic-risk domains:
- Journal
- Relationships
- Health

## 22.1 Phase objective
- Deepen single-domain expert coverage before any cross-domain expert expansion.
- Preserve deterministic replay, evidence-first output, and non-chat interaction model.

## 22.2 Safety guardrails
- Journal: no psychological diagnosis or hidden-intent inference.
- Relationships: no relationship quality judgment and no inferred intent/emotion of others.
- Health: no medical diagnosis, treatment recommendation, or clinical framing.
- All findings must remain evidence-referenced and confidence-labeled using canonical vocabulary.

## 22.3 Boundary and deferrals
- In scope: later-wave domain strategy modules, domain-specific claim categories, and domain limitation language.
- Deferred: cross-domain expert synthesis and timeline intelligence foundations.
- Forbidden: omniscient assistant architecture, hidden personalization/ranking, runtime ML decisioning.

## 22.4 Execution reference
- `lifeos/docs/tasks/phase_7_domain_expert_briefs.md` (first-wave closure)
- `lifeos/docs/tasks/phase_7_1_later_wave_domain_expert_briefs.md` (later-wave closure)

---

# 23. Phase 8 Cross-Domain Inquiry Expansion (Constitutional Decision, Binding)

Phase 8 introduces deterministic cross-domain inquiry synthesis for approved domain pairs while preserving domain trust boundaries.

## 23.1 Phase objective
- Expand inquiry capability beyond single-domain depth into bounded multi-domain synthesis.
- Preserve deterministic replay, evidence-first reasoning, and non-assistant interaction model.

## 23.2 Approved initial pair profiles
- Finance + Habits
- Projects + Skills
- Journal + Habits
- Health + Habits
- Projects + Calendar
- Relationships + Journal

## 23.3 Safety guardrails
- Allowed outputs are observational and evidence-referenced only (co-occurrence, temporal alignment, coverage/structural gaps).
- Forbidden outputs include psychological interpretation, medical inference, moral judgment, intent inference of others, and unsupported causality.
- Cross-domain synthesis must not become free-form assistant narrative output.

## 23.4 Boundary and deferrals
- In scope: pair-profile strategy registry, deterministic evidence aggregation, deterministic synthesis rules.
- Deferred: timeline intelligence, predictive systems, recommendation engines, and broad causal modeling.
- Forbidden: omniscient assistant architecture, hidden personalization/ranking, runtime ML decisioning.

## 23.5 Execution reference
- `lifeos/docs/tasks/phase_8_cross_domain_inquiry_expansion.md` (phase closure brief)

---

# 24. Phase 8.1 Inquiry Productization (Constitutional Decision, Binding)

Phase 8.1 improves inquiry usefulness quality without expanding inference breadth.

## 24.1 Phase objective
- Increase direct-answer quality and decision usefulness in inquiry briefs.
- Preserve deterministic, evidence-bounded, non-assistant behavior.

## 24.2 Productization boundaries
- In scope: deterministic question-to-brief matching, relevance shaping, limitation deduplication, answerability classification, and refine-guidance improvement.
- Out of scope: timeline intelligence, recommendation layer, causal explanation layer, and runtime ML reasoning.

## 24.3 Safety guardrails
- Productized wording must not overstate truth boundaries.
- Answer quality must not be treated as certainty.
- Correlation must not be presented as causation.
- Context remains non-evidence unless independently supported by canonical records.

## 24.4 Execution reference
- `lifeos/docs/tasks/phase_8_1_inquiry_productization.md`

---

# 25. Phase 9 Timeline Intelligence Foundations (Constitutional Decision, Binding)

Phase 9 introduces deterministic temporal pattern interpretation for inquiry without changing LifeOS into a recommendation, causal, or predictive system.

## 25.1 Phase objective
- Add replay-stable temporal reasoning for recurrence, continuity/breaks, drift, baseline comparison, stability, and change across fixed historical windows.
- Improve inquiry usefulness for "what is changing over time?" questions while preserving evidence-bounded, non-chat, non-causal behavior.

## 25.2 Product position
- Bounded-window reasoning answers what appears inside one selected interval.
- Timeline intelligence answers how comparable intervals relate to each other across history.
- Temporal findings remain observational summaries over canonical evidence, not diagnoses, recommendations, forecasts, or causal stories.

## 25.3 Architectural placement
- Phase 9 adds a shared timeline layer under `lifeos/core/timeline/`; it is distinct from Phase 5 timeline ingestion in `lifeos/core/insights/timeline_ingestor.py`.
- Inquiry generation must route all temporal claims through this shared layer before domain or cross-domain brief assembly. Domain strategies and cross-domain pair profiles must not implement ad-hoc temporal math outside the shared timeline layer.
- Core shared components:
  - `semantics.py`: canonical windowing, ordering, timezone, and `as_of_ts` rules
  - `contracts.py`: versioned timeline request/summary/profile contracts
  - `registry.py`: allowlisted domain and approved-pair timeline profiles
  - `feature_builder.py`: deterministic bucket construction from canonical evidence
  - `window_comparator.py`: current vs prior comparable window comparison
  - `baseline_estimator.py`: fixed baseline construction from prior comparable windows
  - `recurrence_engine.py`: recurrence, continuity, and break detection
  - `drift_detector.py`: baseline-relative change classification
  - `summary_assembler.py`: bounded temporal findings with provenance, limits, and metadata
  - `adapters/`: domain-specific temporal adapters that normalize safe domain evidence into timeline features without altering domain semantics

## 25.4 Determinism and replay law
- Timeline computation identity is fixed by normalized inquiry input, selected domains, captured timezone, fixed window specification, `as_of_ts`, timeline profile/version, and deterministic evidence manifest hash.
- Comparison windows must be equal-duration, non-overlapping, and fully determined from the active window plus profile policy; no sampling, heuristic backfilling, or moving baselines are allowed.
- No evidence with timestamps after `as_of_ts` may affect any temporal feature, baseline, comparison, or rendered claim.
- Missing or sparse history must degrade to explicit insufficiency language, not silent interpolation or inferred continuity.

## 25.5 Allowed temporal capability scope
- In scope:
  - recurrence detection
  - streak continuity and break detection
  - recent-window vs prior-window comparison
  - fixed-baseline comparison
  - trend direction over comparable windows
  - volatility / instability description
  - episodic vs sustained distinction
  - drift from established baseline
  - approved-pair temporal alignment persistence across windows
- Internal-only support features may include density/clustering metrics, but these are not standalone user claims in Phase 9.

## 25.6 Semantic guardrails
- Allowed temporal claims are observational only: "recurred", "increased relative to the prior comparable window", "more variable than the recent baseline", "appears recent rather than sustained", "alignment persisted across multiple windows".
- Forbidden claims include:
  - causality ("because", "caused by", "driven by")
  - inevitability ("will happen again", "always", "destined")
  - pathology or diagnosis from volatility/drift
  - recommendations or prescribed interventions
  - prediction, forecasting, or counterfactual reasoning
- Confidence vocabulary remains unchanged and canonical. Temporal directness may improve, but certainty may not be upgraded without stronger evidence.

## 25.7 UX scope
- Phase 9 changes the inquiry surface only. No dedicated timeline dashboard/view is introduced in this phase.
- Inquiry output may add bounded read-first sections such as:
  - "Change over time"
  - "Compared with prior window"
  - "Recurring pattern"
  - "Stability / instability"
- Every temporal finding must expose window labels, evidence references, and an explicit note when history is sparse or partial.
- Forbidden UI patterns in Phase 9: dense KPI dashboards, predictive arrows, causal storytelling, opaque scores, and hidden evidence behind charts.

## 25.8 Domain rollout and cross-domain scope
- First-wave timeline support: finance, habits, projects, skills, calendar.
- Later-wave timeline support: health, journal, relationships.
- Cross-domain timeline scope is limited to approved Phase 8 domain pairs and only for persistence/alignment across fixed windows. No 3+ domain temporal synthesis is allowed.

## 25.9 Docs and execution references
- Required updates:
  - `lifeos/docs/ui_ux_constitution.md`
  - `lifeos/docs/semantics/INSIGHT_CONTRACTS.md`
  - `lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md`
  - `lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md`
- `lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md` remains unchanged.
- Execution reference: `lifeos/docs/tasks/phase_9_timeline_intelligence_foundations.md`

---

# 26. Phase 10 Insight Humanization Layer (Constitutional Decision, Binding)

Phase 10 introduces a deterministic humanization layer that transforms canonical inquiry briefs into ordinary-user-readable explanations without changing meaning, evidence boundaries, confidence semantics, or auditability.

## 26.1 Phase objective
- Improve readability, interpretability, and brevity for ordinary users while preserving canonical inquiry truth conditions.
- Make inquiry answer the user’s practical reading questions first: what happened, why it matters, how sure the system is, and what to review next.

## 26.2 Product position
- Semantic correctness and human comprehensibility are distinct requirements.
- Canonical inquiry remains the semantic source of truth.
- Humanization is a presentation transformation over canonical inquiry, not a new inference stage, assistant behavior, or recommendation system.

## 26.3 Canonical vs humanized model
- LifeOS now has two output layers:
  - canonical brief layer: semantically precise, replay-auditable, technical source of truth
  - humanized brief layer: deterministic user-facing rendering derived from the canonical brief
- Canonical output must always remain available.
- Humanized output is the default visible reading surface in inquiry.

## 26.4 Architectural placement
- Humanization lives after canonical inquiry assembly, productization, and timeline interpretation.
- It does not replace reasoning, evidence selection, confidence assignment, or timeline computation.
- Planned shared location: `lifeos/core/insights/inquiry_humanization/`
- Core shared components:
  - `contracts.py`: canonical-to-humanized transformation contracts and version metadata
  - `phrasebook.py`: approved plain-language substitutions and bounded phrases
  - `terminology.py`: technical-term simplification rules
  - `structure_compressor.py`: section compression and shortening rules
  - `section_prioritizer.py`: default reading order for humanized blocks
  - `duplication_reducer.py`: caveat and metadata repetition reduction
  - `evidence_explainer.py`: deterministic "why this matters" rendering from canonical evidence references
  - `assembler.py`: humanized brief assembly
  - `adapters/`: domain and approved-pair phrasing adapters limited to wording and ordering only

## 26.5 Determinism and equivalence law
- Humanization must be byte-stable for the same canonical brief payload, canonical brief hash, and humanization version.
- Humanization version is part of replay identity.
- Humanization must not:
  - add claims,
  - remove material limitations,
  - intensify confidence,
  - hide evidence existence,
  - introduce advice, causality, diagnosis, or prediction.
- Humanized blocks must remain traceable back to canonical finding identifiers.

## 26.6 UX scope
- Inquiry becomes humanized-by-default with a collapsed but accessible canonical/technical brief.
- Forbidden UI patterns in Phase 10:
  - chat bubbles or assistant transcripts,
  - fake conversational framing,
  - multiple competing panels,
  - dashboard overload,
  - hiding technical access behind obscure navigation.

## 26.7 Docs and execution references
- Required updates:
  - `lifeos/docs/ui_ux_constitution.md`
  - `lifeos/docs/semantics/INSIGHT_CONTRACTS.md`
  - `lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md`
  - `lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md`
- `lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md` remains unchanged.
- Execution reference: `lifeos/docs/tasks/phase_10_insight_humanization_layer.md`

---

# 27. Phase 11 First-Run Onboarding (Constitutional Decision, Binding)

Phase 11 introduces a first-run onboarding wizard that activates once after a user's first login. It collects domain preferences, calendar source selection, and marks the user as onboarded — all stored via the existing `UserPreference` key-value system with zero migration cost.

## 27.1 Phase objective
- Provide a guided first-run experience that collects user intent (which domains to activate, which calendar source to connect) before exposing the full application surface.
- Onboarding must only trigger once per user (first login) and redirect to the calendar view upon completion.

## 27.2 Storage model
- All onboarding state persisted via `UserPreference` (existing generic key-value JSON store).
- Keys used:
  - `onboarding_domains` → `{"selected": ["finance", "calendar", ...]}`
  - `onboarding_calendar_source` → `{"provider": "google" | "apple" | "skip"}`
  - `onboarding_completed` → `{"v": true}`
- No new tables, no migration required.

## 27.3 Backend surface
- **Domain:** `lifeos/core/users/` (extends existing user module, not a new domain)
- **Endpoints:**
  - `GET /api/users/me/onboarding-status` — returns `{completed, domains, calendar_source}`
  - `POST /api/users/me/onboarding` — accepts `{step, data}` where step is `domains|calendar|complete`
- **Event:** `user.onboarding.completed` emitted when step=`complete` with `payload_version: 1`
- **Schemas:** `OnboardingStatusResponse`, `OnboardingStepRequest` (Pydantic DTOs in `users/schemas.py`)
- **Services:** `get_onboarding_status()`, `save_onboarding_step()` in `users/services.py`

## 27.4 Frontend surface
- **Route group:** `frontend/app/(onboarding)/` — separate layout, no sidebar
- **Steps:**
  1. Domain selection (multi-select cards for Finance, Health, Habits, Skills, Calendar, Projects, Relationships, Journal)
  2. Calendar source (Google or Apple, with skip option)
  3. Animated processing screen (deterministic, no real computation — visual transition only)
  4. Redirect to `/calendar`
- **Auth guard:** `(app)/layout.tsx` checks `user.onboarding_completed`; redirects to `/onboarding` if false
- **Login redirect:** Post-login target changes from `/insights/data` to `/calendar`
- **Design:** Follows Botanical Editorial — sage palette, Newsreader headlines, pill buttons, glassmorphism header, clipped-specimen cards for domain selection

## 27.5 Boundaries
- Onboarding does NOT initiate actual calendar sync (that is Phase 2 Calendar-First).
- Domain selection records intent only — it does not enable/disable backend features.
- The processing screen is purely visual (animated transition), not a real computation.
- Onboarding state is read-only after completion; no re-onboarding flow in this phase.

## 27.6 Docs and execution references
- Governing design: `DESIGN.md` lines 296–309 (onboarding page spec)
- UI binding: `lifeos/docs/ui_ux_constitution.md`
- User preference system: `lifeos/core/users/preferences.py`

---

# 28. Private Alpha Product Cut (Constitutional Decision, Binding)

Private alpha is a tightly scoped, invite-only, inquiry-first release for 10–30 users. It is not a broad feature release and it is not a general assistant launch.

## 28.1 Product thesis
- LifeOS private alpha exists to test whether users repeatedly trust and return to structured, evidence-based inquiry about their own records when the product is:
  - calm,
  - readable,
  - traceable,
  - non-chat.
- The product is not positioned as an AI companion, coach, or general assistant.

## 28.2 User-visible alpha surface
- Alpha is inquiry-first and humanized-by-default.
- Primary user-visible surfaces:
  - invite and account access
  - onboarding and data readiness
  - inquiry creation
  - inquiry result view
  - technical brief expansion
  - refine flow
  - inquiry history
  - explicit feedback submission
- General-purpose domain CRUD surfaces are not part of the primary alpha experience.

## 28.3 Domain scope
- Wave 1 (live in alpha): calendar, habits, projects, skills
- Wave 2 (hidden / disabled by default): finance, journal
- Later (not part of alpha): health, relationships
- Alpha cross-domain scope is limited to approved Wave 1 pairs:
  - projects + calendar
  - projects + skills

## 28.4 Required alpha features
- Must-have for launch:
  - invite-only access
  - structured inquiry submission
  - humanized brief view
  - canonical technical brief access
  - refine flow
  - inquiry history
  - explicit inquiry feedback capture
  - first-wave single-domain timeline interpretation
  - approved-pair cross-domain inquiry for wave-1 pairs only
- Deferred from alpha:
  - open-ended chat
  - public signup
  - broad domain exposure
  - recommendation or coaching behavior
  - predictive or causal surfaces

## 28.5 Operational boundaries
- Deployment target is low-cost, high-reliability private alpha infrastructure, not public-scale architecture.
- Invite-only is mandatory.
- User cap is operationally small and intentionally enforced.
- Feature failures must degrade to narrower inquiry behavior, not to free-form assistant behavior.

## 28.6 Docs and execution reference
- Execution brief: `lifeos/docs/tasks/private_alpha_architecture_cut.md`
- UI binding remains governed by `lifeos/docs/ui_ux_constitution.md`.

---

# 29. Phase 12 — Habit UX & Analytics (Planned)

_20 tickets (HAB-001 through HAB-020) across 4 sub-phases. Extends the habits domain with streak visualization, materialized analytics, engagement feedback loops, desktop master-detail layout, and ML prediction foundation._

## 29.1 Motivation
The habits domain has a complete backend lifecycle (CRUD, logging, streaks, events) but the frontend surfaces raw data with minimal psychological engagement. Habit apps succeed through cue→action→reward loops. This phase adds the reward layer (streaks, animations, milestones), the cue layer (time-aware nudges), and the analytical infrastructure to power future intelligence.

## 29.2 Sub-phases

### Phase 12a — Quick Wins (HAB-002, HAB-003, HAB-008, HAB-009)
**Scope:** Frontend-only. No backend/DB changes.
- **HAB-002**: Fix timestamp display — replace raw GMT strings with relative time (`Today`, `Yesterday`, `3 days ago`, `Mar 18`)
- **HAB-003**: Redesign LOG button as primary CTA — filled olive/navy, min 44px touch target, hover/press animation
- **HAB-008**: Standardize spacing to 8px grid (8, 16, 24, 32, 48, 64px increments)
- **HAB-009**: Reduce "Your Habits" section header weight — subordinate to habit names in visual hierarchy

### Phase 12b — Core Features (HAB-014, HAB-015, HAB-017, HAB-001, HAB-004)
**Scope:** DB migration + backend streak engine + QA + frontend streak display.
- **HAB-014**: Migration `20260321_habit_stat_table.py` — new `habit_stat` table (see ERD §3)
- **HAB-015**: Streak calculation service — timezone-aware day boundary, gap detection, configurable grace period, recalculates on log insert/delete
- **HAB-017**: Streak accuracy test suite — timezone, DST, backdated, concurrent, grace period edge cases
- **HAB-001**: Streak counter on habit card — prominent number with flame icon, persists across sessions
- **HAB-004**: DONE badge + LOG button state conflict — LOG transforms to "Undo" when completed today; backend supports log deletion for undo

### Phase 12c — Engagement Layer (HAB-005, HAB-006, HAB-010, HAB-011, HAB-013)
**Scope:** Analytics API endpoints + frontend engagement features.
- **HAB-013**: Analytics API endpoints:
  - `GET /api/habits/<id>/stats` → {current_streak, longest_streak, completion_rate_30d, total_logs}
  - `GET /api/habits/<id>/history?range=7d|30d|90d` → [{date, logged, value?}, ...]
  - `GET /api/habits/<id>/heatmap?year=2026` → [{date, logged}, ...] (365 entries)
  - All endpoints: JWT auth, user-scoped, response time < 200ms
- **HAB-005**: 7-day completion dot row — horizontal dots (Mon–Sun or rolling 7), filled=completed, empty=missed
- **HAB-006**: Completion rate percentage — `X% this month` computed from habit_stat; ML team stores as training feature
- **HAB-010**: Logging micro-animation — checkmark (200–400ms), streak counter increment animation, milestone celebrations (7/30/100-day confetti)
- **HAB-011**: Empty state redesign — illustration, motivational copy, primary CTA, optional starter habit suggestions

### Phase 12d — Desktop & Intelligence (HAB-007, HAB-012, HAB-016, HAB-018, HAB-019, HAB-020, HAB-022, HAB-023)
**Scope:** Desktop layout, time-aware cues, ML foundation, UX polish, QA, DevOps.

#### HAB-022: Card UX Polish (Frontend-only)
- **Log button icon:** Add `Check` (lucide-react) icon to the left of "LOG" text; add `Undo2` icon to the left of "Undo" text
- **Completed card dimming:** Completed-today cards get `opacity: 0.65` on the card body EXCEPT the streak badge (streak badge stays full opacity via `opacity: 1` override). Achieves "done, move on" visual hierarchy.
- **Log button hover suppression:** When `completed_today === true` (Undo state), remove `translateY`/`scale`/`boxShadow` hover effects — the button should feel inert, not inviting.
- **Delete confirmation dialog:** When the user clicks the delete button (trash icon) on a habit card, show a confirmation dialog (`AlertDialog` from shadcn/ui) with: habit name in the message body, destructive-styled "Delete" button, neutral "Cancel" button. Do NOT delete without confirmation. Dialog copy: "This will permanently delete **{habit name}** and all its logs. This cannot be undone."

#### HAB-007: Master-detail split layout (desktop)
- **Layout structure:** At `≥1024px`, the habits page becomes a two-panel layout:
  - **Left panel (60%):** Existing habit card list (scrollable)
  - **Right panel (40%):** Detail panel for the currently selected habit
- **Selection model:** Clicking a habit card selects it (adds `selectedHabitId` state). On desktop, the right detail panel updates in place. On mobile/tablet (<1024px), tapping a card opens a detail drawer/sheet for analytics and scheduled-time editing.
- **Detail panel contents:** Streak chart (line chart of 30-day history from `/history?range=30d`), yearly heatmap (from `/heatmap`), stats summary (from `/stats`), habit description/notes.
- **Components:**
  - `HabitDetailPanel` at `frontend/app/(app)/habits/_components/HabitDetailPanel.tsx` — the right panel container
  - `HabitHeatmap` at `frontend/app/(app)/habits/_components/HabitHeatmap.tsx` — yearly calendar heatmap (GitHub-style, sage palette)
  - `HabitStreakChart` at `frontend/app/(app)/habits/_components/HabitStreakChart.tsx` — 30-day line/bar chart
- **Responsive collapse:** Below 1024px, only the card list renders. The detail panel is conditionally rendered via CSS (`hidden lg:block`) or a media query check.
- **Empty selection state:** When no habit is selected (or on initial load on desktop), the detail panel shows a placeholder: "Select a habit to see its analytics" with a leaf illustration or subtle icon.

#### HAB-012: Time-aware cue messaging
- **Migration 2 required:** `20260322_habit_scheduled_time.py` — adds `scheduled_time` (Time, nullable) to `habits_habit`
- **Backend:** Add `scheduled_time` to `HabitCreate`, `HabitUpdate`, `HabitSummaryResponse`, and `HabitDetailResponse` schemas. Expose in list endpoint payload.
- **Frontend cue logic:** For habits with `scheduled_time` set:
  - Before scheduled time: show "Due in Xh Ym" in muted sage (`#5a6157`)
  - Within 30 minutes: show "Due soon" in amber (`#b8860b`)
  - After scheduled time (not logged): show "Overdue by Xh" in earthy coral (`#e8735c`)
  - Already logged today: no cue shown (the card is already dimmed)
- **Cue placement:** Below the 7-day dot row, same row as completion rate
- **Time computation is client-side only.** The server stores `scheduled_time`; the frontend computes relative time using the user's local clock.

#### HAB-023: Habit Studio create-flow refinement (Frontend-only)
- **Create flow container:** Replace inline create form with a centered modal "Habit Studio" over the habits page.
- **Layout:** Two-panel modal (`lg:grid-cols-5`) with form on the left (`3/5`) and live reflection panel on the right (`2/5`).
- **Terminology:** Use **Frequency** instead of **Schedule** in the create flow labels and preview copy.
- **Preferred time input:** Use a concise single-block native `type="time"` control in Habit Studio across desktop/mobile. Persist canonical `scheduled_time` to backend and render a localized, human-friendly preview in the reflection panel.
- **Live reflection:** Right panel updates immediately from in-progress form state (name, frequency, preferred time, description).
- **Encouraging copy model:** Base/near-ready/ready states are selected by readiness signals (action-focused name, frequency selected, time cue enabled, description context).
- **Rotating guidance tip:** Bottom tip rotates every 5s with fade transition (same cadence pattern as auth testimonial rotation style).
- **Visual language:** Modal and reflection panel align to habits blue accents (`#3a5272` / `#2e4460`), while preserving Botanical Editorial typography and clipped corners.
- **Localization:** All Habit Studio reflection/encouragement copy and labels are localized for English, Korean, and Chinese.
- **Dismiss behavior:** Modal closes via backdrop click, `Esc`, and Cancel button. No dedicated top-right close icon.

#### HAB-016: Habit completion prediction model (foundation)
- **Location:** `lifeos/domains/habits/ml/habit_prediction.py` (replace existing stub)
- **Features:** `day_of_week` (0–6), `streak_length` (int), `completion_rate_7d` (float 0–1), `hours_since_last_log` (float)
- **Model:** Logistic regression (scikit-learn `LogisticRegression`) — simplest baseline, deterministic, versioned
- **Training:** Offline CLI script `lifeos/scripts/train_habit_model.py` reads from `habit_stat` + `habit_log`, trains per-user model, serializes to versioned artifact
- **Evaluation:** AUC > 0.7 on held-out test set (80/20 split)
- **Output:** `P(completion_today)` float 0.0–1.0, stored in a new `habit_prediction` column on `habit_stat` (nullable float). NOT surfaced to users in this phase.
- **Determinism rule:** `model_version` string stored alongside prediction. Same features + same model_version → same prediction.
- **No migration for prediction storage in this phase.** Store in-memory only during batch run; persist to `habit_stat.predicted_completion` in Phase 13 when the column is added.

#### HAB-018: Cross-device responsive testing (QA)
- **Breakpoints to verify:** 375px (mobile S), 414px (mobile L), 768px (tablet), 1024px (breakpoint boundary), 1440px (desktop)
- **Checkpoints:** Touch target ≥44px, animation frame budget <16ms, no horizontal scroll, text legible without zoom, master-detail collapse at 1023px
- **Automation:** Playwright viewport matrix test in `lifeos/tests/e2e/` (if e2e infra exists) or manual QA checklist

#### HAB-019: CI/CD for analytics pipeline (DevOps)
- **Migration CI:** Add analytics migration check to PR pipeline — verify `alembic heads` returns single head, `alembic upgrade head` succeeds on test DB
- **API integration tests:** Add habit analytics endpoints to integration test suite — verify `/stats`, `/history`, `/heatmap` return correct shapes and user-scoped data
- **ML validation gate:** Add model training smoke test to CI — train on fixture data, assert AUC > 0.6 (relaxed for CI fixture data), assert output shape

#### HAB-020: Performance monitoring (DevOps)
- **APM:** Add timing middleware or decorator to analytics endpoints (`/stats`, `/history`, `/heatmap`)
- **Alerting:** p95 > 200ms triggers warning; p95 > 500ms triggers alert
- **Slow query log:** Log queries exceeding 100ms in analytics endpoints at WARNING level

## 29.3 DB changes

### Migration 1: `20260321_habit_stat_table.py`
**New table: `habit_stat`**
| Column | Type | Constraints |
|--------|------|-------------|
| id | Integer | PK, autoincrement |
| habit_id | Integer | FK → habits_habit.id, UNIQUE, NOT NULL, ON DELETE CASCADE |
| user_id | Integer | FK → user.id, NOT NULL, indexed |
| current_streak | Integer | NOT NULL, default 0 |
| longest_streak | Integer | NOT NULL, default 0 |
| completion_rate_30d | Float | nullable, 0.0–1.0 |
| total_logs | Integer | NOT NULL, default 0 |
| last_logged_at | Date | nullable |
| updated_at | DateTime | NOT NULL, default utcnow, onupdate utcnow |

- **Backfill:** After table creation, backfill from existing `habit_log` data using the streak calculation service.
- **Depends on:** none (additive)

### Migration 2: `20260322_habit_scheduled_time.py`
**Alter table: `habits_habit`**
- ADD COLUMN `scheduled_time` (Time, nullable) — precise scheduled time for cue messaging
- Existing `time_of_day` (varchar) retained for backward compatibility
- **Depends on:** none (additive)

## 29.4 New events
| Event | Payload | Version | Trigger |
|-------|---------|---------|---------|
| `habits.stat.recomputed` | {habit_id, user_id, current_streak, longest_streak, completion_rate_30d, total_logs} | v1 | After log create/delete when stat row is recalculated |
| `habits.habit.streak_milestone` | {habit_id, user_id, streak_length, milestone_type (7\|30\|100), achieved_at} | v1 | When streak crosses a milestone threshold |

- `habits.habit.streak_milestone` feeds `habits_rules.py` in the insights engine for milestone notifications.

## 29.5 New API endpoints (Phase 12c)
All under existing blueprint prefix `/api/habits`. JWT auth required.
| Method | Path | Response | Notes |
|--------|------|----------|-------|
| GET | `/<id>/stats` | `HabitStatsResponse` | Reads from `habit_stat` table |
| GET | `/<id>/history` | `HabitHistoryResponse` | Query params: `range` (7d\|30d\|90d), paginated |
| GET | `/<id>/heatmap` | `HabitHeatmapResponse` | Query params: `year` (int), returns 365 entries |

## 29.6 Frontend surface

### Phase 12a (frontend-only)
- **Location:** `frontend/app/(app)/habits/page.tsx`
- **Changes:** Timestamp formatting utility, LOG button redesign, 8px grid spacing, section header hierarchy

### Phase 12b–c (new components)
- **Location:** `frontend/app/(app)/habits/` + `frontend/components/habits/`
- **New components:**
  - `StreakBadge` — flame icon + streak count with animation
  - `CompletionDots` — 7-day dot row
  - `CompletionRate` — percentage display
  - `LogAnimation` — micro-animation on log action
  - `HabitEmptyState` — motivational empty state
  - `HabitDetailPanel` — right panel for master-detail (Phase 12d)
  - `HabitHeatmap` — yearly heatmap visualization (Phase 12d)

### Phase 12d (layout + polish)
- **HAB-022 (frontend-only):** Log button icon (Check/Undo2), completed card dimming (opacity 0.65 except streak), hover suppression on Undo button, delete confirmation AlertDialog
- **HAB-007:** Master-detail: `frontend/app/(app)/habits/page.tsx` restructured with split layout (60/40 at ≥1024px, single column below)
- **New components** (all under `frontend/app/(app)/habits/_components/`):
  - `HabitDetailPanel.tsx` — right panel container, consumes `/stats`, `/history`, `/heatmap` via React Query
  - `HabitHeatmap.tsx` — yearly calendar heatmap (GitHub-style, sage-green fills)
  - `HabitStreakChart.tsx` — 30-day history line/bar visualization
- **HAB-012:** Time-aware cue messaging — relative time display below dot row, client-side computation from `scheduled_time` field
- **HAB-023:** Habit Studio modal create flow — frequency-first terminology, concise native preferred-time input with localized preview, multilingual encouraging live copy, rotating guidance tip, blue-aligned reflection panel

## 29.7 ML surface (Phase 12d)
- **Location:** `lifeos/domains/habits/ml/habit_prediction.py` (replace existing stub)
- **Features:** day_of_week, streak_length, completion_rate_7d, hours_since_last_log
- **Model:** Logistic regression or lightweight gradient boosting
- **Training:** Offline batch from `habit_stat` + `habit_log`
- **Evaluation:** AUC > 0.7 on held-out test set
- **Output:** Probability of completion today (0.0–1.0), stored but not surfaced to users in this phase
- **Determinism rule:** Model is versioned; same features + same model version → same prediction

## 29.8 Dependencies
```
Phase 12a → (no deps, ship immediately) ✅ DONE
Phase 12b → HAB-014 (DB) → HAB-015 (service) → HAB-017 (QA) → HAB-001 (FE+BE) → HAB-004 (FE+BE) ✅ DONE
Phase 12c → HAB-013 (API) depends on HAB-014; HAB-010 depends on HAB-001 + HAB-003 ✅ DONE
Phase 12d execution order:
  HAB-022 (FE polish) → no deps, ship first
  HAB-012 (time cues) → depends on Migration 2 (DB) → then BE schema update → then FE cue display
  HAB-007 (master-detail) → depends on HAB-005 + HAB-006 (✅ done) + HAB-013 (✅ done); ship after HAB-022
  HAB-023 (Habit Studio refinement) → FE-only; depends on HAB-007 + HAB-012 baseline interactions
  HAB-016 (ML) → depends on HAB-014 (✅ done) + HAB-013 (✅ done); can run in parallel with HAB-007
  HAB-018 (QA) → depends on HAB-007 + HAB-012 completion; final verification
  HAB-019 (CI/CD) → can start in parallel with HAB-007
  HAB-020 (monitoring) → can start in parallel with HAB-007
```

## 29.9 Boundaries
- Streak calculation is deterministic: facts from logs only, no inference or prediction.
- ML prediction (HAB-016) outputs are stored but NOT surfaced to users in this phase. No predictive claims in the UI.
- `scheduled_time` is user-set only; no AI-suggested scheduling.
- Milestone celebrations are client-side only (no server-rendered notifications in this phase).
- Master-detail layout does NOT introduce a new route; it's a layout change within `/habits`.
- Analytics endpoints serve the UI; they do NOT power external dashboards or exports.
- Habit Studio preferred-time input remains a presentation-layer UX decision; backend `scheduled_time` remains canonical 24-hour time semantics.

## 29.10 Docs and execution references
- Ticket board: `lifeos_habit_improvements.xlsx` (20 tickets, HAB-001 through HAB-020)
- UI binding: `lifeos/docs/ui_ux_constitution.md` §5 Habits contract
- Design: `DESIGN.md` (Botanical Editorial tokens)
- Semantic contract: `lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md` §Habits

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
