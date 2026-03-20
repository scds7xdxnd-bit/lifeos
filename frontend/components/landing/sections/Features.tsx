'use client';

import type { Translations } from '../translations';
import { MicroLabel } from '../components/MicroLabel';
import { ScrollReveal, StaggerChildren, StaggerItem } from '../components/Motion';
import { useBreakpoint } from '../hooks/useBreakpoint';
import { colors, fonts, typography, shadows, radii, spacing } from '../tokens';

interface DomainsProps {
  t: Translations['domains'];
}

/* ── Inline SVG icons ──────────────────────────────────────── */

const FinanceIcon = (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
    <rect x="4" y="16" width="5" height="8" rx="1.5" fill="currentColor" opacity="0.4" />
    <rect x="11.5" y="10" width="5" height="14" rx="1.5" fill="currentColor" opacity="0.65" />
    <rect x="19" y="5" width="5" height="19" rx="1.5" fill="currentColor" />
  </svg>
);

const JournalIcon = (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
    <path
      d="M6 22V6a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v16"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path
      d="M6 22a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
    />
    <path d="M10 9h8M10 13h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
  </svg>
);

const HealthIcon = (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
    <path
      d="M14 24s-9-6.5-9-12.5C5 7.4 7.7 5 11 5c1.8 0 3.4.9 3 2.2C14.4 5.9 16.2 5 18 5c3.3 0 6 2.4 6 6.5 0 6-9 12.5-9 12.5z"
      fill="currentColor"
    />
  </svg>
);

const RelationshipsIcon = (
  <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
    <circle cx="10" cy="10" r="4" fill="currentColor" opacity="0.6" />
    <circle cx="18" cy="10" r="4" fill="currentColor" opacity="0.4" />
    <circle cx="14" cy="18" r="4" fill="currentColor" />
  </svg>
);

const icons = [FinanceIcon, JournalIcon, HealthIcon, RelationshipsIcon];

const iconColors = [
  { bg: colors.primaryContainer, fg: colors.primary, hoverBg: colors.primary, hoverFg: '#ffffff' },
  { bg: colors.accentAmberContainer, fg: colors.accentAmber, hoverBg: colors.accentAmber, hoverFg: '#ffffff' },
  { bg: colors.accentCoralContainer, fg: colors.accentCoral, hoverBg: colors.accentCoral, hoverFg: '#ffffff' },
  { bg: colors.secondaryContainer, fg: colors.onSecondaryContainer, hoverBg: colors.onSecondaryContainer, hoverFg: '#ffffff' },
] as const;

