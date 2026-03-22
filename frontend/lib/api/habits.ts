import { apiFetch, apiGet, apiPost } from './client'

export interface Habit {
  id: number
  name: string
  description: string | null
  schedule_type: string
  target_count: number | null
  time_of_day: string | null
  scheduled_time: string | null
  difficulty: string | null
  is_active: boolean
  count: number
  last_logged_date: string | null
  completed_today: boolean
  current_streak: number
  completion_rate_30d: number | null
  today_log_id: number | null
  last_7_days: Array<{ date: string; logged: boolean }>
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
  scheduled_time?: string | null
  difficulty?: string | null
}

export interface LogHabitInput {
  logged_date?: string | null
  value?: number | null
  note?: string | null
}

export interface HabitStats {
  current_streak: number
  longest_streak: number
  completion_rate_30d: number | null
  total_logs: number
  last_logged_at: string | null
}

export interface HabitHistoryEntry {
  date: string
  logged: boolean
  value: number | null
}

export interface HabitHeatmapEntry {
  date: string
  logged: boolean
}

interface HabitListResponse { ok: boolean; habits: Habit[] }
interface HabitDetailResponse { ok: boolean; habit: HabitDetail }
interface HabitLogResponse { ok: boolean; log: HabitLog }
interface HabitStatsResponse { ok: boolean; stats: HabitStats }
interface HabitHistoryResponse { ok: boolean; history: { entries: HabitHistoryEntry[]; range: string } }
interface HabitHeatmapResponse { ok: boolean; heatmap: { year: number; entries: HabitHeatmapEntry[] } }

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

  stats: (id: number) =>
    apiGet<HabitStatsResponse>(`/api/habits/${id}/stats`),

  history: (id: number, range: string = '30d') =>
    apiGet<HabitHistoryResponse>(`/api/habits/${id}/history?range=${range}`),

  heatmap: (id: number, year: number) =>
    apiGet<HabitHeatmapResponse>(`/api/habits/${id}/heatmap?year=${year}`),
}
