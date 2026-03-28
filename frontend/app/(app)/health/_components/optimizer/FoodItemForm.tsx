'use client'

import { useState, useEffect, useCallback } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { foodLibraryApi } from '@/lib/api/foodLibrary'
import type { FoodItem } from '@/lib/api/foodLibrary'
import type { FoodSearchResult } from '@/lib/api/foodSearch'
import type { HealthPageTranslations } from '@/lib/translations/app'
import { FoodSearchInput } from './FoodSearchInput'

interface Props {
  mode: 'create' | 'edit'
  initialData?: FoodItem | null
  t: HealthPageTranslations
  lang?: string
  onClose: () => void
  onSuccess: () => void
}

const LABEL: React.CSSProperties = {
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.6875rem',
  fontWeight: 700,
  letterSpacing: '0.05em',
  textTransform: 'uppercase' as const,
  color: '#5a6157',
  display: 'block',
  marginBottom: 5,
}

const FIELD: React.CSSProperties = {
  width: '100%',
  padding: '9px 12px',
  fontFamily: 'Manrope, sans-serif',
  fontSize: '0.875rem',
  color: '#2e342b',
  background: '#f7f8f5',
  border: '1.5px solid rgba(173,180,168,0.4)',
  borderRadius: 4,
  outline: 'none',
  boxSizing: 'border-box' as const,
}

function useFlash() {
  const [flashing, setFlashing] = useState(false)
  const flash = useCallback(() => {
    setFlashing(true)
    setTimeout(() => setFlashing(false), 420)
  }, [])
  return { flashing, flash }
}

