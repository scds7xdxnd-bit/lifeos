import type { CSSProperties, ReactNode } from 'react';
import { typography, colors } from '../tokens';

interface MicroLabelProps {
  children: ReactNode;
  color?: string;
  style?: CSSProperties;
}

export const MicroLabel = ({ children, color = colors.primary, style }: MicroLabelProps) => (
  <span
    style={{
      display: 'inline-block',
      fontFamily: typography.microLabel.fontFamily,
      fontWeight: typography.microLabel.fontWeight,
      letterSpacing: typography.microLabel.letterSpacing,
      textTransform: typography.microLabel.textTransform,
      fontSize: '0.82rem',
      color,
      ...style,
    }}
  >
    {children}
  </span>
);
