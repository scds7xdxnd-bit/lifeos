# LifeOS Finance Frontend: Account Search & Inline Creation Integration Guide

**Date:** 2025-12-18  
**Status:** ✅ Complete  
**Target Users:** Frontend developers, UI designers

---

## Overview

This guide documents the new frontend components for the Finance domain that enable **journal-first, inline account creation** workflows. Users can now:

1. **Search existing accounts** via typeahead (live as-you-type)
2. **Create accounts inline** with minimal friction (3 fields: name, type, subtype)
3. **Leverage ML suggestions** for account recommendations (optional, graceful fallback)

---

## Architecture

### New Frontend Assets

#### JavaScript Modules (in `/static/js/`)

1. **`finance-account-search.js`** (Global: `lifeosAccountSearch`)
   - Provides: `searchAccounts()`, `createAccountInline()`, `highlightMatch()`, `createDebouncedSearch()`
   - Implements API integration for GET/POST account endpoints
   - Handles debouncing, timeouts, error handling

2. **`finance-account-subtypes.js`** (Global: `lifeosAccountSubtypes`)
   - Provides: `getSubtypes()`, `getAllSubtypes()`, `getCachedSubtypes()`, `clearCache()`
   - Caches subtype responses to minimize API calls
   - Supports all 5 account types: asset, liability, equity, income, expense

#### Jinja Templates (in `/templates/components/`)

1. **`account_search_dropdown.html`**
   - Standalone account search component with inline creation support
   - Self-initializes via `<script>` tag
   - Emits selection via callback
   - Can be included multiple times on same page

2. **`journal_entry_form_v2.html`** (NEW - Recommended)
   - Modern journal entry form using account search dropdowns
   - Replaces old `journal_entry_form.html` (which uses simple selects)
   - Per-line account search with automatic account discovery
   - Inline account creation from search results

#### CSS (in `/static/css/main.css`)

- `.account-search-wrapper`, `.account-search-input`, `.account-search-dropdown`
- `.account-search-result`, `.account-search-create-new`
- `select` (universal styling for account type/subtype dropdowns)

---

## Usage Patterns

### Pattern 1: Use v2 Journal Form (Recommended)

**File:** `/templates/finance/journal.html`

```html
{% extends "layouts/base.html" %}

{% block content %}
<div class="container" style="max-width: 1100px; margin: 0 auto; display: grid; gap: 1rem; padding: 1rem 0;">
  <!-- New form component with account search -->
  {% include "components/journal_entry_form_v2.html" %}

  <div class="card">
    <h3 style="margin:0;">Recent entries</h3>
    <div id="journal-list" style="display:grid; gap:0.5rem; margin-top:0.5rem;"></div>
  </div>
</div>

<script>
  // Refresh entries when a new one is posted
  window.addEventListener('journal:entry-posted', async () => {
    const res = await fetch('/api/finance/journal', { headers: lifeosAuth.authHeaders() });
    const data = await res.json();
    // Update UI...
  });
</script>
{% endblock %}
```

**What This Gives You:**
- ✅ Typeahead account search on each journal line
- ✅ Inline account creation (+ Create new account)
- ✅ Auto-balancing display (Debit/Credit/Diff)
- ✅ Full error handling & validation

---

### Pattern 2: Use Standalone Account Search Dropdown

For forms that aren't journal entries (e.g., transaction filters, account assignment):

```html
{% set search_id = 'filter-account' %}
{% set placeholder = 'Filter by account...' %}
{% include "components/account_search_dropdown.html" %}

<script>
  // Initialize with callback
  const dropdown = new AccountSearchDropdown('filter-account', (account) => {
    console.log('Selected account:', account);
    // Use account.id in your form/query
  });
</script>
```

---

### Pattern 3: Use JavaScript Modules Directly

For custom UI or integration with framework components:

