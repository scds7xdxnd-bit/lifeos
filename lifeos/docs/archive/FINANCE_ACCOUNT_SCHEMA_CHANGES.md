# Finance Account Schema Changes

**Date:** 2025-12-06  
**Migration:** `20251206_finance_account_type_classification.py`  
**Status:** Additive (backwards compatible)

---

## Table: `finance_account`

### New Columns

#### 1. `account_type` (VARCHAR 16)
- **Default:** `'asset'`
- **Nullable:** NO
- **Indexed:** Yes (single column)
- **Composite Indexes:** `(user_id, account_type)`
- **Valid Values:** `'asset'`, `'liability'`, `'equity'`, `'income'`, `'expense'`
- **Purpose:** Primary classification for trial balance grouping (replaces folder hierarchy)
- **Migration:** Existing accounts mapped from `AccountCategory.code`:
  - `'ASSET'` → `'asset'`
  - `'LIABILITY'` → `'liability'`
  - `'EQUITY'` → `'equity'`
  - `'INCOME'` → `'income'`
  - `'EXPENSE'` → `'expense'`
  - Unknown → `'asset'` (safe default)

#### 2. `account_subtype` (VARCHAR 64)
- **Default:** NULL
- **Nullable:** Yes
- **Indexed:** No (single column)
- **Valid Values:** Depends on `account_type`:
  - **asset:** `'cash'`, `'bank'`, `'investment'`, `'property'`, `'other'`
  - **liability:** `'loan'`, `'credit_card'`, `'payable'`, `'other'`
  - **equity:** `'contributed'`, `'retained_earnings'`, `'other'`
  - **income:** `'salary'`, `'investment'`, `'business'`, `'rental'`, `'other'`
  - **expense:** `'groceries'`, `'utilities'`, `'rent'`, `'transportation'`, `'entertainment'`, `'other'`
- **Purpose:** Secondary classification for finer grouping (enables future enhancements like "Bank" vs "Cash" under Assets)
- **Usage:** Optional; users can select "other" if unsure

#### 3. `normalized_name` (VARCHAR 255)
- **Default:** Empty string (backfilled during migration)
- **Nullable:** NO
- **Indexed:** Yes (single column)
- **Composite Indexes:** `(user_id, normalized_name)`
- **Derivation:** `LOWER(TRIM(name))` with deduplicated whitespace
- **Purpose:** Fast typeahead search (prefix/substring matching)
- **Examples:**
  - "My Savings" → "my savings"
  - "CHECKING ACCOUNT" → "checking account"
  - "My   Savings" → "my savings" (whitespace normalized)
- **Duplicate Detection:** Same normalized_name + user_id = same account (idempotency)

#### 4. `created_at` (TIMESTAMP)
- **Default:** `NOW()` (server timestamp)
- **Nullable:** NO
- **Indexed:** No (single column)
- **Composite Indexes:** None (but useful for sorting)
- **Purpose:** Track account creation time (enables sorting "newest first" in search)
- **Migration:** Backfilled with `NOW()` for existing accounts

### New Indexes

#### 1. `ix_finance_account_type`
```sql
CREATE INDEX ix_finance_account_type ON finance_account(account_type);
```
- **Purpose:** Fast filtering by account type (for trial balance grouping)
- **Cardinality:** Low (5 distinct values: asset, liability, equity, income, expense)
- **Usage:** Trial balance queries, analytics

#### 2. `ix_finance_account_user_type`
```sql
CREATE INDEX ix_finance_account_user_type ON finance_account(user_id, account_type);
```
- **Purpose:** Fast lookup of accounts by user + type (most common query pattern)
- **Cardinality:** Medium (user_id × 5 types)
- **Usage:** Trial balance, account discovery, insights

#### 3. `ix_finance_account_normalized_name`
```sql
CREATE INDEX ix_finance_account_normalized_name ON finance_account(normalized_name);
```
- **Purpose:** Fast prefix/substring search on normalized names
- **Cardinality:** High (one entry per account name)
- **Usage:** Typeahead search across all users (rare; mostly user-scoped)

#### 4. `ix_finance_account_user_normalized_name`
```sql
CREATE INDEX ix_finance_account_user_normalized_name ON finance_account(user_id, normalized_name);
```
- **Purpose:** Fast typeahead search scoped to user (most common search pattern)
- **Cardinality:** Very high (unique per user)
- **Usage:** Account search endpoint, journal entry form

