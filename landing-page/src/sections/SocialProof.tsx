import type { Translations } from '../translations';
import { Card } from '../components/Card';
import { colors, fonts, typography } from '../tokens';

interface SocialProofProps {
  t: Translations['social'];
}

export const SocialProof = ({ t }: SocialProofProps) => (
  <section style={{ padding: '100px 48px', background: colors.surfaceContainerLow }}>
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <h2
        style={{
          ...typography.headline,
          fontSize: 'clamp(1.8rem, 2.8vw, 2.4rem)',
          color: colors.onSurface,
          textAlign: 'center',
          margin: '0 0 56px',
        }}
      >
        {t.headline}
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        {t.items.map(({ quote, name, role }) => (
          <Card key={name} style={{ padding: '32px' }}>
            <p
              style={{
                fontSize: '0.97rem',
                color: colors.onSurfaceVariant,
                lineHeight: 1.7,
                margin: '0 0 24px',
                fontStyle: 'italic',
                fontFamily: fonts.serif,
              }}
            >
              &ldquo;{quote}&rdquo;
            </p>
            <p
              style={{
                ...typography.label,
                color: colors.onSurface,
                margin: 0,
                fontSize: '0.92rem',
              }}
            >
              {name}
            </p>
            <p
              style={{
                color: colors.outline,
                margin: '2px 0 0',
                fontSize: '0.82rem',
                fontFamily: fonts.sans,
              }}
            >
              {role}
            </p>
          </Card>
        ))}
      </div>
    </div>
  </section>
);
