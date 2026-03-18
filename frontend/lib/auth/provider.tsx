'use client'

/**
 * Flask auth provider — wraps the existing /auth/* endpoints.
 *
 * To migrate to Clerk (or any other provider) later:
 *   1. Create lib/auth/clerk-provider.tsx with the same AuthContext.Provider shape
 *   2. Swap the import in app/providers.tsx
 *   3. Nothing else changes
 */

import { useCallback, useEffect, useState } from 'react'
import { AuthContext } from './context'
import type { RegisterInput, StoredTokens, User } from './types'

const STORAGE_KEY = 'lifeos_tokens'
const API_URL = process.env.NEXT_PUBLIC_API_URL ?? ''

function getStored(): StoredTokens | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as StoredTokens) : null
  } catch {
    return null
  }
}

function setStored(tokens: StoredTokens) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tokens))
}

function clearStored() {
  localStorage.removeItem(STORAGE_KEY)
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const tokens = getStored()
    if (!tokens) {
      // Prime CSRF token from bootstrap endpoint for unauthenticated requests
      fetch(`${API_URL}/api/bootstrap`, {
        credentials: 'include',
      })
        .then((r) => (r.ok ? r.json() : Promise.reject()))
        .then((data: { csrf_token: string }) => {
          setStored({
            access_token: '',
            refresh_token: '',
            csrf_token: data.csrf_token,
          })
        })
        .catch(() => {
          // Continue without CSRF token if bootstrap fails
        })
        .finally(() => setIsLoading(false))
      return
    }
    fetch(`${API_URL}/auth/me`, {
      headers: { Authorization: `Bearer ${tokens.access_token}` },
    })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then((data: { user: User }) => setUser(data.user))
      .catch(() => clearStored())
      .finally(() => setIsLoading(false))
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    const res = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.message ?? 'Login failed')
    setStored({
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      csrf_token: data.csrf_token,
    })
    setUser(data.user as User)
  }, [])

  const register = useCallback(async (input: RegisterInput) => {
    const res = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(input),
      credentials: 'include',  // Enable cross-origin cookies for CSRF validation
    })
    const data = await res.json()
    if (!res.ok) throw new Error(data.message ?? 'Registration failed')
    if (data.access_token) {
      setStored({
        access_token: data.access_token,
        refresh_token: data.refresh_token,
        csrf_token: data.csrf_token,
      })
      setUser(data.user as User)
    }
  }, [])

  const logout = useCallback(async () => {
    const tokens = getStored()
    clearStored()
    setUser(null)
    if (tokens?.refresh_token) {
      await fetch(`${API_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${tokens.refresh_token}`,
          'X-CSRF-Token': tokens.csrf_token,
          'Content-Type': 'application/json',
        },
      }).catch(() => {})
    }
  }, [])

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        getAccessToken: () => getStored()?.access_token ?? null,
        getCsrfToken: () => getStored()?.csrf_token ?? null,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
