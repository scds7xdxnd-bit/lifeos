'use client'

import { useState, useEffect, useRef } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { ChevronDown } from 'lucide-react'
import { calculatorApi, type CalorieReport, type Warning, type CalculatorInput } from '@/lib/api/calculator'
import type { HealthPageTranslations } from '@/lib/translations/app'
import CalculatorForm from './CalculatorForm'
import ReportCard from './ReportCard'
import ReportHistory from './ReportHistory'

interface CalculatorPanelProps {
  t: HealthPageTranslations
}

interface ActiveReport {
  report: CalorieReport
  warnings: Warning[]
  isLatest: boolean
}

const CARD: React.CSSProperties = {
  background: '#ffffff',
  borderRadius: '0 16px 16px 16px',
  padding: '24px',
  boxShadow: '0 4px 16px rgba(46,52,43,0.06)',
}

const SECTION_TOGGLE: React.CSSProperties = {
  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
  width: '100%', background: 'none', border: 'none', cursor: 'pointer', padding: 0,
}

const MICRO_LABEL: React.CSSProperties = {
  fontFamily: 'Manrope, sans-serif', fontWeight: 700, fontSize: '0.6875rem',
  letterSpacing: '0.05em', textTransform: 'uppercase', color: '#8b4a3a',
}

