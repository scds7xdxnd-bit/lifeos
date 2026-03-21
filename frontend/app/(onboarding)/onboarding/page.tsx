'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useMutation } from '@tanstack/react-query'
import {
  Wallet,
  Heart,
  Repeat,
  BookOpen,
  Calendar,
  ChevronRight,
  ChevronLeft,
  Check,
  Sparkles,
  Leaf,
  LayoutGrid,
  Cloud,
  ArrowRight,
} from 'lucide-react'
import { onboardingApi } from '@/lib/api/onboarding'
import { useLang } from '@/lib/useLang'
import { getAppTranslations } from '@/lib/translations/app'
import { LanguageMenu } from '@/components/common/LanguageMenu'

/* ── Domain definitions (top 4 user-voted) ── */
interface Domain {
  id: string
  icon: React.ElementType
  accent: string      // icon bg tint
  accentDark: string   // icon colour when selected
  gradient: string     // selected card gradient
}

const DOMAINS: Domain[] = [
  {
    id: 'finance',
    icon: Wallet, accent: '#e8f0e3', accentDark: '#3a5c35',
    gradient: 'linear-gradient(135deg, #edf5e8 0%, #d9ebcf 100%)',
  },
  {
    id: 'health',
    icon: Heart, accent: '#fce8e4', accentDark: '#8b4a3a',
    gradient: 'linear-gradient(135deg, #fdf0ed 0%, #f5ddd6 100%)',
  },
  {
    id: 'habits',
    icon: Repeat, accent: '#e4edf5', accentDark: '#3a5272',
    gradient: 'linear-gradient(135deg, #edf2f8 0%, #d6e3f0 100%)',
  },
  {
    id: 'skills',
    icon: BookOpen, accent: '#f5f0e4', accentDark: '#6b5a35',
    gradient: 'linear-gradient(135deg, #f8f3eb 0%, #ede4d0 100%)',
  },
]

/* ── Calendar providers ── */
interface CalendarOption {
  id: 'google' | 'apple' | 'skip'
  icon: React.ElementType
  iconColor: string
  accent: string
  gradient: string
}

const CALENDAR_OPTIONS: CalendarOption[] = [
  {
    id: 'google',
    icon: Calendar, iconColor: '#4b6646', accent: '#e8f0e3',
    gradient: 'linear-gradient(135deg, #edf5e8 0%, #d9ebcf 100%)',
  },
  {
    id: 'apple',
    icon: Cloud, iconColor: '#3a5272', accent: '#e4edf5',
    gradient: 'linear-gradient(135deg, #edf2f8 0%, #d6e3f0 100%)',
  },
  {
    id: 'skip',
    icon: ArrowRight, iconColor: '#767d72', accent: '#f1f1ed',
    gradient: 'linear-gradient(135deg, #f3f3ef 0%, #e8e8e2 100%)',
  },
]

type Step = 'domains' | 'calendar' | 'processing'
type ProcessingCopy = ReturnType<typeof getAppTranslations>['onboarding']['processing']

