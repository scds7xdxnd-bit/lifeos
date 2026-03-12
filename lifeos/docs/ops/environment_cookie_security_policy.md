# Environment Cookie Security Policy (Binding)

**Audience:** Backend, Frontend, QA, DevOps
**Owner:** Architecture
**Status:** Binding

## Purpose
Prevent login loops and authentication drift caused by incorrect cookie security flags across environments.

## Policy

### Development Environments
- HTTP access is allowed.
- `SESSION_COOKIE_SECURE = False`.

### Production Environments
- HTTPS is required.
- `SESSION_COOKIE_SECURE = True`.

## Mandatory Cookie Invariants
- `SESSION_COOKIE_HTTPONLY = True` must remain enabled.
- `SESSION_COOKIE_SAMESITE = "Lax"` must remain enabled.

## Enforcement
- Cookie security mode is environment-scoped via config class selection.
- Runtime toggling that contradicts the selected environment policy is forbidden.

## Verification
- Development: browser must send session cookie over HTTP local/dev.
- Production: browser must send session cookie only over HTTPS.
- Any divergence is a release blocker for auth-related changes.

---

## Ops Runtime Confirmation (Session-Cookie API Auth)

### 1) Cookie-session prerequisites in runtime
- Stable signing keys are required and must be identical across web workers:
  - `SECRET_KEY`
  - `JWT_SECRET_KEY`
- Environment policy must match transport:
  - `APP_ENV=development` / `local-dev` -> `SESSION_COOKIE_SECURE=False`
  - `APP_ENV=staging` / `production` -> `SESSION_COOKIE_SECURE=True`

### 2) Reverse-proxy behavior
- Current repository ingress/compose definitions do not include cookie-stripping directives.
- No `proxy_set_header Authorization` injection is configured in ingress manifests.
- Cookie forwarding remains default pass-through from client -> ingress -> web service.

### 3) Deterministic ops check (`/auth/me` cookie-only)
- Login and verify API auth without `Authorization` header:

```bash
EMAIL="ops.cookie.$(date +%s)@example.com"
PASS='Secret123'
COOKIE=/tmp/lifeos_cookie_ops.txt
rm -f "$COOKIE"

curl -sS -c "$COOKIE" -b "$COOKIE" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\",\"full_name\":\"Ops Cookie\",\"timezone\":\"UTC\"}" \
  http://127.0.0.1:8000/auth/register >/dev/null || true

curl -sS -c "$COOKIE" -b "$COOKIE" -H 'Content-Type: application/json' \
  -d "{\"email\":\"$EMAIL\",\"password\":\"$PASS\"}" \
  http://127.0.0.1:8000/auth/login >/dev/null

curl -sS -o /dev/null -w 'ME=%{http_code}\n' -b "$COOKIE" http://127.0.0.1:8000/auth/me
curl -sS -o /dev/null -w 'CAL=%{http_code}\n' -b "$COOKIE" "http://127.0.0.1:8000/api/v1/calendar/day?date=2026-03-04"
```

Expected:
- `ME=200`
- `CAL=200`
- Cookie jar contains `session` cookie.

### 4) Latest local validation (2026-03-04)
- `LOGIN_CODE=200`
- `ME_COOKIE_ONLY=200`
- `CAL_COOKIE_ONLY=200`
- `session` cookie present in cookie jar.

**Operational conclusion:** current environment supports session-cookie auth for browser-used API routes.
