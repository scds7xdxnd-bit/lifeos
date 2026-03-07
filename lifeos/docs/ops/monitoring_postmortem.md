# Monitoring Post-Mortem (Local Dev)

Below is a consolidated, technical post-mortem of what went wrong, how it was diagnosed, how it was fixed, and what to institutionalize so this does not recur.

---

## 1) cAdvisor "errors" that were not actually fatal

### Symptom

`lifeos-cadvisor` logs included warnings/errors such as:

- "Nodes topology is not available..."
- "Failed to get system UUID: open /etc/machine-id: no such file..."
- "Couldn't collect info from ... machine-id"

### Root cause

cAdvisor tries to read host machine identity and topology data (e.g., `/etc/machine-id`, NUMA topology, CPU vendor id). On macOS Docker Desktop, containers run in a Linux VM and the host filesystem mapping is non-standard. These identity files often do not exist in the expected places (or cannot be accessed), so cAdvisor logs warnings.

### Why it looked scary

The logs contain `E`/`W` prefixes and phrases like "Failed to get system UUID," which look severe. But they are largely about metadata, not the core metrics pipeline.

### Fix / disposition

No change required for core monitoring. Metrics collection still works as long as `/metrics` is exposed and Prometheus scrapes successfully.

### Future notes

- Treat these messages as non-blocking noise unless you see missing metrics or scrape failures.
- The correct success criteria is:
  - cAdvisor endpoint responds: `curl http://127.0.0.1:8080/metrics`
  - Prometheus target is `UP`
  - Prometheus has series like `container_cpu_usage_seconds_total`

---

## 2) Prometheus/Grafana looked "empty" after restart

### Symptom

After restarting Prometheus and Grafana:

- Targets were `UP`, but graphs were empty.
- Prometheus "Graph" page had no PromQL expression.
- Grafana had no visible charts/dashboards.

### Root cause

Two separate "normal" behaviors:

1. Prometheus does not display graphs without a query. "Empty graph" is expected if you did not enter PromQL.
2. Grafana is just a renderer. Without a configured datasource + dashboards (or imported dashboards), it will look empty even though Prometheus is scraping.

Additionally, if you ever recreate containers with volume removal (`down -v`), you lose:

- Prometheus time-series history
- Grafana saved dashboards/state

So "empty" can also mean "data was wiped and is only accumulating from now."

### Fix / actions taken

- Verified Prometheus ingestion via PromQL sanity checks:
  - `up`
  - `scrape_samples_scraped`
- Verified metrics existence (e.g., `container_*` metrics).
- Validated Grafana datasource connectivity (common pitfall: using `localhost:9090` from inside a container; correct is `http://prometheus:9090` on the Docker network).
- Imported or provisioned dashboards as needed.

### Future notes

Create a standard "monitoring sanity checklist":

- Prometheus:
  - Targets all `UP`
  - `up` returns time-series
  - `scrape_samples_scraped` non-zero
- Grafana:
  - Explore -> query `up` against Prometheus datasource (fastest verification)
  - Ensure datasource URL uses Docker service name (`prometheus:9090`) if Grafana is containerized
- Persist volumes; avoid `down -v` unless you explicitly intend to wipe monitoring history.

---

## 3) `/api/v1/insights/proposals` returned 404 even though routes existed

### Symptom

Frontend network calls:

- `GET http://127.0.0.1:8000/api/v1/insights/proposals?status=proposed`
- returned `404 NOT FOUND`

But `flask routes` on your codebase showed the route exists:

- `GET /api/v1/insights/proposals`

### Root cause

You had a port ownership collision:

- A host-run Python server was listening on IPv4 `*:8000` (127.0.0.1).
- Docker was also forwarding `*:8000` (notably on IPv6 / Docker bridge).

Result:

- Requests to `127.0.0.1:8000` (IPv4) went to the host Python server (stale/older build) -> 404
- Requests that resolved via IPv6/localhost could go to Docker container -> correct routes

This created a confusing split-brain: "routes exist" but "runtime returns 404."

### How you diagnosed it

- `lsof -nP -iTCP:8000 -sTCP:LISTEN` showed both Python processes and Docker listening.
- `docker ps` confirmed `lifeos-web` published port `8000->8000`.
- `docker exec -it lifeos-web flask routes` proved the route existed in the container, not in the host server you were hitting.

