# PUBLIC_TDEE_TOOL_SPEC.md

**Status:** Ready for execution
**Author:** Opus 4.6 (Architect)
**Executor:** Sonnet 4.6
**Date:** 2026-03-30

---

## 0. Build Philosophy & Strategic Decisions

### 0.1 Purpose

This tool is a **public, unauthenticated TDEE/BMR calculator** at `/tools/tdee`. It serves as a demand-testing funnel: visitors compute their calorie targets using the same clinical math LifeOS uses internally, then see a conversion CTA directing them to `https://taeyangcv.vercel.app/` or the LifeOS login page.

### 0.2 Strategic Decision: Component Decoupling

**Decision: Extract stateless "Specimen" components. Do NOT refactor existing authenticated components.**

The existing `CalculatorForm.tsx` and `ReportCard.tsx` are tightly coupled to:
- Auth-specific props (`editingReport`, `isEditMode`, `save_profile`)
- Translation objects (`HealthPageTranslations`)
- Prefill data from authenticated APIs
- The `CalorieReport` type (which includes `id`, `created_at` — DB fields)

**Approach:**
1. Create new **standalone components** under `frontend/app/tools/tdee/_components/` that duplicate the visual design but strip all auth, persistence, and editing concerns.
2. The public form component handles its own local state and calls a **client-side compute function** for instant results. The backend API call is a secondary validation/canonical-result path.
3. The existing `(app)/health/` components remain untouched. No shared component extraction — the coupling overhead exceeds the DRY benefit for two components.

**Rationale:** The public tool is a marketing surface with a distinct lifecycle from the internal health dashboard. Tying them together creates a coupling risk where changes to the authenticated experience (new features, prefill, edit mode) break the public funnel. Two separate implementations sharing the same backend math is the correct trade-off.

### 0.3 Strategic Decision: API Exposure

**Decision: Create `POST /api/v1/public/health/calculate` — stateless, no JWT, aggressive rate limiting.**

- The endpoint calls the existing `calculator_service.calculate()` function (pure, no side effects) and `calculator_service.get_warnings()`.
- It does NOT call `create_report()`, `save_health_profile()`, or any DB-writing function.
- Rate limit: **30 requests per minute per IP** (via `flask-limiter`, already installed). This is 10x below the authenticated default and sufficient for legitimate use.
- The endpoint reuses the existing `CalculatorInput` Pydantic schema, minus the `save_profile` field.

### 0.4 Strategic Decision: Funnel Logic

**Decision: State is carried via URL query parameters, not session storage.**

When the user clicks the "Save your results" CTA, the tool encodes the computed result summary (TDEE, daily calories, goal type) into URL search params and redirects to `https://taeyangcv.vercel.app/` (or a future `/login?from=tdee&tdee=2400&goal=lose` path when LifeOS self-registration launches). This is stateless, shareable, and works across devices.

### 0.5 Client-Side Compute vs. API

**Decision: Primary compute happens client-side. API is optional validation.**

The Mifflin-St Jeor and Katch-McArdle formulas are deterministic arithmetic. The public tool will implement the math in TypeScript for instant results (no network latency, no spinner). The API endpoint exists for:
- Canonical validation (backend is source of truth)
- Future analytics (counting compute requests without storing PII)
- Parity testing in CI

The client-side TypeScript module must mirror `calculator_service.py:calculate()` exactly.

---

## 1. Architectural Changes (Stateless Refactoring)

### 1.1 No Changes to Existing Files

The following files are **read-only** for this feature:

| File | Reason |
|---|---|
| `lifeos/domains/health/services/calculator_service.py` | Source of truth. Called by new public controller. Not modified. |
| `lifeos/domains/health/schemas/calculator_schemas.py` | `CalculatorInput` schema reused. Not modified. |
| `frontend/app/(app)/health/_components/calculator/CalculatorForm.tsx` | Authenticated component. Not touched. |
| `frontend/app/(app)/health/_components/calculator/ReportCard.tsx` | Authenticated component. Not touched. |
| `frontend/app/(app)/layout.tsx` | Auth-gated layout. Not touched. |
| `frontend/lib/api/calculator.ts` | Auth-wrapped API client. Not touched. |
| `frontend/lib/api/client.ts` | Auth-aware fetch. Not touched. |

### 1.2 New File Inventory

| # | File | Type | Purpose |
|---|---|---|---|
| B1 | `lifeos/domains/health/schemas/public_calculator_schemas.py` | Backend Schema | Pydantic DTO for public endpoint (no `save_profile`) |
| B2 | `lifeos/domains/health/controllers/public_calculator_api.py` | Backend Controller | Public endpoint with rate limiting |
| B3 | `lifeos/__init__.py` | Backend Registration | Add blueprint registration (one line) |
| F1 | `frontend/app/tools/layout.tsx` | Frontend Layout | Public layout (no auth, no sidebar) |
| F2 | `frontend/app/tools/tdee/page.tsx` | Frontend Page | TDEE tool page with SEO metadata |
| F3 | `frontend/app/tools/tdee/_components/TdeeCalculatorForm.tsx` | Frontend Component | Public calculator form |
| F4 | `frontend/app/tools/tdee/_components/TdeeReportCard.tsx` | Frontend Component | Public result display |
| F5 | `frontend/app/tools/tdee/_components/ConversionCta.tsx` | Frontend Component | "Join LifeOS" CTA footer |
| F6 | `frontend/app/tools/tdee/_components/ToolsHeader.tsx` | Frontend Component | Minimal branded header |
| F7 | `frontend/lib/tdee-calculator.ts` | Frontend Utility | Client-side TDEE/BMR compute (mirrors backend) |

