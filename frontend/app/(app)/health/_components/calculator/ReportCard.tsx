'use client'

import { useState } from 'react'
import { TriangleAlert, ChevronDown } from 'lucide-react'
import type { CalorieReport, Warning } from '@/lib/api/calculator'
import type { HealthPageTranslations } from '@/lib/translations/app'

interface ReportCardProps {
  report: CalorieReport
  warnings: Warning[]
  isLatest?: boolean
  expanded?: boolean
  onToggleExpand?: () => void
  t: HealthPageTranslations
}

const ACTIVITY_LABEL_MAP: Record<string, keyof HealthPageTranslations> = {
  sedentary: 'sedentary',
  lightly_active: 'lightlyActive',
  moderately_active: 'moderatelyActive',
  very_active: 'veryActive',
  extra_active: 'extraActive',
}

const GOAL_LABEL_MAP: Record<string, keyof HealthPageTranslations> = {
  lose: 'lose',
  gain: 'gain',
  maintain: 'maintain',
}

export default function ReportCard({ report, warnings, isLatest, expanded = true, onToggleExpand, t }: ReportCardProps) {
  const [deltaOpen, setDeltaOpen] = useState(false)

  const microLabel: React.CSSProperties = {
    fontFamily: 'Manrope, sans-serif', fontWeight: 700, fontSize: '0.6875rem',
    letterSpacing: '0.05em', textTransform: 'uppercase', color: '#8b4a3a',
  }

  if (!expanded && onToggleExpand) {
    return (
      <div
        onClick={onToggleExpand}
        style={{
          background: '#f8faf2', borderRadius: '0 10px 10px 10px', padding: '14px 18px',
          marginBottom: '8px', cursor: 'pointer', display: 'flex', alignItems: 'center',
          gap: '12px',
        }}
      >
        <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#5a6157', flex: 1 }}>
          {new Date(report.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
        </span>
        <span style={{ borderRadius: '100px', background: '#fce8e4', color: '#8b4a3a', fontFamily: 'Manrope, sans-serif', fontSize: '0.6875rem', fontWeight: 500, padding: '3px 10px' }}>
          {t[GOAL_LABEL_MAP[report.goal_type] as keyof HealthPageTranslations] as string}
        </span>
        <span style={{ fontFamily: 'Manrope, sans-serif', fontWeight: 600, fontSize: '0.875rem', color: '#2e342b' }}>
          {report.daily_calories.toLocaleString()} {t.kcalPerDay}
        </span>
        <ChevronDown size={16} color="#adb4a8" />
      </div>
    )
  }

  return (
    <div style={{ animation: 'reportIn 300ms ease', marginBottom: '24px' }}>
      <style>{`@keyframes reportIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: none; } }`}</style>

      {/* Hero: Daily Calorie Target */}
      <div style={{ textAlign: 'center', marginBottom: '24px' }}>
        <p style={{ ...microLabel, marginBottom: '8px' }}>{t.yourDailyTargets}</p>
        <div style={{ fontFamily: 'Newsreader, serif', fontWeight: 300, fontSize: '2.5rem', color: '#4b6646', lineHeight: 1 }}>
          {report.daily_calories.toLocaleString()}
          <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '1rem', color: '#767d72', marginLeft: '8px', fontWeight: 400 }}>{t.kcalPerDay}</span>
        </div>
        <span style={{ display: 'inline-block', marginTop: '8px', borderRadius: '100px', background: '#fce8e4', color: '#8b4a3a', fontFamily: 'Manrope, sans-serif', fontSize: '0.6875rem', fontWeight: 500, padding: '4px 12px' }}>
          {t[GOAL_LABEL_MAP[report.goal_type] as keyof HealthPageTranslations] as string}
        </span>
        {isLatest && (
          <span style={{ display: 'inline-block', marginTop: '8px', marginLeft: '8px', borderRadius: '100px', background: '#f1f5eb', color: '#4b6646', fontFamily: 'Manrope, sans-serif', fontSize: '0.6875rem', fontWeight: 500, padding: '4px 12px' }}>
            {t.latestReport}
          </span>
        )}
      </div>

      {/* Warnings */}
      {warnings.length > 0 && (
        <div style={{ marginBottom: '20px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {warnings.map((w, i) => (
            <div key={i} style={{ background: '#fdf0ed', borderRadius: '0 12px 12px 12px', padding: '12px 16px', display: 'flex', gap: '10px', alignItems: 'flex-start', animation: `reportIn 300ms ease ${100 + i * 50}ms both` }}>
              <TriangleAlert size={16} color="#8b4a3a" style={{ flexShrink: 0, marginTop: '2px' }} />
              <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#2e342b', lineHeight: 1.5 }}>{w.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* BMR Breakdown */}
      <div style={{ background: '#ffffff', borderRadius: '0 16px 16px 16px', padding: '24px', marginBottom: '16px', boxShadow: '0 2px 8px rgba(46,52,43,0.06)' }}>
        <p style={{ ...microLabel, marginBottom: '16px' }}>{t.bmrBreakdown}</p>
        {((): Array<{ label: string; value: React.ReactNode }> => [
          { label: t.method, value: <span style={{ borderRadius: '100px', background: '#f1f5eb', color: '#5a6157', fontSize: '0.75rem', padding: '3px 10px' }}>{report.method_used === 'katch_mcardle' ? t.katchMcardle : t.mifflinStJeor}</span> },
          ...(report.lean_body_mass != null ? [{ label: t.leanBodyMass, value: `${report.lean_body_mass.toFixed(1)} kg` }] : []),
          { label: t.bmr, value: `${report.bmr.toLocaleString()} ${t.kcalPerDay}` },
          { label: t.activity, value: `${t[ACTIVITY_LABEL_MAP[report.activity_level] as keyof HealthPageTranslations] as string} (×${report.activity_multiplier})` },
          { label: t.tdee, value: `${report.tdee.toLocaleString()} ${t.kcalPerDay}` },
          ...(report.delta_kcal_per_day != null ? [{ label: t.dailyAdjustment, value: `${report.delta_kcal_per_day > 0 ? '+' : ''}${report.delta_kcal_per_day.toFixed(0)} kcal` }] : []),
        ])().map(({ label, value }, i) => (
          <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '6px 0', borderBottom: '1px solid rgba(173,180,168,0.1)' }}>
            <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>{label}</span>
            <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', fontWeight: 600, color: '#2e342b' }}>{value}</span>
          </div>
        ))}
      </div>

      {/* Macro Table */}
      <div style={{ background: '#ffffff', borderRadius: '0 16px 16px 16px', padding: '24px', marginBottom: '16px', boxShadow: '0 2px 8px rgba(46,52,43,0.06)' }}>
        <p style={{ ...microLabel, marginBottom: '16px' }}>{t.macroTargets}</p>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0' }}>
          {[['', t.daily, t.monthlyX30],
            [t.protein, `${report.protein_g_per_day.toFixed(0)}g`, `${report.monthly_protein_g.toFixed(0)}g`],
            [t.fat, `${report.fat_g_per_day.toFixed(0)}g`, `${report.monthly_fat_g.toFixed(0)}g`],
            [t.carbs, `${report.carbs_g_per_day.toFixed(0)}g`, `${report.monthly_carbs_g.toFixed(0)}g`],
            [t.fiber, `${report.fiber_g_per_day.toFixed(0)}g`, `${report.monthly_fiber_g.toFixed(0)}g`],
            [t.kcalPerDay, `${report.daily_calories.toLocaleString()}`, `${report.monthly_calories.toLocaleString()}`],
          ].map((row, ri) => (
            row.map((cell, ci) => (
              <div
                key={`${ri}-${ci}`}
                style={{
                  padding: '8px 4px',
                  background: ri % 2 === 0 ? '#f8faf2' : '#ffffff',
                  fontFamily: 'Manrope, sans-serif',
                  fontSize: ri === 0 ? '0.6875rem' : '0.875rem',
                  fontWeight: ri === 0 ? 700 : (ci === 0 ? 400 : 600),
                  color: ri === 0 ? '#8b4a3a' : (ci === 2 ? '#767d72' : '#2e342b'),
                  textTransform: ri === 0 ? 'uppercase' : 'none',
                  letterSpacing: ri === 0 ? '0.04em' : 'normal',
                  borderBottom: '1px solid rgba(173,180,168,0.08)',
                }}
              >
                {cell}
              </div>
            ))
          ))}
        </div>
      </div>

      {/* Delta Breakdown (expandable) */}
      {report.goal_type !== 'maintain' && report.delta_bw != null && (
        <div style={{ marginBottom: '8px' }}>
          <button
            type="button"
            onClick={() => setDeltaOpen(o => !o)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px', fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#5a6157', padding: '8px 0', minHeight: '44px' }}
          >
            <ChevronDown size={14} style={{ transform: deltaOpen ? 'rotate(180deg)' : 'none', transition: 'transform 0.2s' }} />
            {t.deltaBreakdown}
          </button>
          {deltaOpen && (
            <div style={{ paddingLeft: '20px', borderLeft: '2px solid rgba(173,180,168,0.2)' }}>
              {[
                [t.deltaBodyWeight, `${report.delta_bw! > 0 ? '+' : ''}${report.delta_bw!.toFixed(2)} kg`],
                [t.kcalPerKgAssumption, `${report.kcal_per_kg_used?.toLocaleString()} kcal/kg`],
                [t.totalKcalDelta, `${report.total_delta_kcal!.toLocaleString()} kcal`],
                [t.dailyKcalAdjustment, `${report.delta_kcal_per_day! > 0 ? '+' : ''}${report.delta_kcal_per_day!.toFixed(0)} kcal/day`],
              ].map(([label, value], i) => (
                <div key={i} style={{ display: 'flex', justifyContent: 'space-between', padding: '5px 0', fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#5a6157' }}>
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