```javascript
// Search accounts
const results = await lifeosAccountSearch.searchAccounts('savings', 20, true);
// results = [
//   { id: 42, name: "Savings Account", account_type: "asset", account_subtype: "bank", ... },
//   { id: 99, name: "High Yield Savings", account_type: "asset", account_subtype: "bank", ... },
//   { ... }
// ]

// Get formatted display
const display = lifeosAccountSearch.formatResultDisplay(results[0]);
// "Savings Account [asset] (bank)"

// Highlight matching part
const highlighted = lifeosAccountSearch.highlightMatch(display, 'sav');
// "Savings Account [asset] (bank)"
//  ^^^^^^ (would be wrapped in <mark> tag)

// Create debounced search
const search = lifeosAccountSearch.createDebouncedSearch((results) => {
  console.log('Search results:', results);
}, 300); // 300ms debounce

// Use in input listener
input.addEventListener('input', (e) => search(e.target.value));

// Create account inline
const newAccount = await lifeosAccountSearch.createAccountInline(
  'My Savings',
  'asset',
  'bank'
);
// newAccount = { id: 123, name: "My Savings", account_type: "asset", account_subtype: "bank", created_at: "2025-12-18T..." }

// Get account subtypes
const subtypes = await lifeosAccountSubtypes.getSubtypes('asset');
// ['cash', 'bank', 'investment', 'property', 'other']

// Cache subtypes for all types
const allSubtypes = await lifeosAccountSubtypes.getAllSubtypes();
// { asset: [...], liability: [...], equity: [...], income: [...], expense: [...] }

// Check cached subtypes (no fetch)
const cached = lifeosAccountSubtypes.getCachedSubtypes('asset');
// null if not loaded, or array if cached
```

---

## API Integration Reference

### Backend Endpoints

All endpoints require JWT authentication (except subtypes).

#### 1. GET `/finance/accounts/search`

**Purpose:** Typeahead search for existing accounts

**Query Parameters:**
- `q` (string, required): Search query (1-100 chars)
- `limit` (integer, default 20): Max results (1-100)
- `include_ml` (boolean, default true): Include ML suggestions

**Response (200 OK):**
```json
{
  "ok": true,
  "results": [
    {
      "id": 1,
      "name": "Savings Account",
      "account_type": "asset",
      "account_subtype": "bank",
      "is_ml_suggestion": false
    },
    {
      "id": 2,
      "name": "High Yield Savings",
      "account_type": "asset",
      "account_subtype": "bank",
      "is_ml_suggestion": true
    }
  ]
}
```

**Rate Limit:** 240 requests/minute

---

#### 2. POST `/finance/accounts/inline`

**Purpose:** Create a new account with minimal input

**Body:**
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
    "created_at": "2025-12-18T10:30:00Z"
  }
}
```

**Idempotency:** Same normalized name (lowercase, trimmed) + user = same account returned

**Rate Limit:** 120 requests/minute

**Error Responses:**
- 400 `invalid_name`: Name is empty or > 255 chars
- 400 `invalid_account_type`: Type not in allowed list
- 400 `invalid_account_subtype`: Subtype not valid for type
- 401: Missing JWT
- 403: Missing CSRF or insufficient permissions
- 429: Rate limit exceeded

---

#### 3. GET `/finance/accounts/subtypes/<account_type>`

**Purpose:** Get valid subtypes for an account type

**Path Parameters:**
- `account_type` (string): One of: `asset`, `liability`, `equity`, `income`, `expense`

**Response (200 OK):**
```json
{
  "ok": true,
  "subtypes": ["cash", "bank", "investment", "property", "other"]
}
```

**No Authentication Required** ✅ (public data)

**Rate Limit:** 600 requests/minute (cached responses are cheap)

---

## Component Details

### account_search_dropdown.html

**Auto-Init Variables:**
- `search_id`: Unique ID prefix for all elements (required)
- `placeholder`: Input placeholder text (default: "Search accounts...")

**Class: AccountSearchDropdown**

Methods:
- `constructor(componentId, onSelect)` - Initialize
- `showDropdown()` - Show dropdown menu
- `hideDropdown()` - Hide dropdown menu
- `setLoading(isLoading)` - Show/hide loading state
- `renderResults(results)` - Populate dropdown with results
- `selectResult(result)` - User selected an account
- `showCreateForm()` - Display inline creation form
- `updateSubtypesDropdown(accountType)` - Populate subtype options
- `submitCreateForm()` - Submit new account creation

**Events:**
- Component dispatches nothing; uses `onSelect` callback

**Form Fields:**
```html
<input id="{search_id}-input" type="text" ... />
<div id="{search_id}-dropdown" style="display: none;">
  <div id="{search_id}-loading">Searching...</div>
  <div id="{search_id}-results"><!-- Account results --></div>
  <div id="{search_id}-create-form">
    <input id="{search_id}-create-name" ... />
    <select id="{search_id}-create-type"> ... </select>
    <select id="{search_id}-create-subtype"> ... </select>
    <button id="{search_id}-create-submit">Create</button>
  </div>
