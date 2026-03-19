import type { CSSProperties, ReactNode } from 'react';
import { glass } from '../tokens';

interface GlassContainerProps {
  children: ReactNode;
  style?: CSSProperties;
}

export const GlassContainer = ({ children, style }: GlassContainerProps) => (
  <div
    style={{
      background: glass.background,
      backdropFilter: glass.blur,
      WebkitBackdropFilter: glass.blur,
      border: glass.border,
      ...style,
    }}
  >
    {children}
  </div>
);
