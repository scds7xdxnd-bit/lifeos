'use client'

import { useState, useEffect, useRef } from 'react'
import { ChevronDown, Trash2 } from 'lucide-react'
import type { Constraint, ConstraintOp, ObjectiveMode } from '@/lib/optimizer/solveLP'
import type { HealthPageTranslations } from '@/lib/translations/app'

interface Props {
  t: HealthPageTranslations
  constraints: Constraint[]
  onChange: (constraints: Constraint[]) => void
  objectiveMode: ObjectiveMode | null
  latestReportExists?: boolean
  onSwitchToCalculator?: () => void
}

type Category = Constraint['category']

const SELECT: React.CSSProperties = {
  padding: '4px 6px',
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.8rem',
  fontWeight: 500,
  color: '#2e342b',
  background: 'transparent',
  border: 'none',
  borderBottom: '1.5px solid rgba(75,102,70,0.25)',
  borderRadius: 0,
  outline: 'none',
  cursor: 'pointer',
  appearance: 'none' as const,
  WebkitAppearance: 'none' as const,
}

const NUM_INPUT: React.CSSProperties = {
  width: 90,
  padding: '4px 6px',
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.8rem',
  color: '#2e342b',
  background: 'transparent',
  border: 'none',
  borderBottom: '1.5px solid rgba(75,102,70,0.25)',
  borderRadius: 0,
  outline: 'none',
}

