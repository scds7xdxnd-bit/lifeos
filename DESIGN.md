# Design System: The Botanical Editorial

## 1. Overview & Creative North Star

The North Star is **The Botanical Editorial**. We reject the cold efficiency of traditional productivity software in favor of the tactile, intentional feeling of a premium print journal — the kind of object you'd find on a curated shelf, not in a cubicle.

Every screen should feel like turning the page of a beautifully bound book. We are building a digital sanctuary, not a dashboard.

This system achieves a bespoke aesthetic through:

- **Intentional Asymmetry:** The signature sharp top-left corner on cards creates an architectural rhythm — like a clipped botanical specimen pinned to a collector's page.
- **Atmospheric Depth:** Depth is created through shifting tints of sage and paper, not through harsh lines or standard shadows. Light passes through clouds, not off glass.
- **Typographic Tension:** Tight-tracked serif headlines (the "authority") paired with functional sans-serif body text (the "guide") create a sophisticated editorial feel — the digital equivalent of a New York Times Magazine spread.
- **Tonal Contrast:** Muted dark forest tones frame the warm paper-white content area, like a book cover holding its pages.
- **Moments of Wonder:** In data-heavy pages, break the rhythm with Newsreader pull-quotes, editorial labels, or generous whitespace pauses. The user should feel curated calm, not spreadsheet fatigue.

---

## 2. Colors: Paper & Sage

The palette is rooted in organic tones designed to reduce cognitive load and mimic the reflective qualities of physical paper.

### Core Tokens

| Token | Hex | Usage |
|---|---|---|
| `background` | #f8faf2 | Base page background |
| `surface` | #f8faf2 | Content area fill |
| `surface-container-low` | #f1f5eb | Section backgrounds, alternating blocks |
| `surface-container-lowest` | #ffffff | Elevated cards, input fields, modals |
| `surface-container` | #ebefe4 | Secondary containers, step indicators |
| `surface-container-high` | #e5eade | Hover/active states, recessed areas |
| `surface-container-highest` | #dee5d7 | Secondary buttons, pressed states |
| `primary` | #4b6646 | Primary actions, headlines, brand mark |
| `primary-dim` | #3f5a3a | Gradient endpoints, secondary emphasis |
| `primary-container` | #ccebc2 | Decorative fills, selected backgrounds, icon containers |
| `on-surface` | #2e342b | Primary text (never use #000000) |
| `on-surface-variant` | #5a6157 | Secondary text, descriptions, body copy |
| `outline` | #767d72 | Placeholder text, tertiary labels |
| `outline-variant` | #adb4a8 | Ghost borders (always at 15–20% opacity) |
| `accent-coral` | #e8735c | Sparingly: active states, notifications, "human" moments |
| `secondary-container` | #d6e8ce | Chips, tags, pill badges |
| `on-secondary-container` | #465642 | Chip/tag text |

### Domain Accent Palette

Each LifeOS domain carries a muted, botanical-adjacent accent that distinguishes it visually while staying within the organic tone family. These are NOT bright or saturated — they are desaturated, earthy tints that feel like pressed-flower pigments.

| Domain | Accent Tint (bg) | Accent Dark (icon/border) | Selected Gradient |
|---|---|---|---|
| Finance | `#e8f0e3` (sage) | `#3a5c35` | `linear-gradient(135deg, #edf5e8, #d9ebcf)` |
| Health | `#fce8e4` (clay rose) | `#8b4a3a` | `linear-gradient(135deg, #fdf0ed, #f5ddd6)` |
| Habits | `#e4edf5` (pressed lavender) | `#3a5272` | `linear-gradient(135deg, #edf2f8, #d6e3f0)` |
| Skills | `#f5f0e4` (aged parchment) | `#6b5a35` | `linear-gradient(135deg, #f8f3eb, #ede4d0)` |

