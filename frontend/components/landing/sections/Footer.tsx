'use client';

import type { Translations } from '../translations';
import { useBreakpoint } from '../hooks/useBreakpoint';
import { colors, fonts } from '../tokens';

interface FooterProps {
  t: Translations['footer'];
}

export const Footer = ({ t }: FooterProps) => {
  const bp = useBreakpoint();
  const isMobile = bp === 'mobile';

  return (
    <footer
      style={{
        padding: isMobile ? '24px 20px' : bp === 'tablet' ? '32px 32px' : '32px 48px',
        background: colors.dark,
        display: 'flex',
        flexDirection: isMobile ? 'column' : 'row',
        alignItems: 'center',
        justifyContent: isMobile ? 'center' : 'space-between',
        flexWrap: 'wrap',
        gap: isMobile ? '12px' : '16px',
        textAlign: isMobile ? 'center' : undefined,
      }}
    >
      <span
        style={{
          fontFamily: fonts.serif,
          fontStyle: 'italic',
          fontSize: '1rem',
          fontWeight: 400,
          color: colors.darkTextActive,
          letterSpacing: '-0.01em',
        }}
      >
        LifeOS
      </span>

      <p style={{ color: colors.darkTextInactive, fontSize: '0.85rem', margin: 0, fontFamily: fonts.sans }}>
        {t.rights}
      </p>

      <div style={{ display: 'flex', gap: isMobile ? '16px' : '24px' }}>
        {t.links.map((l) => (
          <a
            key={l}
            href="#"
            style={{
              color: colors.darkTextInactive,
              fontSize: '0.85rem',
              textDecoration: 'none',
              fontFamily: fonts.sans,
              transition: 'color 0.15s ease',
            }}
            onMouseEnter={(e) => { e.currentTarget.style.color = colors.darkTextActive; }}
            onMouseLeave={(e) => { e.currentTarget.style.color = colors.darkTextInactive; }}
          >
            {l}
          </a>
        ))}
      </div>
    </footer>
  );
};
