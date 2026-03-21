'use client'

import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { calendarApi, type CalendarEvent, type CreateEventInput } from '@/lib/api/calendar'
import { Input } from '@/components/ui/input'
import { Calendar, Plus, X, Trash2, MapPin, Clock } from 'lucide-react'

function fmtDate(iso: string) {
  try { return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }) } catch { return iso }
}
function fmtTime(iso: string) {
  try { return new Date(iso).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' }) } catch { return '' }
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
      {/* Page header */}
      <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
        <div>
          <p
            className="text-xs font-bold uppercase mb-2"
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              letterSpacing: '0.05em',
              color: '#4b6646',
            }}
          >
            Timeline
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
            Calendar
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
            Manage calendar events for inquiry analysis.
          </p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="flex items-center gap-2 btn-pill"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontWeight: 700,
            fontSize: '0.8125rem',
            color: '#ffffff',
            background: 'linear-gradient(135deg, #4b6646, #3f5a3a)',
            borderRadius: '100px',
            padding: '10px 20px',
            border: 'none',
            cursor: 'pointer',
            boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
          }}
        >
          {showForm ? <><X size={14} /> Cancel</> : <><Plus size={14} /> Add Event</>}
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
              color: '#4b6646',
              letterSpacing: '-0.03em',
            }}
          >
            New Event
          </h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="ev-title" style={microLabel}>Title</label>
              <input id="ev-title" required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Event title" style={inputStyle} />
            </div>
            <div className="space-y-2">
              <label htmlFor="ev-loc" style={microLabel}>Location</label>
              <input id="ev-loc" value={location} onChange={(e) => setLocation(e.target.value)} placeholder="Optional" style={inputStyle} />
            </div>
            <div className="space-y-2">
              <label htmlFor="ev-start" style={microLabel}>Start</label>
              <Input id="ev-start" type="datetime-local" required value={startTime} onChange={(e) => setStartTime(e.target.value)} />
            </div>
            <div className="space-y-2">
              <label htmlFor="ev-end" style={microLabel}>End</label>
              <Input id="ev-end" type="datetime-local" value={endTime} onChange={(e) => setEndTime(e.target.value)} />
            </div>
          </div>
          <label className="flex items-center gap-2.5 cursor-pointer">
            <input type="checkbox" checked={allDay} onChange={(e) => setAllDay(e.target.checked)} className="rounded" style={{ accentColor: '#4b6646' }} />
            <span style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', color: '#2e342b' }}>All day</span>
          </label>
          <button
            type="submit"
            disabled={createMut.isPending}
            className="btn-pill"
            style={{
              fontFamily: 'var(--font-manrope), sans-serif',
              fontWeight: 700,
              fontSize: '0.875rem',
              color: '#ffffff',
              background: 'linear-gradient(135deg, #4b6646, #3f5a3a)',
              borderRadius: '100px',
              padding: '12px 28px',
              border: 'none',
              cursor: 'pointer',
              boxShadow: '0 4px 20px rgba(46, 52, 43, 0.18)',
            }}
          >
            {createMut.isPending ? 'Saving…' : 'Save Event'}
          </button>
        </form>
      )}

      {/* Events list */}
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
            color: '#4b6646',
            letterSpacing: '-0.03em',
          }}
        >
          Events
        </h2>
        {isLoading && (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => <div key={i} className="h-14 rounded-xl animate-pulse" style={{ background: '#f1f5eb' }} />)}
          </div>
        )}
        {!isLoading && events.length === 0 && (
          <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
            No events yet. Add your first event above.
          </p>
        )}
        {events.length > 0 && (
          <ul className="space-y-3">
            {events.map((ev: CalendarEvent) => (
              <li
                key={ev.id}
                className="px-4 sm:px-5 py-4 flex items-start justify-between gap-3 sm:gap-4 transition-all duration-220 card-lift"
                style={{
                  borderRadius: '0 12px 12px 12px',
                  background: '#f8faf2',
                }}
              >
                <div className="min-w-0 flex-1">
                  <p style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b' }}>
                    {ev.title}
                  </p>
                  <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1" style={{ fontFamily: 'var(--font-manrope), sans-serif', fontSize: '0.75rem', color: '#767d72' }}>
                    <span className="flex items-center gap-1"><Clock size={11} /> {fmtDate(ev.start_time)} {!ev.all_day && fmtTime(ev.start_time)}{ev.end_time && ` → ${fmtTime(ev.end_time)}`}</span>
                    {ev.location && <span className="flex items-center gap-1"><MapPin size={11} /> {ev.location}</span>}
                    {ev.source !== 'manual' && (
                      <span
                        className="px-2 py-0.5"
                        style={{
                          background: '#d6e8ce',
                          color: '#465642',
                          borderRadius: '100px',
                          fontSize: '0.625rem',
                          fontWeight: 700,
                          textTransform: 'uppercase',
                          letterSpacing: '0.05em',
                        }}
                      >
                        {ev.source}
                      </span>
                    )}
                  </div>
                </div>
                <button
                  type="button"
                  onClick={() => deleteMut.mutate(ev.id)}
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
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
