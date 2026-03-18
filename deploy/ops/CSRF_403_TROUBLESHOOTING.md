# LifeOS CSRF 403 Errors - Operations Troubleshooting Guide

**Last Updated:** 2026-03-18
**Issue:** HTTP 403 Forbidden errors on `/auth/register` and `/api/habits`
**Root Cause:** CSRF token handling in cross-origin requests
**Severity:** CRITICAL - Blocks user registration and API access

---

## Quick Summary

The LifeOS production deployment is rejecting requests with **HTTP 403** errors:
- **Endpoint:** `POST /auth/register` → 403 (register endpoint)
- **Endpoint:** `GET/POST /api/habits` → 403 (habits API)

**Root Cause:** CSRF token validation is failing due to:
1. Frontend not priming CSRF token before registration
2. Cross-origin requests missing cookie credentials
3. Production HTTPS configuration not matching CSRF cookie settings

---

## Architecture Context

### LifeOS Ops Structure

```
lifeos/                          # Core application
  core/
    auth/                        # Authentication layer
      controllers.py             # @auth_bp.post("/register") - NO @csrf_protected
    utils/
      decorators.py              # @csrf_protected decorator
  domains/
    habits/
      controllers/habit_api.py   # ALL endpoints have @csrf_protected
    ...other domains with similar protection

deploy/
  fly.io/                        # Fly.io production config
    fly.toml                     # force_https = true
  gunicorn.conf.py              # Production WSGI server
  Dockerfile                     # Container definition

frontend/
  lib/
    api/
      client.ts                  # apiFetch() - adds X-CSRF-Token header
      habits.ts                  # Uses apiFetch()
    auth/
      provider.tsx               # Uses plain fetch() - NO CSRF handling!
```

### CSRF Token Flow (Expected)

```
1. User visits landing page
   ↓
2. Frontend needs CSRF token before making requests
   ↓
3. Call /auth/register or GET /auth/csrf-token
   ← Backend returns csrf_token in response header OR response body
   ↓
4. Frontend stores csrf_token in localStorage
   ↓
5. Frontend adds X-CSRF-Token header on all mutations
   ↓
6. Backend validates: X-CSRF-Token matches session CSRF
   ↓
7. Request succeeds (201 Created, 200 OK, etc.)
```

**Actual Flow (Broken):**

```
1. User visits landing page (no csrf_token in localStorage)
   ↓
2. User clicks "Register"
   ↓
3. Frontend calls POST /auth/register (plain fetch, no CSRF token)
   ↓
4. Backend receives request WITHOUT X-CSRF-Token header
   ↓
5. WTF_CSRF_ENABLED=True checks for CSRF token - VALIDATION FAILS
   ↓
6. Returns HTTP 403 with body: {"error": "csrf_failed"}
```

---

## Configuration Analysis

### Backend CSRF Settings (lifeos/config.py)

```python
# BaseConfig (applies to all environments)
WTF_CSRF_ENABLED = True                    # ← Always enabled
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"           # ← May be too restrictive for cross-origin
SESSION_COOKIE_SECURE = False              # ← ⚠️ MISMATCH with production HTTPS

JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
JWT_COOKIE_CSRF_PROTECT = True
JWT_COOKIE_SECURE = SESSION_COOKIE_SECURE  # ← Inherits False from above
JWT_COOKIE_SAMESITE = SESSION_COOKIE_SAMESITE
JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=30)
```

### Production Config (fly.toml)

```toml
[http_service]
  processes = ['web']
  internal_port = 8080
  force_https = true                       # ← HTTPS enforced
  auto_stop_machines = 'off'
  auto_start_machines = true
```

**Mismatch Found:**
- ✅ Production forces HTTPS: `force_https = true`
- ❌ CSRF cookies set to `SESSION_COOKIE_SECURE = False`
- ❌ Cross-origin cookies with `SameSite=Lax` may not be sent by browser

### Frontend API Client (frontend/lib/api/client.ts)

