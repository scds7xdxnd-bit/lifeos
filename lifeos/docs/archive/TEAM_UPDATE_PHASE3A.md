# Team Update — Post Calendar-First (v2.1)

Context:
- Calendar-First Phase 2 is complete; CI/CD pipelines (`lifeos-main.yml`, `lifeos-pr.yml`, `lifeos-release.yml`, `lifeos-nightly.yml`) are operational with 85% coverage.
- Architecture doc is updated to v2.1 (2025-12-10).
- Next strategic focus: Phase 3a (Cross-Domain Intelligence) unless Product reprioritizes.

## DevOps
- Monitor the first `lifeos-main.yml` run on GitHub Actions; ensure green.
- Configure GitHub Secrets: `CODECOV_TOKEN`, container registry creds (GHCR_TOKEN or equivalent), staging/prod env secrets.
- Enforce GitHub environment protection rules (staging, production) and branch protections (PR-first, required checks).
- Archive `docs/DEVOPS_HANDOFF_CI_FIX.md` after confirming main is green.

## QA
- Verify coverage uploads (Codecov) and CI parity; keep nightly (`lifeos-nightly.yml`) monitored.
- Confirm all 521 tests pass in CI; track the 10 xfailed cases.
- Add remaining inferred-record integration tests (domain-specific) on top of calendar interpreter tests.

## Backend / Frontend / ML
- Use PR-first workflow; no direct pushes to main.
- For any new events or schema changes, update `lifeos/docs/lifeos_architecture.md` before implementation.
- Leverage `/health` and `/api/v1/ping` for smoke checks post-deploy.
- Prepare for Phase 3a: ensure event payloads include `model_version`/`payload_version` where ML is involved; avoid cross-domain imports (event-driven only).

## All Teams
- Keep architecture doc current when boundaries, events, or migrations change.
- Run `flask db upgrade` before feature testing; keep DB at head (`20251219_calendar_oauth_tokens`).
- Continue to label tests with `pytestmark` (unit/integration/ml) and maintain ≥85% coverage.
