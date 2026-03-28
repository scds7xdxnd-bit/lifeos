'use client'

import { Heart } from 'lucide-react'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import type { BiometricEntry, WorkoutEntry, NutritionEntry, WeeklySummary } from '@/lib/api/health'
import WeightSparkline from './WeightSparkline'
import WeeklyWorkoutDots from './WeeklyWorkoutDots'
import NutritionQualityDots from './NutritionQualityDots'

interface HealthDetailPanelProps {
  selectedItem: { type: 'biometric' | 'workout' | 'nutrition'; id: number } | null
  biometrics: BiometricEntry[]
  workouts: WorkoutEntry[]
  nutritionLogs: NutritionEntry[]
  weeklySummary: WeeklySummary | null
}

function StatCard({ label, value }: { label: string; value: string | number | null }) {
  return (
    <div
      style={{
        background: '#fdf0ed',
        borderRadius: '0 10px 10px 10px',
        padding: '14px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
      }}
    >
      <span
        style={{
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.6875rem',
          fontWeight: 700,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: '#8b4a3a',
        }}
      >
        {label}
      </span>
      <span
        style={{
          fontFamily: 'var(--font-serif), Georgia, serif',
          fontSize: '1.25rem',
          fontWeight: 400,
          color: '#2e342b',
        }}
      >
        {value ?? '—'}
      </span>
    </div>
  )
}

function formatDate(dateStr: string) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

function buildWeekDays(entries: WorkoutEntry[]): Array<{ date: string; hasWorkout: boolean }> {
  const today = new Date()
  const monday = new Date(today)
  const day = today.getDay()
  monday.setDate(today.getDate() - (day === 0 ? 6 : day - 1))
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    const dateStr = d.toISOString().split('T')[0]
    return { date: dateStr, hasWorkout: entries.some(w => w.date === dateStr) }
  })
}

function buildQualityDays(logs: NutritionEntry[]): Array<{ date: string; avgQuality: number | null }> {
  const today = new Date()
  const monday = new Date(today)
  const day = today.getDay()
  monday.setDate(today.getDate() - (day === 0 ? 6 : day - 1))
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(monday)
    d.setDate(monday.getDate() + i)
    const dateStr = d.toISOString().split('T')[0]
    const dayLogs = logs.filter(n => n.date === dateStr && n.quality_score != null)
    const avg = dayLogs.length ? dayLogs.reduce((s, n) => s + (n.quality_score ?? 0), 0) / dayLogs.length : null
    return { date: dateStr, avgQuality: avg }
  })
}

