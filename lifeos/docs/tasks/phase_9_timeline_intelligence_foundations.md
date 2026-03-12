# LifeOS - Phase 9: Timeline Intelligence Foundations

**Audience:** Architecture, Backend, Frontend, DB, QA, DevOps, ML (contracts-only)
**Owner:** LifeOS Architecture
**Preconditions:** Phase 8.1 complete and governance-aligned
**Status:** Approved to Open
**Nature:** Deterministic temporal pattern interpretation (observational, non-causal, non-predictive)

---

## SECTION 1 — Phase 8.1 Postmortem

### 1.1 What inquiry now does well
- Inquiry is now strong at bounded, scoped, evidence-cited answers.
- Domain expert briefs can answer domain-specific questions with deterministic structure and explicit limitations.
- Approved cross-domain pairs can describe co-occurrence, alignment, and coverage gaps without collapsing into assistant narrative.
- Productization improved direct answers, relevance ordering, answerability visibility, and refine usefulness.

### 1.2 What inquiry still cannot do because temporal intelligence is missing
- It cannot reliably distinguish a one-window event from a recurring pattern.
- It cannot say whether a recent change is new, sustained, weakening, or reverting.
- It cannot compare the current window to a stable historical baseline in a replay-safe way.
- It cannot distinguish density bursts from true continuity.
- It cannot robustly answer whether the present period is typical relative to prior comparable periods.

### 1.3 Why productized inquiry is still limited without timeline reasoning
- Phase 8.1 made answers clearer, not deeper in temporal structure.
- A clearer bounded-window answer is still limited if the underlying system cannot compare windows or classify pattern persistence.
- Decision usefulness plateaus when the system can only summarize "what is in the box" and not "how this box relates to prior boxes."

### 1.4 Weakly supported user questions today
- "Is this becoming more frequent or was this just a busy week?"
- "Has this pattern been stable or is it drifting?"
- "Is this a recurring rhythm or a recent spike?"
- "Did this alignment show up only once or across multiple windows?"
- "Is this current period unusual relative to my recent history?"

### 1.5 Wrong next move
- The wrong next move is to add recommendations, causal explanation, or prediction before the system can safely describe temporal structure.
- That would force LifeOS to overclaim on top of shallow time modeling.

### 1.6 Bounded-window reasoning vs temporal pattern reasoning
- Bounded-window reasoning: summarizes evidence inside one explicitly selected interval.
- Temporal pattern reasoning: compares multiple fixed, comparable intervals to classify recurrence, persistence, drift, stability, escalation, and episodic behavior.
- LifeOS has the first capability already. Phase 9 adds the second without exceeding observational limits.

---

## SECTION 2 — Phase Decision

### Decision
- Choose **A) Phase 9 — Timeline Intelligence Foundations**.

### Why this is correct now
- Recommendations need temporal priors to avoid reacting to noise.
- Causal explanation needs temporal ordering discipline plus stronger confound boundaries than LifeOS currently has.
- Predictive work needs stable, replay-safe temporal features and labeled evaluation windows first.
- Timeline intelligence materially increases user value now while preserving current constitutional guardrails.

### Why the alternatives are premature
- **Recommendation Layer** is premature because the system cannot yet robustly distinguish episodic noise from sustained change.
- **Causal Explanation Layer** is premature because LifeOS does not yet have the temporal substrate required to separate sequence from cause.
- **Predictive Modeling Foundations** are premature because stable temporal features, baseline policies, and replay-safe comparison windows are not yet frozen.

---

## SECTION 3 — Problem Definition

### 3.1 Product problem
- Bounded-window summaries answer what happened in one scope, but users also need to know whether the current window is new, typical, recurring, drifting, stabilizing, or sustained.
- Without temporal interpretation, LifeOS can surface facts and pairwise alignment but cannot yet explain pattern shape over time.

### 3.2 Architecture problem
- Temporal reasoning is currently implicit, inconsistent, or absent across strategies.
- If time interpretation is added ad hoc inside domain strategies, replay stability, semantic safety, and contract consistency will drift.
- LifeOS needs one shared deterministic timeline layer so every temporal claim uses the same window rules, ordering rules, baseline rules, and insufficiency thresholds.

### 3.3 Missing pattern classes today
- Recurrence
- Continuity and break
- Relative increase / decrease across comparable windows
- Baseline-relative drift
- Stability vs volatility
- Episodic vs sustained presence
- Cross-window persistence of approved cross-domain alignment

