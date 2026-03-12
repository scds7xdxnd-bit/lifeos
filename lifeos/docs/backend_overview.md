# LifeOS Backend Overview (Stakeholder Edition)

## Department scope and boundaries
- Owns the server-side platform for LifeOS: API surface, domain logic, persistence, events, and operational controls.
- Owns cross-domain intelligence infrastructure (insights, interpreter, contracts, read models, observability).
- Owns database schemas and migrations (additive-only via Alembic).
- Owns runtime services (web app, worker dispatcher) and service-to-service integration points.

## Backend owns vs does not own
Backend owns:
- Domain APIs and business logic for Calendar, Finance, Journal, Projects, Habits, Health, Relationships, Skills, and Insights.
- AuthN/AuthZ (JWT + session hybrid, roles/permissions, password reset).
- Database schemas, migrations, and data integrity constraints.
- Event system (event bus, outbox) and worker runtime.
- Read model scaffolding and read-through cache for projections.
- Operational docs, runbooks, and contract governance docs.

Backend does not own:
- UI/UX design and frontend interaction details (governed by UI/UX constitution).
- Mobile, offline, and client sync strategies (explicitly deferred).
- External broker selection (broker is a stub; real broker deferred post-v1).
- ML personalization or autonomous assistant behavior (framework only; rules-based only).

## Service and domain boundaries
- Core: auth, users/prefs, roles/permissions, events, insights engine, interpreter, app factory, worker runtime, outbox.
- Calendar: events, external sync, interpretations, tagging, deterministic views (day/week/month/ledger).
- Finance: accounts, journal entries/lines, transactions, schedules/forecasts, receivables/loans, trial balance.
- Journal: personal entries with mood/tags and signals for insights.
- Projects: projects, tasks, task logs, lifecycle events.
- Habits: habit definitions, logs, streaks, metrics.
- Health: biometrics, workouts, nutrition logs.
- Relationships: people, interactions, reconnect cues.
- Skills: skills, practice sessions, metrics.
- Insights and Interpretations: rule-based insights pipeline, confidence routing, interpreter outputs, and review flows.

## System architecture map (backend view)
```
Client (Web UI)
   |
   v
Flask API (controllers + auth + rate limiting)
   |
   v
Domain Services
   |
   v
SQLAlchemy ORM (repository boundary) -> PostgreSQL (prod) / SQLite (dev)
   |
   v
Outbox (durable events) -> Worker Dispatcher -> Event Bus -> Handlers (Insights, Interpreter)
```

## Request flow
```
Client -> API route -> Auth (JWT/session + roles) -> Controller -> Service -> ORM queries -> DB
```
- Repository layer is the ORM query boundary inside services (no separate repository folder).

## Event and queue usage
- Producers: domain services emit events to the platform outbox and optionally to the in-process event bus.
- Consumers: worker dispatcher reads outbox and publishes to the event bus for handlers (insights, interpreter, domain listeners).
- Topics: domain-scoped event types (for example, calendar.event.created, finance.journal.entry.created).
- Retry/DLQ policy: outbox statuses pending -> sending -> sent/failed/dead with exponential backoff and retry limits.
- Audit: event_record stores canonical event history.

## Read models vs write models
- Write models are the domain tables (CalendarEvent, JournalEntry, Account, etc).
- Read models are defined in readmodels/ and used for read-only projections.
- Read-through cache exists for high-read endpoints; invalidated on relevant writes.

## Codebase structure (top 3 levels)
```
/
├── lifeos/
│   ├── core/                # Auth, events, insights, interpreter, utils, admin
│   ├── domains/             # Calendar, Finance, Journal, Projects, Habits, Health, Relationships, Skills
│   ├── lifeos_platform/     # Outbox, worker runtime, broker stubs, clients
│   ├── readmodels/          # Projection scaffolding and contracts
│   ├── migrations/          # Alembic migrations (app-local)
│   ├── templates/           # Server-rendered UI templates
│   ├── static/              # Frontend assets (CSS/JS)
│   ├── tests/               # Unit/integration/contract tests
│   └── docs/                # Architecture, contracts, runbooks, tasks
├── deploy/                  # Monitoring, dashboards, infra configs
├── scripts/                 # Ops scripts and smoke tests
└── migrations/              # Root Alembic home for repo
```