</div>
```

---

### journal_entry_form_v2.html

**Auto-Init Variables:**
- `component_id`: Unique ID prefix (default: "journal")

**Features:**
- Minimum 2 lines (auto-initialized as Debit/Credit)
- Per-line account search with debouncing
- Auto-balancing (live Debit/Credit/Diff display)
- Inline account creation support
- Validation: account required, amount > 0, balanced entry
- Event: `journal:entry-posted` custom event on success

**Line Structure:**
```javascript
{
  account_id: <int>,      // Selected account ID
  account_name: <string>, // Display name
  dc: 'D' | 'C',         // Debit or Credit
  amount: <number>,       // Amount (>0)
  memo: <string>          // Optional memo
}
```

---

## Styling Customization

### CSS Classes

```css
.account-search-wrapper     /* Container (position: relative) */
.account-search-input       /* Search input field */
.account-search-dropdown    /* Dropdown menu container */
.account-search-result      /* Individual result item */
.account-search-create-new  /* "Create new account" option */
select                      /* All select dropdowns */
```

### Theme Customization

All components use LifeOS design tokens:
- Primary color: `#0b4f9c` (blue)
- Background: `#f7f8fa` (light gray)
- Border: `#e0e5ec` (medium gray)
- Text: `#1f2430` (dark)
- Success: `#1d7a36` (green)
- Error: `#b3352f` (red)

Modify in `static/css/main.css` by changing color hex values.

---

## Error Handling

### Network Errors
- Timeouts (5 seconds): Gracefully fallback to empty results
- 401/403: Log auth error, show "Log in" message
- 429: Show "Rate limit exceeded" message
- Other: Log to console, show generic error

### Validation Errors
- Empty query: Don't search
- Empty account name: Show "Account name required"
- Invalid type: Show "Invalid type" (dropdown prevents this)
- Invalid subtype: Show "Invalid subtype"

### UX Feedback
- Loading state: "Searching..." spinner
- No results: "No accounts found"
- Success: Account added to form, display name shown
- Error: Red status message with details

---

## Testing Checklist

### Unit Tests (for developers)
- [ ] Search with prefix query ("sav" → "Savings Account")
- [ ] Search with substring query ("vings" → "Savings Account")
- [ ] Search with no results
- [ ] Create account with all fields
- [ ] Create account with minimal fields
- [ ] Idempotent creation (duplicate name)
- [ ] Subtype dropdown population
- [ ] Subtype filtering (asset → cash, bank, etc.)

### Integration Tests (for QA)
- [ ] Login and open journal form
- [ ] Type in account search field
- [ ] Click existing account from dropdown
- [ ] See account populated in journal line
- [ ] Click "+ Create new account"
- [ ] Fill account name, type, subtype
- [ ] Click "Create" button
- [ ] Account created and populated in line
- [ ] Post balanced journal entry
- [ ] Verify entry appears in recent entries list

### Browser Tests (for QA)
- [ ] Works in Chrome/Firefox/Safari
- [ ] Mobile: Typeahead works on small screens
- [ ] Mobile: Dropdown scrolls without page scroll
- [ ] Keyboard: Tab/Enter navigation works
- [ ] Keyboard: Escape closes dropdown
- [ ] Accessibility: Screen reader announcements

---

## Troubleshooting

### Issue: Typeahead not showing results

**Cause:** Not authenticated or API endpoint not responding

**Fix:**
1. Check browser console for errors
2. Verify JWT token: `lifeosAuth.getTokens()`
3. Check network tab for `/finance/accounts/search` request
4. Verify backend is running and returning 200 status

### Issue: "+ Create new account" not appearing

**Cause:** Results shown but no create option visible