export const Features = ({ t }: DomainsProps) => {
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';
  const isDesktop = bp === 'desktop';

  const gridCols = isMobile
    ? 'repeat(1, 1fr)'
    : bp === 'tablet'
      ? 'repeat(2, 1fr)'
      : 'repeat(4, 1fr)';

  return (
    <section
      id="features"
      style={{ padding: spacing.sectionPadding[bp], background: colors.surfaceContainerLow }}
    >
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <ScrollReveal style={{ textAlign: 'center', marginBottom: isMobile ? '40px' : '64px' }}>
          <MicroLabel style={{ marginBottom: '16px', display: 'block' }}>{t.eyebrow}</MicroLabel>
          <h2
            style={{
              ...typography.headline,
              fontStyle: 'italic',
              fontSize: 'clamp(2rem, 3.5vw, 3rem)',
              color: colors.onSurface,
              margin: '0 0 16px',
              lineHeight: 1.2,
            }}
          >
            {t.headline}
          </h2>
          <p
            style={{
              ...typography.body,
              fontSize: isMobile ? '1rem' : '1.1rem',
              color: colors.onSurfaceVariant,
              maxWidth: '600px',
              margin: '0 auto',
            }}
          >
            {t.sub}
          </p>
        </ScrollReveal>

        {/* Domain cards grid */}
        <StaggerChildren
          stagger={0.12}
          style={{ display: 'grid', gridTemplateColumns: gridCols, gap: isMobile ? '20px' : '28px' }}
        >
          {t.items.map((item, i) => (
            <StaggerItem key={item.title}>
              <div
                style={{
                  transform: isDesktop
                    ? i % 2 === 1
                      ? 'perspective(1000px) rotateX(2deg) rotateY(-2deg) translateY(32px)'
                      : 'perspective(1000px) rotateX(2deg) rotateY(-2deg)'
                    : 'none',
                  background: colors.surfaceContainerLowest,
                  borderRadius: radii.card,
                  padding: isMobile ? '24px' : '32px',
                  boxShadow: shadows.floating,
                  transition: 'transform 0.4s ease, box-shadow 0.4s ease',
                  display: 'flex',
                  flexDirection: 'column' as const,
                  gap: isMobile ? '16px' : '20px',
                  cursor: 'default',
                }}
                onMouseEnter={
                  isDesktop
                    ? (e) => {
                        const el = e.currentTarget;
                        el.style.transform =
                          i % 2 === 1
                            ? 'perspective(1000px) rotateX(0) rotateY(0) translateY(24px)'
                            : 'perspective(1000px) rotateX(0) rotateY(0) translateY(-8px)';
                        el.style.boxShadow = shadows.cardHover;
                        const iconEl = el.querySelector<HTMLElement>('[data-icon]');
                        if (iconEl) {
                          iconEl.style.background = iconColors[i].hoverBg;
                          iconEl.style.color = iconColors[i].hoverFg;
                        }
                      }
                    : undefined
                }
                onMouseLeave={
                  isDesktop
                    ? (e) => {
                        const el = e.currentTarget;
                        el.style.transform =
                          i % 2 === 1
                            ? 'perspective(1000px) rotateX(2deg) rotateY(-2deg) translateY(32px)'
                            : 'perspective(1000px) rotateX(2deg) rotateY(-2deg)';
                        el.style.boxShadow = shadows.floating;
                        const iconEl = el.querySelector<HTMLElement>('[data-icon]');
                        if (iconEl) {
                          iconEl.style.background = iconColors[i].bg;
                          iconEl.style.color = iconColors[i].fg;
                        }
                      }
                    : undefined
                }
              >
                {/* Decorative accent bar */}
                <div
                  style={{
                    width: '36px',
                    height: '3px',
                    borderRadius: '2px',
                    background: iconColors[i].fg,
                    opacity: 0.5,
                    marginBottom: isMobile ? '4px' : '8px',
                  }}
                />
                <div
                  data-icon=""
                  style={{
                    width: 56,
                    height: 56,
                    borderRadius: '50%',
                    background: iconColors[i].bg,
                    color: iconColors[i].fg,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    transition: 'background 0.5s ease, color 0.5s ease',
                  }}
                >
                  {icons[i]}
                </div>
                <h3
                  style={{
                    ...typography.headline,
                    fontSize: isMobile ? '1.3rem' : '1.5rem',
                    color: colors.onSurface,
                    margin: 0,
                  }}
                >
                  {item.title}
                </h3>
                <p
                  style={{
                    ...typography.body,
                    fontSize: '0.9rem',
                    color: colors.onSurfaceVariant,
                    margin: 0,
                  }}
                >
                  {item.body}
                </p>
                <div
                  style={{
                    paddingTop: '16px',
                    borderTop: `1px solid ${colors.surfaceContainerLow}`,
                    marginTop: 'auto',
                  }}
                >
                  <span
                    style={{
                      display: 'inline-block',
                      padding: '4px 12px',
                      borderRadius: '100px',
                      background: iconColors[i].bg,
                      color: iconColors[i].fg,
                      fontSize: '0.7rem',
                      fontWeight: 700,
                      letterSpacing: '0.08em',
                      textTransform: 'uppercase' as const,
                      fontFamily: fonts.sans,
                    }}
                  >
                    {item.stat}
                  </span>
                </div>
              </div>
            </StaggerItem>
          ))}
        </StaggerChildren>

        {/* Coming soon note */}
        <ScrollReveal delay={0.5} style={{ textAlign: 'center', marginTop: isMobile ? '32px' : '48px' }}>
          <p
            style={{
              ...typography.body,
              fontSize: '0.95rem',
              color: colors.outline,
              fontStyle: 'italic',
            }}
          >
            {t.comingSoon}
          </p>
        </ScrollReveal>
      </div>
    </section>
  );
};
