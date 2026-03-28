import { apiFetch, apiGet, apiPost } from './client'

export interface FoodItem {
  id: number
  name: string
  cost_per_100g: number
  calories_per_100g: number
  protein_per_100g: number
  carbohydrate_per_100g: number
  fat_per_100g: number
  fiber_per_100g: number | null
  created_at: string
  updated_at: string | null
}

export interface FoodItemCreateInput {
  name: string
  cost_per_100g: number
  calories_per_100g: number
  protein_per_100g: number
  carbohydrate_per_100g: number
  fat_per_100g: number
  fiber_per_100g?: number
}

export interface FoodItemUpdateInput {
  name?: string
  cost_per_100g?: number
  calories_per_100g?: number
  protein_per_100g?: number
  carbohydrate_per_100g?: number
  fat_per_100g?: number
  fiber_per_100g?: number
}

export interface FoodLibraryListResponse {
  ok: boolean
  items: FoodItem[]
  page: number
  pages: number
  total: number
}

export const foodLibraryApi = {
  list: (page = 1, perPage = 200) =>
    apiGet<FoodLibraryListResponse>(
      `/api/health/food-library?page=${page}&per_page=${perPage}`
    ),

  get: (id: number) =>
    apiGet<{ ok: boolean; item: FoodItem }>(`/api/health/food-library/${id}`),

  create: (data: FoodItemCreateInput) =>
    apiPost<{ ok: boolean; item: FoodItem }>('/api/health/food-library', data),

  update: (id: number, data: FoodItemUpdateInput) =>
    apiFetch<{ ok: boolean; item: FoodItem }>(`/api/health/food-library/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),

  delete: (id: number) =>
    apiFetch<{ ok: boolean }>(`/api/health/food-library/${id}`, {
      method: 'DELETE',
    }),
}
