import type { Translations } from '../translations';
import { Card } from '../components/Card';
import { Button } from '../components/Button';
import { MicroLabel } from '../components/MicroLabel';
import { LifeIllustration } from '../assets/Illustration';
import { colors, fonts, typography, shadows } from '../tokens';

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
    }}
  >
    <div style={{ flex: '0 0 auto', maxWidth: '520px' }}>
      {/* Badge */}
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

      {/* Headline — Newsreader Light */}
      <h1
        style={{
          ...typography.display,
          fontSize: 'clamp(2.6rem, 4.5vw, 3.8rem)',
          color: colors.onSurface,
          margin: '0 0 20px',
          lineHeight: 1.12,
        }}
      >
        {t.headline1}
        <br />
        <span style={{ color: colors.primary }}>{t.headline2}</span>
      </h1>

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

      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '20px',
          flexWrap: 'wrap',
        }}
      >
        <Button variant="primary" onClick={() => scrollTo('waitlist')}>
          {t.primaryCta}
        </Button>
        <Button variant="ghost" onClick={() => scrollTo('features')}>
          {t.secondaryCta}
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
    </div>

    {/* Illustration + floating cards */}
    <div
      style={{
        flex: 1,
        position: 'relative',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '480px',
      }}
    >
      <LifeIllustration />

      {/* Floating cards — clipped-specimen style */}
      {[
        { cls: 'float-a', pos: { top: '14%', left: '2%' }, data: t.cards.card1, maxW: '220px' },
        { cls: 'float-b', pos: { bottom: '22%', right: '1%' }, data: t.cards.card2, maxW: '240px' },
        { cls: 'float-c', pos: { top: '52%', left: '0%' }, data: t.cards.card3, maxW: '210px' },
      ].map(({ cls, pos, data, maxW }) => (
        <Card
          key={cls}
          className={cls}
          style={{
            position: 'absolute',
            ...pos,
            maxWidth: maxW,
            padding: '14px 18px',
            boxShadow: shadows.floating,
          }}
        >
          <MicroLabel
            color={colors.outline}
            style={{ display: 'block', fontSize: '0.72rem', marginBottom: '4px' }}
          >
            {data.label}
          </MicroLabel>
          <p
            style={{
              fontSize: '0.88rem',
              color: colors.onSurface,
              margin: 0,
              lineHeight: 1.4,
              fontFamily: fonts.sans,
            }}
          >
            {data.text}
          </p>
        </Card>
      ))}
    </div>
  </section>
);
