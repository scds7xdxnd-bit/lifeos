import type { FoodItem } from '@/lib/api/foodLibrary'
import solver from 'javascript-lp-solver'

/** Six objective modes per spec §2 */
export type ObjectiveMode =
  | 'min_cost'
  | 'max_cost'
  | 'min_calories'
  | 'max_calories'
  | 'target_cost'
  | 'target_calories'

export type ConstraintOp = '>=' | '<=' | '='

export interface Constraint {
  id: string
  category: 'calories' | 'protein' | 'carbohydrate' | 'fat' | 'fiber' | 'cost'
  operator: ConstraintOp
  value: number
  source?: 'calculator' | 'user'
}

/** Bounds are in units of 100g (the solver variable unit) */
export type FoodBounds = Record<number, { min?: number; max?: number }>

export interface SolveInput {
  foods: FoodItem[]
  objective: ObjectiveMode
  targetValue: number        // used only for target_cost / target_calories modes
  constraints: Constraint[]
  bounds: FoodBounds
}

export interface SolveResultItem {
  food: FoodItem
  quantity100g: number       // raw solver value
  quantityGrams: number      // × 100 for display
  cost: number
  calories: number
  protein: number
  carbohydrate: number
  fat: number
  fiber: number | null
}

export interface SolveTotals {
  cost: number
  calories: number
  protein: number
  carbohydrate: number
  fat: number
  fiber: number
}

export interface ConstraintSatisfaction {
  constraint: Constraint
  lhsValue: number
  satisfied: boolean
  slack: number
  tight: boolean
}

export interface SolveResult {
  feasible: true
  bounded: true
  objectiveValue: number
  quantities: SolveResultItem[]
  totals: SolveTotals
  constraintSatisfaction: ConstraintSatisfaction[]
}

export type SolveOutput =
  | SolveResult
  | { feasible: false }
  | { feasible: true; bounded: false }

/**
 * Solve the food optimizer LP.
 *
 * Variables: X_i = quantity of food i in units of 100g (continuous, ≥ 0)
 * Field names in the solver model are prefixed with `_` to avoid conflicts
 * with solver reserved words.
 */
