# LifeOS UI/UX Constitution

*(Normative · Binding · Long-Lived — frontend must conform even when backend exposes richer data)*

## 1. Purpose & Emotional Contract (Frozen)
- Purpose: help a person calmly face themselves over time and choose responsible action. Not a feed, not a dashboard for power users, not a productivity contest.
- Target user: cognitively loaded, time-constrained, sensitive to judgment. UI must reduce friction, never shame.
- Emotional contract: relaxed enough to be honest, high-spirited enough to be accountable. Allowed: calm, encouraged. Forbidden: urgent-by-default, guilty, addicted.

## 2. Core UX Principles (Non-Negotiable, Enforceable)
- Observe → Decide → Act ordering: always show context first, then decision options, then action. Never lead with input.
- Read-first, act-on-intent: default state is readable summaries; inputs appear only after explicit intent.
- One primary action per screen: one dominant CTA; secondary actions are quiet links/menus. If multiple actions exist, one must be visually dominant; others are clearly secondary and never compete spatially or chromatically.
- Progressive disclosure of complexity: advanced filters/forms hidden until requested; tables and bulk tools are opt-in overlays.
- Calm-first, precision-second: tone and visuals stay calm; numbers/dates/confidence are precise and legible when revealed.
- Progress must be felt, not just shown: surface recent movement, streaks, confirmations, completions before raw counts.
- State is persistent and visible: always communicate current state (today, active, pending, reviewed, archived); users should never wonder “what state am I in?”
- Nothing disappears silently: delete = archive; reject ≠ erase; history is accessible.
- Confirm/Reject is sacred for inferred records: low-effort, auditable, reversible; no dark patterns, no silent hiding.

## 3. Global Layout & Interaction Rules
- Page structure: Header (orientation) → Focus area (the one primary question) → History/management (context, logs). Do not mix multiple primary questions in one view.
- Modes: Default “read mode” (summaries, guidance). “Edit mode” is explicit and scoped; forms open in overlays/drawers and close on completion. No always-on forms.
- Forms: Collapsed by default; opened by explicit user intent (button/link). Save/cancel are always visible; autosave only when clearly messaged.
- Tables: Allowed only when comparison across many rows is the intent. Otherwise use summarized cards/rows. Tables are tucked behind “View all” or “Manage” affordances.
- Mobile-first implications: Vertical flow, one primary action visible, filters and bulk actions behind drawers. Avoid dense grids; prioritize readability and thumb reach. **Landing page:** Three responsive breakpoints (mobile ≤639px, tablet 640–1023px, desktop 1024px+) implemented via `useBreakpoint()` hook; multi-column layouts collapse to single-column, parallax effects disabled, navigation collapses to hamburger menu. See `DESIGN.md` §6 "Landing Page — Responsive Breakpoints" for full spec.
- History & audit: Rejections, confirmations, edits surface in a visible, filterable activity log per domain screen.
- Cross-domain consistency: identical patterns (confirm/reject, edit overlays, history access) behave the same across domains to avoid fragmentation.

## 4. Visual System Direction (First Iteration — Direction, not Spec)
- Hierarchy philosophy: Orientation text first, then primary metric/decision, then secondary details. CTAs are fewer and quieter; the dominant element is the current question/answer, not chrome.
- Color usage: Neutral base; one accent active per screen; semantic colors restrained (success/warn/info/neutral). Red is only for destructive/alert; green denotes “confirmed” not “goodness.”
- Typography intent: Calm, readable, humanist; hierarchy via size/weight, not color. Numbers legible; avoid italics/ALL CAPS except concise labels.
- Cards/spacing/rhythm: Generous whitespace; cards for grouping related signals; spacing increases around primary decision zones; rhythm favors short vertical scans over wide tables.
- Confidence encoding: Numeric or bar, muted/secondary; no emojis/stars; confidence is contextual, not celebratory.

## 5. Domain UX Contracts (Frontend must adhere)
For each domain: answer the primary user question first; hide complexity until intent; keep one primary action.

