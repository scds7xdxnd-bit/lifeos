import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'LifeOS Tools',
}

export default function ToolsLayout({ children }: { children: React.ReactNode }) {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#f8faf2' }}>
      <main style={{ flex: 1 }}>
        {children}
      </main>
    </div>
  )
}