**Fix:**
1. This is expected when exactly 0 results match
2. Type more characters to see the create option
3. Or clear field and it should appear

### Issue: Account creation fails with "Invalid subtype"

**Cause:** Subtype not valid for selected account_type

**Fix:**
1. Verify subtype is in the dropdown options
2. Call `lifeosAccountSubtypes.getSubtypes(type)` to check valid values
3. Use `account_subtype: null` instead if unsure

### Issue: Form not disabling when not logged in

**Cause:** Auth check not running

**Fix:**
1. Ensure `lifeosAuth.getTokens()` returns valid tokens
2. Check browser localStorage for `lifeos_tokens` key
3. Verify role includes `finance:write`

---

## Performance Considerations

### Caching
- Subtypes are cached in memory (call `clearCache()` to reset)
- Search results are NOT cached (fresh on each query)
- ML suggestions are rate-limited (240/min)

### Debouncing
- Default: 300ms between search requests
- Can be customized: `createDebouncedSearch(callback, 500)` for 500ms
- Prevents excessive API calls while typing

### Network
- Timeout: 5 seconds per request
- Aborts pending requests when new query arrives
- Graceful degradation (no results vs error)

### Browser
- Dropdown max-height: 350px (scrollable)
- Max results: 20 (configurable per call)
- Account name truncation: None (full display name shown)

---

## Migration Guide

### From Old Form to V2

**Old (simple select dropdowns):**
```html
{% include "components/journal_entry_form.html" %}
```

**New (typeahead search):**
```html
{% include "components/journal_entry_form_v2.html" %}
```

**Differences:**
- ✅ Old form: Static dropdown of pre-loaded accounts
- ✅ New form: Dynamic typeahead search + inline creation
- ✅ Old form: Must create accounts separately
- ✅ New form: Create while journalizing

**Backward Compatibility:**
- Old form still exists and works
- New form is a drop-in replacement
- No API changes on backend

---

## Future Enhancements

### Planned
- [ ] ML account suggestions (ranker integration)
- [ ] Recently used accounts (history)
- [ ] Favorite accounts (star/pin)
- [ ] Account favorites bar above search
- [ ] Keyboard shortcuts (e.g., / to focus search)

### Out of Scope (v1)
- Multi-select (batch journal entries)
- Account templates (predefined charts)
- Split transactions (native UI)
- Recurring entries (separate feature)

---

## Developer Notes

### File Locations
```
lifeos/
├── templates/
│   ├── layouts/base.html                          # Script includes
│   ├── components/
│   │   ├── account_search_dropdown.html           # NEW
│   │   ├── journal_entry_form.html                # OLD (kept for compat)
│   │   └── journal_entry_form_v2.html             # NEW
│   └── finance/
│       └── journal.html                           # Update to use v2
├── static/
│   ├── css/
│   │   └── main.css                               # Added account search styles
│   └── js/
│       ├── finance-account-search.js              # NEW
│       └── finance-account-subtypes.js            # NEW
└── domains/
    └── finance/
        └── controllers/                           # Backend endpoints (already done)
```

### Key APIs to Remember
- `lifeosAuth.authHeaders()` - Get JWT/CSRF headers
- `lifeosAuth.getTokens()` - Check logged-in state
- `lifeosAccountSearch.searchAccounts(query, limit, includeMl)`
- `lifeosAccountSearch.createAccountInline(name, type, subtype)`
- `lifeosAccountSubtypes.getSubtypes(type)` - Returns Promise
- `window.dispatchEvent(new CustomEvent('journal:entry-posted', ...))` - Emit event

### Dependencies
- None! Pure JavaScript + HTML + CSS
- Works in any browser with Fetch API + ES6+ support
- Compatible with IE11? No (uses Fetch, Promise, etc.)

---

## Support & Questions

For issues or questions:
1. Check this guide's Troubleshooting section
2. Review component source code comments
3. Check browser console for errors
4. Review backend API reference in `FINANCE_JOURNAL_API_REFERENCE.md`
5. Open issue with:
   - Steps to reproduce
   - Browser/OS
   - Console errors
   - Network tab screenshots

---

**Created:** 2025-12-18  
**Last Updated:** 2025-12-18  
**Version:** 1.0  
**Status:** ✅ Production Ready