### Fix / actions taken

- You killed the host Python process (`kill 70242`), leaving only Docker to own port 8000.
- Re-tested the endpoint:
  - It returned `200 OK` with a valid JSON payload.

### Future notes (critical)

Institutionalize "single source of truth" for ports:

- Do not run host server on the same port as Docker’s published port.
- Pick one of these operating modes:
  - Docker-only backend on 8000 (recommended)
  - Host backend on 8001 and Docker on 8000 (or vice versa)
- Add a preflight guard before starting anything on port 8000:
  - `lsof -nP -iTCP:8000 -sTCP:LISTEN`
- When debugging "404 but route exists," always confirm which process answers the port.

---

## 4) `/auth/login` returned 401 invalid_credentials

### Symptom

`POST /auth/login` with JSON `{email, password}` returned:

- `401 UNAUTHORIZED`
- response body: `{"error":"invalid_credentials","ok":false}`

### Root cause

The backend was functioning correctly; it was rejecting the credentials because:

- the user did not exist in the DB used by the runtime, or
- the password did not match the stored hash.

Complicating factors:

- You had previously used different runtimes (host vs Docker), which can point to different SQLite DB files.
- You also had an expired token during validation (`/auth/me` returned "Token has expired"), which is normal but added noise.

### How you diagnosed it

- Verified the correct routes existed for auth (`flask routes | rg auth|login`).
- Confirmed the runtime DB env vars inside container:
  - `DATABASE_URL=sqlite:///instance/lifeos.db`
- Confirmed the DB file exists inside the container and has tables.
- Enumerated tables with Python because `sqlite3` CLI was not installed inside container:
  - Observed user table name was `user` (not `users`).

### Fix / actions taken

- Stopped assuming host DB == Docker DB.
- Migrated/replicated the old DB content into the Docker environment, so the expected user/records existed.

### Future notes

- Make "which DB am I using?" explicit every time:
  - On host: check env and file path
  - In container: `docker exec lifeos-web printenv | rg DATABASE_URL`
- Prefer a bind mount for the `instance/` folder if you want host and container to share the exact same SQLite DB file.
- Treat `invalid_credentials` as "user mismatch / DB mismatch" first, not as a network or routing issue.

---

## 5) Migrating data from old local DB to Docker DB

### Symptom

You attempted to import an SQL dump into the container DB and got:

- `sqlite3.OperationalError: table alembic_version already exists`

Later you also hit:

- `FileNotFoundError: /tmp/lifeos_dump.sql` after restarting containers.

You also ran:

- `docker compose up -d lifeos-web`
- got `no such service: lifeos-web`

### Root causes

There were three distinct operational issues:

1. Importing into a non-empty DB
   The container DB already had schema (including `alembic_version`), so applying a full `.dump` script collided with existing tables.
2. Ephemeral /tmp in container
   The SQL dump file copied to `/tmp` inside the container is not persistent. If the container is recreated, the file disappears.
3. Confusing container name vs compose service name
   `lifeos-web` is a container name. Compose starts service names (often `web`), not container names, so `docker compose up ... lifeos-web` can fail depending on your compose definition.

### Fix / actions taken

- Correctly made the target DB empty before import:
  - Backed up container DB.
  - Deleted `instance/lifeos.db` inside container and recreated it.
- Re-copied the dump file after container recreation (because `/tmp` was wiped).
- Started services using correct Compose service naming:
  - Use `docker compose config --services` to get the real service names.
  - Use `docker compose up -d` or `docker compose up -d <service>`.

### Future notes (best practice)

- For SQLite migration, choose one of two safe patterns:
  - Pattern A: Replace the DB file (fastest, least error-prone)
  - Pattern B: Dump/import (portable but requires empty target)
- Never rely on container `/tmp` for persistence. If you need persistence, use:
  - a bind mount, or
  - copy the file again, or
  - store it in a mounted volume.
- Add a "compose discipline" rule:
  - Use `docker compose config --services` to identify service names.
  - Use `docker ps` for container names.
  - Do not mix the two.

---

## Operational Runbook: What you should do next time (short form)

### A. If you see "route exists but 404"

1. `lsof -nP -iTCP:<port> -sTCP:LISTEN`
2. Confirm which process owns the port
3. `docker exec <container> flask routes | rg <keyword>`
4. Kill the competing server or change ports

