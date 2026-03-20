'use client';

import { useEffect } from 'react';
import type { Translations } from '../translations';
import { ScrollReveal } from '../components/Motion';
import { colors, fonts, typography, shadows, glass } from '../tokens';

declare global {
  interface Window {
    Tally: { loadEmbeds: () => void };
  }
}

interface CallToActionProps {
  t: Translations['cta'];
}

export const Waitlist = ({ t }: CallToActionProps) => {
  useEffect(() => {
    // If Tally already loaded (e.g. remount after language switch), refresh embeds
    if (typeof window.Tally !== 'undefined') {
      window.Tally.loadEmbeds();
      return;
    }
    // Only inject script once globally
    if (document.querySelector('script[src*="tally.so"]')) return;
    const s = document.createElement('script');
    s.src = 'https://tally.so/widgets/embed.js';
    s.async = true;
    document.body.appendChild(s);
    s.onload = () => {
      if (typeof window.Tally !== 'undefined') window.Tally.loadEmbeds();
    };
  }, []);

  return (
    <section id="waitlist" style={{ padding: '120px 48px' }}>
      <div
        style={{
          maxWidth: '900px',
          margin: '0 auto',
          borderRadius: '20px',
          background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryDim})`,
          padding: '64px 48px 80px',
          textAlign: 'center',
          color: '#ffffff',
          position: 'relative',
          overflow: 'hidden',
          boxShadow: shadows.floating,
        }}
      >
        <ScrollReveal>
          {/* Decorative quote mark */}
          <span
            style={{
              fontFamily: fonts.serif,
              fontSize: '5rem',
              opacity: 0.25,
              display: 'block',
              lineHeight: 1,
              marginBottom: '16px',
            }}
          >
            &ldquo;
          </span>

          <h2
            style={{
              ...typography.headline,
              fontStyle: 'italic',
              fontSize: 'clamp(2rem, 4vw, 3.5rem)',
              color: '#ffffff',
              margin: '0 0 20px',
              lineHeight: 1.2,
            }}
          >
            {t.headline}
          </h2>

          <p
            style={{
              ...typography.body,
              fontSize: '1.15rem',
              opacity: 0.9,
              maxWidth: '560px',
              margin: '0 auto 40px',
            }}
          >
            {t.sub}
          </p>

          {/* Tally form in glassmorphic container */}
          <div
            style={{
              maxWidth: '500px',
              margin: '0 auto',
              background: 'rgba(255, 255, 255, 0.2)',
              borderRadius: '16px',
              padding: '32px',
              backdropFilter: glass.blur,
              WebkitBackdropFilter: glass.blur,
              border: '1px solid rgba(255, 255, 255, 0.25)',
            }}
          >
            <p
              style={{
                fontFamily: fonts.serif,
                fontSize: '1.1rem',
                fontWeight: 400,
                color: '#ffffff',
                margin: '0 0 16px',
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
          </div>

          <p
            style={{
              marginTop: '24px',
              fontSize: '0.88rem',
              opacity: 0.5,
              fontStyle: 'italic',
              fontFamily: fonts.serif,
              letterSpacing: '-0.02em',
            }}
          >
            {t.footnote}
          </p>
        </ScrollReveal>
      </div>
    </section>
  );
};
