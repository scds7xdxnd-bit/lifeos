Finance App (Flask)
===================

Modern bookkeeping app with transactions, folders/accounts, and an interactive Trial Balance setup. Includes admin tools and optional ML account suggesters.

Features
--------
- Users + sessions; Admin dashboard (Admin1 protected)
- Transactions: add, edit, delete, CSV import, full‑DB filtering, AJAX filters/pagination
- Accounting: folders and accounts with drag‑and‑drop, renaming, codes
- Trial Balance: first‑time grouping wizard (drag folders into Asset/Liability/Equity/Expense/Income), then opening balances per account with completion ticks
- Loan threads: group receivable/payable flows, link repayments, and view contact timelines
- Optional ML suggesters for debit/credit fields

Requirements
------------
Install from `requirements.txt`:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run
---

```bash
export FLASK_APP=app.py
flask run
# or
python3 wsgi.py
PYTHONPATH=flask_app/ml-suggester-repo uvicorn ml_suggester.api_server:app --reload --port 8001
ml-suggester transform --input data/data.xlsx --out output.parquet --out-format parquet --currencies "KRW,MYR,CNY"

```

Open http://127.0.0.1:5000

Database & migrations
---------------------
- Default DB: `sqlite:///instance/finance_app.db` (both Flask and Alembic use this path). Override with `DATABASE_URL` (Flask) or `ALEMBIC_DATABASE_URL`/`--db-url` (Alembic/CLI).
- Apply schema: `PYTHONPATH=. alembic upgrade head` or `flask upgrade-schema --db-url <db-url>` to run against a specific database.
- Backups: timestamped copies live in `instance/backups/`; keep a fresh copy before wiping or rebasing.

Configuration & Hardening
-------------------------
- Environment: set `APP_ENV` to `development` (default), `staging`, or `production` for cookie/security tweaks.
- Uploads: override `UPLOAD_ALLOWED_EXTENSIONS` (default `csv,png,jpg,jpeg,gif,pdf`), `UPLOAD_FOLDER`, and `MAX_CONTENT_LENGTH` (default 10MB). Files are saved under `instance/uploads` by default.
- Static caching: `STATIC_CACHE_MAX_AGE` controls Cache-Control for `/static/` responses (default 3600s).
- Sessions: `SESSION_TTL_SECONDS`, `SESSION_COOKIE_SECURE`, and `SESSION_COOKIE_SAMESITE` can be set per environment.

Money Schedule (Daily Forecast)
-------------------------------
The money schedule feature delivers a daily cash forecast with actual end-of-day balances and inline editing.

1. Apply migrations to create the schedule, account, and snapshot tables:

   ```bash
   alembic upgrade head
   ```

2. (Optional) Seed demo data (accounts, snapshots, and schedule rows) for the current week:

   ```bash
   python3 scripts/seed_money_schedule.py
   ```

3. (Optional) Backfill empty days between two dates with zeroed rows:

   ```bash
   flask money-schedule-fill 2025-01-01 2025-01-31
   ```

4. Start the Flask server and open `http://127.0.0.1:5000/money-schedule`. From this page you can:
   - Review the initialization day (D₀); the money schedule automatically mirrors the Trial Balance initialization date so both modules stay in sync.
   - Update inflow/outflow/description inline; saves cascade forward, recomputing predicted closing, actuals, and variance.
   - Filter the visible window by adjusting the start/end range. All timestamps are evaluated in the Asia/Seoul timezone.
- Use the Baseline Accounts panel to decide which cash/checking/savings accounts seed the initialization balance.
- Actual balances are auto-computed from the Trial Balance initialization totals (cash/checking/savings) plus each day’s net inflow/outflow. Use the inline inputs to keep forecasts accurate.
- Configure recurring inflows/outflows via the Recurring Events modal (daily/weekly/monthly/custom cadences) to auto-fill upcoming days; switch to list view when you need to override a generated value.

5. Run the focused tests with:

   ```bash
   python3 -m pytest tests/test_money_schedule.py
   ```

Environment
-----------
- `SECRET_KEY`: Flask secret (set in production)
- `SESSION_COOKIE_SECURE`: `true|false` (default false)
- `DISABLE_ML`: `1` to avoid installing heavy ML deps; app will fall back gracefully

Loan Threads & Receivable Grouping
----------------------------------
- **Migration:** run `alembic upgrade head` (or `python -m alembic upgrade head`) to install the new `loan_group` and `loan_group_link` tables.
- **Backfill (optional):** `python scripts/backfill_loan_groups.py --dry-run` inspects existing receivable trackers and shows the loan threads it would create. Re-run with `--commit` to persist.
- **UI:** the Accounts → Receivables & Debt view now surfaces a _Loan Threads_ panel inside the contact overview modal (click a contact card). Create new threads, edit or delete existing ones, review running balances, and expand the timeline for allocations; per-loan status (open/closed/overpaid) is calculated automatically once repayments extinguish the principal.
- **REST endpoints:** `POST/GET/PATCH/DELETE /accounting/loan-groups`, `POST /accounting/transaction-links`, `DELETE /accounting/transaction-links/<id>`, `GET /accounting/loan-groups/<id>/summary`, `GET /accounting/loan-groups/<id>/entries`, and `POST /accounting/allocation/suggest` are available for programmatic control (all require an authenticated session and CSRF token for mutations).

CLI Tools (optional)
--------------------
- `flask prune-hints` – clean low-signal suggestion tokens
- `flask assign-account-ids` – backfill transaction FK ids
- `flask assign-codes` – assign/refresh account codes per folder

Refactor backlog
----------------
- Add service/controller extraction coverage for CSV import and money-schedule UI flows (tests + validations).
- Continue extracting accounting/transaction routes into services (receivables, loan groups, TB flows), and finalize double-entry cutover off legacy `Transaction`.
- Postgres cutover: set `DATABASE_URL=postgresql+psycopg2://user:pass@host:5432/finance_app` and `ALEMBIC_DATABASE_URL` to match; run `PYTHONPATH=. alembic upgrade head`; migrate data from SQLite via export/import script; drop SQLite-only pragmas after validation.

Smoke Test
----------

```bash
python3 scripts/smoke_test.py
```

Tips
----
- If both “Accounts” and “Trial Balance” toggles look active, hard refresh to reload assets; tabs now store last view and only one is active at a time.
- Transactions filters update instantly and keep the list open; Clear resets filters without a full page refresh.

License
-------
MIT
