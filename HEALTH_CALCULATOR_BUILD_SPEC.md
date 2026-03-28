# HEALTH_CALCULATOR_BUILD_SPEC.md

**Version:** 1.0
**Date:** 2026-03-28
**Author:** Opus (architectural specification)
**Executor:** Sonnet 4.6 (file-by-file implementation)
**Status:** Approved feature set only — no scope expansion permitted
**Depends on:** HEALTH_OPTIMIZER_BUILD_SPEC.md (optimizer must be built first)

---

## 0. Build Philosophy & Constraints

### What This Feature IS

A **calorie calculator with persistent reports** embedded as a sub-tab within the LifeOS health page. It produces immutable report records that the user can revisit anytime. The latest report's values automatically feed into the optimizer's constraint builder, bridging planning (calculator) with execution (optimizer).

It consists of three surfaces:
1. **Calculator Form** — input fields for user biometrics and goals, producing a computed report
2. **Report Card** — a detailed breakdown of BMR, TDEE, daily/monthly targets, and macro suggestions
3. **Report History** — a chronological list of past reports with summary view and expand-to-detail

Plus two modifications to the existing optimizer:
4. **Constraint Auto-Population** — latest report values pre-fill optimizer constraints
5. **Time Horizon Selector** — converts daily targets to multi-day constraint values

### What This Feature Is NOT

- Not a food tracker or nutrition log (standalone calculator, no writes to `health_nutrition_log`)
- Not a dietary recommendation engine (fixed formulas, user controls all inputs)
- Not a BMI calculator or body type classifier (explicitly cut — see Boundaries)
- Not a meal planner (produces targets, not meals)
- Not connected to the optimizer's solver (produces constraints, doesn't invoke the LP)

### Emotional Contract

Same as health domain (UI/UX Constitution §1, §9):
- **Allowed:** "Based on these inputs, your estimated daily target is...", "This timeline may result in a very low daily intake."
- **Forbidden:** "You should lose weight", "Your intake is too high", "You must reduce calories"

### Breadth-First Rule

Every section ~20% depth before any section reaches 80%. Sonnet must build all backend files to functional state before starting any frontend work. All frontend files must reach skeleton state before polishing any single component.

### Later-Wave Domain Rules (Constitution §12.1)

Health is a later-wave domain. The calculator reports numbers derived from deterministic formulas; it does not interpret health data or make recommendations. All UI copy must avoid clinical or prescriptive framing.

---

## 1. Formula Reference

All formulas reproduced verbatim. Sonnet must implement these exactly — no alternative formulas, no rounding variations, no additional calculations.

### 1.1 BMR Calculation

**Method selection rule:**
```
IF body_fat_pct is provided AND body_fat_pct > 0:
    USE Katch-McArdle
ELSE:
    USE Mifflin-St Jeor
```

**Katch-McArdle Equation:**
```
LBM = weight_kg × (1 - body_fat_pct / 100)
BMR = 370 + (21.6 × LBM)
```

**Mifflin-St Jeor Equation:**
```
Male:   BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age_years) + 5
Female: BMR = (10 × weight_kg) + (6.25 × height_cm) - (5 × age_years) - 161
```

### 1.2 TDEE Calculation

```
TDEE = BMR × activity_multiplier
```

**Activity multipliers (exact values, no interpolation):**

| Level | Multiplier |
|-------|-----------|
| `sedentary` | 1.2 |
| `lightly_active` | 1.375 |
| `moderately_active` | 1.55 |
| `very_active` | 1.725 |
| `extra_active` | 1.9 |

### 1.3 Daily Calorie Target

**Losing weight (goal_type = 'lose'):**
```
delta_bw = goal_weight_kg - weight_kg                    (negative value)
total_delta_kcal = delta_bw × 7700                       (7700 kcal ≈ 1 kg fat)
delta_kcal_per_day = total_delta_kcal / (30 × goal_timeline_months)
daily_calories = TDEE + delta_kcal_per_day               (delta is negative → reduces TDEE)
```

**Gaining weight (goal_type = 'gain'):**
```
delta_bw = goal_weight_kg - weight_kg                    (positive value)
total_delta_kcal = delta_bw × 4500                       (4500 kcal ≈ 1 kg muscle)
delta_kcal_per_day = total_delta_kcal / (30 × goal_timeline_months)
daily_calories = TDEE + delta_kcal_per_day               (delta is positive → increases TDEE)
```

**Maintaining weight (goal_type = 'maintain'):**
```
daily_calories = TDEE
```

### 1.4 Macro Suggestions

All derived from current weight. Fixed formulas, no customization:

```
protein_g_per_day  = 2.0 × weight_kg
fat_g_per_day      = 0.8 × weight_kg
carbs_g_per_day    = 250                                  (fixed constant)
fiber_g_per_day    = 24                                   (fixed constant)
```

### 1.5 Monthly Conversion

```
monthly_value = daily_value × 30
```

Applied to: calories, protein, fat, carbs, fiber. This produces the default constraint values for the optimizer.

### 1.6 kcal-per-kg Assumptions

| Goal Type | kcal per kg | Rationale |
|-----------|------------|-----------|
| `lose` | 7700 | ~1 kg body fat |
| `gain` | 4500 | ~1 kg lean mass |
| `maintain` | N/A | No delta |

---

## 2. Storage Decisions

### 2.1 Height, Age, Gender — `UserPreference` with key `health_profile`

**Decision:** Store in the existing `UserPreference` model as a JSON value under key `health_profile`.

**Justification:**
- The `UserPreference` model already exists with a `key: str` + `value: JSON` pattern (used for onboarding domains, calendar sources, etc.)
- Height, age, and gender are semi-permanent user attributes — they change rarely but are not truly immutable
- Creating a new `health_user_profile` table would require a migration, model, service, and controller for just 3 fields
- Using `UserPreference` requires zero backend schema changes — only a new service function to get/set the health profile
- The JSON value shape: `{ "height_cm": 175.0, "age_years": 28, "gender": "male" }`
- These values persist across calculator sessions — the form pre-fills them on return visits

**Access pattern:**
```python
# Read
pref = UserPreference.query.filter_by(user_id=user_id, key="health_profile").first()
profile = pref.value if pref else {}

# Write (upsert)
pref = UserPreference.query.filter_by(user_id=user_id, key="health_profile").first()
if pref:
    pref.value = {**pref.value, **new_fields}
else:
    pref = UserPreference(user_id=user_id, key="health_profile", value=new_fields)
    db.session.add(pref)
db.session.commit()
```

### 2.2 Calorie Reports — New `health_calorie_report` Table

**Decision:** Dedicated table with structured columns.

**Justification:**
- Reports have a fixed, well-defined schema with 20+ numeric fields
- Full history is required — users must browse and compare past reports
- Immutable records — create-only, no update or delete
- Querying by user_id + ordering by created_at is the primary access pattern
- A JSON blob in UserPreference would make list/sort/query operations awkward and unperformant
- Structured columns enable future read model projections and inquiry integration

---

## 3. Backend Spec

### 3.1 Migration

**File:** `lifeos/migrations/versions/20260328_health_calorie_report.py`

**Action:** Create new table `health_calorie_report`.

```python
"""Add calorie report table for health calculator.

Revision ID: 20260328_health_calorie_report
Revises: <CURRENT_HEAD>
Create Date: 2026-03-28
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op

revision = "20260328_health_calorie_report"
down_revision = "<CURRENT_HEAD>"  # Sonnet: run `cd lifeos && python -m alembic heads` to find this
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "health_calorie_report",
        # Identity
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("user.id"), nullable=False, index=True),

        # Input snapshot
        sa.Column("weight_kg", sa.Numeric(10, 2), nullable=False),
        sa.Column("height_cm", sa.Numeric(10, 2), nullable=False),
        sa.Column("age_years", sa.Integer, nullable=False),
        sa.Column("gender", sa.String(16), nullable=False),          # 'male' | 'female'
        sa.Column("body_fat_pct", sa.Numeric(5, 2), nullable=True),  # null if not provided
        sa.Column("activity_level", sa.String(32), nullable=False),   # sedentary..extra_active
        sa.Column("goal_type", sa.String(16), nullable=False),       # 'lose' | 'gain' | 'maintain'
        sa.Column("goal_weight_kg", sa.Numeric(10, 2), nullable=True),  # null if maintain
        sa.Column("goal_timeline_months", sa.Integer, nullable=True),    # null if maintain

        # Computed values
        sa.Column("method_used", sa.String(32), nullable=False),     # 'katch_mcardle' | 'mifflin_st_jeor'
        sa.Column("lean_body_mass", sa.Numeric(10, 2), nullable=True),  # null if mifflin
        sa.Column("bmr", sa.Numeric(10, 2), nullable=False),
        sa.Column("activity_multiplier", sa.Numeric(4, 3), nullable=False),
        sa.Column("tdee", sa.Numeric(10, 2), nullable=False),

        # Delta breakdown
        sa.Column("delta_bw", sa.Numeric(10, 2), nullable=True),           # null if maintain
        sa.Column("total_delta_kcal", sa.Numeric(12, 2), nullable=True),   # null if maintain
        sa.Column("delta_kcal_per_day", sa.Numeric(10, 2), nullable=True), # null if maintain
        sa.Column("kcal_per_kg_used", sa.Integer, nullable=True),          # 7700 or 4500 or null

        # Daily targets
        sa.Column("daily_calories", sa.Numeric(10, 2), nullable=False),
        sa.Column("protein_g_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("fat_g_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("carbs_g_per_day", sa.Numeric(10, 2), nullable=False),
        sa.Column("fiber_g_per_day", sa.Numeric(10, 2), nullable=False),

        # Monthly targets (daily × 30)
        sa.Column("monthly_calories", sa.Numeric(12, 2), nullable=False),
        sa.Column("monthly_protein_g", sa.Numeric(10, 2), nullable=False),
        sa.Column("monthly_fat_g", sa.Numeric(10, 2), nullable=False),
        sa.Column("monthly_carbs_g", sa.Numeric(10, 2), nullable=False),
        sa.Column("monthly_fiber_g", sa.Numeric(10, 2), nullable=False),

        # Timestamp
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
    )
    op.create_index(
        "ix_health_calorie_report_user_created",
        "health_calorie_report",
        ["user_id", "created_at"],
    )


def downgrade():
    op.drop_index("ix_health_calorie_report_user_created")
    op.drop_table("health_calorie_report")
```

