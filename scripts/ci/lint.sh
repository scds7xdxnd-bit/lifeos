#!/usr/bin/env bash
# Purpose: Run all linters
# Called by: make lint
# Exit: Non-zero if any linter fails

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Running Ruff Linter ==="
if command -v ruff &> /dev/null; then
    ruff check lifeos/ --output-format=github || ruff check lifeos/
else
    echo "⚠️ Ruff not installed, using flake8 fallback"
    flake8 lifeos --count --select=E9,F63,F7,F82 --show-source --statistics
fi

echo "=== Checking Black Formatting ==="
black --check lifeos/ || {
    echo "⚠️ Black check failed. Run 'black lifeos/' to fix formatting."
    exit 1
}

echo "=== Checking Import Order ==="
if command -v ruff &> /dev/null; then
    ruff check lifeos/ --select I --output-format=github || ruff check lifeos/ --select I
else
    isort --check-only lifeos/ || {
        echo "⚠️ Import order check failed. Run 'isort lifeos/' to fix."
        exit 1
    }
fi

echo "✓ All linting checks passed"
