'use client'

import type { ObjectiveMode } from '@/lib/optimizer/solveLP'
import type { HealthPageTranslations } from '@/lib/translations/app'

interface Props {
  t: HealthPageTranslations
  value: ObjectiveMode | null
  targetValue: number
  onChange: (mode: ObjectiveMode) => void
  onTargetChange: (value: number) => void
}

const OPTIONS: { value: ObjectiveMode; label: (t: HealthPageTranslations) => string }[] = [
  { value: 'min_cost',       label: (t) => t.minimizeCost },
  { value: 'max_cost',       label: (t) => t.maximizeCost },
  { value: 'target_cost',    label: (t) => t.targetCost },
  { value: 'min_calories',   label: (t) => t.minimizeCalories },
  { value: 'max_calories',   label: (t) => t.maximizeCalories },
  { value: 'target_calories', label: (t) => t.targetCalories },
]

export function ObjectiveSelector({ t, value, targetValue, onChange, onTargetChange }: Props) {
  const isTarget = value === 'target_cost' || value === 'target_calories'

  return (
    <div>
      <p
        style={{
          fontFamily: 'Manrope, sans-serif',
          fontSize: '0.6875rem',
          fontWeight: 700,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: '#8b4a3a',
          marginBottom: 12,
        }}
      >
        {t.objective}
      </p>

      {/* 3×2 pill grid */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(3, 1fr)',
          gap: 6,
        }}
      >
        {OPTIONS.map((opt) => {
          const isActive = value === opt.value
          return (
            <button
              key={opt.value}
              type="button"
              onClick={() => onChange(opt.value)}
              style={{
                padding: '8px 10px',
                borderRadius: 100,
                border: 'none',
                background: isActive ? '#fce8e4' : '#f1f5eb',
                fontFamily: 'Manrope, sans-serif',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: isActive ? '#8b4a3a' : '#5a6157',
                cursor: 'pointer',
                transition: 'background 0.15s, color 0.15s',
                textAlign: 'center',
                whiteSpace: 'nowrap',
                overflow: 'hidden',
                textOverflow: 'ellipsis',
                minHeight: 36,
              }}
            >
              {opt.label(t)}
            </button>
          )
        })}
      </div>

      {/* Target value input */}
      {isTarget && (
        <div style={{ marginTop: 14 }}>
          <label
            style={{
              fontFamily: 'Manrope, sans-serif',
              fontSize: '0.6875rem',
              fontWeight: 700,
              letterSpacing: '0.05em',
              textTransform: 'uppercase',
              color: '#5a6157',
              display: 'block',
              marginBottom: 5,
            }}
          >
            {t.targetValue}
          </label>
          <input
            type="number"
            min="0"
            step="0.01"
            value={targetValue}
            onChange={(e) => onTargetChange(parseFloat(e.target.value) || 0)}
            placeholder="0"
            style={{
              width: '100%',
              padding: '9px 12px',
              fontFamily: 'Manrope, sans-serif',
              fontSize: '0.875rem',
              color: '#2e342b',
              background: '#f7f8f5',
              border: '1.5px solid rgba(173,180,168,0.4)',
              borderRadius: 4,
              outline: 'none',
              boxSizing: 'border-box',
            }}
          />
        </div>
      )}
    </div>
  )
}
