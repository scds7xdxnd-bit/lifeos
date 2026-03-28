'use client'

import { useState } from 'react'
import { ChevronDown } from 'lucide-react'
import type { FoodItem } from '@/lib/api/foodLibrary'
import type { FoodBounds } from '@/lib/optimizer/solveLP'
import type { HealthPageTranslations } from '@/lib/translations/app'

interface Props {
  t: HealthPageTranslations
  selectedFoods: FoodItem[]
  bounds: FoodBounds
  onChange: (bounds: FoodBounds) => void
}

const INPUT: React.CSSProperties = {
  width: 80,
  padding: '6px 8px',
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.8rem',
  color: '#2e342b',
  background: '#ffffff',
  border: '1px solid rgba(173,180,168,0.4)',
  borderRadius: 4,
  outline: 'none',
}


export function FoodBoundsEditor({ t, selectedFoods, bounds, onChange }: Props) {
  const [expanded, setExpanded] = useState(false)

  if (selectedFoods.length === 0) return null

  function update(foodId: number, key: 'min' | 'max', raw: string) {
    // Store in units of 100g (solver units); user inputs actual grams
    const val = raw === '' ? undefined : Math.max(0, (parseFloat(raw) || 0) / 100)
    const current = bounds[foodId] ?? {}
    onChange({ ...bounds, [foodId]: { ...current, [key]: val } })
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
          {t.foodBounds} ({t.optional})
        </span>
        <ChevronDown
          size={14}
          color="#8b4a3a"
          style={{ transform: expanded ? 'rotate(180deg)' : '', transition: 'transform 0.2s' }}
        />
      </button>

      {expanded && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
          {/* Column headers */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 90px 90px',
              gap: 8,
              fontFamily: 'Manrope, sans-serif',
              fontSize: '0.65rem',
              fontWeight: 700,
              letterSpacing: '0.04em',
              textTransform: 'uppercase',
              color: '#767d72',
            }}
          >
            <span>{t.food}</span>
            <span style={{ textAlign: 'center' }}>{t.minBound}</span>
            <span style={{ textAlign: 'center' }}>{t.maxBound}</span>
          </div>

          {selectedFoods.map((food) => {
            const b = bounds[food.id] ?? {}
            return (
              <div
                key={food.id}
                style={{ display: 'grid', gridTemplateColumns: '1fr 90px 90px', gap: 8, alignItems: 'start' }}
              >
                <span
                  style={{
                    fontFamily: 'Manrope, sans-serif',
                    fontSize: '0.82rem',
                    color: '#2e342b',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                    paddingTop: 8,
                  }}
                >
                  {food.name}
                </span>
                <div>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={b.min != null ? +(b.min * 100).toFixed(2) : ''}
                    onChange={(e) => update(food.id, 'min', e.target.value)}
                    placeholder="—"
                    style={INPUT}
                  />
                </div>
                <div>
                  <input
                    type="number"
                    min="0"
                    step="1"
                    value={b.max != null ? +(b.max * 100).toFixed(2) : ''}
                    onChange={(e) => update(food.id, 'max', e.target.value)}
                    placeholder="—"
                    style={INPUT}
                  />
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}
