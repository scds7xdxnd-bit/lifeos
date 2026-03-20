'use client';

import type { Translations } from '../translations';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { ScrollReveal, ParallaxLayer } from '../components/Motion';
import { LifeIllustration } from '../assets/Illustration';
import { colors, fonts, typography, shadows, glass } from '../tokens';

interface HeroProps {
  t: Translations['hero'];
}

const scrollTo = (id: string) =>
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });

export const Hero = ({ t }: HeroProps) => (
  <section
    style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      padding: '80px 48px 0',
      maxWidth: '1280px',
      margin: '0 auto',
      gap: '48px',
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

    {/* Left column — text content */}
    <div style={{ flex: '0 0 auto', maxWidth: '520px', zIndex: 1 }}>
      <ScrollReveal delay={0.1} distance={20}>
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

      <ScrollReveal delay={0.2} distance={24}>
        <h1
          style={{
            ...typography.display,
            fontStyle: 'italic',
            fontSize: 'clamp(3rem, 5vw, 4.5rem)',
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

      <ScrollReveal delay={0.35} distance={20}>
        <p
          style={{
            ...typography.body,
            fontSize: '1.15rem',
            color: colors.onSurfaceVariant,
            margin: '0 0 36px',
            maxWidth: '460px',
          }}
        >
          {t.sub}
        </p>
      </ScrollReveal>

      <ScrollReveal delay={0.45} distance={16}>
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
    <div style={{ flex: 1, position: 'relative', zIndex: 1 }}>
      <ScrollReveal delay={0.3} distance={40}>
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
              aspectRatio: '1',
              maxHeight: '600px',
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
                padding: '40px',
              }}
            >
              <LifeIllustration />
            </div>
          </div>
        </div>
      </ScrollReveal>

      {/* Floating card — overlapping from left */}
      <ParallaxLayer
        speed={25}
        style={{
          position: 'absolute',
          top: '20%',
          left: '-48px',
          maxWidth: '280px',
          zIndex: 20,
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
              Archive
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
              Pattern
            </span>
          </div>
        </Card>
      </ParallaxLayer>

      {/* Floating glass badge — bottom right */}
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
              fill={colors.primary}
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
            Evidence Synthesis
          </span>
        </div>
      </ParallaxLayer>
    </div>
  </section>
);
