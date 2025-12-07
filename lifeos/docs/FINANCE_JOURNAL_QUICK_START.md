# Finance Journal Backend: Quick Start Guide

**For:** Backend developers integrating with journal/account features  
**Time to understand:** 5 minutes  
**Time to integrate:** 10 minutes

---

## TL;DR

Three new endpoints for journal-first account creation:

```bash
# 1. Search existing accounts (typeahead)
GET /finance/accounts/search?q=savings&limit=20

# 2. Create new account (minimal input)
POST /finance/accounts/inline
{ "name": "My Savings", "account_type": "asset", "account_subtype": "bank" }

# 3. Get valid subtypes (for dropdowns)
GET /finance/accounts/subtypes/asset
```

All are production-ready, fully tested, and event-driven.

---

## Integration Checklist

### For Frontend Team

- [ ] Add typeahead input in journal entry form
- [ ] Call GET `/finance/accounts/search` as user types
- [ ] Show dropdown with existing accounts + "+ Create new" option
- [ ] On "Create new", show inline form with 3 fields:
  - Account name (text input)
  - Account type (dropdown: asset/liability/equity/income/expense)
  - Account subtype (dropdown, populate from GET `/finance/accounts/subtypes/<type>`)
- [ ] Call POST `/finance/accounts/inline` on form submit
- [ ] Use returned `account.id` in journal entry lines
- [ ] Test typeahead with various queries (prefix, substring, no match)
- [ ] Test inline creation with all account types
- [ ] Test idempotency (same form submission twice = same account)

**Estimated effort:** 4-6 hours

---

### For Backend Team (Post-Implementation)

- [ ] Apply migration: `flask db upgrade`
- [ ] Run tests: `pytest lifeos/tests/test_finance*.py -v`
- [ ] Verify indexes created in DB
- [ ] Check outbox queue (should be empty after worker runs)
- [ ] Monitor typeahead latency (should be < 100ms)
- [ ] Optional: Update trial balance UI to group by `account_type`
- [ ] Optional: Add ML account suggester to `get_suggested_accounts()`

**Estimated effort:** 2-4 hours

---

### For DevOps Team

- [ ] Test migration on staging database
- [ ] Backup production database before deployment
- [ ] Deploy migration with zero downtime (online DDL)
- [ ] Verify indexes: `SHOW INDEXES FROM finance_account;`
- [ ] Monitor query performance for first 24 hours
- [ ] Check worker logs for outbox processing

**Estimated effort:** 1-2 hours

---

## Code Examples

### Example 1: Frontend - Typeahead Search

```javascript
// React component for account search
import { useState, useEffect } from 'react';

export function AccountSearchDropdown({ onSelectAccount }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (query.length < 1) {
      setResults([]);
      return;
    }

    setLoading(true);
    fetch(`/finance/accounts/search?q=${encodeURIComponent(query)}&limit=20`, {
      headers: { 'Authorization': `Bearer ${getJWT()}` }
    })
      .then(r => r.json())
      .then(data => {
        setResults(data.results);
        setLoading(false);
      })
      .catch(err => {
        console.error('Search failed:', err);
        setLoading(false);
      });
  }, [query]);

  return (
    <div>
      <input
        type="text"
        value={query}
        onChange={e => setQuery(e.target.value)}
        placeholder="Search or create account..."
      />
      {loading && <p>Loading...</p>}
      <ul>
        {results.map(acc => (
          <li key={acc.id} onClick={() => onSelectAccount(acc)}>
            {acc.name} ({acc.account_type})
          </li>
        ))}
        {results.length === 0 && query && (
          <li onClick={() => onSelectAccount(null)}>
            + Create new account "{query}"
          </li>
        )}
      </ul>
    </div>
  );
}
```

### Example 2: Frontend - Inline Account Creation Form

```javascript
export function InlineAccountCreationForm({ accountName, onAccountCreated }) {
  const [accountType, setAccountType] = useState('asset');
  const [accountSubtype, setAccountSubtype] = useState('');
  const [subtypes, setSubtypes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load subtypes when account type changes
  useEffect(() => {
    fetch(`/finance/accounts/subtypes/${accountType}`)
      .then(r => r.json())
      .then(data => setSubtypes(data.subtypes));
  }, [accountType]);

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/finance/accounts/inline', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${getJWT()}`,
          'X-CSRF-Token': getCsrfToken(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: accountName,
          account_type: accountType,
          account_subtype: accountSubtype || null
        })
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.error || 'Creation failed');
      }

      const data = await response.json();
      onAccountCreated(data.account);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      <div>
        <label>Account Type *</label>
        <select value={accountType} onChange={e => setAccountType(e.target.value)}>
          <option value="asset">Asset</option>
          <option value="liability">Liability</option>
          <option value="equity">Equity</option>
          <option value="income">Income</option>
          <option value="expense">Expense</option>
        </select>
      </div>

      <div>
        <label>Account Subtype</label>
        <select value={accountSubtype} onChange={e => setAccountSubtype(e.target.value)}>
          <option value="">-- Select --</option>
          {subtypes.map(st => (
            <option key={st} value={st}>{st}</option>
          ))}
        </select>
      </div>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      <button type="submit" disabled={loading}>
        {loading ? 'Creating...' : 'Create Account'}
      </button>
    </form>
  );
}
```

### Example 3: Backend - Service Usage

```python
from lifeos.domains.finance.services.accounting_service import (
    search_accounts,
    create_account_inline,
    get_account_subtypes,
)

