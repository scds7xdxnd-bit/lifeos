# LifeOS CI/CD Runbook

**Owner:** DevOps Team  
**Last Updated:** 2025-12-07  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#1-overview)
2. [Pipeline Architecture](#2-pipeline-architecture)
3. [Ownership Matrix](#3-ownership-matrix)
4. [Local Development](#4-local-development)
5. [CI/CD Workflows](#5-cicd-workflows)
6. [Database Migrations](#6-database-migrations)
7. [Deployment Procedures](#7-deployment-procedures)
8. [Monitoring & Alerts](#8-monitoring--alerts)
9. [Troubleshooting](#9-troubleshooting)
10. [Secrets & Configuration](#10-secrets--configuration)

---

## 1. Overview

### Current CI/CD Design

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE FLOW                                      │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Developer        PR Pipeline         Main Pipeline        Release Pipeline │
│       │                │                    │                     │          │
│       ▼                ▼                    ▼                     ▼          │
│   ┌───────┐       ┌─────────┐         ┌─────────┐          ┌──────────┐     │
│   │ Local │──────▶│  PR     │────────▶│ Staging │─────────▶│Production│     │
│   │  Dev  │       │Validate │         │  Deploy │          │  Deploy  │     │
│   └───────┘       └─────────┘         └─────────┘          └──────────┘     │
│       │                │                    │                     │          │
│   make test       ~10 min              ~15 min              Manual Gate     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **CI runs migrations, never creates them** — DB team owns Alembic revisions
2. **All jobs call Makefile targets** — Consistency between local and CI
3. **Production requires manual approval** — Safety gate before deploy
4. **Dangerous migrations flagged** — Patterns like `drop_table` trigger review

---

## 2. Pipeline Architecture

### Workflow Files

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| PR Validation | `.github/workflows/lifeos-pr.yml` | Pull requests | Fast feedback, blocks merge |
| Main Build | `.github/workflows/lifeos-main.yml` | Push to main/develop | Full suite + staging deploy |
| Release | `.github/workflows/lifeos-release.yml` | Tag `v*.*.*` | Production with approval |
| Nightly | `.github/workflows/lifeos-nightly.yml` | 2 AM UTC | ML tests, dependency audit |

### CI Scripts

All scripts in `scripts/ci/` are called via Makefile:

```
scripts/ci/
├── lint.sh              # Ruff + Black
├── typecheck.sh         # Mypy
├── security.sh          # Bandit + Safety
├── test_unit.sh         # Fast unit tests
├── test_integration.sh  # DB integration tests
├── test_ml.sh           # ML model tests
├── test_all.sh          # Full suite
├── check_migrations.sh  # Alembic consistency
├── run_migrations.sh    # Apply migrations
├── smoketest.sh         # Health verification
├── build_image.sh       # Docker build
└── coverage_report.sh   # Coverage generation
```

---

## 3. Ownership Matrix

### Task Ownership

| Activity | DevOps | DB Team | Backend | QA |
|----------|:------:|:-------:|:-------:|:--:|
| Create Alembic migrations | ❌ | ✅ Owner | ❌ | ❌ |
| Review migration safety | ❌ | ✅ Owner | ⚠️ Consult | ❌ |
| Check migration consistency | ✅ CI | — | — | — |
| Run/apply migrations | ✅ CI | — | — | — |
| Write unit tests | ❌ | ❌ | ✅ Owner | ⚠️ Review |
| Write integration tests | ❌ | ❌ | ✅ Owner | ✅ Owner |
| Maintain CI pipelines | ✅ Owner | ❌ | ❌ | ❌ |
| Configure environments | ✅ Owner | ❌ | ❌ | ❌ |
| Approve production deploys | ⚠️ Consult | ❌ | ✅ Owner | ❌ |
| Monitor deployment health | ✅ Owner | ❌ | ⚠️ Consult | ❌ |

### Pending Configuration Tasks

| Task | Owner | Priority | Status |
|------|-------|----------|--------|
| Configure staging secrets in GitHub | DevOps (Admin) | P0 | ⏳ Pending |
| Configure production secrets in GitHub | DevOps (Admin) | P0 | ⏳ Pending |
| Set up environment protection rules | DevOps (Admin) | P0 | ⏳ Pending |
| Add CODECOV_TOKEN secret | DevOps (Admin) | P1 | ⏳ Pending |
| Test PR workflow end-to-end | DevOps | P0 | ⏳ Pending |
| Test staging auto-deploy | DevOps | P0 | ⏳ Pending |

---

## 4. Local Development

### Prerequisites

```bash
# Python 3.10+
python --version

# Virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
make install
```

### Running Tests Locally

```bash
# Quick unit tests (~5 min)
make test-unit

# Integration tests (requires DB)
DATABASE_URL=postgresql://user:pass@localhost/lifeos_test make test-integration

# Full suite
make test-all

# With coverage
make coverage
```

### Running Linters

```bash
# All linters
make lint

# Type checking
make typecheck

# Security scan
make security
```

### Running Migrations Locally

```bash
# Check migration consistency
make check-migrations

# Apply migrations (requires DATABASE_URL)
DATABASE_URL=postgresql://user:pass@localhost/lifeos make run-migrations
```

### Docker Development

```bash
# Start all services
make docker-up

# View logs
make docker-logs

# Stop services
make docker-down

# Build image
make build-image
```

---

## 5. CI/CD Workflows

### PR Pipeline (`lifeos-pr.yml`)

**Trigger:** Pull request to `main`, `develop`, or `release/*`

**Jobs:**
1. `lint` — Ruff + Black formatting (2 min)
2. `typecheck` — Mypy type checking (3 min)
3. `security` — Bandit + Safety scans (2 min)
4. `unit-tests` — Fast tests, coverage (5 min)
5. `migration-check` — Alembic consistency (1 min)
6. `integration-tests` — Optional, label-triggered (10 min)

**Quality Gates:**
- All required jobs must pass to merge
- Coverage uploaded to Codecov
- Dangerous migrations flagged for DB review

### Main Pipeline (`lifeos-main.yml`)

**Trigger:** Push to `main` or `develop`

**Jobs:**
1. `lint` + `security` — Quality gates
2. `unit-tests` — Matrix: Python 3.10, 3.11
3. `integration-tests` — Full DB tests
4. `build` — Docker image with SHA tag
5. `scan-image` — Trivy vulnerability scan
6. `deploy-staging` — Auto-deploy to staging
7. `smoke-test` — Health verification

### Release Pipeline (`lifeos-release.yml`)

**Trigger:** Tag `v*.*.*` (semver)

**Jobs:**
1. `validate-tag` — Semver format check
2. `full-test-suite` — All tests including slow
3. `build-prod` — Production image
4. `security-scan` — Full container scan
5. `deploy-staging-verify` — Pre-prod verification
6. `approval-gate` — **Manual approval required**
7. `deploy-production` — Production rollout
8. `post-deploy` — GitHub release, notifications

### Nightly Pipeline (`lifeos-nightly.yml`)

**Trigger:** 2 AM UTC daily (cron)

**Jobs:**
1. `full-test-suite` — All markers including slow/ml
2. `ml-model-validation` — Model performance checks
3. `dependency-audit` — pip-audit + safety
4. `coverage-report` — Full coverage analysis
5. `notify-results` — Summary notification

---

## 6. Database Migrations

### Golden Rules

1. **DevOps runs migrations, DB team creates them**
2. **Never create migrations in CI** — Only `flask db upgrade`
3. **Dangerous patterns require review** — `drop_table`, `drop_column`, `execute(`

### CI Migration Workflow

```
PR Submitted
    │
    ▼
┌─────────────────────────────────┐
│ check_migrations.sh             │
│ • Verify single Alembic head    │
│ • Apply to ephemeral SQLite     │
│ • Flag dangerous patterns       │
└─────────────────────────────────┘
    │
    ▼ (if new migrations)
┌─────────────────────────────────┐
│ Request DB Team Review          │
│ • GitHub warning annotation     │
│ • List changed migration files  │
└─────────────────────────────────┘
    │
    ▼ (after approval)
┌─────────────────────────────────┐
│ Staging Deploy                  │
│ • run_migrations.sh             │
│ • flask db upgrade head         │
└─────────────────────────────────┘
    │
    ▼ (after testing)
┌─────────────────────────────────┐
│ Production Deploy               │
│ • Manual approval gate          │
│ • run_migrations.sh             │
│ • Verify + rollback ready       │
└─────────────────────────────────┘
```

### Manual Migration Commands

```bash
# Check current state
cd lifeos && flask db current

# Apply pending migrations
cd lifeos && flask db upgrade head

# Rollback one migration
cd lifeos && flask db downgrade -1

# Show migration history
cd lifeos && flask db history
```

---

## 7. Deployment Procedures

### Staging Deployment (Automatic)

1. Push to `main` or `develop`
2. CI runs full test suite
3. Docker image built and pushed
4. Auto-deploy to staging environment
5. Smoke test verifies health

### Production Deployment (Manual Approval)

1. Create and push semver tag: `git tag v1.2.3 && git push origin v1.2.3`
2. Release pipeline triggers
3. Full test suite runs
4. Image built and scanned
5. Staging verification deployment
6. **Manual approval required** (GitHub environment protection)
7. Production deployment executes
8. Smoke test verifies health
9. GitHub release created

### Rollback Procedure

```bash
# Kubernetes
kubectl rollout undo deployment/lifeos -n production

# Docker Compose
docker-compose pull lifeos:previous-sha
docker-compose up -d

# Database (if migration failed)
cd lifeos && flask db downgrade -1
```

---

## 8. Monitoring & Alerts

### Health Endpoints

| Endpoint | Purpose | Expected Response |
|----------|---------|-------------------|
| `/health` | Liveness probe | `{"status": "ok"}` |
| `/ready` | Readiness probe | `{"status": "ready"}` |

### Alert Conditions

| Condition | Severity | Action |
|-----------|----------|--------|
| Deployment failed | Critical | Page on-call, investigate logs |
| Smoke test failed | Critical | Auto-rollback, notify team |
| Health check failing | High | Investigate, potential restart |
| Nightly tests failed | Medium | Investigate next business day |
| Security vulnerability | High | Assess severity, patch if critical |

### Metrics to Monitor

- Deployment success rate
- Time to deploy (staging, production)
- Test pass rate
- Coverage trend
- Container image size
- Vulnerability count

---

## 9. Troubleshooting

### Common Issues

#### Tests Failing in CI but Passing Locally

```bash
# Ensure you're using the same environment
cp .env.ci lifeos/.env
export PYTHONPATH=$PWD
make test-unit
```

#### Migration Heads Conflict

```bash
# Check for multiple heads
cd lifeos && flask db heads

# If multiple, DB team must merge:
cd lifeos && flask db merge heads -m "merge_heads"
```

#### Docker Build Failing

```bash
# Check Dockerfile syntax
docker build --file deploy/Dockerfile --no-cache .

# Check for missing dependencies
pip check
```

#### Coverage Below Threshold

```bash
# Generate detailed coverage report
make coverage

# View uncovered lines
open htmlcov/index.html
```

### Log Locations

| Environment | Log Location |
|-------------|--------------|
| CI | GitHub Actions → Workflow run → Job logs |
| Staging | `kubectl logs -n staging -l app=lifeos` |
| Production | `kubectl logs -n production -l app=lifeos` |
| Local Docker | `docker-compose logs -f` |

---

## 10. Secrets & Configuration

### Required GitHub Secrets

| Secret | Environment | Purpose |
|--------|-------------|---------|
| `STAGING_DATABASE_URL` | staging | PostgreSQL connection |
| `PROD_DATABASE_URL` | production | PostgreSQL connection |
| `CODECOV_TOKEN` | all | Coverage upload |
| `SLACK_WEBHOOK` | all | Notifications (optional) |

### Environment Configuration

| Environment | Config File | Database | Features |
|-------------|-------------|----------|----------|
| Local | `.env` (gitignored) | SQLite | All enabled |
| CI | `.env.ci` (committed) | SQLite/:memory: | ML disabled |
| Staging | Secrets | PostgreSQL | All enabled |
| Production | Secrets | PostgreSQL | All enabled |

### Setting Up Secrets (GitHub Admin)

1. Go to repo → Settings → Secrets and variables → Actions
2. Add repository secrets:
   - `STAGING_DATABASE_URL`
   - `PROD_DATABASE_URL`
   - `CODECOV_TOKEN`
3. Go to Settings → Environments
4. Create environments: `staging`, `production`, `production-approval`
5. For `production-approval`: Add required reviewers

---

## Quick Reference

### Common Commands

```bash
# Run tests
make test-unit                    # Fast unit tests
make test-all                     # Full suite

# Check quality
make lint                         # Linters
make security                     # Security scan

# Migrations
make check-migrations             # Verify consistency
make run-migrations               # Apply (needs DATABASE_URL)

# Deploy
make build-image                  # Build Docker image
make smoketest TARGET_URL=...     # Health check
make deploy ENV=staging           # Deploy to staging
```

### Workflow Triggers

| Action | Workflow Triggered |
|--------|-------------------|
| Open PR | `lifeos-pr.yml` |
| Push to main | `lifeos-main.yml` |
| Push tag `v1.2.3` | `lifeos-release.yml` |
| 2 AM UTC daily | `lifeos-nightly.yml` |

---

**Questions?** Contact the DevOps team or check `lifeos/docs/CI_CD_ARCHITECTURE.md` for the full specification.
