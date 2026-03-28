'use client'

import type { FoodItem } from '@/lib/api/foodLibrary'
import type { HealthPageTranslations } from '@/lib/translations/app'

interface Props {
  t: HealthPageTranslations
  foods: FoodItem[]
  selectedIds: Set<number>
  onToggle: (id: number) => void
  onSelectAll: () => void
  onDeselectAll: () => void
}

export function FoodSelector({ t, foods, selectedIds, onToggle, onSelectAll, onDeselectAll }: Props) {
  const allSelected = foods.length > 0 && selectedIds.size === foods.length

  return (
    <div>
      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
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
          {t.selectFoods}
        </span>
        <button
          type="button"
          onClick={allSelected ? onDeselectAll : onSelectAll}
          style={{
            background: 'none',
            border: 'none',
            fontFamily: 'Manrope, sans-serif',
            fontSize: '0.75rem',
            fontWeight: 600,
            color: '#5a6157',
            cursor: 'pointer',
            padding: '2px 4px',
          }}
          onMouseEnter={(e) => (e.currentTarget.style.color = '#4b6646')}
          onMouseLeave={(e) => (e.currentTarget.style.color = '#5a6157')}
        >
          {allSelected ? t.deselectAll : t.selectAll}
        </button>
      </div>

      {foods.length === 0 ? (
        <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', color: '#767d72' }}>
          {t.noFoodsInLibrary}
        </p>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 340, overflowY: 'auto' }}>
          {foods.map((food) => {
            const isSelected = selectedIds.has(food.id)
            return (
              <label
                key={food.id}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 10,
                  padding: '8px 10px',
                  borderRadius: '0 8px 8px 8px',
                  background: isSelected ? '#fdf0ed' : 'transparent',
                  cursor: 'pointer',
                  minHeight: 44,
                  transition: 'background 0.12s',
                }}
              >
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => onToggle(food.id)}
                  style={{ accentColor: '#4b6646', width: 18, height: 18, flexShrink: 0, cursor: 'pointer' }}
                />
                <span
                  style={{
                    fontFamily: 'Manrope, sans-serif',
                    fontSize: '0.875rem',
                    fontWeight: isSelected ? 600 : 400,
                    color: '#2e342b',
                    flex: 1,
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    whiteSpace: 'nowrap',
                  }}
                >
                  {food.name}
                </span>
                <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.75rem', color: '#5a6157', flexShrink: 0 }}>
                  {Math.round(Number(food.calories_per_100g))} {t.colKcal} ·{' '}
                  {Number(food.protein_per_100g).toFixed(1)}g {t.protein}
                </span>
              </label>
            )
          })}
        </div>
      )}
    </div>
  )
}
