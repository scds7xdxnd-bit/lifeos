#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:5001}"
PYTHON_BIN="${PYTHON_BIN:-}"

EXPECT_SKILLS_GOALS="${EXPECT_SKILLS_GOALS:-true}"
EXPECT_SKILLS_PATH="${EXPECT_SKILLS_PATH:-true}"
EXPECT_SKILLS_FORECAST="${EXPECT_SKILLS_FORECAST:-false}"
EXPECT_SKILLS_GOALS_STRICT="${EXPECT_SKILLS_GOALS_STRICT:-false}"
SKILLS_JWT="${SKILLS_JWT:-}"
SKILL_ID="${SKILL_ID:-}"

function normalize_bool() {
  local raw
  raw="$(echo "$1" | tr '[:upper:]' '[:lower:]')"
  case "${raw}" in
    true|1|yes) echo "true" ;;
    false|0|no) echo "false" ;;
    *)
      echo "ERROR: Invalid boolean value '${1}'. Use true/false, 1/0, or yes/no." >&2
      exit 1
      ;;
  esac
}

function resolve_python_bin() {
  if [[ -z "${PYTHON_BIN}" ]]; then
    if command -v python3 >/dev/null 2>&1; then
      PYTHON_BIN="python3"
    elif command -v python >/dev/null 2>&1; then
      PYTHON_BIN="python"
    else
      echo "ERROR: Could not find 'python3' or 'python' in PATH. Set PYTHON_BIN." >&2
      exit 1
    fi
  fi

  if [[ "${PYTHON_BIN}" == */* ]]; then
    if [[ ! -x "${PYTHON_BIN}" ]]; then
      echo "ERROR: Python binary not found or not executable: ${PYTHON_BIN}" >&2
      exit 1
    fi
  else
    if ! command -v "${PYTHON_BIN}" >/dev/null 2>&1; then
      echo "ERROR: Python command not found on PATH: ${PYTHON_BIN}" >&2
      exit 1
    fi
  fi
}

function assert_bool() {
  local name="$1"
  local actual="$2"
  local expected="$3"
  if [[ "${actual}" != "${expected}" ]]; then
    echo "ERROR: ${name} expected=${expected} actual=${actual}" >&2
    exit 1
  fi
  echo "OK: ${name}=${actual}"
}

resolve_python_bin

EXPECT_SKILLS_GOALS="$(normalize_bool "${EXPECT_SKILLS_GOALS}")"
EXPECT_SKILLS_PATH="$(normalize_bool "${EXPECT_SKILLS_PATH}")"
EXPECT_SKILLS_FORECAST="$(normalize_bool "${EXPECT_SKILLS_FORECAST}")"
EXPECT_SKILLS_GOALS_STRICT="$(normalize_bool "${EXPECT_SKILLS_GOALS_STRICT}")"

echo "== Phase 12 Skills Forecast Rollout Check =="
echo "BASE_URL=${BASE_URL}"
echo "PYTHON_BIN=${PYTHON_BIN}"

echo "-- Health check"
status_code="$(curl -sS -o /dev/null -w "%{http_code}" "${BASE_URL}/health" || true)"
if [[ "${status_code}" != "200" ]]; then
  echo "ERROR: health check failed at ${BASE_URL}/health (status=${status_code})" >&2
  exit 1
fi
echo "OK: health endpoint returned 200"

echo "-- Effective config check (local process env)"
config_json="$(${PYTHON_BIN} - <<'PY'
import json
from lifeos.config import BaseConfig
print(json.dumps({
    "goals": bool(BaseConfig.ENABLE_PHASE12_SKILLS_GOALS),
    "path": bool(BaseConfig.ENABLE_PHASE12_SKILLS_PATH),
    "forecast": bool(BaseConfig.ENABLE_PHASE12_SKILLS_FORECAST),
    "strict": bool(BaseConfig.ENABLE_PHASE12_SKILLS_GOALS_STRICT),
}))
PY
)"

read -r goals_actual path_actual forecast_actual strict_actual < <(
  ${PYTHON_BIN} - <<PY
import json
cfg = json.loads('''${config_json}''')
print(str(cfg["goals"]).lower(), str(cfg["path"]).lower(), str(cfg["forecast"]).lower(), str(cfg["strict"]).lower())
PY
)

assert_bool "ENABLE_PHASE12_SKILLS_GOALS" "${goals_actual}" "${EXPECT_SKILLS_GOALS}"
assert_bool "ENABLE_PHASE12_SKILLS_PATH" "${path_actual}" "${EXPECT_SKILLS_PATH}"
assert_bool "ENABLE_PHASE12_SKILLS_FORECAST" "${forecast_actual}" "${EXPECT_SKILLS_FORECAST}"
assert_bool "ENABLE_PHASE12_SKILLS_GOALS_STRICT" "${strict_actual}" "${EXPECT_SKILLS_GOALS_STRICT}"

echo "-- Optional runtime endpoint check"
if [[ -n "${SKILLS_JWT}" && -n "${SKILL_ID}" ]]; then
  expected_status="404"
  if [[ "${EXPECT_SKILLS_FORECAST}" == "true" ]]; then
    expected_status="200"
  fi
  forecast_status="$(curl -sS -o /dev/null -w "%{http_code}" -H "Authorization: Bearer ${SKILLS_JWT}" "${BASE_URL}/api/skills/${SKILL_ID}/forecast" || true)"
  if [[ "${forecast_status}" != "${expected_status}" ]]; then
    echo "ERROR: Runtime forecast endpoint mismatch expected=${expected_status} actual=${forecast_status}" >&2
    exit 1
  fi
  echo "OK: Runtime forecast endpoint status=${forecast_status} (skill_id=${SKILL_ID})"
else
  echo "SKIPPED: Set SKILLS_JWT and SKILL_ID to verify running service behavior."
fi

echo "-- Guidance"
if [[ "${forecast_actual}" == "true" ]]; then
  echo "Forecast is ENABLED: verify Skills cards render forecast panel and monitor 5xx/latency."
else
  echo "Forecast is DISABLED: system is in safe fallback mode."
fi

echo "PASS: Phase 12 skills forecast rollout checks completed"