## Contracts and interfaces
- API schemas and DTOs: lifeos/domains/*/schemas/ and lifeos/core/*/schemas.
- Domain semantic contracts: lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md
- Event semantics freeze: lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md
- Insight contracts: lifeos/docs/semantics/INSIGHT_CONTRACTS.md
- Confidence vocabulary: lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md
- DSDs and alignment checklists: lifeos/docs/tasks/ (archived when complete).

## Data model ownership (by domain)
- Core: User, UserPreference, Role, Permission, PasswordResetToken, SessionToken, JWTBlocklist, InsightRecord, EventRecord.
- Calendar: CalendarEvent, CalendarEventInterpretation, CalendarOAuthToken.
- Finance: Account, AccountCategory, JournalEntry, JournalEntryLine, Transaction, TrialBalance, MoneyScheduleRow, Receivable, Loan.
- Journal: JournalEntry (text, mood, tags).
- Projects: Project, ProjectTask, ProjectTaskLog.
- Habits: Habit, HabitLog, HabitStreak, HabitMetric.
- Health: Biometrics, Workout, NutritionLog.
- Relationships: Person, Interaction, ReconnectCue.
- Skills: Skill, PracticeSession, SkillMetric.

## User scoping and tenancy
- All domain tables are scoped by user_id.
- Controllers always derive user_id from JWT/session identity and filter queries by user_id.
- Roles and permissions gate writes (for example, calendar:write, finance:write).

## Cross-cutting concerns
- AuthN/AuthZ: JWT + session hybrid, roles/permissions, CSRF on session-bound writes.
- Validation: Pydantic schemas for request bodies and query params.
- Rate limiting: Flask-Limiter applied per endpoint.
- Idempotency: external sync uses unique external_id per user to deduplicate calendar imports.
- Read-only guard: read-only endpoints are protected from writes.

## Observability
- Logs: application logs from Flask and worker runtime.
- Metrics: Prometheus metrics exposed by the app, SLO alerts defined in ops runbooks.
- Telemetry: in-memory insight/inference telemetry snapshots for admin debugging.

## Error taxonomy and standard payloads
- Standard JSON error shape:
  - { "ok": false, "error": "<code>", "details": [...] }
- Common error codes: validation_error, not_found, forbidden, unauthorized, csrf_failed, contract_mismatch, read_only_violation.

## Deployment and runtime model (backend slice)
- Web app: Flask app served via Gunicorn.
- Worker: separate dispatcher process consuming outbox events.
- Database: PostgreSQL in production, SQLite in dev.
- Monitoring: Prometheus and Grafana dashboards in deploy/monitoring.
- Scheduled tasks: calendar sync can be triggered via CLI (flask sync-calendars) and run under ops scheduling.

## Team operating model
- Work split primarily by domain (Calendar, Finance, Journal, Projects, Habits, Health, Relationships, Skills).
- Platform capability team owns Core (auth, events, insights, interpreter, outbox, readmodels).
- DevOps owns CI/CD, deployments, and monitoring pipelines.

## Definition of done and required artifacts
- Code changes include tests (unit/integration/contract) and pass CI.
- Migrations are additive, versioned in Alembic, and documented.
- Architecture and semantic contracts updated when behavior changes.
- Ops runbooks updated when new metrics or SLOs are introduced.

## One-page summary table
| Component | Responsibility | Interfaces | Persistence | SLO/SLI |
|---|---|---|---|---|
| API (Flask) | HTTP entrypoint, auth, routing | /api/v1/*, /health, /api/v1/ping | None | API latency p95, error rate |
| Auth | Login, tokens, roles, CSRF | /api/v1/auth/* | User, SessionToken, JWTBlocklist | Auth failure rate |
| Domain Services | Business logic per domain | /api/* domain routes | Domain tables | Request success rate |
| Outbox | Durable event storage | Outbox enqueue/dispatch | platform_outbox | Dispatch success rate |
| Worker Dispatcher | Async delivery and retries | Event bus publish | Outbox status | Retry rate, DLQ rate |
| Event Bus | In-process handlers | event_type catalog | EventRecord | Handler latency |
| Insights Engine | Rule-based insight generation | /api/v1/insights/* | InsightRecord | Insight latency p95 |
| Interpreter | Calendar classification | calendar.event.* events | Inferred fields | Classification throughput |
| Read Models/Cache | Projection reads | readmodels/*, cached reads | Read cache, readmodel tables | Projection correctness |
| Database | Source of truth | SQLAlchemy ORM | PostgreSQL/SQLite | Migration success |
| Observability | Metrics and logs | /metrics, dashboards | Metrics store | SLO alerting coverage |