---

## 2. Backend Spec (Public Endpoint + Rate Limiting)

### 2.1 File: `lifeos/domains/health/schemas/public_calculator_schemas.py`

```python
"""Public calculator Pydantic DTOs — no auth-specific fields."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class PublicCalculatorInput(BaseModel):
    """Request body for POST /api/v1/public/health/calculate.

    Identical to CalculatorInput minus save_profile.
    """

    weight_kg: float = Field(gt=0, le=500)
    height_cm: float = Field(gt=0, le=300)
    age_years: int = Field(ge=1, le=120)
    gender: Literal["male", "female"]
    body_fat_pct: Optional[float] = Field(default=None, ge=0, le=80)
    activity_level: Literal[
        "sedentary", "lightly_active", "moderately_active", "very_active", "extra_active"
    ]
    goal_type: Literal["lose", "gain", "maintain"]
    goal_weight_kg: Optional[float] = Field(default=None, gt=0, le=500)
    goal_timeline_months: Optional[int] = Field(default=None, ge=1, le=120)

    @model_validator(mode="after")
    def validate_goal_fields(self):
        if self.goal_type in ("lose", "gain"):
            if self.goal_weight_kg is None:
                raise ValueError("goal_weight_kg is required when goal_type is 'lose' or 'gain'")
            if self.goal_timeline_months is None:
                raise ValueError("goal_timeline_months is required when goal_type is 'lose' or 'gain'")
        return self
```

### 2.2 File: `lifeos/domains/health/controllers/public_calculator_api.py`

```python
"""Public (unauthenticated) calorie calculator API controller."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from pydantic import ValidationError

from lifeos.domains.health.services import calculator_service
from lifeos.domains.health.schemas.public_calculator_schemas import PublicCalculatorInput
from lifeos.extensions import limiter

public_calculator_api_bp = Blueprint("public_calculator_api", __name__)


@public_calculator_api_bp.post("/calculate")
@limiter.limit("30 per minute")
def public_calculate():
    """
    Run the calorie calculator and return results.

    - No JWT required.
    - No report persistence.
    - No event emission.
    - Rate-limited to 30/min per IP.
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = PublicCalculatorInput.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    computed = calculator_service.calculate(
        weight_kg=data.weight_kg,
        height_cm=data.height_cm,
        age_years=data.age_years,
        gender=data.gender,
        body_fat_pct=data.body_fat_pct,
        activity_level=data.activity_level,
        goal_type=data.goal_type,
        goal_weight_kg=data.goal_weight_kg,
        goal_timeline_months=data.goal_timeline_months,
    )

    warnings = calculator_service.get_warnings(
        gender=data.gender,
        daily_calories=computed["daily_calories"],
        tdee=computed["tdee"],
        goal_type=data.goal_type,
    )

    return jsonify({"ok": True, "result": computed, "warnings": warnings}), 200
```

**Key differences from authenticated endpoint:**
- No `@jwt_required()` decorator
- No `@csrf_protected` decorator
- No `create_report()` call
- No `save_health_profile()` call
- No `map_calorie_report()` — returns raw compute dict as `result` (not `report`)
- Rate-limited to 30/min (vs. default 200/hour for authenticated)
- Returns HTTP 200 (not 201 — nothing was created)

### 2.3 Blueprint Registration in `lifeos/__init__.py`

Add to the `_register_blueprints()` function, near line 292 (after the existing calculator blueprint):

```python
from lifeos.domains.health.controllers.public_calculator_api import public_calculator_api_bp
# ... (in the registration block):
app.register_blueprint(public_calculator_api_bp, url_prefix="/api/v1/public/health/calculator")
```

**URL prefix:** `/api/v1/public/health/calculator`
**Full endpoint:** `POST /api/v1/public/health/calculator/calculate`

The `/public/` segment in the URL makes it obvious this is unauthenticated. This is a naming convention, not a middleware boundary — the lack of `@jwt_required()` is what makes it public.

### 2.4 CORS Note

No CORS changes required. The existing CORS config allows requests from all configured frontend origins. The `/api/v1/public/` path is under the same Flask app and inherits the same CORS policy.

---

## 3. Frontend Component Registry

### 3.1 Directory Structure

```
frontend/
├── app/
│   ├── (app)/           # Existing — NOT TOUCHED
│   ├── (auth)/          # Existing — NOT TOUCHED
│   └── tools/           # NEW — Public tools (no auth)
│       ├── layout.tsx           # [F1] Public layout shell
│       └── tdee/
│           ├── page.tsx         # [F2] TDEE tool page
│           └── _components/
│               ├── TdeeCalculatorForm.tsx   # [F3] Form
│               ├── TdeeReportCard.tsx       # [F4] Results
│               ├── ConversionCta.tsx        # [F5] CTA
│               └── ToolsHeader.tsx          # [F6] Header
├── lib/
│   └── tdee-calculator.ts       # [F7] Client-side compute
```

### 3.2 Type Definitions

The public tool uses its own types, defined inline in `frontend/lib/tdee-calculator.ts`:

```typescript
/** Input for TDEE/BMR calculation — mirrors backend PublicCalculatorInput. */
export interface TdeeInput {
  weight_kg: number
  height_cm: number
  age_years: number
  gender: 'male' | 'female'
  body_fat_pct: number | null
  activity_level: 'sedentary' | 'lightly_active' | 'moderately_active' | 'very_active' | 'extra_active'
  goal_type: 'lose' | 'gain' | 'maintain'
  goal_weight_kg: number | null
  goal_timeline_months: number | null
}

/** Output from TDEE/BMR calculation — mirrors backend calculator_service.calculate() return. */
export interface TdeeResult {
  method_used: 'mifflin_st_jeor' | 'katch_mcardle'
  lean_body_mass: number | null
  bmr: number
  activity_multiplier: number
  tdee: number
  delta_bw: number | null
  total_delta_kcal: number | null
  delta_kcal_per_day: number | null
  kcal_per_kg_used: number | null
  daily_calories: number
  protein_g_per_day: number
  fat_g_per_day: number
  carbs_g_per_day: number
  fiber_g_per_day: number
  monthly_calories: number
  monthly_protein_g: number
  monthly_fat_g: number
  monthly_carbs_g: number
  monthly_fiber_g: number
}

export interface TdeeWarning {
  type: string
  message: string
}
```

---

## 4. Surface Specs (Layout + Page + Conversion)

### 4.1 [F1] `frontend/app/tools/layout.tsx` — Public Layout

**Purpose:** Minimal shell for all `/tools/*` pages. No sidebar, no app header, no auth guard.

```
┌────────────────────────────────────────┐
│  [ToolsHeader]                         │
│  "LifeOS Tools" logo → taeyangcv link  │
├────────────────────────────────────────┤
│                                        │
│  {children}                            │
│                                        │
├────────────────────────────────────────┤
│  Footer: "Built by Taeyang" link       │
└────────────────────────────────────────┘
```

**Implementation details:**

```tsx
// frontend/app/tools/layout.tsx
// 'use client' is NOT needed — this is a server component layout.

import { Metadata } from 'next'

export const metadata: Metadata = {
  // Overridden per-page. This is a fallback.
  title: 'LifeOS Tools',
}

export default function ToolsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#f8faf2' }}>
      {/* Header rendered by page-level client components */}
      <main style={{ flex: 1 }}>
        {children}
      </main>
    </div>
  )
}
```

**Key constraints:**
- No `useAuth()`, no `useRouter()` redirect, no `isAuthenticated` check.
- Background: `#f8faf2` (design system `background` token).
- No `AppHeader` / `AppFooter` imports.
- No `Providers` wrapping needed (root layout already wraps all routes).

### 4.2 [F6] `frontend/app/tools/tdee/_components/ToolsHeader.tsx` — Branded Header

```tsx
'use client'

// Minimal header: "LifeOS Tools" brand mark linking to portfolio.
// Glassmorphism per DESIGN.md §5.

// Styles:
// - Position: sticky, top: 0, z-index: 50
// - Background: rgba(248, 250, 242, 0.75) (background at 75% opacity)
// - Backdrop-filter: blur(8px)
// - Inner border: 1px solid rgba(255, 255, 255, 0.2)
// - Height: 56px
// - Max-width: 960px centered
// - Brand: "LifeOS" in Newsreader Italic, color #4b6646, tracking -0.03em
//   followed by "Tools" in Manrope 700, color #5a6157
// - Links to https://taeyangcv.vercel.app/
```

### 4.3 [F2] `frontend/app/tools/tdee/page.tsx` — TDEE Tool Page

**Purpose:** Single-page calculator. Server component for metadata, wraps client component for interactivity.

**Page structure:**

```
┌──────────────────────────────────────────────┐
│ [ToolsHeader] — sticky glassmorphism         │
├──────────────────────────────────────────────┤
│                                              │
│  MICRO-LABEL: "HEALTH TOOLS"                │
│  HEADLINE: "TDEE & BMR Calculator"           │
│    (Newsreader Light 300, -0.03em, #4b6646)  │
│  SUBTITLE: clinical-formula description      │
│    (Manrope 400, #5a6157)                    │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ [TdeeCalculatorForm]                   │  │
│  │  Clipped specimen card (0 16 16 16)    │  │
│  │  White background, tinted shadow       │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ [TdeeReportCard] — shown after submit  │  │
│  │  Entrance animation (reportIn 300ms)   │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  ┌────────────────────────────────────────┐  │
│  │ [ConversionCta] — always visible       │  │
│  │  "Want to track this over time?"       │  │
│  │  Primary gradient pill → signup/login  │  │
│  └────────────────────────────────────────┘  │
│                                              │
│  Footer: "Built by Taeyang" · portfolio link │
└──────────────────────────────────────────────┘
```

**Metadata (server component export):**

```tsx
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'TDEE & BMR Calculator | LifeOS',
  description: 'Accurate daily energy expenditure and macro calculation using clinical formulas. Simple, private, and calm.',
  openGraph: {
    title: 'TDEE & BMR Calculator | LifeOS',
    description: 'Accurate daily energy expenditure and macro calculation using clinical formulas.',
    type: 'website',
    siteName: 'LifeOS',
  },
}
```

**Page component:**

The page.tsx file is a **server component** that exports metadata and renders a single client component `TdeeToolPage` which orchestrates all the interactive pieces:

```tsx
// frontend/app/tools/tdee/page.tsx
import type { Metadata } from 'next'
import TdeeToolPage from './_components/TdeeToolPage'

export const metadata: Metadata = { /* as above */ }

export default function Page() {
  return <TdeeToolPage />
}
```

Wait — this means we need one more client component to orchestrate state. **Revised file list:**

