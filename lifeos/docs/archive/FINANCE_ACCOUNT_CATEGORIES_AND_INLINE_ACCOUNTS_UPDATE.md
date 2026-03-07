# LifeOS Finance: Advanced Account Categories & Inline Accounts Update

**Role:** Backend + Frontend Handoff
**Scope:** Account categories, inline account creation, trial balance grouping
**Status:** Implemented (tests green in `lifeos/tests`)

---

## 1) Context & Goals
- Reduce friction: users can create accounts inline with minimal fields and get clean trial balance grouping.
- Standardize account classification: base types + optional subtypes + categories (system and user defaults).
- Deliver consistent API surface for frontend (search, inline create, subtypes, categories) with explicit error codes.

## 2) Data Model & Services
- `AccountCategory` expanded: `code`, `slug`, `base_type`, `normal_balance`, `is_default`, `is_system`. User or system-scoped.
- `Account` classification: `account_type` (asset/liability/equity/income/expense), optional `account_subtype`, `normalized_name`, `category_id` nullable, `created_at` present.
- Service logic (`accounting_service.py`):
  - Category normalization + slug/code generation.
  - Default resolution: prefer user default; else system default; else create user default.
  - Custom category create with optional default toggle; idempotent on slug/base_type.
  - Account create/update: validates type/subtype, normalizes names, idempotent on normalized name, attaches categories, emits events.
  - Subtypes map exposed via `get_account_subtypes`.
- Trial balance (`trial_balance_service.py`): returns `accounts` plus `categories` rollups keyed by (base_type, category_id); uncategorized labeled "Uncategorized"; net respects category normal balance.

## 3) APIs (all under `/api/finance`)
- `GET /api/finance/accounts/search` (JWT): query params `q`, `limit`, `include_ml`; errors `invalid_query`/`validation_error`.
- `POST /api/finance/accounts/inline` (JWT + role `finance:write` + CSRF): body `name`, `account_type`, optional `account_subtype`; errors `invalid_account_type`, `invalid_account_subtype`, `invalid_name`, `validation_error`; idempotent on normalized name.
- `GET /api/finance/accounts/subtypes/<type>` (public): returns subtypes; `invalid_account_type` on bad type.
- `GET /api/finance/account-categories` (JWT): list user + system categories; filters `base_type`, `include_system`.
- `POST /api/finance/account-categories` (JWT + role `finance:write` + CSRF): create custom category; optional `is_default` flips prior default for that base_type/user.

## 4) Migration Notes
- Migrations: `20251206_finance_account_type_classification.py`, `20251218_backend_updates_validation.py` (both marked `TWO_PHASE = True` due to `op.execute` backfills/validations).
- Validation migration ensures columns/indexes exist and backfills `normalized_name` for existing accounts; does not drop data.

## 5) Frontend Integration Hints
- Use `/api/finance/accounts/search` for typeahead (requires Authorization header bearer JWT).
- Inline create requires JWT + `finance:write` role + `X-CSRF-Token` when CSRF enabled; handle specific error codes above.
- Subtypes endpoint is unauthenticated; safe for populating dropdowns.
- Trial balance responses now include `categories` rollups; show "Uncategorized" when `category_id` is null.

## 6) Testing
- Finance API suites all pass (`.venv/bin/pytest lifeos/tests/test_finance_*`).
- New service/grouping coverage: `lifeos/tests/test_finance_services_and_trial_balance.py`.
- Full LifeOS suite: `.venv/bin/pytest lifeos/tests` → 86 passed (only legacy SQLAlchemy warnings).

## 7) Impact Summary
- Backend: account/category creation/update paths hardened; category defaults deterministic; events enriched.
- DB: additive-safe migrations with backfill; no destructive ops.
- Frontend: consistent endpoints and error codes; trial balance grouping now category-aware with uncategorized bucket.
