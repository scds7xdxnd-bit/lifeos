'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { skillsApi, type Skill, type CreateSkillInput } from '@/lib/api/skills'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import { Input } from '@/components/ui/input'
import { Lightbulb, Plus, X, Trash2, Clock, Play, Flame } from 'lucide-react'

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
  const [showForm, setShowForm] = useState(false)
  const [name, setName] = useState('')
  const [category, setCategory] = useState('')
  const [description, setDescription] = useState('')

  const [practiceSkillId, setPracticeSkillId] = useState<number | null>(null)
  const [duration, setDuration] = useState('30')
  const [practiceNotes, setPracticeNotes] = useState('')

  const { data, isLoading } = useQuery({
    queryKey: ['skills'],
    queryFn: () => skillsApi.list(),
  })

  const createMut = useMutation({
    mutationFn: (input: CreateSkillInput) => skillsApi.create(input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['skills'] })
      setShowForm(false)
      setName('')
      setCategory('')
      setDescription('')
    },
  })

  const practiceMut = useMutation({
    mutationFn: ({ skillId, mins, notes }: { skillId: number; mins: number; notes: string }) =>
      skillsApi.logPractice(skillId, { duration_minutes: mins, notes: notes || undefined }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['skills'] })
      setPracticeSkillId(null)
      setDuration('30')
      setPracticeNotes('')
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => skillsApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['skills'] }),
  })

  const skills = data?.skills ?? []

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!name.trim()) return
    createMut.mutate({
      name: name.trim(),
      category: category.trim() || undefined,
      description: description.trim() || undefined,
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
          onClick={() => setShowForm(!showForm)}
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
          {showForm ? <><X size={14} /> {t.cancel}</> : <><Plus size={14} /> {t.newSkill}</>}
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
              color: '#6b5a35',
              letterSpacing: '-0.03em',
            }}
          >
            {t.newSkill}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="sk-name" style={microLabel}>{t.name}</label>
              <input id="sk-name" required value={name} onChange={(e) => setName(e.target.value)} placeholder={t.namePlaceholder} style={inputStyle} />
            </div>
            <div className="space-y-2">
              <label htmlFor="sk-cat" style={microLabel}>{t.category}</label>
              <input id="sk-cat" value={category} onChange={(e) => setCategory(e.target.value)} placeholder={t.categoryPlaceholder} style={inputStyle} />
            </div>
          </div>
          <div className="space-y-2">
            <label htmlFor="sk-desc" style={microLabel}>{t.description}</label>
            <input id="sk-desc" value={description} onChange={(e) => setDescription(e.target.value)} placeholder={t.optional} style={inputStyle} />
          </div>
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
        </form>
      )}

      {/* Practice form */}
      {practiceSkillId && (
        <form
          onSubmit={handlePractice}
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
              color: '#6b5a35',
              letterSpacing: '-0.03em',
            }}
          >
            {t.logPractice} — {skills.find((s) => s.id === practiceSkillId)?.name}
          </h2>
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
              {practiceMut.isPending ? t.logging : t.logSession}
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
        {isLoading && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="h-14 rounded-xl animate-pulse" style={{ background: '#f5f0e4' }} />)}
          </div>
        )}
        {!isLoading && skills.length === 0 && (
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
            {t.noSkills}
          </p>
        )}
        {skills.length > 0 && (
          <ul className="space-y-3">
            {skills.map((s: Skill) => (
              <li
                key={s.id}
                className="px-5 py-4 flex items-start justify-between gap-4 transition-all duration-220 card-lift"
                style={{
                  borderRadius: '0 12px 12px 12px',
                  background: '#f8faf2',
                }}
              >
                <div className="min-w-0 flex-1">
                  <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b' }}>
                    {s.name}
                  </p>
                  <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
                    {s.category && (
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
                        {s.category}
                      </span>
                    )}
                    <span className="flex items-center gap-1"><Clock size={11} /> {fmtMinutes(s.total_minutes)}</span>
                    <span>{s.session_count} {t.sessions}</span>
                    {s.streak_days > 0 && <span className="flex items-center gap-1"><Flame size={11} /> {s.streak_days}{t.streak}</span>}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => setPracticeSkillId(s.id)}
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
                    <Play size={10} /> {t.practice}
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteMut.mutate(s.id)}
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
