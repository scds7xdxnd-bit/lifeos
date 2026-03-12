#!/usr/bin/env bash
set -euo pipefail

# Smoke test for Calendar Event Creation UX markup on /calendar.
# Validates presence of "When" block, duration presets, advanced toggle, and 10-color palette.

BASE_URL="${BASE_URL:-http://localhost:8000}"
CALENDAR_URL="${CALENDAR_URL:-${BASE_URL}/calendar}"

HTML="$(curl -fsS "${CALENDAR_URL}")"

fail=0

require_fragment() {
  local label="$1"
  local fragment="$2"
  if ! grep -Fq "${fragment}" <<<"${HTML}"; then
    echo "ERROR: Missing ${label} (${fragment})"
    fail=1
  else
    echo "OK: ${label}"
  fi
}

require_count() {
  local label="$1"
  local fragment="$2"
  local expected="$3"
  local count
  count="$(grep -Fo "${fragment}" <<<"${HTML}" | wc -l | tr -d '[:space:]')"
  if [ "${count}" -ne "${expected}" ]; then
    echo "ERROR: ${label} expected ${expected}, found ${count}"
    fail=1
  else
    echo "OK: ${label} (${count})"
  fi
}

echo "Calendar UX smoke test: ${CALENDAR_URL}"

require_fragment "When block" 'id="cal-when-controls"'
require_fragment "Start time input" 'id="cal-event-start-time"'
require_fragment "End time toggle" 'id="cal-event-end-toggle"'
require_fragment "End time input" 'id="cal-event-end-time"'
require_fragment "Duration block" 'id="cal-event-duration"'
require_count "Duration presets" 'class="cal-duration-btn"' 4
require_fragment "Advanced toggle" 'id="cal-event-advanced-toggle"'
require_fragment "Advanced section" 'id="cal-event-advanced"'
require_fragment "Color palette" 'id="cal-event-color-palette"'
require_count "Color swatches" 'class="cal-color-swatch"' 10
require_fragment "Time options datalist" 'id="cal-time-options"'

exit "${fail}"
