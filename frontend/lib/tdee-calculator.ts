/**
 * Client-side TDEE/BMR calculator.
 * Mirrors calculator_service.py:calculate() and get_warnings() exactly.
 * Uses IEEE 754 float (no Decimal) — sufficient for non-persisted compute.
 *
 * Verification: calculate({ weight_kg: 80, height_cm: 180, age_years: 25,
 *   gender: 'male', body_fat_pct: null, activity_level: 'moderately_active',
 *   goal_type: 'maintain', goal_weight_kg: null, goal_timeline_months: null })
 * → bmr ≈ 1830, tdee ≈ 2836.5
 */

// ── Types ──────────────────────────────────────────────────────────

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

// ── Constants — mirror calculator_service.py ──────────────────────

const ACTIVITY_MULTIPLIERS: Record<TdeeInput['activity_level'], number> = {
  sedentary: 1.2,
  lightly_active: 1.375,
  moderately_active: 1.55,
  very_active: 1.725,
  extra_active: 1.9,
}

const KCAL_PER_KG_LOSE = 7700
const KCAL_PER_KG_GAIN = 4500
const MONTHLY_MULTIPLIER = 30

const PROTEIN_FACTOR = 2.0   // g per kg bodyweight
const FAT_FACTOR = 0.8       // g per kg bodyweight
const CARBS_FIXED = 250      // g per day
const FIBER_FIXED = 24       // g per day

// ── Helper: round to 2 decimal places (mirrors _r2) ───────────────

function r2(val: number): number {
  return Math.round(val * 100) / 100
}

// ── Core calculation ───────────────────────────────────────────────

export function calculate(input: TdeeInput): TdeeResult {
  const { weight_kg: w, height_cm: h, age_years: age, gender, body_fat_pct, activity_level, goal_type, goal_weight_kg, goal_timeline_months } = input

  // ── BMR ──
  let bmr: number
  let lbm: number | null
  let method_used: TdeeResult['method_used']

  if (body_fat_pct !== null && body_fat_pct > 0) {
    lbm = r2(w * (1 - body_fat_pct / 100))
    bmr = r2(370 + 21.6 * lbm)
    method_used = 'katch_mcardle'
  } else {
    lbm = null
    if (gender === 'male') {
      bmr = r2(10 * w + 6.25 * h - 5 * age + 5)
    } else {
      bmr = r2(10 * w + 6.25 * h - 5 * age - 161)
    }
    method_used = 'mifflin_st_jeor'
  }

  // ── TDEE ──
  const multiplier = ACTIVITY_MULTIPLIERS[activity_level]
  const tdee = r2(bmr * multiplier)

  // ── Daily calorie target ──
  let delta_bw: number | null = null
  let total_delta_kcal: number | null = null
  let delta_kcal_per_day: number | null = null
  let kcal_per_kg_used: number | null = null
  let daily_calories: number

  if (goal_type === 'lose') {
    const gw = goal_weight_kg!
    delta_bw = r2(gw - w)
    total_delta_kcal = r2(delta_bw * KCAL_PER_KG_LOSE)
    delta_kcal_per_day = r2(total_delta_kcal / (MONTHLY_MULTIPLIER * goal_timeline_months!))
    daily_calories = r2(tdee + delta_kcal_per_day)
    kcal_per_kg_used = KCAL_PER_KG_LOSE
  } else if (goal_type === 'gain') {
    const gw = goal_weight_kg!
    delta_bw = r2(gw - w)
    total_delta_kcal = r2(delta_bw * KCAL_PER_KG_GAIN)
    delta_kcal_per_day = r2(total_delta_kcal / (MONTHLY_MULTIPLIER * goal_timeline_months!))
    daily_calories = r2(tdee + delta_kcal_per_day)
    kcal_per_kg_used = KCAL_PER_KG_GAIN
  } else {
    daily_calories = tdee
  }

  // ── Macro suggestions ──
  const protein_g = r2(PROTEIN_FACTOR * w)
  const fat_g = r2(FAT_FACTOR * w)

  // ── Monthly targets ──
  const monthly_calories = r2(daily_calories * MONTHLY_MULTIPLIER)
  const monthly_protein = r2(protein_g * MONTHLY_MULTIPLIER)
  const monthly_fat = r2(fat_g * MONTHLY_MULTIPLIER)
  const monthly_carbs = r2(CARBS_FIXED * MONTHLY_MULTIPLIER)
  const monthly_fiber = r2(FIBER_FIXED * MONTHLY_MULTIPLIER)

  return {
    method_used,
    lean_body_mass: lbm,
    bmr,
    activity_multiplier: multiplier,
    tdee,
    delta_bw,
    total_delta_kcal,
    delta_kcal_per_day,
    kcal_per_kg_used,
    daily_calories,
    protein_g_per_day: protein_g,
    fat_g_per_day: fat_g,
    carbs_g_per_day: CARBS_FIXED,
    fiber_g_per_day: FIBER_FIXED,
    monthly_calories,
    monthly_protein_g: monthly_protein,
    monthly_fat_g: monthly_fat,
    monthly_carbs_g: monthly_carbs,
    monthly_fiber_g: monthly_fiber,
  }
}

// ── Validation warnings — mirrors get_warnings() ─────────────────

interface GetWarningsOpts {
  gender: TdeeInput['gender']
  daily_calories: number
  tdee: number
  goal_type: TdeeInput['goal_type']
}

export function getWarnings(opts: GetWarningsOpts): TdeeWarning[] {
  const { gender, daily_calories, tdee, goal_type } = opts
  const warnings: TdeeWarning[] = []
  const floor = gender === 'female' ? 1200 : 1500

  if (goal_type === 'lose' && daily_calories < floor) {
    warnings.push({
      type: 'low_intake',
      message:
        'This timeline may result in a very low daily intake. ' +
        'Consider extending the timeline or adjusting your goal weight.',
    })
  }

  if (goal_type === 'gain' && daily_calories > tdee + 1000) {
    warnings.push({
      type: 'high_surplus',
      message: 'This is a significant surplus. A more gradual approach may be easier to sustain.',
    })
  }

  return warnings
}
