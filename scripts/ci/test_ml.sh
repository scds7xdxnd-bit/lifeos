#!/usr/bin/env bash
# Purpose: Run ML tests (slow, nightly only)
# Called by: make test-ml

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export APP_ENV="${APP_ENV:-ci}"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

echo "=== Running ML Tests ==="

pytest lifeos/tests/ \
    -m "ml or slow" \
    --tb=short \
    --junitxml=test-results-ml.xml \
    -v \
    --timeout=300

echo "✓ ML tests passed"
