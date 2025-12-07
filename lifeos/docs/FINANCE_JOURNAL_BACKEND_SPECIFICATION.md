# LifeOS Finance: Journal + Inline Account Creation Backend Specification

**Role:** LifeOS-Finance Backend Engineer  
**Scope:** Implement the new journal-first, inline account-creation workflow in the Finance domain  
**Status:** Specification (non-code)

---

## 1. Context & Goals

### 1.1 LifeOS Overview
LifeOS is a single-tenant, multi-domain personal operating system built on Flask + SQLAlchemy. It uses strict domain boundaries, an event-driven architecture, and a single Alembic migration home at `lifeos/migrations/`. The Finance domain is one of seven domains (Finance, Habits, Health, Skills, Projects, Relationships, Journal) and currently has an MVP with accounts, journal, trial balance, receivables, and forecasting.

### 1.2 Current Finance State
- **Models:** `Account`, `AccountCategory`, `JournalEntry`, `JournalLine`, `Transaction` (in `lifeos/domains/finance/models/accounting_models.py`)
- **Services:** `accounting_service.py`, `journal_service.py`, `trial_balance_service.py`, etc.
- **Controllers:** RESTful APIs in `lifeos/domains/finance/controllers/{journal_api.py, accounting_api.py, ...}`
- **Templates:** Basic Jinja2 views in `lifeos/templates/finance/`
- **Events:** Journal posted, transactions created, ML suggestions, etc. (catalog in `lifeos/domains/finance/events.py`)

### 1.3 Problem Statement
The old Finance App workflow forced users to:
1. Create an account (arbitrary name).
2. Encounter it as "unassigned."
3. Create folders (Cash, Bank, Debt categories).
4. Manually assign accounts to folders.
5. Assign folders to trial-balance groups (Assets/Liabilities/Equity/Income/Expense).
6. Only then could the trial balance be useful.

**This is unacceptable friction for a personal OS.** Users should be able to open the journal and start recording transactions immediately.

### 1.4 New Vision
- **Journal-first:** Users live in the journal entry form.
- **Inline account creation:** When typing an account name, they see a searchable dropdown. If the account doesn't exist, they choose "+ Create new account" and the system creates it with minimal input (name + account type).
- **Minimal classification at creation:** User picks account_type (Asset/Liability/Equity/Income/Expense) and optionally a subtype/category (Cash, Bank, Loan, etc.). This is enough for the trial balance to be clean.
- **Progressive refinement:** Later, users can visit a Chart of Accounts page (out of scope for now) to refine structure, but it is not a blocker.

---

## 2. Data Model & Schema Changes

### 2.1 Existing Models to Review
- `Account` (in `accounting_models.py`): Currently has `id`, `user_id`, `category_id` (FK to AccountCategory), `name`, `code`, `description`, `is_active`.
- `AccountCategory`: Has `id`, `code`, `name`, `normal_balance` (debit/credit).
- `JournalEntry` / `JournalLine`: Double-entry structure; already functional.

### 2.2 Schema Changes Required

#### 2.2.1 Add Account Type Classification
**Update** `Account` model to add:
```
account_type: Mapped[str] = mapped_column(
    db.String(16),
    nullable=False,
    default="asset",
    index=True
)
# Enum values: 'asset', 'liability', 'equity', 'income', 'expense'

account_subtype: Mapped[str | None] = mapped_column(
    db.String(64),
    nullable=True
)
# Examples: 'cash', 'bank', 'loan', 'credit_card', 'income_salary', 'income_investment', etc.

normalized_name: Mapped[str] = mapped_column(
    db.String(255),
    nullable=False,
    index=True
)
# Normalized (lowercase, stripped, deduplicated whitespace) for fast search/typeahead.

created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
# Track when account was created (for sorting, filtering).
```

**Rationale:**
- `account_type` enables trial-balance grouping without folder hierarchy.
- `account_subtype` allows optional categorization for more granular TB views (future enhancement).
- `normalized_name` enables fast typeahead searches (exact-match and prefix-match queries).
- `created_at` enables chronological ordering in searches and sorting recent accounts first.