export function ConstraintBuilder({ t, constraints, onChange, objectiveMode, latestReportExists, onSwitchToCalculator }: Props) {
  const [expanded, setExpanded] = useState(false)
  // Auto-expand when constraints are first populated (e.g. from calculator auto-fill)
  const prevLengthRef = useRef(constraints.length)
  useEffect(() => {
    if (prevLengthRef.current === 0 && constraints.length > 0) {
      setExpanded(true)
    }
    prevLengthRef.current = constraints.length
  }, [constraints.length])
  const [category, setCategory] = useState<Category>('protein')
  const [operator, setOperator] = useState<ConstraintOp>('>=')
  const [value, setValue] = useState('')

  const showCost = objectiveMode === 'min_calories' || objectiveMode === 'max_calories' || objectiveMode === 'target_calories'

  const CATEGORIES: { value: Category; label: string }[] = [
    { value: 'calories', label: t.catCalories },
    { value: 'protein', label: t.catProtein },
    { value: 'carbohydrate', label: t.catCarbs },
    { value: 'fat', label: t.catFat },
    { value: 'fiber', label: t.catFiber },
    ...(showCost ? [{ value: 'cost' as Category, label: t.catBudget }] : []),
  ]

  function addConstraint() {
    const num = parseFloat(value)
    if (isNaN(num)) return
    onChange([...constraints, { id: `${Date.now()}`, category, operator, value: num, source: 'user' }])
    setValue('')
  }

  function updateConstraintValue(id: string, newVal: number) {
    onChange(constraints.map(c => c.id === id ? { ...c, value: newVal, source: 'user' } : c))
  }

  function updateConstraintOperator(id: string, op: ConstraintOp) {
    onChange(constraints.map(c => c.id === id ? { ...c, operator: op, source: 'user' } : c))
  }

  function remove(id: string) {
    onChange(constraints.filter((c) => c.id !== id))
  }

  return (
    <div>
      {/* Collapsible header */}
      <button
        type="button"
        onClick={() => setExpanded((v) => !v)}
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          width: '100%',
          background: 'none',
          border: 'none',
          cursor: 'pointer',
          padding: 0,
          marginBottom: expanded ? 14 : 0,
        }}
      >
        <span
          style={{
            fontFamily: 'Manrope, sans-serif',
            fontSize: '0.6875rem',
            fontWeight: 700,
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
            color: '#8b4a3a',
          }}
        >
          {t.constraints} {constraints.length > 0 ? `(${constraints.length})` : ''}
        </span>
        <ChevronDown
          size={14}
          color="#8b4a3a"
          style={{ transform: expanded ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }}
        />
      </button>

      {expanded && (
        <>
          {/* Empty state prompt when no constraints and no latest report */}
          {constraints.length === 0 && !latestReportExists && onSwitchToCalculator && (
            <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#767d72', marginBottom: '12px', lineHeight: 1.5 }}>
              {t.calcPrompt.replace('Calculator tab', '')}
              <button type="button" onClick={onSwitchToCalculator} style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#4b6646', fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', fontWeight: 600, padding: 0, textDecoration: 'underline' }}>
                Calculator
              </button>
              {' '}tab to get personalized suggestions here.
            </p>
          )}

          {/* Existing constraints */}
          {constraints.length > 0 && (
            <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginBottom: 10 }}>
              {constraints.map((c) => (
                <div
                  key={c.id}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 6,
                    padding: '4px 8px',
                    background: '#f8faf2',
                    borderRadius: '0 8px 8px 8px',
                  }}
                >
                  <select
                    value={c.category}
                    onChange={e => onChange(constraints.map(x => x.id === c.id ? { ...x, category: e.target.value as Category, source: 'user' } : x))}
                    style={{ ...SELECT, fontSize: '0.75rem', flex: '0 0 auto' }}
                  >
                    {CATEGORIES.map(cat => <option key={cat.value} value={cat.value}>{cat.label}</option>)}
                  </select>
                  <select
                    value={c.operator}
                    onChange={e => updateConstraintOperator(c.id, e.target.value as ConstraintOp)}
                    style={{ ...SELECT, fontSize: '0.75rem', flexShrink: 0 }}
                  >
                    <option value=">=">&ge;</option>
                    <option value="<=">&le;</option>
                    <option value="=">=</option>
                  </select>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={c.value}
                    onChange={e => updateConstraintValue(c.id, parseFloat(e.target.value) || 0)}
                    style={{ ...NUM_INPUT, width: 76, padding: '4px 6px', fontSize: '0.75rem', flexShrink: 0 }}
                  />
                  {c.source === 'calculator' && (
                    <span style={{ borderRadius: '100px', background: '#fdf0ed', color: '#8b4a3a', fontFamily: 'Manrope, sans-serif', fontSize: '0.6rem', fontWeight: 500, padding: '2px 6px', whiteSpace: 'nowrap', flexShrink: 0 }}>
                      {t.fromCalculator}
                    </span>
                  )}
                  <button
                    type="button"
                    onClick={() => remove(c.id)}
                    aria-label="Remove constraint"
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      color: '#adb4a8',
                      padding: '4px 6px',
                      display: 'flex',
                      alignItems: 'center',
                      marginLeft: 'auto',
                      flexShrink: 0,
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.color = '#e8735c')}
                    onMouseLeave={(e) => (e.currentTarget.style.color = '#adb4a8')}
                  >
                    <Trash2 size={12} />
                  </button>
                </div>
              ))}
            </div>
          )}

          {/* Add new row */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap' }}>
            <select value={category} onChange={(e) => setCategory(e.target.value as Category)} style={SELECT}>
              {CATEGORIES.map((c) => <option key={c.value} value={c.value}>{c.label}</option>)}
            </select>

            <select value={operator} onChange={(e) => setOperator(e.target.value as ConstraintOp)} style={SELECT}>
              <option value=">=">&ge;</option>
              <option value="<=">&le;</option>
              <option value="=">=</option>
            </select>

            <input
              type="number"
              min="0"
              step="0.1"
              value={value}
              onChange={(e) => setValue(e.target.value)}
              placeholder="0"
              style={NUM_INPUT}
              onKeyDown={(e) => e.key === 'Enter' && (e.preventDefault(), addConstraint())}
            />

            <button
              type="button"
              onClick={addConstraint}
              style={{
                padding: '7px 16px',
                borderRadius: 100,
                border: 'none',
                background: '#f1f5eb',
                fontFamily: 'Manrope, sans-serif',
                fontSize: '0.78rem',
                fontWeight: 600,
                color: '#2e342b',
                cursor: 'pointer',
                minHeight: 36,
              }}
            >
              + {t.addConstraint}
            </button>
          </div>
        </>
      )}
    </div>
  )
}
