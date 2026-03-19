'use client';

import type { Translations } from '../translations';
import { MicroLabel } from '../components/MicroLabel';
import { colors, fonts, typography } from '../tokens';

interface InquiryDemoProps {
  t: Translations['inquiry'];
}

export const InquiryDemo = ({ t }: InquiryDemoProps) => (
  <section style={{ padding: '100px 48px', background: colors.dark }}>
    <div style={{ maxWidth: '860px', margin: '0 auto', textAlign: 'center' }}>
      <MicroLabel color={colors.darkAccent} style={{ marginBottom: '16px', display: 'block' }}>
        {t.eyebrow}
      </MicroLabel>
      <h2
        style={{
          ...typography.headline,
          fontSize: 'clamp(1.8rem, 2.8vw, 2.6rem)',
          color: '#ffffff',
          margin: '0 0 16px',
          lineHeight: 1.2,
        }}
      >
        {t.headline}
      </h2>
      <p style={{ ...typography.body, fontSize: '1.05rem', color: colors.darkTextInactive, margin: '0 0 56px' }}>
        {t.sub}
      </p>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', textAlign: 'left' }}>
        {t.items.map(({ q, a }) => (
          <div
            key={q}
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              borderRadius: '0 16px 16px 16px',
              padding: '24px 28px',
              transition: 'background 0.2s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.background = 'rgba(255, 255, 255, 0.09)'; }}
            onMouseLeave={(e) => { e.currentTarget.style.background = 'rgba(255, 255, 255, 0.05)'; }}
          >
            <p style={{ fontSize: '0.9rem', color: colors.darkTextActive, margin: '0 0 10px', fontStyle: 'italic', fontFamily: fonts.serif }}>
              &ldquo;{q}&rdquo;
            </p>
            <p style={{ ...typography.body, fontSize: '0.97rem', color: '#ffffff', margin: 0 }}>
              {a}
            </p>
          </div>
        ))}
      </div>
    </div>
  </section>
);
