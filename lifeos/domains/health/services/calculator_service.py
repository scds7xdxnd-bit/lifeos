"""Calorie calculator service — calculation logic and report persistence."""

from __future__ import annotations

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

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

PROTEIN_FACTOR = Decimal("2.0")  # g per kg bodyweight
FAT_FACTOR = Decimal("0.8")  # g per kg bodyweight
CARBS_FIXED = Decimal("250")  # g per day (constant)
FIBER_FIXED = Decimal("24")  # g per day (constant)


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
        warnings.append(
            {
                "type": "low_intake",
                "message": (
                    "This timeline may result in a very low daily intake. "
                    "Consider extending the timeline or adjusting your goal weight."
                ),
            }
        )

    if goal_type == "gain" and daily_calories > tdee + 1000:
        warnings.append(
            {
                "type": "high_surplus",
                "message": ("This is a significant surplus. " "A more gradual approach may be easier to sustain."),
            }
        )

    return warnings


# ── Persist report ────────────────────────────────────────────────


def create_report(
    user_id: int,
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
    computed: dict,
) -> CalorieReport:
    """Persist a calorie report. Returns the saved record."""
    report = CalorieReport(
        user_id=user_id,
        weight_kg=weight_kg,
        height_cm=height_cm,
        age_years=age_years,
        gender=gender,
        body_fat_pct=body_fat_pct,
        activity_level=activity_level,
        goal_type=goal_type,
        goal_weight_kg=goal_weight_kg,
        goal_timeline_months=goal_timeline_months,
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


# ── Mutate reports ───────────────────────────────────────────────


def delete_report(user_id: int, report_id: int) -> bool:
    """Delete a report scoped to user. Returns True if deleted, False if not found."""
    report = CalorieReport.query.filter_by(id=report_id, user_id=user_id).first()
    if not report:
        return False
    db.session.delete(report)
    db.session.commit()
    return True


def update_report(
    user_id: int,
    report_id: int,
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
) -> CalorieReport | None:
    """Re-calculate and update an existing report in place. Returns updated record or None."""
    report = CalorieReport.query.filter_by(id=report_id, user_id=user_id).first()
    if not report:
        return None
    computed = calculate(
        weight_kg=weight_kg,
        height_cm=height_cm,
        age_years=age_years,
        gender=gender,
        body_fat_pct=body_fat_pct,
        activity_level=activity_level,
        goal_type=goal_type,
        goal_weight_kg=goal_weight_kg,
        goal_timeline_months=goal_timeline_months,
    )
    report.weight_kg = weight_kg
    report.height_cm = height_cm
    report.age_years = age_years
    report.gender = gender
    report.body_fat_pct = body_fat_pct
    report.activity_level = activity_level
    report.goal_type = goal_type
    report.goal_weight_kg = goal_weight_kg
    report.goal_timeline_months = goal_timeline_months
    for key, val in computed.items():
        setattr(report, key, val)
    db.session.commit()
    return report


# ── Query reports ─────────────────────────────────────────────────


def list_reports(
    user_id: int,
    page: int = 1,
    per_page: int = 20,
) -> tuple[list[CalorieReport], int]:
    """List all calorie reports for a user, newest first."""
    query = CalorieReport.query.filter_by(user_id=user_id).order_by(CalorieReport.created_at.desc())
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    return items, total


def get_report(user_id: int, report_id: int) -> CalorieReport | None:
    """Get a single report by ID, scoped to user."""
    return CalorieReport.query.filter_by(id=report_id, user_id=user_id).first()


def get_latest_report(user_id: int) -> CalorieReport | None:
    """Get the most recent report for a user. Used by optimizer constraint bridge."""
    return CalorieReport.query.filter_by(user_id=user_id).order_by(CalorieReport.created_at.desc()).first()


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
        Biometric.query.filter_by(user_id=user_id).order_by(Biometric.date.desc(), Biometric.created_at.desc()).first()
    )
    if not bio:
        return None
    return {
        "weight_kg": float(bio.weight) if bio.weight else None,
        "body_fat_pct": float(bio.body_fat_pct) if bio.body_fat_pct else None,
    }