/* ── Processing screen — inspired by "Listening to the Archive" ── */
function ProcessingScreen({ t }: { t: ProcessingCopy }) {
  const [progress, setProgress] = useState(0)
  const [activeCard, setActiveCard] = useState(0)

  const discoveryItems = t.items

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(p => Math.min(p + 2, 100))
    }, 50)
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const interval = setInterval(() => {
      setActiveCard(c => (c + 1) % discoveryItems.length)
    }, 800)
    return () => clearInterval(interval)
  }, [discoveryItems.length])

  return (
    <div className="processing-screen">
      {/* Floating particles */}
      <div className="particles">
        {Array.from({ length: 12 }).map((_, i) => (
          <div key={i} className="particle" style={{
            left: `${10 + Math.random() * 80}%`,
            animationDelay: `${i * 0.4}s`,
            animationDuration: `${3 + Math.random() * 4}s`,
          }} />
        ))}
      </div>

      {/* Central hero */}
      <div className="hero-orb">
        <div className="orb-ring orb-ring-outer" />
        <div className="orb-ring orb-ring-inner" />
        <div className="orb-core">
          <Leaf size={32} color="#4b6646" strokeWidth={1.5} />
        </div>
      </div>

      {/* Floating discovery cards */}
      <div className="discovery-cards">
        {discoveryItems.map((item, i) => (
          <div
            key={item.label}
            className={`discovery-card ${i === activeCard ? 'discovery-card-active' : ''}`}
            style={{ animationDelay: `${i * 0.15}s` }}
          >
            <Sparkles size={14} color="#4b6646" strokeWidth={2} />
            <div className="discovery-card-content">
              <span className="discovery-status">{item.status}</span>
              <span className="discovery-label">{item.label}</span>
            </div>
          </div>
        ))}
      </div>

      {/* Headline */}
      <h1 className="processing-title">{t.title}</h1>
      <p className="processing-subtitle">
        {t.subtitle}
      </p>

      {/* Progress bar */}
      <div className="progress-track">
        <div className="progress-fill" style={{ width: `${progress}%` }} />
      </div>
      <span className="progress-label">{progress}% {t.complete}</span>

      {/* Bottom status cards */}
      <div className="status-cards">
        <div className="status-card status-card-light">
          <LayoutGrid size={20} color="#4b6646" strokeWidth={1.8} />
          <div className="status-badge status-badge-connected">{t.connected}</div>
          <h3 className="status-card-title">{t.digitalRhythm}</h3>
          <p className="status-card-desc">
            {t.digitalRhythmDesc}
          </p>
        </div>
        <div className="status-card status-card-dark">
          <Sparkles size={20} color="#a8c4a0" strokeWidth={1.8} />
          <div className="status-badge status-badge-processing">{t.processing}</div>
          <h3 className="status-card-title-dark">{t.intentMapping}</h3>
          <p className="status-card-desc-dark">
            {t.intentMappingDesc}
          </p>
        </div>
      </div>
    </div>
  )
}

