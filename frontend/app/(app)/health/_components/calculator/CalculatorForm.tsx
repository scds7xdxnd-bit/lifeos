'use client'

import { useState, useEffect } from 'react'
import type { CalorieReport, CalculatorInput, Warning } from '@/lib/api/calculator'
import type { HealthPageTranslations } from '@/lib/translations/app'
import InfoTooltip from './InfoTooltip'

interface PrefillData {
  biometric: { weight_kg: number | null; body_fat_pct: number | null } | null
  profile: { height_cm: number; age_years: number; gender: string } | null
}

interface CalculatorFormProps {
  prefillData: PrefillData | null
  isLoading: boolean
  onCalculate: (input: CalculatorInput) => void
  isCalculating: boolean
  editingReport?: CalorieReport | null
  isEditMode?: boolean
  t: HealthPageTranslations
}

const ACTIVITY_LEVELS = [
  { value: 'sedentary', labelKey: 'sedentary', multiplier: 1.2, descKey: 'sedentaryDesc' },
  { value: 'lightly_active', labelKey: 'lightlyActive', multiplier: 1.375, descKey: 'lightlyActiveDesc' },
  { value: 'moderately_active', labelKey: 'moderatelyActive', multiplier: 1.55, descKey: 'moderatelyActiveDesc' },
  { value: 'very_active', labelKey: 'veryActive', multiplier: 1.725, descKey: 'veryActiveDesc' },
  { value: 'extra_active', labelKey: 'extraActive', multiplier: 1.9, descKey: 'extraActiveDesc' },
] as const

const autoFilledStyle: React.CSSProperties = {
  animation: 'autofill-flash 400ms ease forwards',
}

