# LifeOS Private Alpha Architecture Cut

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps, Product Ops
**Owner:** LifeOS Architecture
**Status:** Ratified
**Nature:** Binding launch-scope decision package for the private alpha cut

---

## 1. Executive Architecture Decision Summary

- LifeOS private alpha is an **inquiry-first, invite-only, humanized-by-default** product for 10–30 users.
- It is **not** a chatbot, general assistant, or broad life-management suite.
- Alpha goes online with a **narrow Wave 1 domain set**:
  - calendar
  - habits
  - projects
  - skills
- Alpha cross-domain scope is limited to:
  - projects + calendar
  - projects + skills
- The default output is the **humanized brief**. The **canonical technical brief** remains accessible on the same screen.
- The primary product loop is:
  - data readiness
  - ask one structured question
  - read one humanized answer
  - inspect technical support if needed
  - refine or return later
- Broad domain CRUD, public signup, recommendation logic, assistant behavior, causal explanation, and predictive surfaces stay out of alpha.
- Alpha reliability is achieved through scope discipline, explicit feature flags, invite-only rollout, and fallback to narrower inquiry behavior when advanced layers fail.

---

## 2. Alpha Product Thesis

### What LifeOS is
- A structured personal insight system that lets a user ask bounded questions about their own records and receive evidence-based inquiry briefs.

### What LifeOS is not
- Not a chatbot
- Not an AI companion
- Not a general productivity operating system
- Not an autonomous coach
- Not a recommendation engine

### Core user value loop
1. User gets enough relevant personal data into one or more live alpha domains.
2. User asks one structured question.
3. LifeOS returns one humanized answer with visible technical grounding.
4. User decides whether to trust it, inspect it, refine it, or return later.

### Single most important alpha hypothesis
- Users will repeatedly return to a non-chat, evidence-based inquiry product if the answers are human-readable, grounded, and narrow enough to trust.

---

## 3. Alpha User Flow

### 3.1 Invite acceptance
- User goal: gain access to the alpha.
- System behavior: verify one-time invite token and show product framing before registration.
- Required inputs:
  - invite token
  - invited email
- Required outputs:
  - valid invite acceptance screen
  - blocked screen for invalid/expired invite
- Failure states:
  - invalid token
  - expired token
  - invite already used
- Fallback states:
  - support/contact path
  - resend invite flow handled by Product Ops/Admin

### 3.2 Account creation / login
- User goal: create an account and securely sign in.
- System behavior: allow registration only from a valid invite; reuse existing auth flow for login and password reset.
- Required inputs:
  - email
  - password
  - display name
  - accepted invite token
- Required outputs:
  - account created
  - authenticated session
- Failure states:
  - duplicate email
  - invalid password rules
  - expired invite at submission time
  - auth failure
- Fallback states:
  - password reset
  - support path for invite/auth issues

### 3.3 Onboarding
- User goal: understand what LifeOS does and get ready to ask a first question.
- System behavior:
  - explain product scope in plain language,
  - collect timezone,
  - show supported alpha domains,
  - route user into data readiness.
- Required inputs:
  - timezone
  - selected live domains of interest
  - optional calendar connect
- Required outputs:
  - onboarding completion state
  - readiness summary
- Failure states:
  - timezone missing
  - no live domain selected
  - calendar connect failure
- Fallback states:
  - manual-setup path
  - onboarding can be resumed later

### 3.4 Initial data readiness assumptions
- User goal: reach a state where inquiry is worth using.
- System behavior:
  - compute readiness only across alpha-live domains,
  - require at least one Wave 1 domain with minimally usable recent data before enabling full inquiry.
- Minimum readiness rule:
  - at least one Wave 1 domain with recent usable records
  - or one approved cross-domain pair with usable records on both sides
- Required inputs:
  - existing records or successful calendar sync/manual setup
- Required outputs:
  - ready
  - not ready yet
- Failure states:
  - zero usable records
  - sync incomplete
- Fallback states:
  - show exact next setup step
  - allow browsing onboarding/help, but do not expose full inquiry as if it were ready