| # | File | Purpose |
|---|---|---|
| F2a | `frontend/app/tools/tdee/page.tsx` | Server component (metadata only) |
| F2b | `frontend/app/tools/tdee/_components/TdeeToolPage.tsx` | Client component (state orchestrator) |

**`TdeeToolPage.tsx` state management:**

```tsx
'use client'

import { useState } from 'react'
import { calculate, getWarnings, type TdeeInput, type TdeeResult, type TdeeWarning } from '@/lib/tdee-calculator'
import ToolsHeader from './ToolsHeader'
import TdeeCalculatorForm from './TdeeCalculatorForm'
import TdeeReportCard from './TdeeReportCard'
import ConversionCta from './ConversionCta'

export default function TdeeToolPage() {
  const [result, setResult] = useState<TdeeResult | null>(null)
  const [warnings, setWarnings] = useState<TdeeWarning[]>([])

  function handleCalculate(input: TdeeInput) {
    const computed = calculate(input)
    const warns = getWarnings({
      gender: input.gender,
      daily_calories: computed.daily_calories,
      tdee: computed.tdee,
      goal_type: input.goal_type,
    })
    setResult(computed)
    setWarnings(warns)
  }

  return (
    <>
      <ToolsHeader />
      <div style={{ maxWidth: 640, margin: '0 auto', padding: '48px 20px 80px' }}>
        {/* Micro-label + Headline */}
        {/* ... (see section 4.3 above for structure) */}

        <TdeeCalculatorForm onCalculate={handleCalculate} />

        {result && (
          <div style={{ marginTop: 32 }}>
            <TdeeReportCard result={result} warnings={warnings} />
          </div>
        )}

        <ConversionCta hasResult={!!result} result={result} />
      </div>
      {/* Footer */}
    </>
  )
}
```

### 4.4 [F3] `frontend/app/tools/tdee/_components/TdeeCalculatorForm.tsx`

**Prop interface:**

```typescript
interface TdeeCalculatorFormProps {
  onCalculate: (input: TdeeInput) => void
}
```

**Visual specification (mirrors existing CalculatorForm):**

- **Card shell:** `background: #ffffff`, `border-radius: 0 16px 16px 16px`, `padding: 32px`, `box-shadow: 0 4px 16px rgba(46,52,43,0.06)`.
- **Micro-labels:** Manrope 700, 0.6875rem, uppercase, +0.05em tracking, `color: #8b4a3a`.
- **Input fields:** `background: #ffffff`, `border: 1px solid rgba(173,180,168,0.2)`, `border-radius: 4px`, Manrope 0.875rem, `color: #2e342b`.
- **Labels:** Manrope 700, 0.75rem, `color: #2e342b`.
- **Segmented controls:** Pill-shaped buttons (`border-radius: 100px`). Selected: `background: #fce8e4`, `color: #8b4a3a`, `outline: 2px solid #4b6646`. Unselected: `background: #f1f5eb`, `color: #5a6157`.
- **Submit button:** Primary gradient pill (`linear-gradient(135deg, #4b6646, #3f5a3a)`), `color: #ffffff`, Manrope 600, `border-radius: 100px`, `min-height: 48px`.
- **Submit label:** "Calculate" (no "Update" or edit-mode variants).

**Fields (in order):**
1. Body Measurements section (micro-label): Weight (kg), Height (cm), Age, Body Fat % (optional)
2. Gender section: Male / Female segmented control
3. Activity Level section: 5-option segmented control (sedentary → extra active)
4. Goal section: Lose / Maintain / Gain segmented control
5. Conditional fields (if lose/gain): Goal Weight (kg), Timeline (months)
6. Calculate button

**Differences from authenticated `CalculatorForm.tsx`:**
- No `prefillData` prop, no `isLoading`/`isCalculating` spinner state, no `editingReport`/`isEditMode`
- No auto-filled field tracking (`autoFilledFields`)
- No `save_profile` field in submit payload
- No `InfoTooltip` components (simplify for public; may add later)
- All labels are hardcoded English strings (no translation system for public tools in v1)

### 4.5 [F4] `frontend/app/tools/tdee/_components/TdeeReportCard.tsx`

**Prop interface:**

```typescript
interface TdeeReportCardProps {
  result: TdeeResult
  warnings: TdeeWarning[]
}
```

**Visual specification (mirrors existing ReportCard):**

- **Hero section:** Daily calorie target in Newsreader Light 300, 2.5rem, `color: #4b6646`. "kcal/day" suffix in Manrope 1rem, `color: #767d72`. Goal type pill below.
- **Warnings:** Clay rose cards (`background: #fdf0ed`, `border-radius: 0 12px 12px 12px`), TriangleAlert icon from lucide-react.
- **BMR Breakdown card:** White, clipped specimen corners, tinted shadow. Rows: Method, Lean Body Mass (if applicable), BMR, Activity Level + multiplier, TDEE, Daily Adjustment (if applicable).
- **Macro Targets card:** 3-column grid (label, daily, monthly×30). Rows: Protein, Fat, Carbs, Fiber, Calories.
- **Delta Breakdown:** Expandable (ChevronDown toggle). Shows delta body weight, kcal/kg assumption, total kcal delta, daily adjustment.

**Differences from authenticated `ReportCard.tsx`:**
- No `isLatest` badge, no `expanded`/`onToggleExpand` collapse mode
- No `created_at` date display (no persistence)
- No `id` field reference
- Props receive `TdeeResult` (raw compute output), not `CalorieReport` (DB entity)
- All labels hardcoded English

