'use client';

import Link from 'next/link';
import type { Translations, Lang } from '../translations';
import { GlassContainer } from '../components/GlassContainer';
import { Button } from '../components/Button';
import { colors, fonts } from '../tokens';

interface NavBarProps {
  t: Translations['nav'];
  lang: Lang;
  setLang: (l: Lang) => void;
}

export const NavBar = ({ t, lang, setLang }: NavBarProps) => (
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
      padding: '0 48px',
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

    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      {/* Language toggle */}
      <div
        style={{
          display: 'flex',
          background: colors.surfaceContainerHigh,
          borderRadius: '100px',
          padding: '3px',
        }}
      >
        {(['en', 'zh'] as Lang[]).map((l) => (
          <button
            key={l}
            onClick={() => setLang(l)}
            style={{
              padding: '5px 14px',
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
            {l === 'en' ? 'EN' : '\u4E2D\u6587'}
          </button>
        ))}
      </div>

      <Link href="/login" style={{ textDecoration: 'none' }}>
        <Button variant="primary">{t.cta}</Button>
      </Link>
    </div>
  </GlassContainer>
);
