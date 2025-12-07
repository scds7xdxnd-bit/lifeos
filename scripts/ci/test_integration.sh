#!/usr/bin/env bash
# Purpose: Run integration tests (requires DB)
# Called by: make test-integration

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export APP_ENV="${APP_ENV:-ci}"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

# Use ephemeral test database if not specified
export DATABASE_URL="${DATABASE_URL:-sqlite:///:memory:}"

echo "=== Running Integration Tests ==="
echo "Database: ${DATABASE_URL}"

pytest lifeos/tests/ \
    -m "integration" \
    --tb=short \
    --cov=lifeos \
    --cov-report=xml:coverage-integration.xml \
    --cov-report=term-missing \
    --junitxml=test-results-integration.xml \
    -v

echo "✓ Integration tests passed"