### 3.5 First inquiry creation
- User goal: ask one meaningful structured question.
- System behavior:
  - present inquiry form with alpha-supported domains/pairs only,
  - provide question examples,
  - allow timeframe presets,
  - allow optional context text.
- Required inputs:
  - question
  - domain or approved pair
  - timeframe preset
  - optional context
- Required outputs:
  - inquiry submitted
  - loading state
- Failure states:
  - unsupported domain/pair
  - empty or invalid question
  - readiness not met
- Fallback states:
  - inline validation
  - suggestions to narrow scope or complete readiness first

### 3.6 Inquiry results view
- User goal: understand the answer quickly.
- System behavior:
  - show humanized brief first,
  - keep technical brief expandable,
  - preserve evidence traceability,
  - show refine and feedback actions.
- Required inputs:
  - successful inquiry generation
- Required outputs:
  - humanized brief
  - technical brief access
  - evidence references
- Failure states:
  - inquiry generation error
  - humanization failure
  - insufficient evidence
- Fallback states:
  - canonical brief fallback if humanization fails
  - insufficiency result instead of broken answer
  - retry action with preserved draft

### 3.7 Humanized brief view
- User goal: quickly understand what happened and why it matters.
- System behavior:
  - show short humanized explanation with plain-language sections,
  - keep confidence and limitations visible.
- Required outputs:
  - what stands out
  - why it matters
  - how sure this is
  - what to review next
- Failure states:
  - fallback-to-canonical mode
- Fallback states:
  - render canonical brief as primary with explicit notice

### 3.8 Technical brief / evidence trace view
- User goal: verify and inspect support.
- System behavior:
  - allow expansion on the same results page,
  - show canonical findings, evidence refs, limitations, and metadata.
- Required outputs:
  - technical brief block
  - evidence trace links/references
- Failure states:
  - technical expansion unavailable
- Fallback states:
  - show canonical summary with evidence list at minimum

### 3.9 Refine-question flow
- User goal: get a better answer without starting over.
- System behavior:
  - allow refine from results screen,
  - preserve previous inquiry context,
  - suggest narrower or clearer follow-up.
- Required inputs:
  - same inquiry with modified question/timeframe/context
- Required outputs:
  - new inquiry version
  - linked history entry
- Failure states:
  - invalid refinement
  - unsupported pair/domain after refinement
- Fallback states:
  - preserve prior valid inputs
  - present refine guidance rather than error-only response

### 3.10 Feedback submission
- User goal: tell the system whether the result was useful or confusing.
- System behavior:
  - capture explicit feedback from results page only,
  - attach it to inquiry result/version metadata.
- Required inputs:
  - feedback type
  - optional note
- Required outputs:
  - feedback acknowledged
- Failure states:
  - submission failure
  - duplicate submission
- Fallback states:
  - non-blocking retry
  - result page remains usable

### 3.11 History / revisit flow
- User goal: return to prior inquiries and compare past answers.
- System behavior:
  - show inquiry history with title, scope, date, and status,
  - allow reopen of result page.
- Required outputs:
  - history list
  - reopen action
- Failure states:
  - empty history
  - history fetch error
- Fallback states:
  - empty-state guidance
  - retry option

---

## 4. UI / UX Structure

### Primary navigation
- Inquiry
- History
- Data
- Account / Help

### Screens that exist in alpha
- Invite acceptance
- Account creation / login / reset
- Onboarding + data readiness
- Inquiry creation page
- Inquiry results page
- History page
- Data page
- Account / Help page

### Screens hidden from ordinary alpha users
- Broad domain CRUD pages as primary navigation
- Insights feed as a user-facing primary home
- Admin dashboards
- Experimental ML / model-debug surfaces

### Inquiry page structure
- Orientation header
- Supported domain/pair selector
- Timeframe preset selector
- Question input
- Optional context input
- Primary CTA: Generate brief
- Secondary help/example prompts

### Results page structure
- Header with inquiry question, scope, timeframe
- Humanized brief block as primary
- Technical brief expansion as secondary
- Evidence preview / trace links
- Refine control
- Feedback control

