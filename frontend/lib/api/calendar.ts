import { apiFetch, apiGet, apiPost } from './client'

export interface CalendarEvent {
  id: number
  title: string
  description: string | null
  start_time: string
  end_time: string | null
  all_day: boolean
  location: string | null
  source: string
  color: string | null
  is_private: boolean
  tags: string[]
  duration_minutes: number | null
  created_at: string
}

export interface CreateEventInput {
  title: string
  description?: string | null
  start_time: string
  end_time?: string | null
  all_day?: boolean
  location?: string | null
  tags?: string[]
}

export interface UpdateEventInput {
  title?: string
  description?: string | null
  start_time?: string
  end_time?: string | null
  all_day?: boolean
  location?: string | null
  tags?: string[]
}

interface EventListResponse { ok: boolean; events: CalendarEvent[] }
interface EventResponse { ok: boolean; event: CalendarEvent }

export const calendarApi = {
  list: (limit = 50, offset = 0) =>
    apiGet<EventListResponse>(`/api/calendar/events?limit=${limit}&offset=${offset}`),

  get: (id: number) =>
    apiGet<EventResponse>(`/api/calendar/events/${id}`),

  create: (data: CreateEventInput) =>
    apiPost<EventResponse>('/api/calendar/events', data),

  update: (id: number, data: UpdateEventInput) =>
    apiFetch<EventResponse>(`/api/calendar/events/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    apiFetch<{ ok: boolean }>(`/api/calendar/events/${id}`, { method: 'DELETE' }),
}
