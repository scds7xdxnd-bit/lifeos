# Phase 3b Cross-Team Handoff (API Hardening & Read-Only Insights)

Context
- Architecture v2.1; Phase 3a delivered inference telemetry, event catalog completeness, DB hardening, and admin debug telemetry (non-prod).
- Phase 3b focuses on API hardening for external/mobile consumers, introducing `/api/v1`, and exposing a read-only insights feed; no broker migration or new ML models.

Overall Goals (Phase 3b)
- Add `/api/v1` namespace without breaking existing routes.
- Expose a read-only insights feed (paginated, filtered).
- Standardize auth/token handling for API consumers (Bearer + CSRF) with a refresh flow.
- Keep changes additive; no schema breakage; optional read-model tables only if gated by config.
- Client-friendly API semantics locked in:
  - Finance account search: empty query → 200 with empty `results`.
  - Trial balance: invalid params → 200 with empty `accounts/categories` (and `totals`).
  - Journal list: always returns pagination metadata; invalid filters → 200 with empty items + `page/pages/total`.

What’s Stable / Must Not Break
- Event catalog contracts, including inference fields (`status`, `payload_version`, `model_version`, optional `is_false_positive`/`is_false_negative`, `inferred_structure`).
- Outbox/dispatcher semantics; insights telemetry endpoint (non-prod/admin-only).
- Existing domain APIs and auth flows; additive migrations only.
- Architecture guardrails (event catalog completeness, additive migrations, controller→service→model layering).

Allowed to Change (Phase 3b Scope)
- Add `/api/v1` namespace wrappers.
- Add `GET /api/v1/insights/feed` (read-only, paginated, filtered).
- Normalize auth login/refresh responses/headers for API consumers.
- Optional: add config-gated additive read-model tables/views if needed for performance; otherwise rely on existing service queries.
- Incremental ORM cleanup: replace `Query.get()` with `Session.get()` over time; do not silence warnings globally.

Team-Specific Focus

Backend
- Implement `/api/v1/insights/feed` (service/controller/schemas/tests) using `insight_record`.
- Introduce `/api/v1` namespace alongside legacy routes.
- Ensure auth login/refresh returns tokens (Bearer + CSRF) and headers are documented/accepted.
- Keep events unchanged; no new event types for this phase.
- Enforce test hygiene: per-test DB isolation (transaction/savepoint), unique fixture data (e.g., UUID emails), no swallowed `IntegrityError`, and `xfail` always justified.

Frontend
- Update clients to call `/api/v1/` endpoints where available; ensure auth headers (Bearer + CSRF) are sent after login.
- If consuming insights feed, add pagination/filter UI; handle empty states gracefully.
- Do not introduce domain logic in templates; rely on DTOs.

DevOps
- No infra changes planned; ensure CI runs `./scripts/ci/lint.sh` and tests against merge SHA.
- Keep secrets/branch protection enforced; no new env vars expected.
- Monitor `/api/v1/insights/feed` once live; no broker changes.

QA
- Add integration tests for `/api/v1/insights/feed` (auth required, filters, pagination).
- Regression: auth/login/refresh headers (Bearer + CSRF) and /api/v1 namespace compatibility.
- Guardrails: event catalog completeness, additive migrations.
- Verify client-friendly API semantics: finance search empty query returns 200 + empty results; trial balance invalid params returns 200 with empty payload; journal list always returns pagination metadata even on invalid filters.

ML
- No new models; ensure inference events continue to carry `status/payload_version/model_version` and optional FP/FN flags.
- Validate telemetry remains correct after API changes; no changes to inference emitter needed.

Risks / Mitigations
- API namespace drift: keep legacy routes working; add `/api/v1` without breaking existing clients.
- Performance on insights feed: cap pagination; add optional read-model tables only if needed and gated by config.
- Auth header consistency: document and test Bearer + CSRF; ensure frontend/mobile send both.

Definition of Done (Phase 3b)
- `/api/v1` namespace available and documented; existing routes unaffected.
- `GET /api/v1/insights/feed` returns correct data (filtered, paginated, user-scoped).
- Auth flows (login/refresh) return tokens and accept Bearer + CSRF headers; 401/403 predictable.
- Guardrails/tests pass; migrations additive; telemetry endpoint behavior unchanged (non-prod/admin-only).
- ORM warning debt tracked: `Query.get()` usage reduced or eliminated; remaining instances noted for follow-up.
