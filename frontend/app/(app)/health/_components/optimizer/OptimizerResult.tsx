'use client'

import { useState } from 'react'
import { CheckCircle, TriangleAlert } from 'lucide-react'
import type { SolveResult, SolveOutput, ObjectiveMode, ConstraintSatisfaction } from '@/lib/optimizer/solveLP'
import type { HealthPageTranslations } from '@/lib/translations/app'

// ── Constraint display helpers ──────────────────────────────────────────────

function fmtNum(n: number): string {
  if (n >= 1000) return n.toLocaleString(undefined, { maximumFractionDigits: 0 })
  if (n >= 10)   return n.toLocaleString(undefined, { maximumFractionDigits: 1 })
  return n.toLocaleString(undefined, { maximumFractionDigits: 2 })
}

function fmtVal(n: number, cat: string): string {
  if (cat === 'cost')     return `$${fmtNum(n)}`
  if (cat === 'calories') return `${fmtNum(n)} kcal`
  return `${fmtNum(n)}g`
}

function opLabel(op: string): string {
  return op === '>=' ? '≥' : op === '<=' ? '≤' : '='
}

interface StatusInfo { text: string; color: string; iconColor: string; isOk: boolean }

function getStatus(cs: ConstraintSatisfaction, strict: boolean, t: HealthPageTranslations): StatusInfo {
  const { constraint: c, lhsValue, slack, tight } = cs
  const rhs = c.value
  const tolerancePct = rhs > 0 ? (slack / rhs) * 100 : 0
  const withinTolerance = tolerancePct <= 2
  const amt = fmtVal(slack, c.category)
  const actual = fmtVal(lhsValue, c.category)

  // ── equality target ────────────────────────────────────────────────────
  if (c.operator === '=') {
    if (tight)
      return { text: `${actual} — ${t.cOnTarget}`, color: '#4b6646', iconColor: '#4b6646', isOk: true }
    if (!strict && withinTolerance)
      return { text: `${actual} — ${amt} ${t.cOff} (${t.cWithin2})`, color: '#6b5a35', iconColor: '#6b5a35', isOk: true }
    const dir = lhsValue > rhs ? t.cAboveTarget : t.cBelowTarget
    return { text: `${actual} — ${amt} ${dir}`, color: '#8b4a3a', iconColor: '#e8735c', isOk: false }
  }

  // ── minimum (≥) ────────────────────────────────────────────────────────
  if (c.operator === '>=') {
    if (lhsValue >= rhs) {
      if (tight)
        return { text: `${actual} — ${t.cMinJustMet}`, color: '#4b6646', iconColor: '#4b6646', isOk: true }
      return { text: `${actual} — +${amt} ${t.cAboveMin}`, color: '#5a6157', iconColor: '#4b6646', isOk: true }
    }
    if (!strict && withinTolerance)
      return { text: `${actual} — ${amt} ${t.cShortWithin2}`, color: '#6b5a35', iconColor: '#6b5a35', isOk: true }
    return { text: `${actual} — ${amt} ${t.cBelowMin}`, color: '#8b4a3a', iconColor: '#e8735c', isOk: false }
  }

  // ── maximum (≤) ────────────────────────────────────────────────────────
  if (lhsValue <= rhs) {
    if (tight)
      return { text: `${actual} — ${t.cAtLimit}`, color: '#6b5a35', iconColor: '#4b6646', isOk: true }
    return { text: `${actual} — ${amt} ${t.cUnderLimit}`, color: '#5a6157', iconColor: '#4b6646', isOk: true }
  }
  if (!strict && withinTolerance)
    return { text: `${actual} — ${amt} ${t.cOverWithin2}`, color: '#6b5a35', iconColor: '#6b5a35', isOk: true }
  return { text: `${actual} — ${amt} ${t.cOverLimit}`, color: '#8b4a3a', iconColor: '#e8735c', isOk: false }
}

interface Props {
  t: HealthPageTranslations
  result: SolveOutput | null
  error: string | null
  objectiveMode: ObjectiveMode | null
  onAdjustConstraints?: () => void
}

const MICRO: React.CSSProperties = {
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.6875rem',
  fontWeight: 700,
  letterSpacing: '0.05em',
  textTransform: 'uppercase' as const,
}

function objLabel(mode: ObjectiveMode | null, t: HealthPageTranslations) {
  if (!mode) return ''
  if (mode === 'min_cost') return t.minimizeCost
  if (mode === 'max_cost') return t.maximizeCost
  if (mode === 'min_calories') return t.minimizeCalories
  if (mode === 'max_calories') return t.maximizeCalories
  if (mode === 'target_cost') return t.targetCost
  return t.targetCalories
}