**Indexes:**
- `user_id` — individual index (created by `index=True` on the column)
- `(user_id, created_at)` — composite index for "list my reports newest first" query

**Sonnet instructions:** Before writing this file, run `cd lifeos && python -m alembic heads` to get the current head revision. Replace `<CURRENT_HEAD>` with the actual value. If the optimizer migration `20260328_health_food_library` is the current head, use that as `down_revision`.

### 3.2 Model

**File:** `lifeos/domains/health/models/calorie_report.py` (NEW)

```python
"""Calorie report model for health calculator."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Numeric
from sqlalchemy.orm import Mapped, mapped_column

from lifeos.extensions import db


class CalorieReport(db.Model):
    __tablename__ = "health_calorie_report"
    __table_args__ = (
        db.Index("ix_health_calorie_report_user_created", "user_id", "created_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(db.ForeignKey("user.id"), index=True, nullable=False)

    # Input snapshot
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    height_cm: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    age_years: Mapped[int] = mapped_column(nullable=False)
    gender: Mapped[str] = mapped_column(db.String(16), nullable=False)
    body_fat_pct: Mapped[Decimal | None] = mapped_column(Numeric(5, 2), nullable=True)
    activity_level: Mapped[str] = mapped_column(db.String(32), nullable=False)
    goal_type: Mapped[str] = mapped_column(db.String(16), nullable=False)
    goal_weight_kg: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    goal_timeline_months: Mapped[int | None] = mapped_column(nullable=True)

    # Computed values
    method_used: Mapped[str] = mapped_column(db.String(32), nullable=False)
    lean_body_mass: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    bmr: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    activity_multiplier: Mapped[Decimal] = mapped_column(Numeric(4, 3), nullable=False)
    tdee: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Delta breakdown
    delta_bw: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    total_delta_kcal: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    delta_kcal_per_day: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    kcal_per_kg_used: Mapped[int | None] = mapped_column(nullable=True)

    # Daily targets
    daily_calories: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    protein_g_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fat_g_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    carbs_g_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    fiber_g_per_day: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Monthly targets
    monthly_calories: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    monthly_protein_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    monthly_fat_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    monthly_carbs_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    monthly_fiber_g: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
```

**Update `lifeos/domains/health/models/__init__.py`:** Add import:

```python
from .calorie_report import CalorieReport
```

Add `CalorieReport` to `__all__`.

### 3.3 Schemas

**File:** `lifeos/domains/health/schemas/calculator_schemas.py` (NEW)

```python
"""Calorie calculator Pydantic DTOs."""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class CalculatorInput(BaseModel):
    """Request body for POST /api/v1/health/calculator/calculate."""

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

    # Whether to persist the height/age/gender to UserPreference for future visits
    save_profile: bool = Field(default=True)

    @model_validator(mode="after")
    def validate_goal_fields(self):
        if self.goal_type in ("lose", "gain"):
            if self.goal_weight_kg is None:
                raise ValueError("goal_weight_kg is required when goal_type is 'lose' or 'gain'")
            if self.goal_timeline_months is None:
                raise ValueError("goal_timeline_months is required when goal_type is 'lose' or 'gain'")
        return self


class ReportListParams(BaseModel):
    """Query params for GET /api/v1/health/calculator/reports."""

    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)
```

### 3.4 Service (Calculation Logic + Persistence)

**File:** `lifeos/domains/health/services/calculator_service.py` (NEW)

```python
"""Calorie calculator service — calculation logic and report persistence."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional

from lifeos.core.users.models import UserPreference
from lifeos.domains.health.events import HEALTH_CALORIE_REPORT_CREATED
from lifeos.domains.health.models import Biometric
from lifeos.domains.health.models.calorie_report import CalorieReport
from lifeos.extensions import db
from lifeos.lifeos_platform.outbox import enqueue as enqueue_outbox


# ── Activity multipliers ──────────────────────────────────────────

ACTIVITY_MULTIPLIERS: dict[str, Decimal] = {
    "sedentary": Decimal("1.2"),
    "lightly_active": Decimal("1.375"),
    "moderately_active": Decimal("1.55"),
    "very_active": Decimal("1.725"),
    "extra_active": Decimal("1.9"),
}

KCAL_PER_KG_LOSE = 7700
KCAL_PER_KG_GAIN = 4500
MONTHLY_MULTIPLIER = 30

# ── Fixed macro constants ─────────────────────────────────────────

PROTEIN_FACTOR = Decimal("2.0")    # g per kg bodyweight
FAT_FACTOR = Decimal("0.8")       # g per kg bodyweight
CARBS_FIXED = Decimal("250")      # g per day (constant)
FIBER_FIXED = Decimal("24")       # g per day (constant)


# ── Helper: round to 2 decimal places ─────────────────────────────

def _r2(val: Decimal) -> Decimal:
    return val.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


# ── Core calculation ───────────────────────────────────────────────

def calculate(
    *,
    weight_kg: float,
    height_cm: float,
    age_years: int,
    gender: str,
    body_fat_pct: float | None,
    activity_level: str,
    goal_type: str,
    goal_weight_kg: float | None,
    goal_timeline_months: int | None,
) -> dict:
    """
    Run the calorie calculator. Returns a dict of all computed fields.
    Pure function — no DB access, no side effects.
    """
    w = Decimal(str(weight_kg))
    h = Decimal(str(height_cm))
    age = age_years

    # ── BMR ──
    if body_fat_pct is not None and body_fat_pct > 0:
        bf = Decimal(str(body_fat_pct))
        lbm = _r2(w * (1 - bf / 100))
        bmr = _r2(Decimal("370") + Decimal("21.6") * lbm)
        method_used = "katch_mcardle"
    else:
        lbm = None
        if gender == "male":
            bmr = _r2(Decimal("10") * w + Decimal("6.25") * h - Decimal("5") * age + 5)
        else:
            bmr = _r2(Decimal("10") * w + Decimal("6.25") * h - Decimal("5") * age - 161)
        method_used = "mifflin_st_jeor"

    # ── TDEE ──
    multiplier = ACTIVITY_MULTIPLIERS[activity_level]
    tdee = _r2(bmr * multiplier)

    # ── Daily calorie target ──
    delta_bw = None
    total_delta_kcal = None
    delta_kcal_per_day = None
    kcal_per_kg_used = None

    if goal_type == "lose":
        gw = Decimal(str(goal_weight_kg))
        delta_bw = _r2(gw - w)  # negative
        total_delta_kcal = _r2(delta_bw * KCAL_PER_KG_LOSE)
        delta_kcal_per_day = _r2(total_delta_kcal / (MONTHLY_MULTIPLIER * goal_timeline_months))
        daily_calories = _r2(tdee + delta_kcal_per_day)
        kcal_per_kg_used = KCAL_PER_KG_LOSE
    elif goal_type == "gain":
        gw = Decimal(str(goal_weight_kg))
        delta_bw = _r2(gw - w)  # positive
        total_delta_kcal = _r2(delta_bw * KCAL_PER_KG_GAIN)
        delta_kcal_per_day = _r2(total_delta_kcal / (MONTHLY_MULTIPLIER * goal_timeline_months))
        daily_calories = _r2(tdee + delta_kcal_per_day)
        kcal_per_kg_used = KCAL_PER_KG_GAIN
    else:  # maintain
        daily_calories = tdee

    # ── Macro suggestions ──
    protein_g = _r2(PROTEIN_FACTOR * w)
    fat_g = _r2(FAT_FACTOR * w)
    carbs_g = CARBS_FIXED
    fiber_g = FIBER_FIXED

    # ── Monthly targets ──
    monthly_calories = _r2(daily_calories * MONTHLY_MULTIPLIER)
    monthly_protein = _r2(protein_g * MONTHLY_MULTIPLIER)
    monthly_fat = _r2(fat_g * MONTHLY_MULTIPLIER)
    monthly_carbs = _r2(carbs_g * MONTHLY_MULTIPLIER)
    monthly_fiber = _r2(fiber_g * MONTHLY_MULTIPLIER)

    return {
        "method_used": method_used,
        "lean_body_mass": float(lbm) if lbm is not None else None,
        "bmr": float(bmr),
        "activity_multiplier": float(multiplier),
        "tdee": float(tdee),
        "delta_bw": float(delta_bw) if delta_bw is not None else None,
        "total_delta_kcal": float(total_delta_kcal) if total_delta_kcal is not None else None,
        "delta_kcal_per_day": float(delta_kcal_per_day) if delta_kcal_per_day is not None else None,
        "kcal_per_kg_used": kcal_per_kg_used,
        "daily_calories": float(daily_calories),
        "protein_g_per_day": float(protein_g),
        "fat_g_per_day": float(fat_g),
        "carbs_g_per_day": float(carbs_g),
        "fiber_g_per_day": float(fiber_g),
        "monthly_calories": float(monthly_calories),
        "monthly_protein_g": float(monthly_protein),
        "monthly_fat_g": float(monthly_fat),
        "monthly_carbs_g": float(monthly_carbs),
        "monthly_fiber_g": float(monthly_fiber),
    }


# ── Validation warnings ──────────────────────────────────────────

def get_warnings(
    *,
    gender: str,
    daily_calories: float,
    tdee: float,
    goal_type: str,
) -> list[dict]:
    """
    Return a list of warning objects (observation tone, never prescriptive).
    Each: { "type": str, "message": str }
    """
    warnings = []
    floor = 1200 if gender == "female" else 1500

    if goal_type == "lose" and daily_calories < floor:
        warnings.append({
            "type": "low_intake",
            "message": (
                "This timeline may result in a very low daily intake. "
                "Consider extending the timeline or adjusting your goal weight."
            ),
        })

    if goal_type == "gain" and daily_calories > tdee + 1000:
        warnings.append({
            "type": "high_surplus",
            "message": (
                "This is a significant surplus. "
                "A more gradual approach may be easier to sustain."
            ),
        })

    return warnings


# ── Persist report ────────────────────────────────────────────────

def create_report(
    user_id: int,
    *,
    # Input snapshot
    weight_kg: float,
    height_cm: float,
    age_years: int,
    gender: str,
    body_fat_pct: float | None,
    activity_level: str,
    goal_type: str,
    goal_weight_kg: float | None,
    goal_timeline_months: int | None,
    # Computed values (from calculate())
    computed: dict,
) -> CalorieReport:
    """Persist a calorie report. Returns the saved record."""
    report = CalorieReport(
        user_id=user_id,
        # Input snapshot
        weight_kg=weight_kg,
        height_cm=height_cm,
        age_years=age_years,
        gender=gender,
        body_fat_pct=body_fat_pct,
        activity_level=activity_level,
        goal_type=goal_type,
        goal_weight_kg=goal_weight_kg,
        goal_timeline_months=goal_timeline_months,
        # Computed values
        **{k: v for k, v in computed.items()},
    )
    db.session.add(report)
    db.session.flush()

    enqueue_outbox(
        HEALTH_CALORIE_REPORT_CREATED,
        {
            "report_id": report.id,
            "user_id": user_id,
            "bmr": computed["bmr"],
            "tdee": computed["tdee"],
            "daily_calories": computed["daily_calories"],
            "goal_type": goal_type,
            "goal_weight_kg": goal_weight_kg,
            "timeline_months": goal_timeline_months,
            "method_used": computed["method_used"],
            "created_at": report.created_at.isoformat() if report.created_at else datetime.utcnow().isoformat(),
        },
        user_id=user_id,
    )
    db.session.commit()
    return report


# ── Query reports ─────────────────────────────────────────────────

def list_reports(
    user_id: int,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[CalorieReport], int]:
    """List all calorie reports for a user, newest first."""
    query = (
        CalorieReport.query
        .filter_by(user_id=user_id)
        .order_by(CalorieReport.created_at.desc())
    )
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_report(user_id: int, report_id: int) -> CalorieReport | None:
    """Get a single report by ID, scoped to user."""
    return CalorieReport.query.filter_by(id=report_id, user_id=user_id).first()


def get_latest_report(user_id: int) -> CalorieReport | None:
    """Get the most recent report for a user. Used by optimizer constraint bridge."""
    return (
        CalorieReport.query
        .filter_by(user_id=user_id)
        .order_by(CalorieReport.created_at.desc())
        .first()
    )


# ── Health profile (UserPreference) ──────────────────────────────

def get_health_profile(user_id: int) -> dict:
    """
    Get the user's saved health profile (height, age, gender) from UserPreference.
    Returns {} if not set.
    """
    pref = UserPreference.query.filter_by(user_id=user_id, key="health_profile").first()
    return pref.value if pref else {}


def save_health_profile(user_id: int, *, height_cm: float, age_years: int, gender: str) -> None:
    """Upsert the user's health profile in UserPreference."""
    pref = UserPreference.query.filter_by(user_id=user_id, key="health_profile").first()
    profile_data = {"height_cm": height_cm, "age_years": age_years, "gender": gender}
    if pref:
        pref.value = {**pref.value, **profile_data}
    else:
        pref = UserPreference(user_id=user_id, key="health_profile", value=profile_data)
        db.session.add(pref)
    db.session.commit()


# ── Auto-fill latest biometric ────────────────────────────────────

def get_latest_biometric(user_id: int) -> dict | None:
    """
    Get the latest biometric entry for weight and body_fat_pct auto-fill.
    Returns { weight_kg, body_fat_pct } or None.
    """
    bio = (
        Biometric.query
        .filter_by(user_id=user_id)
        .order_by(Biometric.date.desc(), Biometric.created_at.desc())
        .first()
    )
    if not bio:
        return None
    return {
        "weight_kg": float(bio.weight) if bio.weight else None,
        "body_fat_pct": float(bio.body_fat_pct) if bio.body_fat_pct else None,
    }
```