export function solveLP(input: SolveInput): SolveOutput {
  const { foods, objective, targetValue, constraints, bounds } = input
  if (foods.length === 0) return { feasible: false }

  // ---------- Build variables ----------
  const variables: Record<string, Record<string, number>> = {}

  for (const food of foods) {
    const key = `f${food.id}`
    variables[key] = {
      _cost: Number(food.cost_per_100g),
      _calories: Number(food.calories_per_100g),
      _protein: Number(food.protein_per_100g),
      _carbohydrate: Number(food.carbohydrate_per_100g),
      _fat: Number(food.fat_per_100g),
      _fiber: food.fiber_per_100g != null ? Number(food.fiber_per_100g) : 0,
      _dummy: 0, // for target modes
    }
  }

  // ---------- Per-food bounds as individual constraints ----------
  const lpConstraints: Record<string, { min?: number; max?: number; equal?: number }> = {}

  for (const food of foods) {
    const b = bounds[food.id]

    // Each bound direction needs its own uniquely-named attribute so the
    // constraint key matches the variable attribute key (LP solver requirement).
    if (b?.min != null && b.min > 0) {
      const minAttr = `_bmin${food.id}`
      for (const other of foods) {
        variables[`f${other.id}`][minAttr] = other.id === food.id ? 1 : 0
      }
      lpConstraints[minAttr] = { min: b.min }
    }

    if (b?.max != null) {
      const maxAttr = `_bmax${food.id}`
      for (const other of foods) {
        variables[`f${other.id}`][maxAttr] = other.id === food.id ? 1 : 0
      }
      lpConstraints[maxAttr] = { max: b.max }
    }
  }

  // ---------- User constraints ----------
  for (const c of constraints) {
    const attrMap: Record<string, string> = {
      calories: '_calories',
      protein: '_protein',
      carbohydrate: '_carbohydrate',
      fat: '_fat',
      fiber: '_fiber',
      cost: '_cost',
    }
    const attr = attrMap[c.category]
    const key = `uc_${c.id}`

    // Add constraint-specific attribute to each food variable
    for (const food of foods) {
      variables[`f${food.id}`][key] = variables[`f${food.id}`][attr] ?? 0
    }

    if (c.operator === '<=') lpConstraints[key] = { max: c.value }
    else if (c.operator === '>=') lpConstraints[key] = { min: c.value }
    else lpConstraints[key] = { equal: c.value }
  }

  // ---------- Objective ----------
  let optimizeAttr: string
  let opType: 'min' | 'max'

  if (objective === 'min_cost') { optimizeAttr = '_cost'; opType = 'min' }
  else if (objective === 'max_cost') { optimizeAttr = '_cost'; opType = 'max' }
  else if (objective === 'min_calories') { optimizeAttr = '_calories'; opType = 'min' }
  else if (objective === 'max_calories') { optimizeAttr = '_calories'; opType = 'max' }
  else if (objective === 'target_cost') {
    // Pin cost as equality, minimize dummy (find any feasible solution)
    optimizeAttr = '_dummy'; opType = 'min'
    const key = `target_cost`
    for (const food of foods) variables[`f${food.id}`][key] = variables[`f${food.id}`]['_cost']
    lpConstraints[key] = { equal: targetValue }
  } else {
    // target_calories
    optimizeAttr = '_dummy'; opType = 'min'
    const key = `target_calories`
    for (const food of foods) variables[`f${food.id}`][key] = variables[`f${food.id}`]['_calories']
    lpConstraints[key] = { equal: targetValue }
  }

  const model = {
    optimize: optimizeAttr,
    opType,
    constraints: lpConstraints,
    variables,
    ints: {},
    unrestricted: {},
  }

  // ---------- Solve ----------
  let raw: Record<string, number | boolean>
  try {
    raw = solver.Solve(model) as Record<string, number | boolean>
  } catch {
    return { feasible: false }
  }

  if (!raw.feasible) return { feasible: false }
  if (raw.bounded === false) return { feasible: true, bounded: false }

  // ---------- Extract quantities ----------
  const quantities: SolveResultItem[] = []
  for (const food of foods) {
    const units = (raw[`f${food.id}`] as number) ?? 0
    if (units < 1e-9) continue
    const grams = units * 100
    quantities.push({
      food,
      quantity100g: units,
      quantityGrams: Math.round(grams * 10) / 10,
      cost: Math.round(units * Number(food.cost_per_100g) * 100) / 100,
      calories: Math.round(units * Number(food.calories_per_100g) * 10) / 10,
      protein: Math.round(units * Number(food.protein_per_100g) * 10) / 10,
      carbohydrate: Math.round(units * Number(food.carbohydrate_per_100g) * 10) / 10,
      fat: Math.round(units * Number(food.fat_per_100g) * 10) / 10,
      fiber:
        food.fiber_per_100g != null
          ? Math.round(units * Number(food.fiber_per_100g) * 10) / 10
          : null,
    })
  }

  const totals: SolveTotals = quantities.reduce(
    (acc, it) => ({
      cost: acc.cost + it.cost,
      calories: acc.calories + it.calories,
      protein: acc.protein + it.protein,
      carbohydrate: acc.carbohydrate + it.carbohydrate,
      fat: acc.fat + it.fat,
      fiber: acc.fiber + (it.fiber ?? 0),
    }),
    { cost: 0, calories: 0, protein: 0, carbohydrate: 0, fat: 0, fiber: 0 }
  )

  // Round totals
  totals.cost = Math.round(totals.cost * 100) / 100
  totals.calories = Math.round(totals.calories * 10) / 10
  totals.protein = Math.round(totals.protein * 10) / 10
  totals.carbohydrate = Math.round(totals.carbohydrate * 10) / 10
  totals.fat = Math.round(totals.fat * 10) / 10
  totals.fiber = Math.round(totals.fiber * 10) / 10

  // ---------- Constraint satisfaction ----------
  const nutrientTotal: Record<string, number> = {
    calories: totals.calories,
    protein: totals.protein,
    carbohydrate: totals.carbohydrate,
    fat: totals.fat,
    fiber: totals.fiber,
    cost: totals.cost,
  }

  const constraintSatisfaction: ConstraintSatisfaction[] = constraints.map((c) => {
    const lhsValue = nutrientTotal[c.category] ?? 0
    const rhs = c.value
    let satisfied: boolean
    if (c.operator === '<=') satisfied = lhsValue <= rhs + 0.001
    else if (c.operator === '>=') satisfied = lhsValue >= rhs - 0.001
    else satisfied = Math.abs(lhsValue - rhs) < 0.01
    const slack = Math.abs(lhsValue - rhs)
    return {
      constraint: c,
      lhsValue: Math.round(lhsValue * 100) / 100,
      satisfied,
      slack: Math.round(slack * 100) / 100,
      tight: slack < 0.01,
    }
  })

  const objectiveValue = objective === 'min_cost' || objective === 'max_cost' || objective === 'target_cost'
    ? totals.cost
    : totals.calories

  return {
    feasible: true,
    bounded: true,
    objectiveValue,
    quantities,
    totals,
    constraintSatisfaction,
  }
}
