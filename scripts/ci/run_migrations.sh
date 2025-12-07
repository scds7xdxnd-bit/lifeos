#!/usr/bin/env bash
# Purpose: Apply pending migrations to target database
# Called by: make run-migrations
# IMPORTANT: This script only RUNS migrations, never CREATES them
# DB team is responsible for creating/reviewing Alembic revisions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

echo "=== Applying Database Migrations ==="

# Safety check: DATABASE_URL must be set
if [ -z "${DATABASE_URL:-}" ]; then
    echo "❌ ERROR: DATABASE_URL not set"
    echo "Set DATABASE_URL environment variable before running migrations."
    exit 1
fi

# Mask password in output
MASKED_URL=$(echo "$DATABASE_URL" | sed 's/:[^:]*@/:***@/')
echo "Target database: ${MASKED_URL}"

# Show current state
echo ""
echo "Current migration state:"
cd lifeos && python -m flask --app wsgi:app db current

# Apply migrations
echo ""
echo "Applying pending migrations..."
cd lifeos && python -m flask --app wsgi:app db upgrade head

# Verify final state
echo ""
echo "Final migration state:"
cd lifeos && python -m flask --app wsgi:app db current

echo ""
echo "✓ Migrations applied successfully"
