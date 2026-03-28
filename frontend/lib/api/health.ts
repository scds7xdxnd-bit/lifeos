import { apiGet, apiPost } from './client'

export interface BiometricEntry {
  id: number
  date: string
  weight: number | null
  body_fat_pct: number | null
  resting_hr: number | null
  energy_level: number | null
  stress_level: number | null
  notes: string | null
  created_at: string | null
}

export interface WorkoutEntry {
  id: number
  date: string
  workout_type: string
  duration_minutes: number
  intensity: 'low' | 'medium' | 'high'
  calories_est: number | null
  notes: string | null
  created_at: string | null
}

export interface NutritionEntry {
  id: number
  date: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'other'
  items: string[]
  calories_est: number | null
  quality_score: number | null
  created_at: string | null
}

export interface DailySummary {
  date: string
  biometric: BiometricEntry | null
  workouts: { count: number; total_duration_minutes: number; by_type: Record<string, number> }
  nutrition: { count: number; calories_est_total: number }
  energy_level: number | null
  stress_level: number | null
}

export interface WeeklySummary {
  week_start: string
  week_end: string
  biometric: {
    average_weight: number | null
    average_resting_hr: number | null
    average_energy_level: number | null
    average_stress_level: number | null
  }
  workouts: { count: number; total_duration_minutes: number; by_type: Record<string, number> }
  nutrition: { count: number; calories_est_total: number }
}

export interface ListResponse<T> {
  ok: boolean
  items: T[]
  page: number
  pages: number
  total: number
}

export interface BiometricCreateInput {
  date?: string
  weight?: number
  body_fat_pct?: number
  resting_hr?: number
  energy_level?: number
  stress_level?: number
  notes?: string
}

export interface WorkoutCreateInput {
  date?: string
  workout_type: string
  duration_minutes?: number
  intensity?: 'low' | 'medium' | 'high'
  calories_est?: number
  notes?: string
}

export interface NutritionCreateInput {
  date?: string
  meal_type: 'breakfast' | 'lunch' | 'dinner' | 'snack' | 'other'
  items: string
  calories_est?: number
  quality_score?: number
}

interface ListParams {
  page?: number
  per_page?: number
  start_date?: string
  end_date?: string
}

function buildQs(params?: ListParams): string {
  if (!params) return ''
  const parts: string[] = []
  if (params.page != null) parts.push(`page=${params.page}`)
  if (params.per_page != null) parts.push(`per_page=${params.per_page}`)
  if (params.start_date) parts.push(`start_date=${params.start_date}`)
  if (params.end_date) parts.push(`end_date=${params.end_date}`)
  return parts.length ? `?${parts.join('&')}` : ''
}

export const healthApi = {
  listBiometrics: (params?: ListParams) =>
    apiGet<ListResponse<BiometricEntry>>(`/api/health/biometrics${buildQs(params)}`),

  createBiometric: (data: BiometricCreateInput) =>
    apiPost<{ ok: boolean; biometric: BiometricEntry }>('/api/health/biometrics', data),

  listWorkouts: (params?: ListParams) =>
    apiGet<ListResponse<WorkoutEntry>>(`/api/health/workouts${buildQs(params)}`),

  createWorkout: (data: WorkoutCreateInput) =>
    apiPost<{ ok: boolean; workout: WorkoutEntry }>('/api/health/workouts', data),

  listNutrition: (params?: ListParams) =>
    apiGet<ListResponse<NutritionEntry>>(`/api/health/nutrition${buildQs(params)}`),

  createNutrition: (data: NutritionCreateInput) =>
    apiPost<{ ok: boolean; nutrition: NutritionEntry }>('/api/health/nutrition', data),

  dailySummary: (date?: string) =>
    apiGet<{ ok: boolean; summary: DailySummary }>(
      `/api/health/summary/daily${date ? `?date=${date}` : ''}`
    ),

  weeklySummary: (start?: string) =>
    apiGet<{ ok: boolean; summary: WeeklySummary }>(
      `/api/health/summary/weekly${start ? `?start=${start}` : ''}`
    ),
}