- **Calendar**: Question: “What’s next and what needs confirmation?” Default: upcoming events with inferred interpretations and confidence. Hidden until intent: bulk sync settings, recurrence builders. Good UX: quick confirm/reject flows, clear time context, no grid overwhelm; week/day focus with calm timeline.
- **Finance**: Question: “Where do I stand right now, and what changed recently?” Default: summarized balances, recent transactions with suggested classifications. Hidden until intent: full journal tables, import mappings, advanced filters. Good UX: show drift/variance and next action (confirm, reclassify) as primary; tables only behind “review all.”
- **Habits**: Question: “Did I keep my commitments recently?” Default: streak/status summary with 7-day dot row, completion rate, and today’s plan. Hidden until intent: backfill logs, bulk edits, advanced charts, yearly heatmap. Good UX: one tap/one click to log/confirm with satisfying micro-animation (checkmark + streak increment); history visible but not dominant. Desktop (≥1024px): master-detail split layout (60/40) — habit list left, selected habit detail right (streak chart, heatmap, notes). Mobile/tablet: habit detail opens in a drawer/sheet interaction. LOG button is the dominant CTA (filled olive, min 44px touch); transforms to “Undo” when today is already logged. Streak milestones (7/30/100 days) trigger celebration animations. Time-aware cues show relative time to scheduled habits (“Due in 2h”). Habit creation uses a centered Habit Studio modal with split form/reflection panels; labels prefer “Frequency” language, and preferred time uses a concise native time input with localized preview while persisting canonical backend time semantics. Reflection copy is encouraging, localized (en/ko/zh), and includes a rotating tip line (~5s cadence) with gentle fade. Modal dismissal must remain simple: backdrop tap, Esc, and explicit Cancel action. Empty state is a motivational onboarding moment, not a blank list.
- **Skills**: Question: “Am I improving and what should I practice next?” Default: recent sessions and next planned practice. Hidden until intent: detailed metrics, session edits, archival. Good UX: surface progression cues; edits in overlays.
- **Health**: Question: “How is my baseline and what needs attention?” Default: key vitals/workouts summary with trends. Hidden until intent: raw metric tables, nutrition grids. Good UX: calm trend cards; alerts minimal and actionable.
- **Journal**: Question: “What did I note and how did I feel?” Default: recent entries with mood/tags; editing is secondary. Hidden until intent: bulk tag management, exports. Good UX: read-first; edits in-place but gated; no dense tables.
- **Relationships**: Question: “Who needs attention next?” Default: reconnect cues and recent interactions. Hidden until intent: contact CRUD, import, bulk notes. Good UX: cues first, interaction log accessible, no Rolodex tables unless requested.
- **Projects**: Question: “What is the next meaningful step?” Default: active projects with the next task per project. Hidden until intent: full task grids, burndowns, archival. Good UX: one primary action (complete/advance) per project card; history/log tucked behind “history.”
- **Profile/Auth**: Question: “Is my account safe and configured?” Default: security status and session/admin reset info. Hidden until intent: credential changes, device/session details (read models) in drawers. Good UX: clarity over density; no always-on forms.

## 6. Frontend Handoff (Binding)
- MUST follow this constitution even if backend exposes more primitives; prefer synthesized summaries over raw fields.
- MUST default to summaries/read mode; forms and bulk tools appear only after intent.
- MUST avoid admin-panel aesthetics: no dense tables by default, no “form walls,” no chrome-heavy layouts.
- MUST interpret read models as sources for summaries/trends, not as UI schemas; derive human-readable groupings and confidence cues.
- MUST design new screens by stating the primary user question, primary action, and what stays hidden until intent—then verify alignment with sections 2–5.
- MUST NOT expose backend primitives directly by default; avoid “power-user density” without clear intent affordance.
- MUST NOT add complexity for “power users” that conflicts with calm-first, single-question views.
- MUST NOT optimize for density over clarity; vertical scan > horizontal cram.

## 7. Explicit Non-Goals (Do Not Do Now)
- No cosmetic reskinning for its own sake; no branding/marketing language.
- No framework/library choices in this document.
- No dedicated mobile app UI spec. Landing page responsive design is implemented (see `DESIGN.md` §6). App shell mobile responsiveness is deferred.
- No multi-device/offline UX commitments (deferred to Phase 3c triggers).
- No new data exposure beyond what backend already emits; frontend should down-scope, not up-scope.

## 7.1 UX Debt (Binding)
- UX debt is real debt. If a feature deviates from this constitution for expedience, it must be explicitly documented and scheduled for correction.

## 8. Order of Operations for Frontend Work
1) Declare the primary user question and primary action for the screen.
2) Choose read mode contents (summaries, cues, trends); hide forms/tables until intent.
3) Place confirm/reject (where relevant) before creation flows.
4) Add progressive disclosure for advanced tools (filters, bulk, imports).
5) Validate against domain contract and global principles before styling.

