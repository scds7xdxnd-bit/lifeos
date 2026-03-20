'use client';

import type { CSSProperties } from 'react';

interface BotanicalProps {
  style?: CSSProperties;
  color?: string;
  className?: string;
}

/**
 * Large fern frond silhouette — Hero background accent.
 * Designed to sit at very low opacity behind content.
 */
export const FernFrond = ({ style, color = 'currentColor' }: BotanicalProps) => (
  <svg
    viewBox="0 0 400 600"
    fill="none"
    style={{ width: '100%', height: '100%', ...style }}
  >
    {/* Main stem */}
    <path
      d="M200 580 C200 580, 195 400, 200 200 C205 100, 200 40, 198 20"
      stroke={color}
      strokeWidth="2.5"
      strokeLinecap="round"
      fill="none"
    />
    {/* Left leaflets */}
    <path d="M200 500 C180 490, 120 470, 80 440 C120 460, 170 480, 200 490" fill={color} opacity="0.5" />
    <path d="M200 450 C175 435, 110 405, 60 370 C110 395, 165 425, 200 440" fill={color} opacity="0.55" />
    <path d="M200 400 C170 380, 100 340, 50 300 C100 330, 160 370, 200 390" fill={color} opacity="0.6" />
    <path d="M200 350 C168 325, 95 280, 45 235 C95 270, 158 315, 200 340" fill={color} opacity="0.6" />
    <path d="M200 300 C170 275, 105 225, 55 175 C105 215, 160 265, 200 290" fill={color} opacity="0.55" />
    <path d="M200 250 C175 228, 120 180, 75 130 C120 170, 165 218, 200 240" fill={color} opacity="0.5" />
    <path d="M200 200 C180 182, 140 145, 105 100 C140 135, 175 172, 200 190" fill={color} opacity="0.4" />
    <path d="M200 155 C188 140, 160 110, 135 75 C160 105, 185 135, 200 148" fill={color} opacity="0.3" />
    {/* Right leaflets */}
    <path d="M200 480 C220 468, 280 445, 320 415 C280 435, 230 458, 200 470" fill={color} opacity="0.5" />
    <path d="M200 430 C225 413, 290 380, 340 345 C290 370, 235 403, 200 420" fill={color} opacity="0.55" />
    <path d="M200 380 C230 358, 300 315, 350 275 C300 305, 240 348, 200 370" fill={color} opacity="0.6" />
    <path d="M200 330 C232 305, 305 258, 355 210 C305 248, 242 295, 200 320" fill={color} opacity="0.6" />
    <path d="M200 280 C228 255, 295 205, 345 155 C295 195, 238 245, 200 270" fill={color} opacity="0.55" />
    <path d="M200 235 C222 215, 275 170, 320 125 C275 160, 228 205, 200 225" fill={color} opacity="0.5" />
    <path d="M200 190 C215 175, 255 140, 290 100 C255 130, 220 165, 200 182" fill={color} opacity="0.4" />
    <path d="M200 148 C210 135, 238 108, 262 78 C238 100, 215 128, 200 142" fill={color} opacity="0.3" />
  </svg>
);

/**
 * Horizontal vine with small leaves — section divider.
 * Renders as a wide, thin decorative element.
 */
export const VineDivider = ({ style, color = 'currentColor' }: BotanicalProps) => (
  <svg
    viewBox="0 0 800 60"
    fill="none"
    style={{ width: '100%', height: 'auto', ...style }}
  >
    {/* Main vine stem — organic curve */}
    <path
      d="M0 35 C80 30, 160 40, 240 32 C320 24, 400 38, 480 30 C560 22, 640 36, 720 28 C760 24, 790 30, 800 32"
      stroke={color}
      strokeWidth="1.5"
      strokeLinecap="round"
      fill="none"
    />
    {/* Small leaves along the vine */}
    <path d="M120 33 C115 22, 130 18, 135 28" fill={color} opacity="0.5" />
    <path d="M125 33 C130 22, 115 18, 110 28" fill={color} opacity="0.35" />
    <path d="M300 30 C295 19, 310 15, 315 25" fill={color} opacity="0.5" />
    <path d="M305 30 C310 19, 295 15, 290 25" fill={color} opacity="0.35" />
    <path d="M500 31 C495 20, 510 16, 515 26" fill={color} opacity="0.5" />
    <path d="M505 31 C510 20, 495 16, 490 26" fill={color} opacity="0.35" />
    <path d="M680 29 C675 18, 690 14, 695 24" fill={color} opacity="0.5" />
    <path d="M685 29 C690 18, 675 14, 670 24" fill={color} opacity="0.35" />
    {/* Tiny dots / buds */}
    <circle cx="200" cy="36" r="2" fill={color} opacity="0.3" />
    <circle cx="410" cy="33" r="2" fill={color} opacity="0.3" />
    <circle cx="600" cy="27" r="2" fill={color} opacity="0.3" />
  </svg>
);

/**
 * Corner leaf cluster — Waitlist CTA accent.
 * Designed to anchor to bottom-right of a container.
 */
export const LeafCluster = ({ style, color = 'currentColor' }: BotanicalProps) => (
  <svg
    viewBox="0 0 300 300"
    fill="none"
    style={{ width: '100%', height: '100%', ...style }}
  >
    {/* Branch */}
    <path
      d="M300 300 C280 270, 240 220, 200 180 C170 150, 130 120, 100 100"
      stroke={color}
      strokeWidth="1.5"
      strokeLinecap="round"
      fill="none"
    />
    {/* Secondary branch */}
    <path
      d="M240 240 C225 225, 200 210, 170 200 C150 194, 120 190, 100 192"
      stroke={color}
      strokeWidth="1"
      strokeLinecap="round"
      fill="none"
    />
    {/* Leaves — varying sizes and opacities */}
    <path d="M200 180 C185 160, 175 145, 190 140 C205 135, 210 155, 200 175" fill={color} opacity="0.5" />
    <path d="M200 180 C215 160, 225 145, 210 140 C195 135, 190 155, 200 175" fill={color} opacity="0.35" />
    <path d="M160 155 C148 138, 140 125, 152 120 C164 115, 168 132, 160 150" fill={color} opacity="0.45" />
    <path d="M160 155 C172 138, 180 125, 168 120 C156 115, 152 132, 160 150" fill={color} opacity="0.3" />
    <path d="M130 130 C122 118, 117 108, 126 105 C135 102, 137 114, 130 127" fill={color} opacity="0.4" />
    <path d="M170 200 C158 186, 150 175, 160 170 C170 165, 174 180, 170 195" fill={color} opacity="0.45" />
    <path d="M170 200 C182 186, 190 175, 180 170 C170 165, 166 180, 170 195" fill={color} opacity="0.3" />
    <path d="M130 195 C120 184, 114 175, 123 172 C132 169, 134 180, 130 192" fill={color} opacity="0.35" />
    {/* Small buds */}
    <circle cx="110" cy="105" r="3" fill={color} opacity="0.25" />
    <circle cx="105" cy="195" r="2.5" fill={color} opacity="0.25" />
    <circle cx="240" cy="235" r="2" fill={color} opacity="0.2" />
  </svg>
);
