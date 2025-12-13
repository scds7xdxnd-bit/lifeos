# Incident Report: CI Lint & Test Failures (Merge-SHA, Formatter Drift, Import Sorting)

**Title:** CI Lint & Test Failures Due to Merge-SHA Drift, Formatter Config Mismatch, and Import Sorting Enforcement
**System:** LifeOS Backend
**Date:** 2025-12-12
**Severity:** Medium (Blocked CI, no production impact)
**Status:** Resolved

---

## 1) Summary
CI pipelines reported widespread lint and test failures while local environments appeared clean. Root causes were:
1) CI running against the PR merge commit (not PR head).
2) Black formatter configuration drift between local and CI.
3) Ruff import-order enforcement (I001) not handled by Black.
4) Test teardown inconsistencies in one CI workflow due to DB lifecycle differences.

All issues were resolved via config alignment, reproducible local CI execution, and explicit import sorting.

---

## 2) Impact
- CI blocked: Black “would reformat” across ~135 files; Ruff I001 after Black fix; one workflow with ~500 test errors (teardown failures).
- Developer confidence degraded due to mismatch between local and CI.
- No production impact.

---

## 3) Timeline (key points)
1. Initial observation: local `black --check` passed; CI lint failed.
2. Discrepancy: Main integration job green; CI Build & Test showed massive failures.
3. SHA verification: CI checked out merge SHA `6923d857...`; local HEAD `369b087...`.
4. Local reproduction: checked out `pr-4-merge`, ran `./scripts/ci/lint.sh`, reproduced failures.
5. Root causes found: Black config mismatch; Ruff import-order enforcement; Postgres-oriented teardown leaking into SQLite tests.
6. Fixes: central Black config (pyproject.toml), pinned Black in CI, Ruff `--select I --fix`, normalized test DB lifecycle.
7. Verification: `./scripts/ci/lint.sh` passed locally; CI lint/tests green.

---

## 4) Root Causes
- **RC-1 (Merge SHA):** CI ran on merge commit; local checks were on PR head only.
- **RC-2 (Formatter drift):** CI called `black --check ... --line-length=120` without a central config; local invocations varied.
- **RC-3 (Import sorting):** Ruff enforced I001; Black does not sort imports.
- **RC-4 (DB teardown):** Postgres-specific teardown behavior affected SQLite-based tests in one workflow.

---

## 5) Resolution
**Formatting & Linting**
- Added repo-wide formatter config (pyproject.toml): `line-length = 120`, `target-version = py310`.
- Pinned Black in CI; surfaced `black --version` in logs.
- Fixed imports: `ruff check lifeos/ --select I --fix`.

**CI Reproducibility**
- Verified merge SHA from Actions logs; reproduced locally by checking out `pr-*-merge`.

**Testing**
- Normalized test DB config/teardown to avoid Postgres-only behavior in SQLite tests; teardown stabilized.

---

## 6) Preventive Actions
1) Validate CI vs local on the merge SHA; note the SHA from `actions/checkout` logs.
2) Single source of truth for formatting: keep Black settings in pyproject.toml; avoid ad-hoc CI overrides.
3) Pin and surface tool versions in CI (Black, Ruff, etc.).
4) Require `./scripts/ci/lint.sh` locally before push; Black formats, Ruff enforces imports.
5) Keep tests environment-agnostic; ensure teardown logic doesn’t assume Postgres when running on SQLite.
6) SQLAlchemy upgrade readiness: track and replace `Query.get()` with `Session.get()` incrementally; do not silence warnings globally until coverage is clean.
7) Test hygiene guardrails to freeze:
   - DB isolation enforced centrally (per-test transaction/savepoint; no ad-hoc cleanup).
   - `xfail` entries carry reasons; no silent skips.
   - Tests never disable constraints or swallow `IntegrityError`.

---

## 7) Final Status
- All lint checks passing.
- All tests passing.
- CI pipelines green.
- Incident closed.

---

## Context Notes (from investigation)
- CI vs local mismatch: CI merge SHA `6923d857...` vs local `369b087...`.
- Formatting: Black mismatch due to missing central config; resolved by pyproject.toml + pinning.
- Import sorting: Ruff I001 required explicit fix.
- Test teardown: Postgres FK drop errors (`psycopg2.errors.DependentObjectsStillExist`) fixed by aligning DB lifecycle and stripping Postgres-specific args for SQLite tests.
