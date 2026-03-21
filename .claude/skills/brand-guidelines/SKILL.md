---
name: brand-guidelines
description: The Botanical Editorial design system for LifeOS. Auto-applies whenever generating or modifying UI components, pages, styles, or any visual output. Enforces the sage palette, Newsreader + Manrope typography, clipped-specimen cards, pill buttons, glassmorphism, and tinted shadows. Use this skill for any task involving HTML, CSS, Tailwind, React components, or visual design decisions.
---

# The Botanical Editorial — LifeOS Brand Guidelines

Every screen must feel like turning the page of a beautifully bound book. We are building a digital sanctuary, not a dashboard.

---

## Color Tokens (Mandatory)

### Light Surface

| Token | Hex | When to use |
|---|---|---|
| `background` | `#f8faf2` | Base page background |
| `surface` | `#f8faf2` | Content area fill |
| `surface-container-low` | `#f1f5eb` | Section backgrounds, alternating blocks |
| `surface-container-lowest` | `#ffffff` | Elevated cards, input fields, modals |
| `surface-container` | `#ebefe4` | Secondary containers |
| `surface-container-high` | `#e5eade` | Hover/active states |
| `surface-container-highest` | `#dee5d7` | Secondary buttons, pressed states |
| `primary` | `#4b6646` | Primary actions, headlines, brand mark |
| `primary-dim` | `#3f5a3a` | Gradient endpoints |
| `primary-container` | `#ccebc2` | Decorative fills, selected backgrounds |
| `on-surface` | `#2e342b` | Primary text (**never #000000**) |
| `on-surface-variant` | `#5a6157` | Body text, descriptions |
| `outline` | `#767d72` | Placeholder text |
| `outline-variant` | `#adb4a8` | Ghost borders (15–20% opacity only) |
| `accent-coral` | `#e8735c` | Sparingly: notifications, active confirmations |
| `secondary-container` | `#d6e8ce` | Chips, tags, badges |
| `on-secondary-container` | `#465642` | Chip/tag text |

### Dark Surface (sidebar, footer, dark sections)

| Token | Hex | When to use |
|---|---|---|
| `dark` | `#1a1f1a` | Dark backgrounds (never pure black) |
| `dark-text-active` | `#a8c4a0` | Active text on dark (sage-tinted) |
| `dark-text-inactive` | `#5a6857` | Secondary text on dark |
| `dark-accent` | `#6b8f65` | Accent lines, brand mark on dark |

### Domain Accent Palette

Each domain carries a muted, botanical-adjacent accent — like pressed-flower pigments:

| Domain | Tint (bg) | Dark (icon/border) | Selected Gradient |
|---|---|---|---|
| Finance | `#e8f0e3` (sage) | `#3a5c35` | `135deg, #edf5e8 → #d9ebcf` |
| Health | `#fce8e4` (clay rose) | `#8b4a3a` | `135deg, #fdf0ed → #f5ddd6` |
| Habits | `#e4edf5` (pressed lavender) | `#3a5272` | `135deg, #edf2f8 → #d6e3f0` |
| Skills | `#f5f0e4` (aged parchment) | `#6b5a35` | `135deg, #f8f3eb → #ede4d0` |

- Domain accents only appear on selected/active states — never on text, buttons, or large fills.
- Unselected cards remain in core sage palette (`#ffffff` bg).
- Primary CTAs always stay `primary` (#4b6646) regardless of domain.

---

## Typography (Mandatory)

### Font Pairing
- **Newsreader** (serif) — Headlines, display text, pull-quotes. Conveys feeling.
- **Manrope** (sans-serif) — Body text, labels, buttons, UI elements. Conveys function.

### Hierarchy

| Level | Font | Weight | Tracking | Use |
|---|---|---|---|---|
| Display | Newsreader | Light (300) | `-0.03em` | Hero headlines, page titles |
| Headline | Newsreader | Regular (400) | `-0.03em` | Section headers, card titles |
| Headline Italic | Newsreader | Regular Italic | `-0.03em` | Brand mark, pull-quotes |
| Micro-label | Manrope | Bold (700), UPPERCASE | `+0.05em` | Category tags, metadata |
| Body | Manrope | Regular (400) | Normal | Paragraphs (line-height: 1.65) |
| Label | Manrope | Bold (700) | Normal | Buttons, form labels |

### Rules
- Newsreader headlines MUST use `-0.03em` letter-spacing
- Display = Newsreader **Light** (300), not Bold. Thin strokes = editorial elegance
- Never use Newsreader for body text. Serif at body size = eye fatigue
- Headline color: `primary` (#4b6646). Body color: `on-surface-variant` (#5a6157)
- Micro-label pattern: Manrope Bold + UPPERCASE + `+0.05em` tracking above a Newsreader headline

---

## Components (Mandatory)

### Cards — "The Clipped Specimen"
```
border-radius: 0 16px 16px 16px   /* sharp top-left, rounded rest */
```
- **Never use `clip-path`** — it clips content and clickable area
- Fill: `surface-container-lowest` (#ffffff) on light, `rgba(255,255,255,0.05)` on dark
- No borders. Tonal layering for definition
- Padding: 2rem minimum
- Hover: shadow deepens (0.06 → 0.08 opacity) + `translateY(-2px)`, 220ms ease

### Buttons — Always Pills
- **All buttons MUST be `rounded-full`**. No square or slightly-rounded. No exceptions.
- Primary: gradient `primary` → `primary-dim` at 135deg, white text, tinted shadow
- Secondary: `surface-container-highest` bg, `on-surface` text, no shadow at rest
- Ghost: Manrope Bold UPPERCASE +0.05em, no background, hover opacity 0.7
- Accent (rare): `accent-coral` fill, white text — only for "human" moments

### Sidebar
- Background: `dark` (#1a1f1a) — warm forest, NOT pure black
- Brand: Newsreader italic in `dark-accent`
- Active: 2px left border `dark-accent`, text `dark-text-active`, subtle bg tint
- Inactive: `dark-text-inactive`, hover → `dark-text-active`

### Input Fields
- Background: `surface-container-lowest` (#ffffff)
- Border: ghost border `outline-variant` at 20% opacity
- Focus: 2px `primary` ring (ghost border disappears)
- Labels: micro-label style, 8px above field
- Radius: 4px (NOT pill — inputs are functional)

### Chips & Tags
- Shape: `rounded-full` (pill)
- Background: `secondary-container` (#d6e8ce)
- Text: `on-secondary-container` (#465642), micro-label style

---

## Shadows (Mandatory — Never Pure Grey)

All shadows tinted with `on-surface` (#2e342b):

| Context | Shadow |
|---|---|
| Card resting | `0 8px 24px rgba(46, 52, 43, 0.06)` |
| Card hover | `0 30px 60px rgba(46, 52, 43, 0.08)` |
| Floating elements | `0 20px 40px rgba(46, 52, 43, 0.06)` |
| Primary button | `0 4px 20px rgba(46, 52, 43, 0.18)` |
| Primary button hover | `0 10px 34px rgba(46, 52, 43, 0.24)` |

---

## Glassmorphism (Floating Elements)

- Fill: `background` (#f8faf2) at 75% opacity
- Blur: `backdrop-filter: blur(8px)` — **never above 8px**
- Inner border: 1px solid white at 20% opacity (frost line)

---

## Layout Principles

- **Surface hierarchy:** background → surface-container-low → surface-container-lowest (desk → sheet → card)
- **No 1px borders** for sectioning. Background color shifts only.
- **Ghost borders** only when same-color containers need definition: `outline-variant` at 15–20% opacity
- **Generous whitespace.** Space is luxury, not a bug.
- **Divider lines are forbidden.** Use 1.2rem spacing or alternating tints.
- **Read-first, act-on-intent.** Default = readable summaries; inputs appear after explicit intent.
- **One primary action per screen.** One dominant CTA; others are quiet.

---

## Motion

| Element | Animation | Duration | Easing |
|---|---|---|---|
| Card entrance | Stagger 50ms between cards | 300ms | ease-out |
| Card hover | Shadow + `translateY(-2px)` | 220ms | ease |
| Button hover | Gradient shift + shadow + `translateY(-2px) scale(1.025)` | 180ms | ease |
| Modal enter | Fade + scale 0.97→1 | 200ms | ease-out |
| Modal exit | Fade + scale down | 150ms | ease-in |

---

## Hard Prohibitions

These will break the design system if violated:

1. **No `#000000`** — use `on-surface` (#2e342b) for dark text
2. **No pure grey shadows** — tint with `rgba(46, 52, 43, ...)`
3. **No 1px section borders** — background shifts only
4. **No rounded top-left on cards** — `border-top-left-radius: 0` always
5. **No `clip-path` for cards** — `border-radius` only
6. **No square/rounded-rect buttons** — `rounded-full` always
7. **No bright emerald/lime greens** — sage tones only
8. **No `backdrop-blur` above 8px** — crisp glass, not fog
9. **No Newsreader at body size** — headlines and editorial moments only
10. **No zinc/slate grays for body text** — sage palette (#5a6157) only
11. **No bright, saturated, or non-botanical accents** — domain accents (clay rose, pressed lavender, aged parchment) are permitted; neon/UI-primary colors are not
12. **No divider lines** — spacing or tonal shifts only

---

## Tone of Voice (UI Copy)

- Allowed: "It looks like...", "You may want to review...", "Based on recent activity..."
- Forbidden: "You should...", "You failed to...", "You must..."
- Emotion: calm enough to be honest, spirited enough to be accountable
- Never shame. Never create urgency as default.