**Current Implementation:**
```typescript
export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const tokens = getTokens()  // Reads from localStorage

  if (tokens?.csrf_token && MUTATION_METHODS.has(method)) {
    headers['X-CSRF-Token'] = tokens.csrf_token  // ← Adds header if csrf_token exists
  }

  const res = await fetch(`${API_URL}${path}`, { ...options, headers })
  // ⚠️ Note: Did NOT include credentials: 'include' for cross-origin requests
}
```

**Problem:** Missing `credentials: 'include'` means:
- Browser won't send cookies with cross-origin requests
- CSRF validation checks session cookies - if no cookies sent, validation fails

### Registration Endpoint (lifeos/core/auth/controllers.py:48-77)

```python
@auth_bp.post("/register")
@limiter.limit("5/minute")
def register():
    # ⚠️ No @csrf_protected decorator
    # ⚠️ No CSRF token validation

    payload = request.get_json(silent=True) or {}

    # ... validation and user creation ...

    resp = {"ok": True, "user": serialize_user(user).model_dump()}
    if "access_token" in result:
        resp.update({
            "access_token": result["access_token"],
            "refresh_token": result["refresh_token"],
            "csrf_token": result["csrf_token"],  # ← Returns csrf_token
        })
    return jsonify(resp), 201
```

**Problem:** Registration endpoint:
- ✅ Returns `csrf_token` in response
- ❌ Doesn't require CSRF token to register
- ❌ Frontend doesn't know to call this first before other APIs

---

## Error Scenarios & Fixes

### Scenario 1: POST /auth/register Returns 403

**Error Details:**
```
Failed to load resource: the server responded with a status of 403
URL: https://lifeos-black-pond-2352.fly.dev/auth/register
X-CSRF-Token header: Missing or invalid
```

**Root Cause Analysis:**
1. Frontend's `provider.tsx` uses plain `fetch()` (not `apiFetch()`)
2. Doesn't include `credentials: 'include'` (needed for cross-origin cookies)
3. Doesn't set `X-CSRF-Token` header (none exists yet)
4. Backend WTF_CSRF sees no CSRF token → rejects with 403

**Fix:**
```typescript
// frontend/lib/auth/provider.tsx
const res = await fetch(`${API_URL}/auth/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(input),
  credentials: 'include',  // ← ADD: Send cookies with cross-origin request
})
```

OR: Disable CSRF for registration endpoint:
```python
# lifeos/core/auth/controllers.py
@auth_bp.post("/register")
@limiter.limit("5/minute")
def register():
    # If CSRF should be disabled for unauthenticated registration
    # explicitly mark it safe, OR handle CSRF token seeding
    ...
```

### Scenario 2: GET/POST /api/habits Returns 403

**Error Details:**
```
Failed to load resource: the server responded with a status of 403
URL: https://lifeos-black-pond-2352.fly.dev/api/habits
X-CSRF-Token header: Missing or invalid
```

**Root Cause Analysis:**
1. User successfully logged in and has `csrf_token` in localStorage
2. Frontend `apiFetch()` adds `X-CSRF-Token: <token>` header ✓
3. BUT `apiFetch()` doesn't include `credentials: 'include'`
4. Response cookies not sent by browser (cross-origin + no credentials flag)
5. Backend can't validate CSRF token from session cookies → 403

**Fix:**
```typescript
// frontend/lib/api/client.ts
export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  // ... existing code ...

  const res = await fetch(`${API_URL}${path}`, {
    ...options,
    headers,
    credentials: 'include',  // ← ADD: Enable cross-origin cookies
  })
}
```

### Scenario 3: Session Cookie Secure Flag Mismatch

**Production Issue:**
- Fly.io enforces HTTPS: `force_https = true`
- Session cookies set `Secure=False` in config
- HTTPS browser won't send insecure cookies over HTTP

**Fix in Production:**
```python
# In production environment override
class ProductionConfig(BaseConfig):
    ENV = "production"
    DEBUG = False
    SESSION_COOKIE_SECURE = True        # ← HTTPS requires Secure=True
    JWT_COOKIE_SECURE = True
