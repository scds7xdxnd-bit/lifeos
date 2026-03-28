'use client'

import { useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { healthApi, BiometricCreateInput } from '@/lib/api/health'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'

interface BiometricLogFormProps {
  onClose: () => void
  onSuccess: () => void
}

function DotSelector({ value, onChange, label }: { value: number | null; onChange: (v: number) => void; label: string }) {
  return (
    <div>
      <label style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '8px' }}>
        {label}
      </label>
      <div className="flex gap-2">
        {[1, 2, 3, 4, 5].map(n => (
          <button
            key={n}
            type="button"
            onClick={() => onChange(n)}
            aria-label={`${label} ${n}`}
            style={{
              width: 20, height: 44, display: 'flex', alignItems: 'center', justifyContent: 'center',
              background: 'none', border: 'none', cursor: 'pointer', padding: 0,
            }}
          >
            <div style={{ width: 12, height: 12, borderRadius: '50%', background: value != null && n <= value ? '#4b6646' : '#dee5d7' }} />
          </button>
        ))}
      </div>
    </div>
  )
}

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '10px 14px', borderRadius: '8px',
  border: '1.5px solid #e8ede4', background: '#f8faf2',
  fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem',
  color: '#2e342b', outline: 'none', minHeight: '44px',
}

export default function BiometricLogForm({ onClose, onSuccess }: BiometricLogFormProps) {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health
  const today = new Date().toISOString().split('T')[0]

  const [form, setForm] = useState<BiometricCreateInput & { date: string }>({
    date: today, weight: undefined, body_fat_pct: undefined,
    resting_hr: undefined, energy_level: null as unknown as undefined,
    stress_level: null as unknown as undefined, notes: '',
  })
  const [energyLevel, setEnergyLevel] = useState<number | null>(null)
  const [stressLevel, setStressLevel] = useState<number | null>(null)
  const [duplicateError, setDuplicateError] = useState(false)

  const mutation = useMutation({
    mutationFn: () => healthApi.createBiometric({
      date: form.date,
      ...(form.weight != null ? { weight: form.weight } : {}),
      ...(form.body_fat_pct != null ? { body_fat_pct: form.body_fat_pct } : {}),
      ...(form.resting_hr != null ? { resting_hr: form.resting_hr } : {}),
      ...(energyLevel != null ? { energy_level: energyLevel } : {}),
      ...(stressLevel != null ? { stress_level: stressLevel } : {}),
      ...(form.notes ? { notes: form.notes } : {}),
    }),
    onSuccess: () => { onSuccess(); onClose() },
    onError: (err: Error) => {
      if (err.message === 'duplicate') setDuplicateError(true)
    },
  })

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setDuplicateError(false)
    mutation.mutate()
  }

  return (
    <div
      role="dialog" aria-modal="true" aria-label={t.logBiometric}
      style={{ position: 'fixed', inset: 0, zIndex: 70, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px' }}
    >
      <div style={{ position: 'absolute', inset: 0, background: 'rgba(22,33,49,0.44)', backdropFilter: 'blur(6px)' }} onClick={onClose} />
      <div style={{ position: 'relative', background: '#ffffff', borderRadius: '0 16px 16px 16px', padding: '32px', width: '100%', maxWidth: '480px', zIndex: 1 }}>
        <h2 style={{ fontFamily: 'var(--font-serif), Georgia, serif', fontSize: '1.25rem', fontWeight: 400, color: '#4b6646', marginBottom: '24px', letterSpacing: '-0.03em' }}>
          {t.logBiometric}
        </h2>

        <form onSubmit={handleSubmit}>
          <div className="flex flex-col gap-4">
            <div>
              <label htmlFor="bio-date" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.date}</label>
              <input id="bio-date" type="date" value={form.date} onChange={e => setForm(f => ({ ...f, date: e.target.value }))} required style={inputStyle} />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label htmlFor="bio-weight" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.weight}</label>
                <input id="bio-weight" type="number" step="0.1" min="0" value={form.weight ?? ''} onChange={e => setForm(f => ({ ...f, weight: e.target.value ? +e.target.value : undefined }))} style={inputStyle} />
              </div>
              <div>
                <label htmlFor="bio-fat" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.bodyFat}</label>
                <input id="bio-fat" type="number" step="0.1" min="0" value={form.body_fat_pct ?? ''} onChange={e => setForm(f => ({ ...f, body_fat_pct: e.target.value ? +e.target.value : undefined }))} style={inputStyle} />
              </div>
            </div>

            <div>
              <label htmlFor="bio-hr" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.restingHr}</label>
              <input id="bio-hr" type="number" step="1" min="0" value={form.resting_hr ?? ''} onChange={e => setForm(f => ({ ...f, resting_hr: e.target.value ? +e.target.value : undefined }))} style={inputStyle} />
            </div>

            <DotSelector value={energyLevel} onChange={setEnergyLevel} label={t.energy} />
            <DotSelector value={stressLevel} onChange={setStressLevel} label={t.stress} />

            <div>
              <label htmlFor="bio-notes" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', display: 'block', marginBottom: '6px' }}>{t.notes}</label>
              <textarea id="bio-notes" rows={3} maxLength={4096} value={form.notes} onChange={e => setForm(f => ({ ...f, notes: e.target.value }))} style={{ ...inputStyle, resize: 'vertical', minHeight: '80px' }} />
            </div>

            {duplicateError && (
              <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#8b4a3a' }}>{t.duplicateError}</p>
            )}

            <div className="flex gap-3 justify-end pt-2">
              <button type="button" onClick={onClose} aria-label={t.cancel} style={{ background: 'none', border: '1.5px solid #e8ede4', borderRadius: '100px', padding: '10px 24px', minHeight: '44px', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#5a6157', cursor: 'pointer' }}>
                {t.cancel}
              </button>
              <button type="submit" disabled={mutation.isPending} aria-label={mutation.isPending ? t.saving : t.save} style={{ background: 'linear-gradient(135deg, #4b6646, #3f5a3a)', borderRadius: '100px', padding: '10px 28px', minHeight: '44px', fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#ffffff', border: 'none', cursor: mutation.isPending ? 'not-allowed' : 'pointer', opacity: mutation.isPending ? 0.7 : 1 }}>
                {mutation.isPending ? t.saving : t.save}
              </button>
            </div>
          </div>
        </form>
      </div>
    </div>
  )
}
