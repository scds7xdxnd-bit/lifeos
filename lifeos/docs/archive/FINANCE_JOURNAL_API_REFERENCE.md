# Finance Journal API Reference

**Base URL:** `http://localhost:5000/finance`  
**Authentication:** JWT Bearer token (all endpoints except subtypes)  
**Content-Type:** application/json

---

## Endpoints

### 1. Search Accounts (Typeahead)

**Endpoint:** `GET /accounts/search`

**Purpose:** Find existing accounts by name. For journal entry UI to populate account field.

**Query Parameters:**
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | - | Search query (1-100 chars) |
| `limit` | integer | No | 20 | Max results (1-100) |
| `include_ml` | boolean | No | true | Include ML suggestions |

**Rate Limit:** 240 requests/minute

**Example Request:**
```bash
GET /finance/accounts/search?q=savings&limit=10
Authorization: Bearer eyJhbGc...
```

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
      "is_existing": true
    },
    {
      "id": 2,
      "name": "High Yield Savings",
      "account_type": "asset",
      "account_subtype": "savings",
      "is_existing": true
    }
  ]
}
```

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 400 | `invalid_query` | Query is empty or > 100 chars |
| 401 | - | Missing JWT token |
| 429 | - | Rate limit exceeded |

---

### 2. Create Account Inline

**Endpoint:** `POST /accounts/inline`

**Purpose:** Create a new account with minimal input. Called when user chooses "+ Create new account" in typeahead.

**Required Permissions:** `finance:write`

**Request Body:**
```json
{
  "name": "My Savings Account",
  "account_type": "asset",
  "account_subtype": "bank"
}
```

**Body Parameters:**
| Field | Type | Required | Max Length | Valid Values |
|-------|------|----------|-----------|--------------|
| `name` | string | Yes | 255 | Any non-empty string |
| `account_type` | string | Yes | - | `asset`, `liability`, `equity`, `income`, `expense` |
| `account_subtype` | string | No | 64 | Depends on account_type (see GET /subtypes) |

**Rate Limit:** 120 requests/minute

**Security:**
- Requires valid JWT
- Requires CSRF token (in header or cookie)
- Requires `finance:write` role

**Example Request:**
```bash
POST /finance/accounts/inline
Authorization: Bearer eyJhbGc...
X-CSRF-Token: abc123...
Content-Type: application/json

{
  "name": "My Savings",
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
    "name": "My Savings",
    "account_type": "asset",
    "account_subtype": "bank",
    "created_at": "2025-12-06T10:30:00Z"
  }
}
```

**Note:** If account with same normalized name already exists, returns existing account (idempotent).

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 400 | `invalid_name` | Name is empty or > 255 chars |
| 400 | `invalid_account_type` | account_type not in allowed list |
| 400 | `invalid_account_subtype` | account_subtype not valid for account_type |
| 400 | `validation_error` | Other validation error (see details) |
| 401 | - | Missing JWT token |
| 403 | - | Missing CSRF token or insufficient permissions |
| 429 | - | Rate limit exceeded |

---

### 3. Get Account Subtypes

**Endpoint:** `GET /accounts/subtypes/<account_type>`

**Purpose:** Retrieve valid subtypes for a given account type. Used to populate subtype dropdown in inline creation form.

**Path Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `account_type` | string | One of: `asset`, `liability`, `equity`, `income`, `expense` |

**Rate Limit:** 600 requests/minute (high limit; response is cacheable)

**Authentication:** Not required (public data)

**Example Request:**
```bash
GET /finance/accounts/subtypes/asset
```

**Response (200 OK):**
```json
{
  "ok": true,
  "account_type": "asset",
  "subtypes": [
    "cash",
    "bank",
    "investment",
    "property",
    "other"
  ]
}
```

**All Valid Combinations:**

| Account Type | Subtypes |
|--------------|----------|
| `asset` | cash, bank, investment, property, other |
| `liability` | loan, credit_card, payable, other |
| `equity` | contributed, retained_earnings, other |
| `income` | salary, investment, business, rental, other |
| `expense` | groceries, utilities, rent, transportation, entertainment, other |

**Error Responses:**

| Status | Error | Description |
|--------|-------|-------------|
| 400 | `invalid_account_type` | account_type not in allowed list |

---

## Integration Examples

### Example 1: User Opens Journal Entry Form

```javascript
// 1. Initialize dropdown
async function loadAccountSubtypes(accountType) {
  const response = await fetch(`/finance/accounts/subtypes/${accountType}`);
  const data = await response.json();
  return data.subtypes;
}

