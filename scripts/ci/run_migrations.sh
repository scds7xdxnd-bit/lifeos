#!/usr/bin/env bash
# Purpose: Apply pending migrations to target database
# Called by: make run-migrations
# IMPORTANT: This script only RUNS migrations, never CREATES them
# DB team is responsible for creating/reviewing Alembic revisions

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

# Hard-reset PYTHONPATH so stdlib modules (e.g., platform) cannot be shadowed by
# our lifeos/platform package during CLI startup. CWD provides lifeos on sys.path.
export PYTHONPATH=""

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
python -m flask --app lifeos.wsgi db current

# Apply migrations
echo ""
echo "Applying pending migrations..."
python -m flask --app lifeos.wsgi db upgrade head

# Verify final state
echo ""
echo "Final migration state:"
python -m flask --app lifeos.wsgi db current

echo ""
echo "✓ Migrations applied successfully"
