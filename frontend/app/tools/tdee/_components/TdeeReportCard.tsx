'use client'

import { useState } from 'react'
import { TriangleAlert, ChevronDown } from 'lucide-react'
import type { TdeeInput, TdeeResult, TdeeWarning } from '@/lib/tdee-calculator'

interface TdeeReportCardProps {
  result: TdeeResult
  warnings: TdeeWarning[]
  goal_type: TdeeInput['goal_type']
}

const ACTIVITY_LABEL_MAP: Record<string, string> = {
  sedentary: 'Sedentary',
  lightly_active: 'Lightly Active',
  moderately_active: 'Moderately Active',
  very_active: 'Very Active',
  extra_active: 'Extra Active',
}

const GOAL_LABEL_MAP: Record<string, string> = {
  lose: 'Lose Weight',
  gain: 'Gain Weight',
  maintain: 'Maintain Weight',
}

export default function TdeeReportCard({ result, warnings, goal_type }: TdeeReportCardProps) {
  const [deltaOpen, setDeltaOpen] = useState(false)

  const microLabel: React.CSSProperties = {
    fontFamily: 'var(--font-manrope), Manrope, sans-serif',
    fontWeight: 700,
    fontSize: '0.6875rem',
    letterSpacing: '0.05em',
    textTransform: 'uppercase',
    color: '#8b4a3a',
  }

  return (
    <div style={{ animation: 'reportIn 300ms ease' }}>
      <style>{`@keyframes reportIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }`}</style>

      {/* Hero: Daily Calorie Target */}
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <p style={{ ...microLabel, marginBottom: '8px' }}>Your Daily Targets</p>
        <div style={{ fontFamily: 'var(--font-serif), Newsreader, serif', fontWeight: 300, fontSize: '2.5rem', color: '#4b6646', lineHeight: 1 }}>
          {result.daily_calories.toLocaleString()}
          <span style={{ fontFamily: 'var(--font-manrope), Manrope, sans-serif', fontSize: '1rem', color: '#767d72', marginLeft: '8px', fontWeight: 400 }}>
            kcal/day
          </span>
        </div>
        <span style={{
          display: 'inline-block',
          marginTop: '8px',
          borderRadius: '100px',
          background: '#fce8e4',
          color: '#8b4a3a',
          fontFamily: 'var(--font-manrope), Manrope, sans-serif',
          fontSize: '0.6875rem',
          fontWeight: 500,
          padding: '4px 12px',
        }}>
          {GOAL_LABEL_MAP[goal_type]}
        </span>
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div style={{ marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {warnings.map((w, i) => (
            <div
              key={i}
              style={{
                background: '#fdf0ed',
                borderRadius: '0 12px 12px 12px',
                padding: '12px 16px',
                display: 'flex',
                gap: '10px',
                alignItems: 'flex-start',
                animation: `reportIn 300ms ease ${100 + i * 50}ms both`,
              }}
            >
              <TriangleAlert size={16} color="#8b4a3a" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span style={{ fontFamily: 'var(--font-manrope), Manrope, sans-serif', fontSize: '0.8125rem', color: '#2e342b', lineHeight: 1.5 }}>
                {w.message}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* BMR Breakdown */}
      <div style={{ background: '#ffffff', borderRadius: '0 16px 16px 16px', padding: '24px', marginBottom: '16px', boxShadow: '0 2px 8px rgba(46,52,43,0.06)' }}>
        <p style={{ ...microLabel, marginBottom: '16px' }}>BMR Breakdown</p>
        {((): Array<{ label: string; value: React.ReactNode }> => [
          {
            label: 'Method',
            value: (
              <span style={{ borderRadius: '100px', background: '#f1f5eb', color: '#5a6157', fontSize: '0.75rem', padding: '3px 10px' }}>
                {result.method_used === 'katch_mcardle' ? 'Katch-McArdle' : 'Mifflin-St Jeor'}
              </span>
            ),
          },
          ...(result.lean_body_mass != null ? [{ label: 'Lean Body Mass', value: `${result.lean_body_mass.toFixed(1)} kg` }] : []),
          { label: 'BMR', value: `${result.bmr.toLocaleString()} kcal/day` },
          { label: 'Activity', value: `${ACTIVITY_LABEL_MAP[result.activity_multiplier] ?? ''} (×${result.activity_multiplier})` },
          { label: 'TDEE', value: `${result.tdee.toLocaleString()} kcal/day` },
          ...(result.delta_kcal_per_day != null
            ? [{ label: 'Daily Adjustment', value: `${result.delta_kcal_per_day > 0 ? '+' : ''}${result.delta_kcal_per_day.toFixed(0)} kcal` }]
            : []),
        ])().map(({ label, value }, i) => (
          <div
            key={i}
            style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid rgba(173,180,168,0.1)' }}
          >
            <span style={{ fontFamily: 'var(--font-manrope), Manrope, sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>{label}</span>
            <span style={{ fontFamily: 'var(--font-manrope), Manrope, sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b' }}>{value}</span>
          </div>
        ))}
      </div>

      {/* Macro Table */}
      <div style={{ background: '#ffffff', borderRadius: '0 16px 16px 16px', padding: '24px', marginBottom: '16px', boxShadow: '0 2px 8px rgba(46,52,43,0.06)' }}>
        <p style={{ ...microLabel, marginBottom: '16px' }}>Macro Targets</p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0' }}>
          {[
            ['', 'Daily', 'Monthly (×30)'],
            ['Protein', `${result.protein_g_per_day.toFixed(0)}g`, `${result.monthly_protein_g.toFixed(0)}g`],
            ['Fat', `${result.fat_g_per_day.toFixed(0)}g`, `${result.monthly_fat_g.toFixed(0)}g`],
            ['Carbs', `${result.carbs_g_per_day.toFixed(0)}g`, `${result.monthly_carbs_g.toFixed(0)}g`],
            ['Fiber', `${result.fiber_g_per_day.toFixed(0)}g`, `${result.monthly_fiber_g.toFixed(0)}g`],
            ['kcal/day', `${result.daily_calories.toLocaleString()}`, `${result.monthly_calories.toLocaleString()}`],
          ].map((row, ri) =>
            row.map((cell, ci) => (
              <div
                key={`${ri}-${ci}`}
                style={{
                  padding: '8px 4px',
                  background: ri % 2 === 0 ? '#f8faf2' : '#ffffff',
                  fontFamily: 'var(--font-manrope), Manrope, sans-serif',
                  fontSize: ri === 0 ? '0.6875rem' : '0.875rem',
                  fontWeight: ri === 0 ? 700 : ci === 0 ? 400 : 600,
                  color: ri === 0 ? '#8b4a3a' : ci === 2 ? '#767d72' : '#2e342b',
                  textTransform: ri === 0 ? 'uppercase' : 'none',
                  letterSpacing: ri === 0 ? '0.04em' : 'normal',
                  borderBottom: '1px solid rgba(173,180,168,0.08)',
                }}
              >
                {cell}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Delta Breakdown (expandable) */}
      {goal_type !== 'maintain' && result.delta_bw != null && (
        <div style={{ marginBottom: '8px' }}>
          <button
            type="button"
            onClick={() => setDeltaOpen(o => !o)}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              fontFamily: 'var(--font-manrope), Manrope, sans-serif',
              fontSize: '0.8125rem',
              color: '#5a6157',
              padding: '8px 0',
              minHeight: '44px',
            }}
          >
            <ChevronDown
              size={14}
              style={{ transform: deltaOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }}
            />
            Delta Breakdown
          </button>
          {deltaOpen && (
            <div style={{ paddingLeft: '20px', borderLeft: '2px solid rgba(173,180,168,0.2)' }}>
              {[
                ['Δ Body Weight', `${result.delta_bw > 0 ? '+' : ''}${result.delta_bw.toFixed(2)} kg`],
                ['kcal/kg Assumption', `${result.kcal_per_kg_used?.toLocaleString()} kcal/kg`],
                ['Total kcal Δ', `${result.total_delta_kcal!.toLocaleString()} kcal`],
                ['Daily kcal Adjustment', `${result.delta_kcal_per_day! > 0 ? '+' : ''}${result.delta_kcal_per_day!.toFixed(0)} kcal/day`],
              ].map(([label, value], i) => (
                <div
                  key={i}
                  style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', fontFamily: 'var(--font-manrope), Manrope, sans-serif', fontSize: '0.8125rem', color: '#5a6157' }}
                >
                  <span>{label}</span>
                  <span style={{ fontWeight: 600 }}>{value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
