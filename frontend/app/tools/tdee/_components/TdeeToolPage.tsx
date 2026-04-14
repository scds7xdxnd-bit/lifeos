'use client'

import { useState } from 'react'
import { calculate, getWarnings } from '@/lib/tdee-calculator'
import type { TdeeInput, TdeeResult, TdeeWarning } from '@/lib/tdee-calculator'
import ToolsHeader from './ToolsHeader'
import TdeeCalculatorForm from './TdeeCalculatorForm'
import TdeeReportCard from './TdeeReportCard'
import ConversionCta from './ConversionCta'

export default function TdeeToolPage() {
  const [input, setInput] = useState<TdeeInput | null>(null)
  const [result, setResult] = useState<TdeeResult | null>(null)
  const [warnings, setWarnings] = useState<TdeeWarning[]>([])

  function handleCalculate(input: TdeeInput) {
    const computed = calculate(input)
    const warns = getWarnings({
      gender: input.gender,
      daily_calories: computed.daily_calories,
      tdee: computed.tdee,
      goal_type: input.goal_type,
    })
    setInput(input)
    setResult(computed)
    setWarnings(warns)
  }

  return (
    <>
      <ToolsHeader />

      <div style={{ maxWidth: 640, margin: '0 auto', padding: '48px 20px 80px' }}>
        {/* Micro-label */}
        <p
          style={{
            fontFamily: 'var(--font-manrope), Manrope, sans-serif',
            fontWeight: 700,
            fontSize: '0.6875rem',
            letterSpacing: '0.05em',
            textTransform: 'uppercase',
            color: '#8b4a3a',
            marginBottom: '12px',
          }}
        >
          Health Tools
        </p>

        {/* Headline */}
        <h1
          style={{
            fontFamily: 'var(--font-serif), Newsreader, serif',
            fontWeight: 300,
            fontSize: 'clamp(2rem, 5vw, 2.5rem)',
            color: '#4b6646',
            letterSpacing: '-0.03em',
            marginBottom: '8px',
            lineHeight: 1.1,
          }}
        >
          TDEE &amp; BMR Calculator
        </h1>

        {/* Subtitle */}
        <p
          style={{
            fontFamily: 'var(--font-manrope), Manrope, sans-serif',
            fontWeight: 400,
            fontSize: '0.9375rem',
            color: '#5a6157',
            lineHeight: 1.65,
            marginBottom: '32px',
          }}
        >
          Calculate your daily energy expenditure and macronutrient targets using clinical-grade
          Mifflin-St Jeor and Katch-McArdle formulas.
        </p>

        <TdeeCalculatorForm onCalculate={handleCalculate} />

        {result && (
          <div style={{ marginTop: '32px' }}>
            <TdeeReportCard result={result} warnings={warnings} goal_type={input!.goal_type} />
          </div>
        )}

        <ConversionCta hasResult={!!result} result={result} />
      </div>

      <footer
        style={{
          textAlign: 'center',
          padding: '40px 20px',
          fontFamily: 'var(--font-manrope), Manrope, sans-serif',
          fontSize: '0.8125rem',
          color: '#767d72',
        }}
      >
        Built by{' '}
        <a
          href="https://taeyangcv.vercel.app/"
          target="_blank"
          rel="noopener noreferrer"
          style={{ color: '#4b6646', fontWeight: 600, textDecoration: 'none' }}
        >
          Taeyang
        </a>
      </footer>
    </>
  )
}
