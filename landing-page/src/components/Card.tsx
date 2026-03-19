import type { CSSProperties, ReactNode } from 'react';
import { colors, radii, shadows } from '../tokens';

interface CardProps {
  children: ReactNode;
  style?: CSSProperties;
  className?: string;
  /** Use inverted colors for dark backgrounds */
  inverted?: boolean;
}

export const Card = ({ children, style, className, inverted }: CardProps) => (
  <div
    className={className}
    style={{
      background: inverted ? 'rgba(255, 255, 255, 0.05)' : colors.surfaceContainerLowest,
      borderRadius: radii.card,
      padding: '2rem',
      boxShadow: inverted ? 'none' : shadows.card,
      transition: 'transform 0.22s ease, box-shadow 0.22s ease',
      ...style,
    }}
    onMouseEnter={(e) => {
      const el = e.currentTarget;
      el.style.transform = 'translateY(-2px)';
      el.style.boxShadow = inverted ? 'none' : shadows.cardHover;
    }}
    onMouseLeave={(e) => {
      const el = e.currentTarget;
      el.style.transform = 'translateY(0)';
      el.style.boxShadow = inverted ? 'none' : shadows.card;
    }}
  >
    {children}
  </div>
);