**Update `lifeos/domains/health/services/__init__.py`:** Add imports from `calculator_service`:

```python
from lifeos.domains.health.services.calculator_service import (
    calculate,
    create_report,
    get_health_profile,
    get_latest_biometric,
    get_latest_report,
    get_report,
    get_warnings,
    list_reports,
    save_health_profile,
)
```

Add all nine to `__all__`.

### 3.5 Controller (API Contract)

**File:** `lifeos/domains/health/controllers/calculator_api.py` (NEW)

Blueprint name: `calculator_api_bp`

All routes relative to blueprint prefix. Blueprint registered at `/api/v1/health/calculator`.

```python
"""Calorie calculator API controller."""

from __future__ import annotations

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from pydantic import ValidationError

from lifeos.core.utils.decorators import csrf_protected
from lifeos.domains.health import services
from lifeos.domains.health.mappers import map_calorie_report
from lifeos.domains.health.schemas.calculator_schemas import CalculatorInput, ReportListParams

calculator_api_bp = Blueprint("calculator_api", __name__)


@calculator_api_bp.post("/calculate")
@jwt_required()
@csrf_protected
def calculate_and_save():
    """
    Run the calorie calculator, persist the report, and return the result.
    Also saves height/age/gender to UserPreference if save_profile is true.
    """
    payload = request.get_json(silent=True) or {}
    try:
        data = CalculatorInput.model_validate(payload)
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400

    user_id = int(get_jwt_identity())

    # Run calculation
    computed = services.calculate(
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

    # Check for warnings
    warnings = services.get_warnings(
        gender=data.gender,
        daily_calories=computed["daily_calories"],
        tdee=computed["tdee"],
        goal_type=data.goal_type,
    )

    # Persist report
    report = services.create_report(
        user_id,
        weight_kg=data.weight_kg,
        height_cm=data.height_cm,
        age_years=data.age_years,
        gender=data.gender,
        body_fat_pct=data.body_fat_pct,
        activity_level=data.activity_level,
        goal_type=data.goal_type,
        goal_weight_kg=data.goal_weight_kg,
        goal_timeline_months=data.goal_timeline_months,
        computed=computed,
    )

    # Save profile if requested
    if data.save_profile:
        services.save_health_profile(
            user_id,
            height_cm=data.height_cm,
            age_years=data.age_years,
            gender=data.gender,
        )

    return jsonify({
        "ok": True,
        "report": map_calorie_report(report),
        "warnings": warnings,
    }), 201


@calculator_api_bp.get("/reports")
@jwt_required()
def list_reports():
    """List all calorie reports for the authenticated user."""
    user_id = int(get_jwt_identity())
    try:
        params = ReportListParams.model_validate(dict(request.args))
    except ValidationError as exc:
        return jsonify({"ok": False, "error": "validation_error", "details": exc.errors()}), 400
    items, total = services.list_reports(user_id, page=params.page, per_page=params.per_page)
    pages = (total + params.per_page - 1) // params.per_page if params.per_page else 1
    return jsonify({
        "ok": True,
        "reports": [map_calorie_report(r) for r in items],
        "page": params.page,
        "pages": pages,
        "total": total,
    })


@calculator_api_bp.get("/reports/latest")
@jwt_required()
def latest_report():
    """Get the latest calorie report. Used by optimizer for constraint auto-population."""
    user_id = int(get_jwt_identity())
    report = services.get_latest_report(user_id)
    if not report:
        return jsonify({"ok": True, "report": None})
    return jsonify({"ok": True, "report": map_calorie_report(report)})


@calculator_api_bp.get("/reports/<int:report_id>")
@jwt_required()
def get_report(report_id: int):
    """Get a single report by ID."""
    user_id = int(get_jwt_identity())
    report = services.get_report(user_id, report_id)
    if not report:
        return jsonify({"ok": False, "error": "not_found"}), 404
    return jsonify({"ok": True, "report": map_calorie_report(report)})


@calculator_api_bp.get("/prefill")
@jwt_required()
def get_prefill():
    """
    Get auto-fill data for the calculator form:
    - Latest biometric (weight, body_fat_pct)
    - Saved health profile (height, age, gender)
    """
    user_id = int(get_jwt_identity())
    biometric = services.get_latest_biometric(user_id)
    profile = services.get_health_profile(user_id)
    return jsonify({
        "ok": True,
        "biometric": biometric,
        "profile": profile,
    })
```

#### Mapper Addition

**Add to `lifeos/domains/health/mappers.py`:**

```python
def map_calorie_report(r: CalorieReport) -> dict:
    return {
        "id": r.id,
        # Input snapshot
        "weight_kg": float(r.weight_kg),
        "height_cm": float(r.height_cm),
        "age_years": r.age_years,
        "gender": r.gender,
        "body_fat_pct": float(r.body_fat_pct) if r.body_fat_pct is not None else None,
        "activity_level": r.activity_level,
        "goal_type": r.goal_type,
        "goal_weight_kg": float(r.goal_weight_kg) if r.goal_weight_kg is not None else None,
        "goal_timeline_months": r.goal_timeline_months,
        # Computed values
        "method_used": r.method_used,
        "lean_body_mass": float(r.lean_body_mass) if r.lean_body_mass is not None else None,
        "bmr": float(r.bmr),
        "activity_multiplier": float(r.activity_multiplier),
        "tdee": float(r.tdee),
        # Delta breakdown
        "delta_bw": float(r.delta_bw) if r.delta_bw is not None else None,
        "total_delta_kcal": float(r.total_delta_kcal) if r.total_delta_kcal is not None else None,
        "delta_kcal_per_day": float(r.delta_kcal_per_day) if r.delta_kcal_per_day is not None else None,
        "kcal_per_kg_used": r.kcal_per_kg_used,
        # Daily targets
        "daily_calories": float(r.daily_calories),
        "protein_g_per_day": float(r.protein_g_per_day),
        "fat_g_per_day": float(r.fat_g_per_day),
        "carbs_g_per_day": float(r.carbs_g_per_day),
        "fiber_g_per_day": float(r.fiber_g_per_day),
        # Monthly targets
        "monthly_calories": float(r.monthly_calories),
        "monthly_protein_g": float(r.monthly_protein_g),
        "monthly_fat_g": float(r.monthly_fat_g),
        "monthly_carbs_g": float(r.monthly_carbs_g),
        "monthly_fiber_g": float(r.monthly_fiber_g),
        # Metadata
        "created_at": r.created_at.isoformat() if r.created_at else None,
    }
```

