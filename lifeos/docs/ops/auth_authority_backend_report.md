# Backend Auth Authority Report

## Previous Auth Mechanism

- `/auth/me` and domain API routes relied on `@jwt_required()`.
- Browser session cookie (`session=...`) was not sufficient by itself.
- Resulting observed behavior:
  - `/auth/me` cookie-only -> `401`
  - `/auth/me` with `Authorization: Bearer ...` -> `200`

## New Session-Auth Mechanism

- Login now establishes Flask session auth:
  - `POST /auth/login` calls `login_user(...)`.
  - `POST /api/v1/auth/login` calls `login_user(...)`.
- Auth scope bridge is enforced for browser-used API scope:
  - Scope: `/auth/me` and `/api/*`.
  - If no `Authorization` header is present and user is session-authenticated, backend injects a server-generated access token into request context for existing `@jwt_required()` routes.
  - This preserves current controller/service contracts while making session-cookie auth primary for web UI.

## Mixed-Mode Behavior

- Policy: deterministic rejection.
- If request contains both:
  - session cookie, and
  - `Authorization` header
- On scoped routes (`/auth/me`, `/api/*`), backend returns:
  - HTTP `403`
  - body: `{ "ok": false, "error": "mixed_auth_forbidden" }`

## CSRF Authority Alignment

- CSRF remains session-bound only.
- CSRF validation compares header token against session canonical token.
- Structured CSRF failure logging includes:
  - `session_id`
  - `expected_csrf`
  - `received_csrf`
  - `auth_header_present`
  - `request_id`
  - `build_id`

## Proof (Automated Verification)

From integration tests:

- `login -> /auth/me (cookie-only)`:
  - `POST /auth/login` -> `200`
  - `GET /auth/me` -> `200`
- Calendar read (`cookie-only`):
  - `GET /api/v1/calendar/day?date=2026-03-04` -> `200`
- Session write (`cookie-only + CSRF`):
  - `POST /api/bootstrap` -> `200` (token retrieval)
  - `POST /api/habits` with `X-CSRF-Token` -> `201`
- Mixed mode rejection:
  - `GET /auth/me` with session cookie + Authorization header -> `403` (`mixed_auth_forbidden`)

Test run:
- All targeted tests passed:
  - `lifeos/tests/test_session_cookie_auth_scope.py`
  - `lifeos/tests/test_csrf_determinism.py`