### B. If login returns `invalid_credentials`

1. Confirm DB env in runtime (`DATABASE_URL`)
2. Confirm user exists in that DB (query via Python if sqlite3 missing)
3. Register or migrate data into that DB
4. Only then debug password hashing / reset flows

### C. If Grafana is empty

1. Prometheus UI: run `up`
2. Grafana Explore: run `up`
3. Fix datasource URL (container: use `http://prometheus:9090`)
4. Import/provision dashboards
5. Confirm volumes not wiped

---

## Recommendation to lock stability in

1. Chosen "single backend mode":
   - We will do Docker-only on 8000, no host-only or hybrid on 8000.
2. Add a short `docs/ops/local_run.md` with:
   - start/stop commands
   - sanity queries (`up`, `scrape_samples_scraped`)
   - port ownership check
3. SQLite should not be shared across host and docker:
   - treat container DB as canonical and stop using host-run DB.

---

## Why the Docker DB differed from the local DB

Your `web` service uses named Docker volumes:

- `lifeos-instance:/app/instance`
- `lifeos-logs:/app/logs`

That means:

- The SQLite database file `sqlite:///instance/lifeos.db` lives in `/app/instance/lifeos.db` inside a Docker-managed volume, not in your repo folder.
- When you run the app on the host (e.g., `python3 lifeos/wsgi.py`), it will use your host filesystem (likely `./instance/lifeos.db`), which is a completely different file.
- Therefore, Docker DB and local DB will diverge unless you explicitly mount the same directory.

This is the correct explanation for the credential mismatch and why you had to migrate data.

---

## Recommended fix: bind-mount `./instance` in development (and keep named volumes for production)

You generally want two different behaviors:

- Local development: share the same DB file and artifacts between host and container, so you do not get split-brain.
- Production-like runs: use Docker volumes for isolation and persistence.

### Option A (best practice): create a `docker-compose.override.yml` for local dev

Leave your base compose as-is (good for prod-like), and add an override file that only applies locally.

Create `docker-compose.override.yml` (Compose automatically picks it up):

```yaml
services:
  web:
    volumes:
      - ./instance:/app/instance
      - ./logs:/app/logs
```

What this does:

- Replaces the Docker volume `lifeos-instance` with your host folder `./instance`.
- Replaces Docker volume `lifeos-logs` with your host folder `./logs`.

Then:

```bash
mkdir -p instance logs
docker compose up -d --build
```

Now both:

- host-run app and
- docker-run app

can point at the same physical file if you also standardize host config to use `instance/lifeos.db`.

### Notes

- This prevents "I created a user in host DB but Docker can't log in" forever.
- It also makes DB backup/inspection trivial because the file is on your host.

### Option B: use bind mounts directly in your main compose (simple, but less clean)

Change your existing `web.volumes` from:

```yaml
volumes:
  - lifeos-instance:/app/instance
  - lifeos-logs:/app/logs
```

to:

```yaml
volumes:
  - ./instance:/app/instance
  - ./logs:/app/logs
```

This is fine if you are only using this compose file for local dev. If you deploy with the same compose file, do not do this; use Option A.

---

## Operational notes for your team (what to standardize)

### 1) Decide which DB is canonical per environment

- Local dev canonical: `./instance/lifeos.db`
- Container canonical: `/app/instance/lifeos.db` (bind-mounted to `./instance`)

### 2) Add explicit "no port collision" rule

Because you previously ran host Python and docker web on the same port:

- Either only run Docker, or run host on a different port (8001).

### 3) Add a repeatable DB migration procedure

When you must move data:

- If using bind mounts, migration becomes "copy file into ./instance/".
- If using Docker volumes, keep the dump/import procedure as a documented fallback.

### 4) Make the "compose mode" obvious

- Prod-like mode: named volumes (current base compose)
- Dev mode: override to bind mounts

---

## Practical next step (to implement now)

If you want to eliminate split-brain immediately with minimal risk, do Option A:

1. Create `docker-compose.override.yml` with the bind mounts.
2. Create the directories:

```bash
mkdir -p instance logs
```

3. Restart:

```bash
docker compose down
docker compose up -d --build
```

If you want, we can provide an exact diff patch for the repo (including a short `docs/ops/local_db.md` explaining why this matters and how to switch modes).
