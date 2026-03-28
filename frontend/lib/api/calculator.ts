import { apiGet, apiPost, apiPatch, apiDelete } from '@/lib/api/client'

export interface CalorieReport {
  id: number
  weight_kg: number
  height_cm: number
  age_years: number
  gender: string
  body_fat_pct: number | null
  activity_level: string
  goal_type: string
  goal_weight_kg: number | null
  goal_timeline_months: number | null
  method_used: string
  lean_body_mass: number | null
  bmr: number
  activity_multiplier: number
  tdee: number
  delta_bw: number | null
  total_delta_kcal: number | null
  delta_kcal_per_day: number | null
  kcal_per_kg_used: number | null
  daily_calories: number
  protein_g_per_day: number
  fat_g_per_day: number
  carbs_g_per_day: number
  fiber_g_per_day: number
  monthly_calories: number
  monthly_protein_g: number
  monthly_fat_g: number
  monthly_carbs_g: number
  monthly_fiber_g: number
  created_at: string
}

export interface CalculatorInput {
  weight_kg: number
  height_cm: number
  age_years: number
  gender: 'male' | 'female'
  body_fat_pct?: number | null
  activity_level: string
  goal_type: 'lose' | 'gain' | 'maintain'
  goal_weight_kg?: number | null
  goal_timeline_months?: number | null
  save_profile?: boolean
}

export interface Warning {
  type: string
  message: string
}

export interface PrefillResponse {
  ok: boolean
  biometric: { weight_kg: number | null; body_fat_pct: number | null } | null
  profile: { height_cm: number; age_years: number; gender: string } | null
}

export const calculatorApi = {
  getPrefill: () =>
    apiGet<PrefillResponse>('/api/v1/health/calculator/prefill'),

  calculate: (data: CalculatorInput) =>
    apiPost<{ ok: boolean; report: CalorieReport; warnings: Warning[] }>(
      '/api/v1/health/calculator/calculate',
      data
    ),

  listReports: (params?: { page?: number; per_page?: number }) =>
    apiGet<{ ok: boolean; reports: CalorieReport[]; page: number; pages: number; total: number }>(
      `/api/v1/health/calculator/reports?page=${params?.page ?? 1}&per_page=${params?.per_page ?? 20}`
    ),

  getLatestReport: () =>
    apiGet<{ ok: boolean; report: CalorieReport | null }>(
      '/api/v1/health/calculator/reports/latest'
    ),

  getReport: (id: number) =>
    apiGet<{ ok: boolean; report: CalorieReport }>(
      `/api/v1/health/calculator/reports/${id}`
    ),

  updateReport: (id: number, data: CalculatorInput) =>
    apiPatch<{ ok: boolean; report: CalorieReport; warnings: Warning[] }>(
      `/api/v1/health/calculator/reports/${id}`,
      data
    ),

  deleteReport: (id: number) =>
    apiDelete<{ ok: boolean }>(`/api/v1/health/calculator/reports/${id}`),
}
