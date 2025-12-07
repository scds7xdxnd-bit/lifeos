# LifeOS CI/CD Architecture Specification

_Last updated: 2025-12-07_  
_Owner: Architect_  
_Implementer: DevOps Team_

---

## Executive Summary

This document defines the CI/CD architecture for the LifeOS monorepo-style project. It establishes pipeline stages, repo structure, quality gates, and clear ownership boundaries. The design is incremental, safe, and respects the existing LifeOS architecture constitution.

**Key Principles:**
- CI/CD **runs** migrations but never **creates** them (DB team owns Alembic)
- Fast feedback on PRs (< 10 min target)
- Production deploys require manual approval
- All CI jobs call Makefile targets for consistency

---

## Table of Contents

1. [Pipeline Types](#1-pipeline-types)
2. [Environment Flow](#2-environment-flow)
3. [Repository Structure](#3-repository-structure)
4. [File Specifications](#4-file-specifications)
5. [Database & Migrations Handling](#5-database--migrations-handling)
6. [Testing Strategy](#6-testing-strategy)
7. [Build & Deploy Strategy](#7-build--deploy-strategy)
8. [Security & Secrets](#8-security--secrets)
9. [RACI Matrix](#9-raci-matrix)
10. [Implementation Handoff](#10-implementation-handoff)

---

## 1. Pipeline Types

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           PIPELINE HIERARCHY                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   PR/Branch  │───▶│  Main/Develop │───▶│   Release    │                   │
│  │   Pipeline   │    │   Pipeline    │    │   Pipeline   │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
│        │                    │                    │                           │
│        ▼                    ▼                    ▼                           │
│   Fast feedback        Full suite          Build + Deploy                   │
│   (~5 min target)      (~15 min)           + Production                     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Pipeline A: PR / Feature Branch (`lifeos-pr.yml`)

**Trigger:** Pull request to `main`, `develop`, or `release/*`

**Purpose:** Fast feedback loop for developers; blocks merge if quality gates fail

| Stage | Jobs | Required for Merge | Timeout |
|-------|------|-------------------|---------|
| `lint` | ruff, black --check | ✅ Yes | 2 min |
| `typecheck` | mypy (strict on core) | ✅ Yes | 3 min |
| `security` | bandit, safety | ✅ Yes | 2 min |
| `unit_tests` | pytest -m unit | ✅ Yes | 5 min |
| `migration_check` | alembic heads consistency | ✅ Yes | 1 min |
| `integration_tests` | pytest -m integration (ephemeral DB) | ⚠️ Optional | 10 min |

**Quality Gates:**
- All required stages must pass
- Code coverage ≥ 80% on changed files
- No new security vulnerabilities (bandit high/critical)
- Migration heads consistent with current

---

### Pipeline B: Main / Develop (`lifeos-main.yml`)

**Trigger:** Push to `main` or `develop` branch

**Purpose:** Full validation; builds artifacts; deploys to staging

| Stage | Jobs | Required | Timeout |
|-------|------|----------|---------|
| `lint` | Full lint suite | ✅ Yes | 2 min |
| `typecheck` | Full mypy | ✅ Yes | 3 min |
| `security` | bandit + safety + trivy (container) | ✅ Yes | 5 min |
| `unit_tests` | pytest -m unit (matrix: py3.10, py3.11) | ✅ Yes | 5 min |
| `integration_tests` | pytest -m integration | ✅ Yes | 15 min |
| `build` | Docker image build | ✅ Yes | 10 min |
| `push` | Push to container registry | ✅ Yes | 2 min |
| `deploy_staging` | Deploy to staging environment | ✅ Yes | 10 min |
| `smoke_test` | Health check + basic API test | ✅ Yes | 3 min |

**Quality Gates:**
- All stages must pass
- Coverage report published
- Container image scanned for vulnerabilities
- Staging deployment healthy

---

### Pipeline C: Release / Tag (`lifeos-release.yml`)

**Trigger:** Push of tag `v*.*.*` (semver)

**Purpose:** Production deployment with approvals

| Stage | Jobs | Required | Timeout |
|-------|------|----------|---------|
| `validate_tag` | Verify semver format, changelog present | ✅ Yes | 1 min |
| `full_test_suite` | All tests including ML tests | ✅ Yes | 30 min |
| `build_prod` | Docker image with prod optimizations | ✅ Yes | 10 min |
| `security_scan` | Full container + dependency scan | ✅ Yes | 5 min |
| `push_prod` | Push with semver + SHA tags | ✅ Yes | 2 min |
| `deploy_staging` | Deploy to staging for final verification | ✅ Yes | 10 min |
| `approval_gate` | **Manual approval required** | ✅ Yes | — |
| `deploy_prod` | Production deployment | ✅ Yes | 15 min |
| `post_deploy` | Smoke test + rollback readiness | ✅ Yes | 5 min |

**Quality Gates:**
- Manual approval required before production
- Staging smoke test must pass
- No critical/high vulnerabilities
- Rollback plan documented in release notes

---

### Pipeline D: Nightly (`lifeos-nightly.yml`)

**Trigger:** Scheduled (cron: `0 2 * * *` — 2 AM UTC)

**Purpose:** Slow tests, ML model validation, dependency updates

| Stage | Jobs | Required | Timeout |
|-------|------|----------|---------|
| `full_test_suite` | All tests including slow ML tests | ✅ Yes | 60 min |
| `dependency_audit` | Check for outdated/vulnerable deps | ⚠️ Warn | 5 min |
| `ml_model_validation` | Validate ML model performance | ⚠️ Warn | 30 min |
| `coverage_report` | Full coverage analysis | ✅ Yes | 10 min |

---

## 2. Environment Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENVIRONMENT PROMOTION                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   Developer        PR Pipeline         Main Pipeline        Release Pipeline │
│       │                │                    │                     │          │
│       ▼                ▼                    ▼                     ▼          │
│   ┌───────┐       ┌─────────┐         ┌─────────┐          ┌──────────┐     │
│   │ Local │──────▶│Ephemeral│────────▶│ Staging │─────────▶│Production│     │
│   │  Dev  │       │  Test   │         │   Env   │          │   Env    │     │
│   └───────┘       └─────────┘         └─────────┘          └──────────┘     │
│       │                │                    │                     │          │
│  .env.dev         .env.ci              .env.staging          .env.prod      │
│  SQLite           SQLite/PG            PostgreSQL            PostgreSQL     │
│  No worker        Mock broker          Full stack            Full stack     │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Environment | Config File | Database | Broker | Auto-Deploy |
|-------------|-------------|----------|--------|-------------|
| Local Dev | `.env` (gitignored) | SQLite | Disabled | — |
| CI/Test | `.env.ci` (committed) | SQLite/:memory: | Mock | Yes |
| Staging | `.env.staging` (secrets) | PostgreSQL | Full | Yes (main push) |
| Production | `.env.prod` (secrets) | PostgreSQL | Full | No (manual) |

---

## 3. Repository Structure

### Complete File Tree (CI/CD additions)

```
finance_app_clean/
├── .github/
│   └── workflows/
│       ├── lifeos-pr.yml              # PR/branch pipeline
│       ├── lifeos-main.yml            # Main/develop pipeline  
│       ├── lifeos-release.yml         # Release/tag pipeline
│       ├── lifeos-nightly.yml         # Nightly scheduled pipeline
│       └── _reusable-test.yml         # Reusable test workflow (DRY)
│
├── scripts/
│   └── ci/
│       ├── lint.sh                    # Lint runner (ruff + black)
│       ├── typecheck.sh               # Mypy runner
│       ├── security.sh                # Bandit + safety scan
│       ├── test_unit.sh               # Unit tests only
│       ├── test_integration.sh        # Integration tests with DB
│       ├── test_ml.sh                 # ML-specific tests
│       ├── test_all.sh                # Full test suite
│       ├── check_migrations.sh        # Migration consistency check
│       ├── run_migrations.sh          # Apply migrations (wrapper)
│       ├── smoketest.sh               # Post-deploy health check
│       ├── build_image.sh             # Docker build wrapper
│       └── coverage_report.sh         # Coverage generation
│
├── Makefile                           # Developer + CI entry points
│
├── pyproject.toml                     # Tool configs (ruff, mypy, pytest)
│
├── .env.example                       # Template for all environments
├── .env.ci                            # CI-specific overrides (committed)
│
├── lifeos/
│   ├── Dockerfile                     # LifeOS container (exists)
│   └── ... (existing structure)
│
├── deploy/
│   ├── Dockerfile                     # Production Dockerfile (exists)
│   ├── docker-compose.yml             # Local dev orchestration (exists)
│   ├── docker-compose.ci.yml          # CI-specific compose overrides
│   └── k8s/                           # Kubernetes manifests (future)
│       ├── staging/
│       │   ├── deployment.yaml
│       │   ├── service.yaml
│       │   └── configmap.yaml
│       └── production/
│           ├── deployment.yaml
│           ├── service.yaml
│           └── configmap.yaml
│
└── docs/
    ├── lifeos_architecture.md         # Master architecture (Architect owns)
    ├── CI_CD_ARCHITECTURE.md          # This document
    └── CI_CD_RUNBOOK.md               # Operational runbook (DevOps creates)
```

---

## 4. File Specifications

### 4.1 Makefile

```makefile
# LifeOS CI/CD Makefile
# All CI jobs call these targets for consistency

.PHONY: help lint typecheck security test test-unit test-integration test-ml \
        check-migrations run-migrations smoketest build-image deploy clean

# Default Python and environment
PYTHON ?= python3
APP_ENV ?= development
LIFEOS_PATH ?= lifeos

#------------------------------------------------------------------------------
# Help
#------------------------------------------------------------------------------
help:
	@echo "LifeOS CI/CD Targets"
	@echo "===================="
	@echo "  lint              Run linters (ruff, black --check)"
	@echo "  typecheck         Run mypy type checking"
	@echo "  security          Run security scans (bandit, safety)"
	@echo "  test              Run all tests"
	@echo "  test-unit         Run unit tests only (fast)"
	@echo "  test-integration  Run integration tests (requires DB)"
	@echo "  test-ml           Run ML tests (slow)"
	@echo "  check-migrations  Verify Alembic migration consistency"
	@echo "  run-migrations    Apply pending migrations"
	@echo "  smoketest         Run post-deploy smoke tests"
	@echo "  build-image       Build Docker image"
	@echo "  deploy            Deploy to target environment (ENV=staging|prod)"
	@echo "  clean             Clean build artifacts"

#------------------------------------------------------------------------------
# Quality Gates
#------------------------------------------------------------------------------
lint:
	@./scripts/ci/lint.sh

typecheck:
	@./scripts/ci/typecheck.sh

security:
	@./scripts/ci/security.sh

#------------------------------------------------------------------------------
# Testing
#------------------------------------------------------------------------------
test: test-unit test-integration

test-unit:
	@./scripts/ci/test_unit.sh

test-integration:
	@./scripts/ci/test_integration.sh

test-ml:
	@./scripts/ci/test_ml.sh

test-all:
	@./scripts/ci/test_all.sh

#------------------------------------------------------------------------------
# Database / Migrations (CI only runs, never generates)
#------------------------------------------------------------------------------
check-migrations:
	@./scripts/ci/check_migrations.sh

run-migrations:
	@./scripts/ci/run_migrations.sh

#------------------------------------------------------------------------------
# Build & Deploy
#------------------------------------------------------------------------------
build-image:
	@./scripts/ci/build_image.sh

smoketest:
	@./scripts/ci/smoketest.sh

deploy:
	@echo "Deploying to $(ENV)..."
	@./scripts/ci/deploy.sh $(ENV)

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage
```

---

### 4.2 CI Scripts

#### `scripts/ci/lint.sh`

```bash
#!/usr/bin/env bash
# Purpose: Run all linters
# Called by: make lint
# Exit: Non-zero if any linter fails

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Running Ruff Linter ==="
ruff check lifeos/ --output-format=github

echo "=== Checking Black Formatting ==="
black --check lifeos/

echo "=== Checking Import Order ==="
ruff check lifeos/ --select I --output-format=github

echo "✓ All linting checks passed"
```

---

#### `scripts/ci/typecheck.sh`

```bash
#!/usr/bin/env bash
# Purpose: Run mypy type checking
# Called by: make typecheck

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Running Mypy Type Checker ==="

# Strict checking on core, relaxed on domains (transitional)
mypy lifeos/core/ --strict --ignore-missing-imports
mypy lifeos/domains/ --ignore-missing-imports
mypy lifeos/platform/ --ignore-missing-imports

echo "✓ Type checking passed"
```

---

#### `scripts/ci/security.sh`

```bash
#!/usr/bin/env bash
# Purpose: Run security scans
# Called by: make security

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Running Bandit Security Scan ==="
bandit -r lifeos/ -ll -ii --format json --output bandit-report.json || true
bandit -r lifeos/ -ll -ii

echo "=== Checking Dependencies for Vulnerabilities ==="
safety check --file lifeos/requirements.txt --output json > safety-report.json || true
safety check --file lifeos/requirements.txt

echo "✓ Security scans completed"
```

---

#### `scripts/ci/test_unit.sh`

```bash
#!/usr/bin/env bash
# Purpose: Run unit tests only (fast)
# Called by: make test-unit
# Markers: -m unit (or exclude integration/ml)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export APP_ENV="${APP_ENV:-ci}"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "=== Running Unit Tests ==="

pytest lifeos/tests/ \
    -m "not integration and not ml and not slow" \
    --tb=short \
    --cov=lifeos \
    --cov-report=xml:coverage-unit.xml \
    --cov-report=term-missing \
    --junitxml=test-results-unit.xml \
    -v

echo "✓ Unit tests passed"
```

---

#### `scripts/ci/test_integration.sh`

```bash
#!/usr/bin/env bash
# Purpose: Run integration tests (requires DB)
# Called by: make test-integration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export APP_ENV="${APP_ENV:-ci}"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

# Use ephemeral test database
export DATABASE_URL="${DATABASE_URL:-sqlite:///:memory:}"

echo "=== Running Integration Tests ==="

pytest lifeos/tests/ \
    -m "integration" \
    --tb=short \
    --cov=lifeos \
    --cov-report=xml:coverage-integration.xml \
    --cov-report=term-missing \
    --junitxml=test-results-integration.xml \
    -v

echo "✓ Integration tests passed"
```

---

#### `scripts/ci/test_ml.sh`

```bash
#!/usr/bin/env bash
# Purpose: Run ML tests (slow, nightly only)
# Called by: make test-ml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export APP_ENV="${APP_ENV:-ci}"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "=== Running ML Tests ==="

pytest lifeos/tests/ \
    -m "ml or slow" \
    --tb=short \
    --junitxml=test-results-ml.xml \
    -v \
    --timeout=300

echo "✓ ML tests passed"
```

---

#### `scripts/ci/test_all.sh`

```bash
#!/usr/bin/env bash
# Purpose: Run full test suite
# Called by: make test-all

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export APP_ENV="${APP_ENV:-ci}"
export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"
export DATABASE_URL="${DATABASE_URL:-sqlite:///:memory:}"

echo "=== Running Full Test Suite ==="

pytest lifeos/tests/ \
    --tb=short \
    --cov=lifeos \
    --cov-report=xml:coverage-full.xml \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    --junitxml=test-results-full.xml \
    -v

echo "✓ All tests passed"
```

---

#### `scripts/ci/check_migrations.sh`

```bash
#!/usr/bin/env bash
# Purpose: Verify Alembic migration consistency (CI does NOT create migrations)
# Called by: make check-migrations
# Responsibility: Detect inconsistencies; DB team owns actual revisions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "=== Checking Alembic Migration Consistency ==="

# Check that there's exactly one head (no branches)
HEADS=$(cd lifeos && python -m flask --app wsgi:app db heads 2>/dev/null | grep -c "Rev:" || echo "0")
if [ "$HEADS" -gt 1 ]; then
    echo "❌ ERROR: Multiple migration heads detected. Merge required."
    cd lifeos && python -m flask --app wsgi:app db heads
    exit 1
fi

# Verify migrations can be applied to empty DB
echo "Verifying migrations apply cleanly..."
export DATABASE_URL="sqlite:///:memory:"
cd lifeos && python -m flask --app wsgi:app db upgrade head

# Check for dangerous patterns in migrations (flag for review)
echo "Checking for dangerous migration patterns..."
DANGEROUS_PATTERNS=("drop_table" "drop_column" "execute(")
for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if grep -r "$pattern" lifeos/migrations/versions/*.py 2>/dev/null; then
        echo "⚠️ WARNING: Potentially dangerous migration pattern detected: $pattern"
        echo "Requires DB team review before merge."
    fi
done

echo "✓ Migration check passed (single head, applies cleanly)"
```

---

#### `scripts/ci/run_migrations.sh`

```bash
#!/usr/bin/env bash
# Purpose: Apply pending migrations to target database
# Called by: make run-migrations
# IMPORTANT: This script only RUNS migrations, never CREATES them
# DB team is responsible for creating/reviewing Alembic revisions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export PYTHONPATH="$PROJECT_ROOT:$PYTHONPATH"

echo "=== Applying Database Migrations ==="

# Safety check: DATABASE_URL must be set
if [ -z "${DATABASE_URL:-}" ]; then
    echo "❌ ERROR: DATABASE_URL not set"
    exit 1
fi

# Show current state
echo "Current migration state:"
cd lifeos && python -m flask --app wsgi:app db current

# Apply migrations
echo "Applying pending migrations..."
cd lifeos && python -m flask --app wsgi:app db upgrade head

# Verify final state
echo "Final migration state:"
cd lifeos && python -m flask --app wsgi:app db current

echo "✓ Migrations applied successfully"
```

---

#### `scripts/ci/smoketest.sh`

```bash
#!/usr/bin/env bash
# Purpose: Post-deploy smoke test
# Called by: make smoketest

set -euo pipefail

TARGET_URL="${TARGET_URL:-http://localhost:5000}"
MAX_RETRIES=30
RETRY_DELAY=2

echo "=== Running Smoke Tests against $TARGET_URL ==="

# Wait for service to be ready
echo "Waiting for service to be ready..."
for i in $(seq 1 $MAX_RETRIES); do
    if curl -sf "${TARGET_URL}/health" > /dev/null 2>&1; then
        echo "Service is ready!"
        break
    fi
    if [ $i -eq $MAX_RETRIES ]; then
        echo "❌ ERROR: Service did not become ready in time"
        exit 1
    fi
    echo "Attempt $i/$MAX_RETRIES - waiting ${RETRY_DELAY}s..."
    sleep $RETRY_DELAY
done

# Health endpoint
echo "Testing /health endpoint..."
HEALTH=$(curl -sf "${TARGET_URL}/health")
if echo "$HEALTH" | grep -q "ok\|healthy"; then
    echo "✓ Health check passed"
else
    echo "❌ Health check failed: $HEALTH"
    exit 1
fi

# Basic API endpoint (if auth not required)
echo "Testing /api/v1/ping (if available)..."
curl -sf "${TARGET_URL}/api/v1/ping" || echo "(endpoint may require auth, skipping)"

echo "✓ Smoke tests passed"
```

---

#### `scripts/ci/build_image.sh`

```bash
#!/usr/bin/env bash
# Purpose: Build Docker image for LifeOS
# Called by: make build-image

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Defaults
IMAGE_NAME="${IMAGE_NAME:-lifeos}"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse --short HEAD)}"
DOCKERFILE="${DOCKERFILE:-deploy/Dockerfile}"
BUILD_CONTEXT="${BUILD_CONTEXT:-.}"

echo "=== Building Docker Image ==="
echo "Image: ${IMAGE_NAME}:${IMAGE_TAG}"
echo "Dockerfile: ${DOCKERFILE}"

docker build \
    --file "$DOCKERFILE" \
    --tag "${IMAGE_NAME}:${IMAGE_TAG}" \
    --tag "${IMAGE_NAME}:latest" \
    --build-arg BUILD_DATE="$(date -u +'%Y-%m-%dT%H:%M:%SZ')" \
    --build-arg GIT_SHA="$(git rev-parse HEAD)" \
    --build-arg GIT_BRANCH="$(git rev-parse --abbrev-ref HEAD)" \
    "$BUILD_CONTEXT"

echo "✓ Image built: ${IMAGE_NAME}:${IMAGE_TAG}"
```

---

### 4.3 Environment Configuration

#### `.env.ci`

```bash
# CI Environment Configuration
# This file is committed to repo; no secrets here

APP_ENV=ci
DEBUG=false
TESTING=true

# Database: ephemeral for tests
DATABASE_URL=sqlite:///:memory:

# Disable external services
ENABLE_ML=false
ENABLE_INSIGHTS=true
ENABLE_ASSISTANT=false

# Rate limiting disabled for tests
RATELIMIT_ENABLED=false

# Worker disabled in CI tests
WORKER_ENABLED=false

# Logging
LOG_LEVEL=WARNING
```

---

### 4.4 pyproject.toml (CI-relevant sections)

```toml
[tool.pytest.ini_options]
testpaths = ["lifeos/tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
markers = [
    "unit: Fast unit tests (no external dependencies)",
    "integration: Integration tests (require database)",
    "ml: ML-related tests (slow, model loading)",
    "slow: Tests that take > 10 seconds",
]
addopts = "--strict-markers"
filterwarnings = [
    "ignore::DeprecationWarning",
]

[tool.coverage.run]
source = ["lifeos"]
omit = [
    "lifeos/tests/*",
    "lifeos/migrations/*",
    "*/__pycache__/*",
]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "raise NotImplementedError",
]
fail_under = 80

[tool.ruff]
target-version = "py310"
line-length = 120
src = ["lifeos"]

[tool.ruff.lint]
select = ["E", "F", "I", "W", "B", "C4", "UP"]
ignore = ["E501"]  # Line length handled separately

[tool.mypy]
python_version = "3.10"
warn_return_any = true
warn_unused_ignores = true
ignore_missing_imports = true

[tool.bandit]
exclude_dirs = ["tests", "migrations"]
skips = ["B101"]  # assert usage in tests
```

---

## 5. Database & Migrations Handling

### 5.1 Responsibility Matrix

| Activity | CI/CD Pipeline | DB Team | Backend Team |
|----------|:-------------:|:-------:|:------------:|
| **Create** Alembic revisions | ❌ Never | ✅ Owner | ❌ No |
| **Review** migration safety | ❌ No | ✅ Owner | ⚠️ Consult |
| **Check** migration consistency | ✅ Yes | — | — |
| **Run** migrations (apply) | ✅ Yes | — | — |
| **Rollback** on failure | ✅ Automated | ✅ Manual approval | — |

### 5.2 CI Migration Checks

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     MIGRATION SAFETY CHECKS IN CI                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  PR Pipeline:                                                                │
│  ┌─────────────────────────────────────────────────────────────┐            │
│  │ 1. Verify single Alembic head (no branch conflicts)         │            │
│  │ 2. Apply migrations to ephemeral SQLite → must succeed      │            │
│  │ 3. If PR contains new migrations → flag for DB team review  │            │
│  └─────────────────────────────────────────────────────────────┘            │
│                                                                              │
│  Main Pipeline (Staging Deploy):                                             │
│  ┌─────────────────────────────────────────────────────────────┐            │
│  │ 1. Run `flask db upgrade head` against staging Postgres     │            │
│  │ 2. If fails → abort deployment, notify DB team              │            │
│  │ 3. If succeeds → proceed to app deployment                  │            │
│  └─────────────────────────────────────────────────────────────┘            │
│                                                                              │
│  Release Pipeline (Production):                                              │
│  ┌─────────────────────────────────────────────────────────────┐            │
│  │ 1. Pre-flight: verify staging migrations match production   │            │
│  │ 2. Manual approval gate if new migrations present           │            │
│  │ 3. Apply migrations in separate job BEFORE app rollout      │            │
│  │ 4. Verify migration success before proceeding               │            │
│  │ 5. Rollback: revert app + alert DB team (manual recovery)   │            │
│  └─────────────────────────────────────────────────────────────┘            │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 5.3 Dangerous Migration Detection

CI flags PRs for manual review if migrations contain:

- `drop_table`
- `drop_column`
- `alter_column` (type changes)
- `execute(` (raw SQL)

These require explicit DB team approval before merge.

---

## 6. Testing Strategy

### 6.1 Test Categorization

| Category | Marker | Duration | When Run | Dependencies |
|----------|--------|----------|----------|--------------|
| Unit | `@pytest.mark.unit` | < 100ms each | Every PR | None |
| Integration | `@pytest.mark.integration` | < 1s each | Every PR (optional), Every main push | SQLite/Postgres |
| ML | `@pytest.mark.ml` | 1-30s each | Nightly only | Model files |
| Slow | `@pytest.mark.slow` | > 10s | Nightly only | Various |

### 6.2 Matrix Builds

```yaml
strategy:
  matrix:
    python-version: ['3.10', '3.11']
    os: [ubuntu-latest]
  fail-fast: false
```

### 6.3 Caching Strategy

| Cache Type | Key | TTL |
|------------|-----|-----|
| pip dependencies | `pip-${{ runner.os }}-${{ hashFiles('**/requirements*.txt') }}` | 7 days |
| mypy cache | `mypy-${{ runner.os }}-${{ hashFiles('**/pyproject.toml') }}` | 7 days |
| ML model artifacts | `ml-models-${{ hashFiles('lifeos/ml_assets/**') }}` | 30 days |

### 6.4 ML Test Handling

- **PR Pipeline**: Skip ML tests by default (too slow); run only if PR touches `lifeos/domains/*/ml/` or `lifeos/ml_assets/`
- **Nightly Pipeline**: Run full ML test suite; validate model performance metrics; alert if accuracy drops below threshold

---

## 7. Build & Deploy Strategy

### 7.1 Docker Image Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  Stage 1: builder                                                │
│  FROM python:3.10-slim AS builder                               │
│  - Install build dependencies                                    │
│  - pip wheel --no-cache-dir                                      │
│  - Output: /wheels/*.whl                                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  Stage 2: runtime                                                │
│  FROM python:3.10-slim AS runtime                               │
│  - Install runtime dependencies only                            │
│  - COPY --from=builder /wheels                                  │
│  - pip install --no-index /wheels/*.whl                         │
│  - COPY lifeos/ /app/lifeos/                                    │
│  - USER nonroot                                                 │
│  - EXPOSE 5000                                                  │
│  - CMD ["gunicorn", "-c", "deploy/gunicorn.conf.py"]            │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Image Tagging Strategy

| Trigger | Tags Applied | Registry |
|---------|--------------|----------|
| PR build | `lifeos:pr-<number>-<sha>` | (not pushed) |
| Main push | `lifeos:<sha>`, `lifeos:main` | ghcr.io/org/lifeos |
| Develop push | `lifeos:<sha>`, `lifeos:develop` | ghcr.io/org/lifeos |
| Release tag | `lifeos:<semver>`, `lifeos:<sha>`, `lifeos:latest` | ghcr.io/org/lifeos |

### 7.3 Deployment Sequence

```
1. PRE-DEPLOY (separate job)
   - Pull latest image
   - Run: flask db upgrade head (against target DB)
   - If fails → ABORT, notify, do NOT proceed

2. DEPLOY (rolling update)
   - kubectl apply -f k8s/{env}/deployment.yaml
   - Wait for rollout: kubectl rollout status
   - If fails → kubectl rollout undo

3. POST-DEPLOY
   - Smoke test against new deployment
   - If fails → trigger rollback, alert
   - If succeeds → update deployment dashboard
```

---

## 8. Security & Secrets

### 8.1 Secrets Management

| Secret | Where Stored | Access |
|--------|--------------|--------|
| `DATABASE_URL` | GitHub Secrets (per environment) | `deploy-*` jobs only |
| `JWT_SECRET_KEY` | GitHub Secrets | `deploy-*` jobs only |
| `REGISTRY_PASSWORD` | GitHub Secrets | `push` jobs only |
| `SLACK_WEBHOOK` | GitHub Secrets | Notification jobs |

**Rules:**
- Never echo secrets in logs (`set +x` before secret usage)
- Use GitHub environment protection for staging/production
- Rotate secrets quarterly (ops runbook)

### 8.2 Access Control

| Environment | Required Reviewers | Auto-deploy |
|-------------|-------------------|-------------|
| `ci` (ephemeral) | None | Yes |
| `staging` | None | Yes (on main push) |
| `production` | 1 from `@org/release-approvers` | No (manual gate) |

### 8.3 CI Observability

**Artifacts Published:**
- `coverage-*.xml` → Codecov/SonarQube
- `test-results-*.xml` → GitHub Actions summary
- `bandit-report.json` → Security dashboard
- `safety-report.json` → Dependency tracking

**Metrics to Track:**
- Build duration by stage
- Test pass/fail rate
- Coverage trend over time
- Deployment frequency + lead time
- Rollback frequency

---

## 9. RACI Matrix

| Activity | Architect | DevOps | Backend | DB | QA | ML |
|----------|:---------:|:------:|:-------:|:--:|:--:|:--:|
| **Define pipeline stages & gates** | **R/A** | C | I | I | C | I |
| **Write workflow YAML files** | C | **R/A** | C | I | I | I |
| **Write CI helper scripts** | C | **R/A** | C | I | I | I |
| **Maintain Dockerfile** | C | **R/A** | C | I | I | I |
| **Create Alembic migrations** | I | I | I | **R/A** | I | I |
| **Review migration safety** | C | I | C | **R/A** | I | I |
| **Add pytest markers to tests** | I | I | **R/A** | I | C | C |
| **Define test coverage thresholds** | C | I | C | I | **R/A** | I |
| **Add CLI hooks for CI** | I | C | **R/A** | I | I | I |
| **Configure ML test strategy** | C | C | I | I | I | **R/A** |
| **Approve production deploys** | I | C | I | C | **R/A** | I |
| **Monitor CI/CD health** | I | **R/A** | I | I | I | I |

**Legend:** R=Responsible, A=Accountable, C=Consulted, I=Informed

---

## 10. Implementation Handoff

### 10.1 For DevOps Team

**Phase 1: Foundation (Week 1)**

| Task | Priority | Deliverable |
|------|----------|-------------|
| Create `scripts/ci/lint.sh` | P0 | Working script |
| Create `scripts/ci/typecheck.sh` | P0 | Working script |
| Create `scripts/ci/security.sh` | P0 | Working script |
| Create `scripts/ci/test_unit.sh` | P0 | Working script |
| Create `scripts/ci/test_integration.sh` | P0 | Working script |
| Create `scripts/ci/check_migrations.sh` | P0 | Working script |
| Create `Makefile` | P0 | All targets listed |
| Create `.env.ci` | P0 | Committed config |
| Create `.github/workflows/lifeos-pr.yml` | P0 | PR checks working |
| Create `.github/workflows/_reusable-test.yml` | P1 | DRY test workflow |

**Phase 2: Build & Deploy (Week 2)**

| Task | Priority | Deliverable |
|------|----------|-------------|
| Create `scripts/ci/run_migrations.sh` | P0 | Working script |
| Create `scripts/ci/smoketest.sh` | P0 | Working script |
| Create `scripts/ci/build_image.sh` | P0 | Working script |
| Create `.github/workflows/lifeos-main.yml` | P0 | Staging auto-deploy |
| Create `.github/workflows/lifeos-release.yml` | P0 | Prod with approval |
| Create `.github/workflows/lifeos-nightly.yml` | P1 | Scheduled tests |
| Set up GitHub environments | P0 | staging, production |
| Configure GitHub Secrets | P0 | All secrets listed |
| Create `deploy/docker-compose.ci.yml` | P1 | CI compose override |

**Phase 3: Kubernetes (Week 3, if applicable)**

| Task | Priority | Deliverable |
|------|----------|-------------|
| Create `deploy/k8s/staging/*.yaml` | P1 | Staging manifests |
| Create `deploy/k8s/production/*.yaml` | P1 | Prod manifests |
| Create `docs/CI_CD_RUNBOOK.md` | P1 | Ops documentation |
| Test rollback procedure | P0 | Documented + tested |

### 10.2 Verification Checklist

After implementation, DevOps should verify:

- [ ] `make lint` passes locally and in CI
- [ ] `make test-unit` runs correct test subset
- [ ] `make check-migrations` detects multi-head scenario
- [ ] PR pipeline completes in < 10 minutes
- [ ] Main pipeline deploys to staging automatically
- [ ] Release pipeline requires manual approval for production
- [ ] Rollback procedure tested and documented
- [ ] All secrets configured in GitHub
- [ ] Coverage reports published to Codecov/SonarQube

### 10.3 Questions for DevOps

Before starting implementation:

1. **Container Registry**: Which registry should we use? (ghcr.io, ECR, GCR, DockerHub)
2. **Kubernetes**: Is K8s the target, or Docker Compose for staging?
3. **Notifications**: Slack channel for CI failures?
4. **Coverage Tool**: Codecov, SonarQube, or both?
5. **Python Versions**: Confirm matrix: 3.10 + 3.11?

---

## Appendix A: GitHub Actions Workflow Templates

### `lifeos-pr.yml` (Template)

```yaml
name: LifeOS PR Pipeline

on:
  pull_request:
    branches: [main, develop, 'release/*']
    paths:
      - 'lifeos/**'
      - 'scripts/**'
      - 'pyproject.toml'
      - 'requirements*.txt'

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

env:
  PYTHON_VERSION: '3.10'
  APP_ENV: ci

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      - run: pip install ruff black
      - run: make lint

  typecheck:
    runs-on: ubuntu-latest
    timeout-minutes: 3
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      - run: pip install mypy
      - run: make typecheck

  security:
    runs-on: ubuntu-latest
    timeout-minutes: 2
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      - run: pip install bandit safety
      - run: make security

  migration-check:
    runs-on: ubuntu-latest
    timeout-minutes: 1
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      - run: pip install -r lifeos/requirements.txt
      - run: make check-migrations

  unit-tests:
    runs-on: ubuntu-latest
    timeout-minutes: 5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ env.PYTHON_VERSION }}
          cache: 'pip'
      - run: pip install -r lifeos/requirements.txt
      - run: make test-unit
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-unit
          path: coverage-unit.xml
```

---

_Document version: 1.0_  
_Approved by: LifeOS Architect_  
_Implementation owner: DevOps Team_
