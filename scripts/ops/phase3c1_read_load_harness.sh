#!/usr/bin/env bash
set -euo pipefail

# Phase 3c-1 synthetic read-path load harness.
# Exercises calendar, finance, and insights read endpoints with configurable concurrency.

BASE_URL="${BASE_URL:-http://localhost:8000}"
AUTH_TOKEN="${AUTH_TOKEN:-}"
ITERATIONS="${ITERATIONS:-10}"
CONCURRENCY="${CONCURRENCY:-4}"
SLEEP_SECONDS="${SLEEP_SECONDS:-0.2}"
PYTHON_BIN="${PYTHON_BIN:-}"

if [[ -z "${AUTH_TOKEN}" ]]; then
  echo "ERROR: AUTH_TOKEN is required (Bearer token)." >&2
  exit 1
fi

if [[ -z "${PYTHON_BIN}" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
  else
    echo "ERROR: python not found. Set PYTHON_BIN to your venv python." >&2
    exit 1
  fi
elif ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
  echo "ERROR: PYTHON_BIN '${PYTHON_BIN}' not found in PATH." >&2
  exit 1
fi

read -r DAY WEEK_START YEAR MONTH < <("$PYTHON_BIN" - <<'PY'
from datetime import date, timedelta
today = date.today()
week_start = today - timedelta(days=today.weekday())  # Monday of this week
print(today.isoformat(), week_start.isoformat(), today.year, f"{today.month:02d}")
PY
)

request_url() {
  local path="$1"
  curl -fsS -H "Authorization: Bearer ${AUTH_TOKEN}" \
    -H "Accept: application/json" \
    "${BASE_URL}${path}" >/dev/null
}

export -f request_url
export BASE_URL AUTH_TOKEN

for ((i = 1; i <= ITERATIONS; i++)); do
  page="${i}"
  offset="$(( (i - 1) * 50 ))"
  direction="backward"
  if (( i % 2 == 0 )); then
    direction="forward"
  fi

  urls=(
    "/api/v1/calendar/day?date=${DAY}"
    "/api/v1/calendar/week?start=${WEEK_START}"
    "/api/v1/calendar/month?year=${YEAR}&month=${MONTH}"
    "/api/v1/calendar/ledger?anchor=${DAY}&direction=${direction}&limit=50"
    "/api/finance/dashboard"
    "/api/finance/trial_balance"
    "/api/finance/trial_balance/period"
    "/api/finance/trial_balance/monthly"
    "/api/finance/forecast?days=30"
    "/api/v1/insights/feed?page=${page}&per_page=50"
    "/api/v1/insights/review?limit=50&offset=${offset}"
  )

  printf '%s\n' "${urls[@]}" | xargs -P "${CONCURRENCY}" -n1 -I{} bash -c 'request_url "$@"' _ {}

  if awk "BEGIN {exit !(${SLEEP_SECONDS} > 0)}"; then
    sleep "${SLEEP_SECONDS}"
  fi
done

echo "OK: Phase 3c-1 read load complete"
