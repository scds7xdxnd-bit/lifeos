'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { calendarApi, type CalendarEvent, type CreateEventInput } from '@/lib/api/calendar'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

function fmtDate(iso: string) {
  try { return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) } catch { return iso }
}
function fmtTime(iso: string) {
  try { return new Date(iso).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) } catch { return '' }
}

export default function CalendarPage() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [title, setTitle] = useState('')
  const [startTime, setStartTime] = useState('')
  const [endTime, setEndTime] = useState('')
  const [location, setLocation] = useState('')
  const [allDay, setAllDay] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['calendar-events'],
    queryFn: () => calendarApi.list(100),
  })

  const createMut = useMutation({
    mutationFn: (input: CreateEventInput) => calendarApi.create(input),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['calendar-events'] })
      setShowForm(false)
      setTitle('')
      setStartTime('')
      setEndTime('')
      setLocation('')
      setAllDay(false)
    },
  })

  const deleteMut = useMutation({
    mutationFn: (id: number) => calendarApi.delete(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['calendar-events'] }),
  })

  const events = data?.events ?? []

  function handleCreate(e: React.FormEvent) {
    e.preventDefault()
    if (!title.trim() || !startTime) return
    createMut.mutate({
      title: title.trim(),
      start_time: new Date(startTime).toISOString(),
      end_time: endTime ? new Date(endTime).toISOString() : undefined,
      location: location.trim() || undefined,
      all_day: allDay,
    })
  }

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Calendar</h1>
          <p className="text-sm text-muted-foreground mt-1.5">Manage calendar events for inquiry analysis.</p>
        </div>
        <Button onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Cancel' : 'Add Event'}
        </Button>
      </div>

      {showForm && (
        <form onSubmit={handleCreate} className="glass rounded-2xl p-6 space-y-4">
          <h2 className="font-semibold text-foreground">New Event</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="ev-title">Title</Label>
              <Input id="ev-title" required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Event title" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ev-loc">Location</Label>
              <Input id="ev-loc" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Optional" />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ev-start">Start</Label>
              <Input id="ev-start" type="datetime-local" required value={startTime} onChange={(e) => setStartTime(e.target.value)} />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ev-end">End</Label>
              <Input id="ev-end" type="datetime-local" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
            </div>
          </div>
          <label className="flex items-center gap-2.5 cursor-pointer">
            <input type="checkbox" checked={allDay} onChange={(e) => setAllDay(e.target.checked)} className="rounded-md" />
            <span className="text-sm">All day</span>
          </label>
          <Button type="submit" disabled={createMut.isPending}>
            {createMut.isPending ? 'Saving…' : 'Save Event'}
          </Button>
        </form>
      )}

      <div className="glass rounded-2xl p-6 space-y-4">
        <h2 className="font-semibold text-foreground">Events</h2>
        {isLoading && <p className="text-sm text-muted-foreground">Loading…</p>}
        {!isLoading && events.length === 0 && (
          <p className="text-sm text-muted-foreground">No events yet. Add your first event above.</p>
        )}
        {events.length > 0 && (
          <ul className="space-y-2">
            {events.map((ev: CalendarEvent) => (
              <li key={ev.id} className="rounded-xl bg-white/30 hover:bg-white/50 transition-all px-5 py-3.5 flex items-start justify-between gap-4">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground">{ev.title}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    {fmtDate(ev.start_time)} {!ev.all_day && fmtTime(ev.start_time)}
                    {ev.end_time && ` → ${fmtTime(ev.end_time)}`}
                    {ev.location && ` · ${ev.location}`}
                    {ev.source !== 'manual' && ` · ${ev.source}`}
                  </p>
                </div>
                <button
                  type="button"
                  onClick={() => deleteMut.mutate(ev.id)}
                  className="text-xs px-3 py-1.5 rounded-full text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-all"
                >
                  Delete
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
