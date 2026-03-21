'use client'

import { Wallet } from 'lucide-react'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'

export default function FinancesPage() {
  const [lang] = useLang()
  const t = getAppTranslations(lang).finances

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div>
        <p
          className="text-xs font-bold uppercase mb-2"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            letterSpacing: '0.05em',
            color: '#3a5c35',
          }}
        >
          {t.eyebrow}
        </p>
        <h1
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '2rem',
            fontWeight: 300,
            color: '#4b6646',
            letterSpacing: '-0.03em',
          }}
        >
          {t.title}
        </h1>
        <p
          className="mt-2"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.9375rem',
            color: '#5a6157',
            lineHeight: 1.65,
          }}
        >
          {t.subtitle}
        </p>
      </div>

      {/* Coming soon card */}
      <div
        className="p-10 text-center"
        style={{
          background: '#ffffff',
          borderRadius: '0 16px 16px 16px',
          boxShadow: '0 8px 24px rgba(46, 52, 43, 0.06)',
        }}
      >
        <div
          className="w-16 h-16 rounded-full mx-auto mb-4 flex items-center justify-center"
          style={{ background: '#e8f0e3' }}
        >
          <Wallet size={28} style={{ color: '#3a5c35' }} />
        </div>
        <h3
          style={{
            fontFamily: 'var(--font-serif), Georgia, serif',
            fontSize: '1.25rem',
            fontWeight: 400,
            color: '#4b6646',
            letterSpacing: '-0.03em',
          }}
        >
          {t.comingSoonTitle}
        </h3>
        <p
          className="mt-2 max-w-md mx-auto"
          style={{
            fontFamily: 'var(--font-manrope), sans-serif',
            fontSize: '0.875rem',
            color: '#767d72',
            lineHeight: 1.65,
          }}
        >
          {t.comingSoonBody}
        </p>
      </div>
    </div>
  )
}
