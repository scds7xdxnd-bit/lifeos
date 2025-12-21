#!/usr/bin/env bash
# Purpose: Verify Alembic migration consistency (CI does NOT create migrations)
# Called by: make check-migrations
# Responsibility: Detect inconsistencies; DB team owns actual revisions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

echo "=== Checking Alembic Migration Consistency ==="

# Check that there's exactly one head (no branches)
echo "Checking for single migration head..."
HEADS=$(cd lifeos && python -m flask --app wsgi:app db heads 2>/dev/null | grep -c "Rev:" || echo "0")
HEADS_TRIMMED=$(echo "$HEADS" | tr -d '[:space:]')
if [ "${HEADS_TRIMMED:-0}" -gt 1 ]; then
    echo "❌ ERROR: Multiple migration heads detected. Merge required."
    cd lifeos && python -m flask --app wsgi:app db heads
    exit 1
fi
echo "✓ Single migration head confirmed"

# Verify migrations can be applied to empty DB
echo ""
echo "Verifying migrations apply cleanly to empty database..."
export DATABASE_URL="sqlite:///:memory:"
cd lifeos && python -m flask --app wsgi:app db upgrade head
echo "✓ Migrations apply cleanly"

# Check for dangerous patterns in migrations (flag for review)
echo ""
echo "Checking for dangerous migration patterns..."
DANGEROUS_FOUND=0
DANGEROUS_PATTERNS=("drop_table" "drop_column" "execute(")

for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if grep -r "$pattern" lifeos/migrations/versions/*.py 2>/dev/null; then
        echo "⚠️ WARNING: Potentially dangerous pattern detected: $pattern"
        DANGEROUS_FOUND=1
    fi
done

if [ $DANGEROUS_FOUND -eq 1 ]; then
    echo ""
    echo "⚠️ Dangerous migration patterns detected. Requires DB team review before merge."
fi

echo ""
echo "✓ Migration check passed (single head, applies cleanly)"
