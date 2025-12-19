# Domain Semantic Contracts (Phase 2.5)

Canonical source for domain purpose and semantic boundaries.

## Core Domains

### Auth
- Purpose: Authenticate identity and manage access state.
- Asserts: User identity and access changes explicitly requested or enforced.
- Must not infer: No inference about user intent beyond explicit requests.

### Calendar
- Purpose: Capture declared intentions and scheduled commitments.
- Asserts: User- or sync-declared events with time bounds.
- Must not infer: No guarantee that an event occurred; no behavioral certainty.

### Finance
- Purpose: Record financial transactions and ledger state changes.
- Asserts: User-committed ledger/transaction facts.
- Must not infer: No inference about causality or intent beyond recorded fields.

### Habits
- Purpose: Track repeated behaviors and their logs.
- Asserts: User-logged or inferred habit occurrences.
- Must not infer: No assumptions about streaks beyond recorded logs.

### Health
- Purpose: Record biometrics, workouts, and nutrition logs.
- Asserts: User-logged health records or inferred entries.
- Must not infer: No medical conclusions or diagnoses.

### Skills
- Purpose: Track skill definitions and practice sessions.
- Asserts: User-logged practice activity and skill metadata.
- Must not infer: No proficiency claims beyond explicit metrics.

### Projects
- Purpose: Track projects, tasks, and logged work sessions.
- Asserts: User-maintained project/task state changes.
- Must not infer: No performance judgments beyond recorded state.

### Relationships
- Purpose: Track people and interactions.
- Asserts: User-logged interaction facts and contact metadata.
- Must not infer: No subjective relationship judgments.

### Journal
- Purpose: Capture private reflections and mood signals.
- Asserts: User-authored entries and stated mood/tags.
- Must not infer: No mental health diagnosis or hidden intent.

### System
- Purpose: Record system and workflow events required for audit.
- Asserts: Operational and workflow state changes.
- Must not infer: No user intent beyond explicit system actions.

## ML Scope
- ML consumes domain semantics to decide what can be treated as evidence; do not train on claims outside a domain's "Asserts".
- No UI-filtered subsets are valid for training/eval; only canonical event streams and deterministic windows are allowed inputs.
- ML attachment is limited to inference events with explicit logging fields (`model_version`, `payload_version`) as defined in the ML attachment contracts.

## QA Scope
- Verify every required domain has a contract entry (no gaps).
- Validate that purpose/asserts/must_not_infer are non-empty and aligned with domain usage.
- Ensure event and insight contracts do not assert meaning outside these domain boundaries.