/* ── Main onboarding wizard ── */
export default function OnboardingPage() {
  const [lang, setLang] = useLang()
  const t = getAppTranslations(lang).onboarding
  const router = useRouter()
  const [step, setStep] = useState<Step>('domains')
  const [selectedDomains, setSelectedDomains] = useState<Set<string>>(new Set())
  const [calendarProvider, setCalendarProvider] = useState<'google' | 'apple' | 'skip' | null>(null)
  const [fadeIn, setFadeIn] = useState(true)
  const [enterDirection, setEnterDirection] = useState<'right' | 'left'>('right')

  const domainCopy = Object.fromEntries(t.domains.map((d) => [d.id, d])) as Record<string, { id: string; label: string; description: string }>
  const calendarCopy = Object.fromEntries(t.calendar.map((c) => [c.id, c])) as Record<'google' | 'apple' | 'skip', { id: string; label: string; subtitle: string }>

  /* ── Mutations ── */
  const domainsMutation = useMutation({
    mutationFn: () =>
      onboardingApi.submitStep({
        step: 'domains',
        data: { selected: Array.from(selectedDomains) },
      }),
  })

  const calendarMutation = useMutation({
    mutationFn: (provider: string) =>
      onboardingApi.submitStep({
        step: 'calendar',
        data: { provider },
      }),
  })

  const completeMutation = useMutation({
    mutationFn: () =>
      onboardingApi.submitStep({
        step: 'complete',
        data: {},
      }),
  })

  /* ── Domain toggle ── */
  const toggleDomain = useCallback((id: string) => {
    setSelectedDomains((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }, [])

  /* ── Step transitions ── */
  const transitionTo = useCallback((nextStep: Step, direction: 'right' | 'left' = 'right') => {
    setFadeIn(false)
    setTimeout(() => {
      setStep(nextStep)
      setEnterDirection(direction)
      setFadeIn(true)
    }, 250)
  }, [])

  const handleDomainsContinue = useCallback(async () => {
    await domainsMutation.mutateAsync()
    transitionTo('calendar', 'right')
  }, [domainsMutation, transitionTo])

  const handleCalendarContinue = useCallback(async () => {
    if (!calendarProvider) return
    await calendarMutation.mutateAsync(calendarProvider)
    transitionTo('processing', 'right')
  }, [calendarProvider, calendarMutation, transitionTo])

  const handleBack = useCallback(() => {
    transitionTo('domains', 'left')
  }, [transitionTo])

  /* ── Processing auto-advance ── */
  useEffect(() => {
    if (step !== 'processing') return
    const timer = setTimeout(async () => {
      await completeMutation.mutateAsync()
      router.push('/calendar')
    }, 5000)
    return () => clearTimeout(timer)
  }, [step, completeMutation, router])

  /* ── Step progress indicator ── */
  const stepIndex = step === 'domains' ? 0 : step === 'calendar' ? 1 : 2
  const translateDir = enterDirection === 'right' ? '20px' : '-20px'

  return (
    <>
      <div style={{ position: 'fixed', top: '16px', right: '16px', zIndex: 70 }}>
        <LanguageMenu lang={lang} setLang={setLang} iconOnly />
      </div>
      <style>{`
        /* ── Animations ── */
        @keyframes slideIn {
          from { opacity: 0; transform: translateY(16px) translateX(${translateDir}); }
          to { opacity: 1; transform: translateY(0) translateX(0); }
        }
        .step-enter {
          animation: slideIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        @keyframes cardEntrance {
          from { opacity: 0; transform: translateY(20px) scale(0.96); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }

        @keyframes checkPop {
          0% { transform: scale(0); }
          60% { transform: scale(1.2); }
          100% { transform: scale(1); }
        }

        @keyframes shimmer {
          0% { background-position: -200% 0; }
          100% { background-position: 200% 0; }
        }

        @keyframes float {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-8px); }
        }

        @keyframes particleRise {
          0% { opacity: 0; transform: translateY(40px) scale(0.5); }
          20% { opacity: 0.6; }
          80% { opacity: 0.3; }
          100% { opacity: 0; transform: translateY(-100px) scale(0); }
        }

        @keyframes orbPulse {
          0%, 100% { transform: scale(1); opacity: 0.3; }
          50% { transform: scale(1.15); opacity: 0.15; }
        }

        @keyframes orbPulseInner {
          0%, 100% { transform: scale(1); opacity: 0.5; }
          50% { transform: scale(1.08); opacity: 0.3; }
        }

        @keyframes breathe {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.05); }
        }

        @keyframes progressGlow {
          0%, 100% { box-shadow: 0 0 8px rgba(75, 102, 70, 0.3); }
          50% { box-shadow: 0 0 20px rgba(75, 102, 70, 0.5); }
        }

        @keyframes discoverySlideIn {
          from { opacity: 0; transform: translateX(30px); }
          to { opacity: 1; transform: translateX(0); }
        }

        @keyframes statusCardEnter {
          from { opacity: 0; transform: translateY(30px); }
          to { opacity: 1; transform: translateY(0); }
        }

        /* ── Domain cards ── */
        .domain-card {
          position: relative;
          display: flex;
          align-items: center;
          gap: 16px;
          padding: 22px 24px;
          border-radius: 0 16px 16px 16px;
          border: 2px solid transparent;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
          animation: cardEntrance 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
          opacity: 0;
        }
        .domain-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 16px 40px rgba(46, 52, 43, 0.1);
        }
        .domain-card:active {
          transform: scale(0.98);
        }

        /* ── Check indicator ── */
        .check-circle {
          position: absolute;
          top: 12px;
          right: 12px;
          width: 24px;
          height: 24px;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: all 0.2s ease;
        }
        .check-circle-empty {
          border: 2px solid rgba(173, 180, 168, 0.3);
          background: transparent;
        }
        .check-circle-filled {
          border: none;
          background: #4b6646;
          animation: checkPop 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }

        /* ── Calendar cards ── */
        .calendar-card {
          position: relative;
          display: flex;
          align-items: center;
          gap: 18px;
          padding: 22px 28px;
          border-radius: 0 16px 16px 16px;
          border: 2px solid transparent;
          cursor: pointer;
          transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
          animation: cardEntrance 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
          opacity: 0;
        }
        .calendar-card:hover {
          transform: translateY(-3px);
          box-shadow: 0 16px 40px rgba(46, 52, 43, 0.1);
        }
        .calendar-card:active {
          transform: scale(0.98);
        }

        /* ── Button styles ── */
        .btn-primary {
          transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .btn-primary:hover:not(:disabled) {
          transform: translateY(-2px) scale(1.025);
          box-shadow: 0 10px 34px rgba(46, 52, 43, 0.24);
        }
        .btn-primary:active:not(:disabled) {
          transform: translateY(0) scale(0.98);
        }
        .btn-ghost {
          transition: all 0.2s ease;
        }
        .btn-ghost:hover {
          background: rgba(75, 102, 70, 0.08);
        }

        /* ── Processing screen ── */
        .processing-screen {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 80vh;
          text-align: center;
          position: relative;
          overflow: hidden;
          padding: 40px 24px;
        }

        .particles {
          position: absolute;
          inset: 0;
          pointer-events: none;
        }
        .particle {
          position: absolute;
          bottom: 20%;
          width: 6px;
          height: 6px;
          border-radius: 50%;
          background: rgba(75, 102, 70, 0.2);
          animation: particleRise 4s ease-in-out infinite;
        }

        /* Orb hero */
        .hero-orb {
          position: relative;
          width: 120px;
          height: 120px;
          margin-bottom: 32px;
        }
        .orb-ring {
          position: absolute;
          border-radius: 50%;
          border: 1.5px solid rgba(75, 102, 70, 0.15);
        }
        .orb-ring-outer {
          inset: -12px;
          animation: orbPulse 4s ease-in-out infinite;
        }
        .orb-ring-inner {
          inset: -4px;
          animation: orbPulseInner 3s ease-in-out infinite;
        }
        .orb-core {
          width: 100%;
          height: 100%;
          border-radius: 50%;
          background: linear-gradient(145deg, #e3f0dc 0%, #ccebc2 50%, #d6e8ce 100%);
          display: flex;
          align-items: center;
          justify-content: center;
          box-shadow: 0 8px 40px rgba(75, 102, 70, 0.2);
          animation: breathe 4s ease-in-out infinite;
        }

        /* Discovery cards */
        .discovery-cards {
          display: flex;
          flex-wrap: wrap;
          justify-content: center;
          gap: 10px;
          margin-bottom: 36px;
          max-width: 480px;
        }
        .discovery-card {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 8px 14px;
          border-radius: 100px;
          background: rgba(255, 255, 255, 0.8);
          backdrop-filter: blur(8px);
          border: 1px solid rgba(255, 255, 255, 0.3);
          box-shadow: 0 2px 12px rgba(46, 52, 43, 0.06);
          animation: discoverySlideIn 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
          opacity: 0;
          transition: all 0.3s ease;
        }
        .discovery-card-active {
          background: rgba(204, 235, 194, 0.5);
          box-shadow: 0 4px 16px rgba(75, 102, 70, 0.12);
          transform: scale(1.05);
        }
        .discovery-card-content {
          display: flex;
          flex-direction: column;
          align-items: flex-start;
        }
        .discovery-status {
          font-family: var(--font-manrope), 'Manrope', sans-serif;
          font-size: 0.6rem;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          color: #4b6646;
        }
        .discovery-label {
          font-family: var(--font-manrope), 'Manrope', sans-serif;
          font-size: 0.78rem;
          font-weight: 600;
          color: #2e342b;
        }

        .processing-title {
          font-family: var(--font-serif), 'Newsreader', Georgia, serif;
          font-size: 2rem;
          font-weight: 400;
          font-style: italic;
          letter-spacing: -0.03em;
          color: #4b6646;
          margin-bottom: 10px;
        }
        .processing-subtitle {
          font-family: var(--font-manrope), 'Manrope', sans-serif;
          font-size: 0.9rem;
          color: #5a6157;
          line-height: 1.6;
          max-width: 380px;
          margin-bottom: 32px;
        }

        /* Progress bar */
        .progress-track {
          width: 200px;
          height: 4px;
          border-radius: 100px;
          background: rgba(75, 102, 70, 0.1);
          overflow: hidden;
          margin-bottom: 8px;
        }
        .progress-fill {
          height: 100%;
          border-radius: 100px;
          background: linear-gradient(90deg, #4b6646, #6b8f65);
          transition: width 0.1s linear;
          animation: progressGlow 2s ease-in-out infinite;
        }
        .progress-label {
          font-family: var(--font-manrope), 'Manrope', sans-serif;
          font-size: 0.72rem;
          font-weight: 600;
          letter-spacing: 0.05em;
          text-transform: uppercase;
          color: #767d72;
          margin-bottom: 40px;
        }

        /* Status cards */
        .status-cards {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 16px;
          max-width: 480px;
          width: 100%;
        }
        .status-card {
          padding: 24px 20px;
          border-radius: 0 16px 16px 16px;
          animation: statusCardEnter 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
          opacity: 0;
        }
        .status-card:first-child { animation-delay: 0.8s; }
        .status-card:last-child { animation-delay: 1s; }
        .status-card-light {
          background: #ffffff;
          box-shadow: 0 4px 20px rgba(46, 52, 43, 0.06);
        }
        .status-card-dark {
          background: #2e342b;
        }
        .status-badge {
          display: inline-block;
          font-family: var(--font-manrope), 'Manrope', sans-serif;
          font-size: 0.6rem;
          font-weight: 700;
          letter-spacing: 0.08em;
          text-transform: uppercase;
          padding: 3px 10px;
          border-radius: 100px;
          margin-top: 12px;
          margin-bottom: 10px;
        }
        .status-badge-connected {
          background: #ccebc2;
          color: #3f5a3a;
        }
        .status-badge-processing {
          background: rgba(168, 196, 160, 0.2);
          color: #a8c4a0;
        }
        .status-card-title {
          font-family: var(--font-serif), 'Newsreader', Georgia, serif;
          font-size: 1.05rem;
          font-weight: 400;
          letter-spacing: -0.03em;
          color: #4b6646;
          margin-bottom: 6px;
        }
        .status-card-title-dark {
          font-family: var(--font-serif), 'Newsreader', Georgia, serif;
          font-size: 1.05rem;
          font-weight: 400;
          letter-spacing: -0.03em;
          color: #a8c4a0;
          margin-bottom: 6px;
        }
        .status-card-desc {
          font-family: var(--font-manrope), 'Manrope', sans-serif;
          font-size: 0.78rem;
          color: #5a6157;
          line-height: 1.5;
        }
        .status-card-desc-dark {
          font-family: var(--font-manrope), 'Manrope', sans-serif;
          font-size: 0.78rem;
          color: #5a6857;
          line-height: 1.5;
        }

        /* ── Selection counter ── */
        .selection-counter {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          padding: 6px 14px;
          border-radius: 100px;
          background: rgba(75, 102, 70, 0.08);
          font-family: var(--font-manrope), 'Manrope', sans-serif;
          font-size: 0.78rem;
          font-weight: 600;
          color: #4b6646;
          transition: all 0.3s ease;
        }

        @media (max-width: 480px) {
          .status-cards { grid-template-columns: 1fr; }
          .processing-title { font-size: 1.6rem; }
          .hero-orb { width: 96px; height: 96px; margin-bottom: 24px; }
        }
        @media (max-width: 360px) {
          .domain-card { padding: 20px 14px 18px !important; }
        }
      `}</style>

      <div
        style={{
          width: '100%',
          maxWidth: step === 'processing' ? '720px' : '560px',
          padding: step === 'processing' ? '20px 24px' : '40px 24px 140px',
          transition: 'opacity 0.25s ease, transform 0.25s ease',
          opacity: fadeIn ? 1 : 0,
          transform: fadeIn ? 'translateY(0)' : 'translateY(8px)',
        }}
      >
        {/* ── Step indicator ── */}
        {step !== 'processing' && (
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px',
              marginBottom: '48px',
            }}
          >
            {[0, 1].map((i) => (
              <div
                key={i}
                style={{
                  width: i === stepIndex ? '36px' : '8px',
                  height: '8px',
                  borderRadius: '100px',
                  background: i <= stepIndex
                    ? 'linear-gradient(90deg, #4b6646, #6b8f65)'
                    : 'rgba(75, 102, 70, 0.12)',
                  transition: 'all 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
                }}
              />
            ))}
          </div>
        )}

        {/* ── Step 1: Domain Selection ── */}
        {step === 'domains' && (
          <div className="step-enter">
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
              <p
                style={{
                  fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase' as const,
                  color: '#767d72',
                  marginBottom: '12px',
                }}
              >
                {t.step1of2}
              </p>
              <h1
                style={{
                  fontFamily: "var(--font-serif), 'Newsreader', Georgia, serif",
                  fontSize: '2.2rem',
                  fontWeight: 300,
                  letterSpacing: '-0.03em',
                  color: '#4b6646',
                  marginBottom: '12px',
                  lineHeight: 1.2,
                }}
              >
                {t.whatToTrack}
              </h1>
              <p
                style={{
                  fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                  fontSize: '0.92rem',
                  color: '#5a6157',
                  lineHeight: 1.6,
                }}
              >
                {t.whatToTrackSub}
              </p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '14px' }}>
              {DOMAINS.map((domain, index) => {
                const isSelected = selectedDomains.has(domain.id)
                const Icon = domain.icon
                const copy = domainCopy[domain.id]
                return (
                  <button
                    key={domain.id}
                    type="button"
                    onClick={() => toggleDomain(domain.id)}
                    className="domain-card"
                    style={{
                      animationDelay: `${index * 0.08}s`,
                      background: isSelected ? domain.gradient : '#ffffff',
                      borderColor: isSelected ? domain.accentDark : 'rgba(173, 180, 168, 0.15)',
                      boxShadow: isSelected
                        ? '0 6px 24px rgba(46, 52, 43, 0.1)'
                        : '0 2px 12px rgba(46, 52, 43, 0.05)',
                      flexDirection: 'column',
                      alignItems: 'center',
                      textAlign: 'center',
                      padding: '28px 20px 24px',
                      gap: '14px',
                    }}
                  >
                    {/* Check circle */}
                    <div className={`check-circle ${isSelected ? 'check-circle-filled' : 'check-circle-empty'}`}
                      style={isSelected ? { background: domain.accentDark } : undefined}
                    >
                      {isSelected && <Check size={14} color="#ffffff" strokeWidth={3} />}
                    </div>

                    <div style={{
                      width: '56px',
                      height: '56px',
                      borderRadius: '16px',
                      background: isSelected ? `${domain.accentDark}18` : domain.accent,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      transition: 'all 0.3s ease',
                    }}>
                      <Icon
                        size={26}
                        color={isSelected ? domain.accentDark : '#5a6157'}
                        strokeWidth={1.6}
                      />
                    </div>
                    <div>
                      <span
                        style={{
                          display: 'block',
                          fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                          fontSize: '0.95rem',
                          fontWeight: 700,
                          color: '#2e342b',
                          marginBottom: '4px',
                        }}
                      >
                        {copy?.label ?? domain.id}
                      </span>
                      <span
                        style={{
                          fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                          fontSize: '0.76rem',
                          color: '#767d72',
                          lineHeight: 1.4,
                        }}
                      >
                        {copy?.description ?? ''}
                      </span>
                    </div>
                  </button>
                )
              })}
            </div>

            {/* Selection counter */}
            {selectedDomains.size > 0 && (
              <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
                <div className="selection-counter">
                  <Check size={14} strokeWidth={2.5} />
                  {selectedDomains.size} {t.selected}
                </div>
              </div>
            )}

            {domainsMutation.isError && (
              <p style={{
                fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                fontSize: '0.82rem',
                color: '#e8735c',
                textAlign: 'center',
                marginTop: '16px',
              }}>
                {t.errorGeneric}
              </p>
            )}
          </div>
        )}

        {/* ── Step 2: Calendar Source ── */}
        {step === 'calendar' && (
          <div className="step-enter">
            <div style={{ textAlign: 'center', marginBottom: '40px' }}>
              <p
                style={{
                  fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                  fontSize: '0.7rem',
                  fontWeight: 700,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase' as const,
                  color: '#767d72',
                  marginBottom: '12px',
                }}
              >
                {t.step2of2}
              </p>
              <h1
                style={{
                  fontFamily: "var(--font-serif), 'Newsreader', Georgia, serif",
                  fontSize: '2.2rem',
                  fontWeight: 300,
                  letterSpacing: '-0.03em',
                  color: '#4b6646',
                  marginBottom: '12px',
                  lineHeight: 1.2,
                }}
              >
                {t.connectCalendar}
              </h1>
              <p
                style={{
                  fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                  fontSize: '0.92rem',
                  color: '#5a6157',
                  lineHeight: 1.6,
                }}
              >
                {t.connectCalendarSub}
              </p>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {CALENDAR_OPTIONS.map((option, index) => {
                const isActive = calendarProvider === option.id
                const OptionIcon = option.icon
                const copy = calendarCopy[option.id]
                return (
                  <button
                    key={option.id}
                    type="button"
                    onClick={() => setCalendarProvider(option.id)}
                    className="calendar-card"
                    style={{
                      animationDelay: `${index * 0.1}s`,
                      background: isActive ? option.gradient : '#ffffff',
                      borderColor: isActive ? option.iconColor : 'rgba(173, 180, 168, 0.15)',
                      boxShadow: isActive
                        ? '0 6px 24px rgba(46, 52, 43, 0.1)'
                        : '0 2px 12px rgba(46, 52, 43, 0.05)',
                    }}
                  >
                    {/* Check circle */}
                    <div className={`check-circle ${isActive ? 'check-circle-filled' : 'check-circle-empty'}`}
                      style={isActive ? { background: option.iconColor } : undefined}
                    >
                      {isActive && <Check size={14} color="#ffffff" strokeWidth={3} />}
                    </div>

                    <div style={{
                      width: '52px',
                      height: '52px',
                      borderRadius: '14px',
                      background: isActive ? `${option.iconColor}15` : option.accent,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      flexShrink: 0,
                      transition: 'all 0.3s ease',
                    }}>
                      <OptionIcon
                        size={24}
                        color={isActive ? option.iconColor : '#5a6157'}
                        strokeWidth={1.6}
                      />
                    </div>
                    <div>
                      <span
                        style={{
                          display: 'block',
                          fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                          fontSize: '0.95rem',
                          fontWeight: 600,
                          color: '#2e342b',
                          marginBottom: '2px',
                        }}
                      >
                        {copy?.label ?? option.id}
                      </span>
                      <span
                        style={{
                          fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                          fontSize: '0.8rem',
                          color: '#767d72',
                        }}
                      >
                        {copy?.subtitle ?? ''}
                      </span>
                    </div>
                  </button>
                )
              })}
            </div>

            {calendarMutation.isError && (
              <p style={{
                fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                fontSize: '0.82rem',
                color: '#e8735c',
                textAlign: 'center',
                marginTop: '16px',
              }}>
                {t.errorGeneric}
              </p>
            )}
          </div>
        )}

        {/* ── Step 3: Processing Animation ── */}
        {step === 'processing' && <ProcessingScreen t={t.processing} />}
      </div>

      {/* ── Bottom bar ── */}
      {step !== 'processing' && (
        <div
          style={{
            position: 'fixed',
            bottom: 0,
            left: 0,
            right: 0,
            padding: '20px 24px calc(20px + env(safe-area-inset-bottom, 0px))',
            background: 'rgba(248, 250, 242, 0.85)',
            backdropFilter: 'blur(8px)',
            WebkitBackdropFilter: 'blur(8px)',
            borderTop: '1px solid rgba(255, 255, 255, 0.2)',
            boxShadow: '0 -4px 20px rgba(46, 52, 43, 0.04)',
          }}
        >
          <div
            style={{
              maxWidth: '560px',
              margin: '0 auto',
              display: 'flex',
              alignItems: 'center',
              justifyContent: step === 'domains' ? 'flex-end' : 'space-between',
              gap: '12px',
            }}
          >
            {step === 'calendar' && (
              <button
                type="button"
                onClick={handleBack}
                className="btn-ghost"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '12px 24px',
                  borderRadius: '100px',
                  border: 'none',
                  background: 'transparent',
                  fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                  fontSize: '0.88rem',
                  fontWeight: 600,
                  color: '#5a6157',
                  cursor: 'pointer',
                }}
              >
                <ChevronLeft size={18} strokeWidth={2.2} />
                {t.back}
              </button>
            )}

            <button
              type="button"
              onClick={step === 'domains' ? handleDomainsContinue : handleCalendarContinue}
              disabled={
                (step === 'domains' && selectedDomains.size === 0) ||
                (step === 'calendar' && !calendarProvider) ||
                domainsMutation.isPending ||
                calendarMutation.isPending
              }
              className="btn-primary"
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                padding: '14px 36px',
                borderRadius: '100px',
                border: 'none',
                background:
                  (step === 'domains' && selectedDomains.size === 0) ||
                  (step === 'calendar' && !calendarProvider)
                    ? 'rgba(75, 102, 70, 0.2)'
                    : 'linear-gradient(135deg, #4b6646, #3f5a3a)',
                color: '#ffffff',
                fontFamily: "var(--font-manrope), 'Manrope', sans-serif",
                fontSize: '0.9rem',
                fontWeight: 700,
                letterSpacing: '0.01em',
                cursor:
                  (step === 'domains' && selectedDomains.size === 0) ||
                  (step === 'calendar' && !calendarProvider)
                    ? 'not-allowed'
                    : 'pointer',
                boxShadow:
                  (step === 'domains' && selectedDomains.size === 0) ||
                  (step === 'calendar' && !calendarProvider)
                    ? 'none'
                    : '0 4px 20px rgba(46, 52, 43, 0.18)',
                opacity: domainsMutation.isPending || calendarMutation.isPending ? 0.7 : 1,
              }}
            >
              {domainsMutation.isPending || calendarMutation.isPending ? (
                t.saving
              ) : (
                <>
                  {t.continue}
                  <ChevronRight size={18} strokeWidth={2.2} />
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </>
  )
}
