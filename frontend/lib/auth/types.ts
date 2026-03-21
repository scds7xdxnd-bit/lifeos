export interface User {
  id: number
  email: string
  timezone?: string
  onboarding_completed?: boolean
}

export interface StoredTokens {
  access_token: string
  refresh_token: string
  csrf_token: string
}

export interface RegisterInput {
  email: string
  password: string
  timezone?: string
  invite_token?: string
}

/**
 * Stable auth interface — the implementation (Flask, Clerk, etc.) can be
 * swapped in AuthProvider without touching any consuming component.
 */
export interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<void>
  register: (data: RegisterInput) => Promise<void>
  logout: () => Promise<void>
  getAccessToken: () => string | null
  getCsrfToken: () => string | null
}
