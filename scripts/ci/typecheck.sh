#!/usr/bin/env bash
# Purpose: Run mypy type checking
# Called by: make typecheck

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Running Mypy Type Checker ==="

# Check if mypy is available
if ! command -v mypy &> /dev/null; then
    echo "⚠️ Mypy not installed, skipping type checks"
    exit 0
fi

# Strict checking on core, relaxed on domains (transitional)
echo "Checking lifeos/core/ (strict)..."
mypy lifeos/core/ --strict --ignore-missing-imports || {
    echo "⚠️ Type errors in core/"
    exit 1
}

echo "Checking lifeos/domains/..."
mypy lifeos/domains/ --ignore-missing-imports || {
    echo "⚠️ Type errors in domains/"
    exit 1
}

echo "Checking lifeos/platform/..."
mypy lifeos/platform/ --ignore-missing-imports || {
    echo "⚠️ Type errors in platform/"
    exit 1
}

echo "✓ Type checking passed"
