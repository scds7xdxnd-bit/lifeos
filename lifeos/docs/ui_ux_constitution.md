# LifeOS UI/UX Constitution

*(Normative · Binding · Long-Lived)*

## 1. Purpose of the UI
LifeOS UI exists to do one thing: help a person calmly face themselves over time and choose to act responsibly. It is not a motivation engine, a dopamine machine, a social feed, or a productivity contest. If a UI decision does not support calm accountability, it is wrong.

## 2. Target User (Frozen)
Designed for people in self-development (students, busy professionals). Users are cognitively loaded, time constrained, emotionally sensitive to judgment. UI must reduce friction, never shame, never overwhelm.

## 3. Emotional Contract (Frozen)
When a user opens LifeOS, they should feel: relaxed enough to be honest, high-spirited enough to be accountable. Allowed: calm, encouraged. Forbidden: urgent (default), guilty, addicted.

## 4. Aesthetic Philosophy (Frozen) — “Quiet Authority”
- Quiet: low saturation, few accents, no shouting, generous whitespace.
- Authority: clear hierarchy, precise typography, predictable interactions, no gimmicks.
- Decorative without informative value is suspect.

## 5. Core UI Principles (Non-Negotiable)
- Time first: calendar/timeline is the primary spatial metaphor; domains overlay time.
- Reveal, don’t demand: no forced actions, no “you must” language; suggestions as observations.
- Soft guidance, hard truth: gentle language; precise numbers/dates/confidence.
- One cognitive question per screen: each screen answers one question only.

## 6. Interaction Grammar
- Confirm/Reject is sacred for inferred records: clear, low-effort, auditable, reversible history; no dark patterns, no silent hiding.
- Nothing disappears silently: deleted = archived; rejected ≠ erased; history accessible.
- Mobile first ≠ minimal first: calm, focused, vertical; density allowed if hierarchy is clear.

## 7. First Visual System (Design Tokens)
- Color: background primary (off-white or deep charcoal); secondary neutral; surface card subtle elevation. One primary accent visible at once. Semantic colors for success/warning/neutral; red is never default; green means “confirmed,” not “good.”
- Typography: neutral humanist sans; legible numbers. Hierarchy via size/weight, not color; avoid italics/ALL CAPS (except labels).
- Spacing: generous by default; tight only by user opt-in. Lists > cards > grids.
- Confidence encoding: numeric/bar, muted, secondary; no emojis/smiley/stars.

## 8. Tone of Voice
- Allowed: “It looks like…”, “You may want to review…”, “Based on recent activity…”
- Forbidden: “You should…”, “You failed to…”, “You must…”

## 9. What to Design First (Strict Order)
- Calendar (Day/Week view)
- Inferred Record Review Queue
- Insights Feed

## 10. Optimizes For
Long-term personal use, trust over novelty, expansion to mobile, monetization without attention selling. Scales from solo to pro/long-term subscribers.

## 11. Next Actions
1) Lock this constitution in the repo.
2) Define design tokens (even manually).
3) Redesign one screen using this system.
4) Evaluate: calmer? more honest?

**Reference in frontend PRs:** “Aligned with UI/UX Constitution §X.”