## 9. Tone of Voice (Retained, Binding)
- Allowed: “It looks like…”, “You may want to review…”, “Based on recent activity…”
- Forbidden: “You should…”, “You failed to…”, “You must…”

## 10. Reference in Frontend PRs
Include: “Aligned with UI/UX Constitution §X” and cite the domain contract applied.

## 11. Focused Inquiry v1 Surface Contract (Binding)
- Surface type: dedicated inquiry page/surface. Not chat, not dashboard, not feed replacement.
- Primary user question: "What exactly am I trying to understand right now?"
- Primary action: "Generate brief."
- Entry point: explicit user intent from Insights/Navigation ("New Inquiry").
- Interaction posture: guided analyst brief flow, not assistant conversation.

### 11.1 Canonical Flow
- Step 1 (scope): choose domain lens (or explicit cross-domain lens) and timeframe.
- Step 2 (optional context): user may provide context text; UI must label it as user-provided context.
- Step 3 (confirm): user confirms request and generates the brief.
- Step 4 (review): render brief with findings, evidence links, confidence labels, and uncertainty notes.
- Step 5 (refine): user may refine scope/timeframe/context and regenerate.
- Step 6 (history): user can revisit prior inquiries and generated briefs.

### 11.2 Read-First Hierarchy
- Header: inquiry title, selected lens, timeframe.
- Brief body: findings first, evidence references second, caveats/unknowns third.
- Secondary controls: refine and history access.
- Hidden until intent: advanced filters, raw record tables, any bulk controls.

### 11.3 Evidence and Confidence Presentation
- Every finding must show "Based on" references to canonical evidence sources.
- Confidence labels must use only canonical vocabulary.
- If evidence is mixed-quality, uncertainty must be explicit in the finding block.
- User-provided context is displayed in a visually separate "Context (not evidence)" block.

### 11.4 Explicit Anti-Patterns
- Must not render as an open-ended chatbot transcript.
- Must not inject dashboard-style dense KPI tiles into inquiry output.
- Must not present ungrounded recommendations as facts.
- Must not hide uncertainty or downgrade caveats for visual cleanliness.
- Must not auto-expand into cross-domain claims without explicit evidence references.

## 12. Domain Expert Briefs (Phase 7/7.1, Binding)
- Domain expert briefs must remain within the same inquiry surface and flow; no new assistant shell is allowed.
- Domain profile/version metadata must be visible but secondary to findings/evidence.
- Domain-specific limitation language is required and must be explicit when evidence coverage is thin.

### 12.1 First-wave and later-wave behavior
- First-wave domains (finance, habits, projects, skills) may render specialized finding categories and deterministic refine guidance.
- Later-wave domains (journal, relationships, health) must render stronger caution labels and explicit scope boundaries.
- Later-wave domains must never infer diagnosis, relationship quality, or hidden intent.

### 12.2 Presentation constraints
- Findings still render as brief blocks, not conversational turns.
- Evidence references remain mandatory for each finding.
- Confidence labels remain canonical and human-legible.
- Context remains labeled as "not evidence" and visually separated.

## 13. Cross-Domain Inquiry Expansion (Phase 8, Binding)
- Cross-domain inquiry stays inside the same inquiry surface and interaction flow.
- Cross-domain setup must require explicit domain-pair selection; no implicit omniscient mode.
- Output remains structured findings, never assistant-style narrative/chat.

### 13.1 Rendering requirements
- Findings must show cross-domain claim category labels.
- Evidence must be grouped and labeled per contributing domain.
- Limitation language must be explicit for partial coverage or weak alignment.
- Confidence labels remain canonical and secondary to evidence clarity.

### 13.2 Explicit anti-patterns
- No "AI explains your life" narrative framing.
- No speculative causal storytelling between domains.
- No clinical or psychological framing in cross-domain summaries.
- No inferred intent/emotion framing for other people.

## 14. Inquiry Productization (Phase 8.1, Binding)
- Inquiry remains read-first and structured; no assistant shell or chat transcript is introduced.
- Productization improves usefulness quality, not inference breadth.

