#!/usr/bin/env bash
# Purpose: Run full test suite
# Called by: make test-all

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export APP_ENV="${APP_ENV:-ci}"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"
export DATABASE_URL="${DATABASE_URL:-sqlite:///:memory:}"

echo "=== Running Full Test Suite ==="
echo "Database: ${DATABASE_URL}"

pytest lifeos/tests/ \
    --tb=short \
    --cov=lifeos \
    --cov-report=xml:coverage-full.xml \
    --cov-report=html:htmlcov \
    --cov-report=term-missing \
    --junitxml=test-results-full.xml \
    -v

echo "✓ All tests passed"
