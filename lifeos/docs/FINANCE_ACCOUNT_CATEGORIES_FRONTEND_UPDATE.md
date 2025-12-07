# Finance Account Categories - Frontend Update

**Date:** 2025-12-06  
**Status:** Complete  
**Backend Spec:** `FINANCE_ACCOUNT_CATEGORIES_AND_INLINE_ACCOUNTS_UPDATE.md`

---

## Overview

Frontend implementation for the new account categories feature, including category management UI, trial balance grouping by category, and enhanced inline account creation with category selection.

---

## New Files

### `lifeos/static/js/finance-account-categories.js`

New JavaScript module for account categories API integration.

**Public API (exposed as `window.lifeosAccountCategories`):**

| Function | Description |
|----------|-------------|
| `listCategories(options)` | List categories. Options: `{base_type, include_system}` |
| `createCategory(base_type, name, is_default)` | Create custom category |
| `listCategoriesGrouped(includeSystem)` | Get categories grouped by base_type |
| `listCategoriesCached(options)` | Cached version (1-minute TTL) |
| `clearCache()` | Clear the categories cache |
| `createCategoryAndClearCache(...)` | Create and auto-clear cache |

**Usage:**
```javascript
const { listCategories, createCategory } = window.lifeosAccountCategories;

// List all categories
const categories = await listCategories();

// Filter by type
const assetCategories = await listCategories({ base_type: 'asset' });

// Create custom category
const newCat = await createCategory('expense', 'Operating Expenses', false);
```

---

## Modified Files

### 1. `lifeos/templates/finance/trial_balance.html`

**Changes:**
- Added new **Category Rollups** card between main table and period totals
- Displays category-level aggregation from `categories` array in API response
- Filter dropdown by account type (asset/liability/equity/revenue/expense)
- "Uncategorized" displayed in italic for accounts with null `category_id`
- Sorted by type order, then category name

**New UI Elements:**
- `#tb-cat-filter` - Type filter select
- `#tb-cat-body` - Category rollups table body
- `#tb-cat-status` - Status display

### 2. `lifeos/templates/finance/accounts.html`

**Changes:**
- Complete redesign from basic table to full-featured dashboard
- Two-card layout with accounts list and categories management

**Accounts List Card:**
- Enhanced table columns: Name, Code, Type, Subtype, Category, Balance
- Client-side filter by account type
- Server-rendered with Jinja2 (existing pattern preserved)

**Categories Management Card:**
- Lists all categories (system + user) with type, default flag, system flag
- Create custom category form:
  - Account type dropdown
  - Category name input
  - "Set as default" checkbox
- Real-time refresh after creation

### 3. `lifeos/templates/components/journal_entry_form_v2.html`

**Changes:**
- Enhanced inline account creation modal with category selection
- Dynamic category dropdown populated based on selected account type
- Optional "create new category" text input
- Error display for creation failures

**Modal Flow:**
1. User selects account type (asset/liability/equity/income/expense)
2. Category dropdown populates with categories for that type
3. User can select existing category OR enter new category name
4. On submit, account created with category assignment

### 4. `lifeos/static/js/finance-account-search.js`

**Changes:**
- Extended `createAccountInline()` signature:

```javascript
// Before
createAccountInline(name, accountType, accountSubtype)

// After
createAccountInline(name, accountType, accountSubtype, categoryId, categoryNameNew)
```

- New parameters:
  - `categoryId` (number|null) - Existing category ID
  - `categoryNameNew` (string|null) - New category name to create inline
- Auto-clears categories cache when new category created

### 5. `lifeos/templates/layouts/base.html`

**Changes:**
- Added `finance-account-categories.js` to global script loading
- Updated module availability check to include the new module

```html
<script src="{{ url_for('static', filename='js/finance-account-categories.js') }}"></script>
```

---

## API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/finance/account-categories` | List categories |
| POST | `/api/finance/account-categories` | Create custom category |
| GET | `/api/finance/trial_balance` | Trial balance with `categories` rollups |
| POST | `/api/finance/accounts/inline` | Create account with category |

---

## UI/UX Notes

### Category Rollups Display
- Sorted by type order: asset → liability → equity → revenue → expense
- Then alphabetically by category name
- "Uncategorized" shown in italic gray for null category_id

### Inline Account Creation
- Category dropdown auto-populates when account type changes
- Shows "(default)" suffix for default categories
- Shows "[system]" suffix for system categories
- New category input clears the dropdown selection and vice versa

### Accounts Page
- Type filter is client-side only (uses `data-type` attribute)
- Categories table refreshes after successful creation
- Form clears after successful category creation

---

## Design Tokens

Consistent with existing LifeOS design:
- Primary: `#0b4f9c`
- Background: `#f7f8fa`
- Borders: `#e0e5ec`
- Text: `#1f2430`
- Muted: `#5b6470`
- Error: `#b3352f`
- Success: `#1d7a36`

---

## Testing Checklist

- [ ] Trial balance loads with category rollups
- [ ] Category filter works on trial balance
- [ ] Accounts page shows enhanced table
- [ ] Categories list loads on accounts page
- [ ] Create custom category works
- [ ] Inline account creation shows category dropdown
- [ ] Category dropdown populates per account type
- [ ] New category name creates category inline
- [ ] Auth sync works (login/logout clears data)
- [ ] Error states display correctly

---

## Dependencies

- `window.lifeosAuth` - Authentication headers
- `window.lifeosAccountSearch` - Account search/create
- `window.lifeosAccountSubtypes` - Subtype management

All modules loaded globally via `base.html`.