### 3.4 Why this must precede recommendation or causal reasoning
- Recommendation without temporal grounding degenerates into reactive nudging.
- Causal language without stable temporal interpretation becomes narrative overreach.
- Prediction without frozen time semantics cannot be trusted, reproduced, or evaluated honestly.

### 3.5 Definition: timeline intelligence in LifeOS terms
- Timeline intelligence is deterministic temporal interpretation over canonical evidence using fixed historical windows and replay-stable comparison rules.
- It remains:
  - deterministic,
  - observational,
  - evidence-bounded,
  - non-predictive,
  - non-causal.

---

## SECTION 4 — Phase Goal

### Goal
- Add deterministic temporal pattern interpretation so LifeOS can reason about recurrence, drift, stability, escalation, and change over time without introducing causal or predictive claims.

### What gets better
- Inquiry can answer change-over-time questions with explicit window comparisons.
- Domain and approved-pair briefs can distinguish recent-only activity from sustained patterns.
- Users can see whether present behavior differs from prior comparable periods or a fixed baseline.

### What does not change
- Inquiry remains read-first, brief-first, and non-chat.
- Evidence references remain mandatory.
- Confidence vocabulary remains unchanged.
- User context remains non-evidence unless independently supported.

### What remains forbidden
- Recommendations
- Causal explanation
- Prediction / forecasting
- Diagnosis or pathology framing
- Hidden personalization or runtime ML scoring

---

## SECTION 5 — Timeline Intelligence Capabilities

### In scope now

#### 5.1 Recurrence detection
- Meaning: whether a pattern appears across multiple comparable windows rather than only once.
- Evidence used: canonical domain facts bucketed into fixed windows.
- Not allowed to imply: inevitability, habit identity, or future continuation.

#### 5.2 Streak continuity / break detection
- Meaning: whether repeated observations continue across adjacent buckets or whether continuity was interrupted.
- Evidence used: date-anchored discrete observations in domains where continuity is semantically safe.
- Not allowed to imply: failure, regression of character, or causal explanation.

#### 5.3 Recent-window vs prior-window comparison
- Meaning: whether the active comparable window is higher, lower, denser, or flatter than the immediately preceding equal-duration window.
- Evidence used: fixed window counts, sums, or safe domain-specific aggregates.
- Not allowed to imply: trend continuation, recommendation, or causal source.

#### 5.4 Baseline comparison
- Meaning: whether the active comparable window differs from a fixed set of prior comparable windows.
- Evidence used: deterministic baseline windows defined by profile policy and `as_of_ts`.
- Not allowed to imply: abnormality, diagnosis, or judgment.

#### 5.5 Trend direction
- Meaning: direction across a fixed run of comparable closed windows, expressed as increase, decrease, or mixed/flat.
- Evidence used: ordered window series built from canonical evidence only.
- Not allowed to imply: forecast, momentum, or future trajectory.

#### 5.6 Volatility / instability
- Meaning: variability of a safe metric across comparable windows.
- Evidence used: dispersion across fixed windows or buckets.
- Not allowed to imply: pathology, unreliability of character, or clinical interpretation.

#### 5.7 Episodic vs sustained distinction
- Meaning: whether observations appear as bursts/clusters or as repeated presence across many windows.
- Evidence used: bucket occupancy and density over the selected comparison horizon.
- Not allowed to imply: root cause or permanence.

#### 5.8 Drift from established baseline
- Meaning: a stable relative shift from a fixed prior baseline, expressed descriptively.
- Evidence used: baseline-relative comparisons using deterministic windows only.
- Not allowed to imply: diagnosis, recommendation, or one-way progression.

#### 5.9 Temporal alignment persistence across windows
- Meaning: for already approved domain pairs only, whether a pairwise alignment pattern persists across multiple comparable windows rather than appearing only once.
- Evidence used: same-window pairwise observations from approved Phase 8 pairs using shared window semantics.
- Not allowed to imply: causality, intervention priority, or hidden dependency.

### Out of scope for Phase 9
- Standalone density/clustering visual analytics as a user-facing feature
- 3+ domain temporal synthesis
- Sequence mining for causal interpretation
- Predictive extrapolation

---

## SECTION 6 — Architectural Scope

