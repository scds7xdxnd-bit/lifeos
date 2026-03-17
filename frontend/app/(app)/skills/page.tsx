'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { skillsApi, type Skill, type CreateSkillInput } from '@/lib/api/skills'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

function fmtMinutes(m: number) {
  if (m < 60) return `${m}m`
  const h = Math.floor(m / 60)
  const rem = m % 60
  return rem ? `${h}h ${rem}m` : `${h}h`
}

export default function SkillsPage() {
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
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Skills</h1>
          <p className="text-sm text-muted-foreground mt-1.5">Track skills and practice sessions for inquiry analysis.</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'New Skill'}
        </Button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="glass rounded-2xl p-6 space-y-4">
          <h2 className="font-semibold text-foreground">Create Skill</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="sk-name">Name</Label>
              <Input id="sk-name" required value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Piano" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="sk-cat">Category</Label>
              <Input id="sk-cat" value={category} onChange={(e) => setCategory(e.target.value)} placeholder="e.g. Music" />
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="sk-desc">Description</Label>
            <Input id="sk-desc" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional" />
          </div>
          <Button type="submit" disabled={createMut.isPending}>
            {createMut.isPending ? 'Creating…' : 'Create Skill'}
          </Button>
        </form>
      )}

      {/* Practice form */}
      {practiceSkillId && (
        <form onSubmit={handlePractice} className="glass rounded-2xl p-6 space-y-4">
          <h2 className="font-semibold text-foreground">
            Log Practice — {skills.find((s) => s.id === practiceSkillId)?.name}
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="pr-dur">Duration (minutes)</Label>
              <Input id="pr-dur" type="number" min="1" required value={duration} onChange={(e) => setDuration(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="pr-notes">Notes</Label>
              <Input id="pr-notes" value={practiceNotes} onChange={(e) => setPracticeNotes(e.target.value)} placeholder="Optional" />
            </div>
          </div>
          <div className="flex gap-2">
            <Button type="submit" disabled={practiceMut.isPending}>
              {practiceMut.isPending ? 'Logging…' : 'Log Session'}
            </Button>
            <Button type="button" variant="ghost" onClick={() => setPracticeSkillId(null)}>Cancel</Button>
          </div>
        </form>
      )}

      <div className="glass rounded-2xl p-6 space-y-4">
        <h2 className="font-semibold text-foreground">Your Skills</h2>
        {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
        {!isLoading && skills.length === 0 && (
          <p className="text-sm text-muted-foreground">No skills yet. Create your first skill above.</p>
        )}
        {skills.length > 0 && (
          <ul className="space-y-2.5">
            {skills.map((s: Skill) => (
              <li key={s.id} className="rounded-xl bg-white/30 hover:bg-white/50 transition-all px-5 py-4 flex items-center justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground">{s.name}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {s.category && `${s.category} · `}
                    {fmtMinutes(s.total_minutes)} total · {s.session_count} sessions
                    {s.streak_days > 0 && ` · ${s.streak_days}d streak`}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => setPracticeSkillId(s.id)}
                    className="text-xs px-3.5 py-1.5 rounded-full bg-primary text-primary-foreground hover:bg-primary/85 transition-all"
                  >
                    Practice
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteMut.mutate(s.id)}
                    className="text-xs px-3 py-1.5 rounded-full text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all"
                  >
                    Delete
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
