'use client';

import type { Translations } from '../translations';
import { colors, fonts } from '../tokens';

interface FooterProps {
  t: Translations['footer'];
}

export const Footer = ({ t }: FooterProps) => (
  <footer
    style={{
      padding: '32px 48px',
      background: colors.dark,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      flexWrap: 'wrap',
      gap: '16px',
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

    <div style={{ display: 'flex', gap: '24px' }}>
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
