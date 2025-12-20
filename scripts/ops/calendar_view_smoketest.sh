#!/usr/bin/env bash
set -euo pipefail

# Simple smoke test for deterministic calendar view/ledger endpoints.
# Requirements: AUTH_TOKEN must be a valid Bearer token; BASE_URL defaults to http://localhost:8000.

BASE_URL="${BASE_URL:-http://localhost:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"
TODAY="${TODAY:-$(date -u +%Y-%m-%d)}"
WEEK_START="${WEEK_START:-${TODAY}}"
MONTH="${MONTH:-$(date -u +%Y-%m)}" # YYYY-MM
LEDGER_LIMIT="${LEDGER_LIMIT:-20}"

if [[ -z "${AUTH_TOKEN}" ]]; then
  echo "ERROR: AUTH_TOKEN is required (Bearer token for an admin/user with calendar access)." >&2
  exit 1
fi

auth_header=("Authorization: Bearer ${AUTH_TOKEN}")

fail=0

check() {
  local label="$1"
  local url="$2"
  local code
  code=$(curl -s -o /tmp/calendar_smoke.$$ -w "%{http_code}" -H "${auth_header[@]}" "${url}") || code="000"
  if [[ "${code}" != "200" ]]; then
    echo "ERROR: ${label} failed (status ${code}) :: ${url}"
    fail=1
  else
    echo "OK: ${label} (status ${code})"
  fi
}

echo "Using BASE_URL=${BASE_URL}"
echo "TODAY=${TODAY}, WEEK_START=${WEEK_START}, MONTH=${MONTH}, LEDGER_LIMIT=${LEDGER_LIMIT}"

check "Day view"    "${BASE_URL}/api/v1/calendar/day?date=${TODAY}"
check "Week view"   "${BASE_URL}/api/v1/calendar/week?start=${WEEK_START}"
check "Month view"  "${BASE_URL}/api/v1/calendar/month?year=${MONTH%-*}&month=${MONTH#*-}"
check "Ledger view" "${BASE_URL}/api/v1/calendar/ledger?anchor=${TODAY}&direction=backward&limit=${LEDGER_LIMIT}"

exit ${fail}