Import `CalorieReport` at the top of `mappers.py`.

#### Blueprint Registration

**File:** `lifeos/__init__.py` — **ADD** in `_register_blueprints()`:

```python
from lifeos.domains.health.controllers.calculator_api import calculator_api_bp

app.register_blueprint(calculator_api_bp, url_prefix="/api/v1/health/calculator")
```

Place this line immediately after the existing `food_library_api_bp` registration.

### 3.6 Events

**File:** `lifeos/domains/health/events.py` — **ADD** one new event constant:

```python
# --- Calculator Events ---
HEALTH_CALORIE_REPORT_CREATED = "health.calorie_report.created"
```

Add to `EVENT_CATALOG`:

```python
HEALTH_CALORIE_REPORT_CREATED: {
    "version": "v1",
    "payload": {
        "report_id": "int",
        "user_id": "int",
        "bmr": "decimal",
        "tdee": "decimal",
        "daily_calories": "decimal",
        "goal_type": "str",
        "goal_weight_kg": "decimal?",
        "timeline_months": "int?",
        "method_used": "str",
        "created_at": "datetime",
    },
},
```

Add `HEALTH_CALORIE_REPORT_CREATED` to `__all__`.

**File:** `lifeos/core/events/semantic_contracts.py` — **ADD** one entry:

```python
"health.calorie_report.created": EventSemanticContract(
    event_type="health.calorie_report.created",
    meaning="A calorie calculator report was generated and persisted for the user.",
    asserted_by="user",
    certainty="confirmed",
),
```

### 3.7 Validation Rules

All validation is enforced in the Pydantic schema (`CalculatorInput`) and the warning system (`get_warnings`):

| Rule | Implementation | User-facing message |
|------|---------------|---------------------|
| `weight_kg > 0` | Pydantic `Field(gt=0)` | Standard validation error |
| `height_cm > 0` | Pydantic `Field(gt=0)` | "Height is needed for the calculation." |
| `age_years >= 1` | Pydantic `Field(ge=1)` | Standard validation error |
| `goal_timeline_months >= 1` | Pydantic `Field(ge=1)` | "Timeline must be at least 1 month." |
| `goal_weight_kg` required if lose/gain | `model_validator` | "Goal weight is required for this goal type." |
| `goal_timeline_months` required if lose/gain | `model_validator` | "Timeline is required for this goal type." |
| Low intake warning | `get_warnings()` | "This timeline may result in a very low daily intake. Consider extending the timeline or adjusting your goal weight." |
| High surplus warning | `get_warnings()` | "This is a significant surplus. A more gradual approach may be easier to sustain." |

**Calorie floor thresholds:**
- Female: daily_calories < 1200
- Male: daily_calories < 1500

**Surplus threshold:**
- daily_calories > TDEE + 1000

These are warnings (observation tone), not hard blocks. The calculator still produces and saves the report.

### 3.8 API Contract Summary

All endpoints under `/api/v1/health/calculator`. Auth: JWT required. CSRF: required on POST.

| Method | Path | Purpose | Request | Response |
|--------|------|---------|---------|----------|
| `POST` | `/api/v1/health/calculator/calculate` | Compute + persist report | Body: `CalculatorInput` | `{ ok, report, warnings[] }` (201) |
| `GET` | `/api/v1/health/calculator/reports` | List user's reports | `?page=1&per_page=20` | `{ ok, reports[], page, pages, total }` |
| `GET` | `/api/v1/health/calculator/reports/latest` | Latest report (for optimizer) | — | `{ ok, report }` (report may be null) |
| `GET` | `/api/v1/health/calculator/reports/:id` | Single report detail | — | `{ ok, report }` or 404 |
| `GET` | `/api/v1/health/calculator/prefill` | Auto-fill data | — | `{ ok, biometric, profile }` |

**Response shape for a calorie report:**

```json
{
  "id": 1,
  "weight_kg": 80.0,
  "height_cm": 175.0,
  "age_years": 28,
  "gender": "male",
  "body_fat_pct": 18.0,
  "activity_level": "moderately_active",
  "goal_type": "lose",
  "goal_weight_kg": 75.0,
  "goal_timeline_months": 3,
  "method_used": "katch_mcardle",
  "lean_body_mass": 65.60,
  "bmr": 1786.96,
  "activity_multiplier": 1.55,
  "tdee": 2769.79,
  "delta_bw": -5.0,
  "total_delta_kcal": -38500.0,
  "delta_kcal_per_day": -427.78,
  "kcal_per_kg_used": 7700,
  "daily_calories": 2342.01,
  "protein_g_per_day": 160.0,
  "fat_g_per_day": 64.0,
  "carbs_g_per_day": 250.0,
  "fiber_g_per_day": 24.0,
  "monthly_calories": 70260.30,
  "monthly_protein_g": 4800.0,
  "monthly_fat_g": 1920.0,
  "monthly_carbs_g": 7500.0,
  "monthly_fiber_g": 720.0,
  "created_at": "2026-03-28T10:00:00"
}
```

**Prefill response shape:**

```json
{
  "ok": true,
  "biometric": {
    "weight_kg": 80.0,
    "body_fat_pct": 18.0
  },
  "profile": {
    "height_cm": 175.0,
    "age_years": 28,
    "gender": "male"
  }
}
```

---

## 4. Frontend Component Registry

All new frontend files for the calculator feature:

| # | Component Name | File Path | Responsibility | Max Lines |
|---|---------------|-----------|----------------|-----------|
| 1 | `calculatorApi` | `frontend/lib/api/calculator.ts` | TypeScript types + API methods for calculator endpoints | 120 |
| 2 | `CalculatorPanel` | `frontend/app/(app)/health/_components/calculator/CalculatorPanel.tsx` | Main calculator orchestrator: form + result + history | 280 |
| 3 | `CalculatorForm` | `frontend/app/(app)/health/_components/calculator/CalculatorForm.tsx` | Input form: biometrics, activity, goal, calculate CTA | 250 |
| 4 | `ReportCard` | `frontend/app/(app)/health/_components/calculator/ReportCard.tsx` | Report result display: BMR, TDEE, daily targets, macro table, monthly | 200 |
| 5 | `ReportHistory` | `frontend/app/(app)/health/_components/calculator/ReportHistory.tsx` | Past reports list with summary and expand-to-detail | 150 |

Additionally, modifications to existing files:
- `frontend/app/(app)/health/page.tsx` — Extend view toggle to 3 options: Overview | Calculator | Optimizer
- `frontend/lib/translations/app.ts` — Extend `HealthPageTranslations` with calculator keys
- `frontend/app/(app)/health/_components/optimizer/OptimizerPanel.tsx` — Add time horizon selector + constraint auto-population
- `frontend/app/(app)/health/_components/optimizer/ConstraintBuilder.tsx` — Add "From Calculator" badge support

**Total new frontend files: 5**
**Estimated total lines: ~1,000**

---

## 5. Surface Specs

### 5.1 Health Page — Three-Tab View Toggle (Modification to Existing Page)

The existing two-tab toggle (`overview` | `optimizer`) expands to three tabs.

**Type change:**
```typescript
type ActiveView = 'overview' | 'calculator' | 'optimizer'
```

**Layout change to `page.tsx`:**

```
+----------------------------------------------------------+
| HEALTH (micro-label)    [Overview | Calculator | Optimizer] |
| Your Wellbeing                                    [LOG v]  |
+----------------------------------------------------------+
| (active view renders here)                                 |
+----------------------------------------------------------+
```

**Implementation:**
- Extend the existing `ActiveView` type to include `'calculator'`
- Add `'calculator'` to the pill button map
- When `activeView === 'calculator'`: render `<CalculatorPanel t={t} />`
- LOG dropdown only visible when `activeView === 'overview'`
- Pill label: `t.calculator` (new translation key)

**Mobile:** Three pills stack horizontally, same styling. If too narrow (< 360px), pills become text-only (no padding increase).

### 5.2 Calculator Form (Surface 1)

**File:** `frontend/app/(app)/health/_components/calculator/CalculatorForm.tsx`

#### Props Interface

```typescript
interface CalculatorFormProps {
  prefillData: {
    biometric: { weight_kg: number | null; body_fat_pct: number | null } | null
    profile: { height_cm: number; age_years: number; gender: string } | null
  } | null
  isLoading: boolean
  onCalculate: (input: CalculatorInput) => void
  isCalculating: boolean
}
```

#### Form Fields

| Field | Type | Label | Input | Auto-filled? | Required | Shown |
|-------|------|-------|-------|-------------|----------|-------|
| `weight_kg` | number | "Weight (kg)" | number, step 0.1 | From latest biometric | Yes | Always |
| `height_cm` | number | "Height (cm)" | number, step 0.1 | From saved profile | Yes | Always |
| `age_years` | number | "Age" | number, step 1 | From saved profile | Yes | Always |
| `gender` | string | "Gender" | segmented control (Male / Female) | From saved profile | Yes | Always |
| `body_fat_pct` | number | "Body fat %" | number, step 0.1 | From latest biometric | No | Always |
| `activity_level` | string | "Activity Level" | segmented control (5 options) | None | Yes | Always |
| `goal_type` | string | "Goal" | segmented control (Lose / Maintain / Gain) | None | Yes | Always |
| `goal_weight_kg` | number | "Goal Weight (kg)" | number, step 0.1 | None | If lose/gain | On goal selection |
| `goal_timeline_months` | number | "Timeline (months)" | number, step 1 | None | If lose/gain | On goal selection |

#### Layout