**Usage rules:**
- Domain accents are used for icon containers, selected card backgrounds, and border highlights — never for text, buttons, or large surface fills.
- The accent dark value is used for the domain icon colour when selected and for the 2px selection border on cards.
- All domain accents must feel "found in nature" — think dried botanicals, mineral pigments, stained paper. No neon, no saturated primaries.
- When a card is unselected, it uses `surface-container-lowest` (#ffffff) with the standard sage palette. Domain colour only appears on selection.
- Primary actions (buttons, links, CTAs) always remain in the core `primary` (#4b6646) palette regardless of domain context.

### Dark Surface Tokens

Used for sidebar, footer, and dark feature sections (e.g., inquiry demo, hero accents):

| Token | Hex | Usage |
|---|---|---|
| `dark` | #1a1f1a | Dark section background (muted forest, never pure black) |
| `dark-text-active` | #a8c4a0 | Active text on dark surfaces (sage-tinted, not bright emerald) |
| `dark-text-inactive` | #5a6857 | Inactive/secondary text on dark surfaces |
| `dark-accent` | #6b8f65 | Accent lines, progress bars, brand mark on dark |

### The "No-Line" Rule

**Standard 1px borders are prohibited for sectioning or card definition.** Boundaries must be defined solely through background color shifts. A `surface-container-low` section sitting on `background` creates a soft, natural break — like the edge where handmade paper meets the desk.

### Surface Hierarchy & Nesting

Treat the UI as stacked organic materials. Each step creates depth without noise:

- **Base:** `background` (#f8faf2) — the desk
- **Sections:** `surface-container-low` (#f1f5eb) — the laid-out sheet
- **Cards:** `surface-container-lowest` (#ffffff) — the specimen card, elevated
- **Active/Hover:** `surface-container-high` (#e5eade) — the pressed area, recessed

### Glassmorphism

For floating elements (navigation bars, modals, notification cards, overlays):

- **Fill:** `background` (#f8faf2) at 75% opacity
- **Blur:** `backdrop-filter: blur(8px)` — crisp, not mushy. 8px is deliberate: editorial clarity, not dreamscape blur.
- **Inner border:** 1px solid white at 20% opacity (the "frost line")

Do NOT use 12px+ blur. The glass should feel like looking through a frosted specimen slide, not a foggy window.

### Signature Gradients & Textures

Primary CTAs and hero backgrounds use a subtle linear gradient from `primary` (#4b6646) to `primary-dim` (#3f5a3a) at 135deg. This prevents flat, web-native feeling and adds "soulful" depth.

Use gradients for:
- Primary pill buttons (subtle, 135deg)
- Hero section accents
- Circular hero borders (primary → primary-container)
- Dark section overlays (dark → slightly lighter dark)

Never use gradients for body text, cards, or input fields. Gradients are reserved for moments of emphasis.

---

## 3. Typography: The Editorial Voice

Typography is the primary tool for conveying "premium sanctuary" vibes. The pairing creates immediate editorial authority.

### Font Pairing

- **Newsreader — "The Authority" (serif):** Headlines, display text, pull-quotes, editorial moments. Its varying stroke weights convey archival, journalistic integrity. Conveys feeling.
- **Manrope — "The Guide" (sans-serif):** Body text, labels, UI elements, buttons. Its geometric but friendly construction ensures legibility. Conveys function.

### Hierarchy Rules

| Level | Font | Weight | Tracking | Usage |
|---|---|---|---|---|
| Display | Newsreader | Light (300) | -0.03em | Hero headlines, page titles |
| Headline | Newsreader | Regular (400) | -0.03em | Section headers, card titles |
| Headline Italic | Newsreader | Regular Italic | -0.03em | Brand mark, pull-quotes, editorial moments |
| Micro-label | Manrope | Bold (700), Uppercase | +0.05em | Category tags, metadata, step labels |
| Body | Manrope | Regular (400) | Normal | Descriptions, paragraphs (line-height: 1.65) |
| Label | Manrope | Bold (700) | Normal | Button text, form labels |

### Key Rules

- Newsreader headlines MUST use `-0.03em` letter-spacing. This tightness is critical — it transforms a standard serif into a custom brand mark.
- Display headlines use Newsreader **Light** (300), not Bold. Thin strokes on large type = editorial elegance. Bold Newsreader at display size looks like a newspaper, not a magazine.
- Pair a `font-light` Newsreader headline with a **bold uppercase** Manrope micro-label above it (e.g., "CHAPTER ONE" above "The Curator's Sanctuary"). This creates the editorial "locked-in" feel.
- Never use Newsreader for body text. Large blocks of serif at small sizes increase eye fatigue. Manrope is for reading; Newsreader is for feeling.
- Use italic Newsreader for decorative/editorial moments only — brand text, pull-quotes, archival labels. CTAs and action text should be upright.
- Use `primary` (#4b6646) for Newsreader headlines to maintain the botanical theme. Reserve `on-surface` (#2e342b) for Manrope body text.

### The Pull-Quote Pattern

In data-heavy pages, break the visual rhythm with a Newsreader pull-quote:
- Newsreader Italic, larger than surrounding body text
- `primary` (#4b6646) color
- Generous vertical margin (3rem+)
- Optional decorative left border in `primary-container` (#ccebc2), 3px wide

This is a "Moment of Wonder" — it reminds the user they're in a curated experience, not a spreadsheet.

---

## 4. Elevation & Depth: Atmospheric Layering

We do not use generic drop shadows. We use **ambient tinted shadows** that feel like light passing through sage-tinted air.

### Tonal Layering (Primary Method)

Place `surface-container-lowest` (#ffffff) cards on `surface-container-low` (#f1f5eb) backgrounds. The color shift alone provides visual affordance without borders or shadows. This is always the first choice.

### Tinted Ambient Shadows

When a float is needed, use shadows tinted with `on-surface` (#2e342b):

| Context | Shadow | Notes |
|---|---|---|
| Cards (resting) | `0 8px 24px rgba(46, 52, 43, 0.06)` | Subtle lift |
| Cards (hover) | `0 30px 60px rgba(46, 52, 43, 0.08)` + `translateY(-2px)` | Hover lift |
| Floating elements | `0 20px 40px rgba(46, 52, 43, 0.06)` | Modals, popovers |
| Primary buttons | `0 4px 20px rgba(46, 52, 43, 0.18)` | Resting |
| Primary buttons (hover) | `0 10px 34px rgba(46, 52, 43, 0.24)` | Hover lift |

Never use pure grey shadows (`rgba(0, 0, 0, ...)`). If the shadow looks like a default Photoshop drop shadow, it's wrong. It should feel like a soft sage-tinted mist — light passing through a cloud, not cast by a spotlight.

### Ghost Borders

When a container sits on the same background color and needs definition, use `outline-variant` (#adb4a8) at 15–20% opacity. Never 100% opaque borders. This is the "ghost border" — present enough for accessibility, invisible enough to maintain the no-line aesthetic.

---

## 5. Components

### Cards: The "Clipped Specimen"

The signature component. Every card uses a sharp top-left corner with the remaining three corners rounded — like a botanical specimen clipped to a collector's page:

```css
border-radius: 0 16px 16px 16px; /* TL: sharp, TR/BR/BL: 16px */
```

- **Implementation:** Use `border-top-left-radius: 0` with `border-radius: 16px`. Do NOT use `clip-path` — it removes clickable area and clips content.
- **Fill:** `surface-container-lowest` (#ffffff) on light backgrounds. `rgba(255, 255, 255, 0.05)` on dark backgrounds (inverted variant).
- **Borders:** None. Use tonal layering for definition.
- **Padding:** 2rem internal padding minimum — content must breathe.
- **Hover:** Shadow deepens from 0.06 → 0.08 opacity + `translateY(-2px)`. Transition: 220ms ease.

The sharp top-left corner is the system's visual signature. Rounding it turns the design back into a generic template.

### Buttons: The Pill

All buttons MUST be `rounded-full` (pill shape). No square or slightly-rounded buttons. No exceptions.

- **Primary:** `rounded-full`. Gradient from `primary` to `primary-dim` at 135deg. White text (Manrope Bold). Tinted shadow (`0 4px 20px rgba(46, 52, 43, 0.18)`). Hover: shadow deepens + `translateY(-2px) scale(1.025)`.
- **Secondary:** `rounded-full`. `surface-container-highest` (#dee5d7) background. `on-surface` (#2e342b) text. No shadow at rest; subtle lift on hover.
- **Ghost/Tertiary:** Manrope Bold, Uppercase, +0.05em tracking. No background. Hover: opacity drops to 0.7. Use for secondary navigation, "Learn more" links.
- **Accent (rare):** `rounded-full`. `accent-coral` (#e8735c) fill. White text. Use sparingly — only for high-priority "human" actions (Save, Focus, Confirm).

### Sidebar: Muted Forest Frame

The sidebar uses a **muted dark forest tone** (#1a1f1a) — warm enough to feel organic, dark enough to create contrast, but NOT pure black.

- **Background:** `dark` (#1a1f1a)
- **Brand:** Newsreader italic in `dark-accent` (#6b8f65)
- **Active item:** 2px left border in `dark-accent`, text in `dark-text-active` (#a8c4a0), subtle `rgba(107, 143, 101, 0.08)` background tint
- **Inactive items:** `dark-text-inactive` (#5a6857), hover brightens to `dark-text-active`
- **Progress bar:** `dark-accent` fill on dark track
- **Key principle:** The sidebar should recede — frame the content like a book cover, not compete with it. No bright emerald greens.

### Dark Sections

Any dark-background section (footer, dark feature demos, hero accents) follows the same dark token set:

- **Background:** `dark` (#1a1f1a)
- **Primary text:** `dark-text-active` (#a8c4a0)
- **Secondary text:** `dark-text-inactive` (#5a6857)
- **Cards on dark:** Inverted variant — `rgba(255, 255, 255, 0.05)` fill, no shadow, clipped specimen corners preserved.
- **Links on dark:** `dark-text-active`, hover brightens slightly.

### Input Fields

- **Background:** `surface-container-lowest` (#ffffff)
- **Border:** Ghost border — `outline-variant` at 20% opacity
- **Focus:** Ghost border disappears, replaced by 2px `primary` ring/glow
- **Labels:** Micro-label style (Manrope, Bold, Uppercase, +0.05em) positioned 8px above the field
- **Radius:** 4px (subtle rounding, NOT pill — inputs are functional, not decorative)

### Selection Cards

For multi-select or single-select flows (onboarding, settings, filters):

- **Shape:** Clipped specimen (`border-radius: 0 16px 16px 16px`)
- **Unselected:** `surface-container-lowest` (#ffffff), tinted shadow (`0 2px 12px rgba(46, 52, 43, 0.05)`)
- **Selected:** Domain-specific gradient background (see Domain Accent Palette) with 2px `accent-dark` border. Shadow deepens to `0 6px 24px rgba(46, 52, 43, 0.1)`.
- **Check indicator:** 24px circle, top-right corner. Unselected: ghost border (`outline-variant` at 30%). Selected: filled with `accent-dark`, white checkmark, pop animation (scale 0 → 1.2 → 1, 300ms).
- **Icon container:** Rounded square (16px radius). Unselected: `accent-tint` bg, `on-surface-variant` icon. Selected: `accent-dark` at 10% bg, `accent-dark` icon.
- **Text:** Title in `on-surface` (#2e342b) Manrope Bold 700. Description in `outline` (#767d72) Manrope Regular.
- **Hover:** `translateY(-3px)`, shadow deepens to `0 16px 40px rgba(46, 52, 43, 0.1)`. 300ms ease.
- **Entrance:** Staggered `cardEntrance` animation (opacity 0→1, translateY 20→0, scale 0.96→1) with 80ms delay between cards.

### Processing & Transition Screens

For loading, processing, and "setting up" moments — these are editorial Moments of Wonder:

- **Layout:** Full-viewport centered, no sidebar, `background` (#f8faf2)
- **Hero Orb:** 120px circle, gradient fill (`#e3f0dc → #ccebc2 → #d6e8ce`), tinted shadow (`0 8px 40px rgba(75, 102, 70, 0.2)`). Two pulsing rings (1.5px `primary` at 15% opacity) at -4px and -12px inset. Core breathes (scale 1→1.05, 4s ease-in-out infinite). Leaf icon inside.
- **Discovery Chips:** Pill-shaped (`rounded-full`), glassmorphic (`rgba(255,255,255,0.8)`, `backdrop-filter: blur(8px)`, `1px solid rgba(255,255,255,0.3)`). Cycle through active state with `primary-container` tint. Content: micro-label status ("FOUND", "ANALYZING") + Manrope 600 label.
- **Headline:** Newsreader Regular Italic, `primary` (#4b6646), `-0.03em` tracking. Use evocative editorial copy ("Listening to the Archive...").
- **Progress Bar:** 200px wide, 4px track in `primary` at 10% opacity. Fill: gradient `primary → dark-accent` (#4b6646 → #6b8f65). Glow animation on fill.
- **Status Cards:** Two-column grid, clipped specimen corners. One light (`surface-container-lowest`, sage tokens), one dark (`on-surface` #2e342b, dark tokens). Status badges in pills: light uses `primary-container` bg, dark uses `dark-accent` at 20% bg.
- **Particles:** 12 floating 6px circles in `primary` at 20% opacity, rising from bottom 20% with staggered delays. Purely decorative.

### Chips & Tags

- **Shape:** `rounded-full` (pill)
- **Background:** `secondary-container` (#d6e8ce)
- **Text:** `on-secondary-container` (#465642), Micro-label style
- **Status chips:** Contextual background with micro-label text (e.g., sage-100 for "Connected", coral-50 for "Pending")

### Lists & Dividers

**Divider lines are forbidden.** Separate list items using 1.2rem vertical spacing. If more distinction is needed, use alternating background tints or Newsreader micro-headers to categorize groups.

---

## 6. Layout Patterns

### Landing Page

Full-width sections with alternating backgrounds (`background` → `surface-container-low`) to create rhythm. The page should feel like flipping through an exhibition catalog — each section a new gallery room.

**Section Flow:**

1. **NavBar:** Glassmorphism container, fixed. Brand in Newsreader Italic `primary`. CTA is primary pill button.

2. **Hero:** Two-column split. Left: italic display headline (Newsreader Light Italic, -0.03em) with micro-label badge above, dual CTAs (primary pill + secondary pill with icon). Right: contained gradient image area (`primary` → `primary-dim` → dark forest) with parallax floating specimen cards. Ambient gradient decoration (`primary-container` at 20% opacity, blurred) in background.

3. **Domain Showcase:** 4-column grid of domain cards on `surface-container-low`. Each card has a colored icon circle (alternating `primary-container`, `secondary-container`, `accent-coral` tint) with hover color inversion. Alternating cards offset vertically by 32px to break rigid alignment. Cards use isometric perspective at rest, flattening on hover (see Motion section). Footer stat line separated by `surface-container-low` tinted border.

4. **Inquiry Bento Grid:** Asymmetric bento layout (7fr + 5fr) on `background`. Left: main Card with example question, pull-quote styled answer (decorative 4px left border in `primary`), and dual source/reference blocks in tinted backgrounds. Right: two stacked cards — top uses primary gradient fill ("sanctuary" card), bottom uses `primary-container` fill ("protocol" card with verification icon).

5. **Timeline Storytelling:** Two-column layout on `surface-container-low`. Left: white container with two overlapping card previews — one white (rotated -3deg, date badge in `accent-coral` tint), one primary-gradient (rotated +3deg). Cards flatten on hover. Right: italic Newsreader headline ("Your life isn't a list. It's a story."), icon-led feature descriptions below.

6. **Call-to-Action:** Full-width rounded card (20px radius) in primary gradient (135deg). Decorative serif quote mark at reduced opacity. Italic Newsreader headline in white. Tally form in glassmorphic inner container. Italic serif footnote.

7. **Footer:** `dark` background. Active links `dark-text-active`, inactive `dark-text-inactive`.

**Responsive Breakpoints:**

The landing page is responsive across three breakpoints. The `useBreakpoint()` hook (at `frontend/components/landing/hooks/useBreakpoint.ts`) returns `'mobile' | 'tablet' | 'desktop'` and all sections adapt their inline styles accordingly. Responsive spacing tokens live in `tokens.ts`.

| Breakpoint | Range | Purpose |
|---|---|---|
| `mobile` | 0–639px | Phones (portrait + landscape) |
| `tablet` | 640–1023px | Tablets, small laptops |
| `desktop` | 1024px+ | Current design target |

**Per-Section Responsive Behavior:**

| Section | Mobile | Tablet | Desktop |
|---|---|---|---|
| NavBar | Hamburger menu with slide-down overlay; language toggle stays inline | Reduced horizontal padding | Full button row |
| Hero | Single column (text above image); floating cards hidden; image aspect ratio 4:3; reduced animation distance | Single column; floating card shown inline (no parallax); glass badge hidden | Two-column split with parallax floating cards |
| Domain Showcase | 1-column grid; no isometric tilt; no hover effects | 2-column grid; no tilt | 4-column grid with isometric perspective + hover |
| Inquiry Bento | Single column; source/reference blocks stack vertically; no minHeight | Single column; sidebar cards side-by-side (1fr 1fr) | 7fr/5fr bento grid |
| Timeline | Column-reverse (text first, card preview below); 16:10 aspect ratio | Same stacking order; medium gap | Side-by-side two-column layout |
| CTA/Waitlist | Reduced padding; full-width form container | Medium padding | Full desktop spacing |
| Footer | Stacked vertically, centered | Row with wrap | Row with space-between |

**Responsive Rules:**

- **Section padding** scales: `120px 48px` (desktop) → `80px 32px` (tablet) → `60px 20px` (mobile). These are codified in `spacing.sectionPadding` tokens.
- **ParallaxLayer** is disabled on tablet/mobile (renders plain `div` via `disabled` prop). Scroll-linked transforms cause jank on touch devices and break layout at narrow widths.
- **Isometric card perspective** (`rotateX/rotateY`) is desktop-only. On touch devices, hover effects are unreachable and the `translateY(32px)` offset wastes vertical space.
- **ScrollReveal animation distance** is reduced on mobile (12–16px instead of 20–40px) to prevent large slide-up jumps on small screens.
- **`clamp()` font sizes** are already partially responsive; mobile overrides further tighten the range where needed (e.g., hero headline uses `clamp(2rem, 8vw, 3rem)` on mobile).

### Auth Pages (Login/Register)

Asymmetric two-column split (5/7 grid):
- **Left:** Editorial headline in Newsreader, body text, decorative "overhanging" botanical illustration card (rotated 2deg, breaking its container bounds)
- **Right:** Form card on `surface-container-lowest` with social OAuth buttons, email/password inputs, gradient primary CTA

### App Shell

- **Sidebar:** Persistent left sidebar (muted forest). See Sidebar section above.
- **Top bar:** Glassmorphism header with brand + utility icons
- **Content:** Scrollable main area on `background` with generous whitespace
- **Cards:** Clipped specimen cards for domain summaries, insights, data views

### Onboarding Pages

- **Layout:** No sidebar. Centered single-column content (max-width 560px) on `background`.
- **Step indicator:** Pill-shaped progress dots (8px inactive, 36px active) with gradient fill (`primary → dark-accent`). Centered above headline.
- **Step label:** Micro-label pattern ("STEP 1 OF 2") above Newsreader Light (300) headline.
- **Content:** Scrollable main area with generous whitespace. Padding: `40px 24px 140px` (bottom space for fixed bar).
- **Bottom bar:** Fixed glassmorphic footer (`background` at 85% opacity, `backdrop-filter: blur(8px)`, `1px solid rgba(255,255,255,0.2)` frost line). Back (ghost pill) + Continue (primary gradient pill). Shadow: `0 -4px 20px rgba(46, 52, 43, 0.04)`.
- **Step transitions:** Fade + slide (opacity + translateY 8px). 250ms ease. Direction-aware (slides right going forward, left going back).

**Step 1 — Domain Selection:**
- 2-column grid of Selection Cards (see Selection Cards component). Each domain shows icon, title, description.
- Selection counter pill below grid when ≥1 selected.

**Step 2 — Calendar Source:**
- Stacked Selection Cards (single-column). Calendar, Cloud, ArrowRight icons. Same selection pattern as Step 1.

**Step 3 — Processing:**
- Full Processing & Transition Screen (see Processing Screens component). "Listening to the Archive..." editorial moment.
- Auto-advances after 5 seconds. Redirects to `/calendar`.

---

## 7. Interaction & Motion

Motion should feel organic and unhurried — like leaves settling, not like UI snapping into place.

### Card & Element Motion

| Element | Animation | Duration | Easing |
|---|---|---|---|
| Card entrance | Stagger with 50ms delay between cards | 300ms | ease-out |
| Card hover | Shadow deepens + `translateY(-2px)` | 220ms | ease |
| Primary button hover | Gradient shift + shadow deepens + `translateY(-2px) scale(1.025)` | 180ms | ease |
| Ghost button hover | Opacity → 0.7 | 180ms | ease |

### Float Animations (Landing/Decorative)

Gentle vertical floating for decorative cards and illustrations:

```css
@keyframes floatA { 0%, 100% { translateY(0) } 50% { translateY(-9px) } }  /* 4.6s */
@keyframes floatB { 0%, 100% { translateY(0) } 50% { translateY(-6px) } }  /* 5.4s, 1s delay */
@keyframes floatC { 0%, 100% { translateY(0) } 50% { translateY(-11px) } } /* 4.0s, 1.8s delay */
```

Use staggered delays to prevent synchronized motion. Each floating element should feel independent.

### Scroll-Triggered Animations (Landing Page)

Entrance animations fire once when elements enter the viewport (framer-motion `whileInView` + `viewport: { once: true }`):

| Element | Animation | Duration | Easing |
|---|---|---|---|
| ScrollReveal | Fade in + slide up (32px default) | 600ms | cubic-bezier(0.25, 0.1, 0.25, 1) |
| StaggerChildren | Container staggers children entrance | Per-child: 500ms | Same |
| ParallaxLayer | Y-offset linked to scroll progress | Continuous | Linear |

Stagger delays: 100–150ms between siblings for grids, 50ms for dense lists (tag pills). Parallax speeds: positive = background feel (slower), negative = foreground feel (faster). Range: 20–40px.

### Isometric Card Hover (Landing Page)

For domain showcase cards, use isometric perspective at rest that flattens on hover:

- **Rest:** `perspective(1000px) rotateX(2deg) rotateY(-2deg)` with `floating` shadow
- **Hover:** `perspective(1000px) rotateX(0) rotateY(0) translateY(-8px)` with `cardHover` shadow
- **Transition:** 400ms ease

This creates a "museum display case" depth effect.

### Overlay & Modal Motion

- **Enter:** Fade in (opacity 0→1) + slight scale (0.97→1). 200ms ease-out.
- **Exit:** Fade out + scale down. 150ms ease-in.
- **Backdrop:** Fade in with subtle blur increase. 200ms.

### What NOT to Animate

- Decorative blur circles — atmospheric, static only
- Background color shifts between sections — these are structural, not transitional
- Body text — never animate text entrance for reading content

---

## 8. Do's and Don'ts

### Do:

- **Do** embrace generous whitespace. If a layout feels "empty," leave it — space is a luxury, not a bug.
- **Do** overlap illustrations with text blocks to create depth and break the rigid grid. Offset headers and images for an editorial "scrapbook" flow.
- **Do** use Newsreader for editorial "Moments of Wonder" — pull-quotes, archival labels, decorative headings that break the functional rhythm.
- **Do** use the micro-label pattern (Manrope Bold, Uppercase, +0.05em) for metadata, category tags, and step labels.
- **Do** keep body text and descriptions within the sage-tinted palette (`on-surface-variant` #5a6157). Never drift to neutral zinc/slate grays.
- **Do** use `accent-coral` (#e8735c) only for "human" moments — notifications, hearts, active confirmations.
- **Do** treat dark sections as inverted sanctuaries — same visual language (clipped corners, tonal layering, tinted shadows), just on dark tokens.

### Don't:

- **Don't** use 1px borders for sections. Background color shifts only.
- **Don't** use pure #000000. Use `on-surface` (#2e342b) for all "dark" text.
- **Don't** use standard grey drop shadows (`rgba(0,0,0,...)`). Shadows must be tinted with `on-surface` (`rgba(46,52,43,...)`).
- **Don't** round the top-left corner of cards. The clipped specimen is the system's signature.
- **Don't** use `clip-path` for the clipped corner. Use `border-top-left-radius: 0` only.
- **Don't** use bright emerald/lime greens anywhere. Keep greens muted and sage-tinted.
- **Don't** use Newsreader for body text or small-size paragraphs. Serif at body size = eye fatigue.
- **Don't** use square or slightly-rounded buttons. All buttons are pills (`rounded-full`).
- **Don't** use `backdrop-blur` values above 8px. Crisp glass, not foggy windows.
- **Don't** align everything to a rigid center-grid. Offset images and headers for editorial rhythm.
- **Don't** use bright, saturated, or non-botanical accent colors. Domain accents (see Domain Accent Palette) are the only permitted departures from sage — and they must feel like pressed-flower pigments, not UI primaries.
