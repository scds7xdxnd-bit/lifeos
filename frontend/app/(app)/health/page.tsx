'use client'

import { useState, useEffect, useRef, useCallback } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ChevronDown } from 'lucide-react'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import { healthApi, BiometricEntry, WorkoutEntry, NutritionEntry } from '@/lib/api/health'
import HealthOverviewCards from './_components/HealthOverviewCards'
import HealthDetailPanel from './_components/HealthDetailPanel'
import HealthEmptyState from './_components/HealthEmptyState'
import BiometricLogForm from './_components/BiometricLogForm'
import WorkoutLogForm from './_components/WorkoutLogForm'
import NutritionLogForm from './_components/NutritionLogForm'
import { OptimizerPanel } from './_components/optimizer/OptimizerPanel'
import CalculatorPanel from './_components/calculator/CalculatorPanel'

function getMonday(d: Date): Date {
  const date = new Date(d)
  const day = date.getDay()
  const diff = date.getDate() - day + (day === 0 ? -6 : 1)
  date.setDate(diff)
  return date
}

function formatEntryDate(dateStr: string) {
  return new Date(dateStr + 'T00:00:00').toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
}

type ActiveTab = 'biometrics' | 'workouts' | 'nutrition'
type LogForm = 'biometric' | 'workout' | 'nutrition' | null
type ActiveView = 'overview' | 'calculator' | 'optimizer'

const ROW_BASE: React.CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  gap: '12px',
  padding: '16px 24px',
  borderRadius: '0 12px 12px 12px',
  cursor: 'pointer',
  transition: 'background 0.15s',
  marginBottom: '6px',
  // All border sides as longhands to avoid shorthand/longhand conflicts on re-render
  borderTopWidth: 0,
  borderTopStyle: 'solid',
  borderTopColor: 'transparent',
  borderRightWidth: 0,
  borderRightStyle: 'solid',
  borderRightColor: 'transparent',
  borderBottomWidth: 0,
  borderBottomStyle: 'solid',
  borderBottomColor: 'transparent',
  borderLeftWidth: '2.5px',
  borderLeftStyle: 'solid',
  borderLeftColor: 'transparent',
}

