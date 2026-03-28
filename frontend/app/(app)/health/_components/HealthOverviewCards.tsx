'use client'

import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import type { DailySummary, WeeklySummary, BiometricEntry } from '@/lib/api/health'
import BiometricTrendCard from './BiometricTrendCard'
import WorkoutSummaryCard from './WorkoutSummaryCard'
import NutritionSummaryCard from './NutritionSummaryCard'

interface HealthOverviewCardsProps {
  dailySummary: DailySummary | null
  weeklySummary: WeeklySummary | null
  recentBiometrics: BiometricEntry[]
  isLoading: boolean
}

function SkeletonCard() {
  return (
    <div
      style={{
        background: '#ffffff', borderRadius: '0 16px 16px 16px',
        boxShadow: '0 8px 24px rgba(46,52,43,0.06)', padding: '32px',
      }}
    >
      <div style={{ background: '#f1f5eb', borderRadius: '4px', height: '10px', width: '60px', marginBottom: '16px' }} />
      <div style={{ background: '#f1f5eb', borderRadius: '4px', height: '28px', width: '100px', marginBottom: '8px' }} />
      <div style={{ background: '#f1f5eb', borderRadius: '4px', height: '12px', width: '80px' }} />
    </div>
  )
}

export default function HealthOverviewCards({
  dailySummary,
  weeklySummary,
  recentBiometrics,
  isLoading,
}: HealthOverviewCardsProps) {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health

  // Derive biometric props
  const weightEntries = recentBiometrics.filter(b => b.weight != null)
  const latestWeight = weightEntries[0]?.weight ?? null
  const oldestWeight = weightEntries[weightEntries.length - 1]?.weight ?? null
  const weightDelta = latestWeight != null && oldestWeight != null ? +(latestWeight - oldestWeight).toFixed(1) : null
  const trendDirection =
    weightDelta == null ? 'stable'
    : weightDelta > 0.5 ? 'up'
    : weightDelta < -0.5 ? 'down'
    : 'stable'

  const latestBio = recentBiometrics[0]
  const energyLevel = latestBio?.energy_level ?? null
  const stressLevel = latestBio?.stress_level ?? null

  // Derive workout props
  const sessionsThisWeek = weeklySummary?.workouts.count ?? 0
  const totalDurationMinutes = weeklySummary?.workouts.total_duration_minutes ?? 0
  const workoutTypes = weeklySummary?.workouts.by_type ?? {}

  // Derive nutrition props
  const mealsToday = dailySummary?.nutrition.count ?? 0
  const weeklyMealDays: boolean[] = Array(7).fill(false)

  return (
    <section>
      <p
        style={{
          fontFamily: 'var(--font-manrope), sans-serif',
          fontSize: '0.6875rem',
          fontWeight: 700,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: '#8b4a3a',
          marginBottom: '6px',
        }}
      >
        {t.overview}
      </p>
      <h2
        style={{
          fontFamily: 'var(--font-serif), Georgia, serif',
          fontSize: '1.125rem',
          fontWeight: 400,
          color: '#4b6646',
          letterSpacing: '-0.03em',
          marginBottom: '16px',
        }}
      >
        {t.yourWeekSoFar}
      </h2>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: '16px',
        }}
      >
        {isLoading ? (
          <>
            <SkeletonCard />
            <SkeletonCard />
            <SkeletonCard />
          </>
        ) : (
          <>
            <BiometricTrendCard
              latestWeight={latestWeight}
              weightDelta={weightDelta}
              trendDirection={trendDirection}
              energyLevel={energyLevel}
              stressLevel={stressLevel}
            />
            <WorkoutSummaryCard
              sessionsThisWeek={sessionsThisWeek}
              totalDurationMinutes={totalDurationMinutes}
              workoutTypes={workoutTypes}
            />
            <NutritionSummaryCard
              mealsToday={mealsToday}
              averageQuality={null}
              weeklyMealDays={weeklyMealDays}
            />
          </>
        )}
      </div>
    </section>
  )
}
