'use client';

import { useState } from 'react';
import Link from 'next/link';
import type { Translations, Lang } from '../translations';
import { GlassContainer } from '../components/GlassContainer';
import { Button } from '../components/Button';
import { useBreakpoint } from '../hooks/useBreakpoint';
import { colors, fonts, spacing } from '../tokens';

interface NavBarProps {
  t: Translations['nav'];
  lang: Lang;
  setLang: (l: Lang) => void;
}

const scrollToWaitlist = () =>
  document.getElementById('waitlist')?.scrollIntoView({ behavior: 'smooth' });

export const NavBar = ({ t, lang, setLang }: NavBarProps) => {
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';
  const [menuOpen, setMenuOpen] = useState(false);

  const langToggle = (
    <div
      style={{
        display: 'flex',
        background: colors.surfaceContainerHigh,
        borderRadius: '100px',
        padding: '3px',
      }}
    >
      {(['en', 'zh', 'ko'] as Lang[]).map((l) => (
        <button
          key={l}
          onClick={() => setLang(l)}
          style={{
            padding: '5px 12px',
            border: 'none',
            borderRadius: '100px',
            fontSize: '0.82rem',
            fontFamily: fonts.sans,
            fontWeight: 700,
            cursor: 'pointer',
            background: lang === l ? colors.surfaceContainerLowest : 'transparent',
            color: lang === l ? colors.onSurface : colors.outline,
            boxShadow: lang === l ? '0 1px 4px rgba(46, 52, 43, 0.10)' : 'none',
            transition: 'all 0.18s ease',
          }}
        >
          {l === 'en' ? 'EN' : l === 'zh' ? '\u4E2D\u6587' : '\uD55C\uAD6D\uC5B4'}
        </button>
      ))}
    </div>
  );

  return (
    <>
      <GlassContainer
        style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          zIndex: 50,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: spacing.navPadding[bp],
          height: '64px',
        }}
      >
        <span
          style={{
            fontFamily: fonts.serif,
            fontStyle: 'italic',
            fontSize: '1.35rem',
            fontWeight: 400,
            color: colors.primary,
            letterSpacing: '-0.01em',
          }}
        >
          LifeOS
        </span>

        {isMobile ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            {langToggle}
            <button
              onClick={() => setMenuOpen(!menuOpen)}
              aria-label="Menu"
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '8px',
                display: 'flex',
                flexDirection: 'column',
                gap: '5px',
              }}
            >
              {[0, 1, 2].map((i) => (
                <span
                  key={i}
                  style={{
                    display: 'block',
                    width: '20px',
                    height: '2px',
                    background: colors.onSurface,
                    borderRadius: '1px',
                    transition: 'transform 0.2s ease, opacity 0.2s ease',
                    ...(menuOpen && i === 0
                      ? { transform: 'translateY(7px) rotate(45deg)' }
                      : {}),
                    ...(menuOpen && i === 1 ? { opacity: 0 } : {}),
                    ...(menuOpen && i === 2
                      ? { transform: 'translateY(-7px) rotate(-45deg)' }
                      : {}),
                  }}
                />
              ))}
            </button>
          </div>
        ) : (
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            {langToggle}
            <Button variant="secondary" onClick={scrollToWaitlist}>
              {t.cta}
            </Button>
            <Link href="/login" style={{ textDecoration: 'none' }}>
              <Button variant="primary">{t.login}</Button>
            </Link>
          </div>
        )}
      </GlassContainer>

      {/* Mobile slide-down menu */}
      {isMobile && (
        <div
          style={{
            position: 'fixed',
            top: '64px',
            left: 0,
            right: 0,
            zIndex: 49,
            background: colors.background,
            borderBottom: `1px solid ${colors.surfaceContainerHigh}`,
            padding: menuOpen ? '20px' : '0 20px',
            maxHeight: menuOpen ? '200px' : '0',
            overflow: 'hidden',
            transition: 'max-height 0.3s ease, padding 0.3s ease',
            display: 'flex',
            flexDirection: 'column',
            gap: '12px',
          }}
        >
          <Button
            variant="secondary"
            onClick={() => {
              setMenuOpen(false);
              scrollToWaitlist();
            }}
            style={{ width: '100%' }}
          >
            {t.cta}
          </Button>
          <Link href="/login" style={{ textDecoration: 'none' }}>
            <Button variant="primary" style={{ width: '100%' }}>
              {t.login}
            </Button>
          </Link>
        </div>
      )}
    </>
  );
};
