'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { habitsApi, type Habit, type CreateHabitInput } from '@/lib/api/habits'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

export default function HabitsPage() {
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
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Habits</h1>
          <p className="text-sm text-muted-foreground mt-1.5">Track daily habits to build inquiry data.</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'New Habit'}
        </Button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="glass rounded-2xl p-6 space-y-4">
          <h2 className="font-semibold text-foreground">Create Habit</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="h-name">Name</Label>
              <Input id="h-name" required value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Morning run" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="h-sched">Schedule</Label>
              <select
                id="h-sched"
                value={scheduleType}
                onChange={(e) => setScheduleType(e.target.value)}
                className="w-full rounded-xl border border-white/40 bg-white/50 backdrop-blur-sm px-3.5 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-ring/30"
              >
                <option value="daily">Daily</option>
                <option value="weekly">Weekly</option>
                <option value="custom">Custom</option>
              </select>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="h-desc">Description</Label>
            <Input id="h-desc" value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Optional" />
          </div>
          <Button type="submit" disabled={createMut.isPending}>
            {createMut.isPending ? 'Creating…' : 'Create Habit'}
          </Button>
        </form>
      )}

      <div className="glass rounded-2xl p-6 space-y-4">
        <h2 className="font-semibold text-foreground">Your Habits</h2>
        {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
        {!isLoading && habits.length === 0 && (
          <p className="text-sm text-muted-foreground">No habits yet. Create your first habit above.</p>
        )}
        {habits.length > 0 && (
          <ul className="space-y-2.5">
            {habits.map((h: Habit) => (
              <li key={h.id} className="rounded-xl bg-white/30 hover:bg-white/50 transition-all px-5 py-4 flex items-center justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium text-foreground">{h.name}</p>
                    {h.completed_today && (
                      <span className="text-xs bg-green-50/80 text-green-700 px-2 py-0.5 rounded-full">Done today</span>
                    )}
                  </div>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {h.schedule_type} · {h.count} logged
                    {h.last_logged_date && ` · last ${h.last_logged_date}`}
                  </p>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => logMut.mutate(h.id)}
                    disabled={h.completed_today || logMut.isPending}
                    className="text-xs px-3.5 py-1.5 rounded-full bg-primary text-primary-foreground hover:bg-primary/85 disabled:opacity-40 transition-all"
                  >
                    Log
                  </button>
                  <button
                    type="button"
                    onClick={() => deleteMut.mutate(h.id)}
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
