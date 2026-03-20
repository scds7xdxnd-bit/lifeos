'use client';

import type { Translations } from '../translations';
import { Card } from '../components/Card';
import { ScrollReveal } from '../components/Motion';
import { colors, fonts, typography, shadows, radii } from '../tokens';

interface InquiryBentoProps {
  t: Translations['inquiryBento'];
}

export const InquiryDemo = ({ t }: InquiryBentoProps) => (
  <section style={{ padding: '120px 48px', background: colors.background }}>
    <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
      {/* Header */}
      <ScrollReveal style={{ marginBottom: '64px' }}>
        <h2
          style={{
            ...typography.headline,
            fontStyle: 'italic',
            fontSize: 'clamp(2rem, 3.5vw, 3rem)',
            color: colors.onSurface,
            margin: '0 0 12px',
            lineHeight: 1.2,
          }}
        >
          {t.headline}
        </h2>
        <p
          style={{
            ...typography.body,
            fontSize: '1.1rem',
            color: colors.onSurfaceVariant,
            maxWidth: '600px',
          }}
        >
          {t.sub}
        </p>
      </ScrollReveal>

      {/* Bento grid: 7fr main + 5fr sidebar */}
      <div style={{ display: 'grid', gridTemplateColumns: '7fr 5fr', gap: '24px' }}>
        {/* Main inquiry card */}
        <ScrollReveal>
          <Card
            style={{
              padding: '40px',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              minHeight: '420px',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {/* Faint background decoration */}
            <svg
              style={{
                position: 'absolute',
                top: '24px',
                right: '24px',
                opacity: 0.04,
                width: '180px',
                height: '180px',
              }}
              viewBox="0 0 24 24"
              fill={colors.onSurface}
            >
              <circle cx="11" cy="11" r="8" fill="none" stroke={colors.onSurface} strokeWidth="2" />
              <path d="M21 21l-4.35-4.35" stroke={colors.onSurface} strokeWidth="2" strokeLinecap="round" />
            </svg>

            <div style={{ position: 'relative', zIndex: 1 }}>
              {/* Question */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '32px' }}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="12" r="10" fill={colors.primaryContainer} />
                  <path
                    d="M9 9a3 3 0 1 1 3 3v1"
                    stroke={colors.primary}
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                  <circle cx="12" cy="16" r="1" fill={colors.primary} />
                </svg>
                <h3
                  style={{
                    ...typography.headline,
                    fontSize: '1.5rem',
                    color: colors.onSurface,
                    margin: 0,
                  }}
                >
                  {t.question}
                </h3>
              </div>

              {/* Answer — pull-quote style */}
              <div
                style={{
                  padding: '20px 24px',
                  background: colors.surfaceContainerLow,
                  borderRadius: '12px',
                  borderLeft: `4px solid ${colors.primary}`,
                  marginBottom: '24px',
                }}
              >
                <p
                  style={{
                    ...typography.body,
                    fontStyle: 'italic',
                    color: colors.onSurface,
                    margin: 0,
                    lineHeight: 1.7,
                  }}
                >
                  &ldquo;{t.answer}&rdquo;
                </p>
              </div>

              {/* Source + Reference blocks */}
              <div style={{ display: 'flex', gap: '16px' }}>
                <div
                  style={{
                    flex: 1,
                    padding: '16px',
                    background: 'rgba(75, 102, 70, 0.08)',
                    borderRadius: '12px',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.7rem',
                      fontWeight: 700,
                      color: colors.primaryDim,
                      textTransform: 'uppercase' as const,
                      letterSpacing: '0.05em',
                      marginBottom: '8px',
                      fontFamily: fonts.sans,
                    }}
                  >
                    {t.sourceLabel}
                  </div>
                  <div
                    style={{
                      fontSize: '0.9rem',
                      fontWeight: 500,
                      fontFamily: fonts.sans,
                      color: colors.onSurface,
                    }}
                  >
                    {t.sourceValue}
                  </div>
                </div>
                <div
                  style={{
                    flex: 1,
                    padding: '16px',
                    background: 'rgba(214, 232, 206, 0.3)',
                    borderRadius: '12px',
                  }}
                >
                  <div
                    style={{
                      fontSize: '0.7rem',
                      fontWeight: 700,
                      color: colors.onSecondaryContainer,
                      textTransform: 'uppercase' as const,
                      letterSpacing: '0.05em',
                      marginBottom: '8px',
                      fontFamily: fonts.sans,
                    }}
                  >
                    {t.refLabel}
                  </div>
                  <div
                    style={{
                      fontSize: '0.9rem',
                      fontWeight: 500,
                      fontFamily: fonts.sans,
                      color: colors.onSurface,
                    }}
                  >
                    {t.refValue}
                  </div>
                </div>
              </div>
            </div>

            {/* Evidence count */}
            <p
              style={{
                fontSize: '0.88rem',
                color: colors.onSurfaceVariant,
                fontWeight: 500,
                marginTop: '24px',
                fontFamily: fonts.sans,
              }}
            >
              {t.evidence}{' '}
              <span style={{ color: colors.primary, textDecoration: 'underline' }}>
                {t.evidenceCount}
              </span>
            </p>
          </Card>
        </ScrollReveal>

        {/* Sidebar — two stacked cards */}
        <div style={{ display: 'grid', gridTemplateRows: '1fr 1fr', gap: '24px' }}>
          {/* Sanctuary card — primary gradient */}
          <ScrollReveal delay={0.15}>
            <div
              style={{
                background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryDim})`,
                color: '#ffffff',
                borderRadius: radii.card,
                padding: '32px',
                boxShadow: shadows.floating,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'center',
                height: '100%',
              }}
            >
              <h4
                style={{
                  ...typography.headline,
                  fontSize: '1.5rem',
                  color: '#ffffff',
                  margin: '0 0 8px',
                }}
              >
                {t.sidebar[0].title}
              </h4>
              <p style={{ ...typography.body, fontSize: '0.9rem', opacity: 0.9, margin: 0 }}>
                {t.sidebar[0].body}
              </p>
            </div>
          </ScrollReveal>

          {/* Protocol card — primary-container */}
          <ScrollReveal delay={0.25}>
            <div
              style={{
                background: colors.primaryContainer,
                color: colors.onSurface,
                borderRadius: radii.card,
                padding: '32px',
                boxShadow: shadows.floating,
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                height: '100%',
              }}
            >
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  background: colors.surfaceContainerLowest,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 2px 8px rgba(46, 52, 43, 0.06)',
                  marginBottom: '16px',
                }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M9 12l2 2 4-4"
                    stroke={colors.primary}
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                  />
                  <circle cx="12" cy="12" r="10" stroke={colors.primary} strokeWidth="2" />
                </svg>
              </div>
              <div>
                <h4
                  style={{
                    ...typography.headline,
                    fontSize: '1.5rem',
                    color: colors.onSurface,
                    margin: '0 0 4px',
                  }}
                >
                  {t.sidebar[1].title}
                </h4>
                <p style={{ ...typography.body, fontSize: '0.9rem', color: colors.onSurfaceVariant, margin: 0 }}>
                  {t.sidebar[1].body}
                </p>
              </div>
            </div>
          </ScrollReveal>
        </div>
      </div>
    </div>
  </section>
);