### Existing Columns (Unchanged)

| Column | Type | Notes |
|--------|------|-------|
| `id` | INT | Primary key |
| `user_id` | INT | Foreign key to `user` (scopes all queries) |
| `category_id` | INT | Foreign key to `finance_account_category` (deprecated but kept for backwards compat) |
| `name` | VARCHAR(255) | Display name (e.g., "My Savings") |
| `code` | VARCHAR(32) | Optional account code (e.g., "1000-CASH") |
| `description` | TEXT | Optional long description |
| `is_active` | BOOLEAN | Soft delete flag (default: true) |

---

## Query Patterns

### Pattern 1: Typeahead Search
```sql
-- Find accounts matching user query "sav"
SELECT * FROM finance_account
WHERE user_id = 1
  AND is_active = true
  AND (
    normalized_name LIKE 'sav%'     -- Prefix match (preferred)
    OR normalized_name LIKE '%sav%'  -- Substring match
  )
ORDER BY 
  CASE WHEN normalized_name LIKE 'sav%' THEN 0 ELSE 1 END,  -- Prefix first
  created_at DESC
LIMIT 20;
```
**Index used:** `ix_finance_account_user_normalized_name` (ideal)

### Pattern 2: Trial Balance by Type
```sql
-- Group accounts by type for trial balance
SELECT account_type, COUNT(*), SUM(debit), SUM(credit)
FROM finance_account acc
LEFT JOIN finance_journal_line jl ON jl.account_id = acc.id
WHERE acc.user_id = 1
  AND acc.is_active = true
GROUP BY acc.account_type;
```
**Index used:** `ix_finance_account_user_type`

### Pattern 3: Duplicate Detection
```sql
-- Check if account with same normalized name already exists
SELECT id FROM finance_account
WHERE user_id = 1
  AND normalized_name = 'my savings'
  AND is_active = true
LIMIT 1;
```
**Index used:** `ix_finance_account_user_normalized_name`

### Pattern 4: Subtype Filtering
```sql
-- Get all bank accounts
SELECT * FROM finance_account
WHERE user_id = 1
  AND account_type = 'asset'
  AND account_subtype = 'bank'
  AND is_active = true;
```
**Index used:** `ix_finance_account_user_type` (partial scan on type, then filter subtype)

---

## Data Migration Details

### Backfill Logic

During migration upgrade:

```sql
-- 1. Normalize all account names
UPDATE finance_account
SET normalized_name = LOWER(TRIM(name))
WHERE normalized_name = '';

-- 2. Map category to account_type
UPDATE finance_account
SET account_type = COALESCE(
  CASE 
    WHEN category_id IN (SELECT id FROM finance_account_category WHERE code IN ('ASSET', 'Assets')) THEN 'asset'
    WHEN category_id IN (SELECT id FROM finance_account_category WHERE code IN ('LIABILITY', 'Liabilities')) THEN 'liability'
    WHEN category_id IN (SELECT id FROM finance_account_category WHERE code IN ('EQUITY', 'Equity')) THEN 'equity'
    WHEN category_id IN (SELECT id FROM finance_account_category WHERE code IN ('INCOME', 'Income')) THEN 'income'
    WHEN category_id IN (SELECT id FROM finance_account_category WHERE code IN ('EXPENSE', 'Expenses')) THEN 'expense'
    ELSE 'asset'
  END,
  'asset'
)
WHERE account_type = 'asset';

-- 3. Set created_at to now for existing accounts (or preserve if already set)
UPDATE finance_account
SET created_at = COALESCE(created_at, NOW())
WHERE created_at IS NULL;
```

### Rollback Logic

During migration downgrade:

```sql
-- 1. Drop indexes
DROP INDEX ix_finance_account_user_normalized_name;
DROP INDEX ix_finance_account_normalized_name;
DROP INDEX ix_finance_account_user_type;
DROP INDEX ix_finance_account_type;

-- 2. Drop columns
ALTER TABLE finance_account
  DROP COLUMN created_at,
  DROP COLUMN normalized_name,
  DROP COLUMN account_subtype,
  DROP COLUMN account_type;
```

---

## Backwards Compatibility

✅ **Fully backwards compatible:**

