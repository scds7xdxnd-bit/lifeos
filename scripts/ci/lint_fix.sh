#!/usr/bin/env bash
# Purpose: Auto-fix linting issues (ruff + black)
# Called by: make lint-fix

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "=== Running Ruff Auto-fix ==="
ruff check lifeos/ --fix
ruff check lifeos/ --select I --fix

echo "=== Running Black Auto-format ==="
black lifeos/

echo "✓ Lint auto-fix complete"
