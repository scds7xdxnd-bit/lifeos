'use client';

import { useEffect, useRef } from 'react';
import type { Translations } from '../translations';
import { Card } from '../components/Card';
import { MicroLabel } from '../components/MicroLabel';
import { colors, fonts, typography } from '../tokens';

declare global {
  interface Window {
    Tally: { loadEmbeds: () => void };
  }
}

interface WaitlistProps {
  t: Translations['waitlist'];
}

export const Waitlist = ({ t }: WaitlistProps) => {
  const scriptLoaded = useRef(false);

  useEffect(() => {
    if (scriptLoaded.current) return;
    scriptLoaded.current = true;
    const s = document.createElement('script');
    s.src = 'https://tally.so/widgets/embed.js';
    s.async = true;
    document.body.appendChild(s);
    s.onload = () => {
      if (typeof window.Tally !== 'undefined') window.Tally.loadEmbeds();
    };
  }, []);

  return (
    <section id="waitlist" style={{ padding: '120px 48px 140px', background: colors.surfaceContainerLow }}>
      <div style={{ maxWidth: '640px', margin: '0 auto', textAlign: 'center' }}>
        <MicroLabel style={{ marginBottom: '16px', display: 'block' }}>{t.eyebrow}</MicroLabel>
        <h2
          style={{
            ...typography.headline,
            fontSize: 'clamp(2rem, 3vw, 2.8rem)',
            color: colors.onSurface,
            margin: '0 0 20px',
            lineHeight: 1.2,
          }}
        >
          {t.headline}
        </h2>
        <p style={{ ...typography.body, fontSize: '1.05rem', color: colors.onSurfaceVariant, margin: '0 0 32px' }}>
          {t.sub}
        </p>

        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center', marginBottom: '48px' }}>
          {t.tags.map((tag) => (
            <span
              key={tag}
              style={{
                padding: '7px 16px',
                background: colors.secondaryContainer,
                color: colors.onSecondaryContainer,
                borderRadius: '100px',
                fontSize: '0.82rem',
                fontFamily: fonts.sans,
                fontWeight: 700,
                transition: 'transform 0.15s ease',
                cursor: 'default',
              }}
              onMouseEnter={(e) => { e.currentTarget.style.transform = 'scale(1.04)'; }}
              onMouseLeave={(e) => { e.currentTarget.style.transform = 'scale(1)'; }}
            >
              &ldquo;{tag}&rdquo;
            </span>
          ))}
        </div>

        <Card style={{ padding: '40px', textAlign: 'left' }}>
          <p
            style={{
              fontFamily: fonts.serif,
              fontSize: '1.15rem',
              fontWeight: 400,
              color: colors.onSurface,
              margin: '0 0 20px',
              textAlign: 'center',
              letterSpacing: '-0.03em',
            }}
          >
            {t.formTitle}
          </p>
          <iframe
            data-tally-src="https://tally.so/embed/kdZZW6?alignLeft=1&hideTitle=1&transparentBackground=1&dynamicHeight=1"
            loading="lazy"
            width="100%"
            height="284"
            style={{ border: 'none', display: 'block' }}
            title={t.formTitle}
          />
        </Card>

        <p style={{ marginTop: '20px', fontSize: '0.82rem', color: colors.outline, fontFamily: fonts.sans }}>
          {t.footnote}
        </p>
      </div>
    </section>
  );
};
