'use client';

import type { Translations } from '../translations';
import { MicroLabel } from '../components/MicroLabel';
import { ScrollReveal, StaggerChildren, StaggerItem } from '../components/Motion';
import { colors, fonts, typography, shadows } from '../tokens';

interface TimelineProps {
  t: Translations['timeline'];
}

export const SocialProof = ({ t }: TimelineProps) => (
  <section style={{ padding: '120px 48px', background: colors.surfaceContainerLow }}>
    <div
      style={{
        maxWidth: '1200px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        gap: '80px',
      }}
    >
      {/* Left — overlapping card previews */}
      <ScrollReveal style={{ flex: 1, position: 'relative' }}>
        <div
          style={{
            width: '100%',
            aspectRatio: '4/3',
            background: colors.surfaceContainerLowest,
            borderRadius: '16px',
            boxShadow: shadows.floating,
            overflow: 'hidden',
            position: 'relative',
            padding: '32px',
          }}
        >
          {/* Faint calendar grid background */}
          <div
            style={{
              position: 'absolute',
              inset: '32px',
              display: 'grid',
              gridTemplateColumns: 'repeat(7, 1fr)',
              gap: '16px',
              opacity: 0.04,
              pointerEvents: 'none',
            }}
          >
            {Array.from({ length: 7 }).map((_, i) => (
              <div
                key={i}
                style={{
                  height: 48,
                  background: colors.onSurface,
                  borderRadius: 2,
                }}
              />
            ))}
          </div>

          {/* Card 1 — white, rotated -3deg */}
          <div
            style={{
              position: 'absolute',
              top: '25%',
              left: '25%',
              width: '75%',
              padding: '20px 24px',
              background: colors.surfaceContainerLowest,
              borderRadius: '12px',
              boxShadow: '0 12px 32px rgba(46, 52, 43, 0.1)',
              transform: 'rotate(-3deg)',
              transition: 'transform 0.5s ease',
              cursor: 'pointer',
              zIndex: 2,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'rotate(0deg)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'rotate(-3deg)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div
                style={{
                  textAlign: 'center' as const,
                  background: 'rgba(232, 115, 92, 0.08)',
                  padding: '8px 12px',
                  borderRadius: '8px',
                  flexShrink: 0,
                }}
              >
                <div
                  style={{
                    fontSize: '0.6rem',
                    fontWeight: 700,
                    color: colors.accentCoral,
                    textTransform: 'uppercase' as const,
                    fontFamily: fonts.sans,
                  }}
                >
                  {t.cards[0].month}
                </div>
                <div
                  style={{
                    fontSize: '1.3rem',
                    fontFamily: fonts.serif,
                    fontWeight: 700,
                    color: colors.onSurface,
                  }}
                >
                  {t.cards[0].day}
                </div>
              </div>
              <div>
                <h5
                  style={{
                    ...typography.headline,
                    fontSize: '1.2rem',
                    color: colors.onSurface,
                    margin: 0,
                  }}
                >
                  {t.cards[0].title}
                </h5>
                <p
                  style={{
                    fontSize: '0.78rem',
                    color: colors.onSurfaceVariant,
                    margin: '2px 0 0',
                    fontFamily: fonts.sans,
                  }}
                >
                  {t.cards[0].sub}
                </p>
              </div>
            </div>
          </div>

          {/* Card 2 — primary gradient, rotated +3deg */}
          <div
            style={{
              position: 'absolute',
              bottom: '25%',
              right: '25%',
              width: '75%',
              padding: '16px 20px',
              background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryDim})`,
              color: '#ffffff',
              borderRadius: '12px',
              boxShadow: '0 12px 32px rgba(46, 52, 43, 0.15)',
              transform: 'rotate(3deg)',
              transition: 'transform 0.5s ease',
              cursor: 'pointer',
              zIndex: 1,
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.transform = 'rotate(0deg)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'rotate(3deg)';
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <div
                style={{
                  width: 48,
                  height: 48,
                  borderRadius: '50%',
                  background: 'rgba(255, 255, 255, 0.2)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  flexShrink: 0,
                }}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path
                    d="M4 19V5a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2v14"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                  <path
                    d="M4 19a2 2 0 0 1 2-2h12a2 2 0 0 1 2 2"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                  />
                </svg>
              </div>
              <div>
                <h5
                  style={{
                    ...typography.headline,
                    fontSize: '1.2rem',
                    color: '#ffffff',
                    margin: 0,
                  }}
                >
                  {t.cards[1].title}
                </h5>
                <p
                  style={{
                    fontSize: '0.78rem',
                    opacity: 0.8,
                    margin: '2px 0 0',
                    fontFamily: fonts.sans,
                  }}
                >
                  {t.cards[1].sub}
                </p>
              </div>
            </div>
          </div>
        </div>
      </ScrollReveal>

      {/* Right — text content */}
      <div style={{ flex: 1 }}>
        <ScrollReveal>
          <MicroLabel style={{ marginBottom: '16px', display: 'block' }}>{t.eyebrow}</MicroLabel>
          <h2
            style={{
              ...typography.headline,
              fontStyle: 'italic',
              fontSize: 'clamp(2rem, 3.5vw, 3rem)',
              color: colors.onSurface,
              margin: '0 0 40px',
              lineHeight: 1.2,
            }}
          >
            {t.headline1}
            <br />
            {t.headline2}
          </h2>
        </ScrollReveal>

        <StaggerChildren
          stagger={0.15}
          style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}
        >
          {t.features.map((feature, i) => (
            <StaggerItem key={feature.title}>
              <div style={{ display: 'flex', gap: '24px' }}>
                <div
                  style={{
                    flexShrink: 0,
                    width: 48,
                    height: 48,
                    borderRadius: '50%',
                    background: i === 0 ? colors.primaryContainer : colors.secondaryContainer,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: i === 0 ? colors.primary : colors.onSecondaryContainer,
                  }}
                >
                  {i === 0 ? (
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                      <rect
                        x="3"
                        y="4"
                        width="18"
                        height="18"
                        rx="3"
                        stroke="currentColor"
                        strokeWidth="2"
                      />
                      <path d="M3 9h18" stroke="currentColor" strokeWidth="2" />
                      <path
                        d="M8 2v4M16 2v4"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </svg>
                  ) : (
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                      <path
                        d="M4 6h16M4 10h12M4 14h16M4 18h10"
                        stroke="currentColor"
                        strokeWidth="2"
                        strokeLinecap="round"
                      />
                    </svg>
                  )}
                </div>
                <div>
                  <h4
                    style={{
                      ...typography.headline,
                      fontSize: '1.5rem',
                      color: colors.onSurface,
                      margin: '0 0 8px',
                    }}
                  >
                    {feature.title}
                  </h4>
                  <p
                    style={{
                      ...typography.body,
                      color: colors.onSurfaceVariant,
                      margin: 0,
                      lineHeight: 1.65,
                    }}
                  >
                    {feature.body}
                  </p>
                </div>
              </div>
            </StaggerItem>
          ))}
        </StaggerChildren>
      </div>
    </div>
  </section>
);