```
Desktop (>= 1024px):
+----------------------------------------------------------+
| CALORIE CALCULATOR (micro-label, health accent #8b4a3a)  |
| Plan Your Targets (Newsreader Light 300, #4b6646)        |
| Estimate your daily calorie and macro targets. (Manrope) |
+----------------------------------------------------------+
| ┌──── Form Card (specimen) ──────────────────────────┐   |
| │                                                      │ |
| │ BODY MEASUREMENTS (micro-label)                      │ |
| │ [Weight (kg)]    [Height (cm)]    [Age]              │ |
| │ [Body fat % (optional)]                              │ |
| │                                                      │ |
| │ GENDER (micro-label)                                 │ |
| │ [ Male ] [ Female ]                                  │ |
| │                                                      │ |
| │ ACTIVITY LEVEL (micro-label)                         │ |
| │ [Sedentary] [Light] [Moderate] [Very] [Extra]        │ |
| │                                                      │ |
| │ GOAL (micro-label)                                   │ |
| │ [ Lose ] [ Maintain ] [ Gain ]                       │ |
| │                                                      │ |
| │ ┌── (progressive: shown if lose/gain) ──┐            │ |
| │ │ [Goal Weight (kg)]  [Timeline (months)]│            │ |
| │ └──────────────────────────────────────┘              │ |
| │                                                      │ |
| │               [Calculate] (primary gradient pill)    │ |
| │                                                      │ |
| └──────────────────────────────────────────────────────┘ |
+----------------------------------------------------------+
```

#### Design Tokens