### 6.1 New shared layer
- Introduce a shared deterministic timeline layer at `lifeos/core/timeline/`.
- This is a new intermediate layer, not a direct extension of productization and not a replacement for inquiry strategies.
- Temporal claims must flow through this layer before brief assembly.

### 6.2 Proposed structure
```text
lifeos/core/timeline/
├── semantics.py
├── contracts.py
├── registry.py
├── feature_builder.py
├── window_comparator.py
├── baseline_estimator.py
├── recurrence_engine.py
├── drift_detector.py
├── summary_assembler.py
└── adapters/
    ├── finance.py
    ├── habits.py
    ├── projects.py
    ├── skills.py
    ├── calendar.py
    ├── health.py
    ├── journal.py
    └── relationships.py
```

### 6.3 Component responsibilities
- `semantics.py`: canonical time boundary law, timezone capture, bucket selection, ordering.
- `contracts.py`: `TimelineRequest`, `TimelineWindowSpec`, `TimelineSummary`, `TimelinePattern`, `TimelineCoverage`, `TimelineProfileToken`.
- `registry.py`: allowlisted single-domain and approved-pair timeline profiles with versioning.
- `feature_builder.py`: maps canonical evidence into normalized temporal buckets/features.
- `window_comparator.py`: active vs prior-window comparison using equal-duration windows.
- `baseline_estimator.py`: fixed prior-window baseline generation and coverage evaluation.
- `recurrence_engine.py`: recurrence, continuity, break, sustained-vs-episodic classification.
- `drift_detector.py`: baseline-relative change and stability/volatility descriptors.
- `summary_assembler.py`: generates bounded temporal findings with provenance, limits, and temporal metadata.
- `adapters/`: read-only domain-specific normalization rules; they do not change domain semantics or emit events.

### 6.4 Connection to existing inquiry architecture
- Inquiry request normalization stays where it is.
- Existing evidence gathering stays authoritative for source eligibility.
- After evidence gathering, inquiry invokes the timeline layer when:
  - the question or profile requires temporal interpretation,
  - the selected domain or approved pair has a Phase 9 timeline profile.
- Domain strategies and approved-pair strategies consume `TimelineSummary` outputs instead of performing free-form time comparisons themselves.
- Productization remains the final shaping layer after temporal findings have already been constrained.

### 6.5 Shared layer vs domain-specific temporal adapters
- Shared layer owns:
  - window rules,
  - comparison logic,
  - baseline policy,
  - recurrence/drift semantics,
  - insufficiency rules,
  - replay identity.
- Domain adapters own:
  - canonical anchor field selection,
  - safe bucket metric selection,
  - domain-specific eligibility rules for temporal analysis.
- Domain adapters must not invent new claims or new confidence semantics.

### 6.6 Replay identity and versioning
- Every timeline computation must carry:
  - `timeline_profile_id`
  - `timeline_profile_version`
  - `window_spec_token`
  - `baseline_policy_token`
  - `timezone_token`
  - `as_of_ts`
  - `evidence_manifest_hash`
  - `timeline_summary_hash`
- Inquiry outputs must expose timeline profile/version metadata when temporal reasoning is present.

---

## SECTION 7 — Time Semantics and Determinism

### 7.1 Canonical window definition
- All temporal computation is anchored to the user timezone captured at inquiry time.
- If no user timezone exists, fallback is UTC.
- Window boundaries are defined in user-local time and then converted to storage-query timestamps.
- Temporal buckets use half-open ranges: `[bucket_start, bucket_end)`.

### 7.2 Canonical anchor field rule
- Each domain adapter declares one canonical time anchor per observation class.
- Examples:
  - finance: `occurred_at` or domain-approved transaction date
  - habits: `logged_date`
  - projects: `logged_date` / completion timestamp depending on claim type
  - skills: `practiced_at`
  - calendar: `start_time`
  - health: metric/workout/log date
  - journal: `entry_date`
  - relationships: `logged_at`

### 7.3 Comparison window selection
- `active comparable window`: the closed-window span inside the user-selected timeframe that ends at or before `as_of_ts`.
- `prior comparable window`: the immediately preceding non-overlapping window of equal duration.
- `baseline windows`: a fixed set of prior non-overlapping windows of equal duration defined by profile policy and ending before the active comparable window.
- Baseline policy must be static and versioned. Phase 9 default is a fixed count of prior comparable windows, not a floating "all available history" baseline.

