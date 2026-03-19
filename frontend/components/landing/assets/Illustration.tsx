import { colors } from '../tokens';

export const LifeIllustration = () => (
  <svg
    viewBox="0 0 520 320"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ width: '100%', maxWidth: '560px' }}
    aria-hidden="true"
  >
    <path d="M15 240 Q130 200 260 216 Q385 232 505 190" stroke={colors.darkAccent} strokeWidth="14" strokeLinecap="round" />
    <path d="M56 220 Q33 170 74 146 Q88 180 56 220Z" fill={colors.primary} />
    <path d="M75 215 Q46 162 98 138 Q106 174 75 215Z" fill={colors.darkAccent} />
    <path d="M96 210 Q78 158 124 138 Q122 176 96 210Z" fill="#6A9A60" />
    <path d="M118 206 Q114 152 156 140 Q148 178 118 206Z" fill={colors.darkAccent} />
    <path d="M140 201 Q143 148 182 140 Q168 178 140 201Z" fill={colors.primary} />
    <circle cx="146" cy="234" r="14" fill={colors.accentCoral} />
    <circle cx="120" cy="240" r="12" fill="#d4614b" />
    <circle cx="168" cy="238" r="11" fill="#c4553e" />
    <path d="M146 220 Q145 207 150 200" stroke="#7A5030" strokeWidth="2" strokeLinecap="round" />
    <path d="M120 228 Q118 215 122 208" stroke="#7A5030" strokeWidth="2" strokeLinecap="round" />
    <polygon points="262,118 295,158 262,198 229,158" fill={colors.primaryContainer} opacity="0.9" />
    <polygon points="262,118 295,158 262,198 229,158" fill="none" stroke={colors.primary} strokeWidth="2.5" />
    <polygon points="262,126 290,158 262,188 234,158" fill={colors.surfaceContainerLowest} opacity="0.4" />
    <path d="M254,130 L262,118 L270,130" fill="white" opacity="0.65" />
    <path d="M236,166 L262,198 L288,166" fill={colors.primary} opacity="0.18" />
    <path d="M213 198 Q189 148 232 126 Q244 165 213 198Z" fill={colors.primary} />
    <path d="M237 193 Q218 140 263 120 Q266 162 237 193Z" fill={colors.darkAccent} />
    <path d="M297 188 Q300 135 340 122 Q334 165 297 188Z" fill="#6A9A60" />
    <path d="M320 182 Q328 128 366 120 Q356 164 320 182Z" fill={colors.darkAccent} />
    <path d="M393 170 Q377 118 420 100 Q430 140 393 170Z" fill={colors.darkAccent} />
    <path d="M416 164 Q406 110 452 95 Q455 137 416 164Z" fill="#6A9A60" />
    <path d="M442 158 Q435 103 479 93 Q478 137 442 158Z" fill={colors.primary} />
    <circle cx="362" cy="226" r="15" fill="#D08830" />
    <circle cx="386" cy="232" r="13" fill="#C07820" />
    <circle cx="338" cy="232" r="11" fill="#E09940" />
    <path d="M362 211 Q361 198 366 191" stroke="#7A5030" strokeWidth="2" strokeLinecap="round" />
    <path d="M480 196 Q477 178 486 166" stroke={colors.primary} strokeWidth="4" strokeLinecap="round" />
    <ellipse cx="486" cy="163" rx="12" ry="7" fill={colors.darkAccent} transform="rotate(-25 486 163)" />
  </svg>
);