### Technical brief layout
- Collapsed by default
- Canonical summary
- Findings
- Evidence references
- Confidence / answerability
- Limitations
- Technical metadata

### Refine flow layout
- Same page, inline or drawer-based
- Previous question retained
- Scope/timeframe/context editable
- One primary CTA: Regenerate

### History view
- Lightweight list, not analytics dashboard
- Inquiry title
- domain/pair
- timestamp
- status
- reopen action

### Feedback capture UI
- Small explicit control on results page
- Positive/negative/usefulness-oriented options only
- Optional note field
- Non-blocking

### Onboarding / explanation surfaces
- product thesis
- supported alpha domains
- how inquiry works
- what technical brief means
- why unsupported features are hidden

### Empty states
- No data ready
- No inquiry history
- No supported cross-domain pair data

### Error states
- Invite invalid
- Login/auth failure
- Inquiry generation failure
- Humanization fallback
- Feedback submission failure

### Loading states
- Inquiry generation
- Humanization render
- Data readiness check
- Calendar sync connection state

### Visual priority decisions
- Primary:
  - inquiry create
  - humanized result
  - clear refine path
- Secondary:
  - technical brief
  - evidence detail
  - history access
- Hidden:
  - machine-facing domain management depth
  - broad operational/admin detail

---

## 5. Alpha Domain Scope

### Wave 1: live in alpha

#### Calendar
- Reason:
  - strongest low-friction data readiness path
  - rich temporal value
  - already central to current architecture
- Risk: scheduled intent vs completed behavior confusion
- Decision: live, but phrasing must preserve plan-vs-actual distinction

#### Habits
- Reason:
  - structured
  - interpretable
  - low onboarding burden
  - good timeline value
- Risk: moralizing adherence language
- Decision: live

#### Projects
- Reason:
  - structured
  - high question quality
  - useful cross-domain pairing with calendar and skills
- Risk: productivity-judgment drift
- Decision: live

#### Skills
- Reason:
  - structured
  - low emotional risk
  - valuable for cadence questions
- Risk: overclaiming improvement
- Decision: live

### Wave 2: hidden / disabled by default

#### Finance
- Reason:
  - useful, but high onboarding burden and sensitivity
  - more failure-prone if chart-of-accounts quality is weak
- Decision: hidden for alpha users; keep off the primary product surface

#### Journal
- Reason:
  - valuable, but phrasing risk remains high for early trust
  - emotionally sensitive
- Decision: hidden for alpha users pending stronger tone validation

### Later: not part of alpha

#### Health
- Reason:
  - highest clinical/interpretive risk
  - stronger sensitivity and tone-control burden
- Decision: not part of private alpha

#### Relationships
- Reason:
  - high sensitivity
  - inferred social meaning risk
- Decision: not part of private alpha

### Alpha cross-domain scope
- Live:
  - projects + calendar
  - projects + skills
- Hidden:
  - all other approved pairs

---

## 6. Core Feature Scope

### Must-have

#### Structured inquiry submission
- Purpose: core input mechanism
- User value: ask one clear question
- Backend dependency: inquiry orchestration
- Required for alpha launch: yes
- Feature-flagged: yes

#### Insight brief generation
- Purpose: produce answer
- User value: core value loop
- Backend dependency: canonical inquiry pipeline
- Required: yes
- Feature-flagged: yes

#### Humanized brief view
- Purpose: ordinary-user-readable default output
- User value: comprehension
- Backend dependency: Phase 10 humanization
- Required: yes
- Feature-flagged: yes

#### Technical brief transparency
- Purpose: trust and auditability
- User value: inspect support
- Backend dependency: canonical brief persistence
- Required: yes
- Feature-flagged: yes

#### Refinement of questions
- Purpose: improve answer without restart
- User value: iterability
- Backend dependency: inquiry versioning
- Required: yes
- Feature-flagged: yes

#### History of prior inquiries
- Purpose: revisit and compare
- User value: continuity
- Backend dependency: inquiry persistence
- Required: yes
- Feature-flagged: yes

