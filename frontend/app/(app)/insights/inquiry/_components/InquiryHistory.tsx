'use client'

import type { Inquiry } from '@/lib/api/inquiries'
import { domainLabel, pairLabel, fmtDate } from './helpers'

interface InquiryHistoryProps {
  items: Inquiry[]
  isLoading: boolean
  selectedId: number | null
  onView: (inquiry: Inquiry) => void
  onRefine: (inquiry: Inquiry) => void
}

export function InquiryHistory({
  items,
  isLoading,
  selectedId,
  onView,
  onRefine,
}: InquiryHistoryProps) {
  if (isLoading) {
    return (
      <div className="glass rounded-2xl p-6">
        <h3 className="font-semibold text-foreground mb-4">Recent Inquiries</h3>
        <div className="space-y-2.5">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-white/30 rounded-xl animate-pulse" />
          ))}
        </div>
      </div>
    )
  }

  if (!items.length) {
    return (
      <div className="glass rounded-2xl p-6">
        <h3 className="font-semibold text-foreground mb-1.5">Recent Inquiries</h3>
        <p className="text-sm text-muted-foreground">No inquiries yet. Generate your first brief above.</p>
      </div>
    )
  }

  return (
    <div className="glass rounded-2xl p-6 space-y-4">
      <h3 className="font-semibold text-foreground">Recent Inquiries</h3>
      <ul className="space-y-2.5">
        {items.map((inq) => {
          const isSelected = inq.id === selectedId
          const domainDisplay =
            (inq.domains?.length ?? 0) > 1
              ? pairLabel(inq.domains)
              : domainLabel(inq.domain)

          return (
            <li
              key={inq.id}
              className={`rounded-xl px-4 py-3.5 transition-all ${
                isSelected
                  ? 'bg-white/70 shadow-sm'
                  : 'bg-white/30 hover:bg-white/50'
              }`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-foreground truncate">{inq.question}</p>
                  <div className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-0.5 text-xs text-muted-foreground">
                    <span>{domainDisplay}</span>
                    <span>·</span>
                    <span>{inq.timeframe?.start} → {inq.timeframe?.end}</span>
                    {inq.last_version_number > 1 && (
                      <>
                        <span>·</span>
                        <span>v{inq.last_version_number}</span>
                      </>
                    )}
                    <span>·</span>
                    <span>{fmtDate(inq.created_at)}</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <button
                    type="button"
                    onClick={() => onView(inq)}
                    className={`text-xs px-3 py-1.5 rounded-full transition-all ${
                      isSelected
                        ? 'bg-primary text-primary-foreground'
                        : 'bg-white/50 text-foreground hover:bg-white/70 border border-white/40'
                    }`}
                  >
                    View
                  </button>
                  <button
                    type="button"
                    onClick={() => onRefine(inq)}
                    className="text-xs px-3 py-1.5 rounded-full bg-white/50 text-muted-foreground hover:text-foreground hover:bg-white/70 border border-white/40 transition-all"
                  >
                    Refine
                  </button>
                </div>
              </div>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
