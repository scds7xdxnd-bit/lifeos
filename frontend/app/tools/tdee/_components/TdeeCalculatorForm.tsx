'use client'

import { useState } from 'react'
import type { TdeeInput } from '@/lib/tdee-calculator'

interface TdeeCalculatorFormProps {
  onCalculate: (input: TdeeInput) => void
}

const ACTIVITY_LEVELS = [
  { value: 'sedentary', label: 'Sedentary' },
  { value: 'lightly_active', label: 'Lightly Active' },
  { value: 'moderately_active', label: 'Moderately Active' },
  { value: 'very_active', label: 'Very Active' },
  { value: 'extra_active', label: 'Extra Active' },
] as const

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
            fontFamily: 'var(--font-manrope), Manrope, sans-serif',
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

export default function TdeeCalculatorForm({ onCalculate }: TdeeCalculatorFormProps) {
  const [weight, setWeight] = useState('')
  const [height, setHeight] = useState('')
  const [age, setAge] = useState('')
  const [gender, setGender] = useState<'male' | 'female' | ''>('')
  const [bodyFat, setBodyFat] = useState('')
  const [activityLevel, setActivityLevel] = useState('')
  const [goalType, setGoalType] = useState<'lose' | 'gain' | 'maintain' | ''>('')
  const [goalWeight, setGoalWeight] = useState('')
  const [timeline, setTimeline] = useState('')

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
      activity_level: activityLevel as TdeeInput['activity_level'],
      goal_type: goalType as 'lose' | 'gain' | 'maintain',
      goal_weight_kg: goalWeight ? parseFloat(goalWeight) : null,
      goal_timeline_months: timeline ? parseInt(timeline) : null,
    })
  }

  const microLabel: React.CSSProperties = {
    fontFamily: 'var(--font-manrope), Manrope, sans-serif',
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
    fontFamily: 'var(--font-manrope), Manrope, sans-serif',
    fontSize: '0.875rem',
    color: '#2e342b',
    width: '100%',
    outline: 'none',
    boxSizing: 'border-box',
  }

  const labelStyle: React.CSSProperties = {
    fontFamily: 'var(--font-manrope), Manrope, sans-serif',
    fontWeight: 700,
    fontSize: '0.75rem',
    color: '#2e342b',
    display: 'block',
    marginBottom: '6px',
  }

  return (
    <form
      onSubmit={handleSubmit}
      style={{
        background: '#ffffff',
        borderRadius: '0 16px 16px 16px',
        padding: '32px',
        boxShadow: '0 4px 16px rgba(46,52,43,0.06)',
      }}
    >
      <style>{`@keyframes fadeIn { from { opacity: 0; transform: translateY(-8px); } to { opacity: 1; transform: none; } }`}</style>

      {/* Body Measurements */}
      <p style={microLabel}>Body Measurements</p>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '16px', marginBottom: '20px' }}>
        <div>
          <label style={labelStyle} htmlFor="tdee-weight">Weight (kg)</label>
          <input
            id="tdee-weight"
            type="number"
            step="0.1"
            min="0"
            max="500"
            value={weight}
            onChange={e => setWeight(e.target.value)}
            style={inputStyle}
            aria-required="true"
            aria-label="Weight (kg)"
          />
        </div>
        <div>
          <label style={labelStyle} htmlFor="tdee-height">Height (cm)</label>
          <input
            id="tdee-height"
            type="number"
            step="0.1"
            min="0"
            max="300"
            value={height}
            onChange={e => setHeight(e.target.value)}
            style={inputStyle}
            aria-required="true"
            aria-label="Height (cm)"
          />
        </div>
        <div>
          <label style={labelStyle} htmlFor="tdee-age">Age</label>
          <input
            id="tdee-age"
            type="number"
            step="1"
            min="1"
            max="120"
            value={age}
            onChange={e => setAge(e.target.value)}
            style={inputStyle}
            aria-required="true"
            aria-label="Age"
          />
        </div>
        <div>
          <label style={labelStyle} htmlFor="tdee-bodyfat">Body Fat %</label>
          <input
            id="tdee-bodyfat"
            type="number"
            step="0.1"
            min="0"
            max="80"
            value={bodyFat}
            onChange={e => setBodyFat(e.target.value)}
            style={inputStyle}
            aria-label="Body Fat %"
            placeholder="Optional"
          />
        </div>
      </div>

      {/* Gender */}
      <p style={{ ...microLabel, marginTop: '8px' }}>Gender</p>
      <div style={{ marginBottom: '20px' }}>
        <SegmentedControl
          options={[{ value: 'male', label: 'Male' }, { value: 'female', label: 'Female' }]}
          value={gender}
          onChange={v => setGender(v as 'male' | 'female')}
          ariaLabel="Gender"
        />
      </div>

      {/* Activity Level */}
      <p style={{ ...microLabel, marginTop: '8px' }}>Activity Level</p>
      <div style={{ marginBottom: '20px' }}>
        <SegmentedControl
          options={ACTIVITY_LEVELS.map(a => ({ value: a.value, label: a.label }))}
          value={activityLevel}
          onChange={setActivityLevel}
          ariaLabel="Activity Level"
        />
      </div>

      {/* Goal */}
      <p style={{ ...microLabel, marginTop: '8px' }}>Goal</p>
      <div style={{ marginBottom: '20px' }}>
        <SegmentedControl
          options={[{ value: 'lose', label: 'Lose Weight' }, { value: 'maintain', label: 'Maintain Weight' }, { value: 'gain', label: 'Gain Weight' }]}
          value={goalType}
          onChange={v => setGoalType(v as 'lose' | 'gain' | 'maintain')}
          ariaLabel="Goal"
        />
      </div>

      {/* Conditional: goal weight + timeline */}
      {(goalType === 'lose' || goalType === 'gain') && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '16px',
            marginBottom: '20px',
            animation: 'fadeIn 200ms ease',
          }}
        >
          <div>
            <label style={labelStyle} htmlFor="tdee-goalweight">Goal Weight (kg)</label>
            <input
              id="tdee-goalweight"
              type="number"
              step="0.1"
              min="0"
              max="500"
              value={goalWeight}
              onChange={e => setGoalWeight(e.target.value)}
              style={inputStyle}
              aria-required="true"
              aria-label="Goal Weight (kg)"
            />
          </div>
          <div>
            <label style={labelStyle} htmlFor="tdee-timeline">Timeline (months)</label>
            <input
              id="tdee-timeline"
              type="number"
              step="1"
              min="1"
              max="120"
              value={timeline}
              onChange={e => setTimeline(e.target.value)}
              style={inputStyle}
              aria-required="true"
              aria-label="Timeline (months)"
            />
          </div>
        </div>
      )}

      {/* Submit */}
      <div style={{ display: 'flex', justifyContent: 'center', marginTop: '8px' }}>
        <button
          type="submit"
          disabled={!canSubmit}
          style={{
            background: 'linear-gradient(135deg, #4b6646, #3f5a3a)',
            color: '#ffffff',
            border: 'none',
            borderRadius: '100px',
            padding: '12px 40px',
            minHeight: '48px',
            fontFamily: 'var(--font-manrope), Manrope, sans-serif',
            fontWeight: 600,
            fontSize: '0.9375rem',
            cursor: canSubmit ? 'pointer' : 'not-allowed',
            opacity: canSubmit ? 1 : 0.5,
            transition: 'opacity 0.15s',
          }}
        >
          Calculate
        </button>
      </div>
    </form>
  )
}