- Form card: `surface-container-lowest` (#ffffff), `border-radius: 0 16px 16px 16px`, `padding: 32px`
- Section labels: Manrope Bold 700 uppercase, `0.6875rem`, `+0.05em`, `#8b4a3a` (health accent dark)
- Input fields: `background: #ffffff`, `border: 1px solid rgba(173,180,168,0.2)`, `border-radius: 4px`, `padding: 10px 14px`
- Input labels: Manrope Bold 700, `0.75rem`, `#2e342b`, positioned 8px above field
- Auto-filled inputs: brief flash animation (fade from `#fdf0ed` to `transparent`, 400ms) on load, with small "Auto-filled" label in `#767d72`
- Segmented controls: pill buttons side by side, `border-radius: 100px`
  - Selected: `background: #fce8e4`, `color: #8b4a3a`
  - Unselected: `background: #f1f5eb`, `color: #5a6157`
- Goal weight/timeline fields: animate in with fade + slideDown (200ms ease) when lose/gain selected, animate out when maintain
- Calculate button: primary gradient pill (`#4b6646` → `#3f5a3a`), white text, `padding: 12px 40px`, `min-height: 48px`, centered
- Calculate button disabled: `opacity: 0.5`, `cursor: not-allowed` (when required fields missing)

#### Interaction

- On page load, `GET /api/v1/health/calculator/prefill` auto-fills weight, body_fat_pct, height, age, gender
- Auto-filled fields are editable — user can override any value
- Activity level is a required selection (no default) — segmented control, not dropdown
- Goal type defaults to no selection — user must pick one
- When "Lose" or "Gain" selected, goal weight + timeline fields animate in
- When "Maintain" selected, goal weight + timeline fields animate out
- "Calculate" button enabled only when all required fields are filled
- On submit: `POST /api/v1/health/calculator/calculate` → result rendered in ReportCard below

#### Mobile Behavior

- Single column, full width
- Segmented controls wrap to two rows if needed (activity level: 3+2 layout on narrow)
- All inputs full width
- Calculate button full width

#### Accessibility

- All inputs have `aria-label` attributes
- Segmented controls use `role="radiogroup"` with `role="radio"` on each option
- `aria-required="true"` on required fields
- Focus ring: `2px solid #4b6646`
- 44px min touch targets on all interactive elements

### 5.3 Report Card (Surface 2)

**File:** `frontend/app/(app)/health/_components/calculator/ReportCard.tsx`

#### Props Interface

```typescript
interface CalorieReport {
  id: number
  // Input snapshot
  weight_kg: number
  height_cm: number
  age_years: number
  gender: string
  body_fat_pct: number | null
  activity_level: string
  goal_type: string
  goal_weight_kg: number | null
  goal_timeline_months: number | null
  // Computed
  method_used: string
  lean_body_mass: number | null
  bmr: number
  activity_multiplier: number
  tdee: number
  // Delta
  delta_bw: number | null
  total_delta_kcal: number | null
  delta_kcal_per_day: number | null
  kcal_per_kg_used: number | null
  // Daily targets
  daily_calories: number
  protein_g_per_day: number
  fat_g_per_day: number
  carbs_g_per_day: number
  fiber_g_per_day: number
  // Monthly targets
  monthly_calories: number
  monthly_protein_g: number
  monthly_fat_g: number
  monthly_carbs_g: number
  monthly_fiber_g: number
  // Meta
  created_at: string
}

interface Warning {
  type: string
  message: string
}

interface ReportCardProps {
  report: CalorieReport
  warnings: Warning[]
  isLatest?: boolean            // show "Latest Report" badge
  expanded?: boolean            // for history: start collapsed
  onToggleExpand?: () => void   // for history: toggle detail
}
```

#### Layout

```
+----------------------------------------------------------+
| YOUR DAILY TARGETS (micro-label, #8b4a3a)                |
|                                                          |
| ┌── Daily Calorie Target ────────────────────────────┐   |
| │      2,342 kcal/day (Newsreader Light 300, large)  │   |
| │ ┌─── (warning card, if any) ───────────────────┐   │   |
| │ │ ⚠ This timeline may result in a very low...  │   │   |
| │ └─────────────────────────────────────────────────┘ │   |
| └────────────────────────────────────────────────────┘   |
|                                                          |
| ┌── BMR Breakdown ───────────────────────────────────┐   |
| │ Method: Katch-McArdle                              │   |
| │ Lean Body Mass: 65.6 kg                            │   |
| │ BMR: 1,787 kcal/day                                │   |
| │ Activity: Moderately Active (×1.55)                │   |
| │ TDEE: 2,770 kcal/day                               │   |
| │ Daily adjustment: -428 kcal/day                    │   |
| └────────────────────────────────────────────────────┘   |
|                                                          |
| ┌── Macro Targets ───────────────────────────────────┐   |
| │         Daily          Monthly (×30)               │   |
| │ Protein  160g          4,800g                      │   |
| │ Fat       64g          1,920g                      │   |
| │ Carbs    250g          7,500g                      │   |
| │ Fiber     24g            720g                      │   |
| │ Calories 2,342 kcal   70,260 kcal                  │   |
| └────────────────────────────────────────────────────┘   |
|                                                          |
| ▸ Delta Breakdown (expandable, hidden by default)        |
+----------------------------------------------------------+
```

#### Design Tokens

- Report container: NO wrapping card — render directly below form (content breathes)
- Daily calorie target: Newsreader Light 300, `2rem`, `#4b6646`, centered. Below it: goal type pill badge (`#fce8e4` bg, `#8b4a3a` text, `border-radius: 100px`, `0.6875rem`)
- Warning cards: `background: #fdf0ed`, `border-radius: 0 12px 12px 12px`, `padding: 12px 16px`. Icon: triangle-alert from lucide-react, `color: #8b4a3a`. Text: Manrope 400, `0.8125rem`, `#2e342b`
- BMR breakdown card: `surface-container-lowest` (#ffffff), specimen radius, `padding: 24px`
  - Labels: Manrope 400, `0.8125rem`, `#767d72`
  - Values: Manrope 600, `0.875rem`, `#2e342b`
  - Method badge: pill, `#f1f5eb` bg, `#5a6157` text
- Macro table: CSS grid (3 columns: label, daily, monthly). No `<table>` tag.
  - Header row: micro-label style
  - Data rows: alternating `#f8faf2` / `#ffffff`
  - Monthly column: `#767d72` color (secondary emphasis)
- Delta breakdown: expandable section with chevron. Hidden by default (progressive disclosure).
  - Contains: delta_bw, total_delta_kcal, delta_kcal_per_day, kcal_per_kg assumption
  - All in Manrope 400, `0.8125rem`, `#5a6157`

#### Interaction

- Report card animates in after calculation: fade + slideUp (300ms ease)
- Warning cards animate in with a slight delay (100ms after report)
- Delta breakdown toggle: chevron rotates 90° on expand
- If `expanded` prop is false (history mode): show only daily_calories + goal_type as summary row

#### Mobile Behavior

- Full width, single column
- Macro table: daily and monthly columns may wrap (stack vertically per macro if < 360px)
- Warning card: full width

### 5.4 Report History (Surface 3)

**File:** `frontend/app/(app)/health/_components/calculator/ReportHistory.tsx`

#### Props Interface

```typescript
interface ReportHistoryProps {
  reports: CalorieReport[]
  isLoading: boolean
  total: number
  page: number
  pages: number
  onPageChange: (page: number) => void
}
```

#### Layout

```
+----------------------------------------------------------+
| PAST REPORTS (micro-label)                               |
|                                                          |
| ┌── Report Row ──────────────────────────────────────┐   |
| │ Mar 28, 2026   Lose   2,342 kcal/day          [▸] │   |
| └────────────────────────────────────────────────────┘   |
| ┌── Report Row (expanded) ───────────────────────────┐   |
| │ Mar 25, 2026   Maintain   2,770 kcal/day       [▾] │   |
| │ ┌── (full ReportCard rendered here) ───────────┐   │   |
| │ └─────────────────────────────────────────────────┘ │   |
| └────────────────────────────────────────────────────┘   |
| ┌── Report Row ──────────────────────────────────────┐   |
| │ Mar 20, 2026   Gain   3,200 kcal/day          [▸] │   |
| └────────────────────────────────────────────────────┘   |
|                                                          |
| (empty state if no reports)                              |
+----------------------------------------------------------+
```

#### Design Tokens

- Container: NO wrapping card — render below the current report area
- Section header: "PAST REPORTS" — Manrope Bold 700 uppercase, `0.6875rem`, `+0.05em`, `#8b4a3a`
- Report rows: `background: #f8faf2`, `border-radius: 0 10px 10px 10px`, `padding: 14px 18px`, `margin-bottom: 8px`
  - Date: Manrope 400, `0.8125rem`, `#5a6157`
  - Goal type badge: pill, `#fce8e4` bg, `#8b4a3a` text, `0.6875rem`
  - Daily kcal: Manrope 600, `0.875rem`, `#2e342b`
  - Expand chevron: `color: #adb4a8`, hover `#4b6646`, `min-width: 44px` touch target
- Expanded state: ReportCard rendered below the summary row (inside the same container), with `expanded={true}`
- Empty state: "No reports yet. Use the calculator above to generate your first report." — Manrope 400, `0.875rem`, `#767d72`, centered
- Pagination: if > 20 reports, show page controls (secondary pills: prev/next)

#### Interaction

- Click anywhere on a report row (or the chevron) to expand/collapse
- Only one report expanded at a time (accordion pattern)
- Row entrance: staggered animation (35ms delay between rows)
- Expanded content: fade + slideDown (200ms ease)

#### Mobile Behavior

- Full width
- Summary row: date and kcal on first line, goal badge below
- Chevron stays right-aligned

### 5.5 Calculator Panel (Main Orchestrator)

**File:** `frontend/app/(app)/health/_components/calculator/CalculatorPanel.tsx`

#### Props Interface

```typescript
interface CalculatorPanelProps {
  t: HealthPageTranslations
}
```

#### State Variables

```typescript
// Prefill data
const { data: prefillData, isLoading: prefillLoading } = useQuery({
  queryKey: ['health', 'calculator', 'prefill'],
  queryFn: () => calculatorApi.getPrefill(),
})

// Latest report (shown immediately on load if exists)
const { data: latestData } = useQuery({
  queryKey: ['health', 'calculator', 'latest'],
  queryFn: () => calculatorApi.getLatestReport(),
})

// Report history
const [historyPage, setHistoryPage] = useState(1)
const { data: historyData, isLoading: historyLoading } = useQuery({
  queryKey: ['health', 'calculator', 'reports', historyPage],
  queryFn: () => calculatorApi.listReports({ page: historyPage }),
})

// Current calculation result (from the form submission in this session)
const [currentResult, setCurrentResult] = useState<{ report: CalorieReport; warnings: Warning[] } | null>(null)

// Calculate mutation
const calculateMutation = useMutation({
  mutationFn: (input: CalculatorInput) => calculatorApi.calculate(input),
  onSuccess: (data) => {
    setCurrentResult({ report: data.report, warnings: data.warnings })
    queryClient.invalidateQueries({ queryKey: ['health', 'calculator'] })
  },
})
```

#### Layout

```
+----------------------------------------------------------+
| CALORIE CALCULATOR (micro-label)                         |
| Plan Your Targets (Newsreader Light 300)                 |
| Estimate your daily calorie and macro targets. (Manrope) |
+----------------------------------------------------------+
| [CalculatorForm — always visible]                        |
+----------------------------------------------------------+
| [ReportCard — appears after calculate, or shows latest]  |
+----------------------------------------------------------+
| [ReportHistory — collapsible, below report card]         |
+----------------------------------------------------------+
```

#### Data Flow

1. On mount: fetch prefill data + latest report + report history
2. If latest report exists and no new calculation yet: show it with "Latest Report" badge
3. User fills form and clicks "Calculate": `POST /api/v1/health/calculator/calculate`
4. On success: `currentResult` replaces the displayed report. History list refreshes.
5. Report history is always available below (collapsible section)

---

## 6. Optimizer Modifications

These changes are made to **existing** optimizer files built from `HEALTH_OPTIMIZER_BUILD_SPEC.md`. They must be applied AFTER both the calculator and optimizer base are fully built.

### 6.1 Time Horizon Selector

**File:** `frontend/app/(app)/health/_components/optimizer/OptimizerPanel.tsx` — **MODIFY**

Add a new state variable:

```typescript
const [horizonDays, setHorizonDays] = useState<number>(30)
```

Add a new UI element in the optimizer header area, between the page subtitle and the food library:

```
+----------------------------------------------------------+
| MACRO & COST OPTIMIZER (micro-label)                     |
| Plan Your Nutrition (Newsreader Light 300)               |
| Find the optimal food combination. (Manrope)             |
|                                                          |
| TIME HORIZON (micro-label)                               |
| Optimizing for [ 1 ▼ ] month(s)                         |
+----------------------------------------------------------+
```

**Implementation:**
- Dropdown select: values `[1, 2, 3, 6]` corresponding to `[30, 60, 90, 180]` days
- Display format: "Optimizing for N month(s)" with the number in a select dropdown
- Select: `background: #ffffff`, `border: 1px solid rgba(173,180,168,0.2)`, `border-radius: 4px`, `width: 60px`
- Label: Manrope 400, `0.875rem`, `#5a6157`
- When horizon changes: all auto-populated constraint values are recalculated (`daily × horizonDays`)

### 6.2 Constraint Auto-Population Flow

**File:** `frontend/app/(app)/health/_components/optimizer/OptimizerPanel.tsx` — **MODIFY**

Add a query for the latest calorie report:

```typescript
const { data: latestReport } = useQuery({
  queryKey: ['health', 'calculator', 'latest'],
  queryFn: () => calculatorApi.getLatestReport(),
})
```

**Auto-population logic (runs when `latestReport` or `horizonDays` changes):**

```typescript
useEffect(() => {
  if (!latestReport?.report) return
  // Only auto-populate if constraints are empty (don't overwrite user edits)
  if (constraints.length > 0) return

  const r = latestReport.report
  const h = horizonDays

  const autoConstraints: Constraint[] = [
    { id: crypto.randomUUID(), category: 'calories', operator: '=', value: Math.round(r.daily_calories * h), source: 'calculator' },
    { id: crypto.randomUUID(), category: 'protein', operator: '>=', value: Math.round(r.protein_g_per_day * h), source: 'calculator' },
    { id: crypto.randomUUID(), category: 'fat', operator: '>=', value: Math.round(r.fat_g_per_day * h), source: 'calculator' },
    { id: crypto.randomUUID(), category: 'carbohydrate', operator: '>=', value: Math.round(r.carbs_g_per_day * h), source: 'calculator' },
    { id: crypto.randomUUID(), category: 'fiber', operator: '>=', value: Math.round(r.fiber_g_per_day * h), source: 'calculator' },
  ]
  setConstraints(autoConstraints)
}, [latestReport, horizonDays])
```

**When horizon changes and constraints already have `source: 'calculator'`:**

```typescript
useEffect(() => {
  if (!latestReport?.report) return
  const r = latestReport.report
  const h = horizonDays

  setConstraints(prev => prev.map(c => {
    if (c.source !== 'calculator') return c  // don't touch user-added constraints
    const dailyMap: Record<string, number> = {
      calories: r.daily_calories,
      protein: r.protein_g_per_day,
      fat: r.fat_g_per_day,
      carbohydrate: r.carbs_g_per_day,
      fiber: r.fiber_g_per_day,
    }
    const daily = dailyMap[c.category]
    if (daily == null) return c
    return { ...c, value: Math.round(daily * h) }
  }))
}, [horizonDays])
```

### 6.3 Constraint Type Extension

**File:** `frontend/lib/optimizer/solveLP.ts` — **MODIFY**

Extend the `Constraint` interface:

```typescript
export interface Constraint {
  id: string
  category: 'calories' | 'protein' | 'carbohydrate' | 'fat' | 'fiber' | 'cost'
  operator: '>=' | '<=' | '='
  value: number
  source?: 'calculator' | 'user'   // NEW — tracks origin for badge display
}
```

The `source` field is optional and display-only. It does not affect the solver logic.

### 6.4 "From Calculator" Badge

**File:** `frontend/app/(app)/health/_components/optimizer/ConstraintBuilder.tsx` — **MODIFY**

For each constraint row, check `constraint.source === 'calculator'` and render a badge:

```
[Calories ▼]  [= ▼]  [70260]  [From Calculator]  [×]
```

Badge design:
- Pill shape: `border-radius: 100px`
- Background: `#fdf0ed` (health accent tint)
- Text: Manrope 500, `0.6875rem`, `#8b4a3a`
- Content: "From Calculator" (translated via `t.fromCalculator`)

When the user manually edits the value of a calculator-sourced constraint:
- The `source` changes from `'calculator'` to `'user'`
- The badge disappears
- The constraint is no longer recalculated when horizon changes

When the user removes a calculator-sourced constraint:
- It is removed normally
- If all calculator constraints are removed and the user opens optimizer again, they will not re-auto-populate (constraints.length > 0 guard)

### 6.5 Empty State — No Report Exists

**File:** `frontend/app/(app)/health/_components/optimizer/ConstraintBuilder.tsx` — **MODIFY**

When the constraint list is empty AND no latest report exists, show a subtle prompt inside the constraint section:

```
+----------------------------------------------------------+
| CONSTRAINTS                                              |
|                                                          |
| Set up your calorie targets in the Calculator tab to     |
| get personalized suggestions here.                       |
|                                                          |
| [+ Add Constraint]                                       |
+----------------------------------------------------------+
```

- Prompt text: Manrope 400, `0.8125rem`, `#767d72`
- "Calculator tab" is a clickable link that switches `activeView` to `'calculator'`
  - Pass a callback from `page.tsx` through `OptimizerPanel` to `ConstraintBuilder` for this

### 6.6 Operator Defaults (From Calculator)

When auto-populating constraints from the calculator report, these operators are used:

| Category | Operator | Rationale |
|----------|----------|-----------|
| `calories` | `=` | Exact target — the user wants to hit this number |
| `protein` | `>=` | Minimum floor — at least this much |
| `fat` | `>=` | Minimum floor |
| `carbohydrate` | `>=` | Minimum floor |
| `fiber` | `>=` | Minimum floor |

---

## 7. Boundaries

### 7.1 Forbidden

| # | Constraint | Rationale |
|---|-----------|-----------|
| F1 | BMI calculation or display | Explicitly cut — not useful, potentially harmful framing |
| F2 | Body type classification (ectomorph/mesomorph/endomorph) | Explicitly cut — pseudoscience |
| F3 | Macro ratio recommendations beyond fixed formulas | Explicitly cut |
| F4 | Meal timing or intermittent fasting suggestions | Explicitly cut |
| F5 | Supplement recommendations | Explicitly cut |
| F6 | Medical or dietary prescription language | Later-wave domain + emotional contract |
| F7 | Comparison to population averages or "ideal weight" | Explicitly cut |
| F8 | Integration with health_nutrition_log | Calculator is planning, not tracking |
| F9 | Export/download of reports | Explicitly cut |
| F10 | Sharing reports | Explicitly cut |
| F11 | Graph/chart of report history | Plain list is sufficient for v1 |
| F12 | Editing past reports | Immutable by design |
| F13 | "You should..." / "You must..." tone | Constitution §9 |
| F14 | Language framing weight loss as inherently good or gain as bad | Emotional contract |
| F15 | Modifying existing health_biometric table | Scope boundary — additive only |
| F16 | Cross-domain imports (except User, UserPreference) | Architecture rule |
| F17 | Pure black text or grey shadows | DESIGN.md rules |
| F18 | 1px borders, square buttons | DESIGN.md rules |
| F19 | Shaming language around weight direction | Emotional contract |
| F20 | Writing to health_nutrition_log | Calculator is standalone |

### 7.2 Required

| # | Constraint | Implementation |
|---|-----------|----------------|
| R1 | Read-first hierarchy | Latest report shown on load; form is secondary |
| R2 | Progressive disclosure (goal fields) | goal_weight + timeline animate in only when lose/gain selected |
| R3 | Calm tone per constitution §9 | All warnings use observation tone ("This may result in...") |
| R4 | Auto-fill from biometrics | Weight + body_fat_pct from latest health_biometric record |
| R5 | Immutable reports | Create-only — no update or delete endpoints |
| R6 | Unrealistic timeline/surplus warnings | Observation tone, not hard blocks |
| R7 | All LifeOS layering rules respected | Controller → Service → Model → Schema → Events |
| R8 | Migration is additive-only | New table, no modifications to existing tables |
| R9 | Events follow catalog pattern | `version: "v1"`, payload documented |
| R10 | 44px min touch targets, ARIA labels | All buttons, segmented controls |
| R11 | Editorial presentation | Newsreader headlines, Manrope body, specimen cards |
| R12 | Optimizer constraint bridge is non-destructive | Suggestions only, user can edit/remove any constraint |
| R13 | Pill-shaped buttons only | `border-radius: 100px` everywhere |
| R14 | Specimen card pattern | `border-radius: 0 16px 16px 16px` on all cards |
| R15 | Sage-tinted shadows only | `rgba(46, 52, 43, 0.06)` |
| R16 | 2rem minimum card padding | `padding: 32px` |
| R17 | Domain accent only on selection | Health accent on selected pills, badges |
| R18 | `prefers-reduced-motion` support | Disable animations when user prefers |
| R19 | Translations for all user-facing text | All strings via `getAppTranslations(lang).health.calculator.*` |
| R20 | Health profile persists via UserPreference | height/age/gender saved for future visits |

---

## 8. Dependency Map (Build Order DAG)

```
BACKEND (must complete before any frontend calculator work)
═══════════════════════════════════════════════════════════

Step B1: Migration
   └─ 20260328_health_calorie_report.py (find current head first — likely 20260328_health_food_library)
         │
Step B2: Model + Mapper (parallel)
   ├─ models/calorie_report.py
   ├─ models/__init__.py (add CalorieReport)
   └─ mappers.py (add map_calorie_report + import CalorieReport)
         │
Step B3: Schemas
   └─ schemas/calculator_schemas.py
         │
Step B4: Events (parallel with B3)
   ├─ events.py (add HEALTH_CALORIE_REPORT_CREATED + catalog entry)
   └─ core/events/semantic_contracts.py (add 1 contract)
         │
Step B5: Service
   ├─ services/calculator_service.py (calculate, create_report, get_warnings, queries, profile)
   └─ services/__init__.py (add 9 new imports)
         │
Step B6: Controller + Registration
   ├─ controllers/calculator_api.py
   └─ __init__.py (register blueprint at /api/v1/health/calculator)
         │
Step B7: Run migration + verify
   └─ cd lifeos && python -m alembic upgrade head
   └─ Manual test: curl endpoints


FRONTEND — CALCULATOR (depends on B7 complete)
═══════════════════════════════════════════════

Step F1: API client + translation keys
   ├─ lib/api/calculator.ts (types + API methods)
   └─ lib/translations/app.ts (extend HealthPageTranslations with calculator keys)
         │
Step F2: Leaf components (parallel)
   ├─ calculator/CalculatorForm.tsx
   ├─ calculator/ReportCard.tsx
   └─ calculator/ReportHistory.tsx
         │
Step F3: Calculator panel (depends on F2)
   └─ calculator/CalculatorPanel.tsx (orchestrates form + report + history)
         │
Step F4: Page integration
   └─ page.tsx (extend ActiveView to 3 tabs, render CalculatorPanel)


OPTIMIZER MODIFICATIONS (depends on F4 + optimizer base complete)
════════════════════════════════════════════════════════════════

Step O1: Type extension
   └─ lib/optimizer/solveLP.ts (add `source` field to Constraint)
         │
Step O2: Optimizer panel changes (parallel)
   ├─ OptimizerPanel.tsx (add horizonDays state, latestReport query, auto-population logic)
   └─ ConstraintBuilder.tsx (add "From Calculator" badge, empty state prompt)
         │
Step O3: Translation keys
   └─ lib/translations/app.ts (add optimizer bridge keys: fromCalculator, timeHorizon, etc.)
```

**Critical ordering notes:**
- The calculator migration (`20260328_health_calorie_report`) must chain from the food library migration (`20260328_health_food_library`). Run `alembic heads` to confirm.
- The optimizer modifications (O1-O3) must come LAST — they depend on both the calculator API (`/reports/latest`) and the optimizer base being fully functional.
- The calculator frontend and optimizer base can be built in parallel if both backend surfaces are complete.

---

## 9. Sonnet Execution Instructions

### Pre-flight Checks

Before starting, verify:
1. `lifeos/domains/health/` exists with controllers/, models/, schemas/, services/ dirs
2. `lifeos/migrations/versions/` exists
3. `lifeos/lifeos_platform/outbox/__init__.py` exports `enqueue`
4. `lifeos/domains/health/models/food_library.py` exists (optimizer already built)
5. `lifeos/domains/health/events.py` already contains `HEALTH_FOOD_LIBRARY_CREATED` etc.
6. `frontend/lib/api/client.ts` exports `apiFetch`, `apiGet`, `apiPost`
7. `frontend/app/(app)/health/page.tsx` exists with `ActiveView = 'overview' | 'optimizer'`
8. `frontend/app/(app)/health/_components/optimizer/` exists with optimizer components
9. `frontend/lib/optimizer/solveLP.ts` exists with `Constraint` interface
10. Run `cd lifeos && python -m alembic heads` — record the current head revision ID

### Backend Steps (B1-B7)

---

#### Step B1: Create migration

**Action:** Create `lifeos/migrations/versions/20260328_health_calorie_report.py`
**Max lines:** 65
**Implements:** `health_calorie_report` table with all columns and indexes per section 3.1
**Critical:** Set `down_revision` to the value from pre-flight check #10 (likely `20260328_health_food_library`)
**Verification:** `cd lifeos && python -m alembic upgrade head` succeeds. `sqlite3 instance/lifeos.db ".schema health_calorie_report"` shows the table.

---

#### Step B2: Create model + update mapper + update __init__

**Action:** Create `lifeos/domains/health/models/calorie_report.py` per section 3.2
**Max lines:** 55
**Action:** Edit `lifeos/domains/health/models/__init__.py` — add `from .calorie_report import CalorieReport` and add to `__all__`
**Action:** Edit `lifeos/domains/health/mappers.py` — add `map_calorie_report` function per section 3.5 mapper addition, add import of `CalorieReport`
**Verification:** `python -c "from lifeos.domains.health.models.calorie_report import CalorieReport; print(CalorieReport.__tablename__)"` prints `health_calorie_report`

---

#### Step B3: Create schemas

**Action:** Create `lifeos/domains/health/schemas/calculator_schemas.py` per section 3.3
**Max lines:** 40
**Verification:** `python -c "from lifeos.domains.health.schemas.calculator_schemas import CalculatorInput; print(CalculatorInput.model_json_schema())"` shows all fields with validators

---

#### Step B4: Add event + semantic contract

**Action:** Edit `lifeos/domains/health/events.py` — add `HEALTH_CALORIE_REPORT_CREATED` constant, 1 catalog entry, update `__all__`
**Action:** Edit `lifeos/core/events/semantic_contracts.py` — add 1 `EventSemanticContract` entry
**Verification:** `python -c "from lifeos.domains.health.events import HEALTH_CALORIE_REPORT_CREATED; print(HEALTH_CALORIE_REPORT_CREATED)"` prints `health.calorie_report.created`

---

#### Step B5: Create service

**Action:** Create `lifeos/domains/health/services/calculator_service.py` per section 3.4
**Max lines:** 220
**Action:** Edit `lifeos/domains/health/services/__init__.py` — add imports and `__all__` entries for all 9 functions
**Verification:** With app context, `services.calculate(weight_kg=80, height_cm=175, age_years=28, gender="male", body_fat_pct=18, activity_level="moderately_active", goal_type="maintain", goal_weight_kg=None, goal_timeline_months=None)` returns a dict with `bmr`, `tdee`, `daily_calories`.

---

#### Step B6: Create controller + register blueprint

**Action:** Create `lifeos/domains/health/controllers/calculator_api.py` per section 3.5
**Max lines:** 100
**Action:** Edit `lifeos/__init__.py` — add blueprint import and `app.register_blueprint(calculator_api_bp, url_prefix="/api/v1/health/calculator")` after the existing health registration lines
**Verification:** Start the dev server. `curl -H "Authorization: Bearer <token>" http://localhost:5000/api/v1/health/calculator/prefill` returns `{"ok": true, "biometric": ..., "profile": ...}`

---

#### Step B7: Run migration + end-to-end test

**Action:** `cd lifeos && python -m alembic upgrade head`
**Verification:** All five endpoints work:
1. GET `/api/v1/health/calculator/prefill` → 200 with biometric + profile data
2. POST `/api/v1/health/calculator/calculate` → 201 with report + warnings
3. GET `/api/v1/health/calculator/reports` → 200 with reports array
4. GET `/api/v1/health/calculator/reports/latest` → 200 with latest report (or null)
5. GET `/api/v1/health/calculator/reports/:id` → 200 with single report or 404

---

### Frontend Steps (F1-F4)

---

#### Step F1: Create API client + extend translations

**Action:** Create `frontend/lib/api/calculator.ts`
**Max lines:** 120

Types to define:

```typescript
export interface CalorieReport {
  id: number
  weight_kg: number
  height_cm: number
  age_years: number
  gender: string
  body_fat_pct: number | null
  activity_level: string
  goal_type: string
  goal_weight_kg: number | null
  goal_timeline_months: number | null
  method_used: string
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
  created_at: string
}

export interface CalculatorInput {
  weight_kg: number
  height_cm: number
  age_years: number
  gender: 'male' | 'female'
  body_fat_pct?: number | null
  activity_level: string
  goal_type: 'lose' | 'gain' | 'maintain'
  goal_weight_kg?: number | null
  goal_timeline_months?: number | null
  save_profile?: boolean
}

export interface Warning {
  type: string
  message: string
}

export interface PrefillResponse {
  ok: boolean
  biometric: { weight_kg: number | null; body_fat_pct: number | null } | null
  profile: { height_cm: number; age_years: number; gender: string } | null
}
```

API methods:

```typescript
export const calculatorApi = {
  getPrefill: () => apiGet<PrefillResponse>('/api/v1/health/calculator/prefill'),
  calculate: (data: CalculatorInput) => apiPost<{ ok: boolean; report: CalorieReport; warnings: Warning[] }>('/api/v1/health/calculator/calculate', data),
  listReports: (params?: { page?: number; per_page?: number }) => apiGet<{ ok: boolean; reports: CalorieReport[]; page: number; pages: number; total: number }>(`/api/v1/health/calculator/reports?page=${params?.page ?? 1}&per_page=${params?.per_page ?? 20}`),
  getLatestReport: () => apiGet<{ ok: boolean; report: CalorieReport | null }>('/api/v1/health/calculator/reports/latest'),
  getReport: (id: number) => apiGet<{ ok: boolean; report: CalorieReport }>(`/api/v1/health/calculator/reports/${id}`),
}
```

**Action:** Edit `frontend/lib/translations/app.ts` — extend `HealthPageTranslations` with calculator keys:

```typescript
// Add to HealthPageTranslations interface:
calculator: string                    // "Calculator"
planTargets: string                   // "Plan Your Targets"
planTargetsSub: string                // "Estimate your daily calorie and macro targets."
bodyMeasurements: string              // "Body Measurements"
weightKg: string                      // "Weight (kg)"
heightCm: string                      // "Height (cm)"
age: string                           // "Age"
genderLabel: string                   // "Gender"
male: string                          // "Male"
female: string                        // "Female"
bodyFatPct: string                    // "Body fat % (optional)"
activityLevel: string                 // "Activity Level"
sedentary: string                     // "Sedentary"
lightlyActive: string                 // "Lightly Active"
moderatelyActive: string              // "Moderately Active"
veryActive: string                    // "Very Active"
extraActive: string                   // "Extra Active"
goal: string                          // "Goal"
lose: string                          // "Lose"
maintain: string                      // "Maintain"
gain: string                          // "Gain"
goalWeightKg: string                  // "Goal Weight (kg)"
timelineMonths: string                // "Timeline (months)"
calculate: string                     // "Calculate"
calculating: string                   // "Calculating..."
yourDailyTargets: string              // "Your Daily Targets"
kcalPerDay: string                    // "kcal/day"
bmrBreakdown: string                  // "BMR Breakdown"
method: string                        // "Method"
katchMcardle: string                  // "Katch-McArdle"
mifflinStJeor: string                 // "Mifflin-St Jeor"
leanBodyMass: string                  // "Lean Body Mass"
bmr: string                           // "BMR"
activity: string                      // "Activity"
tdee: string                          // "TDEE"
dailyAdjustment: string               // "Daily adjustment"
macroTargets: string                  // "Macro Targets"
daily: string                         // "Daily"
monthlyX30: string                    // "Monthly (×30)"
deltaBreakdown: string                // "Delta Breakdown"
pastReports: string                   // "Past Reports"
latestReport: string                  // "Latest Report"
noReportsYet: string                  // "No reports yet. Use the calculator above to generate your first report."
autoFilled: string                    // "Auto-filled"
lowIntakeWarning: string              // "This timeline may result in a very low daily intake. Consider extending the timeline or adjusting your goal weight."
highSurplusWarning: string            // "This is a significant surplus. A more gradual approach may be easier to sustain."
// Optimizer bridge keys
fromCalculator: string                // "From Calculator"
timeHorizon: string                   // "Time Horizon"
optimizingFor: string                 // "Optimizing for"
months: string                        // "month(s)"
calcPrompt: string                    // "Set up your calorie targets in the Calculator tab to get personalized suggestions here."
```

Provide Korean and Chinese translations for all new keys.

**Verification:** TypeScript compiles. `calculatorApi.calculate(...)` type-checks. All translation keys exist in en/ko/zh.

---

#### Step F2: Create leaf components (parallel)

First ensure the directory exists: `mkdir -p frontend/app/(app)/health/_components/calculator`

Build these three files simultaneously:

- `CalculatorForm.tsx` (250 lines) — per section 5.2. Segmented controls for gender, activity, goal. Progressive disclosure for goal fields. Auto-fill from prefill data. Calculate CTA.
- `ReportCard.tsx` (200 lines) — per section 5.3. BMR breakdown, macro table, daily calorie hero number, warning cards, expandable delta breakdown.
- `ReportHistory.tsx` (150 lines) — per section 5.4. Accordion list of past reports with summary rows. Expands to full ReportCard.

**Per-component verification:** Each renders without TypeScript errors. Props interface matches the spec. CalculatorForm shows segmented controls for all selection fields.

---

#### Step F3: Create calculator panel

**Action:** Create `CalculatorPanel.tsx` (280 lines) — per section 5.5
- Orchestrates form + report + history
- Fetches prefill, latest report, and report list via React Query
- Manages calculate mutation
- Passes results to ReportCard and ReportHistory

**Verification:** CalculatorPanel renders with empty state (no reports). Filling in the form and clicking "Calculate" sends the API request and displays the report card.

---

#### Step F4: Integrate into health page

**Action:** Edit `frontend/app/(app)/health/page.tsx`
- Change `ActiveView` type from `'overview' | 'optimizer'` to `'overview' | 'calculator' | 'optimizer'`
- Add `'calculator'` to the pill button map array
- Add conditional render: `{activeView === 'calculator' && <CalculatorPanel t={t} />}`
- Import `CalculatorPanel` from `./_components/calculator/CalculatorPanel`
- Pass `onSwitchToCalculator` callback through optimizer components for the empty-state link

**Verification checklist:**
1. Health page loads with "Overview" selected by default — existing functionality unchanged
2. Clicking "Calculator" shows the calculator panel
3. Auto-fill works: weight and body_fat_pct from biometrics, height/age/gender from profile
4. Selecting "Lose" shows goal weight and timeline fields
5. Selecting "Maintain" hides goal weight and timeline fields
6. Clicking "Calculate" produces a report card with correct values
7. Warnings appear for low intake / high surplus scenarios
8. Past reports list shows history with expand/collapse
9. Switching to "Optimizer" shows the optimizer with three-tab nav working
10. Switching back to "Overview" shows the original health page content
11. All text from translation keys (no hardcoded English)
12. No TypeScript errors, no console warnings

---

### Optimizer Modification Steps (O1-O3)

---

#### Step O1: Extend Constraint type

**Action:** Edit `frontend/lib/optimizer/solveLP.ts`
- Add `source?: 'calculator' | 'user'` field to `Constraint` interface
- No changes to solver logic (source is display-only)

**Verification:** Existing optimizer tests/behavior unchanged. TypeScript compiles.

---

#### Step O2: Optimizer panel + constraint builder changes

**Action:** Edit `frontend/app/(app)/health/_components/optimizer/OptimizerPanel.tsx`
- Add `horizonDays` state (default 30)
- Add time horizon dropdown UI per section 6.1
- Add `latestReport` query per section 6.2
- Add auto-population `useEffect` per section 6.2
- Add horizon recalculation `useEffect` per section 6.2
- Pass `latestReport` and `onSwitchToCalculator` to ConstraintBuilder

**Action:** Edit `frontend/app/(app)/health/_components/optimizer/ConstraintBuilder.tsx`
- Accept new prop: `latestReportExists: boolean`
- Accept new prop: `onSwitchToCalculator?: () => void`
- Render "From Calculator" badge on constraints where `source === 'calculator'` per section 6.4
- Render empty-state calculator prompt when no constraints and no latest report per section 6.5
- When user edits a calculator-sourced constraint value: change `source` to `'user'`

**Verification checklist:**
1. Open optimizer with no calculator reports: empty constraint builder with calculator prompt
2. Create a calculator report (switch to Calculator tab, fill form, calculate)
3. Switch back to Optimizer: constraints auto-populated with "From Calculator" badges
4. Change time horizon to 2 months: constraint values double
5. Edit a constraint value: "From Calculator" badge disappears
6. Add a manual constraint: no badge, not affected by horizon changes
7. Remove all constraints, switch to overview, switch back to optimizer: auto-populate fires again (constraints were empty)