export default function HealthDetailPanel({
  selectedItem,
  biometrics,
  workouts,
  nutritionLogs,
  weeklySummary,
}: HealthDetailPanelProps) {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health

  const panelStyle: React.CSSProperties = {
    background: 'linear-gradient(160deg, #fdf0ed 0%, #ffffff 100%)',
    borderRadius: '0 16px 16px 16px',
    boxShadow: '0 10px 26px rgba(46, 52, 43, 0.07)',
    padding: '24px',
    display: 'flex',
    flexDirection: 'column',
    gap: '24px',
    height: '100%',
  }

  if (!selectedItem) {
    return (
      <div style={panelStyle}>
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', textAlign: 'center', minHeight: '200px' }}>
          <div style={{ width: 48, height: 48, borderRadius: '50%', background: '#fce8e4', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Heart size={22} style={{ color: '#8b4a3a' }} aria-hidden="true" />
          </div>
          <p style={{ fontFamily: 'var(--font-serif), Georgia, serif', fontSize: '1.125rem', fontWeight: 400, color: '#5a6157' }}>
            {t.selectEntry}
          </p>
        </div>
      </div>
    )
  }

  if (selectedItem.type === 'biometric') {
    const entry = biometrics.find(b => b.id === selectedItem.id)
    if (!entry) return <div style={panelStyle} />
    const sparkData = biometrics
      .filter(b => b.weight != null)
      .map(b => ({ date: b.date, weight: b.weight! }))
      .reverse()

    return (
      <div style={panelStyle}>
        <div>
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#8b4a3a', marginBottom: '4px' }}>{t.selectedEntry}</p>
          <p style={{ fontFamily: 'var(--font-serif), Georgia, serif', fontSize: '1.125rem', fontWeight: 400, color: '#2e342b' }}>{formatDate(entry.date)}</p>
          {entry.notes && <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', marginTop: '4px' }}>{entry.notes}</p>}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <StatCard label={t.weight} value={entry.weight != null ? `${entry.weight} kg` : null} />
          <StatCard label={t.bodyFat} value={entry.body_fat_pct != null ? `${entry.body_fat_pct}%` : null} />
          <StatCard label={t.restingHr} value={entry.resting_hr != null ? `${entry.resting_hr} bpm` : null} />
          <StatCard label={`${t.energy} / ${t.stress}`} value={entry.energy_level != null ? `${entry.energy_level} / ${entry.stress_level ?? '—'}` : null} />
        </div>
        <div>
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#8b4a3a', marginBottom: '12px' }}>{t.weightTrend}</p>
          <WeightSparkline entries={sparkData} />
        </div>
      </div>
    )
  }

  if (selectedItem.type === 'workout') {
    const entry = workouts.find(w => w.id === selectedItem.id)
    if (!entry) return <div style={panelStyle} />
    const weekDays = buildWeekDays(workouts)

    return (
      <div style={panelStyle}>
        <div>
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#8b4a3a', marginBottom: '4px' }}>{t.selectedEntry}</p>
          <p style={{ fontFamily: 'var(--font-serif), Georgia, serif', fontSize: '1.125rem', fontWeight: 400, color: '#2e342b' }}>
            {entry.workout_type.charAt(0).toUpperCase() + entry.workout_type.slice(1)} · {formatDate(entry.date)}
          </p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <StatCard label={t.duration} value={`${entry.duration_minutes} ${t.minUnit}`} />
          <StatCard label={t.intensity} value={({ low: t.low, medium: t.medium, high: t.high } as Record<string, string>)[entry.intensity] ?? entry.intensity} />
          <StatCard label={t.estimatedCalories} value={entry.calories_est != null ? `~${entry.calories_est} cal` : null} />
          <StatCard label={t.thisWeek} value={`${weeklySummary?.workouts.count ?? 0} ${t.sessions}`} />
        </div>
        <div>
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#8b4a3a', marginBottom: '12px' }}>{t.thisWeek}</p>
          <WeeklyWorkoutDots days={weekDays} />
        </div>
      </div>
    )
  }

  if (selectedItem.type === 'nutrition') {
    const entry = nutritionLogs.find(n => n.id === selectedItem.id)
    if (!entry) return <div style={panelStyle} />
    const qualityDays = buildQualityDays(nutritionLogs)

    return (
      <div style={panelStyle}>
        <div>
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#8b4a3a', marginBottom: '4px' }}>{t.selectedEntry}</p>
          <p style={{ fontFamily: 'var(--font-serif), Georgia, serif', fontSize: '1.125rem', fontWeight: 400, color: '#2e342b' }}>
            {({ breakfast: t.breakfast, lunch: t.lunch, dinner: t.dinner, snack: t.snack, other: t.other } as Record<string, string>)[entry.meal_type] ?? entry.meal_type} · {formatDate(entry.date)}
          </p>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
          <StatCard label={t.qualityScore} value={entry.quality_score != null ? `${entry.quality_score} / 5` : null} />
          <StatCard label={t.itemsLabel} value={entry.items.length} />
          <StatCard label={t.todaysMeals} value={weeklySummary ? null : null} />
          <StatCard label={t.thisWeek} value={`${weeklySummary?.nutrition.count ?? 0} ${t.mealsUnit}`} />
        </div>
        <div>
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.6875rem', fontWeight: 700, letterSpacing: '0.05em', textTransform: 'uppercase', color: '#8b4a3a', marginBottom: '12px' }}>{t.nutrition}</p>
          <NutritionQualityDots days={qualityDays} />
        </div>
      </div>
    )
  }

  return <div style={panelStyle} />
}
