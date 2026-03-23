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
  step_id: number | null
  notes: string | null
  practiced_at: string
}

export type SkillGoalType = 'hours' | 'sessions' | 'milestones' | 'benchmark' | 'deadline'
export type SkillProgressState = 'on_track' | 'at_risk' | 'completed'

export interface SkillGoalEndpoint {
  goal_type: SkillGoalType
  target_value: number
  current_value: number
  progress_ratio: number
  deadline: string | null
}

export interface SkillOverviewCard {
  skill_id: number
  name: string
  category: string | null
  total_minutes: number
  session_count: number
  progress_state: SkillProgressState
  goal: SkillGoalEndpoint | null
  primary_action: 'continue_practice'
  requires_goal_setup: boolean
  risk_reason: 'no_recent_sessions' | null
}

export type SkillPathStepStatus = 'ready' | 'recommended' | 'blocked' | 'completed'
export type SkillPathStepAction = 'continue_practice' | 'setup_goal' | 'review_goal'

export interface SkillPathStep {
  step_id: string
  label: string
  status: SkillPathStepStatus
  action: SkillPathStepAction
}

export interface SkillPath {
  skill_id: number
  progress_state: SkillProgressState
  risk_reason: 'no_recent_sessions' | null
  goal: SkillGoalEndpoint | null
  steps: SkillPathStep[]
  next_recommended_step?: SkillPathStep | null
}

export type SkillForecastState = 'on_track' | 'at_risk' | 'completed' | 'insufficient_data'
export type SkillForecastRiskReason =
  | 'no_recent_sessions'
  | 'no_goal_configured'
  | 'insufficient_history'
  | 'non_projectable_goal_type'
  | null

export interface SkillForecastBaseline {
  avg_daily_minutes_last_14: number
  sessions_last_14: number
  total_minutes_last_14: number
}

export interface SkillForecastProjection {
  projected_minutes_next_window: number
  projected_sessions_next_window: number
  projected_goal_progress_ratio: number | null
}

export interface SkillForecast {
  skill_id: number
  horizon_days: number
  forecast_state: SkillForecastState
  risk_reason: SkillForecastRiskReason
  goal: SkillGoalEndpoint | null
  baseline: SkillForecastBaseline
  projection: SkillForecastProjection
}

export interface CreateSkillInput {
  name: string
  category?: string | null
  difficulty?: string | null
  goal_type?: SkillGoalType | null
  goal_target_value?: number | null
  goal_deadline?: string | null
  target_level?: number | null
  current_level?: number | null
  description?: string | null
  tags?: string[]
}

export interface LogPracticeInput {
  duration_minutes: number
  intensity?: number | null
  step_id?: number | null
  notes?: string | null
  practiced_at?: string | null
}

interface SkillListResponse { ok: boolean; skills: Skill[] }
interface SkillResponse { ok: boolean; skill: Skill }
interface SkillOverviewResponse {
  ok: boolean
  summary?: {
    total_hours: number
    total_sessions: number
    at_risk: number
    active: number
  }
  groups?: {
    at_risk: SkillOverviewCard[]
    on_track: SkillOverviewCard[]
    completed: SkillOverviewCard[]
  }
  skills: SkillOverviewCard[]
}
interface SkillPathResponse { ok: boolean; path: SkillPath }
interface SkillForecastResponse { ok: boolean; forecast: SkillForecast }

export const skillsApi = {
  list: () => apiGet<SkillListResponse>('/api/skills'),

  overview: () => apiGet<SkillOverviewResponse>('/api/skills/overview'),

  get: (id: number) => apiGet<SkillResponse>(`/api/skills/${id}`),

  path: (id: number) => apiGet<SkillPathResponse>(`/api/skills/${id}/path`),

  forecast: (id: number, horizonDays = 7) =>
    apiGet<SkillForecastResponse>(`/api/skills/${id}/forecast?horizon_days=${horizonDays}`),

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
    apiPost<{ ok: boolean; session: PracticeSession; next_recommended_step?: SkillPathStep | null }>(
      `/api/skills/${skillId}/practice`,
      data,
    ),

  deleteSession: (sessionId: number) =>
    apiFetch<{ ok: boolean }>(`/api/skills/practice/${sessionId}`, { method: 'DELETE' }),
}
