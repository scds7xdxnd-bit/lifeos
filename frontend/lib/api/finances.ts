import { apiGet, apiPost, apiPatch, apiPut } from './client'

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface Currency {
  code: string
  symbol: string
  name: string
  decimal_places: number
  is_base: boolean
}

export interface Account {
  id: number
  name: string
  account_type: 'asset' | 'liability' | 'equity' | 'income' | 'expense'
  account_subtype: string | null
  category_id: number | null
  code: string | null
  is_active: boolean
  description: string | null
  created_at: string | null
}

export interface AccountCategory {
  id: number
  name: string
  base_type: string
  is_default: boolean
  is_system: boolean
}

export interface Transaction {
  id: number
  amount: number
  currency_code: string | null
  description: string | null
  occurred_at: string
  journal_entry_id: number | null
  counterparty: string | null
  category: string | null
  source: string
  is_void: boolean
  void_of_id: number | null
  edited_at: string | null
}

export interface JournalLine {
  id?: number
  account_id: number
  account_name?: string | null
  debit: number
  credit: number
  memo: string | null
  currency_code?: string | null
}

export interface JournalEntryListItem {
  id: number
  entry_number: number
  description: string | null
  posted_at: string
  lines: number
  debit_total: number
  credit_total: number
}

export interface JournalEntryDetail {
  id: number
  description: string | null
  posted_at: string
  debit_total: number
  credit_total: number
  lines: JournalLine[]
}

export interface SeedResult {
  seeded: boolean
  account_count: number
  category_count: number
}

export interface PaginatedTransactions {
  transactions: Transaction[]
  total: number
  page: number
  pages: number
  per_page: number
}

export interface PaginatedAccounts {
  accounts: Account[]
  total: number
  page: number
  pages: number
  per_page: number
}

// ---------------------------------------------------------------------------
// Request types
// ---------------------------------------------------------------------------

export interface CreateTransactionInput {
  debit_account_id: number
  credit_account_id: number
  amount: number
  currency_code?: string | null
  description?: string | null
  occurred_at?: string | null
  counterparty?: string | null
  category?: string | null
}

export interface SplitLineInput {
  account_id: number
  amount: number
  memo?: string | null
}

export interface CreateSplitTransactionInput {
  credit_account_id: number
  total_amount: number
  currency_code?: string | null
  description?: string | null
  occurred_at?: string | null
  counterparty?: string | null
  split_lines: SplitLineInput[]
}

export interface CreateTransferInput {
  from_account_id: number
  to_account_id: number
  amount: number
  currency_code?: string | null
  description?: string | null
  occurred_at?: string | null
}

export interface UpdateTransactionInput {
  description?: string | null
  counterparty?: string | null
  category?: string | null
  occurred_at?: string | null
}

export interface VoidTransactionInput {
  reason?: string | null
}

export interface TransactionListParams {
  start_date?: string
  end_date?: string
  account_id?: number
  category?: string
  counterparty?: string
  currency_code?: string
  min_amount?: number
  max_amount?: number
  source?: string
  include_void?: boolean
  page?: number
  per_page?: number
}

export interface AccountListParams {
  account_type?: string
  account_subtype?: string
  is_active?: boolean
  category_id?: number
  page?: number
  per_page?: number
}

export interface CreateAccountInput {
  name: string
  account_type: 'asset' | 'liability' | 'equity' | 'income' | 'expense'
  account_subtype?: string | null
  category_id?: number | null
  category_name_new?: string | null
  description?: string | null
}

export interface UpdateAccountInput {
  name?: string | null
  description?: string | null
  account_subtype?: string | null
  category_id?: number | null
  category_name_new?: string | null
  default_currency?: string | null
}

export interface ExchangeRate {
  id: number
  from_currency: string
  to_currency: string
  rate: string
  effective_date: string
  source: string
}

export interface CreateExchangeRateInput {
  from_currency: string
  to_currency: string
  rate: string
  effective_date: string
}

// ---------------------------------------------------------------------------
// API client
// ---------------------------------------------------------------------------

const BASE = '/api/finance'

