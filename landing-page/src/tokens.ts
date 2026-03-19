/**
 * LifeOS Design Tokens — The Botanical Editorial
 *
 * Single source of truth for all design tokens.
 * Derived from DESIGN.md at project root.
 */

export const colors = {
  // Backgrounds & surfaces
  background: '#f8faf2',
  surface: '#f8faf2',
  surfaceContainerLow: '#f1f5eb',
  surfaceContainerLowest: '#ffffff',
  surfaceContainer: '#ebefe4',
  surfaceContainerHigh: '#e5eade',
  surfaceContainerHighest: '#dee5d7',

  // Primary
  primary: '#4b6646',
  primaryDim: '#3f5a3a',
  primaryContainer: '#ccebc2',

  // Text
  onSurface: '#2e342b',
  onSurfaceVariant: '#5a6157',
  outline: '#767d72',
  outlineVariant: '#adb4a8',

  // Accent
  accentCoral: '#e8735c',

  // Secondary
  secondaryContainer: '#d6e8ce',
  onSecondaryContainer: '#465642',

  // Dark surfaces (sidebar, footer, dark sections)
  dark: '#1a1f1a',
  darkTextActive: '#a8c4a0',
  darkTextInactive: '#5a6857',
  darkAccent: '#6b8f65',
} as const;

export const fonts = {
  serif: "'Newsreader', Georgia, 'Times New Roman', serif",
  sans: "'Manrope', system-ui, -apple-system, sans-serif",
} as const;

export const shadows = {
  card: '0 8px 24px rgba(46, 52, 43, 0.06)',
  cardHover: '0 30px 60px rgba(46, 52, 43, 0.08)',
  floating: '0 20px 40px rgba(46, 52, 43, 0.06)',
  button: '0 4px 20px rgba(46, 52, 43, 0.18)',
  buttonHover: '0 10px 34px rgba(46, 52, 43, 0.24)',
} as const;

export const radii = {
  card: '0 16px 16px 16px', // clipped specimen — sharp top-left
  pill: '100px',
} as const;

export const glass = {
  background: 'rgba(248, 250, 242, 0.75)',
  blur: 'blur(8px)',
  border: '1px solid rgba(255, 255, 255, 0.20)',
} as const;

export const typography = {
  display: {
    fontFamily: fonts.serif,
    fontWeight: 300, // Light
    letterSpacing: '-0.03em',
  },
  headline: {
    fontFamily: fonts.serif,
    fontWeight: 400,
    letterSpacing: '-0.03em',
  },
  microLabel: {
    fontFamily: fonts.sans,
    fontWeight: 700,
    letterSpacing: '0.05em',
    textTransform: 'uppercase' as const,
  },
  body: {
    fontFamily: fonts.sans,
    fontWeight: 400,
    lineHeight: 1.65,
  },
  label: {
    fontFamily: fonts.sans,
    fontWeight: 700,
  },
} as const;