#### Timeline interpretation
- Purpose: answer change-over-time questions for Wave 1
- User value: pattern understanding
- Backend dependency: Phase 9
- Required: yes
- Feature-flagged: yes

#### Output feedback collection
- Purpose: learn what is useful or unclear
- User value: user has a voice in alpha
- Backend dependency: feedback persistence
- Required: yes
- Feature-flagged: yes

### Should-have

#### Bounded cross-domain analysis
- Purpose: show pair-value without breadth explosion
- User value: higher-value synthesis in a narrow lane
- Backend dependency: Phase 8
- Required: should-have
- Feature-flagged: yes

#### Data readiness page
- Purpose: reduce bad first inquiries
- User value: clear setup path
- Backend dependency: readiness evaluator
- Required: should-have
- Feature-flagged: yes

#### Calendar sync for alpha
- Purpose: low-friction data acquisition
- User value: faster time-to-first-value
- Backend dependency: existing calendar sync
- Required: should-have
- Feature-flagged: yes

### Deferred
- general insights feed as primary user home
- broad domain browsing
- recommendation surfaces
- automation/write actions
- assistant-style exploratory interaction

---

## 7. Explicit Non-Goals

### Open-ended chat
- Excluding it protects product positioning and prevents assistant drift.

### Autonomous coaching or recommendation engine
- Excluding it preserves trust and avoids overclaiming during alpha.

### Write actions / automation
- Excluding it lowers operational and product risk.

### Broad domain coverage
- Excluding it keeps onboarding, QA, and failure modes manageable.

### Public signup
- Excluding it preserves rollout discipline and support quality.

### Mobile app
- Excluding it avoids product and engineering fragmentation.

### Rich frontend framework migration
- Excluding it preserves launchability and low operational burden.

### Experimental ML user surfaces
- Excluding them protects determinism and scope clarity.

### User-facing admin dashboards
- Excluding them keeps the product inquiry-first rather than ops-first.

---

## 8. Backend Architecture Requirements

### Required services
- invite validation / invite issuance support
- auth using existing session/JWT stack
- onboarding readiness evaluator
- inquiry orchestration
- Phase 9 timeline layer for Wave 1
- Phase 10 humanization layer
- inquiry history service
- explicit inquiry feedback service
- feature-flag evaluation

### Required modules
- invite/access module or additive auth extension
- readiness service under inquiry or onboarding boundary
- humanization service
- alpha-gating service for visible domains/pairs
- feedback linkage to inquiry result/version

### Required persistence behavior
- persist inquiry requests and versions
- persist canonical briefs
- persist humanization version/hash linkage
- persist explicit feedback linked to inquiry result/version
- persist invite and invite-use state if not already present

### Required job / worker behavior
- existing worker/outbox remains sufficient
- calendar sync remains background-capable
- no new heavy background architecture required for alpha

### Required auth behavior
- invite-only registration
- existing login/reset semantics preserved
- no public signup path

### Required role / access model
- `alpha_user`
- `admin`
- ordinary alpha users do not access admin or broad operational surfaces

### Required logging / audit behavior
- invite accepted / rejected
- onboarding completed / blocked
- inquiry requested / generated / viewed / refined
- humanization fallback events
- technical brief expansion
- feedback submitted

### Required observability
- readiness completion rate
- inquiry generation latency
- insufficiency rate
- humanization failure/fallback
- feedback rate
- active alpha user count
- cross-domain usage rate

### Required feature flags
- `ENABLE_PRIVATE_ALPHA`
- `ALPHA_INVITE_ONLY`
- `ALPHA_MAX_USERS`
- `ALPHA_VISIBLE_DOMAINS`
- `ALPHA_ENABLED_CROSS_DOMAIN_PAIR_PROFILES`
- `ALPHA_ENABLE_TECHNICAL_BRIEF`
- `ALPHA_ENABLE_HISTORY`
- `ALPHA_ENABLE_INQUIRY_FEEDBACK`
- `ALPHA_HIDE_DOMAIN_CRUD`
- `ALPHA_REQUIRE_DATA_READINESS`
- `ALPHA_ENABLE_CALENDAR_SYNC`
- existing inquiry/timeline/humanization feature flags remain authoritative

