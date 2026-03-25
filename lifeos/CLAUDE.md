# LifeOS Backend Context

This is the Flask backend for LifeOS. Read `lifeos/docs/lifeos_architecture.md` (the constitution) before making changes.

## Structure

```
lifeos/
├── core/              # Cross-cutting: auth, events, insights, interpreter, timeline
├── domains/           # 8 domain modules (calendar, finance, journal, projects, habits, health, relationships, skills)
├── lifeos_platform/   # Infrastructure: outbox, worker, broker, clients
├── readmodels/        # Read model projections and runners
├── migrations/        # Alembic migrations (single home — all versions here)
├── docs/              # Architecture docs, semantic contracts, runbooks
├── tests/             # Test suite with markers (unit/integration/ml)
├── templates/         # Jinja2 legacy templates
├── static/            # CSS/JS static assets
└── scripts/           # CLI tools (sync, runners)
```

## Domain Module Pattern

Every domain at `lifeos/domains/{domain}/` follows:
```
models/        → SQLAlchemy ORM (aggregate roots + entities)
controllers/   → Flask blueprints, routes, auth decorators
services/      → Business logic (ORM queries inline, no repo layer)
schemas/       → Pydantic request/response DTOs
events.py      → Domain events with payload_version
tasks/         → Optional background task definitions (present where needed)
```

## Key Rules
- No cross-domain imports. Communicate through events only.
- All routes under `/api/v1/`. Pydantic validation on all inputs.
- Tests require markers: `@pytest.mark.unit`, `@pytest.mark.integration`, `@pytest.mark.ml`
- Never import from `flask_app/` — it's unrelated.
- Run tests: `python -m pytest lifeos/tests/ --ignore=flask_app -x`
