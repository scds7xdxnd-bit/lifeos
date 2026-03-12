## Auth/CSRF Secret Stability & Build Identity

### Purpose
Prevent CSRF/session failures caused by secret drift or image drift between deploys.

### Secret Stability (Binding)
- **Canonical sources:** `SECRET_KEY` and `JWT_SECRET_KEY` must be explicitly set via `.env`, compose, or deployment secrets.
- **No startup randomness:** secrets must **not** be generated at container start.
- **Shared across instances:** all web containers must receive the same secret values.

**Enforcement in compose**
- `docker-compose.yml` requires `SECRET_KEY` and `JWT_SECRET_KEY` via required env vars.
- `.env` must define both keys for local/dev.

**Verification**
- `docker compose exec -T web printenv | rg "SECRET_KEY|JWT_SECRET_KEY"` (values must be present and consistent across web instances).

### Build Identity (Binding)
- **Required env:** `BUILD_ID` (or `GIT_SHA`/`COMMIT_SHA`) must be injected at deploy time.
- **Runtime exposure:** build identity is returned by `/health` and as `X-LifeOS-Build` on responses.

**Verification**
- `curl -fsS http://<host>:8000/health | rg build_id`
- Inspect response headers for `X-LifeOS-Build`.

### Dev Reset Protocol (when secrets change)
1. **Invalidate client state:** clear browser cookies for the app domain.
2. **Restart containers:** `docker compose up -d --force-recreate web`.
3. **Re-authenticate:** obtain fresh JWT + CSRF token.
4. **Confirm health/build:** `/health` returns the expected `build_id`.

### Notes
- CSRF failures without code changes usually indicate **secret drift** or **image drift**.
- Treat missing/empty secret env vars as a hard failure.

---

## Cookie Security Policy by Environment

### Authority
- Cookie security mode is selected by `APP_ENV` and mapped to Flask config classes in `lifeos/config.py`.
- `SESSION_COOKIE_SECURE` is not runtime-toggled by env vars; policy is environment-bound.

### Policy matrix
- `local-dev` / `development`
  - `SESSION_COOKIE_SECURE=False`
  - `JWT_COOKIE_SECURE=False`
  - HTTP local access allowed.
- `staging`
  - `SESSION_COOKIE_SECURE=True`
  - `JWT_COOKIE_SECURE=True`
  - HTTPS required for cookie transport.
- `production`
  - `SESSION_COOKIE_SECURE=True`
  - `JWT_COOKIE_SECURE=True`
  - HTTPS required for cookie transport.

### Environment determination
- App factory reads `APP_ENV` (`create_app`).
- Mapping:
  - `local-dev` -> `DevelopmentConfig`
  - `development` -> `DevelopmentConfig`
  - `staging` -> `StagingConfig`
  - `production` -> `ProductionConfig`
  - `testing` / `ci` -> `TestingConfig`

### Environment file usage
- Local dev: `.env` with `APP_ENV=local-dev` (or `development`).
- Staging: staging deployment env/config with `APP_ENV=staging`.
- Production: production deployment env/config with `APP_ENV=production`.

---

## CSRF Boot Determinism Rule (Binding)

### Canonical CSRF source (runtime)
- The **only** valid CSRF authority for API writes is the server-issued, session-bound CSRF token.

### Forbidden CSRF fallbacks
- localStorage/sessionStorage tokens
- derived hashes or client-generated tokens
- JWT claims used as CSRF authority
- stale/cached meta tags not refreshed from the server session

### Boot contract (required; choose exactly one)
- **A) Server-rendered pages must include the canonical CSRF meta tag**, or
- **B) A single bootstrap contract `GET /api/bootstrap` returns `csrf_token` and is required before any write.**

### Invariant
- The `X-CSRF-Token` header must always equal the current session CSRF token; mismatch is a hard 403.
