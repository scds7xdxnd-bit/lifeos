import { resolveApiUrl } from '@/lib/api/resolveApiUrl'

const STORAGE_KEY = 'lifeos_tokens'

const MUTATION_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

interface StoredTokens {
  access_token: string
  csrf_token: string
}

function getTokens(): StoredTokens | null {
  if (typeof window === 'undefined') return null
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const tokens = getTokens()
  const method = (options.method ?? 'GET').toUpperCase()

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(options.headers as Record<string, string>),
  }

  if (tokens?.access_token) {
    headers['Authorization'] = `Bearer ${tokens.access_token}`
  }
  if (tokens?.csrf_token && MUTATION_METHODS.has(method)) {
    headers['X-CSRF-Token'] = tokens.csrf_token
  }

  const res = await fetch(`${resolveApiUrl()}${path}`, {
    ...options,
    headers,
    // Explicitly omit cookies to prevent sending session cookies alongside JWT,
    // which triggers the backend's mixed-auth rejection (403).
    // Placed after ...options so callers can't accidentally re-enable cookies.
    credentials: 'omit',
  })

  if (res.status === 401) {
    if (typeof window !== 'undefined') {
      localStorage.removeItem(STORAGE_KEY)
      window.location.href = '/login'
    }
    throw new Error('Unauthorized')
  }

  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const err = data as { message?: string; error?: string }
    throw new Error(err.message ?? err.error ?? `API error ${res.status}`)
  }

  return data as T
}

export const apiGet = <T>(path: string) => apiFetch<T>(path)

export const apiPost = <T>(path: string, body: unknown) =>
  apiFetch<T>(path, { method: 'POST', body: JSON.stringify(body) })

export const apiPatch = <T>(path: string, body: unknown) =>
  apiFetch<T>(path, { method: 'PATCH', body: JSON.stringify(body) })

export const apiDelete = <T>(path: string) =>
  apiFetch<T>(path, { method: 'DELETE' })