#### 2.2.2 Drop or Deprecate AccountCategory Relationship
- `AccountCategory` (currently 1-to-many with Account via `category_id`) will become **optional** or deprecated.
- Going forward, classification is via `account_type` + `account_subtype`, not `AccountCategory`.
- **For backwards compatibility:** Existing Accounts will be migrated: either map their category to an account_type, or set a sensible default (e.g., 'asset') and require users to refine later.

#### 2.2.3 Alembic Migration
**File:** `lifeos/migrations/versions/<timestamp>_finance_account_type_classification.py`

**DDL (high-level):**
```sql
ALTER TABLE finance_account
  ADD COLUMN account_type VARCHAR(16) NOT NULL DEFAULT 'asset';

ALTER TABLE finance_account
  ADD COLUMN account_subtype VARCHAR(64) DEFAULT NULL;

ALTER TABLE finance_account
  ADD COLUMN normalized_name VARCHAR(255) NOT NULL DEFAULT '';

ALTER TABLE finance_account
  ADD COLUMN created_at TIMESTAMP DEFAULT NOW();

CREATE INDEX ix_finance_account_user_type
  ON finance_account(user_id, account_type);

CREATE INDEX ix_finance_account_normalized_name
  ON finance_account(user_id, normalized_name);

-- Backfill: normalize existing account names and set defaults
UPDATE finance_account
SET
  normalized_name = LOWER(TRIM(name)),
  account_type = COALESCE(
    CASE WHEN category_id IN (SELECT id FROM finance_account_category WHERE code = 'ASSET') THEN 'asset'
         WHEN category_id IN (SELECT id FROM finance_account_category WHERE code = 'LIABILITY') THEN 'liability'
         WHEN category_id IN (SELECT id FROM finance_account_category WHERE code = 'EQUITY') THEN 'equity'
         WHEN category_id IN (SELECT id FROM finance_account_category WHERE code = 'INCOME') THEN 'income'
         WHEN category_id IN (SELECT id FROM finance_account_category WHERE code = 'EXPENSE') THEN 'expense'
         ELSE 'asset'
    END,
    'asset'
  ),
  created_at = COALESCE(created_at, NOW());
```

**Note:** Additive migration; no existing data is destructed. Backfill uses a management command if too complex for Alembic.

---

## 3. Services & Domain Logic

### 3.1 Account Search Service (`accounting_service.py` new methods)

#### 3.1.1 `search_accounts(user_id: int, query: str, limit: int = 20) -> List[Account]`
**Purpose:** Typeahead search for existing accounts.

**Logic:**
1. Normalize the query (lowercase, trim whitespace).
2. Query accounts where:
   - `user_id == user_id`
   - `is_active == true`
   - `normalized_name` starts with normalized query (prefix match) OR contains query (substring match)
3. Order by:
   - Prefix matches first, substring matches second
   - `created_at DESC` (newest first within each category)
   - Limit to `limit` results (default 20)
4. Return list of Account objects (or DTOs with id, name, account_type, account_subtype).

**Example queries:**
- User types "Cash" → returns Accounts where normalized_name starts with "cash"
- User types "Bank" → returns Accounts where normalized_name starts with "bank"
- User types "Loan" → returns existing Loan accounts (if any)

#### 3.1.2 `get_suggested_accounts(user_id: int, query: str, limit: int = 10) -> List[Account]`
**Purpose:** Combine existing account search + ML suggestions (if available).