# In your service or controller
def process_journal_entry(user_id, journal_data):
    # 1. Create missing accounts
    for line in journal_data['lines']:
        if 'account_id' not in line or line['account_id'] is None:
            # Create account inline
            account = create_account_inline(
                user_id=user_id,
                name=line['account_name'],
                account_type=line['account_type'],
                account_subtype=line.get('account_subtype')
            )
            line['account_id'] = account.id

    # 2. Post journal entry with account IDs
    entry = post_journal_entry(
        user_id=user_id,
        description=journal_data.get('description'),
        lines=journal_data['lines']
    )
    return entry
```

---

## File Locations

**All new code is in `/lifeos/domains/finance/`:**

```
finance/
├── models/
│   └── accounting_models.py         # Updated Account model
├── services/
│   └── accounting_service.py        # New search/create functions
├── schemas/
│   └── finance_schemas.py           # New Pydantic schemas
├── controllers/
│   └── accounting_api.py            # New endpoints
└── events.py                        # New FINANCE_ACCOUNT_CREATED event
```

**Tests:**
```
tests/
├── test_finance_account_creation.py # Unit tests
└── test_finance_accounts_api.py     # Integration tests
```

**Documentation:**
```
docs/
├── FINANCE_JOURNAL_BACKEND_SPECIFICATION.md       # Original spec
├── FINANCE_JOURNAL_BACKEND_IMPLEMENTATION_SUMMARY.md  # This delivery
├── FINANCE_JOURNAL_API_REFERENCE.md               # API docs
├── FINANCE_ACCOUNT_SCHEMA_CHANGES.md              # Database docs
└── lifeos_architecture.md                         # Overall architecture
```

---

## Testing

### Run All Tests

```bash
cd /Users/ammarhakimi/Dev/finance_app_clean

# Unit tests (service layer)
pytest lifeos/tests/test_finance_account_creation.py -v

# Integration tests (API layer)
pytest lifeos/tests/test_finance_accounts_api.py -v

# All finance tests
pytest lifeos/tests/test_finance*.py -v --cov=lifeos/domains/finance
```

### Manual Testing

```bash
# 1. Apply migration
flask db upgrade

# 2. Start server
flask run

# 3. Test endpoints
curl -X GET 'http://localhost:5000/finance/accounts/search?q=test' \
  -H "Authorization: Bearer $JWT_TOKEN"

curl -X POST 'http://localhost:5000/finance/accounts/inline' \
  -H "Authorization: Bearer $JWT_TOKEN" \
  -H "X-CSRF-Token: $CSRF_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","account_type":"asset"}'

curl -X GET 'http://localhost:5000/finance/accounts/subtypes/asset'
```

---

## Common Issues

### Issue 1: "invalid_account_type" error

**Cause:** Account type not in `['asset', 'liability', 'equity', 'income', 'expense']`

**Fix:** Check the dropdown options in frontend and ensure only valid types are sent.

### Issue 2: "invalid_account_subtype" error

**Cause:** Subtype not valid for account_type

**Fix:** Call GET `/finance/accounts/subtypes/<type>` first to get valid subtypes.

### Issue 3: Search returns no results

**Cause:** Query is empty or > 100 chars, or account is inactive

**Fix:** Ensure query is 1-100 chars and account has `is_active=true`.

### Issue 4: Account creation returns 201 but account not appearing

**Cause:** Account was created but outbox event failed

**Fix:** Check worker logs (`flask logs worker`), check `platform_outbox` table for pending messages.

### Issue 5: Slow typeahead (> 500ms)

**Cause:** Missing index or large account table

**Fix:** Verify indexes created: `SHOW INDEXES FROM finance_account;` should show `ix_finance_account_user_normalized_name`.

---

## Performance Tips

1. **Typeahead:**
   - Cache subtypes endpoint (response is static)
   - Debounce search input (wait 300ms before calling API)
   - Limit results to 20 (default)

2. **Account Creation:**
   - Show loading state during creation
   - Disable submit button while loading
   - Handle network errors gracefully

3. **Trial Balance:**
   - If you add a trial balance feature, cache for 5 minutes
   - Group by `account_type` (5 values) not `category` (many values)

---

## Next Steps

1. **Frontend Integration (start today):**
   - Add typeahead to journal entry form
   - Test with your mock API
   - Once backend is deployed, switch to real endpoints

2. **Trial Balance Update (after deployment):**
   - Update trial balance query to group by `account_type`
   - Test with new and old accounts
   - Ship it 🚀

3. **ML Integration (future):**
   - Enhance `get_suggested_accounts()` with ML model
   - Pass context (transaction description, etc.)
   - Test with real user data

---

## Support

- **Questions about API?** See `/docs/FINANCE_JOURNAL_API_REFERENCE.md`
- **Questions about schema?** See `/docs/FINANCE_ACCOUNT_SCHEMA_CHANGES.md`
- **Questions about architecture?** See `/docs/lifeos_architecture.md`
- **Questions about code?** See docstrings in source files

---

**You're all set! Start integrating and let us know if you hit any blockers.** 🎉

