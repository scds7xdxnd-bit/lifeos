import type { Translations } from '../translations';
import { MicroLabel } from '../components/MicroLabel';
import { colors, fonts, typography } from '../tokens';

interface HowItWorksProps {
  t: Translations['howItWorks'];
}

export const HowItWorks = ({ t }: HowItWorksProps) => (
  <section style={{ padding: '120px 48px', background: colors.background }}>
    <div style={{ maxWidth: '880px', margin: '0 auto', textAlign: 'center' }}>
      <MicroLabel style={{ marginBottom: '16px', display: 'block' }}>
        {t.eyebrow}
      </MicroLabel>
      <h2
        style={{
          ...typography.headline,
          fontSize: 'clamp(2rem, 3vw, 2.8rem)',
          color: colors.onSurface,
          margin: '0 0 64px',
          lineHeight: 1.2,
        }}
      >
        {t.headline}
      </h2>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '48px' }}>
        {t.steps.map(({ step, title, body }) => (
          <div
            key={step}
            style={{ textAlign: 'left', padding: '24px 0' }}
            onMouseEnter={(e) => {
              const num = e.currentTarget.querySelector<HTMLElement>('[data-step]');
              if (num) num.style.color = colors.primary;
            }}
            onMouseLeave={(e) => {
              const num = e.currentTarget.querySelector<HTMLElement>('[data-step]');
              if (num) num.style.color = colors.surfaceContainer;
            }}
          >
            <span
              data-step
              style={{
                display: 'block',
                fontFamily: fonts.serif,
                fontSize: '2.5rem',
                fontWeight: 300,
                color: colors.surfaceContainer,
                marginBottom: '16px',
                letterSpacing: '-0.03em',
                transition: 'color 0.25s ease',
              }}
            >
              {step}
            </span>
            <h3
              style={{
                ...typography.headline,
                fontSize: '1.15rem',
                color: colors.onSurface,
                margin: '0 0 12px',
              }}
            >
              {title}
            </h3>
            <p
              style={{
                ...typography.body,
                fontSize: '0.95rem',
                color: colors.onSurfaceVariant,
                margin: 0,
              }}
            >
              {body}
            </p>
          </div>
        ))}
      </div>
    </div>
  </section>
);
