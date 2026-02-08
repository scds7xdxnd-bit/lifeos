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
