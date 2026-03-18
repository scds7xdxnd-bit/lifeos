# CSRF 403 Fixes - Applied Changes

**Date Applied:** 2026-03-18
**Status:** ✅ Complete

## Changes Made

### 1. Frontend API Client - frontend/lib/api/client.ts

**Issue:** Cross-origin requests not sending cookies needed for CSRF validation

**Fix Applied:**
```typescript
// BEFORE (line 40)
const res = await fetch(`${API_URL}${path}`, { ...options, headers })

// AFTER (lines 40-46)
const res = await fetch(`${API_URL}${path}`, {
  ...options,
  headers,
  credentials: 'include',  // Enable cross-origin cookies for CSRF validation
})
```

**Impact:** Now all API calls (GET, POST, PATCH, DELETE) will send cookies with cross-origin requests, allowing CSRF token validation.

---

### 2. Frontend Registration Flow - frontend/lib/auth/provider.tsx

**Issue:** Registration endpoint using plain fetch() without credentials flag

**Fix Applied:**
```typescript
// BEFORE (lines 73-78)
const res = await fetch(`${API_URL}/auth/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(input),
})

// AFTER (lines 73-79)
const res = await fetch(`${API_URL}/auth/register`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(input),
  credentials: 'include',  // Enable cross-origin cookies for CSRF validation
})
```

**Impact:** Registration requests now send cookies, allowing backend CSRF token validation instead of immediately rejecting with 403.

---

### 3. Production Configuration - fly.toml

**Issue:** HTTPS enforced in production but CSRF cookie Secure flag not set

**Fix Applied:**
```toml
# ADDED to [env] section (lines 72-73)
  SESSION_COOKIE_SECURE = 'true'
  JWT_COOKIE_SECURE = 'true'
```

**Impact:**
- Session cookies now marked as Secure, required for transmission over HTTPS
- JWT cookies marked as Secure, ensuring they only travel over HTTPS
- Aligns production config with `force_https = true` setting

---

## Technical Details

### What These Changes Fix

| Error | Root Cause | Fix |
|-------|-----------|-----|
| `POST /auth/register` → 403 | Cross-origin request without credentials | Added `credentials: 'include'` to registration fetch |
| `GET/POST /api/habits` → 403 | Cookies not sent on cross-origin requests | Added `credentials: 'include'` to apiFetch() |
| HTTPS cookie mismatch | Secure flag not set in production | Set `SESSION_COOKIE_SECURE = 'true'` in fly.toml |

### How CSRF Validation Now Works

1. User registers: `POST /auth/register` (with `credentials: 'include'`)
2. Browser sends cross-origin cookies + request
3. Backend validates CSRF token from session cookie
4. ✅ Request succeeds (201 Created)
5. Response includes `csrf_token` in body
6. Frontend stores in localStorage
7. Subsequent API calls include `X-CSRF-Token` header
8. ✅ APIs work correctly (200 OK)

---

## Deployment Instructions

### For Fly.io

```bash
# Deploy the updated configuration
fly deploy -a lifeos-black-pond-2352

# Verify deployment
fly status -a lifeos-black-pond-2352

# Check logs for successful startup
fly logs -a lifeos-black-pond-2352
```

### For Local Development

```bash
# Frontend changes are immediate (hot reload)
# No build needed for frontend changes

# For backend config changes in local testing:
# Update your .env file with:
# SESSION_COOKIE_SECURE = true
# JWT_COOKIE_SECURE = true
```

---

## Verification Checklist

After deployment, verify fixes are working:

- [ ] Navigate to registration page
- [ ] Attempt to register a new user
- [ ] Check Network tab: `POST /auth/register` should return 201 (not 403)
- [ ] Verify cookies sent: Network → Request headers → Cookie
- [ ] Verify CSRF token: DevTools Console → `JSON.parse(localStorage.getItem('lifeos_tokens')).csrf_token`
- [ ] Call `/api/habits`: Should return 200 (not 403)
- [ ] Verify X-CSRF-Token header in requests: Network → Request headers

---

## Rollback Instructions

If issues occur, revert changes:

```bash
# Revert frontend/lib/api/client.ts
git checkout frontend/lib/api/client.ts

# Revert frontend/lib/auth/provider.tsx
git checkout frontend/lib/auth/provider.tsx

# Revert fly.toml
git checkout fly.toml

# Redeploy
fly deploy -a lifeos-black-pond-2352
```

---

## Related Files

- [CSRF_403_TROUBLESHOOTING.md](./CSRF_403_TROUBLESHOOTING.md) - Full technical guide
- [frontend/lib/api/client.ts](../../frontend/lib/api/client.ts)
- [frontend/lib/auth/provider.tsx](../../frontend/lib/auth/provider.tsx)
- [fly.toml](../../fly.toml)
- [lifeos/config.py](../../lifeos/config.py)

---

## References

- Flask-WTF CSRF: https://flask-wtf.readthedocs.io/
- Fetch API credentials: https://developer.mozilla.org/en-US/docs/Web/API/fetch#credentials
- SameSite cookies: https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Set-Cookie/SameSite