export default function CalculatorPanel({ t }: CalculatorPanelProps) {
  const queryClient = useQueryClient()
  const [historyPage, setHistoryPage] = useState(1)
  const [formCollapsed, setFormCollapsed] = useState(false)
  const [historyCollapsed, setHistoryCollapsed] = useState(false)

  const [activeReport, setActiveReport] = useState<ActiveReport | null>(null)
  const initialLoadDone = useRef(false)

  const [editingReportId, setEditingReportId] = useState<number | null>(null)
  const [editingReport, setEditingReport] = useState<CalorieReport | null>(null)

  const { data: prefillData, isLoading: prefillLoading } = useQuery({
    queryKey: ['health', 'calculator', 'prefill'],
    queryFn: () => calculatorApi.getPrefill(),
  })

  const { data: latestData } = useQuery({
    queryKey: ['health', 'calculator', 'latest'],
    queryFn: () => calculatorApi.getLatestReport(),
  })

  const { data: historyData, isLoading: historyLoading } = useQuery({
    queryKey: ['health', 'calculator', 'reports', historyPage],
    queryFn: () => calculatorApi.listReports({ page: historyPage }),
  })

  useEffect(() => {
    if (latestData?.report && !initialLoadDone.current) {
      initialLoadDone.current = true
      setActiveReport({ report: latestData.report, warnings: [], isLatest: true })
    }
  }, [latestData])

  const calculateMutation = useMutation({
    mutationFn: (input: CalculatorInput) => calculatorApi.calculate(input),
    onSuccess: (data) => {
      setActiveReport({ report: data.report, warnings: data.warnings, isLatest: true })
      setEditingReportId(null)
      setEditingReport(null)
      queryClient.invalidateQueries({ queryKey: ['health', 'calculator'] })
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, input }: { id: number; input: CalculatorInput }) =>
      calculatorApi.updateReport(id, input),
    onSuccess: (data) => {
      setActiveReport({ report: data.report, warnings: data.warnings, isLatest: false })
      setEditingReportId(null)
      setEditingReport(null)
      queryClient.invalidateQueries({ queryKey: ['health', 'calculator'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: number) => calculatorApi.deleteReport(id),
    onSuccess: (_data, deletedId) => {
      if (activeReport?.report.id === deletedId) setActiveReport(null)
      queryClient.invalidateQueries({ queryKey: ['health', 'calculator'] })
    },
  })

  function handleCalculate(input: CalculatorInput) {
    if (editingReportId) {
      updateMutation.mutate({ id: editingReportId, input: { ...input, save_profile: false } })
    } else {
      calculateMutation.mutate(input)
    }
  }

  function handleSelectHistory(report: CalorieReport) {
    setActiveReport({ report, warnings: [], isLatest: false })
    setEditingReportId(null)
    setEditingReport(null)
  }

  function handleEditReport(report: CalorieReport) {
    setEditingReportId(report.id)
    setEditingReport(report)
    setFormCollapsed(false)
  }

  const isCalculating = calculateMutation.isPending || updateMutation.isPending

  return (
    <div style={{ maxWidth: '1100px', margin: '0 auto', padding: '0 0 48px' }}>
      {/* Header */}
      <div style={{ marginBottom: '28px' }}>
        <p style={{ ...MICRO_LABEL, marginBottom: '4px' }}>{t.calorieCalculator}</p>
        <h2 style={{ fontFamily: 'Newsreader, serif', fontWeight: 300, fontSize: '1.75rem', color: '#4b6646', margin: '4px 0', letterSpacing: '-0.02em' }}>
          {t.planTargets}
        </h2>
        <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.9rem', color: '#767d72', margin: 0 }}>
          {t.planTargetsSub}
        </p>
      </div>

      {/* Two-column layout */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(0,1fr) minmax(0,1fr)', gap: 24, alignItems: 'start' }}>

        {/* ── Left: form + history ── */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

          {/* Calculator form card */}
          <div style={CARD}>
            <button type="button" onClick={() => setFormCollapsed(v => !v)} style={SECTION_TOGGLE}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={MICRO_LABEL}>{t.calculator}</span>
                {editingReportId && (
                  <span style={{ borderRadius: '100px', background: '#fce8e4', color: '#8b4a3a', fontFamily: 'Manrope, sans-serif', fontSize: '0.6875rem', fontWeight: 600, padding: '3px 10px' }}>
                    {t.editingReport}
                  </span>
                )}
              </span>
              <ChevronDown
                size={14} color="#8b4a3a"
                style={{ transform: formCollapsed ? 'rotate(-90deg)' : '', transition: 'transform 0.2s', flexShrink: 0 }}
              />
            </button>

            {!formCollapsed && (
              <div style={{ marginTop: 20 }}>
                {editingReportId && (
                  <div style={{ marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
                    <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#8b4a3a', fontWeight: 600 }}>
                      {t.editingReport}
                    </span>
                    <button
                      type="button"
                      onClick={() => { setEditingReportId(null); setEditingReport(null) }}
                      style={{ background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#767d72', textDecoration: 'underline', padding: 0 }}
                    >
                      {t.cancel}
                    </button>
                  </div>
                )}
                <CalculatorForm
                  prefillData={prefillData ?? null}
                  isLoading={prefillLoading}
                  onCalculate={handleCalculate}
                  isCalculating={isCalculating}
                  editingReport={editingReport}
                  isEditMode={!!editingReportId}
                  t={t}
                />
              </div>
            )}
          </div>

          {/* Past reports card */}
          <div style={CARD}>
            <button type="button" onClick={() => setHistoryCollapsed(v => !v)} style={SECTION_TOGGLE}>
              <span style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <span style={MICRO_LABEL}>{t.pastReports}</span>
                {historyData?.total != null && historyData.total > 0 && (
                  <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.6875rem', color: '#adb4a8', fontWeight: 400 }}>
                    ({historyData.total})
                  </span>
                )}
              </span>
              <ChevronDown
                size={14} color="#8b4a3a"
                style={{ transform: historyCollapsed ? 'rotate(-90deg)' : '', transition: 'transform 0.2s', flexShrink: 0 }}
              />
            </button>

            {!historyCollapsed && (
              <div style={{ marginTop: 16 }}>
                <ReportHistory
                  reports={historyData?.reports ?? []}
                  isLoading={historyLoading}
                  total={historyData?.total ?? 0}
                  page={historyPage}
                  pages={historyData?.pages ?? 1}
                  onPageChange={setHistoryPage}
                  activeReportId={activeReport?.report.id ?? null}
                  onSelect={handleSelectHistory}
                  onEdit={handleEditReport}
                  onDelete={(id) => deleteMutation.mutate(id)}
                  isDeleting={deleteMutation.isPending}
                  deletingId={deleteMutation.variables ?? null}
                  t={t}
                />
              </div>
            )}
          </div>
        </div>

        {/* ── Right: active report ── */}
        <div style={{ position: 'sticky', top: 24 }}>
          {activeReport ? (
            <ReportCard
              report={activeReport.report}
              warnings={activeReport.warnings}
              isLatest={activeReport.isLatest}
              expanded={true}
              t={t}
            />
          ) : (
            <div style={{ ...CARD, padding: '48px 32px', textAlign: 'center', border: '1.5px dashed rgba(173,180,168,0.35)' }}>
              {/* Botanical leaf icon */}
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none" style={{ marginBottom: 20 }}>
                <path
                  d="M24 6C14 6 8 16 8 26c0 8 6 14 16 14 2 0 0 0 0 0V26"
                  stroke="#adb4a8" strokeWidth="1.5" strokeLinecap="round" fill="none"
                />
                <path
                  d="M24 6c10 0 16 10 16 20 0 8-6 14-16 14V6Z"
                  fill="#f1f5eb" stroke="#adb4a8" strokeWidth="1.5" strokeLinejoin="round"
                />
                <line x1="24" y1="26" x2="24" y2="42" stroke="#adb4a8" strokeWidth="1.5" strokeLinecap="round" />
                <path d="M24 32c-4-3-8-3-10-2" stroke="#adb4a8" strokeWidth="1.2" strokeLinecap="round" fill="none" />
                <path d="M24 38c-3-2-6-2-8-1" stroke="#adb4a8" strokeWidth="1.2" strokeLinecap="round" fill="none" />
              </svg>

              <p style={{ ...MICRO_LABEL, marginBottom: 10 }}>{t.yourDailyTargets}</p>
              <p style={{ fontFamily: 'Newsreader, serif', fontWeight: 300, fontSize: '1.25rem', color: '#4b6646', margin: '0 0 8px', letterSpacing: '-0.01em' }}>
                {t.reportEmptyTitle}
              </p>
              <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#adb4a8', margin: '0 0 28px', lineHeight: 1.6 }}>
                {t.reportEmptySubtitle}
              </p>

              {/* Step hints */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, textAlign: 'left', maxWidth: 220, margin: '0 auto' }}>
                {[
                  { n: '1', label: t.stepMeasurements },
                  { n: '2', label: t.stepGoal },
                  { n: '3', label: t.stepResults },
                ].map(({ n, label }) => (
                  <div key={n} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                    <span style={{
                      width: 22, height: 22, borderRadius: '100px',
                      background: '#f1f5eb', color: '#4b6646',
                      fontFamily: 'Manrope, sans-serif', fontSize: '0.6875rem', fontWeight: 700,
                      display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0,
                    }}>
                      {n}
                    </span>
                    <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#767d72' }}>
                      {label}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