// 2. Populate subtype options
const subtypes = await loadAccountSubtypes('asset');
// subtypes = ['cash', 'bank', 'investment', 'property', 'other']
```

### Example 2: User Types Account Name (Typeahead)

```javascript
// Typeahead search as user types
async function searchAccounts(query) {
  if (!query || query.length < 1) return [];
  
  const response = await fetch(
    `/finance/accounts/search?q=${encodeURIComponent(query)}&limit=20`,
    {
      headers: { 'Authorization': `Bearer ${jwt_token}` }
    }
  );
  const data = await response.json();
  return data.results;
}

// Results show existing accounts + "+ Create new account" option
const results = await searchAccounts('sav');
// results = [
//   { id: 1, name: "Savings Account", account_type: "asset", is_existing: true },
//   { id: 2, name: "High Yield Savings", account_type: "asset", is_existing: true }
// ]
```

### Example 3: User Creates New Account

```javascript
// User clicks "+ Create new account" and fills form
async function createAccount(name, accountType, accountSubtype) {
  const response = await fetch(
    '/finance/accounts/inline',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwt_token}`,
        'X-CSRF-Token': csrf_token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        name: name,
        account_type: accountType,
        account_subtype: accountSubtype
      })
    }
  );
  
  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error.error);
    return null;
  }
  
  const data = await response.json();
  return data.account;
}

// Create account
const newAccount = await createAccount('My Savings', 'asset', 'bank');
// newAccount = {
//   id: 42,
//   name: "My Savings",
//   account_type: "asset",
//   account_subtype: "bank",
//   created_at: "2025-12-06T10:30:00Z"
// }

// Now use newAccount.id in journal entry line
```

### Example 4: User Posts Journal Entry

```javascript
// After creating account(s), user posts journal entry
async function postJournalEntry(description, lines) {
  const response = await fetch(
    '/finance/journal',
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${jwt_token}`,
        'X-CSRF-Token': csrf_token,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        description: description,
        lines: lines  // [{ account_id: 42, dc: 'D', amount: 1000, memo: '...' }, ...]
      })
    }
  );
  
  const data = await response.json();
  return data.entry_id;
}
```

---

## Error Handling Guide

### Common Errors

#### 400 Bad Request: Invalid Account Type
```json
{
  "ok": false,
  "error": "invalid_account_type"
}
```
**Fix:** Ensure account_type is one of: `asset`, `liability`, `equity`, `income`, `expense`

#### 400 Bad Request: Invalid Subtype
```json
{
  "ok": false,
  "error": "invalid_account_subtype"
}
```
**Fix:** Call GET `/accounts/subtypes/<type>` first to get valid subtypes for that type

#### 400 Bad Request: Invalid Query
```json
{
  "ok": false,
  "error": "invalid_query"
}
```
**Fix:** Ensure search query is 1-100 characters

#### 401 Unauthorized
```json
{
  "ok": false,
  "error": "..."
}
```
**Fix:** Check JWT token is valid and passed in Authorization header

#### 403 Forbidden
```json
{
  "ok": false,
  "error": "..."
}
```
**Fix:** Check CSRF token is valid and user has `finance:write` permission

#### 429 Too Many Requests
```
HTTP/1.1 429 Too Many Requests
Retry-After: 60
```
**Fix:** Wait before retrying. Rate limits are:
- Search: 240/minute
- Create: 120/minute
- Subtypes: 600/minute

---

## Response Format

All successful responses follow this format:
```json
{
  "ok": true,
  "result_key": {...}  // Specific data for endpoint
}
```

All error responses follow this format:
```json
{
  "ok": false,
  "error": "error_code"
}
```

---

## Idempotency

**Create Account** is idempotent:
- If you call it twice with same `name`, `account_type`, `account_subtype`
- You get back the same account both times
- No duplicate is created
- Safe to retry on network failure

```bash
# First call
POST /finance/accounts/inline
{ "name": "Savings", "account_type": "asset", "account_subtype": "bank" }
→ { "ok": true, "account": { "id": 42, ... } }

# Second call (identical)
POST /finance/accounts/inline
{ "name": "Savings", "account_type": "asset", "account_subtype": "bank" }
→ { "ok": true, "account": { "id": 42, ... } }  # Same ID!
```

---

## Caching

Recommended caching:
- **GET /subtypes/<type>:** Cache for 1 hour (data never changes)
- **GET /accounts/search:** Cache for 5 minutes per query (data updates slowly)
- **POST /accounts/inline:** Never cache (state-modifying)

---

## Event Emission

When you successfully create an account via POST `/accounts/inline`, an event is emitted:

**Event Type:** `finance.account.created`

**Payload:**
```json
{
  "account_id": 42,
  "user_id": 1,
  "name": "My Savings",
  "account_type": "asset",
  "account_subtype": "bank",
  "created_at": "2025-12-06T10:30:00Z"
}
```

This event is:
- Persisted to `platform_outbox` table
- Async-delivered to insights engine
- Used for telemetry and analytics
- Safe for replay (idempotent event type)

