'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/lib/auth/context'
import { AppHeader } from '@/components/shell/AppHeader'
import { AppFooter } from '@/components/shell/AppFooter'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, isAuthenticated, isLoading } = useAuth()
  const router = useRouter()
  const [lang] = useLang()
  const t = getAppTranslations(lang).layout

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.replace('/login')
    }
  }, [isLoading, isAuthenticated, router])

  useEffect(() => {
    if (!isLoading && isAuthenticated && user?.onboarding_completed === false) {
      router.replace('/onboarding')
    }
  }, [isLoading, isAuthenticated, user, router])

  if (isLoading) {
    return (
      <div
        className="min-h-screen flex flex-col items-center justify-center gap-3"
        style={{ background: '#f8faf2' }}
      >
        <div
          className="w-8 h-8 rounded-full border-2 border-t-transparent animate-spin"
          style={{ borderColor: '#4b6646', borderTopColor: 'transparent' }}
        />
        <p
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontStyle: 'italic',
            color: '#767d72',
            fontSize: '0.875rem',
            letterSpacing: '-0.03em',
          }}
        >
          {t.loading}
        </p>
      </div>
    )
  }

  if (!isAuthenticated) return null
  if (user?.onboarding_completed === false) return null

  return (
    <div className="min-h-screen flex flex-col" style={{ background: '#f8faf2' }}>
      <AppHeader />
      <main className="max-w-6xl mx-auto px-4 sm:px-6 py-6 sm:py-8 flex-1 w-full">{children}</main>
      <AppFooter />
    </div>
  )
}
