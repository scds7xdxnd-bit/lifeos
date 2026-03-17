import { apiFetch, apiGet, apiPost } from './client'

export interface Habit {
  id: number
  name: string
  description: string | null
  schedule_type: string
  target_count: number | null
  time_of_day: string | null
  difficulty: string | null
  is_active: boolean
  count: number
  last_logged_date: string | null
  completed_today: boolean
}

export interface HabitLog {
  id: number
  habit_id: number
  logged_date: string
  value: number | null
  note: string | null
}

export interface HabitDetail extends Omit<Habit, 'count' | 'last_logged_date' | 'completed_today'> {
  stats: Record<string, unknown>
  logs: HabitLog[]
}

export interface CreateHabitInput {
  name: string
  description?: string | null
  schedule_type?: string
  target_count?: number | null
  time_of_day?: string | null
  difficulty?: string | null
}

export interface LogHabitInput {
  logged_date?: string | null
  value?: number | null
  note?: string | null
}

interface HabitListResponse { ok: boolean; habits: Habit[] }
interface HabitDetailResponse { ok: boolean; habit: HabitDetail }
interface HabitLogResponse { ok: boolean; log: HabitLog }

export const habitsApi = {
  list: () => apiGet<HabitListResponse>('/api/habits'),

  get: (id: number) => apiGet<HabitDetailResponse>(`/api/habits/${id}`),

  create: (data: CreateHabitInput) =>
    apiPost<{ ok: boolean; habit: Habit }>('/api/habits', data),

  update: (id: number, data: Partial<CreateHabitInput>) =>
    apiFetch<{ ok: boolean; habit: Habit }>(`/api/habits/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    apiFetch<{ ok: boolean }>(`/api/habits/${id}`, { method: 'DELETE' }),

  log: (habitId: number, data: LogHabitInput) =>
    apiPost<HabitLogResponse>(`/api/habits/${habitId}/logs`, data),

  deleteLog: (logId: number) =>
    apiFetch<{ ok: boolean }>(`/api/habits/logs/${logId}`, { method: 'DELETE' }),
}