export default function CalculatorForm({ prefillData, isLoading, onCalculate, isCalculating, editingReport, isEditMode, t }: CalculatorFormProps) {
  const [weight, setWeight] = useState('')
  const [height, setHeight] = useState('')
  const [age, setAge] = useState('')
  const [gender, setGender] = useState<'male' | 'female' | ''>('')
  const [bodyFat, setBodyFat] = useState('')
  const [activityLevel, setActivityLevel] = useState('')
  const [goalType, setGoalType] = useState<'lose' | 'gain' | 'maintain' | ''>('')
  const [goalWeight, setGoalWeight] = useState('')
  const [timeline, setTimeline] = useState('')
  const [autoFilledFields, setAutoFilledFields] = useState<Set<string>>(new Set())

  useEffect(() => {
    if (!prefillData) return
    const filled: string[] = []
    if (prefillData.biometric?.weight_kg) {
      setWeight(String(prefillData.biometric.weight_kg))
      filled.push('weight')
    }
    if (prefillData.biometric?.body_fat_pct) {
      setBodyFat(String(prefillData.biometric.body_fat_pct))
      filled.push('bodyFat')
    }
    if (prefillData.profile?.height_cm) {
      setHeight(String(prefillData.profile.height_cm))
      filled.push('height')
    }
    if (prefillData.profile?.age_years) {
      setAge(String(prefillData.profile.age_years))
      filled.push('age')
    }
    if (prefillData.profile?.gender) {
      setGender(prefillData.profile.gender as 'male' | 'female')
      filled.push('gender')
    }
    if (filled.length > 0) setAutoFilledFields(new Set(filled))
  }, [prefillData])

  // Pre-fill all fields from an existing report when entering edit mode
  useEffect(() => {
    if (!editingReport) return
    setWeight(String(editingReport.weight_kg))
    setHeight(String(editingReport.height_cm))
    setAge(String(editingReport.age_years))
    setGender(editingReport.gender as 'male' | 'female')
    setBodyFat(editingReport.body_fat_pct != null ? String(editingReport.body_fat_pct) : '')
    setActivityLevel(editingReport.activity_level)
    setGoalType(editingReport.goal_type as 'lose' | 'gain' | 'maintain')
    setGoalWeight(editingReport.goal_weight_kg != null ? String(editingReport.goal_weight_kg) : '')
    setTimeline(editingReport.goal_timeline_months != null ? String(editingReport.goal_timeline_months) : '')
    setAutoFilledFields(new Set())
  }, [editingReport?.id])

  const canSubmit =
    weight && height && age && gender && activityLevel && goalType &&
    (goalType === 'maintain' || (goalWeight && timeline))

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!canSubmit) return
    onCalculate({
      weight_kg: parseFloat(weight),
      height_cm: parseFloat(height),
      age_years: parseInt(age),
      gender: gender as 'male' | 'female',
      body_fat_pct: bodyFat ? parseFloat(bodyFat) : null,
      activity_level: activityLevel,
      goal_type: goalType as 'lose' | 'gain' | 'maintain',
      goal_weight_kg: goalWeight ? parseFloat(goalWeight) : null,
      goal_timeline_months: timeline ? parseInt(timeline) : null,
      save_profile: true,
    })
  }

  const microLabel: React.CSSProperties = {
    fontFamily: 'Manrope, sans-serif',
    fontWeight: 700,
    fontSize: '0.6875rem',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    color: '#8b4a3a',
    marginBottom: '12px',
  }

  const inputStyle: React.CSSProperties = {
    background: '#ffffff',
    border: '1px solid rgba(173,180,168,0.2)',
    borderRadius: '4px',
    padding: '10px 14px',
    fontFamily: 'Manrope, sans-serif',
    fontSize: '0.875rem',
    color: '#2e342b',
    width: '100%',
    outline: 'none',
  }

  const labelStyle: React.CSSProperties = {
    fontFamily: 'Manrope, sans-serif',
    fontWeight: 700,
    fontSize: '0.75rem',
    color: '#2e342b',
    display: 'block',
    marginBottom: '6px',
  }

  function SegmentedControl({ options, value, onChange, ariaLabel }: {
    options: { value: string; label: string }[]
    value: string
    onChange: (v: string) => void
    ariaLabel: string
  }) {
    return (
      <div role="radiogroup" aria-label={ariaLabel} style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
        {options.map(opt => (
          <button
            key={opt.value}
            type="button"
            role="radio"
            aria-checked={value === opt.value}
            onClick={() => onChange(opt.value)}
            style={{
              borderRadius: '100px',
              padding: '8px 16px',
              fontFamily: 'Manrope, sans-serif',
              fontSize: '0.8125rem',
              fontWeight: 500,
              border: 'none',
              cursor: 'pointer',
              minHeight: '44px',
              background: value === opt.value ? '#fce8e4' : '#f1f5eb',
              color: value === opt.value ? '#8b4a3a' : '#5a6157',
              outline: value === opt.value ? '2px solid #4b6646' : 'none',
              outlineOffset: '2px',
              transition: 'background 0.15s, color 0.15s',
            }}
          >
            {opt.label}
          </button>
        ))}
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} style={{ background: '#ffffff', borderRadius: '0 16px 16px 16px', padding: '32px', boxShadow: '0 4px 16px rgba(46,52,43,0.06)' }}>
      <style>{`@keyframes autofill-flash { from { background: #fdf0ed; } to { background: #ffffff; } }`}</style>

      <p style={microLabel}>{t.bodyMeasurements}</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        <div>
          <label style={labelStyle} htmlFor="calc-weight">
            {t.weightKg}
            {autoFilledFields.has('weight') && <span style={{ color: '#767d72', fontWeight: 400, marginLeft: '6px', fontSize: '0.6875rem' }}>{t.autoFilled}</span>}
          </label>
          <input
            id="calc-weight"
            type="number"
            step="0.1"
            min="0"
            max="500"
            value={weight}
            onChange={e => setWeight(e.target.value)}
            style={{ ...inputStyle, ...(autoFilledFields.has('weight') ? autoFilledStyle : {}) }}
            aria-required="true"
            aria-label={t.weightKg}
          />
        </div>
        <div>
          <label style={labelStyle} htmlFor="calc-height">
            {t.heightCm}
            {autoFilledFields.has('height') && <span style={{ color: '#767d72', fontWeight: 400, marginLeft: '6px', fontSize: '0.6875rem' }}>{t.autoFilled}</span>}
          </label>
          <input
            id="calc-height"
            type="number"
            step="0.1"
            min="0"
            max="300"
            value={height}
            onChange={e => setHeight(e.target.value)}
            style={{ ...inputStyle, ...(autoFilledFields.has('height') ? autoFilledStyle : {}) }}
            aria-required="true"
            aria-label={t.heightCm}
          />
        </div>
        <div>
          <label style={labelStyle} htmlFor="calc-age">
            {t.age}
            {autoFilledFields.has('age') && <span style={{ color: '#767d72', fontWeight: 400, marginLeft: '6px', fontSize: '0.6875rem' }}>{t.autoFilled}</span>}
          </label>
          <input
            id="calc-age"
            type="number"
            step="1"
            min="1"
            max="120"
            value={age}
            onChange={e => setAge(e.target.value)}
            style={{ ...inputStyle, ...(autoFilledFields.has('age') ? autoFilledStyle : {}) }}
            aria-required="true"
            aria-label={t.age}
          />
        </div>
        <div>
          <label style={labelStyle} htmlFor="calc-bodyfat">
            {t.bodyFatPct}
            <InfoTooltip
              placement="top"
              maxWidth={240}
              content={
                <span>
                  <strong style={{ color: '#2e342b', display: 'block', marginBottom: '4px' }}>{t.tooltipFormulaSelection}</strong>
                  {t.tooltipKatchMcArdle}:<br />
                  BMR = 370 + (21.6 × lean mass)<br />
                  <br />
                  {t.tooltipMifflinStJeor}:<br />
                  Male: 10w + 6.25h − 5a + 5<br />
                  Female: 10w + 6.25h − 5a − 161
                </span>
              }
            />
          </label>
          <input
            id="calc-bodyfat"
            type="number"
            step="0.1"
            min="0"
            max="80"
            value={bodyFat}
            onChange={e => setBodyFat(e.target.value)}
            style={{ ...inputStyle, ...(autoFilledFields.has('bodyFat') ? autoFilledStyle : {}) }}
            aria-label={t.bodyFatPct}
          />
        </div>
      </div>

      <p style={{ ...microLabel, marginTop: '8px' }}>{t.genderLabel}</p>
      <div style={{ marginBottom: '20px' }}>
        <SegmentedControl
          options={[{ value: 'male', label: t.male }, { value: 'female', label: t.female }]}
          value={gender}
          onChange={v => setGender(v as 'male' | 'female')}
          ariaLabel={t.genderLabel}
        />
      </div>

      <p style={{ ...microLabel, marginTop: '8px', display: 'flex', alignItems: 'center' }}>
        {t.activityLevel}
        <InfoTooltip
          placement="top"
          maxWidth={260}
          content={
            <span>
              <strong style={{ color: '#2e342b', display: 'block', marginBottom: '6px' }}>TDEE = BMR × multiplier</strong>
              {ACTIVITY_LEVELS.map(a => (
                <span key={a.value} style={{ display: 'flex', justifyContent: 'space-between', gap: '8px', marginBottom: '3px' }}>
                  <span>×{a.multiplier}</span>
                  <span style={{ color: '#767d72', textAlign: 'right' }}>{t[a.descKey as keyof HealthPageTranslations] as string}</span>
                </span>
              ))}
            </span>
          }
        />
      </p>
      <div style={{ marginBottom: '20px' }}>
        <SegmentedControl
          options={ACTIVITY_LEVELS.map(a => ({ value: a.value, label: t[a.labelKey as keyof HealthPageTranslations] as string }))}
          value={activityLevel}
          onChange={setActivityLevel}
          ariaLabel={t.activityLevel}
        />
      </div>

      <p style={{ ...microLabel, marginTop: '8px', display: 'flex', alignItems: 'center' }}>
        {t.goal}
        <InfoTooltip
          placement="top"
          maxWidth={240}
          content={
            <span>
              <strong style={{ color: '#2e342b', display: 'block', marginBottom: '6px' }}>{t.tooltipCalorieAssumptions}</strong>
              <span style={{ display: 'block', marginBottom: '4px' }}><strong>{t.lose}:</strong> {t.tooltipLoseKcalFact}</span>
              <span style={{ display: 'block', marginBottom: '4px' }}><strong>{t.gain}:</strong> {t.tooltipGainKcalFact}</span>
              <span style={{ display: 'block', color: '#767d72', marginTop: '6px' }}>
                {t.tooltipDailyAdjustmentDesc}
              </span>
            </span>
          }
        />
      </p>
      <div style={{ marginBottom: '20px' }}>
        <SegmentedControl
          options={[{ value: 'lose', label: t.lose }, { value: 'maintain', label: t.maintain }, { value: 'gain', label: t.gain }]}
          value={goalType}
          onChange={v => setGoalType(v as 'lose' | 'gain' | 'maintain')}
          ariaLabel={t.goal}
        />
      </div>

      {(goalType === 'lose' || goalType === 'gain') && (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '20px', animation: 'fadeIn 200ms ease' }}>
          <style>{`@keyframes fadeIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: none; } }`}</style>
          <div>
            <label style={labelStyle} htmlFor="calc-goalweight">{t.goalWeightKg}</label>
            <input
              id="calc-goalweight"
              type="number"
              step="0.1"
              min="0"
              max="500"
              value={goalWeight}
              onChange={e => setGoalWeight(e.target.value)}
              style={inputStyle}
              aria-required="true"
              aria-label={t.goalWeightKg}
            />
          </div>
          <div>
            <label style={labelStyle} htmlFor="calc-timeline">
              {t.timelineMonths}
              <InfoTooltip
                placement="top"
                maxWidth={220}
                content={t.tooltipTimelineDesc}
              />
            </label>
            <input
              id="calc-timeline"
              type="number"
              step="1"
              min="1"
              max="120"
              value={timeline}
              onChange={e => setTimeline(e.target.value)}
              style={inputStyle}
              aria-required="true"
              aria-label={t.timelineMonths}
            />
          </div>
        </div>
      )}

      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '8px' }}>
        <button
          type="submit"
          disabled={!canSubmit || isCalculating}
          style={{
            background: 'linear-gradient(135deg, #4b6646, #3f5a3a)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '100px',
            padding: '12px 40px',
            minHeight: '48px',
            fontFamily: 'Manrope, sans-serif',
            fontWeight: 600,
            fontSize: '0.9375rem',
            cursor: canSubmit && !isCalculating ? 'pointer' : 'not-allowed',
            opacity: canSubmit && !isCalculating ? 1 : 0.5,
            transition: 'opacity 0.15s',
          }}
        >
          {isCalculating ? (isEditMode ? t.updating : t.calculating) : (isEditMode ? t.updateReport : t.calculate)}
        </button>
      </div>
    </form>
  )
}
