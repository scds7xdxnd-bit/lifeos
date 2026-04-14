# Opus Prompt — LifeOS Finance Domain: Phase 1-2 (Accounts + Ledger + Currency Foundation)

Copy this entire prompt into a new Opus conversation.
Attach these 3 files as context: `lifeos_architecture.md`, `DESIGN.md`, `ui_ux_constitution.md`

---

```
TASK: architect finance domain Phase 1-2 (Chart of Accounts + Account Manager, Transaction Input + Double-Entry Ledger) with currency-aware data model for all future phases
CTX:
  project: LifeOS — unified personal life management platform
  purpose: help a person calmly face themselves over time and choose responsible action
  stack: Next.js 16 + React 19 + TypeScript + Tailwind v4 + shadcn/ui (frontend) | Flask 3.x + SQLAlchemy 3.1 + PostgreSQL 16 (backend, deployed Fly.io) | SQLite (dev)
  state_management: React Query v5 (staleTime: 5min, retry: 1)
  auth: JWT + Session hybrid, RBAC (@require_permission), CSRF protection. JWT requests bypass CSRF; session-only requires CSRF.
  events: in-process event bus → outbox (platform_outbox table, skip-locked) → worker dispatcher → insights engine
  i18n: en, ko, zh via getAppTranslations(lang) pattern
  icons: lucide-react
  design_system: "Botanical Editorial" (see attached DESIGN.md)
  ui_constitution: see attached ui_ux_constitution.md (binding)
  architecture: see attached lifeos_architecture.md (normative)

  finance_domain_status:
    backend: ✅ partially complete (14 tables exist, services exist, events exist)

    existing_tables_FULL_SCHEMA:

      # ── Chart of Accounts ───────────────────────────────────────────────────

      finance_account_category:
        columns:
          id: Integer PK
          user_id: Integer FK → user.id, nullable, indexed (null = system category)
          code: String(16), unique, not null (generated)
          name: String(128), not null
          slug: String(128), not null (normalized for uniqueness)
          base_type: String(16), not null (asset/liability/equity/income/expense)
          normal_balance: String(8), default "debit"
          is_default: Boolean, default False
          is_system: Boolean, default False
          created_at: DateTime, default utcnow
          updated_at: DateTime, auto-updated
        indexes:
          uq_(user_id, base_type, slug): UNIQUE
          ix_(user_id, base_type, is_default)
          ix_(user_id, base_type, name)
        relationships:
          one-to-many → Account (category_id)

      finance_account:
        columns:
          id: Integer PK
          user_id: Integer FK → user.id, not null, indexed
          category_id: Integer FK → finance_account_category.id, nullable
          name: String(255), not null
          code: String(32), nullable, indexed
          description: Text, nullable
          is_active: Boolean, default True (soft deactivation)
          account_type: String(16), not null, indexed (asset/liability/equity/income/expense)
          account_subtype: String(64), nullable
          normalized_name: String(255), not null, indexed (lowercase, trimmed for search)
          created_at: DateTime, default utcnow
        indexes:
          ix_(user_id, account_type)
          ix_(user_id, normalized_name)
          ix_(user_id, category_id)
          ix_(account_type)
          ix_(normalized_name)
        valid_subtypes:
          asset: [cash, bank, investment, property, other]
          liability: [loan, credit_card, payable, other]
          equity: [contributed, retained_earnings, other]
          income: [salary, investment, business, rental, other]
          expense: [groceries, utilities, rent, transportation, entertainment, other]
        relationships:
          many-to-one → AccountCategory (category)
          one-to-many → JournalLine (journal_lines)

      # ── Double-Entry Ledger ─────────────────────────────────────────────────

      finance_journal_entry:
        columns:
          id: Integer PK
          user_id: Integer FK → user.id, not null, indexed
          description: Text, nullable
          posted_at: DateTime, default utcnow
        indexes:
          ix_(user_id, posted_at)
        properties:
          is_balanced: True if sum(debit) == sum(credit), tolerance 0.005
        relationships:
          one-to-many → JournalLine (lines, cascade="all, delete-orphan")

      finance_journal_line:
        columns:
          id: Integer PK
          entry_id: Integer FK → finance_journal_entry.id, not null, indexed (CASCADE delete)
          account_id: Integer FK → finance_account.id, not null, indexed
          debit: Numeric(18,2), default 0
          credit: Numeric(18,2), default 0
          memo: Text, nullable
        relationships:
          many-to-one → JournalEntry (entry)
          many-to-one → Account (account)

      # ── Transaction Log ─────────────────────────────────────────────────────

      finance_transaction:
        columns:
          id: Integer PK
          user_id: Integer FK → user.id, not null, indexed
          amount: Numeric(18,2), not null
          description: Text, nullable
          occurred_at: DateTime, default utcnow
          journal_entry_id: Integer FK → finance_journal_entry.id, nullable
          counterparty: String(255), nullable
          category: String(128), nullable
          source: String(32), default "manual" (manual/calendar_inferred/import/api)
          calendar_event_id: Integer FK → calendar_event.id, nullable
          confidence_score: Numeric(3,2), nullable (0.00-1.00)
          inference_status: String(16), nullable (pending/confirmed/rejected/None)
        indexes:
          ix_(user_id, occurred_at)
          ix_(calendar_event_id)

      # ── Reporting ───────────────────────────────────────────────────────────

      finance_trial_balance_setting:
        columns:
          id: Integer PK
          user_id: Integer FK, not null, indexed
          month: String(7), not null (YYYY-MM)
          auto_rollup: Boolean, default True

      finance_trial_balance_snapshot: # exists but minimal — reporting cache

      # ── Cash Forecasting ────────────────────────────────────────────────────

      finance_money_schedule_row:
        columns:
          id: Integer PK
          user_id: Integer FK, not null, indexed
          account_id: Integer FK, not null
          event_date: Date, not null
          amount: Numeric(18,2), not null
          memo: Text, nullable
        indexes:
          ix_(user_id, event_date)

      finance_money_schedule_daily_balance:
        columns:
          id: Integer PK
          user_id: Integer FK, not null, indexed
          as_of: Date, indexed
          balance: Numeric(18,2), not null
        indexes:
          ix_(user_id, as_of)

      finance_money_schedule_scenario:
        columns:
          id: Integer PK
          user_id: Integer FK, not null, indexed
          name: String(128), not null
          description: Text, nullable
        relationships:
          one-to-many → MoneyScheduleScenarioRow (rows, cascade)

      finance_money_schedule_scenario_row:
        columns:
          id: Integer PK
          scenario_id: Integer FK, not null, indexed
          base_row_id: Integer FK, nullable
          delta_amount: Numeric(18,2), default 0

      # ── Receivables ─────────────────────────────────────────────────────────

      finance_receivable_tracker:
        columns:
          id: Integer PK
          user_id: Integer FK, not null, indexed
          counterparty: String(255), not null
          principal: Numeric(18,2), not null
          start_date: Date, not null
          due_date: Date, nullable
          interest_rate: Numeric(5,2), nullable
        relationships:
          one-to-many → ReceivableManualEntry (manual_entries, cascade)
          one-to-many → LoanGroupLink (loan_group_links)

      finance_receivable_manual_entry:
        columns:
          id: Integer PK
          tracker_id: Integer FK, not null, indexed
          entry_date: Date, not null
          amount: Numeric(18,2), not null
          memo: Text, nullable

      # ── Loans ───────────────────────────────────────────────────────────────

      finance_loan_group:
        columns:
          id: Integer PK
          user_id: Integer FK, not null, indexed
          name: String(128), not null
          description: Text, nullable
        relationships:
          one-to-many → LoanGroupLink (links, cascade)

      finance_loan_group_link:
        columns:
          id: Integer PK
          group_id: Integer FK, not null, indexed
          tracker_id: Integer FK, not null, indexed

    CRITICAL_GAP: ALL 14 tables use Numeric(18,2) for monetary amounts with NO currency_code column.
      This Phase must add currency awareness WITHOUT breaking existing tests or services.
      Existing records will be retroactively treated as user's base currency via defaults.

    existing_events_FULL_CATALOG:
      FINANCE_ACCOUNT_CREATED:
        type: finance.account.created
        version: v1
        payload: {account_id, user_id, name, account_type, account_subtype?, category_id?, category_name?, category_base_type?, created_at}

      FINANCE_ACCOUNT_CATEGORY_UPDATED:
        type: finance.account.category_updated
        version: v1
        payload: {account_id, user_id, category_id?, category_name?, category_base_type, updated_at}

      FINANCE_TRANSACTION_CREATED:
        type: finance.transaction.created
        version: v1
        payload: {transaction_id, user_id, amount, description?, category?, counterparty?, occurred_at, source?, calendar_event_id?, confidence_score?, inferred_status?, payload_version}

      FINANCE_TRANSACTION_INFERRED:
        type: finance.transaction.inferred
        version: v1
        payload: {transaction_id, calendar_event_id, user_id, confidence_score, amount?, description?, payload_version, model_version?, is_false_positive?, is_false_negative?}

      FINANCE_JOURNAL_POSTED:
        type: finance.journal.posted
        version: v1
        payload: {entry_id, user_id, debit_total, credit_total, line_count}

      FINANCE_SCHEDULE_CREATED:
        type: finance.schedule.created
        version: v1
        payload: {row_id, user_id, amount, account_id, event_date}

      FINANCE_SCHEDULE_UPDATED:
        type: finance.schedule.updated
        version: v1
        payload: {row_id, user_id, fields (dict)}

      FINANCE_SCHEDULE_DELETED:
        type: finance.schedule.deleted
        version: v1
        payload: {row_id, user_id}

      FINANCE_SCHEDULE_RECOMPUTED:
        type: finance.schedule.recomputed
        version: v1
        payload: {user_id, days}

      FINANCE_RECEIVABLE_CREATED:
        type: finance.receivable.created
        version: v1
        payload: {tracker_id, user_id, principal, counterparty, start_date, due_date?}

      FINANCE_RECEIVABLE_ENTRY_RECORDED:
        type: finance.receivable.entry_recorded
        version: v1
        payload: {tracker_id, amount, entry_date, user_id}

      FINANCE_ML_SUGGEST_ACCOUNTS:
        type: finance.ml.suggest_accounts
        version: v1
        payload: {payload_version, user_id, description, suggestions (list[int]), model, model_version?, context?}

      FINANCE_ML_FEEDBACK:
        type: finance.ml.feedback
        version: v1
        payload: {user_id, suggestion_id, accepted, score?}

    existing_pydantic_schemas:
      AccountCreate: {user_id, name, account_type (Literal), category_id?, category_name_new?, account_subtype?, code?, description?}
      AccountResponse: extends AccountCreate + id
      AccountCategoryCreate: {base_type (Literal), name, is_default?}
      AccountCategoryResponse: {id, name, base_type, is_default, is_system}
      AccountSearchQuery: {q?, limit (default 20, max 100), include_ml?}
      AccountSearchResult: {id, name, account_type, account_subtype?, is_existing (default True)}
      AccountInlineCreate: {name, account_type (Literal), account_subtype?, category_id?, category_name_new?}
      AccountUpdateCategory: {category_id?, category_name_new?}
      AccountSubtypesResponse: {account_type, subtypes: List[str]}
      JournalLineSchema: {account_id, debit (default 0, ge=0), credit (default 0, ge=0), memo?}
      JournalEntryCreate: {user_id, description?, lines: List[JournalLineSchema]}
      JournalEntryLineInput: {account_id, dc (Literal "D"/"C"), amount (Decimal, gt=0), memo?}
      JournalEntryCreateRequest: {user_id, description?, posted_at?, lines (min 2, max 100)}
      TransactionCreate: {user_id, debit_account_id, credit_account_id, amount, description?, suggested_account_ids?}
      ScheduleRowCreate: {account_id, event_date, amount, memo?}
      ScheduleRowUpdate: {account_id?, event_date?, amount?, memo?}
      ForecastParams: {days (default 30, 1-365)}
      ReceivableCreate: {counterparty, principal, start_date, due_date?, interest_rate?}
      ReceivableUpdate: {counterparty?, principal?, start_date?, due_date?, interest_rate?}
      TrialBalanceFilter: {as_of (date)?}
      PeriodBalanceFilter: {start (date), end (date)}
      TrialBalanceRow: {account_id, account_name, account_code?, category_name?, normal_balance, debit, credit, net}

    existing_api_endpoints_FULL:

      # Accounting API (accounting_api.py) — mounted at /api/v1/finance
      GET    /accounts/search          JWT  240/min  Typeahead search by normalized_name
      GET    /accounts/subtypes/<type>  -    600/min  Valid subtypes for account type
      POST   /accounts/inline          JWT  finance:write  120/min  Inline account creation
      GET    /account-categories       JWT  240/min  List categories (optional base_type filter, include_system)
      POST   /account-categories       JWT  finance:write  120/min  Create custom category
      POST   /accounts                 JWT  finance:write  60/min   Create account (full form)
      PATCH  /accounts/<id>/category   JWT  finance:write  90/min   Update account category
      POST   /journal                  JWT  finance:write  120/min  Post journal entry (legacy route)
      POST   /transactions             JWT  finance:write  180/min  Create transaction (2-line entry)
      GET    /trial-balance            JWT  Trial balance per account
      POST   /suggestions/accounts     JWT  ML account suggestions from description
      POST   /suggestions/feedback     JWT  Record ML feedback

      # Journal API (journal_api.py) — mounted at /api/v1/finance
      GET    /journal                  JWT  240/min  List entries (50 most recent, desc by posted_at)
      GET    /journal/entries/<id>     JWT  240/min  Single entry with full line detail
      POST   /journal/entries          JWT  finance:write  120/min  Create journal entry

      # Schedule API (schedule_api.py + forecast_api.py) — mounted at /api/v1/finance
      POST   /schedule                 JWT  finance:write  Add schedule row, triggers recompute
      POST   /schedule/recompute       JWT  finance:write  Recompute daily balances
      GET    /forecast                 JWT  Get N-day forecast (configurable days param)
      PATCH  /schedule/<id>            JWT  finance:write  Update schedule row
      DELETE /schedule/<id>            JWT  finance:write  Delete schedule row

      # Trial Balance API (trial_balance_api.py) — mounted at /api/v1/finance
      GET    /trial_balance            JWT  Trial balance (optional as_of)
      GET    /trial_balance/period     JWT  Period balance (start, end)
      GET    /trial_balance/monthly    JWT  Monthly rollup

      # Receivable API (receivable_api.py) — mounted at /api/v1/finance
      GET    /receivables              JWT  List (paginated: page/per_page)
      POST   /receivables              JWT  finance:write  Create tracker
      GET    /receivables/<id>         JWT  Single tracker
      PATCH  /receivables/<id>         JWT  finance:write  Update tracker
      DELETE /receivables/<id>         JWT  finance:write  Delete tracker
      GET    /receivables/<id>/entries JWT  List entries (paginated)
      POST   /receivables/<id>/entries JWT  finance:write  Record entry

      # Dashboard API (dashboard_api.py) — mounted at /api/v1/finance
      GET    /dashboard                JWT  Aggregated: accounts, recent txns, upcoming schedule, receivables total, 7-day forecast

      # Import API (import_api.py) — mounted at /api/v1/finance
      POST   /import/preview           JWT  finance:write  Preview CSV
      POST   /import/commit            JWT  finance:write  Commit CSV import

      # RESPONSE FORMAT: {"ok": true, ...} or {"ok": false, "error": "error_code"}

    existing_service_methods_KEY:

      accounting_service.post_journal_entry(user_id, description, lines, posted_at?, max_lines?)
        → validates accounts active + belong to user
        → normalizes lines: debit/credit must balance (tolerance 0.005)
        → max 100 lines, max description 512 chars
        → emits FINANCE_JOURNAL_POSTED

      journal_service.record_transaction(user_id, amount, debit_account_id, credit_account_id, description)
        → creates 2-line balanced JournalEntry + Transaction (source="manual")
        → emits FINANCE_TRANSACTION_CREATED

      accounting_service.search_accounts(user_id, query, limit=20)
        → prefix matches first, then substring, then token-based fallback
        → uses normalized_name

      accounting_service.get_suggested_accounts(user_id, query, limit=10, include_ml=True)
        → combines search + optional ML ranking from suggestion_service

      trial_balance_service.calculate_trial_balance(user_id, as_of?)
        → returns {account_id: {"debit": X, "credit": Y}}
        → uses read cache scope "finance.reads"

      trial_balance_service.trial_balance_view(user_id, as_of?)
        → returns {"accounts": [...], "categories": [...]} with net balance per account

      dashboard_service.get_dashboard(user_id)
        → aggregates: accounts, recent_transactions, upcoming_schedule, receivables_total, forecast

      schedule_service.recompute_daily_balances(user_id, commit=True)
        → clears and rebuilds MoneyScheduleDailyBalance
        → emits FINANCE_SCHEDULE_RECOMPUTED

      suggestion_service.suggest_accounts(user_id, description)
        → legacy models → embeddings ranker fallback
        → emits FINANCE_ML_SUGGEST_ACCOUNTS

    existing_service_constants:
      VALID_ACCOUNT_TYPES = {"asset", "liability", "equity", "income", "expense"}
      BASE_TYPE_NORMAL_BALANCE = {
        "asset": "debit", "expense": "debit",
        "liability": "credit", "equity": "credit", "income": "credit"
      }
      ACCOUNT_SUBTYPES_MAP = {see valid_subtypes under finance_account above}
      BALANCE_TOLERANCE = 0.005
      MAX_JOURNAL_LINES = 100
      MAX_DESCRIPTION_LENGTH = 512

    existing_insight_rules:
      finance_rules.py:
        finance.transaction.created → "finance_spend" insight (amount + category)
        finance.journal.posted → "journal_posted" insight (balance update)

      finance strategy profile:
        domain="finance"
        finding_categories=("cashflow_coverage", "ledger_signal", "evidence_gap")
        event_priority_prefixes=("finance.journal.posted", "finance.transaction.created",
                                 "finance.schedule.", "finance.receivable.")
        insight_priority_kinds=("journal_posted", "finance_spend")

      finance humanization adapter:
        term replacements: ledger→"money record", cashflow→"money flow"
        event label: "transaction record(s)"

    existing_interpreter_integration:
      calendar → finance inference:
        classification_rules.py: finance triggered by keywords [buy, purchase, pay, shop, bill, expense, spend, subscription, fee, cost, charge] + location keywords [mall, store, walmart, etc.]
        base confidence: 0.7
        extracts: amount, description, counterparty
        FinanceTransactionAdapter.create_inferred_transaction(user_id, calendar_event_id, confidence_score, description, amount, counterparty, occurred_at)
        if confidence ≥ 0.7: creates inferred Transaction record with source="calendar_inferred"

    existing_tests (must not break):
      test_finance_accounts_api.py           Account CRUD and search
      test_finance_account_categories_api.py Category management
      test_finance_journal_api.py            Journal entry creation and listing
      test_finance_account_creation.py       Account creation workflows
      test_finance_services_and_trial_balance.py Service logic and trial balance
      test_finance_rollups.py                Monthly rollup calculations
      test_finance_ranker.py                 ML suggestion ranking
      test_finance_transactions_api.py       Transaction recording
      test_phase_3a5_finance_read_first_ui.py UI integration tests
      test_phase_3a5_finance_toggle_transitions.py Workflow transitions

    existing_migration_head: 20251224_insight_feed_indexes
    existing_finance_migrations:
      20251206_finance_account_type_classification
      20251206_finance_account_categories_update
      20251207_finance_journal_entry_index

    # ── User Preference Model (for base currency storage) ─────────────────

    user_preference_schema:
      table: user_preference
      columns:
        id: Integer PK
        user_id: Integer FK → user.id, indexed
        key: String(128), not null
        value: JSON, not null, default {}
        created_at: DateTime
        updated_at: DateTime
      access: one-to-many from User (user.preferences), cascade delete
      usage: key-value pairs, e.g. key="base_currency" value={"currency": "KRW"}

    # ── Backend Module Structure ──────────────────────────────────────────

    domain_module_layout:
      lifeos/domains/finance/
      ├── models/
      │   ├── accounting_models.py   → AccountCategory, Account, JournalEntry, JournalLine, Transaction, TrialBalanceSetting
      │   ├── schedule_models.py     → MoneyScheduleRow, MoneyScheduleDailyBalance, MoneyScheduleScenario, MoneyScheduleScenarioRow
      │   └── receivable_models.py   → ReceivableTracker, ReceivableManualEntry, LoanGroup, LoanGroupLink
      ├── controllers/
      │   ├── accounting_api.py      → accounts, categories, journal, transactions, suggestions
      │   ├── journal_api.py         → journal entry list/detail/create
      │   ├── schedule_api.py        → schedule CRUD + recompute
      │   ├── forecast_api.py        → forecast generation
      │   ├── trial_balance_api.py   → trial balance views
      │   ├── receivable_api.py      → receivable CRUD + entries
      │   ├── dashboard_api.py       → aggregated dashboard
      │   ├── import_api.py          → CSV preview/commit
      │   └── pages.py               → HTML template routes (legacy Jinja2)
      ├── services/
      │   ├── accounting_service.py  → account/category mgmt, journal posting, search, ML suggestions
      │   ├── journal_service.py     → record_transaction() (simple 2-line entry)
      │   ├── schedule_service.py    → schedule rows, daily balance recomputation
      │   ├── trial_balance_service.py → balance calculations, period/monthly, caching
      │   ├── receivable_service.py  → receivable CRUD, entries, loan groups
      │   ├── forecast_service.py    → daily balance projections
      │   ├── dashboard_service.py   → aggregated dashboard data
      │   ├── import_service.py      → CSV parsing and bulk import
      │   └── suggestion_service.py  → ML account suggestions + legacy model fallback
      ├── schemas/
      │   └── finance_schemas.py     → all Pydantic DTOs
      ├── events.py                  → event constants + catalog
      ├── mappers.py                 → DTO ↔ Model converters
      └── tasks/
          ├── trial_balance_rollups.py    → monthly aggregation background task
          └── recompute_money_schedule.py → schedule recomputation task

    # ── Frontend Current State ────────────────────────────────────────────

    frontend_existing_files:

      frontend/lib/api/finances.ts:
        EXISTS — fully typed API client with:
          types: Currency, Account, AccountCategory, Transaction (includes is_void, void_of_id, edited_at, currency_code),
                 JournalLine (includes currency_code), JournalEntry, SeedResult, PaginatedTransactions, PaginatedAccounts
          request_types: CreateTransactionInput, SplitLineInput, CreateSplitTransactionInput, CreateTransferInput,
                         UpdateTransactionInput, VoidTransactionInput, TransactionListParams, AccountListParams, CreateAccountInput
          methods:
            listAccounts(params?) → PaginatedAccounts
            createAccount(data) → {ok, account}
            createAccountInline(data) → {ok, account}
            seedAccounts() → {ok, seeded, account_count, category_count}
            searchAccounts(q, limit) → {ok, results}
            getAccountSubtypes(type) → {ok, account_type, subtypes}
            listCategories(baseType?) → {ok, categories}
            createCategory(data) → {ok, category}
            listTransactions(params?) → PaginatedTransactions
            getTransaction(id) → {ok, transaction}
            createTransaction(data) → {ok, journal_entry_id}
            createSplitTransaction(data) → {ok, journal_entry_id}
            createTransfer(data) → {ok, journal_entry_id}
            updateTransaction(id, data) → {ok, transaction}
            voidTransaction(id, data?) → {ok, reversal_entry_id}
            listJournalEntries() → {ok, entries}
            getJournalEntry(id) → {ok, entry}
            getTrialBalance(asOf?) → {ok, accounts[{account_id, name, code, balance}]}
            getDashboard() → {ok, ...}
          BASE_PATH: '/api/finance'

      frontend/app/(app)/finances/page.tsx:
        EXISTS — working page (NOT a stub) with:
          panels: overview | add-transaction | accounts | journal
          queries: ['finance', 'accounts'] → financesApi.listAccounts({per_page: 200})
                   ['finance', 'trial-balance'] → financesApi.getTrialBalance()
          computed: totalAssets, totalLiabilities, netWorth (from trial balance + accounts)
          seed flow: seedMutation → financesApi.seedAccounts() → invalidates ['finance']
          sections:
            - header (eyebrow, title, primaryQuestion)
            - onboarding card (if no accounts → seed CTA)
            - summary cards grid (net worth, total assets, total liabilities)
            - action bar (Add transaction, Accounts, Journal toggle pills)
            - panel switching (TransactionInputForm, AccountList, TransactionList)

      frontend/app/(app)/finances/_components/:
        FinanceSummaryCard.tsx: {label, amount, currency?, trend?, trendLabel?}
          formatAmount with KRW/JPY (0 decimals) vs others (2 decimals)
          Newsreader serif for amount, Manrope micro-label for label
          sage-tinted clipped card

        TransactionList.tsx: {limit?, onViewAll?, labelViewAll?, labelEmpty?, labelLoading?}
          query: ['finance', 'transactions', {per_page: limit}] → financesApi.listTransactions
          TransactionRow: icon for void/inferred/normal, description, date, category, formatted amount
          handles currency_code in display

        TransactionInputForm.tsx: {accounts, onSuccess?, onCancel?, defaultCurrency?, labelTitle?, labelSubmit?, labelCancel?}
          modes: simple | split | transfer
          simple: debit_account_id, credit_account_id, amount, description
          split: credit_account_id, total_amount, split_lines[{account_id, amount, memo}]
          transfer: currently shows "use journal entry form" placeholder
          mutations: financesApi.createTransaction / financesApi.createSplitTransaction
          invalidates: ['finance', 'transactions']

        AccountList.tsx: {onSelect?, filterType?, labelEmpty?, labelLoading?}
          query: ['finance', 'accounts', {account_type}] → financesApi.listAccounts
          groups by account_type in order: asset, liability, equity, income, expense
          TYPE_ICONS: asset=Landmark, liability=CreditCard, equity=TrendingUp, income=DollarSign, expense=ShoppingBag
          TYPE_COLORS: asset=#3a5c35, liability=#e8735c, equity=#4b6646, income=#3a5c35, expense=#767d72
          shows inactive badge for deactivated accounts

      frontend/lib/translations/app.ts:
        FinancesPageTranslations interface exists
        en translations: {eyebrow, title, subtitle, primaryQuestion, setupTitle, setupBody, setupCta, settingUp,
                         netWorth, totalAssets, totalLiabilities, addTransaction, accounts, journal,
                         save, cancel, recentTransactions, noTransactions, noAccounts, loading, viewAll,
                         comingSoonTitle, comingSoonBody}
        ko translations: full Korean translations exist
        zh translations: exist (need verification)

      frontend/components/shell/AppHeader.tsx:
        navigation already wired: {href: '/finances', key: 'finances', icon: Wallet, accent: '#3a5c35'}

    frontend_api_client_pattern:
      # from frontend/lib/api/client.ts
      apiGet<T>(path) → Promise<T>
      apiPost<T>(path, body) → Promise<T>
      apiPatch<T>(path, body) → Promise<T>
      apiDelete<T>(path) → Promise<T>
      # JWT token from localStorage('lifeos_tokens'), CSRF injection for mutations
      # credentials: 'omit', auto-redirect to /login on 401

  ux_contract (from ui_ux_constitution.md §5, binding):
    primary_question: "Where do I stand right now, and what changed recently?"
    default_view: summarized balances, recent transactions with suggested classifications
    hidden_until_intent: full journal tables, import mappings, advanced filters
    good_ux: show drift/variance and next action (confirm, reclassify) as primary;
             tables only behind "review all"

  design_tokens (from DESIGN.md):
    finance_accent_bg: #e8f0e3 (sage)
    finance_accent_dark: #3a5c35 (icon/border on selection only)
    finance_gradient: linear-gradient(135deg, #edf5e8, #d9ebcf)
    card_radius: 0 16px 16px 16px (clipped specimen — sharp TL, rounded rest)
    fonts: Newsreader (headlines, -0.03em tracking, Light 300 for display) | Manrope (body/labels)
    primary: #4b6646 | surface: #f8faf2 | on-surface: #2e342b | on-surface-variant: #5a6157
    surface-container-lowest: #ffffff (cards) | surface-container-low: #f1f5eb (sections)
    surface-container-high: #e5eade (hover) | surface-container-highest: #dee5d7 (secondary buttons)
    outline: #767d72 (placeholder/tertiary) | outline-variant: #adb4a8 (ghost borders 15-20% opacity)
    accent-coral: #e8735c (sparingly: notifications, active states)
    no_line_rule: no 1px borders for sectioning → use bg color shifts only
    shadows: sage-tinted rgba(46,52,43,0.06), never pure grey
    card_hover_shadow: 0 30px 60px rgba(46,52,43,0.08) + translateY(-2px)
    buttons: rounded-full pill shape only, primary gradient 135deg #4b6646→#3f5a3a
    ghost_borders: outline-variant #adb4a8 at 15-20% opacity only when same-bg containers need definition
    glassmorphism: background at 75% opacity, backdrop-filter: blur(8px), 1px solid white at 20% opacity
    padding: 2rem minimum internal card padding

  reference_impl: habits domain Phase 12 (use as structural pattern for):
    card_ux → specimen cards with domain accent on selection only
    master_detail → 60/40 split at ≥1024px, drawer/sheet on mobile
    log_interaction → single-tap primary CTA (LOG button pattern)
    empty_state → motivational onboarding moment, not blank list
    detail_panel → React Query data fetching from /stats, /history endpoints

  my_context:
    currencies_needed: KRW (primary, living costs), MYR (investment portfolio), CNY (potential)
    typical_transactions: rent ₩700k, insurance ₩78k, transport ₩50k, food/daily ₩variable
    income: ₩540k/mo + ₩4.8M biannual (Mar & Sep)
    lending: frequently lends to friends (receivables/debt manager exists)
    financial_goal: ₩12M emergency fund (6 months)

    user_context:
      currencies_needed: KRW (primary), other currencies (potential)
      typical_transactions: rent, insurance, transport, bills, food, clothes, daily
      income: salary, scholarships, allowance, bonus
      lending: lends to/borrow from friends, borrow from bank, loans, debt
      financial_goal: set by user

  breadth_rule: every section → ~20% depth before any section → 80%

  PHASE_1_SCOPE (Chart of Accounts + Account Manager):
    what_exists:
      - finance_account_category + finance_account tables (full schema above)
      - CRUD services (accounting_service.py)
      - ML suggester (suggestion_service.py)
      - Frontend: working AccountList component, seedAccounts flow, account search
    what_this_phase_adds:
      - currency_code field on finance_account (account's default currency)
      - default chart of accounts template for new users (personal finance, not corporate)
      - account type → normal balance mapping (already exists: BASE_TYPE_NORMAL_BALANCE)
      - account deactivation semantics (already exists: is_active flag)
      - account numbering scheme (optional, user-customizable)
      - frontend: enhance account manager with create/edit in drawers, better grouping

    default_account_tree (Opus should refine but start here):
      Asset:
        - Cash & Bank Accounts (checking, savings, cash on hand)
        - Investments (stocks, bonds, ETFs, futures, REITs, CDs)
        - Receivables (money owed to me)
        - Prepaid Expenses (yearly subscriptions, rent, utilities, insurance, etc.)
        - Other Assets
      Liability:
        - Credit Cards
        - Loans (student, personal)
        - Payables (money I owe)
        - Other Liabilities
      Equity:
        - Opening Balance Equity
        - Retained Earnings
        - Other Equity
      Income:
        - Salary & Wages
        - Scholarship/Grants
        - Allowance
        - Bonus
        - Investment Income (dividends, interest)
        - Side Income
        - Other Income
      Expense:
        - Housing (rent, utilities)
        - Food & Dining
        - Transportation
        - Education
        - Personal Care
        - Health & Fitness
        - Entertainment
        - Subscriptions
        - Insurance
        - Gifts & Donations
        - Other Expenses

    account_type_normals:
      Asset: debit-normal (increases with debits)
      Expense: debit-normal
      Liability: credit-normal (increases with credits)
      Income: credit-normal
      Equity: credit-normal

  PHASE_2_SCOPE (Transaction Input + Double-Entry Ledger):
    what_exists:
      - finance_transaction + finance_journal_entry + finance_journal_line tables (full schema above)
      - journal_service.record_transaction() for simple 2-line entries
      - accounting_service.post_journal_entry() for multi-line entries
      - Frontend: working TransactionInputForm (simple + split modes), TransactionList, FinanceSummaryCard
    what_this_phase_adds:
      - currency_code + exchange_rate fields on transactions and journal lines
      - enhanced smart transaction input (UX abstraction layer over double-entry)
      - transaction → journal entry auto-generation rules (extend existing)
      - multi transactions (one payment → multiple accounts/currencies)
      - split transactions (one payment → divide between categories) — partially implemented in frontend
      - transfer transactions (between own accounts, no P&L impact) — placeholder in frontend
      - mutability model (Opus must decide — see MUTABILITY_DECISION below)
      - frontend: complete transfer mode, add edit/void flows, enhance transaction detail

    SMART_TRANSACTION_ABSTRACTION:
      the key UX insight: users think in transactions, the system records in journal entries.
      user inputs: "I paid ₩15,000 for lunch with cash"
      system generates:
        journal_entry:
          line 1: debit Food & Dining ₩15,000
          line 2: credit Cash ₩15,000
      the journal entry is invisible to normal users. they see "Lunch — ₩15,000 from Cash"
      power users can toggle a "Journal View" to see the underlying double-entry.

    TRANSACTION_TYPES:
      simple_expense:
        user provides: amount, description, expense_account, payment_account (asset), date
        auto-generates: debit expense_account, credit payment_account
      simple_income:
        user provides: amount, description, income_account, deposit_account (asset), date
        auto-generates: debit deposit_account, credit income_account
      transfer:
        user provides: amount, from_account (asset), to_account (asset), description, date
        auto-generates: debit to_account, credit from_account
        note: NO income/expense impact — purely balance sheet movement
      multi:
        user provides: total amount, payment_account, date, description
                       list of splits: [{amount, account (asset or expense)}]
        validation: sum of splits must equal total amount
        auto-generates: debit each account for its split amount,
                        credit payment_account for total
        use case: "I paid ₩30,000 for groceries and dining with my card — ₩20k groceries, ₩10k dining"
      split:
        Opus decides the structure.

    MUTABILITY_DECISION:
      Opus must choose one and justify:
        option_a: direct edit
          - user edits transaction → system updates the journal entry in place
          - simpler UX, but loses audit trail
          - pro: much simpler for personal finance (not a regulated business)
          - con: if insights/analytics already consumed the old values, they're stale
        option_b: void + re-enter
          - user "voids" old transaction → system creates reversing journal entry
          - user creates new corrected transaction → new journal entry
          - preserves full audit trail, but complex UX for "I typo'd the amount"
          - pro: accounting purity, audit trail
          - con: over-engineered for personal finance
        option_c: hybrid (recommended consideration)
          - within grace period (e.g., 24-48 hours): direct edit allowed
          - after grace period: void + re-enter
          - pro: best of both worlds
          - con: most complex to implement
      decision_criteria: this is PERSONAL finance, not corporate accounting.
        the user is not audited. simplicity > purity. but don't lose the ability to
        see what changed. Opus should weigh this.
      note: frontend already has updateTransaction() and voidTransaction() API methods defined
            and Transaction type includes is_void, void_of_id, edited_at fields —
            the backend must match these contracts

  CURRENCY_INFRASTRUCTURE:
    new_table: finance_currency
      fields:
        code: VARCHAR(3), PK (ISO 4217: KRW, MYR, CNY, etc.)
        symbol: VARCHAR(10) (₩, RM, ¥, etc.)
        name: VARCHAR(100) ("South Korean Won", "Malaysian Ringgit")
        decimal_places: INTEGER (0 for KRW/JPY, 2 for CNY/MYR)
        is_active: BOOLEAN, default true
      seeded with common currencies on first run

    user_base_currency:
      stored in user_preference (key: "base_currency", value: {"currency": "KRW"})
      the UserPreference model already exists — see schema above
      all summary views aggregate in base currency
      individual transactions display in their original currency

    exchange_rate_storage:
      new_table: finance_exchange_rate
        fields:
          id: PK
          user_id: FK → user (rates are user-scoped for manual entry)
          from_currency: VARCHAR(3), FK → finance_currency
          to_currency: VARCHAR(3), FK → finance_currency
          rate: DECIMAL(19,10) (high precision for FX)
          effective_date: DATE
          source: VARCHAR(20) ("manual" now, "api" later)
          created_at: TIMESTAMP
        index: (user_id, from_currency, to_currency, effective_date)
      note: for Phase 1-2, rates are manual entry only. API integration is Phase 6.

    conversion_semantics:
      at_transaction_time: each transaction stores its currency_code + exchange_rate_to_base
      the exchange_rate_to_base is locked at transaction creation time
      revaluation (Phase 6): periodic recalculation of foreign-currency asset values at current rates
      journal_entry_balance_rule:
        each journal entry must balance WITHIN its currency
        if a journal entry has lines in multiple currencies (e.g., FX conversion),
        a single "FX Gain/Loss" line at the base currency rate resolves the difference
        Opus must specify this precisely — it's the hardest part of multi-currency accounting

    additive_migration_strategy:
      existing amount fields stay as-is (no rename, no drop)
      new fields added alongside:
        finance_transaction: + currency_code VARCHAR(3) DEFAULT 'KRW', + exchange_rate_to_base DECIMAL(19,10) DEFAULT 1.0
        finance_journal_line: + currency_code VARCHAR(3) DEFAULT 'KRW', + exchange_rate_to_base DECIMAL(19,10) DEFAULT 1.0
        finance_account: + default_currency VARCHAR(3) DEFAULT 'KRW'
      existing records retroactively treated as KRW (the default)
      existing tests continue to pass because defaults fill in the new fields

  LAYERING_RULES (from lifeos_architecture.md, binding):
    controllers: HTTP validation, authz only; delegate to services
    services: business logic, invariants, event emission after durable commits
    models: SQLAlchemy + pure data; no cross-domain imports
    schemas: DTO conversion, validation rules
    events: emitted from services after commits; consumed by insights/tasks
    naming: tables prefixed with domain (finance_*); events as domain.resource.action

  EVENT_CATALOG_CHANGES:
    existing events that need payload updates (bump payload_version):
      finance.transaction.created: + currency_code, + exchange_rate_to_base (payload_version: 2)
      finance.journal.posted: + currency_codes[] (list of currencies in the entry) (payload_version: 2)
    new events:
      finance.account.updated → {account_id, user_id, fields, updated_at}
      finance.account.deactivated → {account_id, user_id, deactivated_at}
      finance.transaction.updated → {transaction_id, user_id, fields, updated_at} (if direct edit chosen)
      finance.transaction.voided → {transaction_id, user_id, voided_at, reason?} (if void model chosen)
      finance.exchange_rate.set → {rate_id, user_id, from_currency, to_currency, rate, effective_date}
    note: finance.account.created already exists (see catalog above) — add default_currency to its payload (v2)
    note: no events for currency reference table changes (static reference data)

  MIGRATION_RULES (from lifeos_architecture.md §8):
    single Alembic home: lifeos/migrations/versions/
    current head: 20251224_insight_feed_indexes
    additive-first: new columns nullable/defaulted; new tables allowed
    naming: <timestamp>_<domain>_<short_action>.py
    index_rule: always index user_id plus primary query dimension
    sqlite_compat: DECIMAL(19,4) maps to NUMERIC in SQLite — test with both
    never drop columns, rename tables, or change column types in-place

  CROSS_DOMAIN_INTERFACES (events only, define contracts now for future phases):
    calendar → finance:
      finance.transaction.inferred already exists (see catalog)
      decision_for_opus: does this event need currency_code? if calendar event has no currency
      context, what's the default behavior?
    health → finance (future):
      meal cost tracking: health.nutrition.logged could carry a cost field in future
      but that's a health schema change — for now, just define the event shape
      suggested: finance.expense.linked → {transaction_id, domain, domain_record_id}
    projects → finance (future):
      project expense tracking: same pattern as health
    insights_engine:
      finance_rules.py currently checks raw amount for "finance_spend"
      decision_for_opus: do any rules need updating for currency awareness?
      e.g., "high spend" threshold must be in base currency, not raw amount
    habits → finance (future):
      spending habit tracking: same linking pattern

  EXPLICITLY_CUT (do not include in spec):
    - budget module (Phase 4)
    - recurring transactions (Phase 4)
    - financial statements — IS, BS, CF (Phase 5)
    - multi-currency UI — currency picker, FX rate display, revaluation (Phase 6)
    - analytics, graphs, ratios, benchmarks (Phase 7)
    - receivables/debt manager UI (Phase 8, backend already exists)
    - scenario modeling, goal tracking (Phase 9)
    - CSV/bank statement import (import_api.py exists but not in scope)
    - receipt photo capture
    - tax compliance views
    - approval workflows
    - investment portfolio tracking UI
    - any ERP-grade complexity (approval chains, multi-entity, consolidation)
    - trial balance UI (Phase 3, but data model must support it)
    - money schedule UI (exists in backend, frontend deferred)

  FUTURE_PHASES (do NOT design, but data model must not block):
    | Phase | Module |
    |-------|--------|
    | 3     | Journal Entry Viewer + Trial Balance |
    | 4     | Budget Module + Recurring Transactions |
    | 5     | Financial Statements (IS, BS, CF) |
    | 6     | Multi-currency UI (FX rates, currency picker, revaluation) |
    | 7     | Analytics + Graphs (ratios, trends, benchmarks) |
    | 8     | Receivables/Debt Manager + Receipts |
    | 9     | Scenario Modeling + Goal Tracking |

OBJ: produce a deterministic build spec that Sonnet 4.6 can execute file-by-file in VSCode without improvising

S.T.:
  - output = single markdown document titled "FINANCE_PHASE1_2_BUILD_SPEC.md"
  - spec must cover ALL of these surfaces at ~20% depth:
      1. finance overview page (EXISTING — enhance with currency display, better summary)
      2. account manager (EXISTING AccountList — enhance with create/edit drawers, deactivation)
      3. transaction input — simple mode (EXISTING TransactionInputForm — enhance with transfer mode)
      4. transaction input — split mode (EXISTING — enhance with validation UX)
      5. transaction list + detail (EXISTING TransactionList — add filtering, detail view)
      6. journal entry viewer (progressive disclosure — hidden by default, power user toggle)
      7. finance empty state (EXISTING seed flow — enhance with editorial onboarding moment)
  - BACKEND SPEC must cover:
      1. audit of all 14 existing tables: which need currency fields added?
         for each: table name, new columns, defaults, migration implications
      2. new table: finance_currency (reference data, seeded)
      3. new table: finance_exchange_rate (user-scoped manual rates)
      4. migrations: ordered list, additive-only, backward-compatible
      5. model changes: updated SQLAlchemy models with new columns
      6. schema changes: updated Pydantic DTOs for currency-aware request/response
      7. service changes: transaction → journal entry auto-generation logic,
         split transaction handling, transfer handling, mutability model
      8. controller changes: any new or modified endpoints
         NOTE: frontend already defines these API methods that don't yet have backend routes:
           - GET /api/finance/accounts (list with pagination + filters) — NEEDS BACKEND
           - POST /api/finance/accounts/seed — NEEDS BACKEND
           - GET /api/finance/transactions (list with pagination + filters) — NEEDS BACKEND
           - GET /api/finance/transactions/<id> — NEEDS BACKEND
           - POST /api/finance/transactions/split — NEEDS BACKEND
           - POST /api/finance/transactions/transfer — NEEDS BACKEND
           - PATCH /api/finance/transactions/<id> — NEEDS BACKEND
           - POST /api/finance/transactions/<id>/void — NEEDS BACKEND
      9. event changes: payload version bumps, new events
      10. default chart of accounts seeding logic (service method, called by seed endpoint)
      11. the smart transaction → journal entry mapping engine (the core business logic)
  - for each frontend surface, define:
      file_path | component_name | props_interface (TypeScript) |
      data_source (exact API endpoint from existing backend) |
      layout_rule (responsive breakpoints) |
      design_tokens_used (specific hex values + token names) |
      interaction_pattern (tap targets, transitions, disclosure) |
      mobile_behavior (drawer vs collapse vs stack)
  - for each backend component, define:
      file_path | class/function names | method signatures |
      input/output types | HTTP method + route (for controllers) |
      event emitted (for services)
  - include a BOUNDARIES section:
      forbidden:
        - features listed in EXPLICITLY_CUT above
        - cross-domain imports (except User, UserPreference)
        - dropping or renaming existing columns/tables
        - breaking existing test_finance_*.py tests
        - dense table defaults, always-on forms
        - "You should..." / "You failed to..." / "You must..." tone
        - ERP-grade complexity (approval chains, multi-entity, consolidation)
        - exposing raw journal entries as default view (progressive disclosure only)
        - calorie/health/habit domain work
        - any new insights rules (existing rules may need currency-awareness updates, but no new rules)
      required:
        - read-first hierarchy (observe → decide → act ordering)
        - progressive disclosure (journal entries hidden until explicit intent)
        - calm tone per constitution §9
        - inferred record confirm/reject flow for calendar-sourced transactions
        - domain accent (#e8f0e3/#3a5c35) on selected cards only, not default fill
        - accessibility: 44px min touch targets, ARIA labels, semantic HTML
        - smart transaction input as PRIMARY interface (not raw journal entry form)
        - journal entry mode as SECONDARY, progressively disclosed for power users
        - all monetary amounts store (amount, currency_code) as paired fields
        - default currency from user_preference, overridable per transaction
        - account type → normal balance mapping enforced in journal validation
        - split transaction validation: sum of splits = total
        - transfer transactions: no P&L impact, balance sheet only
        - deactivated accounts: excluded from dropdowns, visible in history
        - editorial Newsreader headlines + Manrope body text
        - specimen card pattern (0 16px 16px 16px radius)
        - no 1px borders — bg color shifts only
        - sage-tinted shadows only, never pure grey
        - pill-shaped buttons only
        - 2rem minimum card padding
        - additive-only migrations with SQLite compatibility
        - event payload versioning on all modified events
        - i18n: all user-visible strings through translation system (en/ko/zh)
  - include a DEPENDENCY_MAP showing build order:
      backend_order:
        1. currency infrastructure (finance_currency table + seed + finance_exchange_rate table)
        2. account model updates (+ default_currency column)
        3. transaction + journal line model updates (+ currency_code, + exchange_rate_to_base)
        4. schema updates (Pydantic DTOs)
        5. service updates (transaction → journal mapping, split handling, transfer handling, void logic)
        6. controller updates (new endpoints to match frontend API client contracts)
        7. event payload version bumps
        8. default chart of accounts seeder
        9. existing test compatibility verification
      frontend_order:
        1. enhance finance empty state + account seeder trigger (already partially works)
        2. enhance account manager (create/edit drawer, deactivation toggle)
        3. complete transaction input — transfer mode (placeholder exists)
        4. enhance transaction input — split mode validation
        5. enhance transaction list + add detail view + filtering
        6. enhance finance overview page (currency-aware summary cards)
        7. add journal entry viewer (power user progressive disclosure)
      frontend depends on: all backend migrations + model updates + new endpoints landed first
  - include API_CONTRACT section listing:
      all existing endpoints that the frontend already consumes
      the GAP endpoints (frontend client methods that have no backend route yet)
      any modified endpoints (with before/after request/response shapes)
      derive from lifeos/domains/finance/ controllers vs frontend/lib/api/finances.ts
  - include COMPONENT_REGISTRY listing every new or modified component with:
      name | location (file path) | responsibility (1 sentence) | max_lines (cap at ~150 for 20% depth)
  - include MUTABILITY_DECISION section:
      Opus must state the chosen option (a/b/c from MUTABILITY_DECISION above)
      justify the decision
      specify exact implementation: what happens to the journal entry on edit/void
      specify the event emitted on edit/void
      note: frontend already expects is_void, void_of_id, edited_at on Transaction
  - include CURRENCY_DECISION section:
      journal_entry_balance_rule: how multi-currency entries balance
      FX gain/loss handling: where does the rounding difference go?
      base currency aggregation: how account balances sum across currencies
      specify precisely — this is the hardest design decision in the spec

OUT:
  format: markdown with clear ## sections
  structure: |
    ## 0. Build Philosophy & Constraints
       - what this feature is and is NOT, emotional contract, breadth-first rule
    ## 1. Currency Infrastructure Decision
       - balance rule, FX handling, base currency aggregation, reference tables
    ## 2. Mutability Decision (with justification)
    ## 3. Existing Table Audit (14 tables — which need changes, which don't)
    ## 4. Backend Spec
       ### 4.1 Migrations (ordered list)
       ### 4.2 Models (new + modified)
       ### 4.3 Schemas (new + modified DTOs)
       ### 4.4 Services (transaction→journal mapping engine, split/transfer logic, void logic)
       ### 4.5 Controllers (API Contract — existing + gap + modified + new)
       ### 4.6 Events (payload version bumps + new events)
       ### 4.7 Default Chart of Accounts Seeder
    ## 5. Frontend Component Registry
    ## 6. Surface Specs (7 surfaces — all partially exist, enhance each)
       - each surface: layout, tokens, interaction, mobile, data source
    ## 7. Cross-Domain Interface Contracts (event shapes for future phases)
    ## 8. Boundaries (forbidden + required — copy from S.T. above)
    ## 9. Dependency Map (build order DAG)
    ## 10. Sonnet Execution Instructions
       - file-by-file checklist with explicit order
       - per-file: "create/modify [path], implement [component], consume [endpoint], max [N] lines"
       - include verification step per file (what to check before moving to next)
  length: 1200-1800 lines (larger than health specs due to currency infrastructure + existing table audit)
  precision: every file path, every prop name, every column name, every token reference,
             every event payload field must be explicit and unambiguous

TONE: architectural specification, not tutorial. assume the reader (Sonnet 4.6) has ZERO prior context about LifeOS, double-entry accounting, or multi-currency semantics — embed all constraints inline so it cannot drift. be specific enough that two different Sonnet instances given this spec would produce structurally identical outputs.
```