export const financesApi = {
  // ── Accounts ──────────────────────────────────────────────────────────────
  listAccounts: (params?: AccountListParams) => {
    const qs = params ? '?' + new URLSearchParams(
      Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== null)
        .map(([k, v]) => [k, String(v)])
    ).toString() : ''
    return apiGet<PaginatedAccounts>(`${BASE}/accounts${qs}`)
  },

  createAccount: (data: CreateAccountInput) =>
    apiPost<{ ok: boolean; account: Account }>(`${BASE}/accounts`, data),

  createAccountInline: (data: Omit<CreateAccountInput, 'code' | 'description'>) =>
    apiPost<{ ok: boolean; account: Account }>(`${BASE}/accounts/inline`, data),

  seedAccounts: () =>
    apiPost<{ ok: boolean } & SeedResult>(`${BASE}/accounts/seed`, {}),

  searchAccounts: (q: string, limit = 20) =>
    apiGet<{ ok: boolean; results: Array<{ id: number; name: string; account_type: string; account_subtype: string | null; is_existing: boolean }> }>(
      `${BASE}/accounts/search?q=${encodeURIComponent(q)}&limit=${limit}`
    ),

  getAccountSubtypes: (accountType: string) =>
    apiGet<{ ok: boolean; account_type: string; subtypes: string[] }>(
      `${BASE}/accounts/subtypes/${accountType}`
    ),

  listCategories: (baseType?: string) => {
    const qs = baseType ? `?base_type=${baseType}` : ''
    return apiGet<{ ok: boolean; categories: AccountCategory[] }>(`${BASE}/account-categories${qs}`)
  },

  createCategory: (data: { base_type: string; name: string; is_default?: boolean }) =>
    apiPost<{ ok: boolean; category: AccountCategory }>(`${BASE}/account-categories`, data),

  updateAccount: (id: number, data: UpdateAccountInput) =>
    apiPatch<{ ok: boolean; account: Account }>(`${BASE}/accounts/${id}`, data),

  deactivateAccount: (id: number) =>
    apiPost<{ ok: boolean; account: { id: number; is_active: boolean } }>(`${BASE}/accounts/${id}/deactivate`, {}),

  // ── Exchange rates ────────────────────────────────────────────────────────
  listCurrencies: () =>
    apiGet<{ ok: boolean; currencies: Currency[] }>(`${BASE}/currencies`),

  getBaseCurrency: () =>
    apiGet<{ ok: boolean; currency_code: string }>(`${BASE}/currencies/base`),

  setBaseCurrency: (currency_code: string) =>
    apiPut<{ ok: boolean; currency_code: string }>(`${BASE}/currencies/base`, { currency_code }),

  listExchangeRates: (from_currency?: string, to_currency?: string) => {
    const qs = new URLSearchParams()
    if (from_currency) qs.set('from_currency', from_currency)
    if (to_currency) qs.set('to_currency', to_currency)
    const q = qs.toString()
    return apiGet<{ ok: boolean; rates: ExchangeRate[] }>(`${BASE}/exchange-rates${q ? '?' + q : ''}`)
  },

  createExchangeRate: (data: CreateExchangeRateInput) =>
    apiPost<{ ok: boolean; rate: ExchangeRate }>(`${BASE}/exchange-rates`, data),

  // ── Transactions ──────────────────────────────────────────────────────────
  listTransactions: (params?: TransactionListParams) => {
    const qs = params ? '?' + new URLSearchParams(
      Object.entries(params)
        .filter(([, v]) => v !== undefined && v !== null)
        .map(([k, v]) => [k, String(v)])
    ).toString() : ''
    return apiGet<PaginatedTransactions>(`${BASE}/transactions${qs}`)
  },

  getTransaction: (id: number) =>
    apiGet<{ ok: boolean; transaction: Transaction }>(`${BASE}/transactions/${id}`),

  createTransaction: (data: CreateTransactionInput) =>
    apiPost<{ ok: boolean; journal_entry_id: number }>(`${BASE}/transactions`, data),

  createSplitTransaction: (data: CreateSplitTransactionInput) =>
    apiPost<{ ok: boolean; journal_entry_id: number }>(`${BASE}/transactions/split`, data),

  createTransfer: (data: CreateTransferInput) =>
    apiPost<{ ok: boolean; journal_entry_id: number }>(`${BASE}/transactions/transfer`, data),

  updateTransaction: (id: number, data: UpdateTransactionInput) =>
    apiPatch<{ ok: boolean; transaction: Transaction }>(`${BASE}/transactions/${id}`, data),

  voidTransaction: (id: number, data?: VoidTransactionInput) =>
    apiPost<{ ok: boolean; reversal_entry_id: number }>(`${BASE}/transactions/${id}/void`, data ?? {}),

  // ── Journal ───────────────────────────────────────────────────────────────
  listJournalEntries: () =>
    apiGet<{ ok: boolean; entries: JournalEntryListItem[] }>(`${BASE}/journal`),

  getJournalEntry: (id: number) =>
    apiGet<{ ok: boolean; entry: JournalEntryDetail }>(`${BASE}/journal/entries/${id}`),

  // ── Trial balance ─────────────────────────────────────────────────────────
  getTrialBalance: (asOf?: string) => {
    const qs = asOf ? `?as_of=${asOf}` : ''
    return apiGet<{ ok: boolean; accounts: Array<{ account_id: number; name: string; code: string | null; balance: number }> }>(
      `${BASE}/trial-balance${qs}`
    )
  },

  // ── Dashboard ─────────────────────────────────────────────────────────────
  getDashboard: () =>
    apiGet<{ ok: boolean; [key: string]: unknown }>(`${BASE}/dashboard`),
}