### 7.4 Partial-window rule
- Open buckets that include `as_of_ts` may be shown as bounded context but must not power recurrence, trend, baseline, or drift claims.
- Temporal pattern claims operate only on closed buckets to avoid moving targets.

### 7.5 Canonical ordering
- Windows are ordered by `window_start` ascending.
- Evidence within a window is ordered by:
  - canonical timestamp,
  - source kind priority: `event_record` then `insight_record` then `read_model`,
  - numeric source id or stable source ref.
- Identical input and evidence ordering must produce identical summaries and hashes.

### 7.6 `as_of_ts` interaction
- No evidence after `as_of_ts` is eligible.
- No baseline or comparator may borrow evidence from partially future periods.
- `as_of_ts`, timezone, and window spec become part of replay identity and must be persisted in inquiry metadata.

### 7.7 Sparse or missing history
- If history is insufficient for a claimed temporal pattern, the system must emit an insufficiency note instead of a weak pattern claim.
- Rules:
  - no prior-window comparison without a full prior comparable window,
  - no baseline comparison without the minimum profile-defined baseline coverage,
  - no recurrence claim from a single occupied window,
  - no trend direction from fewer than the profile-defined minimum closed windows.

### 7.8 Explicitly prevented
- Nondeterministic sampling
- Moving target baselines
- Time leakage across `as_of_ts`
- Silent interpolation of missing history
- Re-bucketing the same request differently across replays

---

## SECTION 8 — Semantic and Epistemic Rules

### 8.1 Allowed temporal claims
- "This pattern recurred across multiple comparable windows."
- "This window is higher/lower than the prior comparable window."
- "This appears more variable than the recent baseline."
- "This pattern appears recent rather than sustained."
- "This pairwise alignment persisted across multiple windows."

### 8.2 Forbidden temporal claims
- Causal claims
- Forecasts or predictions
- Inevitability claims
- Pathology or behavioral diagnosis
- Treatment or intervention language
- Recommendation language framed as temporal truth

### 8.3 Observational phrasing rules
- Use phrases such as:
  - "In the available record..."
  - "Across comparable windows..."
  - "Relative to the recent baseline..."
  - "This appears..."
  - "This was observed..."
- Avoid phrases such as:
  - "This means..."
  - "This proves..."
  - "This is why..."
  - "This will likely..."

### 8.4 Boundary preservation
- Evidence/context separation remains strict.
- Confidence vocabulary remains canonical and unchanged.
- No clinical, therapeutic, moral, or judgmental framing is permitted.
- Volatility is descriptive only.
- Drift is descriptive only.
- Recurrence is descriptive only.

---

## SECTION 9 — UX / UI Model

### 9.1 Surface decision
- Phase 9 changes the inquiry surface only.
- It does not introduce a dedicated timeline view in this phase.

### 9.2 What is shown
- A direct-answer block remains first.
- Inquiry may then render bounded temporal sections:
  - "Change over time"
  - "Compared with prior window"
  - "Recurring pattern"
  - "Stability / instability"
  - "Recent or sustained"
- Each temporal block must show:
  - the comparison label,
  - the active window label,
  - evidence references,
  - limitation or insufficiency note when needed.

### 9.3 What is not shown
- No chart-first dashboard layout.
- No raw analytics workspace.
- No predictive arrows.
- No causal annotations.
- No global life score or anomaly score.

### 9.4 Read-first structure preservation
- Direct answer first.
- Temporal interpretation second.
- Evidence support third.
- Limits and refine guidance fourth.
- Raw tables remain hidden until intent, consistent with the UI constitution.

### 9.5 Dashboard-overload prevention
- Max temporal findings per brief must remain bounded.
- Temporal metadata stays visible but secondary.
- If evidence is thin, the UI shows insufficiency rather than decorative temporal chrome.

### 9.6 Evidence visibility
- Every temporal finding keeps visible traceability.
- The user must be able to see what records and windows support the claim.

---

## SECTION 10 — Domain Implications

### 10.1 First-wave timeline domains

#### Finance
- Appropriate because transaction and schedule records are structured, frequent, and naturally comparable over time.
- Safe/useful signals: recurrence of spend categories, cashflow cadence, recent-vs-prior variation, baseline-relative drift.
- Overreach risk: "normal spending" language becoming judgmental or prescriptive.

