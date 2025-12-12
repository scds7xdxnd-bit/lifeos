# Backend Phase 3b Handoff Outline

Stable / Must Not Break
- Event catalog contracts, including inference fields (`status`, `payload_version`, `model_version`, optional `is_false_positive`/`is_false_negative`, `inferred_structure`).
- Outbox/dispatcher semantics (pending→sending→sent/failed/dead; skip-locked; backoff; dedupe).
- Admin insight telemetry endpoint (non-prod/admin-only): `GET /admin/debug/insight-telemetry`, read-only, in-memory.
- Existing domain APIs and auth flows; additive migrations only.

Allowed to Change (Phase 3b scope)
- Add `/api/v1` namespace (alongside legacy routes) for API consumers.
- Add read-only insights feed endpoint `GET /api/v1/insights/feed` (paginated, filtered).
- Standardize auth login/refresh responses/headers for API consumers (Bearer + CSRF).
- Optional, gated by config: additive read-model tables/views if needed for performance; otherwise reuse existing queries.

Backend Focus (order)
1. Implement `/api/v1/insights/feed` (service + controller + schemas + tests) using `insight_record`.
2. Introduce `/api/v1` namespace without breaking existing routes.
3. Tighten auth responses/headers (login/refresh) to ensure tokens are issued and headers documented/accepted.
4. If needed, add minimal read-model tables/views (additive, config-gated) and tests; otherwise keep service-level queries.

Tests to Add/Run
- Integration: `/api/v1/insights/feed` (auth, filters, pagination).
- Auth regression: login/refresh/header handling (Bearer + CSRF).
- Guardrails: event catalog completeness; additive migrations; architecture constraints.
- If read-model tables: migration test + service correctness.
