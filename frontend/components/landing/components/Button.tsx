'use client';

import type { ButtonHTMLAttributes, CSSProperties } from 'react';
import { colors, fonts, radii, shadows } from '../tokens';

type Variant = 'primary' | 'secondary' | 'ghost';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
}

const baseStyle: CSSProperties = {
  border: 'none',
  borderRadius: radii.pill,
  cursor: 'pointer',
  fontFamily: fonts.sans,
  fontWeight: 700,
  fontSize: '0.95rem',
  letterSpacing: '0.01em',
  transition: 'transform 0.18s ease, box-shadow 0.18s ease, opacity 0.18s ease',
};

const variants: Record<Variant, CSSProperties> = {
  primary: {
    padding: '14px 30px',
    background: `linear-gradient(135deg, ${colors.primary}, ${colors.primaryDim})`,
    color: '#ffffff',
    boxShadow: shadows.button,
  },
  secondary: {
    padding: '14px 30px',
    background: colors.surfaceContainerHighest,
    color: colors.onSurface,
  },
  ghost: {
    padding: '14px 0',
    background: 'transparent',
    color: colors.onSurfaceVariant,
    textTransform: 'uppercase',
    letterSpacing: '0.05em',
    fontSize: '0.85rem',
  },
};

export const Button = ({ variant = 'primary', style, ...props }: ButtonProps) => (
  <button
    {...props}
    style={{ ...baseStyle, ...variants[variant], ...style }}
    onMouseEnter={(e) => {
      const el = e.currentTarget;
      if (variant === 'primary') {
        el.style.transform = 'translateY(-2px) scale(1.025)';
        el.style.boxShadow = shadows.buttonHover;
      } else if (variant === 'secondary') {
        el.style.transform = 'translateY(-1px)';
      } else {
        el.style.opacity = '0.7';
      }
    }}
    onMouseLeave={(e) => {
      const el = e.currentTarget;
      el.style.transform = 'translateY(0) scale(1)';
      el.style.boxShadow = variant === 'primary' ? shadows.button : 'none';
      el.style.opacity = '1';
    }}
  />
);
