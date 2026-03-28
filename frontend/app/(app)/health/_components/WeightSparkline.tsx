'use client'

interface WeightSparklineProps {
  entries: Array<{ date: string; weight: number }>
}

export default function WeightSparkline({ entries }: WeightSparklineProps) {
  const W = 200
  const H = 48

  if (entries.length === 0) {
    return (
      <svg width={W} height={H} aria-label="No weight data">
        <line x1={0} y1={H / 2} x2={W} y2={H / 2} stroke="#dee5d7" strokeWidth={1.5} strokeDasharray="4 4" />
        <text x={W / 2} y={H / 2 + 12} textAnchor="middle" fill="#767d72" fontSize="10" fontFamily="var(--font-manrope), sans-serif">
          No data
        </text>
      </svg>
    )
  }

  if (entries.length === 1) {
    return (
      <svg width={W} height={H} aria-label={`Weight: ${entries[0].weight} kg`}>
        <line x1={0} y1={H / 2} x2={W} y2={H / 2} stroke="#8b4a3a" strokeWidth={1.5} />
        <circle cx={W / 2} cy={H / 2} r={3} fill="#8b4a3a" />
      </svg>
    )
  }

  const weights = entries.map(e => e.weight)
  const minW = Math.min(...weights)
  const maxW = Math.max(...weights)
  const range = maxW - minW || 1
  const pad = 4

  const points = entries.map((e, i) => {
    const x = (i / (entries.length - 1)) * (W - pad * 2) + pad
    const y = H - pad - ((e.weight - minW) / range) * (H - pad * 2)
    return { x, y }
  })

  const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${H} L ${points[0].x} ${H} Z`

  return (
    <svg width={W} height={H} aria-label="Weight trend sparkline">
      <defs>
        <linearGradient id="sparkArea" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#fce8e4" stopOpacity="0.5" />
          <stop offset="100%" stopColor="#fce8e4" stopOpacity="0.05" />
        </linearGradient>
      </defs>
      <path d={areaPath} fill="url(#sparkArea)" />
      <path d={linePath} fill="none" stroke="#8b4a3a" strokeWidth={1.5} strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={points[0].x} cy={points[0].y} r={3} fill="#8b4a3a" />
      <circle cx={points[points.length - 1].x} cy={points[points.length - 1].y} r={3} fill="#8b4a3a" />
    </svg>
  )
}