```

OR use environment variable:
```bash
# In fly.toml [env] section
SESSION_COOKIE_SECURE = 'true'
JWT_COOKIE_SECURE = 'true'
```

---

## Diagnostics & Debugging

### How to Determine Which Issue You Have

**Test 1: Check if CSRF token is being sent**
```bash
# In browser DevTools, Network tab, check POST /auth/register request:
# Headers section should show:
#   X-CSRF-Token: <some-token>
# If missing → Issue is "credentials: 'include' not set"
```

**Test 2: Check if CSRF token exists in storage**
```javascript
// In browser console:
const stored = localStorage.getItem('lifeos_tokens')
console.log(JSON.parse(stored).csrf_token)
// Should print a token string, not undefined
```

**Test 3: Check cookies being sent**
```bash
# In browser DevTools, Network tab, check any request:
# Request Headers → Cookie: should show session cookies
# If empty → "credentials: 'include'" not set or cross-origin restriction
```

**Test 4: Verify HTTPS and cookie flags**
```bash
# In browser DevTools, Application → Cookies → lifeos-black-pond-2352.fly.dev
# Should see cookies with:
#   Secure: ✓ (for HTTPS)
#   SameSite: Lax or None
# If Secure is false but URL is HTTPS → Issue is config mismatch
```

### Backend Debugging

**Check CSRF validation in logs:**
```bash
# In Fly.io logs
fly logs -a lifeos-black-pond-2352

# Look for:
# "CSRF validation failed" → csrf_token not in cookies
# "Missing CSRF token" → X-CSRF-Token header not set
# "Invalid CSRF token" → Token doesn't match session
```

**Enable verbose logging:**
```toml
# fly.toml
[env]
  FLASK_DEBUG = 'true'
  GUNICORN_LOGLEVEL = 'debug'
```

---

## Implementation Checklist

### For Frontend Team

- [ ] Update `frontend/lib/api/client.ts` - Add `credentials: 'include'` to all fetch calls
- [ ] Update `frontend/lib/auth/provider.tsx` registration flow - Add `credentials: 'include'`
- [ ] Verify `localStorage.getItem('lifeos_tokens')` returns `csrf_token` after login
- [ ] Test cross-origin requests in DevTools Network tab
- [ ] Verify X-CSRF-Token header appears on mutation requests

### For Backend Operations

- [ ] Update production config to set `SESSION_COOKIE_SECURE = 'true'` in fly.toml [env]
- [ ] Verify `force_https = true` is set in fly.toml (already is)
- [ ] Review CSRF decorator usage on all endpoints
- [ ] Test via curl with proper headers:
  ```bash
  curl -X POST https://lifeos-black-pond-2352.fly.dev/auth/register \
    -H "Content-Type: application/json" \
    -H "X-CSRF-Token: $CSRF_TOKEN" \
    -b "session=$SESSION_COOKIE" \
    -d '{"email":"test@example.com","password":"test123"}'
  ```
- [ ] Update monitoring to track 403 CSRF failures separately

### For DevOps

- [ ] Ensure CORS headers not blocking legitimate cross-origin requests
- [ ] Check Fly.io HTTP service configuration → no blocking settings
- [ ] Review Cloudflare settings if in front (may filter CSRF headers)

---

## Related Configuration Files

- **Backend config:** [lifeos/config.py](../../lifeos/config.py#L51-L57)
- **Frontend API client:** [frontend/lib/api/client.ts](../../frontend/lib/api/client.ts)
- **Auth endpoints:** [lifeos/core/auth/controllers.py](../../lifeos/core/auth/controllers.py#L48-L77)
- **Habits API:** [lifeos/domains/habits/controllers/habit_api.py](../../lifeos/domains/habits/controllers/habit_api.py)
- **Production deployment:** [fly.toml](../../fly.toml#L1-L30)

---

## References

- Flask-WTF CSRF Protection: https://flask-wtf.readthedocs.io/
- WTForms CSRF: WTF_CSRF_ENABLED enforces CSRF on all endpoints with GET/POST/PUT/DELETE
- Cross-origin credentials: MDN - fetch() credentials: 'include'
- SameSite cookies: Browser security model for cross-origin requests
