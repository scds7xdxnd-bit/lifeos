const RAW_API_URL = process.env.NEXT_PUBLIC_API_URL ?? ''

export function resolveApiUrl(): string {
  if (typeof window === 'undefined') return RAW_API_URL

  if (!RAW_API_URL) {
    return `${window.location.protocol}//${window.location.hostname}:5001`
  }

  try {
    const parsed = new URL(RAW_API_URL)
    if (parsed.hostname === 'localhost' || parsed.hostname === '127.0.0.1') {
      const port = parsed.port || '5001'
      return `${parsed.protocol}//${window.location.hostname}:${port}`
    }
    return RAW_API_URL
  } catch {
    return RAW_API_URL
  }
}
