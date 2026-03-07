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
- Mobile-first implications: Vertical flow, one primary action visible, filters and bulk actions behind drawers. Avoid dense grids; prioritize readability and thumb reach without committing to specific mobile UI.
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
- **Habits**: Question: “Did I keep my commitments recently?” Default: streak/status summary and today’s plan. Hidden until intent: backfill logs, bulk edits, advanced charts. Good UX: one tap/one click to log/confirm; history visible but not dominant.
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
- No mobile UI spec; only mobile-first implications for flow and hierarchy.
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