### Required migrations / schema expectations
- additive only
- invite token/state persistence if needed
- inquiry feedback linkage if existing substrate does not already provide result/version linkage
- no destructive launch migrations

### Backend complexity to postpone
- public-scale rate limiting strategy beyond current stack
- complex role hierarchies
- separate API gateway
- multi-tenant org support
- large-scale async orchestration

---

## 9. Contracts

### A. UI ↔ Backend contracts

#### Request / response expectations
- Server-rendered pages remain primary.
- API JSON remains secondary for testing, observability, and future integrations.
- UI forms must receive stable template inputs for:
  - user readiness state
  - supported domains/pairs
  - question draft
  - result status
  - humanized brief
  - technical brief
  - feedback options

#### Error response structure
- User-facing errors must return:
  - stable error code
  - plain-language message
  - retryable boolean
  - fallback action if available

#### Loading and retry expectations
- Inquiry generation and humanization states must be explicitly represented.
- Retry must preserve valid draft inputs.

### B. Inquiry contract

#### Allowed inquiry types
- single-domain inquiry for Wave 1 domains only
- approved alpha cross-domain pair inquiry only

#### Required fields
- question
- domain or approved pair
- timeframe preset

#### Optional fields
- context text
- explicit `as_of_ts` only for replay/testing/admin paths, not ordinary alpha UI

#### Validation rules
- question required
- unsupported domains rejected at validation
- unsupported pairs rejected at validation
- timeframe must be one of the alpha presets:
  - 7 days
  - 30 days
  - 90 days
- context length bounded

#### Refusal / insufficiency behavior
- If unsupported: return blocked/unsupported state
- If not enough data: return insufficiency state with next setup step
- No assistant-style refusal prose

### C. Results contract

#### Valid result must contain
- inquiry id/version
- result status
- humanized brief
- technical brief
- evidence trace access
- limitations
- confidence visibility
- refine affordance
- feedback affordance

#### Humanized brief structure
- direct answer
- what stands out
- why it matters
- how sure this is
- what to review next
- brief limitation note

#### Technical brief structure
- canonical summary
- findings
- evidence refs
- confidence labels
- answerability / insufficiency status
- technical metadata
- timeline metadata when applicable

#### Evidence trace expectations
- Evidence presence must be visible from the results page.
- Full evidence detail may live in the technical brief expansion.

#### Insufficiency / blocked-claim behavior
- Must render as first-class result states, not generic errors.

### D. Feedback contract

#### Allowed feedback types
- helpful
- unclear
- too_technical
- too_long
- incorrect
- not_useful_yet
- other

#### Required metadata
- inquiry id
- inquiry version / result version
- canonical brief hash
- humanization version
- current surface (`humanized` or `technical`)
- feedback type

#### Optional metadata
- short note

### E. Feature flag contract

#### Flags gating user-visible behavior
- `ENABLE_PRIVATE_ALPHA`
  - gates the alpha shell itself
- `ALPHA_INVITE_ONLY`
  - gates public access off
- `ALPHA_VISIBLE_DOMAINS`
  - gates UI-visible domains
- `ALPHA_ENABLED_CROSS_DOMAIN_PAIR_PROFILES`
  - gates UI-visible pair scope
- `ALPHA_ENABLE_TECHNICAL_BRIEF`
  - gates technical brief visibility
- `ALPHA_ENABLE_HISTORY`
  - gates history page
- `ALPHA_ENABLE_INQUIRY_FEEDBACK`
  - gates results-page feedback controls
- `ALPHA_HIDE_DOMAIN_CRUD`
  - hides broad domain management surfaces
- `ALPHA_REQUIRE_DATA_READINESS`
  - blocks full inquiry before minimum readiness

