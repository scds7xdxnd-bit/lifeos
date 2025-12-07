# LifeOS CI/CD Makefile
# All CI jobs call these targets for consistency
# Owner: DevOps Team

VENV?=.venv
PYTHON?=$(VENV)/bin/python
PIP?=$(VENV)/bin/pip
APP_ENV ?= development
LIFEOS_PATH ?= lifeos

.PHONY: help venv install lint typecheck security test test-unit test-integration test-ml test-all \
        check-migrations run-migrations smoketest build-image coverage deploy run seed demo ci clean

#------------------------------------------------------------------------------
# Help
#------------------------------------------------------------------------------
help:
	@echo "LifeOS CI/CD Targets"
	@echo "===================="
	@echo ""
	@echo "Setup:"
	@echo "  venv              Create Python virtual environment"
	@echo "  install           Install dependencies"
	@echo ""
	@echo "Quality Gates:"
	@echo "  lint              Run linters (ruff/flake8, black --check)"
	@echo "  typecheck         Run mypy type checking"
	@echo "  security          Run security scans (bandit, safety)"
	@echo ""
	@echo "Testing:"
	@echo "  test              Run unit + integration tests"
	@echo "  test-unit         Run unit tests only (fast, ~5 min)"
	@echo "  test-integration  Run integration tests (requires DB)"
	@echo "  test-ml           Run ML tests (slow, nightly only)"
	@echo "  test-all          Run full test suite"
	@echo "  coverage          Generate coverage reports"
	@echo ""
	@echo "Database (CI only RUNS, never CREATES migrations):"
	@echo "  check-migrations  Verify Alembic migration consistency"
	@echo "  run-migrations    Apply pending migrations (requires DATABASE_URL)"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  build-image       Build Docker image"
	@echo "  smoketest         Run post-deploy smoke tests"
	@echo "  deploy            Deploy to target environment (ENV=staging|prod)"
	@echo ""
	@echo "Development:"
	@echo "  run               Start development server"
	@echo "  seed              Seed database with demo data"
	@echo "  demo              Alias for seed"
	@echo "  clean             Clean build artifacts"

#------------------------------------------------------------------------------
# Setup
#------------------------------------------------------------------------------
venv:
	python -m venv $(VENV)

install: venv
	$(PIP) install --upgrade pip
	$(PIP) install -r lifeos/requirements.txt

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

coverage:
	@./scripts/ci/coverage_report.sh

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
ifndef ENV
	$(error ENV is undefined. Use: make deploy ENV=staging|prod)
endif
	@echo "Deploying to $(ENV)..."
	@./deploy/scripts/deploy.sh $(ENV)

#------------------------------------------------------------------------------
# Development
#------------------------------------------------------------------------------
run:
	$(PYTHON) -m lifeos.wsgi

seed:
	$(PYTHON) -m lifeos.scripts.seed_all_demo

demo: seed

ci: install lint test

#------------------------------------------------------------------------------
# Docker Helpers
#------------------------------------------------------------------------------
docker-up:
	@docker-compose up -d

docker-down:
	@docker-compose down

docker-logs:
	@docker-compose logs -f

#------------------------------------------------------------------------------
# Cleanup
#------------------------------------------------------------------------------
clean:
	@echo "Cleaning build artifacts..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov .coverage 2>/dev/null || true
	@rm -f coverage*.xml test-results*.xml bandit-report.json safety-report.json 2>/dev/null || true
	@echo "✓ Clean complete"
