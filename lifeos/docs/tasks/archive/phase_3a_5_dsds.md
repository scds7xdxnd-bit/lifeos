# Phase 3a.5 Domain Surface Definitions (DSD) Pack

Status: Completed (Archived)

---

## Profile (main/profile)
**Domain:** Profile/Auth
**Surface / Page Name:** Profile
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Provide a calm, read-first view of account safety, session posture, and configuration state.

### 2. Primary Question Answered
> "Is my account safe and configured?"

### 3. Intended User State
- Observing

### 4. Primary Action (If Any)
- Action name: None (read-only surface)
- Trigger mechanism: N/A

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Session summary, role summary, security status
#### 5.2 User-Editable Sections
- None on this surface (credential changes are off-surface)

### 6. Authority and Confidence Constraints
- Allowed: factual account/session state
- Must NOT assert: health/behavioral conclusions
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: No

### 8. Data Shape (Human-Facing)
- Account status (system-derived, stable)
- Active sessions count (system-derived, stable)
- Role summary (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure (if session details are expanded)

### 10. Explicit Non-Goals for This Surface
- No account credential changes
- No automation

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Journal (core / non-finance)
**Domain:** Journal
**Surface / Page Name:** Journal
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Provide a calm record of recent notes and reflections without forcing action.

### 2. Primary Question Answered
> "What did I note and how did I feel?"

### 3. Intended User State
- Reflecting

### 4. Primary Action (If Any)
- Action name: Review recent entries
- Trigger mechanism: Button (read-first review)

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Recent entries list, mood/tags summary
#### 5.2 User-Editable Sections
- New entry creation (explicit toggle)

### 6. Authority and Confidence Constraints
- Allowed: factual entry content
- Must NOT assert: conclusions beyond user text
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: Yes (journal entries)

### 8. Data Shape (Human-Facing)
- Entry text (user-entered, stable)
- Tags/mood (user-entered, stable)
- Timestamp (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No ranking
- No automated sentiment scoring

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Projects (index/dashboard)
**Domain:** Projects
**Surface / Page Name:** Projects Dashboard
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Surface active projects and the next meaningful step without exposing full task tables by default.

### 2. Primary Question Answered
> "What is the next meaningful step?"

### 3. Intended User State
- Deciding

### 4. Primary Action (If Any)
- Action name: Review projects
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Project list and next-step summaries
#### 5.2 User-Editable Sections
- New project creation (explicit toggle)
- Task add/manage (explicit per-project toggles)

### 6. Authority and Confidence Constraints
- Allowed: project state and next-step summaries
- Must NOT assert: outcome predictions
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: Yes (project progress)

### 8. Data Shape (Human-Facing)
- Project title/status (user-entered, stable)
- Next task (user-entered, stable)
- Activity timestamps (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No burndown charts by default

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Habits (index/dashboard)
**Domain:** Habits
**Surface / Page Name:** Habits Dashboard
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Present recent adherence signals and today’s plan without judgment.

### 2. Primary Question Answered
> "Did I keep my commitments recently?"

### 3. Intended User State
- Observing

### 4. Primary Action (If Any)
- Action name: Review habits
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Streak and status summaries
#### 5.2 User-Editable Sections
- Log/confirm entry (explicit per-habit toggle)
- New habit creation (explicit toggle)

### 6. Authority and Confidence Constraints
- Allowed: factual streak/log data
- Must NOT assert: moral judgment
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: Yes (habit logs)

### 8. Data Shape (Human-Facing)
- Habit name (user-entered, stable)
- Recent log status (user-entered, stable)
- Streak count (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No scoring or ranking

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Health (index/dashboard)
**Domain:** Health
**Surface / Page Name:** Health Dashboard
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Show baseline health signals and trends without conclusions.

### 2. Primary Question Answered
> "How is my baseline and what needs attention?"

### 3. Intended User State
- Observing

### 4. Primary Action (If Any)
- Action name: Review signals
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Summary trends
#### 5.2 User-Editable Sections
- Log update (explicit toggle)

### 6. Authority and Confidence Constraints
- Allowed: reported metrics
- Must NOT assert: diagnosis
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: Yes (health logs)

### 8. Data Shape (Human-Facing)
- Metric labels (system-derived, stable)
- User-entered values (user-entered, stable)
- Trend snapshots (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No medical recommendations

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Relationships (index/dashboard)
**Domain:** Relationships
**Surface / Page Name:** Relationships Dashboard
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Surface reconnection cues and recent interactions without scoring people.

### 2. Primary Question Answered
> "Who needs attention next?"

### 3. Intended User State
- Reviewing

### 4. Primary Action (If Any)
- Action name: Review reconnection cues
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Reconnection list, recent interactions
#### 5.2 User-Editable Sections
- Add person (explicit toggle)
- Log interaction (explicit per-person toggle)

### 6. Authority and Confidence Constraints
- Allowed: factual interaction history
- Must NOT assert: relationship quality judgments
Confidence rules: Suggestive / Review-only

### 7. Relationship to Insights (If Applicable)
- Displays insights: Yes (reconnect cues)
- Generates evidence: Yes (interaction logs)

### 8. Data Shape (Human-Facing)
- Person name (user-entered, stable)
- Last interaction date (system-derived, stable)
- Reconnect cue (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No ranking or scoring

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Skills (index/dashboard)
**Domain:** Skills
**Surface / Page Name:** Skills Dashboard
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Show current skill practice status and the next practice prompt.

### 2. Primary Question Answered
> "Am I improving and what should I practice next?"

### 3. Intended User State
- Deciding

### 4. Primary Action (If Any)
- Action name: Review practice plan
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Skill summaries and recent sessions
#### 5.2 User-Editable Sections
- New skill creation (explicit toggle)
- Log practice (explicit per-skill toggle)

### 6. Authority and Confidence Constraints
- Allowed: session history
- Must NOT assert: certification or mastery claims
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: Yes (practice logs)

### 8. Data Shape (Human-Facing)
- Skill name (user-entered, stable)
- Session count (system-derived, stable)
- Last practiced date (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No ranking or scoring

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Finance / Journal
**Domain:** Finance
**Surface / Page Name:** Finance Journal
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Provide a precise, read-first ledger of entries and review-required items.

### 2. Primary Question Answered
> "What changed and needs review?"

### 3. Intended User State
- Reviewing

### 4. Primary Action (If Any)
- Action name: Review recent entries
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Recent entries and summaries
#### 5.2 User-Editable Sections
- New entry creation (explicit toggle)

### 6. Authority and Confidence Constraints
- Allowed: exact numbers and dates
- Must NOT assert: inferred categories without review
Confidence rules: Review-only for inferred items

### 7. Relationship to Insights (If Applicable)
- Displays insights: Yes (inferred entries)
- Generates evidence: Yes (ledger entries)

### 8. Data Shape (Human-Facing)
- Entry description, amount (user-entered/imported, stable)
- Occurred date (system-derived, stable)
- Review status (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure
- Review Queue Integration

### 10. Explicit Non-Goals for This Surface
- No auto-classification without review

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Finance / Trial Balance
**Domain:** Finance
**Surface / Page Name:** Trial Balance
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Present read-only balance positions as-of a date with optional rollups.

### 2. Primary Question Answered
> "What is the balance position as of now?"

### 3. Intended User State
- Observing

### 4. Primary Action (If Any)
- Action name: Review balances
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Account balances and rollups
#### 5.2 User-Editable Sections
- Date filters (explicit toggle)

### 6. Authority and Confidence Constraints
- Allowed: exact numeric balances
- Must NOT assert: projections
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: No

### 8. Data Shape (Human-Facing)
- Account name, code, category (system-derived, stable)
- Debit/credit/net (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No edits to balances

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Finance / Receivables
**Domain:** Finance
**Surface / Page Name:** Receivables
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Track receivable principals and entries without mixing with payable flows.

### 2. Primary Question Answered
> "Which receivables need attention?"

### 3. Intended User State
- Reviewing

### 4. Primary Action (If Any)
- Action name: Review trackers
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Tracker list and totals
#### 5.2 User-Editable Sections
- New tracker creation (explicit toggle)
- Add entry (explicit per-tracker toggle)

### 6. Authority and Confidence Constraints
- Allowed: exact amounts and dates
- Must NOT assert: collection likelihood
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: Yes (entries)

### 8. Data Shape (Human-Facing)
- Counterparty, principal (user-entered, stable)
- Entry history (user-entered, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No credit scoring

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Finance / Forecast
**Domain:** Finance
**Surface / Page Name:** Forecast
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Show projected balances driven by scheduled events, with explicit manage mode.

### 2. Primary Question Answered
> "What is my projected cash position?"

### 3. Intended User State
- Observing

### 4. Primary Action (If Any)
- Action name: Refresh forecast
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Forecast table
#### 5.2 User-Editable Sections
- Schedule creation (explicit toggle)
- Schedule edits (explicit manage mode)

### 6. Authority and Confidence Constraints
- Allowed: deterministic projections based on schedule
- Must NOT assert: external cash-flow certainty
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: Yes (scheduled events)

### 8. Data Shape (Human-Facing)
- Schedule rows (user-entered, stable)
- Projected balance by date (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No predictive modeling claims

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Finance / Import
**Domain:** Finance
**Surface / Page Name:** Import 2.0
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Provide a safe preview of import rows before committing.

### 2. Primary Question Answered
> "What will be imported if I proceed?"

### 3. Intended User State
- Reviewing

### 4. Primary Action (If Any)
- Action name: Preview import
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Preview table
#### 5.2 User-Editable Sections
- Upload/select file (explicit toggle)
- Commit import (explicit action)

### 6. Authority and Confidence Constraints
- Allowed: preview errors and validation results
- Must NOT assert: automated corrections
Confidence rules: Review-only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: Yes (imported entries)

### 8. Data Shape (Human-Facing)
- CSV row fields (imported, stable)
- Validation status (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No auto-mapping without review

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Finance / Accounts
**Domain:** Finance
**Surface / Page Name:** Accounts
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Provide a read-only chart of accounts and category reference.

### 2. Primary Question Answered
> "What accounts exist and how are they grouped?"

### 3. Intended User State
- Observing

### 4. Primary Action (If Any)
- Action name: Review accounts
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Account list and balances
#### 5.2 User-Editable Sections
- Category creation (explicit toggle)
- Type filter (explicit toggle)

### 6. Authority and Confidence Constraints
- Allowed: exact account metadata
- Must NOT assert: financial advice
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: No

### 8. Data Shape (Human-Facing)
- Account name, type, category (system-derived, stable)
- Balance (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No automated category changes

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Finance / Transactions
**Domain:** Finance
**Surface / Page Name:** Transactions (redirect to Journal)
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Provide a read-first pointer to the Finance Journal for transaction review.

### 2. Primary Question Answered
> "What changed recently?"

### 3. Intended User State
- Reviewing

### 4. Primary Action (If Any)
- Action name: Review in Journal
- Trigger mechanism: Primary button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Read-first guidance copy
#### 5.2 User-Editable Sections
- None

### 6. Authority and Confidence Constraints
- Allowed: navigation only
- Must NOT assert: transaction details
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: No

### 8. Data Shape (Human-Facing)
- None (navigation)

### 9. Interaction Patterns Used
- Read-First Layout

### 10. Explicit Non-Goals for This Surface
- No data display

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed

---

## Finance / Dashboard (overview)
**Domain:** Finance
**Surface / Page Name:** Finance Dashboard
**Owner:** Product + Frontend
**Phase:** 3a.5
**Status:** Approved
**Last Updated:** 2025-12-13

### 1. Purpose (Non-Negotiable)
Provide a read-first snapshot of balances, recent activity, and near-term forecast.

### 2. Primary Question Answered
> "Where do I stand right now, and what changed recently?"

### 3. Intended User State
- Observing

### 4. Primary Action (If Any)
- Action name: Review transactions
- Trigger mechanism: Button

### 5. Read / Write Boundary
#### 5.1 Read-Only Sections
- Summary tiles, recent transactions, schedule, forecast
#### 5.2 User-Editable Sections
- None on this surface

### 6. Authority and Confidence Constraints
- Allowed: exact summaries and counts
- Must NOT assert: financial advice
Confidence rules: Informational only

### 7. Relationship to Insights (If Applicable)
- Displays insights: No
- Generates evidence: Indirect (via other surfaces)

### 8. Data Shape (Human-Facing)
- Account counts, balances (system-derived, stable)
- Recent transactions (system-derived, stable)
- Forecast snapshots (system-derived, stable)

### 9. Interaction Patterns Used
- Read-First Layout
- Progressive Disclosure

### 10. Explicit Non-Goals for This Surface
- No detailed edits

### 11. Open Questions / Risks
None.


### 12. Approval
- Product: ☑ Approved
- Architecture: ☑ Approved
- Frontend: ☑ Reviewed
- QA: ☑ Reviewed