function formatObjValue(mode: ObjectiveMode | null, val: number) {
  if (!mode) return ''
  if (mode.includes('cost')) return `$${val.toFixed(2)}`
  return `${val.toFixed(0)} kcal`
}

export function OptimizerResult({ t, result, error, objectiveMode, onAdjustConstraints }: Props) {
  const [strict, setStrict] = useState(false)

  if (!result && !error) return null

  // Error state
  if (!result || !result.feasible) {
    return (
      <div
        style={{
          background: '#fdf0ed',
          borderRadius: '0 16px 16px 16px',
          padding: 32,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, marginBottom: 12 }}>
          <TriangleAlert size={18} color="#8b4a3a" style={{ flexShrink: 0, marginTop: 2 }} />
          <span style={{ ...MICRO, color: '#8b4a3a' }}>{t.noSolutionFound}</span>
        </div>
        <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', color: '#2e342b', marginBottom: 16, lineHeight: 1.6 }}>
          {t.noSolution}
        </p>
        {onAdjustConstraints && (
          <button
            type="button"
            onClick={onAdjustConstraints}
            style={{
              padding: '8px 20px',
              borderRadius: 100,
              border: 'none',
              background: '#f1f5eb',
              fontFamily: 'Manrope, sans-serif',
              fontSize: '0.8125rem',
              fontWeight: 600,
              color: '#2e342b',
              cursor: 'pointer',
            }}
          >
            {t.adjustConstraints}
          </button>
        )}
      </div>
    )
  }

  // Unbounded
  if (result.feasible && !result.bounded) {
    return (
      <div
        style={{
          background: '#fdf0ed',
          borderRadius: '0 16px 16px 16px',
          padding: 32,
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: 10, marginBottom: 12 }}>
          <TriangleAlert size={18} color="#8b4a3a" style={{ flexShrink: 0, marginTop: 2 }} />
          <span style={{ ...MICRO, color: '#8b4a3a' }}>{t.unboundedTitle}</span>
        </div>
        <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', color: '#2e342b', lineHeight: 1.6 }}>
          {t.unboundedSolution}
        </p>
      </div>
    )
  }

  const r = result as SolveResult

  const COLS = '2fr 100px 70px 70px 80px 70px 60px 70px'

  return (
    <div
      style={{
        background: '#ffffff',
        borderRadius: '0 16px 16px 16px',
        padding: 32,
      }}
    >
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
        <CheckCircle size={15} color="#4b6646" />
        <span style={{ ...MICRO, color: '#4b6646' }}>{t.optimalSolution}</span>
      </div>
      <p
        style={{
          fontFamily: 'Newsreader, Georgia, serif',
          fontSize: '1.125rem',
          fontWeight: 400,
          color: '#4b6646',
          marginBottom: 4,
        }}
      >
        {t.optimalCombination}
      </p>

      {/* Objective value */}
      <p
        style={{
          fontFamily: 'Newsreader, Georgia, serif',
          fontSize: '1.25rem',
          color: '#2e342b',
          marginBottom: 24,
        }}
      >
        {objLabel(objectiveMode, t)} = {formatObjValue(objectiveMode, r.objectiveValue)}
      </p>

      {/* Results table (CSS grid) */}
      <div style={{ overflowX: 'auto' }}>
        {/* Header row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: COLS,
            gap: 4,
            ...MICRO,
            color: '#5a6157',
            paddingBottom: 8,
            borderBottom: '1px solid #e8ece4',
            minWidth: 660,
          }}
        >
          <span>{t.food}</span>
          <span style={{ textAlign: 'right' }}>{t.qtyGrams}</span>
          <span style={{ textAlign: 'right' }}>{t.cost}</span>
          <span style={{ textAlign: 'right' }}>{t.colKcal}</span>
          <span style={{ textAlign: 'right' }}>{t.protein}</span>
          <span style={{ textAlign: 'right' }}>{t.carbs}</span>
          <span style={{ textAlign: 'right' }}>{t.fat}</span>
          <span style={{ textAlign: 'right' }}>{t.fiber}</span>
        </div>

        {/* Food rows */}
        {r.quantities.map((item, i) => (
          <div
            key={item.food.id}
            style={{
              display: 'grid',
              gridTemplateColumns: COLS,
              gap: 4,
              padding: '8px 0',
              background: i % 2 === 0 ? '#f8faf2' : '#ffffff',
              fontFamily: 'Manrope, sans-serif',
              fontSize: '0.875rem',
              fontWeight: 600,
              color: '#2e342b',
              borderBottom: '1px solid #f0f2ec',
              minWidth: 660,
            }}
          >
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
              {item.food.name}
            </span>
            <span style={{ textAlign: 'right' }}>{item.quantityGrams}g</span>
            <span style={{ textAlign: 'right' }}>${item.cost.toFixed(2)}</span>
            <span style={{ textAlign: 'right' }}>{item.calories}</span>
            <span style={{ textAlign: 'right' }}>{item.protein}g</span>
            <span style={{ textAlign: 'right' }}>{item.carbohydrate}g</span>
            <span style={{ textAlign: 'right' }}>{item.fat}g</span>
            <span style={{ textAlign: 'right' }}>{item.fiber != null ? `${item.fiber}g` : '—'}</span>
          </div>
        ))}

        {/* Totals row */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: COLS,
            gap: 4,
            padding: '10px 0',
            background: '#fdf0ed',
            fontFamily: 'Manrope, sans-serif',
            fontSize: '0.875rem',
            fontWeight: 700,
            color: '#2e342b',
            minWidth: 660,
          }}
        >
          <span style={{ ...MICRO, color: '#8b4a3a', alignSelf: 'center' }}>{t.total}</span>
          <span />
          <span style={{ textAlign: 'right' }}>${r.totals.cost.toFixed(2)}</span>
          <span style={{ textAlign: 'right' }}>{r.totals.calories}</span>
          <span style={{ textAlign: 'right' }}>{r.totals.protein}g</span>
          <span style={{ textAlign: 'right' }}>{r.totals.carbohydrate}g</span>
          <span style={{ textAlign: 'right' }}>{r.totals.fat}g</span>
          <span style={{ textAlign: 'right' }}>{r.totals.fiber}g</span>
        </div>
      </div>

      {/* Constraint satisfaction */}
      {r.constraintSatisfaction.length > 0 && (
        <div style={{ marginTop: 24 }}>
          {/* Header + tolerance toggle */}
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
            <p style={{ ...MICRO, color: '#5a6157', margin: 0 }}>{t.constraints}</p>
            <div style={{ display: 'flex', background: '#f1f5eb', borderRadius: 100, padding: 2, gap: 2 }}>
              {(['strict', 'tolerant'] as const).map((mode) => {
                const active = mode === 'strict' ? strict : !strict
                return (
                  <button
                    key={mode}
                    type="button"
                    onClick={() => setStrict(mode === 'strict')}
                    style={{
                      padding: '3px 12px',
                      borderRadius: 100,
                      border: 'none',
                      background: active ? '#ffffff' : 'transparent',
                      boxShadow: active ? '0 1px 3px rgba(46,52,43,0.1)' : 'none',
                      fontFamily: 'Manrope, sans-serif',
                      fontSize: '0.6875rem',
                      fontWeight: active ? 700 : 500,
                      color: active ? '#2e342b' : '#767d72',
                      cursor: 'pointer',
                      transition: 'all 0.15s',
                      whiteSpace: 'nowrap',
                    }}
                  >
                    {mode === 'strict' ? t.cStrict : t.cTolerance}
                  </button>
                )
              })}
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
            {r.constraintSatisfaction.map((cs) => {
              const status = getStatus(cs, strict, t)
              const CAT_LABELS: Record<string, string> = {
                calories: t.cCalories, protein: t.protein, carbohydrate: t.carbs,
                fat: t.fat, fiber: t.fiber, cost: t.budget,
              }
              const catLbl = CAT_LABELS[cs.constraint.category] ?? cs.constraint.category
              return (
                <div
                  key={cs.constraint.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 10,
                    padding: '8px 12px',
                    background: status.isOk ? '#f8faf2' : '#fdf5f3',
                    borderRadius: '0 8px 8px 8px',
                    flexWrap: 'wrap',
                  }}
                >
                  {status.isOk
                    ? <CheckCircle size={14} color={status.iconColor} style={{ flexShrink: 0 }} />
                    : <TriangleAlert size={14} color={status.iconColor} style={{ flexShrink: 0 }} />
                  }
                  <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#2e342b', flex: 1, minWidth: 120 }}>
                    {catLbl} {opLabel(cs.constraint.operator)} {fmtVal(cs.constraint.value, cs.constraint.category)}
                  </span>
                  <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.75rem', color: status.color, fontWeight: cs.tight ? 600 : 400 }}>
                    {status.text}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