### 14.1 Required brief improvements
- A stronger direct-answer block must appear first.
- Pattern-level takeaways should replace count-heavy summaries when evidence supports it.
- Limitation language should be deduplicated and concise.
- Evidence relevance must be explained in human-readable form ("why this matters"), not only referenced.
- Refine guidance must be specific to expected quality gain.
- Briefs must expose answerability/sufficiency status clearly.

### 14.2 UI constraints that do not change
- Evidence references remain visible and traceable.
- Confidence labels remain canonical and secondary to evidence.
- Context remains explicitly labeled as non-evidence.
- No speculative or assistant-style prose may replace structured findings.

## 15. Timeline Intelligence Foundations (Phase 9, Binding)
- Phase 9 extends the existing inquiry surface only. No dedicated timeline dashboard, analytics lab, or assistant shell is introduced.
- Primary temporal question: "What is changing over time here?"
- Read-first order remains: direct answer, temporal findings, evidence/comparison labels, limits, then refine actions.

### 15.1 What temporal UI may show
- Bounded sections such as:
  - "Change over time"
  - "Compared with prior window"
  - "Recurring pattern"
  - "Stability / instability"
  - "Recent or sustained"
- Each temporal finding must show:
  - the active window label,
  - the comparison reference ("prior comparable window" or "baseline of prior windows"),
  - evidence references,
  - explicit insufficiency language when history is sparse.
- Temporal findings should render as concise brief blocks, not charts-first dashboards.

### 15.2 What temporal UI must not show
- No predictive arrows, forecasts, or "what happens next" widgets.
- No causal arrows or "why this happened" storytelling.
- No global timeline score, health score, life score, or hidden ranking.
- No dense chart walls by default; any future charts remain subordinate to textual findings and evidence.
- No "normal/abnormal" framing that implies diagnosis or judgment; use neutral baseline-relative phrasing instead.

### 15.3 Overload control
- Inquiry should surface only a small set of temporal findings per brief; do not turn the surface into a monitoring cockpit.
- Comparison metadata must stay legible but visually secondary to the answer itself.
- If coverage is too thin for a safe temporal interpretation, show the insufficiency note instead of a weak pseudo-pattern.

## 16. Insight Humanization Layer (Phase 10, Binding)
- Inquiry becomes humanized-by-default in Phase 10, but the canonical technical brief must remain available inside the same surface.
- The first thing a user sees should be the simplest correct explanation, not the fullest technical serialization.
- Humanization must preserve read-first structure and must not turn the surface into a chatbot or story transcript.

### 16.1 Default visible structure
- Default humanized blocks may include:
  - "What stands out"
  - "Why it matters"
  - "How sure this is"
  - "What to review next"
- A collapsed "Technical brief" or equivalent canonical expansion must remain available on the same page.
- Evidence traceability must remain visible from the default reading surface, even if detailed technical metadata moves into the collapsed technical view.

### 16.2 What humanization may do
- Use shorter section names.
- Simplify technical terminology into ordinary-user language.
- Compress repetitive caveats and metadata.
- Reorder sections so the clearest meaning appears first.
- Explain why cited evidence matters using bounded deterministic phrasing.

### 16.3 What humanization must not do
- No chat bubbles, assistant transcript framing, or fake conversational tone.
- No removal of material uncertainty, limitations, or evidence existence.
- No advice posture, recommendations, emotional interpretation, or causal storytelling.
- No hiding of the canonical technical brief behind a separate workflow or secondary page.

## 17. Private Alpha Product Cut (Binding)
- Private alpha is inquiry-first. The product should feel like a focused question-and-answer tool over personal records, not a general life-management suite.
- The primary alpha loop is:
  - get oriented,
  - ask one structured question,
  - read one humanized answer,
  - inspect technical support if desired,
  - refine or return later.
- Alpha must simplify aggressively. If a surface does not directly support this loop, it should be hidden from ordinary alpha users.

### 17.1 Primary alpha navigation
- Primary navigation should be minimal:
  - Inquiry
  - History
  - Data
  - Account / Help
- Domain-by-domain navigation should not be primary in alpha.

### 17.2 Alpha screen priorities
- Inquiry creation and inquiry results are the primary surfaces.
- History is secondary but visible.
- Data/setup is supportive, not product-center.
- Technical detail is available, but never primary.

### 17.3 What stays hidden in alpha
- Broad domain management surfaces
- Admin-style dashboards
- Multi-panel analytics views
- Feature surfaces that imply assistant behavior or broad life-OS control
