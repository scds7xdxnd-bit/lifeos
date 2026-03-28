'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { healthApi, WorkoutCreateInput } from '@/lib/api/health'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'

interface WorkoutLogFormProps {
  onClose: () => void
  onSuccess: () => void
}

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '10px 14px', borderRadius: '8px',
  border: '1.5px solid #e8ede4', background: '#f8faf2',
  fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem',
  color: '#2e342b', outline: 'none', minHeight: '44px',
}

type Intensity = 'low' | 'medium' | 'high'

export default function WorkoutLogForm({ onClose, onSuccess }: WorkoutLogFormProps) {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health
  const today = new Date().toISOString().split('T')[0]

  const [form, setForm] = useState<WorkoutCreateInput & { date: string }>({
    date: today, workout_type: '', duration_minutes: 0, intensity: 'medium',
    calories_est: undefined, notes: '',
  })
  const [intensity, setIntensity] = useState<Intensity>('medium')

  const mutation = useMutation({
    mutationFn: () => healthApi.createWorkout({
      date: form.date,
      workout_type: form.workout_type,
      duration_minutes: form.duration_minutes || 0,
      intensity,
      ...(form.calories_est != null ? { calories_est: form.calories_est } : {}),
      ...(form.notes ? { notes: form.notes } : {}),
    }),
    onSuccess: () => { onSuccess(); onClose() },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    mutation.mutate()
  }

  const intensityOptions: { value: Intensity; label: string }[] = [
    { value: 'low', label: t.low },
    { value: 'medium', label: t.medium },
    { value: 'high', label: t.high },
  ]

  function handleIntensityKey(e: React.KeyboardEvent, val: Intensity) {
    const order: Intensity[] = ['low', 'medium', 'high']
    const idx = order.indexOf(intensity)
    if (e.key === 'ArrowRight' && idx < 2) setIntensity(order[idx + 1])
    else if (e.key === 'ArrowLeft' && idx > 0) setIntensity(order[idx - 1])
    else if (e.key === 'Enter') setIntensity(val)
  }

  return (
    <div
      role="dialog" aria-modal="true" aria-label={t.logWorkout}
      style={{ position: 'fixed', inset: 0, zIndex: 70, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}
    >
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(22,33,49,0.44)', backdropFilter: 'blur(6px)' }} onClick={onClose} />
      <div style={{ position: 'relative', background: '#ffffff', borderRadius: '0 16px 16px 16px', padding: '32px', width: '100%', maxWidth: '480px', zIndex: 1 }}>
        <h2 style={{ fontFamily: 'var(--font-serif), Georgia, serif', fontSize: '1.25rem', fontWeight: 400, color: '#4b6646', marginBottom: '24px', letterSpacing: '-0.03em' }}>
          {t.logWorkout}
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="flex flex-col gap-4">
            <div>
              <label htmlFor="wk-date" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.date}</label>
              <input id="wk-date" type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} required style={inputStyle} />
            </div>

            <div>
              <label htmlFor="wk-type" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.workoutType}</label>
              <input id="wk-type" type="text" maxLength={64} required value={form.workout_type} onChange={e => setForm(f => ({ ...f, workout_type: e.target.value }))} aria-label={t.workoutType} style={inputStyle} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="wk-dur" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.duration}</label>
                <input id="wk-dur" type="number" step="5" min="0" value={form.duration_minutes ?? 0} onChange={e => setForm(f => ({ ...f, duration_minutes: +e.target.value }))} style={inputStyle} />
              </div>
              <div>
                <label htmlFor="wk-cal" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.estimatedCalories}</label>
                <input id="wk-cal" type="number" min="0" value={form.calories_est ?? ''} onChange={e => setForm(f => ({ ...f, calories_est: e.target.value ? +e.target.value : undefined }))} style={inputStyle} />
              </div>
            </div>

            <div>
              <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', marginBottom: '8px' }}>{t.intensity}</p>
              <div className="flex gap-2">
                {intensityOptions.map(({ value, label }) => (
                  <button
                    key={value}
                    type="button"
                    role="radio"
                    aria-checked={intensity === value}
                    onClick={() => setIntensity(value)}
                    onKeyDown={e => handleIntensityKey(e, value)}
                    style={{
                      flex: 1,
                      minHeight: '44px',
                      borderRadius: '100px',
                      border: intensity === value ? '1.5px solid #8b4a3a' : '1.5px solid transparent',
                      background: intensity === value ? '#fce8e4' : '#f1f5eb',
                      color: intensity === value ? '#8b4a3a' : '#5a6157',
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.8125rem',
                      fontWeight: intensity === value ? 600 : 400,
                      cursor: 'pointer',
                    }}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label htmlFor="wk-notes" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.notes}</label>
              <textarea id="wk-notes" rows={2} maxLength={4096} value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} style={{ ...inputStyle, resize: 'vertical', minHeight: '64px' }} />
            </div>

            <div className="flex gap-3 justify-end pt-2">
              <button type="button" onClick={onClose} aria-label={t.cancel} style={{ background: 'none', border: '1.5px solid #e8ede4', borderRadius: '100px', padding: '10px 24px', minHeight: '44px', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#5a6157', cursor: 'pointer' }}>
                {t.cancel}
              </button>
              <button type="submit" disabled={mutation.isPending} aria-label={mutation.isPending ? t.saving : 'Log Workout'} style={{ background: 'linear-gradient(135deg, #4b6646, #3f5a3a)', borderRadius: '100px', padding: '10px 28px', minHeight: '44px', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#ffffff', border: 'none', cursor: mutation.isPending ? 'not-allowed' : 'pointer', opacity: mutation.isPending ? 0.7 : 1 }}>
                {mutation.isPending ? t.saving : t.logWorkout}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
