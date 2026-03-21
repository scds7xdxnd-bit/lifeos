'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'

export default function OnboardingLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/login')
    }
  }, [isLoading, isAuthenticated, router])

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex items-center justify-center"
        style={{ background: '#f8faf2' }}
      >
        <p
          style={{
            fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
            fontSize: '0.875rem',
            color: '#5a6157',
          }}
        >
          Loading...
        </p>
      </div>
    )
  }

  if (!isAuthenticated) return null

  return (
    <div
      className="min-h-screen flex flex-col items-center justify-center"
      style={{ background: '#f8faf2' }}
    >
      {children}
    </div>
  )
}