### 4.6 [F5] `frontend/app/tools/tdee/_components/ConversionCta.tsx`

**Prop interface:**

```typescript
interface ConversionCtaProps {
  hasResult: boolean
  result: TdeeResult | null
}
```

**Visual specification:**

```
┌─────────────────────────────────────────────────────┐
│  background: linear-gradient(135deg, #f1f5eb, #e8f0e3)
│  border-radius: 0 16px 16px 16px  (clipped specimen)
│  padding: 40px 32px
│  margin-top: 40px
│  text-align: center
│
│  MICRO-LABEL: "LIFEOS"
│  (Manrope 700, 0.6875rem, #4b6646, uppercase)
│
│  HEADLINE: "Want to track this over time?"
│  (Newsreader Light 300, 1.75rem, #4b6646, -0.03em)
│
│  BODY: "LifeOS helps you observe your body
│   composition trends with clinical precision."
│  (Manrope 400, 0.9375rem, #5a6157, line-height 1.65)
│
│  [  Join LifeOS  ]  ← Primary gradient pill button
│  (links to https://taeyangcv.vercel.app/)
│  (if hasResult: appends ?tdee={tdee}&goal={goal})
│
└─────────────────────────────────────────────────────┘
```

**CTA button spec:**
- `background: linear-gradient(135deg, #4b6646, #3f5a3a)`
- `color: #ffffff`
- `border-radius: 100px` (pill)
- `padding: 14px 40px`, `min-height: 48px`
- `font: Manrope 600, 0.9375rem`
- `box-shadow: 0 4px 20px rgba(46,52,43,0.18)`
- Hover: `translateY(-2px) scale(1.025)`, shadow deepens to 0.24 opacity
- `<a>` tag, not `<button>` — this navigates to an external URL.

**URL construction when `hasResult` is true:**

```typescript
const ctaUrl = result
  ? `https://taeyangcv.vercel.app/?ref=tdee&tdee=${Math.round(result.tdee)}&daily=${Math.round(result.daily_calories)}&goal=${result.goal_type ?? 'maintain'}`
  : 'https://taeyangcv.vercel.app/?ref=tdee'
```

### 4.7 Footer (inline in `TdeeToolPage.tsx`)

**Not a separate component.** Rendered at the bottom of `TdeeToolPage`:

```tsx
<footer style={{
  textAlign: 'center',
  padding: '40px 20px',
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.8125rem',
  color: '#767d72',
}}>
  Built by{' '}
  <a
    href="https://taeyangcv.vercel.app/"
    target="_blank"
    rel="noopener noreferrer"
    style={{ color: '#4b6646', fontWeight: 600, textDecoration: 'none' }}
  >
    Taeyang
  </a>
</footer>
```

---

## 5. SEO & Metadata Config

### 5.1 Page Metadata

Defined as a named export in `frontend/app/tools/tdee/page.tsx`:

```typescript
export const metadata: Metadata = {
  title: 'TDEE & BMR Calculator | LifeOS',
  description: 'Accurate daily energy expenditure and macro calculation using clinical formulas. Simple, private, and calm.',
  openGraph: {
    title: 'TDEE & BMR Calculator | LifeOS',
    description: 'Accurate daily energy expenditure and macro calculation using clinical formulas.',
    type: 'website',
    siteName: 'LifeOS',
    // TODO: Add og:image when sage-themed preview image is designed.
    // images: [{ url: '/og/tdee-calculator.png', width: 1200, height: 630 }],
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TDEE & BMR Calculator | LifeOS',
    description: 'Accurate daily energy expenditure and macro calculation using clinical formulas.',
  },
  robots: {
    index: true,
    follow: true,
  },
}
```

### 5.2 Structured Data (JSON-LD)

Add a `<script type="application/ld+json">` block in the page's server component:

```json
{
  "@context": "https://schema.org",
  "@type": "SoftwareApplication",
  "name": "TDEE & BMR Calculator",
  "applicationCategory": "HealthApplication",
  "operatingSystem": "Web",
  "offers": {
    "@type": "Offer",
    "price": "0",
    "priceCurrency": "USD"
  },
  "description": "Accurate daily energy expenditure and macro calculation using Mifflin-St Jeor and Katch-McArdle clinical formulas.",
  "creator": {
    "@type": "Organization",
    "name": "LifeOS"
  }
}
```

Embed in `page.tsx`:

```tsx
export default function Page() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({ /* structured data above */ }),
        }}
      />
      <TdeeToolPage />
    </>
  )
}
```

---

## 6. Boundaries (Forbidden / Required)

### 6.1 FORBIDDEN — Do Not Implement

| # | Boundary | Reason |
|---|---|---|
| F1 | User account creation within the tool | Redirect to external signup only |
| F2 | Persisting public reports to DB | Stateless by design |
| F3 | Emitting domain events from public endpoint | Events are for internal state changes |
| F4 | Social sharing buttons | Explicitly cut from scope |
| F5 | Comparison to other users | No user data available |
| F6 | Ad-tech tracking scripts | Privacy-first; Vercel Analytics is sufficient |
| F7 | Multi-step wizard or onboarding flow | Must be one-page |
| F8 | Importing `useAuth`, `AuthContext`, or any auth module in `/tools/` | Public surface must be auth-free |
| F9 | Importing from `frontend/lib/api/client.ts` in public tool | That client injects JWT headers |
| F10 | Using `apiGet`/`apiPost`/`apiPatch`/`apiDelete` from `@/lib/api/client` | Auth-wrapped; use raw `fetch()` if API needed |
| F11 | Translation system (`useLang`, `getAppTranslations`) for public v1 | English-only first; i18n later |
| F12 | Modifying any file in `frontend/app/(app)/` | Authenticated surface is off-limits |
| F13 | Modifying `calculator_service.py` | Source of truth; read-only |
| F14 | Adding DB migration for this feature | No persistence = no schema changes |
| F15 | `clip-path` for card shapes | DESIGN.md rule: use `border-radius: 0 16px 16px 16px` only |
| F16 | Pure black (#000000) anywhere | Use `#2e342b` (on-surface) |
| F17 | Non-tinted shadows | All shadows must use `rgba(46,52,43,...)` |
| F18 | `backdrop-filter: blur()` above 8px | DESIGN.md: crisp glass, not foggy |

