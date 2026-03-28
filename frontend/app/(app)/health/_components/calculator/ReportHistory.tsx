'use client'

import { useState } from 'react'
import { ChevronDown, Pencil, Trash2 } from 'lucide-react'
import type { CalorieReport } from '@/lib/api/calculator'
import type { HealthPageTranslations } from '@/lib/translations/app'

interface ReportHistoryProps {
  reports: CalorieReport[]
  isLoading: boolean
  total: number
  page: number
  pages: number
  onPageChange: (page: number) => void
  activeReportId: number | null
  onSelect: (report: CalorieReport) => void
  onEdit: (report: CalorieReport) => void
  onDelete: (id: number) => void
  isDeleting: boolean
  deletingId: number | null
  t: HealthPageTranslations
}

const GOAL_LABELS: Record<string, keyof HealthPageTranslations> = {
  lose: 'lose',
  gain: 'gain',
  maintain: 'maintain',
}

export default function ReportHistory({
  reports, isLoading, total, page, pages, onPageChange,
  activeReportId, onSelect, onEdit, onDelete, isDeleting, deletingId, t,
}: ReportHistoryProps) {
  const [confirmDeleteId, setConfirmDeleteId] = useState<number | null>(null)

  if (isLoading) return null

  if (reports.length === 0) {
    return (
      <p style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', color: '#767d72', padding: '16px 0' }}>
        {t.noReportsYet}
      </p>
    )
  }

  return (
    <div>
      {reports.map((report, idx) => {
        const isActive = activeReportId === report.id
        const isThisDeleting = isDeleting && deletingId === report.id
        const showConfirm = confirmDeleteId === report.id

        return (
          <div
            key={report.id}
            style={{
              background: isActive ? '#f1f5eb' : '#f8faf2',
              borderRadius: '0 10px 10px 10px',
              marginBottom: '8px',
              overflow: 'hidden',
              animation: `rowIn 300ms ease ${idx * 35}ms both`,
              outline: isActive ? '1.5px solid #4b6646' : 'none',
              opacity: isThisDeleting ? 0.5 : 1,
              transition: 'opacity 0.2s, outline 0.15s',
            }}
          >
            <style>{`@keyframes rowIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: none; } }`}</style>

            <div style={{ padding: '12px 16px', display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              {/* Date + goal badge — clickable to view in panel */}
              <button
                type="button"
                onClick={() => onSelect(report)}
                style={{
                  flex: 1, display: 'flex', alignItems: 'center', gap: '10px',
                  background: 'none', border: 'none', cursor: 'pointer', padding: 0, textAlign: 'left',
                  minHeight: '44px',
                }}
              >
                <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.8125rem', color: '#5a6157' }}>
                  {new Date(report.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' })}
                </span>
                <span style={{ borderRadius: '100px', background: '#fce8e4', color: '#8b4a3a', fontFamily: 'Manrope, sans-serif', fontSize: '0.6875rem', fontWeight: 500, padding: '3px 10px', whiteSpace: 'nowrap' }}>
                  {t[GOAL_LABELS[report.goal_type] as keyof HealthPageTranslations] as string}
                </span>
                <span style={{ fontFamily: 'Manrope, sans-serif', fontWeight: 600, fontSize: '0.875rem', color: '#2e342b', whiteSpace: 'nowrap' }}>
                  {report.daily_calories.toLocaleString()} {t.kcalPerDay}
                </span>
                {isActive && (
                  <ChevronDown size={14} color="#4b6646" style={{ marginLeft: 'auto', flexShrink: 0 }} />
                )}
              </button>

              {/* Action buttons */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px', flexShrink: 0 }}>
                {/* Edit button */}
                <button
                  type="button"
                  onClick={() => { setConfirmDeleteId(null); onEdit(report) }}
                  aria-label={t.editReport}
                  title={t.editReport}
                  style={{
                    background: 'none', border: 'none', cursor: 'pointer',
                    color: '#adb4a8', padding: '6px', display: 'flex', alignItems: 'center',
                    borderRadius: '6px', minHeight: '36px', transition: 'color 0.15s',
                  }}
                  onMouseEnter={e => (e.currentTarget.style.color = '#4b6646')}
                  onMouseLeave={e => (e.currentTarget.style.color = '#adb4a8')}
                >
                  <Pencil size={13} />
                </button>

                {/* Delete — inline confirm */}
                {showConfirm ? (
                  <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.75rem', color: '#8b4a3a', whiteSpace: 'nowrap' }}>
                      {t.confirmDeleteReport}
                    </span>
                    <button
                      type="button"
                      onClick={() => { onDelete(report.id); setConfirmDeleteId(null) }}
                      disabled={isThisDeleting}
                      style={{
                        background: '#fce8e4', border: 'none', cursor: 'pointer',
                        borderRadius: '100px', padding: '4px 10px',
                        fontFamily: 'Manrope, sans-serif', fontSize: '0.75rem', fontWeight: 600,
                        color: '#8b4a3a', minHeight: '28px',
                      }}
                    >
                      {t.yes}
                    </button>
                    <button
                      type="button"
                      onClick={() => setConfirmDeleteId(null)}
                      style={{
                        background: '#f1f5eb', border: 'none', cursor: 'pointer',
                        borderRadius: '100px', padding: '4px 10px',
                        fontFamily: 'Manrope, sans-serif', fontSize: '0.75rem', fontWeight: 600,
                        color: '#5a6157', minHeight: '28px',
                      }}
                    >
                      {t.no}
                    </button>
                  </div>
                ) : (
                  <button
                    type="button"
                    onClick={() => setConfirmDeleteId(report.id)}
                    aria-label={t.deleteReport}
                    title={t.deleteReport}
                    disabled={isThisDeleting}
                    style={{
                      background: 'none', border: 'none', cursor: 'pointer',
                      color: '#adb4a8', padding: '6px', display: 'flex', alignItems: 'center',
                      borderRadius: '6px', minHeight: '36px', transition: 'color 0.15s',
                    }}
                    onMouseEnter={e => (e.currentTarget.style.color = '#e8735c')}
                    onMouseLeave={e => (e.currentTarget.style.color = '#adb4a8')}
                  >
                    <Trash2 size={13} />
                  </button>
                )}
              </div>
            </div>
          </div>
        )
      })}

      {/* Pagination */}
      {pages > 1 && (
        <div style={{ display: 'flex', gap: '8px', justifyContent: 'center', marginTop: '16px' }}>
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
            style={{ borderRadius: '100px', padding: '8px 20px', fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', background: '#f1f5eb', color: '#4b6646', border: 'none', cursor: page > 1 ? 'pointer' : 'not-allowed', opacity: page > 1 ? 1 : 0.4, minHeight: '44px' }}
          >
            ←
          </button>
          <span style={{ fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', color: '#5a6157', padding: '8px 12px', alignSelf: 'center' }}>
            {page} / {pages}
          </span>
          <button
            type="button"
            disabled={page >= pages}
            onClick={() => onPageChange(page + 1)}
            style={{ borderRadius: '100px', padding: '8px 20px', fontFamily: 'Manrope, sans-serif', fontSize: '0.875rem', background: '#f1f5eb', color: '#4b6646', border: 'none', cursor: page < pages ? 'pointer' : 'not-allowed', opacity: page < pages ? 1 : 0.4, minHeight: '44px' }}
          >
            →
          </button>
        </div>
      )}
    </div>
  )
}
