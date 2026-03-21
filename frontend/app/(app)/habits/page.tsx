'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { habitsApi, type Habit, type CreateHabitInput } from '@/lib/api/habits'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import { Input } from '@/components/ui/input'
import { Repeat, Plus, X, Trash2, CheckCircle2 } from 'lucide-react'

const microLabel: React.CSSProperties = {
  fontFamily: 'var(--font-manrope), sans-serif',
  fontSize: '0.6875rem',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.05em',
  color: '#767d72',
}

const inputStyle: React.CSSProperties = {
  fontFamily: 'var(--font-manrope), sans-serif',
  fontSize: '0.875rem',
  color: '#2e342b',
  background: '#ffffff',
  border: '1px solid rgba(173, 180, 168, 0.20)',
  borderRadius: '4px',
  padding: '10px 14px',
  outline: 'none',
  width: '100%',
}

export default function HabitsPage() {
  const [lang] = useLang()
  const t = getAppTranslations(lang).habits
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [scheduleType, setScheduleType] = useState('daily')

  const { data, isLoading } = useQuery({
    queryKey: ['habits'],
    queryFn: () => habitsApi.list(),
  })

  const createMut = useMutation({
    mutationFn: (input: CreateHabitInput) => habitsApi.create(input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['habits'] })
      setShowForm(false)
      setName('')
      setDescription('')
    },
  })

  const logMut = useMutation({
    mutationFn: (habitId: number) => habitsApi.log(habitId, {}),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['habits'] }),
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => habitsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['habits'] }),
  })

  const habits = data?.habits ?? []

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    createMut.mutate({
      name: name.trim(),
      description: description.trim() || undefined,
      schedule_type: scheduleType,
    })
  }

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <p
            className="text-xs font-bold uppercase mb-2"
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              letterSpacing: '0.05em',
              color: '#3a5272',
            }}
          >
            {t.eyebrow}
          </p>
          <h1
            style={{
              fontFamily: 'var(--font-serif), Georgia, serif',
              fontSize: '2rem',
              fontWeight: 300,
              color: '#3a5272',
              letterSpacing: '-0.03em',
            }}
          >
            {t.title}
          </h1>
          <p
            className="mt-2"
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.9375rem',
              color: '#5a6157',
              lineHeight: 1.65,
            }}
          >
            {t.subtitle}
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontWeight: 700,
            fontSize: '0.8125rem',
            color: '#ffffff',
            background: 'linear-gradient(135deg, #3a5272, #2e4460)',
            borderRadius: '100px',
            padding: '10px 20px',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
          }}
        >
          {showForm ? <><X size={14} /> {t.cancel}</> : <><Plus size={14} /> {t.newHabit}</>}
        </button>
      </div>

      {/* Create form */}
      {showForm && (
        <form
          onSubmit={handleCreate}
          className="p-5 sm:p-7 space-y-5"
          style={{
            background: '#ffffff',
            borderRadius: '0 16px 16px 16px',
            boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
          }}
        >
          <h2
            style={{
              fontFamily: 'var(--font-serif), Georgia, serif',
              fontSize: '1.125rem',
              fontWeight: 400,
              color: '#3a5272',
              letterSpacing: '-0.03em',
            }}
          >
            {t.newHabit}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="h-name" style={microLabel}>{t.name}</label>
              <input id="h-name" required value={name} onChange={(e) => setName(e.target.value)} placeholder={t.namePlaceholder} style={inputStyle} />
            </div>
            <div className="space-y-2">
              <label htmlFor="h-sched" style={microLabel}>{t.schedule}</label>
              <select
                id="h-sched"
                value={scheduleType}
                onChange={(e) => setScheduleType(e.target.value)}
                style={{
                  ...inputStyle,
                  appearance: 'none' as const,
                  backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 24 24' fill='none' stroke='%23767d72' stroke-width='2'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E")`,
                  backgroundRepeat: 'no-repeat',
                  backgroundPosition: 'right 14px center',
                  paddingRight: '36px',
                }}
              >
                <option value="daily">{t.daily}</option>
                <option value="weekly">{t.weekly}</option>
                <option value="custom">{t.custom}</option>
              </select>
            </div>
          </div>
          <div className="space-y-2">
            <label htmlFor="h-desc" style={microLabel}>{t.description}</label>
            <input id="h-desc" value={description} onChange={(e) => setDescription(e.target.value)} placeholder={t.optional} style={inputStyle} />
          </div>
          <button
            type="submit"
            disabled={createMut.isPending}
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontWeight: 700,
              fontSize: '0.875rem',
              color: '#ffffff',
              background: 'linear-gradient(135deg, #3a5272, #2e4460)',
              borderRadius: '100px',
              padding: '12px 28px',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
            }}
          >
            {createMut.isPending ? t.creating : t.createHabit}
          </button>
        </form>
      )}

      {/* Habits list */}
      <div
        className="p-7 space-y-5"
        style={{
          background: '#ffffff',
          borderRadius: '0 16px 16px 16px',
          boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
        }}
      >
        <h2
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '1.125rem',
            fontWeight: 400,
            color: '#3a5272',
            letterSpacing: '-0.03em',
          }}
        >
          {t.yourHabits}
        </h2>
        {isLoading && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="h-14 rounded-xl animate-pulse" style={{ background: '#e4edf5' }} />)}
          </div>
        )}
        {!isLoading && habits.length === 0 && (
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
            {t.noHabits}
          </p>
        )}
        {habits.length > 0 && (
          <ul className="space-y-3">
            {habits.map((h: Habit) => (
              <li
                key={h.id}
                className="px-5 py-4 flex items-start justify-between gap-4 transition-all duration-220 card-lift"
                style={{
                  borderRadius: '0 12px 12px 12px',
                  background: '#f8faf2',
                }}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b' }}>
                      {h.name}
                    </p>
                    {h.completed_today && (
                      <span
                        className="flex items-center gap-1 px-2 py-0.5"
                        style={{
                          background: '#d6e8ce',
                          color: '#465642',
                          borderRadius: '100px',
                          fontSize: '0.625rem',
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        <CheckCircle2 size={10} /> {t.done}
                      </span>
                    )}
                  </div>
                  <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
                    <span className="flex items-center gap-1"><Repeat size={11} /> {h.schedule_type}</span>
                    <span>{h.count} {t.logged}</span>
                    {h.last_logged_date && <span>last {h.last_logged_date}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => logMut.mutate(h.id)}
                    disabled={h.completed_today || logMut.isPending}
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.6875rem',
                      fontWeight: 700,
                      textTransform: 'uppercase' as const,
                      letterSpacing: '0.05em',
                      padding: '6px 14px',
                      borderRadius: '100px',
                      border: 'none',
                      cursor: h.completed_today ? 'default' : 'pointer',
                      color: h.completed_today ? '#adb4a8' : '#ffffff',
                      background: h.completed_today ? '#e5eade' : 'linear-gradient(135deg, #3a5272, #2e4460)',
                      boxShadow: h.completed_today ? 'none' : '0 4px 12px rgba(46, 52, 43, 0.15)',
                      opacity: h.completed_today ? 0.6 : 1,
                    }}
                  >
                    {t.log}
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteMut.mutate(h.id)}
                    className="transition-all duration-200"
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      color: '#adb4a8',
                      padding: '6px',
                      borderRadius: '100px',
                    }}
                    onMouseEnter={(e) => { e.currentTarget.style.color = '#e8735c'; e.currentTarget.style.background = 'rgba(232, 115, 92, 0.08)' }}
                    onMouseLeave={(e) => { e.currentTarget.style.color = '#adb4a8'; e.currentTarget.style.background = 'none' }}
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
