# Backend Phase 3b Design Spec (API Hardening & Read-Only Insights)

Context
- Architecture v2.1; Phase 3a delivered inference telemetry, event catalog completeness, DB hardening, and admin debug telemetry endpoint (non-prod).
- Objective for Phase 3b: harden external/mobile API surface, introduce a versioned namespace, and expose a read-only insights/feed endpoint using existing data (no new broker; minimal or optional read-model tables).

Goals
- Provide `/api/v1` namespace for API consumers without breaking existing routes.
- Deliver an insights feed endpoint that aggregates `insight_record` with filters (date range, domain, severity), paginated and user-scoped.
  - Domain filter accepts comma-separated or list inputs; status filter is supported via `data.status`/`data.inference_status` (no new column added).
- Standardize auth flows for API consumers: login returns tokens (Bearer + CSRF), refresh works, and headers are documented/consistent.
- Optional: add lightweight read-model tables/views (additive) gated by config; default to service-level queries.
- API semantics decisions (client-friendly defaults):
  - Finance account search: empty query returns `200` with an empty `results` list (no 400 for blank input).
  - Trial balance: invalid params return `200` with empty accounts/categories (no 400).
  - Journal list: always returns pagination metadata; invalid filters yield `200` with empty items + `page/pages/total`.

Non-Goals
- No broker migration; stay on outbox + in-memory bus.
- No new ML models; reuse existing inference hooks.
- No destructive schema changes; additive-only if any read-model tables are added.

Data Model Impacts (optional)
- None required. If performance demands, add additive read-model tables/views (document per domain, gate by config). Migrations must be additive and reversible.

API/Controllers
- Namespace: introduce `/api/v1` alongside existing endpoints (do not break current routes).
- New endpoint: `GET /api/v1/insights/feed`
  - Query params: `page`, `per_page`, `start_date`, `end_date`, `domain` (optional list), `severity` (optional), `status` (optional).
  - Status filter is applied against stored insight metadata (`data.status`/`data.inference_status`) to avoid schema churn; domain filter accepts comma-separated or list input.
  - Response: `{items: [...], page, pages, total}`; each item includes `id, user_id, insight_type, message/data, created_at, source_event_type?, source_event_id?, severity`.
- Auth endpoints: ensure `/auth/login` (or `/api/v1/auth/login`) returns `access_token, refresh_token, csrf_token, user`; add `/api/v1/auth/refresh` if missing; document headers: `Authorization: Bearer <token>`, `X-CSRF-Token` when using cookies.
- Controllers remain thin; use schemas/DTOs for validation; services supply data.

Services
- Insights feed service (in insights/services.py or new module):
  - `list_insights(user_id, filters, page, per_page) -> (items, total)`; filter by date range, domain, severity/status; include source event metadata if present. Status filtering is metadata-based (in-memory) for now.
- Auth service: confirm/standardize login/refresh issuance and header expectations; no behavioral change aside from consistency.
- Optional read-model helpers (per domain) if needed for performance; otherwise reuse existing queries.
- Finance account search (`GET /api/finance/accounts/search`): `include_ml=true` merges embedding-based ranker output with typed search results while preserving the `200` + empty-list semantics for blank/invalid queries and existing ML event logging/version fields.

Events
- No new event types required. Ensure existing inference events carry `status`, `payload_version`, `model_version`, and optional `is_false_positive`/`is_false_negative`; guardrails already enforce catalog completeness.

Acceptance Criteria
- `/api/v1` namespace is available; existing routes continue to work.
- `GET /api/v1/insights/feed` returns paginated, user-scoped insights with filter support; response includes source event metadata when available.
- Auth flows: login returns tokens; refresh works; Bearer + CSRF headers accepted; 401/403 handled predictably.
- Any optional read-model tables are additive, gated by config, and shipped with migrations/tests.
- Telemetry/admin debug endpoint behavior unchanged (non-prod/admin only).

Testing
- Integration tests for `/api/v1/insights/feed` (auth required, filters, pagination).
- Auth regression tests for login/refresh/header handling (Bearer + CSRF).
- Architecture guardrails remain passing (event catalog completeness, additive migrations).
- If read-model tables added: migration test + service test for correctness.