**Logic:**
1. Call `search_accounts(user_id, query, limit=limit - 2)` to get existing accounts.
2. If ML service is enabled and query length > 2:
   - Call `ml_ranker.suggest_accounts(query, existing_account_names)` (domain's ML adapter).
   - This returns ranked suggestions (e.g., "probably a Bank account" based on description).
3. Merge and deduplicate results; return top `limit` items.
4. Each result includes: `{ id, name, account_type, account_subtype, is_existing: bool }`

**Note:** ML suggestions are abstracted behind the service layer. If ML fails, gracefully fall back to exact search.

#### 3.1.3 `get_account_subtypes(account_type: str) -> List[str]`
**Purpose:** Return valid subtypes for a given account_type.

**Logic:**
- Hardcoded map (or DB lookup, but likely hardcoded for now):
  - `asset` → ['cash', 'bank', 'investment', 'property', 'other']
  - `liability` → ['loan', 'credit_card', 'payable', 'other']
  - `equity` → ['contributed', 'retained_earnings', 'other']
  - `income` → ['salary', 'investment', 'business', 'other']
  - `expense` → ['groceries', 'utilities', 'rent', 'transportation', 'entertainment', 'other']

**Rationale:** Frontend uses this to populate subtype dropdown. Users can always pick "other" if unsure.

### 3.2 Account Creation Service

#### 3.2.1 `create_account_inline(user_id: int, name: str, account_type: str, account_subtype: str | None = None) -> Account`
**Purpose:** Create a new account with minimal user input.

**Logic:**
1. Validate inputs:
   - `name` is non-empty, <= 255 chars.
   - `account_type` is one of: 'asset', 'liability', 'equity', 'income', 'expense'.
   - `account_subtype` is in the allowed list for `account_type` (or None).
2. Normalize the account name (lowercase, trim, deduplicate whitespace).
3. Check for duplicates:
   - Query for existing accounts where `user_id == user_id`, `normalized_name == normalized`, `is_active == true`.
   - If found, return existing account (idempotent behavior).
4. Create new Account:
   - Set `user_id`, `name`, `account_type`, `account_subtype`, `normalized_name`, `is_active=true`.
   - Set `category_id = NULL` (or derive from account_type if a "default" AccountCategory exists).
5. Commit to DB.
6. **Emit event:** `finance.account.created` with payload:
   ```json
   {
     "account_id": <id>,
     "user_id": <user_id>,
     "name": <name>,
     "account_type": <account_type>,
     "account_subtype": <account_subtype>,
     "created_at": <datetime>
   }
   ```
7. Return the created Account object.

**Validation & Errors:**
- Raise `ValueError("invalid_account_type")` if account_type not in allowed list.
- Raise `ValueError("invalid_account_subtype")` if subtype not in list for that type.
- Raise `ValueError("invalid_name")` if name is empty or too long.

### 3.3 Journal Entry Service Updates

#### 3.3.1 `post_journal_entry()` (existing, no changes required)
- Already validates double-entry constraints (debits == credits).
- Already emits `finance.journal.posted` event.
- **No changes needed** for this feature, but the new inline account creation must happen *before* journal entry posting (in the frontend/controller flow).

#### 3.3.2 `validate_journal_lines(lines: List[dict]) -> Tuple[bool, str | None]`
**Purpose:** Validate journal entry lines (called before posting).

**Logic:**
1. Check that each line has a valid `account_id` (FK to finance_account, user_id-scoped).
2. Check that accounts are all active (`is_active == true`).
3. Check that total debits == total credits (balance constraint).
4. Return `(True, None)` if valid; `(False, error_message)` if invalid.

**Errors to check:**
- `account_not_found` (or `inactive_account`) if account doesn't exist or is inactive.
- `unbalanced_entry` if debits != credits.

---

## 4. API / Controller Contracts

### 4.1 Account Search / Typeahead Endpoint

**Route:** `GET /finance/accounts/search`

**Query Parameters:**
```
q: str (required)      # Search query (e.g., "cash", "bank", "salary")
limit: int (optional)  # Max results to return (default: 20)
include_ml: bool (optional)  # Whether to include ML suggestions (default: true)
```

**Response (200 OK):**
```json
{
  "ok": true,
  "results": [
    {
      "id": 1,
      "name": "Cash",
      "account_type": "asset",
      "account_subtype": "cash",
      "is_existing": true
    },
    {
      "id": 2,
      "name": "Checking Account",
      "account_type": "asset",
      "account_subtype": "bank",
      "is_existing": true
    }
  ]
}
```

**Error Response (400 Bad Request):**
```json
{
  "ok": false,
  "error": "invalid_query"
}
```

**Controller Implementation Notes:**
- Rate-limit to 240/minute (light-weight read operation).
- Require `@jwt_required()` (user context).
- No CSRF protection needed (GET request).
- Call `get_suggested_accounts(user_id, query, limit)` from service.

---

### 4.2 Create Account Inline Endpoint

**Route:** `POST /finance/accounts/inline`

**Request Body:**
```json
{
  "name": "My Savings Account",
  "account_type": "asset",
  "account_subtype": "bank"
}
```

**Response (201 Created):**
```json
{
  "ok": true,
  "account": {
    "id": 42,
    "name": "My Savings Account",
    "account_type": "asset",
    "account_subtype": "bank",
    "created_at": "2025-12-06T10:30:00Z"
  }
}
```

**Error Response (400 Bad Request):**
```json
{
  "ok": false,
  "error": "invalid_account_type"
}
```

**Error Response (409 Conflict - account exists):**
```json
{
  "ok": true,
  "account": { ... }  # Return existing account (idempotent)
}
```

**Controller Implementation Notes:**
- Require `@jwt_required()` + `@csrf_protected` + `@require_roles({"finance:write"})`.
- Rate-limit to 120/minute (write operation).
- Validate request using Pydantic schema `AccountInlineCreate`:
  ```python
  class AccountInlineCreate(BaseModel):
      name: str = Field(min_length=1, max_length=255)
      account_type: Literal['asset', 'liability', 'equity', 'income', 'expense']
      account_subtype: Optional[str] = Field(default=None, max_length=64)
  ```
- Call `create_account_inline(user_id, name, account_type, account_subtype)` from service.
- On success, return 201 with account data.
- On error, return 400 with error code (e.g., `invalid_account_type`).

---

### 4.3 Get Account Subtypes Endpoint

**Route:** `GET /finance/accounts/subtypes/<account_type>`

**Path Parameters:**
```
account_type: str  # One of: asset, liability, equity, income, expense
```

**Response (200 OK):**
```json
{
  "ok": true,
  "account_type": "asset",
  "subtypes": ["cash", "bank", "investment", "property", "other"]
}
```

**Error Response (400 Bad Request):**
```json
{
  "ok": false,
  "error": "invalid_account_type"
}
```

**Controller Implementation Notes:**
- No authentication required (public endpoint, hardcoded data).
- Can cache this response indefinitely (no user context).
- Call `get_account_subtypes(account_type)` from service.

---

### 4.4 Journal Entry Creation Endpoint (Existing, No Changes)

**Route:** `POST /finance/journal/entries`

**Request Body (unchanged):**
```json
{
  "description": "Deposited paycheck",
  "lines": [
    { "account_id": 1, "dc": "D", "amount": 5000, "memo": "Salary deposit" },
    { "account_id": 2, "dc": "C", "amount": 5000, "memo": "Salary deposit" }
  ]
}
```

**Response (200 OK) (unchanged):**
```json
{
  "ok": true,
  "entry_id": 123,
  "total_debit": 5000.00,
  "total_credit": 5000.00
}
```

**Note:** The frontend will now call the inline account creation endpoint *before* posting the journal entry, so the `account_id` references in the journal entry request will always exist.

---

### 4.5 New Pydantic Schemas (in `lifeos/domains/finance/schemas/finance_schemas.py`)

```python
class AccountSearchQuery(BaseModel):
    q: str = Field(min_length=1, max_length=100)
    limit: int = Field(default=20, ge=1, le=100)
    include_ml: bool = Field(default=True)

class AccountInlineCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    account_type: Literal['asset', 'liability', 'equity', 'income', 'expense']
    account_subtype: Optional[str] = Field(default=None, max_length=64)

class AccountResponse(BaseModel):
    id: int
    name: str
    account_type: str
    account_subtype: Optional[str]
    is_active: bool
    created_at: datetime
    is_existing: bool = True  # For search results
    
    model_config = ConfigDict(from_attributes=True)

class AccountSubtypesResponse(BaseModel):
    account_type: str
    subtypes: List[str]
```

---

## 5. Events & Integrations

### 5.1 Event Catalog Updates

**Add to** `lifeos/domains/finance/events.py`:

```python
FINANCE_ACCOUNT_CREATED = "finance.account.created"

EVENT_CATALOG = {
    # ... existing entries ...
    FINANCE_ACCOUNT_CREATED: {
        "version": "v1",
        "payload": {
            "account_id": "int",
            "user_id": "int",
            "name": "str",
            "account_type": "str",  # asset, liability, equity, income, expense
            "account_subtype": "str?",
            "created_at": "datetime",
        },
    },
}
```

### 5.2 Event Emission

- **When:** `create_account_inline()` completes successfully (after commit to DB).
- **Payload:** See above.
- **How:** Use `lifeos.platform.outbox.enqueue()` to emit the event to the outbox (for durability + async delivery).
- **Subscribers (future):** Insights engine may listen to account creation to trigger onboarding flows, or export notifications.

### 5.3 Integration with Insights Engine

**Out of scope for this spec**, but note:
- Insights rules may eventually subscribe to `finance.account.created` to emit signals (e.g., "New asset account created").
- Trial balance insights may listen to `finance.journal.posted` to compute aggregate balances.
- ML feedback loop: if a user corrects an ML-suggested account, emit `finance.ml.feedback` (already in catalog).

---

## 6. Migration & Backwards Compatibility

### 6.1 Existing Data

**Current state:** Existing LifeOS deployments may have Accounts linked to AccountCategory via `category_id`.

**Migration strategy:**
1. **Add new columns** (account_type, account_subtype, normalized_name, created_at) with sensible defaults.
2. **Backfill existing accounts:**
   - If account has a category_id, map it to account_type (e.g., category.code == 'ASSET' → account_type = 'asset').
   - Normalize the account name.
   - Set created_at to now (or a past date if available).
3. **Keep category_id:** Don't drop it (for now). It remains a foreign key but is no longer used by new code.
4. **Document deprecation:** In schema comments, note that `category_id` is deprecated; new code should use `account_type` + `account_subtype`.

### 6.2 Journal Entry Posting

- **No changes** to existing journal entry logic.
- The new inline account creation is a *prerequisite* for journal entry posting in the frontend UI.
- Existing API consumers (if any) continue to work as-is, but should migrate to using the inline creation endpoint.

### 6.3 Trial Balance Computation

- **Current logic:** Group by AccountCategory (or custom folders).
- **New logic:** Group by `account_type`, then optionally by `account_subtype`.
- **Update** `trial_balance_service.py` to read `account.account_type` instead of (or in addition to) `account.category`.
- **Result:** Trial balance should show cleaner grouping without requiring users to set up folders first.

### 6.4 Example Migration Scenario

**Before:**
- User creates "My Savings" account.
- It appears as "Unassigned".
- User must navigate to account manager, create "Bank Accounts" folder, assign account to folder, then set folder to "Assets".
- Only then does trial balance show "My Savings" under Assets.

**After:**
- User opens journal entry form.
- Types "My Savings" account name; no matches found.
- Clicks "+ Create new account".
- Fills minimal form: account_type = "asset", account_subtype = "bank", confirm.
- Account created instantly; journal entry form refreshes with account selected.
- User posts journal entry.
- Trial balance immediately shows "My Savings" under Assets → Bank.

---

## 7. Non-Goals / Explicit Exclusions

### 7.1 What We Are NOT Doing

1. **Folder/Hierarchy Management:** No folder creation, folder assignment, or hierarchy building in this phase.
   - Users don't set up "Cash", "Bank", "Debt" folders as prerequisites.
   - Subtypes provide light categorization; deeper structures come later.

2. **Account Manager UI:** No visual "account manager" page yet.
   - Users manage accounts implicitly via the journal.
   - A Chart of Accounts page (view only, then editable) is post-v1.

3. **Custom Account Types:** Only the 5 core types (Asset/Liability/Equity/Income/Expense) in this phase.
   - These map directly to accounting standards.
   - Custom types and roll-ups come later.

4. **Advanced Reconciliation:** No reconciliation UI or multi-account matching.
   - Journal entries are assumed correct; users reconcile manually (for now).

5. **Bulk Import + Account Mapping:** CSV import (if it exists) doesn't yet support account mapping.
   - If users import transactions, they must map accounts inline or in a separate step (post-v1).

6. **Account Deletion:** Accounts are soft-deleted (is_active flag) only.
   - No hard deletion to preserve journal entry history.

---

## 8. Implementation Notes & Constraints

### 8.1 LifeOS Architecture Rules (from lifeos_architecture.md)

**Adhere strictly to:**

1. **Domain Boundaries:**
   - All Finance code goes in `lifeos/domains/finance/`.
   - Models in `models/`, services in `services/`, controllers in `controllers/`, schemas in `schemas/`.
   - No cross-domain imports except for core models (User, UserPreference).

2. **Layering:**
   - **Controllers:** HTTP validation, authz, rate limiting. Delegate to services.
   - **Services:** Business logic, invariants, event emission. Call models + other services.
   - **Models:** SQLAlchemy only; no business logic. Persistence-focused.
   - **Schemas:** Pydantic DTOs for request/response validation.

3. **Migrations:**
   - Single Alembic home: `lifeos/migrations/`.
   - Migrations are **additive-first**; no destructive changes without two-phase strategy.
   - Migration file name: `<timestamp>_finance_<action>.py` (e.g., `20251206_finance_account_type_classification.py`).
   - Test migrations locally before committing.

4. **Events:**
   - Emit from services (not controllers) after successful DB commit.
   - Use `lifeos.platform.outbox.enqueue()` for durability.
   - Define event type in `lifeos/domains/finance/events.py` catalog.
   - Payload is JSON-serializable.

5. **Naming Conventions:**
   - Events: `domain.resource.action[.variant]` (lowercase, dot-separated).
     - Good: `finance.account.created`, `finance.journal.posted`.
     - Bad: `account_created`, `AccountCreated`, `finance.Account.Created`.
   - Methods: Snake case (`create_account_inline`).
   - Classes: PascalCase (`AccountInlineCreate`).
   - Tables: Prefix with domain (`finance_account`); underscores between words.

6. **Database Indexes:**
   - Always index `user_id` (multi-tenant guarantee, even though LifeOS is single-tenant per deployment).
   - Index query dimensions: `created_at`, `is_active`, `account_type`.
   - Composite indexes: `(user_id, created_at)`, `(user_id, account_type)` for common queries.

### 8.2 Testing

**Expectations (covered in** `lifeos/tests/` **by the QA team, but you should write unit tests for services):**

1. **Service unit tests** (`test_finance_account_creation.py`, `test_finance_account_search.py`):
   - Test `search_accounts()` with various queries (prefix, substring, empty).
   - Test `create_account_inline()` with valid/invalid inputs.
   - Test idempotency (creating same account twice returns same result).
   - Test event emission (verify outbox entry created).

2. **Controller integration tests** (`test_finance_accounts_api.py`):
   - Test GET `/finance/accounts/search` with various queries.
   - Test POST `/finance/accounts/inline` with valid/invalid payloads.
   - Test auth/rate limiting.

3. **Migration tests** (`test_finance_migrations.py`):
   - Verify migration applies cleanly to empty DB.
   - Verify backfill logic (mapping old category_id to account_type).
   - Test idempotency (run migration twice without error).

### 8.3 Error Handling

**Use consistent error codes:**
- `invalid_account_type`: account_type not in allowed list.
- `invalid_account_subtype`: account_subtype not in list for that type.
- `invalid_name`: account name empty, too long, or invalid.
- `invalid_query`: search query empty or too long.
- `account_not_found`: account_id doesn't exist or is inactive.
- `unbalanced_entry`: journal entry debits != credits.
- `validation_error`: generic validation failure (see details in response).

**All errors should return appropriate HTTP status codes:**
- 400 Bad Request: Validation errors, invalid input.
- 404 Not Found: Account/entry doesn't exist.
- 409 Conflict: Account already exists (but we return 200 with existing account for idempotency).
- 429 Too Many Requests: Rate limit exceeded.
- 500 Internal Server Error: Unhandled exceptions (log and return generic error).

### 8.4 Performance & Scalability

**Considerations:**
- **Account search:** Normalize query + index on `normalized_name` for fast prefix/substring matching.
  - Expected: < 100ms for 10 results, even with 10k+ accounts per user.
- **ML suggestions:** Abstract behind service layer; disable if slow or fail gracefully.
  - Expected: Typeahead feels responsive (< 200ms round-trip including UI).
- **Journal entry posting:** No changes; existing batch insert for lines is efficient.
- **Trial balance:** May need optimization if 1000s of accounts. Use GROUP BY on account_type for aggregation.

### 8.5 Logging & Observability

**Log at service layer:**
- `create_account_inline()`: Log account creation (name, type, user_id).
- `search_accounts()`: Log queries (optional; can be verbose).
- Errors: Log validation failures, DB errors, ML failures with context.

**Events (in outbox):** Automatically persisted and trackable via outbox table + worker logs.

---

## 9. Deliverables Checklist

### Phase 1: Core Implementation
- [ ] Update `Account` model with account_type, account_subtype, normalized_name, created_at.
- [ ] Create Alembic migration for schema changes (additive + backfill).
- [ ] Implement `search_accounts()` service method.
- [ ] Implement `create_account_inline()` service method with event emission.
- [ ] Implement `get_account_subtypes()` service method.
- [ ] Create new controller methods for account search, creation, subtypes (in `accounting_api.py` or new file).
- [ ] Define new Pydantic schemas (AccountInlineCreate, AccountResponse, etc.).
- [ ] Add new events to event catalog (FINANCE_ACCOUNT_CREATED).
- [ ] Write unit tests for services.
- [ ] Write integration tests for controllers.

### Phase 2: Trial Balance Update (Optional but Recommended)
- [ ] Update `trial_balance_service.py` to group by account_type (in addition to or instead of category).
- [ ] Test trial balance with new inline-created accounts.

### Phase 3: Documentation
- [ ] Update this spec with any changes made during implementation.
- [ ] Add docstrings to new methods (follow existing style).
- [ ] Document the new workflow in the frontend spec.

---

## 10. Questions for Clarification

**Before implementation, resolve:**

1. **AccountCategory deprecation:** Should we hard-delete the `category_id` FK relationship now, keep it as legacy, or migrate fully?
   - **Recommendation:** Keep it for now (add nullable constraint), fully migrate in Phase 2.

2. **Hardcoded subtypes:** Should `get_account_subtypes()` return hardcoded values or be customizable per user?
   - **Recommendation:** Hardcoded for v1; user customization is post-v1.

3. **ML integration:** Should account search always include ML suggestions, or only if enabled?
   - **Recommendation:** Include by default; gracefully degrade if ML unavailable. Frontend can toggle via `include_ml` param.

4. **Trial balance grouping:** Should new accounts (created inline) appear immediately in trial balance, or require some action?
   - **Recommendation:** Immediately after journal entry posts. No additional action needed.

---

## 11. Timeline & Effort Estimate

**Assuming 1 backend engineer, 1 frontend engineer working in parallel:**

- **Backend Implementation:** 2-3 days
  - Day 1: Models + migrations + services
  - Day 2: Controllers + schemas + testing
  - Day 3: Integration + refinements
- **Frontend Implementation:** 2-3 days (parallel, after backend API spec locked)
  - Build typeahead UI + inline account creation form + journal entry form integration
- **QA + Refinement:** 1-2 days
  - Full integration testing, edge case handling, performance validation

**Total:** ~5-7 days of concurrent effort.

---

## Appendix: Example API Interaction Flow

```
1. User opens journal entry form.

2. In the account field, user types "sav" (searching for savings account).
   GET /finance/accounts/search?q=sav&limit=20
   → Response: [{ id: 1, name: "Savings", account_type: "asset", ... }, ...]

3. No exact match found; user types "+ Create new account".
   Frontend shows inline form: name="Savings", account_type=?, account_subtype=?

4. User fills form:
   - Name: "My Savings"
   - Account Type: "asset" (dropdown)
   - Account Subtype: "bank" (dropdown, populated from GET /finance/accounts/subtypes/asset)

5. Frontend submits:
   POST /finance/accounts/inline
   { "name": "My Savings", "account_type": "asset", "account_subtype": "bank" }
   → Response: { ok: true, account: { id: 42, name: "My Savings", ... } }

6. Frontend refreshes account field; now shows "My Savings" (id=42) as selected.

7. User continues journal entry form (other lines, etc.).

8. User submits journal entry:
   POST /finance/journal/entries
   {
     "description": "Deposit",
     "lines": [
       { "account_id": 42, "dc": "D", "amount": 1000, "memo": "Deposit to savings" },
       { "account_id": 2, "dc": "C", "amount": 1000, "memo": "From checking" }
     ]
   }
   → Response: { ok: true, entry_id: 123, total_debit: 1000, total_credit: 1000 }

9. Journal entry posted; event emitted to outbox.
   - finance.journal.posted (entry_id=123, ...)
   - finance.account.created was emitted when account created (step 5).

10. Trial balance updated; "My Savings" (asset → bank) shows with balance.
```

---

**End of specification. Ready for backend implementation.**
