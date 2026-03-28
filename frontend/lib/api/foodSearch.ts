import { apiGet } from './client'

export interface FoodSearchResult {
  product_name: string
  brands: string | null
  calories_per_100g: number
  protein_per_100g: number
  carbohydrate_per_100g: number
  fat_per_100g: number
  fiber_per_100g: number | null
}

/**
 * Search for foods via the backend proxy to Open Food Facts.
 * Proxied server-side to avoid CORS; silently returns [] on any failure.
 *
 * @param query  Search term (min 3 chars). Can be in any language.
 * @param lang   App language code ('en' | 'ko' | 'zh'). Routes to the
 *               regional OFF database for better local product coverage.
 */
export async function searchFoodDatabase(
  query: string,
  lang = 'en',
): Promise<FoodSearchResult[]> {
  if (query.length < 3) return []
  try {
    const data = await apiGet<{ ok: boolean; products: FoodSearchResult[] }>(
      `/api/health/food-library/search?q=${encodeURIComponent(query)}&limit=8&lang=${encodeURIComponent(lang)}`
    )
    return data.products ?? []
  } catch {
    return []
  }
}