#### Default values for alpha
- `ENABLE_PRIVATE_ALPHA=true`
- `ALPHA_INVITE_ONLY=true`
- `ALPHA_MAX_USERS=30`
- `ALPHA_VISIBLE_DOMAINS=calendar,habits,projects,skills`
- `ALPHA_ENABLED_CROSS_DOMAIN_PAIR_PROFILES=projects_calendar_v1,projects_skills_v1`
- `ALPHA_ENABLE_TECHNICAL_BRIEF=true`
- `ALPHA_ENABLE_HISTORY=true`
- `ALPHA_ENABLE_INQUIRY_FEEDBACK=true`
- `ALPHA_HIDE_DOMAIN_CRUD=true`
- `ALPHA_REQUIRE_DATA_READINESS=true`

---

## 10. Operational Alpha Boundaries

### Invite-only model
- Mandatory
- No public registration path

### Account approval logic
- Access only through issued invite tokens
- Product Ops/Admin controls invite issuance

### User cap assumptions
- Hard cap: 30 users
- Soft initial cohort: 10 users or fewer

### Admin privileges
- Internal only
- Admin can issue invites, inspect rollout/ops state, and support account problems

### Support / feedback collection path
- In-product explicit feedback on results page
- Support/contact path from onboarding and account/help

### Safe rollout sequence
1. Internal team
2. 3 concierge users
3. 10 users
4. 30 users max

### What happens if a feature fails in production
- humanization failure → canonical fallback
- cross-domain failure → narrower inquiry or blocked state
- timeline failure → non-timeline inquiry output
- feedback failure → non-blocking retry path

### Rollback expectations
- Roll back by narrowing feature flags first, not by broad platform changes.
- Do not substitute assistant/chat behavior as fallback.

### Required metrics / events
- invites issued / accepted / failed
- onboarding started / completed / blocked
- readiness passed / not-ready
- inquiry requested / generated / viewed / refined
- humanization render / fallback / failure
- technical brief expansions
- feedback submissions
- active users

---

## 11. Documentation Changes Required

### `lifeos/docs/lifeos_architecture.md`
- Add:
  - binding private alpha cut
  - domain wave decisions
  - inquiry-first alpha surface
- Change:
  - current phase focus to alpha implementation
- Deprecate:
  - assumption that broad domain exposure is the default user-facing mode
- Remove contradictions:
  - any language that implies assistant or broad dashboard positioning

### `lifeos/docs/ui_ux_constitution.md`
- Add:
  - alpha inquiry-first navigation and hidden-surface rules
- Change:
  - make minimal alpha nav explicit
- Remove contradictions:
  - any implied equal weighting of many product surfaces for alpha

### `lifeos/docs/tasks/private_alpha_architecture_cut.md`
- Add:
  - this full decision package

### `lifeos/docs/ops/private_alpha_launch_ops.md`
- Add:
  - alpha rollout flags
  - user-cap rules
  - fallback and rollback expectations

### `.env.example`
- Add:
  - alpha feature flags and scope controls

### `lifeos/docs/tasks/phase_10_insight_humanization_layer.md`
- Change:
  - note that humanized-by-default is a launch requirement for alpha, not a generic future ideal

### Semantics docs
- No mandatory semantic change for alpha cut itself.
- Only update semantic registries if implementation introduces new invite or inquiry-feedback event types beyond current contracts.

---

## 12. Final Architect Decision List for Downstream Teams

### Must-have
- Invite-only alpha
- Inquiry-first navigation
- Humanized-by-default results
- Technical brief access on same page
- Wave 1 domains only:
  - calendar
  - habits
  - projects
  - skills
- Alpha cross-domain only:
  - projects + calendar
  - projects + skills
- History
- Refine flow
- Explicit feedback
- Data readiness gating

### Should-have
- Calendar sync as the fastest readiness path
- Concierge onboarding support
- Narrow canary rollout by user cohort

### Deferred
- Finance as alpha-visible
- Journal as alpha-visible
- Health and relationships
- Public signup
- Open-ended chat
- Recommendations
- Causality
- Prediction
- Broad domain management UI
- Rich frontend rewrite

### Final binding product stance
- LifeOS alpha is a private, structured inquiry product with human-readable answers and technical traceability.
- It is not an AI assistant.
