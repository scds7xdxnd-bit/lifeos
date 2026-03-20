'use client';

import {
  motion,
  useScroll,
  useTransform,
  type MotionValue,
} from 'framer-motion';
import { useRef, type CSSProperties, type ReactNode } from 'react';

/* ── ScrollReveal ─────────────────────────────────────────────
 * Fades in + slides up when the element enters the viewport.
 */
interface ScrollRevealProps {
  children: ReactNode;
  style?: CSSProperties;
  className?: string;
  /** Delay in seconds before this element animates (default 0) */
  delay?: number;
  /** Slide distance in px (default 32) */
  distance?: number;
  /** Trigger when this fraction is visible (default 0.15) */
  threshold?: number;
  /** HTML tag to render (default div) */
  as?: 'div' | 'section' | 'span' | 'p' | 'h2' | 'h3';
}

export const ScrollReveal = ({
  children,
  style,
  className,
  delay = 0,
  distance = 32,
  threshold = 0.15,
  as = 'div',
}: ScrollRevealProps) => {
  const Component = motion.create(as);
  return (
    <Component
      className={className}
      style={style}
      initial={{ opacity: 0, y: distance }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: threshold }}
      transition={{
        duration: 0.6,
        delay,
        ease: [0.25, 0.1, 0.25, 1], // cubic-bezier ease-out
      }}
    >
      {children}
    </Component>
  );
};

/* ── StaggerChildren ──────────────────────────────────────────
 * Container that staggers the entrance of its direct children.
 * Each child must be wrapped in a <StaggerItem>.
 */
interface StaggerChildrenProps {
  children: ReactNode;
  style?: CSSProperties;
  className?: string;
  /** Delay between each child in seconds (default 0.1) */
  stagger?: number;
  /** Trigger threshold (default 0.1) */
  threshold?: number;
}

const containerVariants = (stagger: number) => ({
  hidden: {},
  visible: {
    transition: {
      staggerChildren: stagger,
    },
  },
});

export const StaggerChildren = ({
  children,
  style,
  className,
  stagger = 0.1,
  threshold = 0.1,
}: StaggerChildrenProps) => (
  <motion.div
    className={className}
    style={style}
    variants={containerVariants(stagger)}
    initial="hidden"
    whileInView="visible"
    viewport={{ once: true, amount: threshold }}
  >
    {children}
  </motion.div>
);

interface StaggerItemProps {
  children: ReactNode;
  style?: CSSProperties;
  className?: string;
  /** Slide distance in px (default 28) */
  distance?: number;
}

const itemVariants = (distance: number) => ({
  hidden: { opacity: 0, y: distance },
  visible: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as const },
  },
});

export const StaggerItem = ({
  children,
  style,
  className,
  distance = 28,
}: StaggerItemProps) => (
  <motion.div
    className={className}
    style={style}
    variants={itemVariants(distance)}
  >
    {children}
  </motion.div>
);

/* ── ParallaxLayer ────────────────────────────────────────────
 * Moves an element at a different rate than normal scroll.
 * speed > 0 = moves slower (background feel)
 * speed < 0 = moves faster (foreground feel)
 */
interface ParallaxLayerProps {
  children: ReactNode;
  style?: CSSProperties;
  className?: string;
  /** Parallax intensity: px offset over the scroll range (default 40) */
  speed?: number;
}

export const ParallaxLayer = ({
  children,
  style,
  className,
  speed = 40,
}: ParallaxLayerProps) => {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });
  const y = useTransform(scrollYProgress, [0, 1], [speed, -speed]);

  return (
    <motion.div ref={ref} className={className} style={{ ...style, y }}>
      {children}
    </motion.div>
  );
};

/* ── useParallaxValue ─────────────────────────────────────────
 * Hook returning a MotionValue<number> for custom parallax use.
 */
export function useParallaxValue(
  ref: React.RefObject<HTMLElement | null>,
  speed = 40,
): MotionValue<number> {
  const { scrollYProgress } = useScroll({
    target: ref,
    offset: ['start end', 'end start'],
  });
  return useTransform(scrollYProgress, [0, 1], [speed, -speed]);
}
