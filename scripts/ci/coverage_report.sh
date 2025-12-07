#!/usr/bin/env bash
# Purpose: Generate coverage reports
# Called by: make coverage

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

echo "=== Generating Coverage Report ==="

# Combine coverage from multiple test runs if available
if [ -f coverage-unit.xml ] && [ -f coverage-integration.xml ]; then
    echo "Combining coverage from unit and integration tests..."
    coverage combine --append || true
fi

# Generate reports
echo "Generating HTML report..."
coverage html --directory=htmlcov

echo "Generating XML report..."
coverage xml -o coverage.xml

echo "Generating terminal report..."
coverage report --show-missing

# Check coverage threshold
THRESHOLD="${COVERAGE_THRESHOLD:-80}"
echo ""
echo "Checking coverage threshold (${THRESHOLD}%)..."
coverage report --fail-under="$THRESHOLD" || {
    echo "⚠️ Coverage below ${THRESHOLD}%"
    exit 1
}

echo ""
echo "✓ Coverage report generated"
echo "  - HTML: htmlcov/index.html"
echo "  - XML: coverage.xml"
