# LifeOS

## Quick start
- Create and activate a virtualenv, then install: `pip install -r lifeos/requirements.txt`
- Copy `.env.example` to `.env` and fill secrets/paths
- Run DB migrations: `FLASK_APP=lifeos.wsgi flask db upgrade`
- Seed admin and demo data: `python -m lifeos.scripts.seed_all_demo`
- Run the app: `gunicorn -c lifeos/gunicorn.conf.py lifeos.wsgi:app` (or `python -m lifeos.wsgi` for dev)

Default users:
- Admin: `admin@example.com` / `admin12345`
- Demo: `demo@lifeos.test` / `demo12345`

## Configuration
- `SECRET_KEY`, `JWT_SECRET_KEY`: set to strong secrets in production
- `DATABASE_URL`: e.g., `postgresql://user:pass@host:5432/lifeos`
- `REDIS_URL`: for rate limiting (defaults to memory)
- `MLSUGGESTER_MODEL_DIR`: path to legacy joblib models (defaults to `flask_app`)
- `ENABLE_ML`: toggle legacy/embedding model usage

## Tests & CI
- Run tests: `pytest lifeos/tests`
- CI workflow: `.github/workflows/ci.yml`

## Make targets
- `make install` (create venv + install deps)
- `make test`
- `make run`
- `make seed`