### 6.2 REQUIRED — Must Be Present

| # | Requirement | Verification |
|---|---|---|
| R1 | BMR formula parity with `calculator_service.py:calculate()` | Unit test comparing TS and Python outputs for 5+ input sets |
| R2 | Rate limiting on public endpoint (30/min/IP) | `@limiter.limit("30 per minute")` decorator present |
| R3 | Clipped specimen card corners on all cards | `border-radius: 0 16px 16px 16px` |
| R4 | Primary buttons are pills | `border-radius: 100px` |
| R5 | Newsreader for headlines, Manrope for body | Font-family inspection in all styled elements |
| R6 | No auth imports in `frontend/app/tools/` | Grep verification: no `useAuth`, `AuthContext`, `jwt`, `getTokens` |
| R7 | External links use `target="_blank" rel="noopener noreferrer"` | Security requirement |
| R8 | `<meta>` title and description present | `metadata` export in page.tsx |
| R9 | JSON-LD structured data present | `<script type="application/ld+json">` in page output |
| R10 | Conversion CTA links to `https://taeyangcv.vercel.app/` | Hardcoded URL in ConversionCta |
| R11 | Page loads and computes with JavaScript disabled | No — client-side form requires JS. But metadata/SEO renders server-side. |
| R12 | `min-height: 44px` on all interactive elements | Accessibility touch target requirement |

---

## 7. Dependency Map (Build Order)

```
                    ┌─────────────────────┐
                    │  F7: tdee-calculator │  ← No dependencies. Pure math.
                    │  (lib/tdee-calc.ts)  │     Build FIRST.
                    └──────────┬──────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                 │
              ▼                ▼                 ▼
    ┌─────────────┐  ┌──────────────┐  ┌──────────────┐
    │ B1: Schema   │  │ F6: Header   │  │ F5: CTA      │
    │ (public DTO) │  │ (ToolsHeader)│  │ (ConvCta)    │
    └──────┬──────┘  └──────┬───────┘  └──────┬───────┘
           │                │                  │
           ▼                │                  │
    ┌─────────────┐         │                  │
    │ B2: Controller│        │                  │
    │ (public_api)  │        │                  │
    └──────┬──────┘         │                  │
           │                │                  │
           ▼                │                  │
    ┌─────────────┐         │                  │
    │ B3: Register │        │                  │
    │ (__init__.py) │        │                  │
    └─────────────┘         │                  │
                            │                  │
              ┌─────────────┼──────────────────┘
              │             │
              ▼             ▼
    ┌──────────────┐  ┌──────────────────┐
    │ F3: Form     │  │ F4: ReportCard   │
    │ (TdeeCalcForm)│  │ (TdeeReportCard) │
    └──────┬───────┘  └──────┬───────────┘
           │                 │
           └────────┬────────┘
                    │
                    ▼
           ┌───────────────┐
           │ F2b: TdeeTool │
           │   Page.tsx     │  ← Orchestrator (imports F3, F4, F5, F6, F7)
           └───────┬───────┘
                   │
                   ▼
           ┌───────────────┐
           │ F1 + F2a:     │
           │ Layout + Page │  ← Server components (metadata, layout shell)
           └───────────────┘
```

### Build Order (Serial Steps)

| Step | Files | Can Parallelize? |
|---|---|---|
| 1 | F7 (`lib/tdee-calculator.ts`) | — |
| 2 | B1 (`public_calculator_schemas.py`) + F6 (`ToolsHeader.tsx`) + F5 (`ConversionCta.tsx`) | Yes, all three in parallel |
| 3 | B2 (`public_calculator_api.py`) — depends on B1 | — |
| 4 | B3 (register blueprint in `__init__.py`) — depends on B2 | — |
| 5 | F3 (`TdeeCalculatorForm.tsx`) + F4 (`TdeeReportCard.tsx`) — depend on F7 | Yes, both in parallel |
| 6 | F2b (`TdeeToolPage.tsx`) — depends on F3, F4, F5, F6, F7 | — |
| 7 | F1 (`tools/layout.tsx`) + F2a (`tools/tdee/page.tsx`) — depend on F2b | Yes, both in parallel |

---

## 8. Sonnet Execution Instructions (File-by-File Checklist)

### Pre-Flight

