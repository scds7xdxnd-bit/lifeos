'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  skillsApi,
  type CreateSkillInput,
  type SkillOverviewCard,
} from '@/lib/api/skills'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import { Input } from '@/components/ui/input'
import { Plus, X, Trash2, Clock, Play } from 'lucide-react'

function fmtMinutes(m: number) {
  if (m < 60) return `${m}m`
  const h = Math.floor(m / 60)
  const rem = m % 60
  return rem ? `${h}h ${rem}m` : `${h}h`
}

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

export default function SkillsPage() {
  const [lang] = useLang()
  const t = getAppTranslations(lang).skills
  const qc = useQueryClient()
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [createStep, setCreateStep] = useState<1 | 2>(1)
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')
  const [goalType, setGoalType] = useState<'sessions' | 'hours' | 'milestones'>('sessions')
  const [goalTarget, setGoalTarget] = useState('12')

  const [practiceSkillId, setPracticeSkillId] = useState<number | null>(null)
  const [duration, setDuration] = useState('30')
  const [practiceNotes, setPracticeNotes] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['skills'],
    queryFn: () => skillsApi.list(),
  })

  const { data: overviewData, isLoading: isOverviewLoading } = useQuery({
    queryKey: ['skills', 'overview'],
    queryFn: () => skillsApi.overview(),
    retry: false,
  })

  const createMut = useMutation({
    mutationFn: (input: CreateSkillInput) => skillsApi.create(input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['skills'] })
      qc.invalidateQueries({ queryKey: ['skills', 'overview'] })
      setShowCreateModal(false)
      setCreateStep(1)
      setName('')
      setCategory('')
      setDescription('')
      setGoalType('sessions')
      setGoalTarget('12')
    },
  })

  const practiceMut = useMutation({
    mutationFn: ({ skillId, mins, notes }: { skillId: number; mins: number; notes: string }) =>
      skillsApi.logPractice(skillId, { duration_minutes: mins, notes: notes || undefined }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['skills'] })
      qc.invalidateQueries({ queryKey: ['skills', 'overview'] })
      setPracticeSkillId(null)
      setDuration('30')
      setPracticeNotes('')
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => skillsApi.delete(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['skills'] })
      qc.invalidateQueries({ queryKey: ['skills', 'overview'] })
    },
  })

  const skills = data?.skills ?? []
  const hasOverviewPayload = Array.isArray(overviewData?.skills)
  const cards: SkillOverviewCard[] = hasOverviewPayload
    ? (overviewData?.skills ?? [])
    : skills.map((s) => ({
        skill_id: s.id,
        name: s.name,
        category: s.category,
        total_minutes: s.total_minutes,
        session_count: s.session_count,
        progress_state: s.streak_days > 0 ? 'on_track' : 'at_risk',
        goal: null,
        primary_action: 'continue_practice',
        requires_goal_setup: true,
        risk_reason: s.streak_days > 0 ? null : 'no_recent_sessions',
      }))

  const summary = overviewData?.summary ?? {
    total_hours: Number((cards.reduce((acc, c) => acc + c.total_minutes, 0) / 60).toFixed(1)),
    total_sessions: cards.reduce((acc, c) => acc + c.session_count, 0),
    at_risk: cards.filter((c) => c.progress_state === 'at_risk').length,
    active: cards.length,
  }
  const showMigrationBanner = hasOverviewPayload && cards.some((c) => c.requires_goal_setup)

  const skillNameById = new Map(skills.map((s) => [s.id, s.name]))
  for (const c of cards) {
    if (!skillNameById.has(c.skill_id)) {
      skillNameById.set(c.skill_id, c.name)
    }
  }

  function stateChip(card: SkillOverviewCard): { label: string; bg: string; fg: string } {
    if (card.progress_state === 'completed') {
      return { label: 'Completed', bg: '#d6e8ce', fg: '#465642' }
    }
    if (card.progress_state === 'at_risk') {
      return { label: 'At Risk', bg: '#fce8e4', fg: '#8b4a3a' }
    }
    return { label: 'On Track', bg: '#e8f0e3', fg: '#3a5c35' }
  }

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    const targetValue = parseInt(goalTarget)
    if (!targetValue || targetValue <= 0) return

    createMut.mutate({
      name: name.trim(),
      category: category.trim() || undefined,
      description: description.trim() || undefined,
      goal_type: goalType,
      goal_target_value: targetValue,
    })
  }

  function handlePractice(e: React.FormEvent) {
    e.preventDefault()
    const mins = parseInt(duration)
    if (!practiceSkillId || !mins || mins <= 0) return
    practiceMut.mutate({ skillId: practiceSkillId, mins, notes: practiceNotes.trim() })
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
              color: '#6b5a35',
            }}
          >
            {t.eyebrow}
          </p>
          <h1
            style={{
              fontFamily: 'var(--font-serif), Georgia, serif',
              fontSize: '2rem',
              fontWeight: 300,
              color: '#6b5a35',
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
          onClick={() => {
            setCreateStep(1)
            setShowCreateModal(true)
          }}
          className="flex items-center gap-2"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontWeight: 700,
            fontSize: '0.8125rem',
            color: '#ffffff',
            background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
            borderRadius: '100px',
            padding: '10px 20px',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
          }}
        >
          <><Plus size={14} /> {t.newSkill}</>
        </button>
      </div>

      <section
        className="grid grid-cols-2 md:grid-cols-4 gap-3"
        aria-label="Skills summary"
      >
        {[
          { label: 'Total Hours', value: summary.total_hours.toFixed(1) },
          { label: 'Sessions', value: summary.total_sessions.toString() },
          { label: 'At Risk', value: summary.at_risk.toString() },
          { label: 'Active', value: summary.active.toString() },
        ].map((item) => (
          <article
            key={item.label}
            className="p-4"
            style={{
              background: '#ffffff',
              borderRadius: '0 14px 14px 14px',
              boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
            }}
          >
            <p style={microLabel}>{item.label}</p>
            <p
              style={{
                fontFamily: 'var(--font-serif), Georgia, serif',
                fontSize: '1.4rem',
                color: '#6b5a35',
                letterSpacing: '-0.03em',
              }}
            >
              {item.value}
            </p>
          </article>
        ))}
      </section>

      {showMigrationBanner && (
        <aside
          className="p-4"
          role="status"
          style={{
            background: '#f5f0e4',
            borderRadius: '0 14px 14px 14px',
            color: '#6b5a35',
          }}
        >
          <p style={microLabel}>Migration Notice</p>
          <p
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontSize: '0.875rem',
              lineHeight: 1.5,
            }}
          >
            Existing skills were preserved with safe defaults. You can refine any goal endpoint from each skill path.
          </p>
        </aside>
      )}

      {/* Create modal */}
      {showCreateModal && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center p-4"
          style={{
            background: 'rgba(26, 31, 26, 0.35)',
            backdropFilter: 'blur(6px)',
          }}
        >
          <form
            onSubmit={handleCreate}
            className="w-full max-w-xl p-6 space-y-5"
            style={{
              background: '#ffffff',
              borderRadius: '0 16px 16px 16px',
              boxShadow: '0 30px 60px rgba(46, 52, 43, 0.08)',
            }}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <p style={microLabel}>Step {createStep} of 2</p>
                <h2
                  style={{
                    fontFamily: 'var(--font-serif), Georgia, serif',
                    fontSize: '1.2rem',
                    color: '#6b5a35',
                    letterSpacing: '-0.03em',
                  }}
                >
                  {createStep === 1 ? 'Skill Basics' : 'Goal Endpoint'}
                </h2>
              </div>
              <button
                type="button"
                onClick={() => setShowCreateModal(false)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#767d72' }}
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>

            {createStep === 1 && (
              <>
                <div className="space-y-2">
                  <label htmlFor="sk-name" style={microLabel}>{t.name}</label>
                  <input id="sk-name" required value={name} onChange={(e) => setName(e.target.value)} placeholder={t.namePlaceholder} style={inputStyle} />
                </div>
                <div className="space-y-2">
                  <label htmlFor="sk-cat" style={microLabel}>{t.category}</label>
                  <input id="sk-cat" value={category} onChange={(e) => setCategory(e.target.value)} placeholder={t.categoryPlaceholder} style={inputStyle} />
                </div>
                <div className="space-y-2">
                  <label htmlFor="sk-desc" style={microLabel}>{t.description}</label>
                  <input id="sk-desc" value={description} onChange={(e) => setDescription(e.target.value)} placeholder={t.optional} style={inputStyle} />
                </div>
                <button
                  type="button"
                  onClick={() => {
                    if (!name.trim()) return
                    setCreateStep(2)
                  }}
                  style={{
                    fontFamily: 'var(--font-manrope), sans-serif',
                    fontWeight: 700,
                    fontSize: '0.875rem',
                    color: '#ffffff',
                    background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                    borderRadius: '100px',
                    padding: '12px 28px',
                    border: 'none',
                    cursor: 'pointer',
                    boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
                  }}
                >
                  Continue
                </button>
              </>
            )}

            {createStep === 2 && (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label htmlFor="sk-goal-type" style={microLabel}>Goal Type</label>
                    <select
                      id="sk-goal-type"
                      value={goalType}
                      onChange={(e) => setGoalType(e.target.value as 'sessions' | 'hours' | 'milestones')}
                      style={inputStyle}
                    >
                      <option value="sessions">Sessions</option>
                      <option value="hours">Hours</option>
                      <option value="milestones">Milestones</option>
                    </select>
                  </div>
                  <div className="space-y-2">
                    <label htmlFor="sk-goal-target" style={microLabel}>Target Value</label>
                    <Input
                      id="sk-goal-target"
                      type="number"
                      min="1"
                      required
                      value={goalTarget}
                      onChange={(e) => setGoalTarget(e.target.value)}
                    />
                  </div>
                </div>

                <div className="flex gap-3">
                  <button
                    type="button"
                    onClick={() => setCreateStep(1)}
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontWeight: 700,
                      fontSize: '0.8125rem',
                      textTransform: 'uppercase' as const,
                      letterSpacing: '0.05em',
                      color: '#767d72',
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: '12px 20px',
                      borderRadius: '100px',
                    }}
                  >
                    Back
                  </button>
                  <button
                    type="submit"
                    disabled={createMut.isPending}
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontWeight: 700,
                      fontSize: '0.875rem',
                      color: '#ffffff',
                      background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                      borderRadius: '100px',
                      padding: '12px 28px',
                      border: 'none',
                      cursor: 'pointer',
                      boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
                    }}
                  >
                    {createMut.isPending ? t.creating : t.createSkill}
                  </button>
                </div>
              </>
            )}
          </form>
        </div>
      )}

      {/* Practice modal */}
      {practiceSkillId && (
        <div
          className="fixed inset-0 z-40 flex items-center justify-center p-4"
          style={{
            background: 'rgba(26, 31, 26, 0.35)',
            backdropFilter: 'blur(6px)',
          }}
        >
          <form
            onSubmit={handlePractice}
            className="w-full max-w-xl p-6 space-y-5"
            style={{
              background: '#ffffff',
              borderRadius: '0 16px 16px 16px',
              boxShadow: '0 30px 60px rgba(46, 52, 43, 0.08)',
            }}
          >
            <div className="flex items-start justify-between gap-3">
              <h2
                style={{
                  fontFamily: 'var(--font-serif), Georgia, serif',
                  fontSize: '1.125rem',
                  fontWeight: 400,
                  color: '#6b5a35',
                  letterSpacing: '-0.03em',
                }}
              >
                Continue Practice - {skillNameById.get(practiceSkillId) ?? ''}
              </h2>
              <button
                type="button"
                onClick={() => setPracticeSkillId(null)}
                style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#767d72' }}
                aria-label="Close"
              >
                <X size={18} />
              </button>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-2">
                <label htmlFor="pr-dur" style={microLabel}>{t.durationLabel}</label>
                <Input id="pr-dur" type="number" min="1" required value={duration} onChange={(e) => setDuration(e.target.value)} />
              </div>
              <div className="space-y-2">
                <label htmlFor="pr-notes" style={microLabel}>{t.notes}</label>
                <input id="pr-notes" value={practiceNotes} onChange={(e) => setPracticeNotes(e.target.value)} placeholder={t.optional} style={inputStyle} />
              </div>
            </div>

            <div className="flex gap-3">
              <button
                type="submit"
                disabled={practiceMut.isPending}
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontWeight: 700,
                  fontSize: '0.875rem',
                  color: '#ffffff',
                  background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                  borderRadius: '100px',
                  padding: '12px 28px',
                  border: 'none',
                  cursor: 'pointer',
                  boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
                }}
              >
                {practiceMut.isPending ? t.logging : 'Continue Practice'}
              </button>
              <button
                type="button"
                onClick={() => setPracticeSkillId(null)}
                style={{
                  fontFamily: 'var(--font-manrope), sans-serif',
                  fontWeight: 700,
                  fontSize: '0.8125rem',
                  textTransform: 'uppercase' as const,
                  letterSpacing: '0.05em',
                  color: '#767d72',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  padding: '12px 20px',
                  borderRadius: '100px',
                }}
              >
                {t.cancel}
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Skills list */}
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
            color: '#6b5a35',
            letterSpacing: '-0.03em',
          }}
        >
          {t.yourSkills}
        </h2>
        {(isLoading || isOverviewLoading) && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="h-14 rounded-xl animate-pulse" style={{ background: '#f5f0e4' }} />)}
          </div>
        )}
        {!isLoading && !isOverviewLoading && cards.length === 0 && (
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
            {t.noSkills}
          </p>
        )}
        {cards.length > 0 && (
          <ul className="space-y-3">
            {cards.map((card) => {
              const chip = stateChip(card)
              const progressRatio = Math.max(0, Math.min(1, card.goal?.progress_ratio ?? 0))
              return (
              <li
                key={card.skill_id}
                className="px-5 py-4 flex items-start justify-between gap-4 transition-all duration-220 card-lift"
                style={{
                  borderRadius: '0 12px 12px 12px',
                  background: '#f8faf2',
                }}
              >
                <div className="min-w-0 flex-1">
                  <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b' }}>
                    {card.name}
                  </p>
                  <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
                    {card.category && (
                      <span
                        className="px-2 py-0.5"
                        style={{
                          background: '#f5f0e4',
                          color: '#6b5a35',
                          borderRadius: '100px',
                          fontSize: '0.625rem',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        {card.category}
                      </span>
                    )}
                    <span className="flex items-center gap-1"><Clock size={11} /> {fmtMinutes(card.total_minutes)}</span>
                    <span>{card.session_count} {t.sessions}</span>
                    <span
                      className="px-2 py-0.5"
                      style={{
                        background: chip.bg,
                        color: chip.fg,
                        borderRadius: '100px',
                        fontSize: '0.625rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '0.05em',
                      }}
                    >
                      {chip.label}
                    </span>
                  </div>
                  {card.goal && (
                    <div className="mt-3">
                      <div
                        style={{
                          fontFamily: 'var(--font-manrope), sans-serif',
                          fontSize: '0.6875rem',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                          color: '#767d72',
                        }}
                      >
                        Goal Progress
                      </div>
                      <div
                        className="mt-1"
                        style={{
                          height: '6px',
                          background: '#ebefe4',
                          borderRadius: '100px',
                          overflow: 'hidden',
                        }}
                      >
                        <div
                          style={{
                            width: `${Math.round(progressRatio * 100)}%`,
                            height: '100%',
                            background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                          }}
                        />
                      </div>
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => setPracticeSkillId(card.skill_id)}
                    className="flex items-center gap-1"
                    style={{
                      fontFamily: 'var(--font-manrope), sans-serif',
                      fontSize: '0.6875rem',
                      fontWeight: 700,
                      textTransform: 'uppercase' as const,
                      letterSpacing: '0.05em',
                      padding: '6px 14px',
                      borderRadius: '100px',
                      border: 'none',
                      cursor: 'pointer',
                      color: '#ffffff',
                      background: 'linear-gradient(135deg, #6b5a35, #5a4a2a)',
                      boxShadow: '0 4px 12px rgba(46, 52, 43, 0.15)',
                    }}
                  >
                    <Play size={10} /> Continue Practice
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteMut.mutate(card.skill_id)}
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
            )})}
          </ul>
        )}
      </div>
    </div>
  )
}
