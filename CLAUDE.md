# LifeOS — Claude Code Instructions

## Project Overview

LifeOS is a full-stack intelligent life-management platform. It rejects cold productivity software in favor of a thoughtful, editorial experience built on deterministic intelligence.

- **Backend:** Flask 3.x + SQLAlchemy 3.1 + PostgreSQL 16 (SQLite dev) + Redis
- **Frontend:** Next.js 16 + React 19 + TypeScript + Tailwind v4 + shadcn/ui
- **Architecture:** Domain-driven, event-sourced, read/write separation
- **Design:** "The Botanical Editorial" — sage palette, Newsreader + Manrope, glassmorphism
- **Auth:** JWT (API) + Session (cookies) + CSRF (future migration to Clerk planned)

---

## Repository Structure

```
finance_app_clean/
├── CLAUDE.md                  # This file — project-level AI context
├── DESIGN.md                  # Visual design system (Botanical Editorial)
├── docs/                      # Root-level architecture & decision records
│   ├── architecture.md        # → symlink to lifeos/docs/lifeos_architecture.md
│   ├── decisions/             # Architecture Decision Records (ADRs)
│   └── runbooks/              # Operational runbooks
│
├── .claude/
│   ├── settings.local.json    # Permission config
│   ├── hooks/                 # Guardrails and automation checks
│   └── skills/                # Reusable AI workflows
│       ├── architect/         # System architect role
│       ├── backend/           # Backend implementation role
│       ├── frontend/          # Frontend implementation role
│       ├── db/                # Database & migration role
│       ├── devops/            # CI/CD & infrastructure role
│       └── qa/                # Testing & quality role
│
├── tools/
│   └── prompts/               # Reusable prompt templates
│
├── lifeos/                    # Backend source (Flask)
│   ├── CLAUDE.md              # Backend-specific AI context
│   ├── domains/               # 8 domain modules (write models)
│   ├── core/                  # Cross-cutting platform layer
│   ├── lifeos_platform/       # Infrastructure services
│   ├── readmodels/            # Read models (projections)
│   ├── migrations/            # Alembic migrations (single home)
│   ├── docs/                  # Detailed architecture docs
│   ├── tests/                 # 539+ tests (unit/integration/ml)
│   └── scripts/               # CLI tools
│
├── frontend/                  # Frontend source (Next.js)
│   ├── CLAUDE.md              # Frontend-specific AI context
│   ├── app/                   # Next.js App Router pages
│   ├── components/            # Reusable UI components
│   └── lib/                   # Utilities, API client, auth
│
├── deploy/                    # Docker, k8s, monitoring configs
├── .github/workflows/         # CI/CD pipelines
└── flask_app/                 # IGNORE — unrelated legacy app
```

---

## Conventions

### General Rules
- **flask_app/ is off-limits.** It is a separate, unrelated application. Never read, modify, or reference it.
- **Deterministic intelligence only.** All insights and interpretations are rule-based, replay-safe. No ML autonomy.
- **Additive migrations only.** Never drop columns, rename in place, or delete tables.
- **Events are versioned.** Every event payload has `payload_version`. Breaking changes = new event name.
- **API is versioned.** All routes under `/api/v1/`. Pydantic DTOs for request/response.

### Naming Conventions
- **Migrations:** `YYYYMMDD_short_snake_description.py`
- **Events:** `domain.entity.action` (e.g., `finance.transaction.created`)
- **Endpoints:** `/api/v1/{domain}/{resource}`
- **Models:** PascalCase singular (`Transaction`)
- **Tables:** snake_case singular (`transaction`)
- **Feature flags:** `ENABLE_PHASE{N}_{FEATURE_NAME}`

### Architecture Patterns
- **Domain modules:** `lifeos/domains/{domain}/` — each with models/, controllers/, services/, schemas/, events.py, tasks/
- **Core layer:** `lifeos/core/` — auth, events, insights, interpreter, timeline, observability
- **Platform layer:** `lifeos/lifeos_platform/` — outbox, worker, broker, clients
- **Read models:** `lifeos/readmodels/` — projections, runners, registry

### Testing
- All tests carry markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.ml`
- Coverage minimum: 85%
- Run tests: `python -m pytest lifeos/tests/ --ignore=flask_app`

---

## Governing Documents

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` (this file) | Project-level AI context |
| `DESIGN.md` | Visual design system |
| `lifeos/docs/lifeos_architecture.md` | **The Constitution** — normative architecture |
| `lifeos/docs/backend_overview.md` | Stakeholder-facing backend summary |
| `lifeos/docs/ui_ux_constitution.md` | UI/UX interaction rules |
| `lifeos/docs/CI_CD_ARCHITECTURE.md` | Pipeline design |
| `lifeos/docs/semantics/` | Domain contracts, event semantics, insight contracts |

---

## Skills (`.claude/skills/`)

Invoke skills by name to activate specialized roles:

| Skill | Role | What it does |
|-------|------|--------------|
| `architect` | System Architect | High-level architecture, ERD, domain boundaries, events, migrations. Updates the constitution. Never writes code. |
| `backend` | Backend Engineer | Implements Flask domains, services, controllers, events. Follows the constitution. |
| `frontend` | Frontend Engineer | Implements Next.js pages, components, API integration. Follows DESIGN.md. |
| `db` | Database Engineer | Writes migrations, optimizes queries, manages schema evolution. |
| `devops` | DevOps Engineer | CI/CD, Docker, monitoring, deployment, infrastructure. |
| `qa` | QA Engineer | Test strategy, acceptance criteria, regression testing, coverage. |

---

## Domain Map

```
lifeos/domains/
├── calendar/       # Calendar events, external sync (Google/Apple), interpretations
├── finance/        # Accounts, journal entries, transactions, forecasts, loans
├── journal/        # Personal entries, mood, tags, signals for insights
├── projects/       # Projects, tasks, task logs
├── habits/         # Habit definitions, logs, streaks, metrics
├── health/         # Biometrics, workouts, nutrition
├── relationships/  # People, interactions, reconnect cues
└── skills/         # Skills, practice sessions, metrics
```

Each domain owns its data. Cross-domain communication happens through events only. One emitter per event. Read models project across domains for query needs.
