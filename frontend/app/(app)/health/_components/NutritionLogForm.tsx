'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { healthApi, NutritionCreateInput } from '@/lib/api/health'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'

interface NutritionLogFormProps {
  onClose: () => void
  onSuccess: () => void
}

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '10px 14px', borderRadius: '8px',
  border: '1.5px solid #e8ede4', background: '#f8faf2',
  fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem',
  color: '#2e342b', outline: 'none', minHeight: '44px',
}

type MealType = 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'other'

export default function NutritionLogForm({ onClose, onSuccess }: NutritionLogFormProps) {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health
  const today = new Date().toISOString().split('T')[0]

  const [form, setForm] = useState<NutritionCreateInput & { date: string }>({
    date: today, meal_type: 'lunch', items: '', calories_est: undefined, quality_score: undefined,
  })
  const [mealType, setMealType] = useState<MealType>('lunch')
  const [qualityScore, setQualityScore] = useState<number | null>(null)
  const [itemsError, setItemsError] = useState(false)

  const mutation = useMutation({
    mutationFn: () => healthApi.createNutrition({
      date: form.date,
      meal_type: mealType,
      items: form.items,
      ...(form.calories_est != null ? { calories_est: form.calories_est } : {}),
      ...(qualityScore != null ? { quality_score: qualityScore } : {}),
    }),
    onSuccess: () => { onSuccess(); onClose() },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!form.items.trim()) { setItemsError(true); return }
    setItemsError(false)
    mutation.mutate()
  }

  const mealOptions: { value: MealType; label: string }[] = [
    { value: 'breakfast', label: t.breakfast },
    { value: 'lunch', label: t.lunch },
    { value: 'dinner', label: t.dinner },
    { value: 'snack', label: t.snack },
    { value: 'other', label: t.other },
  ]

  return (
    <div
      role="dialog" aria-modal="true" aria-label={t.logMeal}
      style={{ position: 'fixed', inset: 0, zIndex: 70, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}
    >
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(22,33,49,0.44)', backdropFilter: 'blur(6px)' }} onClick={onClose} />
      <div style={{ position: 'relative', background: '#ffffff', borderRadius: '0 16px 16px 16px', padding: '32px', width: '100%', maxWidth: '480px', zIndex: 1 }}>
        <h2 style={{ fontFamily: 'var(--font-serif), Georgia, serif', fontSize: '1.25rem', fontWeight: 400, color: '#4b6646', marginBottom: '24px', letterSpacing: '-0.03em' }}>
          {t.logMeal}
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="flex flex-col gap-4">
            <div>
              <label htmlFor="nut-date" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.date}</label>
              <input id="nut-date" type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} required style={inputStyle} />
            </div>

            <div>
              <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', marginBottom: '8px' }}>{t.mealType}</p>
              <div className="flex flex-wrap gap-2">
                {mealOptions.map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setMealType(value)}
                    style={{
                      minHeight: '44px',
                      borderRadius: '100px',
                      padding: '6px 16px',
                      border: mealType === value ? '1.5px solid #8b4a3a' : '1.5px solid transparent',
                      background: mealType === value ? '#fce8e4' : '#f1f5eb',
                      color: mealType === value ? '#8b4a3a' : '#5a6157',
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.8125rem',
                      fontWeight: mealType === value ? 600 : 400,
                      cursor: 'pointer',
                    }}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label htmlFor="nut-items" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.items}</label>
              <textarea
                id="nut-items"
                rows={3}
                maxLength={4096}
                placeholder={t.itemsPlaceholder}
                value={form.items}
                onChange={e => { setForm(f => ({ ...f, items: e.target.value })); setItemsError(false) }}
                style={{ ...inputStyle, resize: 'vertical', minHeight: '80px', borderColor: itemsError ? '#8b4a3a' : '#e8ede4' }}
              />
              {itemsError && <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#8b4a3a', marginTop: '4px' }}>This field is required.</p>}
            </div>

            <div>
              <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', marginBottom: '8px' }}>{t.qualityScore}</p>
              <div className="flex items-center gap-2">
                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>Poor</span>
                <div className="flex gap-2">
                  {[1, 2, 3, 4, 5].map(n => (
                    <button
                      key={n}
                      type="button"
                      onClick={() => setQualityScore(n === qualityScore ? null : n)}
                      aria-label={`Quality ${n}`}
                      style={{
                        width: 24, height: 44, display: 'flex', alignItems: 'center', justifyContent: 'center',
                        background: 'none', border: 'none', cursor: 'pointer', padding: 0,
                      }}
                    >
                      <div style={{ width: 14, height: 14, borderRadius: '50%', background: qualityScore != null && n <= qualityScore ? '#4b6646' : '#dee5d7', transition: 'background 0.15s' }} />
                    </button>
                  ))}
                </div>
                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>Great</span>
              </div>
            </div>

            <div>
              <label htmlFor="nut-cal" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72', display: 'block', marginBottom: '6px' }}>{t.estimatedCalories}</label>
              <input id="nut-cal" type="number" min="0" value={form.calories_est ?? ''} onChange={e => setForm(f => ({ ...f, calories_est: e.target.value ? +e.target.value : undefined }))} style={{ ...inputStyle, fontSize: '0.8125rem' }} />
            </div>

            <div className="flex gap-3 justify-end pt-2">
              <button type="button" onClick={onClose} aria-label={t.cancel} style={{ background: 'none', border: '1.5px solid #e8ede4', borderRadius: '100px', padding: '10px 24px', minHeight: '44px', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#5a6157', cursor: 'pointer' }}>
                {t.cancel}
              </button>
              <button type="submit" disabled={mutation.isPending} aria-label={mutation.isPending ? t.saving : t.logMeal} style={{ background: 'linear-gradient(135deg, #4b6646, #3f5a3a)', borderRadius: '100px', padding: '10px 28px', minHeight: '44px', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#ffffff', border: 'none', cursor: mutation.isPending ? 'not-allowed' : 'pointer', opacity: mutation.isPending ? 0.7 : 1 }}>
                {mutation.isPending ? t.saving : t.logMeal}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
