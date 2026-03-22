'use client'

import { useEffect, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { habitsApi, type Habit } from '@/lib/api/habits'
import { Flame, BarChart3, Calendar, Leaf } from 'lucide-react'
import { HabitStreakChart } from './HabitStreakChart'
import { HabitHeatmap } from './HabitHeatmap'

interface DetailTranslations {
  detailTitle: string
  currentStreak: string
  longestStreak: string
  completionRate: string
  totalLogs: string
  last30Days: string
  yearlyHeatmap: string
  selectHabit: string
  days: string
  noData: string
}

interface HabitDetailPanelProps {
  habit: Habit | null
  t: DetailTranslations
  onUpdated?: () => void
  sticky?: boolean
}

function containsCjk(text: string): boolean {
  return /[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uac00-\ud7af]/.test(text)
}

function getMicroLabelStyle(label: string, accent = '#767d72'): React.CSSProperties {
  if (containsCjk(label)) {
    return {
      fontFamily: 'var(--font-manrope), sans-serif',
      fontSize: '0.75rem',
      fontWeight: 700,
      textTransform: 'none',
      letterSpacing: '0.02em',
      color: accent,
    }
  }

  return {
    fontFamily: 'var(--font-manrope), sans-serif',
    fontSize: '0.6875rem',
    fontWeight: 700,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    color: accent,
  }
}

export function HabitDetailPanel({ habit, t, onUpdated, sticky = true }: HabitDetailPanelProps) {
  const currentYear = new Date().getFullYear()
  const qc = useQueryClient()
  const [scheduledTimeInput, setScheduledTimeInput] = useState('')

  useEffect(() => {
    setScheduledTimeInput(habit?.scheduled_time?.slice(0, 5) ?? '')
  }, [habit?.id, habit?.scheduled_time])

  const updateMut = useMutation({
    mutationFn: (nextTime: string) => {
      if (!habit) {
        throw new Error('No habit selected')
      }
      return habitsApi.update(habit.id, {
        scheduled_time: nextTime || null,
      })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['habits'] })
      if (habit) {
        qc.invalidateQueries({ queryKey: ['habits', habit.id, 'stats'] })
        qc.invalidateQueries({ queryKey: ['habits', habit.id, 'history', '30d'] })
        qc.invalidateQueries({ queryKey: ['habits', habit.id, 'heatmap', currentYear] })
      }
      onUpdated?.()
    },
  })

  const { data: statsData } = useQuery({
    queryKey: ['habits', habit?.id, 'stats'],
    queryFn: () => habitsApi.stats(habit!.id),
    enabled: !!habit,
  })

  const { data: historyData } = useQuery({
    queryKey: ['habits', habit?.id, 'history', '30d'],
    queryFn: () => habitsApi.history(habit!.id, '30d'),
    enabled: !!habit,
  })

  const { data: heatmapData } = useQuery({
    queryKey: ['habits', habit?.id, 'heatmap', currentYear],
    queryFn: () => habitsApi.heatmap(habit!.id, currentYear),
    enabled: !!habit,
  })

  // Empty selection state
  if (!habit) {
    return (
      <div
        style={{
          background: 'linear-gradient(160deg, #f6f9fc 0%, #ffffff 100%)',
          borderRadius: '0 16px 16px 16px',
          boxShadow: '0 10px 26px rgba(46, 52, 43, 0.07)',
          padding: '48px 24px',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          gap: '16px',
          minHeight: '400px',
        }}
      >
        <div
          style={{
            width: '56px',
            height: '56px',
            borderRadius: '50%',
            background: '#f1f5eb',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Leaf size={24} style={{ color: '#767d72' }} />
        </div>
        <p
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.875rem',
            color: '#767d72',
            textAlign: 'center',
          }}
        >
          {t.selectHabit}
        </p>
      </div>
    )
  }

  const stats = statsData?.stats
  const entries = historyData?.history?.entries ?? []
  const heatmapEntries = heatmapData?.heatmap?.entries ?? []

  return (
    <div
      style={{
        background: 'linear-gradient(160deg, #f6f9fc 0%, #ffffff 100%)',
        borderRadius: '0 16px 16px 16px',
        boxShadow: '0 10px 26px rgba(46, 52, 43, 0.07)',
        padding: '24px',
        display: 'flex',
        flexDirection: 'column',
        gap: '24px',
        position: sticky ? 'sticky' : 'static',
        top: sticky ? '24px' : undefined,
      }}
    >
      {/* Habit name */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <p style={getMicroLabelStyle(t.detailTitle, '#3a5272')}>
          {t.detailTitle}
        </p>
        <h2
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '1.25rem',
            fontWeight: 400,
            color: '#2e342b',
            letterSpacing: '-0.03em',
            margin: 0,
          }}
        >
          {habit.name}
        </h2>
        {habit.description && (
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.8125rem',
              color: '#5a6157',
              lineHeight: 1.5,
              marginTop: '4px',
            }}
          >
            {habit.description}
          </p>
        )}
      </div>

      {/* Scheduled time editor */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        <label
          htmlFor="habit-scheduled-time"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.6875rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: '#767d72',
          }}
        >
          Scheduled time
        </label>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <input
            id="habit-scheduled-time"
            type="time"
            value={scheduledTimeInput}
            onChange={(e) => setScheduledTimeInput(e.target.value)}
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              color: '#2e342b',
              background: '#ffffff',
              border: '1px solid rgba(173, 180, 168, 0.20)',
              borderRadius: '4px',
              padding: '8px 10px',
            }}
          />
          <button
            type="button"
            onClick={() => updateMut.mutate(scheduledTimeInput)}
            disabled={updateMut.isPending}
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.75rem',
              fontWeight: 700,
              color: '#ffffff',
              background: 'linear-gradient(135deg, #3a5272, #2e4460)',
              border: 'none',
              borderRadius: '100px',
              minHeight: '44px',
              padding: '0 14px',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
            }}
          >
            {updateMut.isPending ? 'Saving...' : 'Save'}
          </button>
          <button
            type="button"
            onClick={() => {
              setScheduledTimeInput('')
              updateMut.mutate('')
            }}
            disabled={updateMut.isPending}
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.75rem',
              fontWeight: 700,
              color: '#5a6157',
              background: '#f1f5eb',
              border: 'none',
              borderRadius: '100px',
              minHeight: '44px',
              padding: '0 14px',
              cursor: 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
            }}
          >
            Clear
          </button>
        </div>
      </div>

      {/* Stats grid */}
      {stats && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: '1fr 1fr',
            gap: '12px',
          }}
        >
          <StatCard
            icon={<Flame size={14} style={{ color: '#b8860b' }} />}
            label={t.currentStreak}
            value={`${stats.current_streak} ${t.days}`}
          />
          <StatCard
            icon={<Flame size={14} style={{ color: '#8b4a3a' }} />}
            label={t.longestStreak}
            value={`${stats.longest_streak} ${t.days}`}
          />
          <StatCard
            icon={<BarChart3 size={14} style={{ color: '#3a5272' }} />}
            label={t.completionRate}
            value={stats.completion_rate_30d != null ? `${Math.round(stats.completion_rate_30d * 100)}%` : '\u2014'}
          />
          <StatCard
            icon={<Calendar size={14} style={{ color: '#3a5272' }} />}
            label={t.totalLogs}
            value={`${stats.total_logs}`}
          />
        </div>
      )}

      {/* 30-day streak chart */}
      {entries.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.6875rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: '#767d72',
            }}
          >
            {t.last30Days}
          </p>
          <HabitStreakChart entries={entries} />
        </div>
      )}

      {/* Yearly heatmap */}
      {heatmapEntries.length > 0 && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.6875rem',
              fontWeight: 700,
              textTransform: 'uppercase',
              letterSpacing: '0.05em',
              color: '#767d72',
            }}
          >
            {t.yearlyHeatmap}
          </p>
          <div style={{ overflowX: 'auto' }}>
            <HabitHeatmap entries={heatmapEntries} year={currentYear} />
          </div>
        </div>
      )}
    </div>
  )
}

/* ── Small stat card ──────────────────────────────────────────── */

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div
      style={{
        background: '#eef3f9',
        borderRadius: '0 10px 10px 10px',
        padding: '14px',
        display: 'flex',
        flexDirection: 'column',
        gap: '6px',
      }}
    >
      <div className="flex items-center" style={{ gap: '6px' }}>
        {icon}
        <span
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.625rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.05em',
            color: '#767d72',
          }}
        >
          {label}
        </span>
      </div>
      <span
        style={{
          fontFamily: 'var(--font-serif), Georgia, serif',
          fontSize: '1.25rem',
          fontWeight: 400,
          color: '#2e342b',
          letterSpacing: '-0.03em',
        }}
      >
        {value}
      </span>
    </div>
  )
}