export function FoodItemForm({ mode, initialData, t, lang, onClose, onSuccess }: Props) {
  const qc = useQueryClient()

  const [name, setName] = useState(initialData?.name ?? '')
  const [cost, setCost] = useState(initialData?.cost_per_100g != null ? String(initialData.cost_per_100g) : '')
  const [calories, setCalories] = useState(initialData?.calories_per_100g != null ? String(initialData.calories_per_100g) : '')
  const [protein, setProtein] = useState(initialData?.protein_per_100g != null ? String(initialData.protein_per_100g) : '')
  const [carbs, setCarbs] = useState(initialData?.carbohydrate_per_100g != null ? String(initialData.carbohydrate_per_100g) : '')
  const [fat, setFat] = useState(initialData?.fat_per_100g != null ? String(initialData.fat_per_100g) : '')
  const [fiber, setFiber] = useState(initialData?.fiber_per_100g != null ? String(initialData.fiber_per_100g) : '')
  const [duplicateError, setDuplicateError] = useState(false)

  const calFlash = useFlash()
  const protFlash = useFlash()
  const carbFlash = useFlash()
  const fatFlash = useFlash()
  const fiberFlash = useFlash()

  // Close on Escape
  useEffect(() => {
    function onKey(e: KeyboardEvent) { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  function handleSearchSelect(result: FoodSearchResult) {
    setName(result.product_name)
    setCalories(String(result.calories_per_100g))
    setProtein(String(result.protein_per_100g))
    setCarbs(String(result.carbohydrate_per_100g))
    setFat(String(result.fat_per_100g))
    setFiber(result.fiber_per_100g != null ? String(result.fiber_per_100g) : '')
    // Flash all auto-filled fields
    calFlash.flash(); protFlash.flash(); carbFlash.flash(); fatFlash.flash(); fiberFlash.flash()
    // cost is intentionally NOT set — always manual
  }

  const createMutation = useMutation({
    mutationFn: () => foodLibraryApi.create({
      name: name.trim(),
      cost_per_100g: parseFloat(cost),
      calories_per_100g: parseFloat(calories),
      protein_per_100g: parseFloat(protein),
      carbohydrate_per_100g: parseFloat(carbs),
      fat_per_100g: parseFloat(fat),
      fiber_per_100g: fiber ? parseFloat(fiber) : undefined,
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['health', 'food-library'] }); onSuccess() },
    onError: (e: Error) => { if (e.message?.includes('409') || e.message?.includes('duplicate')) setDuplicateError(true) },
  })

  const updateMutation = useMutation({
    mutationFn: () => foodLibraryApi.update(initialData!.id, {
      name: name.trim(),
      cost_per_100g: parseFloat(cost),
      calories_per_100g: parseFloat(calories),
      protein_per_100g: parseFloat(protein),
      carbohydrate_per_100g: parseFloat(carbs),
      fat_per_100g: parseFloat(fat),
      fiber_per_100g: fiber ? parseFloat(fiber) : undefined,
    }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ['health', 'food-library'] }); onSuccess() },
    onError: (e: Error) => { if (e.message?.includes('409') || e.message?.includes('duplicate')) setDuplicateError(true) },
  })

  const saving = createMutation.isPending || updateMutation.isPending

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setDuplicateError(false)
    if (mode === 'create') createMutation.mutate()
    else updateMutation.mutate()
  }

  function flashStyle(flash: { flashing: boolean }): React.CSSProperties {
    return {
      ...FIELD,
      transition: 'background 0.4s ease',
      background: flash.flashing ? '#fdf0ed' : '#f7f8f5',
    }
  }

  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{ position: 'fixed', inset: 0, background: 'rgba(22,33,49,0.3)', zIndex: 70 }}
        aria-hidden="true"
      />

      {/* Modal card */}
      <div
        style={{
          position: 'fixed',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: 'min(520px, calc(100vw - 32px))',
          maxHeight: 'calc(100vh - 48px)',
          overflowY: 'auto',
          background: '#ffffff',
          borderRadius: '0 16px 16px 16px',
          padding: 32,
          zIndex: 71,
          boxShadow: '0 16px 48px rgba(46,52,43,0.12)',
        }}
        role="dialog"
        aria-modal="true"
      >
        <h2
          style={{
            fontFamily: 'Newsreader, Georgia, serif',
            fontSize: '1.125rem',
            fontWeight: 400,
            color: '#4b6646',
            marginBottom: 24,
          }}
        >
          {mode === 'create' ? t.addFood : t.editFood}
        </h2>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
          {/* Name / search */}
          <div>
            <label style={LABEL}>{t.foodName}</label>
            {mode === 'create' ? (
              <>
                <FoodSearchInput
                  value={name}
                  onChange={(v) => { setName(v); setDuplicateError(false) }}
                  onSelect={handleSearchSelect}
                  disabled={saving}
                  lang={lang}
                />
                <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.6875rem', color: '#767d72', marginTop: 5 }}>
                  Search for a food to auto-fill nutrition data, or enter values manually.
                </p>
              </>
            ) : (
              <input
                value={name}
                onChange={(e) => { setName(e.target.value); setDuplicateError(false) }}
                required
                disabled={saving}
                style={FIELD}
              />
            )}
            {duplicateError && (
              <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8rem', color: '#8b4a3a', marginTop: 4 }}>
                {t.duplicateFoodError}
              </p>
            )}
          </div>

          {/* Cost */}
          <div>
            <label style={LABEL}>{t.costPer100g}</label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={cost}
              onChange={(e) => setCost(e.target.value)}
              required
              disabled={saving}
              placeholder="0.00"
              style={FIELD}
            />
          </div>

          {/* Calories — full width */}
          <div>
            <label style={LABEL}>{t.caloriesPer100g}</label>
            <input
              type="number"
              min="0"
              step="1"
              value={calories}
              onChange={(e) => setCalories(e.target.value)}
              required
              disabled={saving}
              placeholder="0"
              style={flashStyle(calFlash)}
            />
          </div>

          {/* Protein + Carbs */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={LABEL}>{t.proteinPer100g}</label>
              <input type="number" min="0" step="0.1" value={protein} onChange={(e) => setProtein(e.target.value)} required disabled={saving} placeholder="0" style={flashStyle(protFlash)} />
            </div>
            <div>
              <label style={LABEL}>{t.carbsPer100g}</label>
              <input type="number" min="0" step="0.1" value={carbs} onChange={(e) => setCarbs(e.target.value)} required disabled={saving} placeholder="0" style={flashStyle(carbFlash)} />
            </div>
          </div>

          {/* Fat + Fiber */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
            <div>
              <label style={LABEL}>{t.fatPer100g}</label>
              <input type="number" min="0" step="0.1" value={fat} onChange={(e) => setFat(e.target.value)} required disabled={saving} placeholder="0" style={flashStyle(fatFlash)} />
            </div>
            <div>
              <label style={LABEL}>{t.fiberPer100g}</label>
              <input type="number" min="0" step="0.1" value={fiber} onChange={(e) => setFiber(e.target.value)} disabled={saving} placeholder="0" style={flashStyle(fiberFlash)} />
            </div>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end', marginTop: 8 }}>
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              style={{
                padding: '9px 22px',
                borderRadius: 100,
                border: '1.5px solid #c9d0c2',
                background: 'transparent',
                fontFamily: 'Manrope, sans-serif',
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#5a6157',
                cursor: saving ? 'not-allowed' : 'pointer',
              }}
            >
              {t.cancel}
            </button>
            <button
              type="submit"
              disabled={saving}
              style={{
                padding: '9px 22px',
                borderRadius: 100,
                border: 'none',
                background: saving ? '#c9d0c2' : 'linear-gradient(135deg, #4b6646, #3f5a3a)',
                fontFamily: 'Manrope, sans-serif',
                fontSize: '0.875rem',
                fontWeight: 600,
                color: '#ffffff',
                cursor: saving ? 'not-allowed' : 'pointer',
              }}
            >
              {saving ? t.saving : t.saveFood}
            </button>
          </div>
        </form>
      </div>
    </>
  )
}