export default function HealthPage() {
  const [lang] = useLang()
  const t = getAppTranslations(lang).health
  const queryClient = useQueryClient()

  const today = new Date().toISOString().split('T')[0]
  const monday = getMonday(new Date()).toISOString().split('T')[0]

  // UI state
  const [activeView, setActiveView] = useState<ActiveView>('overview')
  const [activeTab, setActiveTab] = useState<ActiveTab>('biometrics')
  const [selectedItem, setSelectedItem] = useState<{ type: 'biometric' | 'workout' | 'nutrition'; id: number } | null>(null)
  const [showLogForm, setShowLogForm] = useState<LogForm>(null)
  const [logDropdownOpen, setLogDropdownOpen] = useState(false)
  const [isCompactViewport, setIsCompactViewport] = useState(false)
  const [mobileDetailOpen, setMobileDetailOpen] = useState(false)
  const [reduceMotion, setReduceMotion] = useState(false)

  // Drawer drag state
  const [drawerOffsetY, setDrawerOffsetY] = useState(0)
  const [drawerDragging, setDrawerDragging] = useState(false)
  const drawerPointerId = useRef<number | null>(null)
  const drawerDragStartY = useRef<number | null>(null)
  const drawerDragStartOffset = useRef<number>(0)
  const drawerLastY = useRef<number>(0)
  const drawerVelocity = useRef<number>(0)

  useEffect(() => {
    const mq = window.matchMedia('(max-width: 1023px)')
    setIsCompactViewport(mq.matches)
    const handler = (e: MediaQueryListEvent) => setIsCompactViewport(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  useEffect(() => {
    const mq = window.matchMedia('(prefers-reduced-motion: reduce)')
    setReduceMotion(mq.matches)
    const handler = (e: MediaQueryListEvent) => setReduceMotion(e.matches)
    mq.addEventListener('change', handler)
    return () => mq.removeEventListener('change', handler)
  }, [])

  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (e.key === 'Escape') {
        if (showLogForm) { setShowLogForm(null); return }
        if (logDropdownOpen) { setLogDropdownOpen(false); return }
        if (mobileDetailOpen) setMobileDetailOpen(false)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [showLogForm, logDropdownOpen, mobileDetailOpen])

  // Queries
  const { data: dailyData } = useQuery({
    queryKey: ['health', 'daily', today],
    queryFn: () => healthApi.dailySummary(today),
  })

  const { data: weeklyData } = useQuery({
    queryKey: ['health', 'weekly', monday],
    queryFn: () => healthApi.weeklySummary(monday),
  })

  const { data: biometricsData, isLoading: bioLoading } = useQuery({
    queryKey: ['health', 'biometrics'],
    queryFn: () => healthApi.listBiometrics({ per_page: 30 }),
  })

  const { data: workoutsData, isLoading: workLoading } = useQuery({
    queryKey: ['health', 'workouts'],
    queryFn: () => healthApi.listWorkouts({ per_page: 30 }),
  })

  const { data: nutritionData, isLoading: nutLoading } = useQuery({
    queryKey: ['health', 'nutrition'],
    queryFn: () => healthApi.listNutrition({ per_page: 30 }),
  })

  const biometrics: BiometricEntry[] = biometricsData?.items ?? []
  const workouts: WorkoutEntry[] = workoutsData?.items ?? []
  const nutrition: NutritionEntry[] = nutritionData?.items ?? []
  const isLoading = bioLoading || workLoading || nutLoading

  const isEmpty = !isLoading && biometrics.length === 0 && workouts.length === 0 && nutrition.length === 0

  function handleSuccess() {
    queryClient.invalidateQueries({ queryKey: ['health'] })
  }

  function handleSelectItem(type: 'biometric' | 'workout' | 'nutrition', id: number) {
    setSelectedItem(prev => prev?.type === type && prev.id === id ? null : { type, id })
    if (isCompactViewport) setMobileDetailOpen(true)
  }

  // Drawer drag handlers
  const onDrawerPointerDown = useCallback((e: React.PointerEvent) => {
    drawerPointerId.current = e.pointerId
    drawerDragStartY.current = e.clientY
    drawerDragStartOffset.current = drawerOffsetY
    drawerLastY.current = e.clientY
    drawerVelocity.current = 0
    setDrawerDragging(true)
    ;(e.currentTarget as HTMLElement).setPointerCapture(e.pointerId)
  }, [drawerOffsetY])

  const onDrawerPointerMove = useCallback((e: React.PointerEvent) => {
    if (!drawerDragging || drawerDragStartY.current === null) return
    const raw = e.clientY - drawerDragStartY.current + drawerDragStartOffset.current
    const clamped = raw < 0 ? 0 : raw < 120 ? raw * 0.9 : 120 + (raw - 120) * 0.35
    drawerVelocity.current = e.clientY - drawerLastY.current
    drawerLastY.current = e.clientY
    setDrawerOffsetY(clamped)
  }, [drawerDragging])

  const onDrawerPointerUp = useCallback(() => {
    setDrawerDragging(false)
    if (drawerOffsetY > 95 || drawerVelocity.current > 0.65) {
      setMobileDetailOpen(false)
      setDrawerOffsetY(0)
    } else {
      setDrawerOffsetY(0)
    }
  }, [drawerOffsetY])

  const isOverviewLoading = bioLoading || workLoading || nutLoading

  const tabStyle = (tab: ActiveTab): React.CSSProperties => ({
    padding: '8px 18px',
    borderRadius: '100px',
    minHeight: '36px',
    border: 'none',
    cursor: 'pointer',
    fontFamily: 'var(--font-manrope), sans-serif',
    fontSize: '0.8125rem',
    fontWeight: activeTab === tab ? 600 : 400,
    background: activeTab === tab ? '#fce8e4' : 'transparent',
    color: activeTab === tab ? '#8b4a3a' : '#5a6157',
    transition: 'background 0.15s, color 0.15s',
  })

  function rowStyle(type: 'biometric' | 'workout' | 'nutrition', id: number): React.CSSProperties {
    const sel = selectedItem?.type === type && selectedItem.id === id
    return {
      ...ROW_BASE,
      background: sel ? 'linear-gradient(135deg, #fdf0ed, #f5ddd6)' : '#f3f7fb',
      borderLeftColor: sel ? '#8b4a3a' : 'transparent',
    }
  }

  function dotRow(value: number | null, filled: string = '#4b6646') {
    return (
      <div className="flex gap-1">
        {Array.from({ length: 5 }, (_, i) => (
          <div key={i} style={{ width: 8, height: 8, borderRadius: '50%', background: value != null && i < value ? filled : '#dee5d7' }} />
        ))}
      </div>
    )
  }

  const animStyle = (i: number): React.CSSProperties =>
    reduceMotion ? {} : {
      opacity: 0,
      animation: `fadeSlideIn 260ms ease-out ${i * 35}ms forwards`,
    }

  return (
    <div style={{ background: '#f8faf2', minHeight: '100%' }}>
      <style>{`
        @keyframes fadeSlideIn {
          from { opacity: 0; transform: translateY(8px); }
          to   { opacity: 1; transform: translateY(0); }
        }
      `}</style>

      {/* Page header */}
      <div className="flex items-start justify-between mb-8">
        <div>
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
            {t.eyebrow}
          </p>
          <h1
            style={{
              fontFamily: 'var(--font-serif), Georgia, serif',
              fontSize: '2rem',
              fontWeight: 300,
              color: '#4b6646',
              letterSpacing: '-0.03em',
            }}
          >
            {t.title}
          </h1>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.9375rem',
              color: '#5a6157',
              lineHeight: 1.65,
              marginTop: '4px',
            }}
          >
            {t.subtitle}
          </p>

          {/* View toggle */}
          <div style={{ display: 'flex', gap: 4, marginTop: 14 }}>
            {(['overview', 'calculator', 'optimizer'] as ActiveView[]).map((view) => (
              <button
                key={view}
                onClick={() => setActiveView(view)}
                style={{
                  padding: '6px 16px',
                  borderRadius: '100px',
                  border: 'none',
                  cursor: 'pointer',
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontSize: '0.78rem',
                  fontWeight: 600,
                  background: activeView === view ? '#fce8e4' : 'transparent',
                  color: activeView === view ? '#8b4a3a' : '#5a6157',
                  transition: 'background 0.15s, color 0.15s',
                }}
              >
                {view === 'overview' ? t.overview : view === 'calculator' ? t.calculator : t.optimizer}
              </button>
            ))}
          </div>
        </div>

        {/* LOG dropdown — only in overview */}
        {activeView === 'overview' && <div style={{ position: 'relative' }}>
          <button
            onClick={() => setLogDropdownOpen(o => !o)}
            aria-label={t.log}
            aria-expanded={logDropdownOpen}
            style={{
              background: 'linear-gradient(135deg, #4b6646, #3f5a3a)',
              borderRadius: '100px',
              padding: '10px 20px',
              minHeight: '44px',
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              fontWeight: 600,
              color: '#ffffff',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            {t.log}
            <ChevronDown size={14} style={{ transform: logDropdownOpen ? 'rotate(180deg)' : '', transition: 'transform 0.15s' }} />
          </button>

          {logDropdownOpen && (
            <div
              style={{
                position: 'absolute',
                right: 0,
                top: 'calc(100% + 8px)',
                background: '#ffffff',
                borderRadius: '0 12px 12px 12px',
                boxShadow: '0 8px 24px rgba(46,52,43,0.06)',
                zIndex: 50,
                minWidth: '180px',
                overflow: 'hidden',
              }}
            >
              {[
                { label: t.logBiometric, form: 'biometric' as LogForm },
                { label: t.logWorkout, form: 'workout' as LogForm },
                { label: t.logMeal, form: 'nutrition' as LogForm },
              ].map(({ label, form }) => (
                <button
                  key={label}
                  onClick={() => { setShowLogForm(form); setLogDropdownOpen(false) }}
                  aria-label={label}
                  style={{
                    display: 'block',
                    width: '100%',
                    textAlign: 'left',
                    padding: '0 20px',
                    minHeight: '44px',
                    background: 'none',
                    border: 'none',
                    cursor: 'pointer',
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontSize: '0.875rem',
                    color: '#2e342b',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.background = '#f1f5eb')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'none')}
                >
                  {label}
                </button>
              ))}
            </div>
          )}
        </div>}
      </div>

      {/* Close dropdown on outside click */}
      {activeView === 'overview' && logDropdownOpen && (
        <div style={{ position: 'fixed', inset: 0, zIndex: 40 }} onClick={() => setLogDropdownOpen(false)} aria-hidden="true" />
      )}

      {/* Calculator view */}
      {activeView === 'calculator' && <CalculatorPanel t={t} />}

      {/* Optimizer view */}
      {activeView === 'optimizer' && <OptimizerPanel t={t} onSwitchToCalculator={() => setActiveView('calculator')} />}

      {/* Overview content */}
      {activeView === 'overview' && (
        <>
      {/* Empty state */}
      {isEmpty && (
        <HealthEmptyState
          onLogBiometric={() => setShowLogForm('biometric')}
          onLogWorkout={() => setShowLogForm('workout')}
          onLogMeal={() => setShowLogForm('nutrition')}
        />
      )}

      {/* Main content */}
      {!isEmpty && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: isCompactViewport ? '1fr' : '60fr 40fr',
            gap: '24px',
            alignItems: 'start',
          }}
        >
          {/* Left column */}
          <div className="flex flex-col gap-8">
            {/* Overview cards */}
            <HealthOverviewCards
              dailySummary={dailyData?.summary ?? null}
              weeklySummary={weeklyData?.summary ?? null}
              recentBiometrics={biometrics}
              isLoading={isOverviewLoading}
            />

            {/* History section */}
            <section>
              <div
                style={{
                  background: '#f1f5eb',
                  borderRadius: '0 16px 16px 16px',
                  padding: '24px',
                }}
              >
                {/* Tabs */}
                <nav className="flex gap-2 mb-6" aria-label="History tabs">
                  {([
                    { key: 'biometrics' as ActiveTab, label: t.biometrics, count: biometricsData?.total },
                    { key: 'workouts' as ActiveTab, label: t.workouts, count: workoutsData?.total },
                    { key: 'nutrition' as ActiveTab, label: t.nutrition, count: nutritionData?.total },
                  ] as { key: ActiveTab; label: string; count: number | undefined }[]).map(({ key, label, count }) => (
                    <button
                      key={key}
                      onClick={() => setActiveTab(key)}
                      aria-selected={activeTab === key}
                      role="tab"
                      style={tabStyle(key)}
                    >
                      {label}{count != null ? ` (${count})` : ''}
                    </button>
                  ))}
                </nav>

                {/* Biometrics tab */}
                {activeTab === 'biometrics' && (
                  <div role="tabpanel">
                    {biometrics.length === 0 ? (
                      <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#767d72' }}>{t.noData}</p>
                    ) : (
                      biometrics.map((entry, i) => (
                        <button
                          key={entry.id}
                          onClick={() => handleSelectItem('biometric', entry.id)}
                          style={{ ...rowStyle('biometric', entry.id), width: '100%', textAlign: 'left', ...animStyle(i) }}
                          aria-label={`Biometric entry ${formatEntryDate(entry.date)}`}
                        >
                          <div style={{ flex: 1 }}>
                            <div className="flex items-center gap-4 flex-wrap">
                              <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b', minWidth: '60px' }}>
                                {formatEntryDate(entry.date)}
                              </span>
                              {entry.weight != null && <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157' }}>{entry.weight} kg</span>}
                              {entry.body_fat_pct != null && <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157' }}>{entry.body_fat_pct}%</span>}
                              {entry.resting_hr != null && <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157' }}>{entry.resting_hr} bpm</span>}
                            </div>
                            <div className="flex items-center gap-4 mt-1">
                              <div className="flex items-center gap-1.5">
                                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>{t.energy}:</span>
                                {dotRow(entry.energy_level)}
                              </div>
                              <div className="flex items-center gap-1.5">
                                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>{t.stress}:</span>
                                {dotRow(entry.stress_level)}
                              </div>
                            </div>
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                )}

                {/* Workouts tab */}
                {activeTab === 'workouts' && (
                  <div role="tabpanel">
                    {workouts.length === 0 ? (
                      <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#767d72' }}>{t.noData}</p>
                    ) : (
                      workouts.map((entry, i) => {
                        const intensityColors: Record<string, { bg: string; color: string }> = {
                          high: { bg: '#fce8e4', color: '#8b4a3a' },
                          medium: { bg: '#f5f0e4', color: '#6b5a35' },
                          low: { bg: '#f1f5eb', color: '#5a6157' },
                        }
                        const ic = intensityColors[entry.intensity] ?? intensityColors.medium
                        return (
                          <button
                            key={entry.id}
                            onClick={() => handleSelectItem('workout', entry.id)}
                            style={{ ...rowStyle('workout', entry.id), width: '100%', textAlign: 'left', ...animStyle(i) }}
                            aria-label={`Workout ${entry.workout_type} ${formatEntryDate(entry.date)}`}
                          >
                            <div style={{ flex: 1 }}>
                              <div className="flex items-center gap-3 flex-wrap">
                                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b', minWidth: '60px' }}>
                                  {formatEntryDate(entry.date)}
                                </span>
                                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b', textTransform: 'capitalize' }}>
                                  {entry.workout_type}
                                </span>
                                <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157' }}>{entry.duration_minutes} {t.minUnit}</span>
                                <span style={{ background: ic.bg, color: ic.color, borderRadius: '100px', padding: '2px 8px', fontSize: '0.75rem', fontFamily: 'var(--font-manrope), sans-serif', fontWeight: 500 }}>
                                  {({ low: t.low, medium: t.medium, high: t.high } as Record<string, string>)[entry.intensity] ?? entry.intensity}
                                </span>
                              </div>
                              {entry.calories_est != null && (
                                <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72', marginTop: '2px' }}>~{entry.calories_est} cal</p>
                              )}
                            </div>
                          </button>
                        )
                      })
                    )}
                  </div>
                )}

                {/* Nutrition tab */}
                {activeTab === 'nutrition' && (
                  <div role="tabpanel">
                    {nutrition.length === 0 ? (
                      <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#767d72' }}>{t.noData}</p>
                    ) : (
                      nutrition.map((entry, i) => (
                        <button
                          key={entry.id}
                          onClick={() => handleSelectItem('nutrition', entry.id)}
                          style={{ ...rowStyle('nutrition', entry.id), width: '100%', textAlign: 'left', ...animStyle(i) }}
                          aria-label={`Nutrition ${entry.meal_type} ${formatEntryDate(entry.date)}`}
                        >
                          <div style={{ flex: 1 }}>
                            <div className="flex items-center gap-3 flex-wrap">
                              <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b', minWidth: '60px' }}>
                                {formatEntryDate(entry.date)}
                              </span>
                              <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b' }}>
                                {({ breakfast: t.breakfast, lunch: t.lunch, dinner: t.dinner, snack: t.snack, other: t.other } as Record<string, string>)[entry.meal_type] ?? entry.meal_type}
                              </span>
                              {entry.quality_score != null && (
                                <div className="flex items-center gap-1.5">
                                  <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>{t.qualityLabel}:</span>
                                  {dotRow(entry.quality_score)}
                                </div>
                              )}
                            </div>
                            <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#5a6157', marginTop: '2px', overflow: 'hidden', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' }}>
                              {entry.items.join(', ')}
                            </p>
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                )}
              </div>
            </section>
          </div>

          {/* Right column — detail panel (desktop only) */}
          {!isCompactViewport && (
            <div style={{ position: 'sticky', top: '24px' }}>
              <HealthDetailPanel
                selectedItem={selectedItem}
                biometrics={biometrics}
                workouts={workouts}
                nutritionLogs={nutrition}
                weeklySummary={weeklyData?.summary ?? null}
              />
            </div>
          )}
        </div>
      )}

        </>
      )}

      {/* Mobile detail drawer */}
      {activeView === 'overview' && isCompactViewport && mobileDetailOpen && (
        <>
          <div
            style={{ position: 'fixed', inset: 0, background: 'rgba(22,33,49,0.3)', zIndex: 60 }}
            onClick={() => { setMobileDetailOpen(false); setDrawerOffsetY(0) }}
            aria-hidden="true"
          />
          <div
            style={{
              position: 'fixed',
              bottom: 0,
              left: 0,
              right: 0,
              maxHeight: '86vh',
              borderRadius: '16px 16px 0 0',
              zIndex: 61,
              overflow: 'auto',
              transform: `translateY(${drawerOffsetY}px)`,
              transition: drawerDragging ? 'none' : 'transform 0.3s ease',
            }}
          >
            {/* Drag handle */}
            <div
              onPointerDown={onDrawerPointerDown}
              onPointerMove={onDrawerPointerMove}
              onPointerUp={onDrawerPointerUp}
              onPointerCancel={onDrawerPointerUp}
              style={{
                background: '#fdf0ed',
                borderRadius: '16px 16px 0 0',
                padding: '12px',
                display: 'flex',
                justifyContent: 'center',
                cursor: 'grab',
                touchAction: 'none',
              }}
              aria-label="Drag to close"
            >
              <div style={{ width: 40, height: 4, borderRadius: '2px', background: '#c8d4be' }} />
            </div>

            <HealthDetailPanel
              selectedItem={selectedItem}
              biometrics={biometrics}
              workouts={workouts}
              nutritionLogs={nutrition}
              weeklySummary={weeklyData?.summary ?? null}
            />
          </div>
        </>
      )}

      {/* Log form modals */}
      {showLogForm === 'biometric' && (
        <BiometricLogForm
          onClose={() => setShowLogForm(null)}
          onSuccess={handleSuccess}
        />
      )}
      {showLogForm === 'workout' && (
        <WorkoutLogForm
          onClose={() => setShowLogForm(null)}
          onSuccess={handleSuccess}
        />
      )}
      {showLogForm === 'nutrition' && (
        <NutritionLogForm
          onClose={() => setShowLogForm(null)}
          onSuccess={handleSuccess}
        />
      )}
    </div>
  )
}
