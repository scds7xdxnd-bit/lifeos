#!/usr/bin/env bash
# Purpose: Run unit tests only (fast)
# Called by: make test-unit
# Markers: -m unit (or exclude integration/ml)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export APP_ENV="${APP_ENV:-ci}"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

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
