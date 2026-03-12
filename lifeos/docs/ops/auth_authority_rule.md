# Auth Authority Rule (Binding)

**Audience:** Backend, Frontend, QA, DevOps
**Owner:** Architecture
**Status:** Binding

---

## 1) Authentication Authority (Web UI)

- **Session-primary only:** Same-origin browser UI requests must authenticate via **session cookies**.
- **JWT header forbidden in browser UI:** `Authorization: Bearer <JWT>` must **not** be used for same-origin browser requests.
- JWT remains valid only for non-browser clients (API consumers, services) that do not use session cookies.

---

## 2) CSRF Authority

- CSRF tokens are **session-bound** and validated **only** against the active session.
- The CSRF token presented in `X-CSRF-Token` must match the server-issued session CSRF token.

---

## 3) Mixed-Auth Behavior (Deterministic)

If a request includes both a session cookie and an Authorization header, the server must apply **one** explicit policy, globally:

- **Preferred:** Reject with error code `mixed_auth_forbidden`, or
- **Alternative:** Explicitly ignore the Authorization header and continue **session-only** validation.

No implicit priority or mixed evaluation is allowed.

---

## 4) Enforcement Notes

- Browser UI must send **session cookie + CSRF header only**.
- Frontend must not attach Bearer tokens to same-origin UI requests.
- QA must include a mixed-auth test to assert rejection/ignore policy is enforced.

---

## 5) Invariant

**Session authentication and CSRF validation are a single authority chain.**
Any request that attempts to mix session and token authorities is invalid by definition.

---

## 6) Backend Implementation Status (Current)

- **Session auth precedence enforced:** same-origin `/api` writes with both `session` cookie and `Authorization` header are rejected with `mixed_auth_forbidden`.
- **Mixed-auth policy enforced:** deterministic rejection with structured logging (`mixed_auth_forbidden`).
- **CSRF validator aligned to session authority:** CSRF checks validate against session-bound token only.
- **CSRF failure logging:** includes session id, expected/received CSRF, and authorization header presence.

---

## 7) DevOps Runtime Confirmation (Binding)

### Infrastructure confirmation
- **No proxy/gateway auth header injection configured** in repository runtime definitions:
  - Docker Compose stack: no reverse-proxy middleware injects `Authorization`.
  - Kubernetes ingress (staging/production): no `auth-url`, `auth-snippet`, `proxy_set_header Authorization`, or equivalent injection directives are configured.
- **Cookie sessions are forwarded** through ingress/web server path as standard request headers (no cookie stripping rules present in current ingress manifests).

### Browser write request contract (canonical)
**Required**
- `Cookie: session=...`
- `X-CSRF-Token: <server-issued session token>`

**Forbidden (same-origin browser UI)**
- `Authorization: Bearer <token>`

### Dev environment guardrails
- Browser extensions or dev tools must not inject `Authorization` on same-origin `/api` requests.
- If extension/header tooling is enabled, it must exclude LifeOS local/staging/prod origins.
- Dev verification must use Network tab to confirm write requests include cookie + CSRF header only.

### Operational conclusion
Runtime infrastructure (compose + ingress + web server path) is configured not to reintroduce `Authorization` headers into same-origin browser requests. Any future `Authorization` presence on browser writes is treated as client-side injection or non-browser API usage, not proxy behavior.
