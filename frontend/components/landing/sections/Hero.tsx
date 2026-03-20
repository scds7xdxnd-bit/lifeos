'use client';

import type { Translations } from '../translations';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { ScrollReveal, ParallaxLayer } from '../components/Motion';
import { LifeIllustration } from '../assets/Illustration';
import { useBreakpoint } from '../hooks/useBreakpoint';
import { FernFrond } from '../assets/Botanicals';
import { colors, fonts, typography, shadows, glass } from '../tokens';

interface HeroProps {
  t: Translations['hero'];
}

const scrollTo = (id: string) =>
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });

export const Hero = ({ t }: HeroProps) => {
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';
  const isDesktop = bp === 'desktop';

  return (
    <section
      style={{
        minHeight: isMobile ? 'auto' : '100vh',
        display: 'flex',
        flexDirection: isDesktop ? 'row' : 'column',
        alignItems: isDesktop ? 'center' : 'flex-start',
        padding: isMobile
          ? '100px 20px 40px'
          : bp === 'tablet'
            ? '100px 32px 60px'
            : '80px 48px 0',
        maxWidth: '1280px',
        margin: '0 auto',
        gap: isMobile ? '32px' : '48px',
        position: 'relative',
        overflow: 'visible',
      }}
    >
      {/* Ambient gradient decoration */}
      <div
        style={{
          position: 'absolute',
          top: '-20%',
          right: '-10%',
          width: '70%',
          height: '120%',
          background: colors.primaryContainer,
          opacity: 0.15,
          borderRadius: '0 0 0 100%',
          filter: 'blur(80px)',
          pointerEvents: 'none',
          zIndex: 0,
        }}
      />

      {/* Botanical fern accent */}
      {!isMobile && (
        <div
          style={{
            position: 'absolute',
            top: '-5%',
            right: isDesktop ? '5%' : '0%',
            width: isDesktop ? '35%' : '40%',
            height: '110%',
            pointerEvents: 'none',
            zIndex: 0,
            opacity: 0.035,
          }}
        >
          <FernFrond color={colors.onSurface} />
        </div>
      )}

      {/* Left column — text content */}
      <div
        style={{
          flex: isDesktop ? '0 0 auto' : undefined,
          maxWidth: isDesktop ? '520px' : '100%',
          width: isDesktop ? undefined : '100%',
          zIndex: 1,
        }}
      >
        <ScrollReveal delay={0.1} distance={isMobile ? 12 : 20}>
          <span
            style={{
              display: 'inline-block',
              marginBottom: '20px',
              padding: '6px 16px',
              background: colors.primaryContainer,
              color: colors.primaryDim,
              borderRadius: '100px',
              ...typography.microLabel,
              fontSize: '0.8rem',
            }}
          >
            {t.badge}
          </span>
        </ScrollReveal>

        <ScrollReveal delay={0.2} distance={isMobile ? 16 : 24}>
          <h1
            style={{
              ...typography.display,
              fontStyle: 'italic',
              fontSize: isMobile
                ? 'clamp(2rem, 8vw, 3rem)'
                : 'clamp(3rem, 5vw, 4.5rem)',
              color: colors.onSurface,
              margin: '0 0 20px',
              lineHeight: 1.1,
            }}
          >
            {t.headline1}
            <br />
            <span style={{ color: colors.primary }}>{t.headline2}</span>
          </h1>
        </ScrollReveal>

        <ScrollReveal delay={0.35} distance={isMobile ? 12 : 20}>
          <p
            style={{
              ...typography.body,
              fontSize: isMobile ? '1rem' : '1.15rem',
              color: colors.onSurfaceVariant,
              margin: '0 0 36px',
              maxWidth: '460px',
            }}
          >
            {t.sub}
          </p>
        </ScrollReveal>

        <ScrollReveal delay={0.45} distance={isMobile ? 8 : 16}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap' }}>
            <Button variant="primary" onClick={() => scrollTo('waitlist')}>
              {t.primaryCta}
            </Button>
          </div>

          <p
            style={{
              marginTop: '20px',
              fontSize: '0.82rem',
              color: colors.outline,
              fontFamily: fonts.sans,
            }}
          >
            {t.footnote}
          </p>
        </ScrollReveal>
      </div>

      {/* Right column — gradient image container + floating elements */}
      <div
        style={{
          flex: isDesktop ? 1 : undefined,
          width: isDesktop ? undefined : '100%',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <ScrollReveal delay={0.3} distance={isMobile ? 20 : 40}>
          <div style={{ position: 'relative', width: '100%' }}>
            {/* Tilted background card */}
            <div
              style={{
                position: 'absolute',
                inset: 0,
                background: colors.secondaryContainer,
                opacity: 0.2,
                borderRadius: '16px',
                transform: 'rotate(3deg)',
                zIndex: -1,
              }}
            />
            {/* Main image container */}
            <div
              style={{
                width: '100%',
                aspectRatio: isMobile ? '4/3' : '1',
                maxHeight: isMobile ? '300px' : bp === 'tablet' ? '400px' : '600px',
                background: `linear-gradient(145deg, ${colors.primary} 0%, ${colors.primaryDim} 50%, #1a2d17 100%)`,
                borderRadius: '12px',
                boxShadow: '0 24px 48px rgba(46, 52, 43, 0.12)',
                overflow: 'hidden',
                position: 'relative',
              }}
            >
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  opacity: 0.15,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  padding: isMobile ? '20px' : '40px',
                }}
              >
                <LifeIllustration />
              </div>
            </div>
          </div>
        </ScrollReveal>

        {/* Floating card — static on mobile/tablet, absolute on desktop */}
        <ParallaxLayer
          speed={25}
          disabled={!isDesktop}
          style={{
            position: isDesktop ? 'absolute' : 'relative',
            top: isDesktop ? '20%' : undefined,
            left: isDesktop ? '-48px' : undefined,
            maxWidth: isMobile ? '100%' : '280px',
            zIndex: 20,
            marginTop: isDesktop ? undefined : '16px',
          }}
        >
            <Card style={{ padding: '20px 24px', boxShadow: shadows.floating }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '12px' }}>
                <div
                  style={{
                    width: 40,
                    height: 40,
                    borderRadius: '50%',
                    background: colors.secondaryContainer,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    flexShrink: 0,
                  }}
                >
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none">
                    <rect x="2" y="2" width="9" height="9" rx="2" fill={colors.onSecondaryContainer} opacity="0.7" />
                    <rect x="13" y="2" width="9" height="9" rx="2" fill={colors.onSecondaryContainer} opacity="0.4" />
                    <rect x="2" y="13" width="9" height="9" rx="2" fill={colors.onSecondaryContainer} opacity="0.4" />
                    <rect x="13" y="13" width="9" height="9" rx="2" fill={colors.onSecondaryContainer} opacity="0.7" />
                  </svg>
                </div>
                <span
                  style={{
                    fontFamily: fonts.serif,
                    fontStyle: 'italic',
                    fontSize: '1.05rem',
                    color: colors.onSurface,
                  }}
                >
                  {t.cards.card1.label}
                </span>
              </div>
              <p
                style={{
                  fontSize: '0.85rem',
                  color: colors.onSurfaceVariant,
                  lineHeight: 1.5,
                  margin: '0 0 12px',
                  fontFamily: fonts.sans,
                }}
              >
                {t.cards.card1.text}
              </p>
              <div style={{ display: 'flex', gap: '8px' }}>
                <span
                  style={{
                    padding: '4px 12px',
                    background: colors.primaryContainer,
                    color: colors.primaryDim,
                    borderRadius: '100px',
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    letterSpacing: '0.05em',
                    textTransform: 'uppercase' as const,
                  }}
                >
                  {t.cardTag1}
                </span>
                <span
                  style={{
                    padding: '4px 12px',
                    background: colors.secondaryContainer,
                    color: colors.onSecondaryContainer,
                    borderRadius: '100px',
                    fontSize: '0.68rem',
                    fontWeight: 700,
                    letterSpacing: '0.05em',
                    textTransform: 'uppercase' as const,
                  }}
                >
                  {t.cardTag2}
                </span>
              </div>
            </Card>
        </ParallaxLayer>

        {/* Floating glass badge — desktop only */}
        {isDesktop && (
          <ParallaxLayer
            speed={-15}
            style={{
              position: 'absolute',
              bottom: '15%',
              right: '-24px',
              zIndex: 20,
            }}
          >
            <div
              style={{
                padding: '12px 20px',
                background: glass.background,
                backdropFilter: glass.blur,
                WebkitBackdropFilter: glass.blur,
                borderRadius: '12px',
                boxShadow: shadows.floating,
                border: glass.border,
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                transform: 'rotate(6deg)',
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path
                  d="M12 2l2.4 7.4H22l-6.2 4.5 2.4 7.4L12 16.8l-6.2 4.5 2.4-7.4L2 9.4h7.6z"
                  fill={colors.accentCoral}
                />
              </svg>
              <span
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 700,
                  color: colors.primary,
                  letterSpacing: '0.08em',
                  textTransform: 'uppercase' as const,
                }}
              >
                {t.evidenceBadge}
              </span>
            </div>
          </ParallaxLayer>
        )}
      </div>
    </section>
  );
};