#### Habits
- Appropriate because cadence, continuity, and break detection are central and semantically clear.
- Safe/useful signals: streak continuity, break detection, recurrence, episodic vs sustained adherence.
- Overreach risk: moralizing missed continuity or implying character judgments.

#### Projects
- Appropriate because work logs and task completions support throughput and burst-vs-sustained activity patterns.
- Safe/useful signals: work-session density, completion cadence, recent-vs-prior throughput.
- Overreach risk: performance judgment or productivity scoring.

#### Skills
- Appropriate because practice sessions are discrete, time-bounded, and naturally recurrence-oriented.
- Safe/useful signals: practice cadence, continuity, sustained vs episodic practice.
- Overreach risk: overclaiming proficiency gain from cadence alone.

#### Calendar
- Appropriate because scheduled commitments are inherently temporal and useful for commitment-pattern visibility.
- Safe/useful signals: recurrence of scheduled commitments, density changes, sustained scheduling patterns.
- Overreach risk: treating scheduled intent as completed behavior.

### 10.2 Later-wave timeline domains

#### Health
- Later-wave because temporal interpretation is useful but quickly drifts into clinical framing if not tightly constrained.
- Safe later signals: descriptive baseline-relative metric changes, workout/nutrition cadence.
- Overreach risk: diagnosis, abnormality framing, treatment suggestions.

#### Journal
- Later-wave because temporal patterns over mood/tags/text are semantically high-risk.
- Safe later signals: entry cadence, explicit-tag recurrence, stated-mood frequency only.
- Overreach risk: psychological diagnosis, hidden-intent inference, personality claims.

#### Relationships
- Later-wave because interaction cadence is structured but socially sensitive.
- Safe later signals: interaction recurrence, gap length relative to prior self-history.
- Overreach risk: relationship quality judgments or intent inference about other people.

### 10.3 Rollout rule
- Phase 9 release gates apply first to first-wave domains only.
- Later-wave domains are feature-gated separately after safety review and QA approval.

---

## SECTION 11 — Cross-Domain Temporal Implications

### Decision
- Phase 9 includes **single-domain temporal reasoning plus approved cross-domain temporal persistence**.

### Scope
- Single-domain temporal reasoning is first-class.
- Cross-domain temporal reasoning is limited to already approved Phase 8 pairs.
- Allowed pairwise temporal questions:
  - whether an approved pair alignment appears in multiple comparable windows,
  - whether the alignment is recent-only or sustained,
  - whether alignment strengthened or weakened descriptively across fixed windows.

### Boundaries
- No new domain pairs in this phase.
- No 3+ domain synthesis.
- No causal explanation of why pairs align.
- No recommendation based on pairwise temporal findings.

---

## SECTION 12 — Contract / Semantic / Docs Impact

### Required updates
- `lifeos/docs/lifeos_architecture.md`
  - Add Phase 9 constitutional decision, layer placement, rollout scope, and guardrails.
- `lifeos/docs/ui_ux_constitution.md`
  - Bind temporal findings to the inquiry surface while preserving read-first rules and anti-dashboard discipline.
- `lifeos/docs/semantics/INSIGHT_CONTRACTS.md`
  - Add timeline-specific inquiry contracts and explicit allowed/forbidden temporal claim classes.

### Additional updates needed
- `lifeos/docs/semantics/DOMAIN_SEMANTIC_CONTRACTS.md`
  - Yes. Add a minimal Phase 9 observational rule clarifying that time interpretation compares existing domain facts without changing domain meaning.
- `lifeos/docs/semantics/EVENT_SEMANTICS_FREEZE.md`
  - Yes. Add a minimal inquiry-event metadata allowance for timeline profile/version, window spec, baseline policy, coverage, and summary hash fields.

### No change by default
- `lifeos/docs/semantics/CONFIDENCE_VOCABULARY.md`
  - No change. Existing vocabulary is sufficient and must remain frozen.

### New task document
- `lifeos/docs/tasks/phase_9_timeline_intelligence_foundations.md`

---

## SECTION 13 — Non-Goals

- No assistant chat mode
- No recommendation engine
- No causal explanation engine
- No prediction or forecasting system
- No behavioral diagnosis
- No hidden personalization
- No runtime ML scoring or generation
- No autonomous planning or action
- No 3+ domain temporal synthesis
- No dedicated timeline analytics dashboard in Phase 9