1. **Existing foreign key constraints preserved:** `category_id` FK to `finance_account_category` remains
2. **No columns dropped:** All existing columns unchanged
3. **Defaults provided:** All new columns have defaults (no NULL for NOT NULL columns)
4. **Old code still works:** Existing queries on `category_id`, `name`, `code` continue to function
5. **Gradual migration:** Old code can coexist with new code during transition

### Migration Path

**Phase 1 (Current):** Deploy new code with migration
- Old: Accounts created via old endpoint still linked to `category_id`
- New: Accounts created via `/accounts/inline` use `account_type` + `account_subtype`
- Both work: Trial balance reads `account_type` (backfilled), old queries still work

**Phase 2 (Future):** Deprecate old endpoint
- Stop creating accounts via old endpoint
- Update trial balance to read only `account_type`, ignore `category_id`
- Optionally drop `category_id` in v2

---

## Query Performance

### Typeahead Search Performance

| Query Dimension | Cardinality | Index | Est. Time |
|-----------------|-------------|-------|-----------|
| Single user, prefix match | Low-medium | `ix_finance_account_user_normalized_name` | < 50ms |
| Single user, substring match | Low-medium | `ix_finance_account_user_normalized_name` | < 100ms |
| All users, prefix match | High | `ix_finance_account_normalized_name` | 50-200ms |
| Cross-user substring | Very high | None (table scan) | 500ms+ |

**Recommendation:** Always query with `user_id` filter (all LifeOS queries do this by default).

### Trial Balance Performance

| Query | Index | Cardinality | Est. Time |
|-------|-------|-------------|-----------|
| Group by account_type | `ix_finance_account_user_type` | 5 × user_accounts | < 100ms |
| Group by account_type + subtype | None (sub-table scan) | user_accounts | < 200ms |
| Filter by account_type | `ix_finance_account_type` | Low (5 values) | < 50ms |

**Note:** Journal line joins are the slow part, not account lookups.

---

## Storage Impact

### Disk Space

**New columns total:**
- `account_type`: 16 bytes per row (VARCHAR 16)
- `account_subtype`: 64 bytes per row (VARCHAR 64)
- `normalized_name`: 255 bytes per row (VARCHAR 255)
- `created_at`: 8 bytes per row (TIMESTAMP)
- **Total per row:** ~343 bytes

**Index overhead:**
- 4 new indexes × ~100 bytes per entry = ~400 bytes per account

**Estimate for 10,000 accounts:**
- Data: 10,000 × 343 bytes = 3.43 MB
- Indexes: 10,000 × 400 bytes = 4 MB
- **Total:** ~7 MB (negligible)

---

## Monitoring

### Recommended Alerts

1. **Search latency > 200ms**
   - Check index statistics: `ANALYZE finance_account;`
   - Rebuild indexes if needed: `REINDEX INDEX ix_finance_account_user_normalized_name;`

2. **Account creation failures**
   - Monitor app logs for `invalid_name`, `invalid_account_type` errors
   - Check outbox queue depth (should stay < 100 pending messages)

3. **Duplicate account creation**
   - Monitor for same `normalized_name` + `user_id` + `is_active=true`
   - Idempotency should prevent duplicates, but monitor as a canary

---

## Example Schema After Migration

```sql
-- Before migration
CREATE TABLE finance_account (
  id INT PRIMARY KEY,
  user_id INT NOT NULL,
  category_id INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  code VARCHAR(32),
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (category_id) REFERENCES finance_account_category(id),
  INDEX (user_id),
  INDEX (code)
);

-- After migration
CREATE TABLE finance_account (
  id INT PRIMARY KEY,
  user_id INT NOT NULL,
  category_id INT NOT NULL,
  name VARCHAR(255) NOT NULL,
  code VARCHAR(32),
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  
  -- NEW
  account_type VARCHAR(16) NOT NULL DEFAULT 'asset',
  account_subtype VARCHAR(64),
  normalized_name VARCHAR(255) NOT NULL DEFAULT '',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  
  FOREIGN KEY (user_id) REFERENCES user(id),
  FOREIGN KEY (category_id) REFERENCES finance_account_category(id),
  INDEX (user_id),
  INDEX (code),
  INDEX (account_type),
  INDEX (normalized_name),
  INDEX ix_finance_account_user_type (user_id, account_type),
  INDEX ix_finance_account_user_normalized_name (user_id, normalized_name)
);
```

