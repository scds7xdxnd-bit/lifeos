'use client';

import type { Translations } from '../translations';
import { Card } from '../components/Card';
import { MicroLabel } from '../components/MicroLabel';
import { colors, typography } from '../tokens';

interface FeaturesProps {
  t: Translations['features'];
}

const UnifiedIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" width="40" height="40" aria-hidden="true">
    <circle cx="20" cy="20" r="20" fill={colors.primaryContainer} />
    <rect x="12" y="12" width="7" height="7" rx="1.5" stroke={colors.primary} strokeWidth="1.8" />
    <rect x="21" y="12" width="7" height="7" rx="1.5" stroke={colors.primary} strokeWidth="1.8" />
    <rect x="12" y="21" width="7" height="7" rx="1.5" stroke={colors.primary} strokeWidth="1.8" />
    <rect x="21" y="21" width="7" height="7" rx="1.5" stroke={colors.primary} strokeWidth="1.8" />
  </svg>
);

const InsightIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" width="40" height="40" aria-hidden="true">
    <circle cx="20" cy="20" r="20" fill={colors.primaryContainer} />
    <path d="M12 28l5-8 4 5 4-10 3 6" stroke={colors.primaryDim} strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

const InquiryIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" width="40" height="40" aria-hidden="true">
    <circle cx="20" cy="20" r="20" fill={colors.primaryContainer} />
    <path d="M13 20h14M20 13v14" stroke={colors.primary} strokeWidth="2.2" strokeLinecap="round" />
    <circle cx="20" cy="20" r="7" stroke={colors.darkAccent} strokeWidth="1.8" />
  </svg>
);

const ICONS = [UnifiedIcon, InsightIcon, InquiryIcon];

export const Features = ({ t }: FeaturesProps) => (
  <section id="features" style={{ padding: '120px 48px', background: colors.surfaceContainerLow }}>
    <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
      <div style={{ textAlign: 'center', marginBottom: '64px' }}>
        <MicroLabel style={{ marginBottom: '16px', display: 'block' }}>{t.eyebrow}</MicroLabel>
        <h2
          style={{
            ...typography.headline,
            fontSize: 'clamp(2rem, 3vw, 2.8rem)',
            color: colors.onSurface,
            margin: 0,
            lineHeight: 1.2,
          }}
        >
          {t.headline}
        </h2>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px' }}>
        {t.items.map(({ title, body }, i) => {
          const Icon = ICONS[i];
          return (
            <Card key={title} style={{ padding: '36px 32px' }}>
              <div style={{ marginBottom: '20px' }}><Icon /></div>
              <h3 style={{ ...typography.headline, fontSize: '1.2rem', color: colors.onSurface, margin: '0 0 12px' }}>
                {title}
              </h3>
              <p style={{ ...typography.body, fontSize: '0.95rem', color: colors.onSurfaceVariant, margin: 0 }}>
                {body}
              </p>
            </Card>
          );
        })}
      </div>
    </div>
  </section>
);