---

## SECTION 14 — Quality / Release Gates

### 14.1 Product criteria
- First-wave domains can answer recurrence, drift, stability, and recent-vs-prior questions with explicit evidence and window labels.
- Sparse history is handled honestly with insufficiency notes.
- Inquiry remains direct, calm, and read-first.

### 14.2 Temporal determinism criteria
- Identical normalized request + timezone + `as_of_ts` + timeline profile/version + evidence state yields identical temporal findings and hashes.
- Closed-window selection is stable.
- Baseline membership is stable.
- No future leakage past `as_of_ts`.

### 14.3 Semantic safety criteria
- No causal, predictive, diagnostic, or recommendation claims pass through.
- Confidence labels remain canonical.
- Temporal claims remain observational and traceable.

### 14.4 QA requirements
- Fixture matrix must cover:
  - dense history,
  - sparse history,
  - single-window only history,
  - DST and timezone boundary cases,
  - month-length variation,
  - late records before `as_of_ts`,
  - records after `as_of_ts` that must be excluded,
  - approved cross-domain pair persistence cases,
  - forbidden-claim regression cases.
- Replay tests must compare hashes and rendered findings across repeated runs.

### 14.5 Observability requirements
- Required metrics:
  - timeline generation latency
  - temporal insufficiency rate
  - baseline coverage distribution
  - blocked forbidden-claim counters
  - per-domain/pair timeline profile usage
  - timeline replay mismatch counters
- Build/profile identity must remain visible for rollout triage.

### 14.6 Rollout criteria
- Stage 1: first-wave domains in staging
- Stage 2: single-domain canary by domain/profile version
- Stage 3: approved-pair temporal persistence canary
- Stage 4: production staged enablement

### 14.7 Release blockers
- Any replay mismatch
- Any time leakage across `as_of_ts`
- Any missing provenance on temporal findings
- Any forbidden claim class escaping to UI or API
- Any UI rendering that hides evidence or turns inquiry into a dashboard

---

## SECTION 15 — Cross-Team Handoff Plan

### Backend
- Own the shared timeline layer, inquiry integration point, timeline profile registry, and temporal metadata contracts.
- Must not change confidence vocabulary, introduce recommendations, or implement causal/predictive logic.

### Frontend
- Own inquiry rendering of temporal findings, labels, and insufficiency states.
- Must not invent timeline scores, charts-first dashboards, or speculative wording.

### DB
- Own additive schema changes required for inquiry metadata persistence or read-model support.
- Must not introduce destructive migration patterns or mutable historical baselines.

### QA
- Own deterministic replay verification, semantic safety checks, timezone/window boundary cases, and first-wave domain acceptance coverage.
- Must treat causal/predictive leakage as blocking defects.

### DevOps
- Own feature flags, observability, rollout controls, canary policy, and production gating for timeline profiles.
- Must preserve build/profile visibility and rollback paths.

### ML
- No runtime ownership in Phase 9.
- Advisory only: review future feature lineage requirements so Phase 9 temporal features remain usable later without changing semantics now.

---

## SECTION 16 — Implementation Sequence

1. Architecture ratifies Phase 9 scope, non-goals, and rollout order.
2. Freeze temporal semantics: timezone, window law, `as_of_ts`, baseline policy, and insufficiency rules.
3. Define the shared timeline layer and timeline profile/version contracts.
4. Update constitutional and semantic docs.
5. Implement backend timeline engines and inquiry integration for first-wave domains.
6. Add inquiry UI rendering for bounded temporal findings.
7. Add QA fixtures, replay checks, timezone boundary cases, and semantic regression tests.
8. Add observability, feature flags, rollout controls, and canary rules.
9. Expand to approved cross-domain temporal persistence after single-domain gates are green.
10. Architecture signs off after determinism, semantic safety, and UX stability all pass.

---

## Outcome

Phase 9 comes before recommendations, causality, and prediction because LifeOS needs a disciplined temporal substrate before it can safely say what should happen, why something happened, or what may happen next.

This phase materially increases value by turning inquiry from a bounded-window explainer into a system that can also describe recurrence, drift, persistence, and stability over time.

It preserves constitutional discipline by keeping the system deterministic, observational, evidence-bounded, non-chat, non-causal, and non-predictive.