Before starting, read these files to establish context:
- `lifeos/domains/health/services/calculator_service.py` (the math to mirror)
- `frontend/app/(app)/health/_components/calculator/CalculatorForm.tsx` (visual reference)
- `frontend/app/(app)/health/_components/calculator/ReportCard.tsx` (visual reference)
- `DESIGN.md` (design tokens — memorize hex codes)
- This spec (you're reading it)

### Step 1: `frontend/lib/tdee-calculator.ts`

**Action:** Create new file.

**Content:** Port `calculator_service.py:calculate()` and `get_warnings()` to TypeScript.

**Critical implementation details:**
- Use standard JS `number` (not `Decimal`). The backend uses `Decimal` for DB precision; the frontend doesn't persist, so IEEE 754 float is sufficient.
- Round to 2 decimal places where the backend uses `_r2()`: `Math.round(val * 100) / 100`.
- Activity multipliers: `{ sedentary: 1.2, lightly_active: 1.375, moderately_active: 1.55, very_active: 1.725, extra_active: 1.9 }`.
- Protein factor: `2.0` g/kg. Fat factor: `0.8` g/kg. Carbs: `250` g/day. Fiber: `24` g/day.
- KCAL_PER_KG_LOSE: `7700`. KCAL_PER_KG_GAIN: `4500`. Monthly multiplier: `30`.
- BMR formula:
  - If `body_fat_pct` is not null and > 0: Katch-McArdle: `370 + 21.6 * (weight * (1 - body_fat_pct / 100))`
  - Else Mifflin-St Jeor: Male: `10 * weight + 6.25 * height - 5 * age + 5`. Female: `10 * weight + 6.25 * height - 5 * age - 161`.
- Export: `calculate(input: TdeeInput): TdeeResult`, `getWarnings(opts): TdeeWarning[]`, and all type interfaces.

**Verification:** The function `calculate({ weight_kg: 80, height_cm: 180, age_years: 25, gender: 'male', body_fat_pct: null, activity_level: 'moderately_active', goal_type: 'maintain', goal_weight_kg: null, goal_timeline_months: null })` must return `bmr ≈ 1830` and `tdee ≈ 2836.5`.

### Step 2a: `lifeos/domains/health/schemas/public_calculator_schemas.py`

**Action:** Create new file. Content as specified in §2.1.

### Step 2b: `frontend/app/tools/tdee/_components/ToolsHeader.tsx`

**Action:** Create new file.

**Content:** Client component. Sticky glassmorphic header bar.
- **Brand text:** `<a href="https://taeyangcv.vercel.app/" target="_blank" rel="noopener noreferrer">` containing:
  - "LifeOS" span: `fontFamily: 'var(--font-serif), Newsreader, serif'`, `fontStyle: italic`, `color: #4b6646`, `letterSpacing: -0.03em`, `fontSize: 1.125rem`.
  - " Tools" span: `fontFamily: 'var(--font-manrope), Manrope, sans-serif'`, `fontWeight: 700`, `color: #5a6157`, `fontSize: 0.875rem`.
- No other nav items.

### Step 2c: `frontend/app/tools/tdee/_components/ConversionCta.tsx`

**Action:** Create new file. Content as specified in §4.6.

### Step 3: `lifeos/domains/health/controllers/public_calculator_api.py`

**Action:** Create new file. Content as specified in §2.2.

**Verification:** The import `from lifeos.domains.health.services import calculator_service` must resolve. Check that `calculator_service.calculate` is the module-level function (line 47 of `calculator_service.py`), not a method.

Note: The existing code uses `from lifeos.domains.health import services` and calls `services.calculate(...)`. For the public controller, import the module directly: `from lifeos.domains.health.services import calculator_service` and call `calculator_service.calculate(...)`. Verify the import path works by checking `lifeos/domains/health/services/__init__.py` — if services are re-exported there, either import path works.

### Step 4: Blueprint Registration in `lifeos/__init__.py`

**Action:** Edit existing file (two changes).

**Change 1 — Import (near line 255):**
```python
from lifeos.domains.health.controllers.public_calculator_api import public_calculator_api_bp
```

**Change 2 — Registration (after line 292, which registers `calculator_api_bp`):**
```python
app.register_blueprint(public_calculator_api_bp, url_prefix="/api/v1/public/health/calculator")
```

### Step 5a: `frontend/app/tools/tdee/_components/TdeeCalculatorForm.tsx`

**Action:** Create new file.

**Content:** Client component with local `useState` for each field. On submit, calls `props.onCalculate(input)` with a `TdeeInput` object. Visual design cloned from `CalculatorForm.tsx` (same inline styles), but stripped of:
- `prefillData` / auto-fill logic
- `editingReport` / edit mode
- `isLoading` / `isCalculating` states (compute is instant client-side, no spinner needed)
- `InfoTooltip` components
- Translation (`t`) prop — use hardcoded English strings:
  - "Body Measurements", "Weight (kg)", "Height (cm)", "Age", "Body Fat %"
  - "Gender", "Male", "Female"
  - "Activity Level", "Sedentary", "Lightly Active", "Moderately Active", "Very Active", "Extra Active"
  - "Goal", "Lose", "Maintain", "Gain"
  - "Goal Weight (kg)", "Timeline (months)"
  - Button: "Calculate"

**Include the `SegmentedControl` inline** (same as existing, it's defined inside the component). Do not extract to a shared file.

### Step 5b: `frontend/app/tools/tdee/_components/TdeeReportCard.tsx`

**Action:** Create new file.

**Content:** Client component receiving `{ result: TdeeResult, warnings: TdeeWarning[] }`. Visual design cloned from `ReportCard.tsx` but:
- Uses `TdeeResult` fields directly (not `CalorieReport` DB entity)
- No `isLatest` badge, no date display, no `created_at`
- No `expanded`/`onToggleExpand` — always fully expanded
- Hardcoded English labels:
  - "Your Daily Targets", "kcal/day"
  - Goal pills: "Lose", "Maintain", "Gain"
  - BMR section: "BMR Breakdown", "Method", "Lean Body Mass", "BMR", "Activity", "TDEE", "Daily Adjustment"
  - Method pills: "Katch-McArdle", "Mifflin-St Jeor"
  - Macro section: "Macro Targets", "Daily", "Monthly (×30)", "Protein", "Fat", "Carbs", "Fiber", "kcal/day"
  - Delta section: "Delta Breakdown", "Δ Body Weight", "kcal/kg Assumption", "Total kcal Δ", "Daily kcal Adjustment"

**Import `TriangleAlert` and `ChevronDown` from `lucide-react`.**

### Step 6: `frontend/app/tools/tdee/_components/TdeeToolPage.tsx`

**Action:** Create new file.

**Content:** Client component orchestrating all pieces, as specified in §4.3. State:
- `result: TdeeResult | null` — starts null
- `warnings: TdeeWarning[]` — starts empty

Layout (inline styles, no Tailwind):
1. `<ToolsHeader />`
2. Content container: `maxWidth: 640px`, `margin: 0 auto`, `padding: 48px 20px 80px`
3. Micro-label: "HEALTH TOOLS" — Manrope 700, 0.6875rem, uppercase, +0.05em, `#8b4a3a`, `marginBottom: 12px`
4. Headline: "TDEE & BMR Calculator" — Newsreader Light (300), 2rem (mobile) / 2.5rem (desktop use `clamp(2rem, 5vw, 2.5rem)`), `color: #4b6646`, `letterSpacing: -0.03em`, `marginBottom: 8px`
5. Subtitle: "Calculate your daily energy expenditure and macronutrient targets using clinical-grade Mifflin-St Jeor and Katch-McArdle formulas." — Manrope 400, 0.9375rem, `color: #5a6157`, `lineHeight: 1.65`, `marginBottom: 32px`
6. `<TdeeCalculatorForm onCalculate={handleCalculate} />`
7. Conditional: `{result && <TdeeReportCard result={result} warnings={warnings} />}` with `marginTop: 32px`
8. `<ConversionCta hasResult={!!result} result={result} />` with `marginTop: 40px`
9. Footer (inline, as specified in §4.7)

### Step 7a: `frontend/app/tools/layout.tsx`

**Action:** Create new file.

**Content:** Server component. Minimal wrapper as specified in §4.1. Just the outer `div` with `minHeight: 100vh`, `flexDirection: column`, `background: #f8faf2`, and renders `{children}` in a `<main>` with `flex: 1`.

### Step 7b: `frontend/app/tools/tdee/page.tsx`

**Action:** Create new file.

**Content:** Server component exporting `metadata` (§5.1) and JSON-LD structured data (§5.2). Renders `<TdeeToolPage />`.

```tsx
import type { Metadata } from 'next'
import TdeeToolPage from './_components/TdeeToolPage'

export const metadata: Metadata = {
  title: 'TDEE & BMR Calculator | LifeOS',
  description: 'Accurate daily energy expenditure and macro calculation using clinical formulas. Simple, private, and calm.',
  openGraph: {
    title: 'TDEE & BMR Calculator | LifeOS',
    description: 'Accurate daily energy expenditure and macro calculation using clinical formulas.',
    type: 'website',
    siteName: 'LifeOS',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'TDEE & BMR Calculator | LifeOS',
    description: 'Accurate daily energy expenditure and macro calculation using clinical formulas.',
  },
  robots: { index: true, follow: true },
}

const jsonLd = {
  '@context': 'https://schema.org',
  '@type': 'SoftwareApplication',
  name: 'TDEE & BMR Calculator',
  applicationCategory: 'HealthApplication',
  operatingSystem: 'Web',
  offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
  description: 'Accurate daily energy expenditure and macro calculation using Mifflin-St Jeor and Katch-McArdle clinical formulas.',
  creator: { '@type': 'Organization', name: 'LifeOS' },
}

export default function Page() {
  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />
      <TdeeToolPage />
    </>
  )
}
```

### Post-Build Verification Checklist

After all files are created:

- [ ] `cd frontend && npx next build` — no TypeScript errors, no build failures
- [ ] Visit `http://localhost:3000/tools/tdee` — page renders without auth redirect
- [ ] Fill form and click Calculate — results appear instantly (no network request)
- [ ] `curl -X POST http://localhost:5001/api/v1/public/health/calculate -H 'Content-Type: application/json' -d '{"weight_kg":80,"height_cm":180,"age_years":25,"gender":"male","activity_level":"moderately_active","goal_type":"maintain"}'` — returns 200 with computed result
- [ ] Hit the endpoint 31 times in one minute — 31st request returns 429 (rate limited)
- [ ] "Join LifeOS" CTA links to `https://taeyangcv.vercel.app/` with query params
- [ ] No `Authorization` header sent from the public page (check Network tab)
- [ ] Page source contains `<script type="application/ld+json">` structured data
- [ ] Page `<title>` is "TDEE & BMR Calculator | LifeOS"
- [ ] All cards have `border-radius: 0px 16px 16px 16px` (inspect element)
- [ ] All buttons are `border-radius: 100px` (pill)
- [ ] No imports from `@/lib/auth/` or `@/lib/api/client` in any `/tools/` file

---

*End of spec. This document is the single source of truth for the public TDEE tool build. If this spec conflicts with DESIGN.md or the UI/UX Constitution, this spec wins for the public surface only — but flag the deviation in the PR description.*
