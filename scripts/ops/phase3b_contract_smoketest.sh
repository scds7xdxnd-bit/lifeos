#!/usr/bin/env bash
set -euo pipefail

# Phase 3b contract hardening smoke tests.
# Runs unit tests that lock API contracts and read-only guard behavior.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"

cd "${PROJECT_ROOT}"
export PYTHONPATH="${PROJECT_ROOT}:${PYTHONPATH:-}"

PYTHON_BIN="${PYTHON_BIN:-python}"
PYTEST_BIN="${PYTEST_BIN:-${PYTHON_BIN} -m pytest}"

tests=(
  "lifeos/tests/test_phase_3b_api_contracts.py"
  "lifeos/tests/test_phase_3b_read_only_guard.py"
  "lifeos/tests/test_phase_3b_frontend_contract_errors.py"
)

echo "Running Phase 3b contract hardening tests..."
echo "Tests: ${tests[*]}"

${PYTEST_BIN} -q "${tests[@]}"
