# Auth Authority & Route Scope (Binding)

**Audience:** Backend, Frontend, QA, DevOps
**Owner:** Architecture
**Status:** Binding

## 1) Authentication Authority (Web UI)
- Same-origin browser UI requests are **session-cookie primary**.
- Session cookie is the authoritative identity source for web UI API calls.
- JWT Authorization headers are **not** the authority for same-origin browser UI flows.

## 2) Route Scope Policy
- **Must accept session auth (minimum required):**
  - `/auth/me`
  - Browser-consumed API routes under `/api/*` used by web UI pages.
- JWT may remain supported for non-browser clients, but it must not alter or override session-primary behavior for same-origin browser requests.

## 3) Mixed-Mode Policy (Deterministic)
- If both session cookie and `Authorization` header are present on a same-origin browser request, the request is **invalid**.
- Backend must reject with `mixed_auth_forbidden`.
- Silent fallback or implicit mode switching is forbidden.

## 4) CSRF Scope (Session-Primary)
- For session-authenticated requests, CSRF is required on state-changing methods (`POST`, `PUT`, `PATCH`, `DELETE`).
- CSRF validation must be session-bound and evaluated against the active session authority only.
- Any request failing session-bound CSRF validation must return `csrf_failed`.

## 5) Testable Invariants
- Cookie-only `/auth/me` succeeds for authenticated web sessions.
- Same request with mixed auth fails with `mixed_auth_forbidden`.
- State-changing session-auth requests require valid session-bound CSRF token.
