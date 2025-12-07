#!/usr/bin/env bash
# Purpose: Run security scans
# Called by: make security

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

EXIT_CODE=0

echo "=== Running Bandit Security Scan ==="
if command -v bandit &> /dev/null; then
    # Generate JSON report for CI artifacts
    bandit -r lifeos/ -ll -ii --format json --output bandit-report.json 2>/dev/null || true
    # Display results
    bandit -r lifeos/ -ll -ii || EXIT_CODE=1
else
    echo "⚠️ Bandit not installed, skipping"
fi

echo ""
echo "=== Checking Dependencies for Vulnerabilities ==="
if command -v safety &> /dev/null; then
    # Generate JSON report for CI artifacts
    safety check --file lifeos/requirements.txt --output json > safety-report.json 2>/dev/null || true
    # Display results
    safety check --file lifeos/requirements.txt || EXIT_CODE=1
else
    echo "⚠️ Safety not installed, skipping dependency check"
fi

if [ $EXIT_CODE -eq 0 ]; then
    echo ""
    echo "✓ Security scans completed successfully"
else
    echo ""
    echo "⚠️ Security issues detected (see above)"
fi

exit $EXIT_CODE
