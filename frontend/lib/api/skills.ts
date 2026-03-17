import { apiFetch, apiGet, apiPost } from './client'

export interface Skill {
  id: number
  name: string
  category: string | null
  difficulty: string | null
  target_level: number | null
  current_level: number | null
  description: string | null
  tags: string[]
  total_minutes: number
  session_count: number
  last_practiced_at: string | null
  streak_days: number
  sessions_last_7: number
  sessions_last_30: number
  recent_sessions: PracticeSession[]
}

export interface PracticeSession {
  id: number
  skill_id: number
  duration_minutes: number
  intensity: number | null
  notes: string | null
  practiced_at: string
}

export interface CreateSkillInput {
  name: string
  category?: string | null
  difficulty?: string | null
  target_level?: number | null
  current_level?: number | null
  description?: string | null
  tags?: string[]
}

export interface LogPracticeInput {
  duration_minutes: number
  intensity?: number | null
  notes?: string | null
  practiced_at?: string | null
}

interface SkillListResponse { ok: boolean; skills: Skill[] }
interface SkillResponse { ok: boolean; skill: Skill }

export const skillsApi = {
  list: () => apiGet<SkillListResponse>('/api/skills'),

  get: (id: number) => apiGet<SkillResponse>(`/api/skills/${id}`),

  create: (data: CreateSkillInput) =>
    apiPost<SkillResponse>('/api/skills', data),

  update: (id: number, data: Partial<CreateSkillInput>) =>
    apiFetch<SkillResponse>(`/api/skills/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    apiFetch<{ ok: boolean }>(`/api/skills/${id}`, { method: 'DELETE' }),

  logPractice: (skillId: number, data: LogPracticeInput) =>
    apiPost<{ ok: boolean; session: PracticeSession }>(`/api/skills/${skillId}/practice`, data),

  deleteSession: (sessionId: number) =>
    apiFetch<{ ok: boolean }>(`/api/skills/practice/${sessionId}`, { method: 'DELETE' }),
}
