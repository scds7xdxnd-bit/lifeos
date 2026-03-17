import { useEffect, useRef, useState } from 'react';
import { translations, type Lang, type Translations } from './translations';

/* ─── Global styles (keyframes + hover) ─────────────────────────────────── */
const GlobalStyles = () => (
  <style>{`
    @keyframes floatA {
      0%, 100% { transform: translateY(0px); }
      50%       { transform: translateY(-9px); }
    }
    @keyframes floatB {
      0%, 100% { transform: translateY(0px); }
      50%       { transform: translateY(-6px); }
    }
    @keyframes floatC {
      0%, 100% { transform: translateY(0px); }
      50%       { transform: translateY(-11px); }
    }
    .float-a { animation: floatA 4.6s ease-in-out infinite; }
    .float-b { animation: floatB 5.4s ease-in-out infinite 1s; }
    .float-c { animation: floatC 4.0s ease-in-out infinite 1.8s; }

    .card-hover {
      transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease;
    }
    .card-hover:hover {
      transform: translateY(-5px);
      box-shadow: 0 20px 48px rgba(0,0,0,0.10) !important;
      border-color: rgba(0,0,0,0.10) !important;
    }

    .inquiry-card {
      transition: background 0.2s ease, border-color 0.2s ease;
    }
    .inquiry-card:hover {
      background: rgba(255,255,255,0.09) !important;
      border-color: rgba(255,255,255,0.20) !important;
    }

    .btn-primary {
      transition: transform 0.18s ease, box-shadow 0.18s ease;
    }
    .btn-primary:hover {
      transform: translateY(-2px) scale(1.025);
      box-shadow: 0 10px 34px rgba(0,0,0,0.32) !important;
    }

    .btn-nav {
      transition: background 0.18s ease, transform 0.18s ease;
    }
    .btn-nav:hover {
      background: #333 !important;
      transform: translateY(-1px);
    }

    .tag-pill {
      transition: background 0.15s ease, transform 0.15s ease;
      cursor: default;
    }
    .tag-pill:hover {
      background: #EDE9E3 !important;
      transform: scale(1.04);
    }

    .footer-link {
      transition: color 0.15s ease;
    }
    .footer-link:hover {
      color: #bbb !important;
    }

    .step-card {
      transition: background 0.2s ease;
    }
    .step-num {
      transition: color 0.25s ease;
    }
    .step-card:hover .step-num {
      color: #C0A878 !important;
    }
  `}</style>
);

/* ─── Types ──────────────────────────────────────────────────────────────── */
declare global {
  interface Window {
    Tally: { loadEmbeds: () => void };
  }
}

/* ─── Illustration ──────────────────────────────────────────────────────── */
const LifeIllustration = () => (
  <svg
    viewBox="0 0 520 320"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    style={{ width: '100%', maxWidth: '560px' }}
    aria-hidden="true"
  >
    <path d="M15 240 Q130 200 260 216 Q385 232 505 190" stroke="#9B7340" strokeWidth="14" strokeLinecap="round" />
    <path d="M56 220 Q33 170 74 146 Q88 180 56 220Z" fill="#4A7843" />
    <path d="M75 215 Q46 162 98 138 Q106 174 75 215Z" fill="#5C8A52" />
    <path d="M96 210 Q78 158 124 138 Q122 176 96 210Z" fill="#6A9A60" />
    <path d="M118 206 Q114 152 156 140 Q148 178 118 206Z" fill="#5C8A52" />
    <path d="M140 201 Q143 148 182 140 Q168 178 140 201Z" fill="#4A7843" />
    <circle cx="146" cy="234" r="14" fill="#C94040" />
    <circle cx="120" cy="240" r="12" fill="#D45050" />
    <circle cx="168" cy="238" r="11" fill="#B83030" />
    <path d="M146 220 Q145 207 150 200" stroke="#7A5030" strokeWidth="2" strokeLinecap="round" />
    <path d="M120 228 Q118 215 122 208" stroke="#7A5030" strokeWidth="2" strokeLinecap="round" />
    <polygon points="262,118 295,158 262,198 229,158" fill="#6BB8C0" opacity="0.9" />
    <polygon points="262,118 295,158 262,198 229,158" fill="none" stroke="#4A9EA8" strokeWidth="2.5" />
    <polygon points="262,126 290,158 262,188 234,158" fill="#A8DCDC" opacity="0.4" />
    <path d="M254,130 L262,118 L270,130" fill="white" opacity="0.65" />
    <path d="M236,166 L262,198 L288,166" fill="#4A9EA8" opacity="0.18" />
    <path d="M213 198 Q189 148 232 126 Q244 165 213 198Z" fill="#4A7843" />
    <path d="M237 193 Q218 140 263 120 Q266 162 237 193Z" fill="#5C8A52" />
    <path d="M297 188 Q300 135 340 122 Q334 165 297 188Z" fill="#6A9A60" />
    <path d="M320 182 Q328 128 366 120 Q356 164 320 182Z" fill="#5C8A52" />
    <path d="M393 170 Q377 118 420 100 Q430 140 393 170Z" fill="#5C8A52" />
    <path d="M416 164 Q406 110 452 95 Q455 137 416 164Z" fill="#6A9A60" />
    <path d="M442 158 Q435 103 479 93 Q478 137 442 158Z" fill="#4A7843" />
    <circle cx="362" cy="226" r="15" fill="#E08830" />
    <circle cx="386" cy="232" r="13" fill="#D07820" />
    <circle cx="338" cy="232" r="11" fill="#EE9940" />
    <path d="M362 211 Q361 198 366 191" stroke="#7A5030" strokeWidth="2" strokeLinecap="round" />
    <path d="M480 196 Q477 178 486 166" stroke="#4A7843" strokeWidth="4" strokeLinecap="round" />
    <ellipse cx="486" cy="163" rx="12" ry="7" fill="#5C8A52" transform="rotate(-25 486 163)" />
  </svg>
);

/* ─── Feature icons ──────────────────────────────────────────────────────── */
const InquiryIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" width="40" height="40" aria-hidden="true">
    <circle cx="20" cy="20" r="20" fill="#EAF4EA" />
    <path d="M13 20h14M20 13v14" stroke="#4A7843" strokeWidth="2.2" strokeLinecap="round" />
    <circle cx="20" cy="20" r="7" stroke="#5C8A52" strokeWidth="1.8" />
  </svg>
);
const InsightIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" width="40" height="40" aria-hidden="true">
    <circle cx="20" cy="20" r="20" fill="#EAF0F4" />
    <path d="M12 28l5-8 4 5 4-10 3 6" stroke="#4A7EA8" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);
const UnifiedIcon = () => (
  <svg viewBox="0 0 40 40" fill="none" width="40" height="40" aria-hidden="true">
    <circle cx="20" cy="20" r="20" fill="#F4EAEF" />
    <rect x="12" y="12" width="7" height="7" rx="1.5" stroke="#A84A7E" strokeWidth="1.8" />
    <rect x="21" y="12" width="7" height="7" rx="1.5" stroke="#A84A7E" strokeWidth="1.8" />
    <rect x="12" y="21" width="7" height="7" rx="1.5" stroke="#A84A7E" strokeWidth="1.8" />
    <rect x="21" y="21" width="7" height="7" rx="1.5" stroke="#A84A7E" strokeWidth="1.8" />
  </svg>
);

const FEATURE_ICONS = [UnifiedIcon, InsightIcon, InquiryIcon];

/* ─── Helpers ────────────────────────────────────────────────────────────── */
const scrollTo = (id: string) =>
  document.getElementById(id)?.scrollIntoView({ behavior: 'smooth' });

/* ─── Nav ────────────────────────────────────────────────────────────────── */
const Nav = ({ t, lang, setLang }: { t: Translations['nav']; lang: Lang; setLang: (l: Lang) => void }) => (
  <nav
    style={{
      position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
      display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      padding: '0 48px', height: '64px',
      background: 'rgba(248,247,245,0.88)',
      backdropFilter: 'blur(12px)', WebkitBackdropFilter: 'blur(12px)',
      borderBottom: '1px solid rgba(0,0,0,0.06)',
    }}
  >
    <span style={{ fontFamily: 'Georgia, "Times New Roman", serif', fontSize: '1.35rem', fontWeight: 700, color: '#1A1A1A', letterSpacing: '-0.01em' }}>
      LifeOS
    </span>

    <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
      {/* Language toggle */}
      <div style={{ display: 'flex', background: '#EFEFED', borderRadius: '100px', padding: '3px' }}>
        {(['en', 'zh'] as Lang[]).map((l) => (
          <button
            key={l}
            onClick={() => setLang(l)}
            style={{
              padding: '5px 14px', border: 'none', borderRadius: '100px',
              fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer',
              background: lang === l ? 'white' : 'transparent',
              color: lang === l ? '#1A1A1A' : '#888',
              boxShadow: lang === l ? '0 1px 4px rgba(0,0,0,0.10)' : 'none',
              transition: 'all 0.18s ease',
            }}
          >
            {l === 'en' ? 'EN' : '中文'}
          </button>
        ))}
      </div>

      <button
        className="btn-nav"
        onClick={() => scrollTo('waitlist')}
        style={{
          padding: '9px 22px', background: '#1A1A1A', color: 'white',
          border: 'none', borderRadius: '100px', fontSize: '0.9rem',
          fontWeight: 600, cursor: 'pointer', letterSpacing: '0.01em',
        }}
      >
        {t.cta}
      </button>
    </div>
  </nav>
);

/* ─── Hero ───────────────────────────────────────────────────────────────── */
const Hero = ({ t }: { t: Translations['hero'] }) => (
  <section style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', padding: '80px 48px 0', maxWidth: '1280px', margin: '0 auto', gap: '48px' }}>
    <div style={{ flex: '0 0 auto', maxWidth: '520px' }}>
      <span style={{ display: 'inline-block', marginBottom: '20px', padding: '5px 14px', background: '#EAF4EA', color: '#3A6A35', borderRadius: '100px', fontSize: '0.8rem', fontWeight: 600, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
        {t.badge}
      </span>
      <h1 style={{ fontFamily: 'Georgia, "Times New Roman", serif', fontSize: 'clamp(2.6rem, 4.5vw, 3.8rem)', fontWeight: 700, color: '#1A1A1A', margin: '0 0 20px', lineHeight: 1.12, letterSpacing: '-0.025em' }}>
        {t.headline1}
        <br />
        <span style={{ color: '#5C8A52' }}>{t.headline2}</span>
      </h1>
      <p style={{ fontSize: '1.15rem', color: '#555', lineHeight: 1.65, margin: '0 0 36px', maxWidth: '460px' }}>
        {t.sub}
      </p>
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px', flexWrap: 'wrap' }}>
        <button
          className="btn-primary"
          onClick={() => scrollTo('waitlist')}
          style={{ padding: '15px 32px', background: '#1A1A1A', color: 'white', border: 'none', borderRadius: '100px', fontSize: '1rem', fontWeight: 600, cursor: 'pointer', boxShadow: '0 4px 20px rgba(0,0,0,0.22)', letterSpacing: '0.01em' }}
        >
          {t.primaryCta}
        </button>
        <button
          onClick={() => scrollTo('features')}
          style={{ padding: '15px 0', background: 'transparent', color: '#555', border: 'none', fontSize: '1rem', cursor: 'pointer', textDecoration: 'underline', textUnderlineOffset: '3px' }}
        >
          {t.secondaryCta}
        </button>
      </div>
      <p style={{ marginTop: '20px', fontSize: '0.82rem', color: '#999' }}>{t.footnote}</p>
    </div>

    <div style={{ flex: 1, position: 'relative', display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '480px' }}>
      <LifeIllustration />
      {/* Floating cards */}
      <div className="float-a" style={{ position: 'absolute', top: '14%', left: '2%', background: 'white', borderRadius: '14px', padding: '14px 18px', boxShadow: '0 8px 28px rgba(0,0,0,0.10)', maxWidth: '220px' }}>
        <p style={{ fontSize: '0.72rem', color: '#999', margin: '0 0 4px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{t.cards.card1.label}</p>
        <p style={{ fontSize: '0.88rem', color: '#1A1A1A', margin: 0, lineHeight: 1.4 }}>{t.cards.card1.text}</p>
      </div>
      <div className="float-b" style={{ position: 'absolute', bottom: '22%', right: '1%', background: 'white', borderRadius: '14px', padding: '14px 18px', boxShadow: '0 8px 28px rgba(0,0,0,0.10)', maxWidth: '240px' }}>
        <p style={{ fontSize: '0.72rem', color: '#999', margin: '0 0 4px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{t.cards.card2.label}</p>
        <p style={{ fontSize: '0.88rem', color: '#1A1A1A', margin: 0, lineHeight: 1.4 }}>{t.cards.card2.text}</p>
      </div>
      <div className="float-c" style={{ position: 'absolute', top: '52%', left: '0%', background: 'white', borderRadius: '14px', padding: '14px 18px', boxShadow: '0 8px 28px rgba(0,0,0,0.10)', maxWidth: '210px' }}>
        <p style={{ fontSize: '0.72rem', color: '#999', margin: '0 0 4px', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>{t.cards.card3.label}</p>
        <p style={{ fontSize: '0.88rem', color: '#1A1A1A', margin: 0, lineHeight: 1.4 }}>{t.cards.card3.text}</p>
      </div>
    </div>
  </section>
);

/* ─── Features ───────────────────────────────────────────────────────────── */
const Features = ({ t }: { t: Translations['features'] }) => (
  <section id="features" style={{ padding: '120px 48px', background: 'white' }}>
    <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
      <p style={{ textAlign: 'center', fontSize: '0.82rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#5C8A52', marginBottom: '16px' }}>
        {t.eyebrow}
      </p>
      <h2 style={{ fontFamily: 'Georgia, "Times New Roman", serif', fontSize: 'clamp(2rem, 3vw, 2.8rem)', fontWeight: 700, color: '#1A1A1A', textAlign: 'center', margin: '0 0 64px', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
        {t.headline}
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '32px' }}>
        {t.items.map(({ title, body }, i) => {
          const Icon = FEATURE_ICONS[i];
          return (
            <div key={title} className="card-hover" style={{ background: '#FAFAF8', borderRadius: '20px', padding: '36px 32px', border: '1px solid rgba(0,0,0,0.05)' }}>
              <div style={{ marginBottom: '20px' }}><Icon /></div>
              <h3 style={{ fontFamily: 'Georgia, "Times New Roman", serif', fontSize: '1.2rem', fontWeight: 700, color: '#1A1A1A', margin: '0 0 12px', letterSpacing: '-0.01em' }}>{title}</h3>
              <p style={{ fontSize: '0.95rem', color: '#666', lineHeight: 1.65, margin: 0 }}>{body}</p>
            </div>
          );
        })}
      </div>
    </div>
  </section>
);

/* ─── How it works ───────────────────────────────────────────────────────── */
const HowItWorks = ({ t }: { t: Translations['howItWorks'] }) => (
  <section style={{ padding: '120px 48px', background: '#F8F7F5' }}>
    <div style={{ maxWidth: '880px', margin: '0 auto', textAlign: 'center' }}>
      <p style={{ fontSize: '0.82rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#5C8A52', marginBottom: '16px' }}>{t.eyebrow}</p>
      <h2 style={{ fontFamily: 'Georgia, "Times New Roman", serif', fontSize: 'clamp(2rem, 3vw, 2.8rem)', fontWeight: 700, color: '#1A1A1A', margin: '0 0 64px', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
        {t.headline}
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)' }}>
        {t.steps.map(({ step, title, body }, i) => (
          <div key={step} className="step-card" style={{ padding: '40px', borderLeft: i > 0 ? '1px solid rgba(0,0,0,0.08)' : 'none', textAlign: 'left' }}>
            <span className="step-num" style={{ display: 'block', fontFamily: 'Georgia, serif', fontSize: '2.5rem', fontWeight: 700, color: '#E8E6E2', marginBottom: '16px', letterSpacing: '-0.02em' }}>{step}</span>
            <h3 style={{ fontFamily: 'Georgia, "Times New Roman", serif', fontSize: '1.15rem', fontWeight: 700, color: '#1A1A1A', margin: '0 0 12px' }}>{title}</h3>
            <p style={{ fontSize: '0.95rem', color: '#666', lineHeight: 1.65, margin: 0 }}>{body}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

/* ─── Inquiry demo ───────────────────────────────────────────────────────── */
const InquiryDemo = ({ t }: { t: Translations['inquiry'] }) => (
  <section style={{ padding: '100px 48px', background: '#1A1A1A' }}>
    <div style={{ maxWidth: '860px', margin: '0 auto', textAlign: 'center' }}>
      <p style={{ fontSize: '0.82rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#7AB87A', marginBottom: '16px' }}>{t.eyebrow}</p>
      <h2 style={{ fontFamily: 'Georgia, "Times New Roman", serif', fontSize: 'clamp(1.8rem, 2.8vw, 2.6rem)', fontWeight: 700, color: 'white', margin: '0 0 16px', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
        {t.headline}
      </h2>
      <p style={{ fontSize: '1.05rem', color: '#999', margin: '0 0 56px', lineHeight: 1.65 }}>{t.sub}</p>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', textAlign: 'left' }}>
        {t.items.map(({ q, a }) => (
          <div key={q} className="inquiry-card" style={{ background: 'rgba(255,255,255,0.05)', border: '1px solid rgba(255,255,255,0.09)', borderRadius: '16px', padding: '24px 28px' }}>
            <p style={{ fontSize: '0.9rem', color: '#aaa', margin: '0 0 10px', fontStyle: 'italic' }}>"{q}"</p>
            <p style={{ fontSize: '0.97rem', color: 'white', margin: 0, lineHeight: 1.6 }}>{a}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

/* ─── Social proof ───────────────────────────────────────────────────────── */
const SocialProof = ({ t }: { t: Translations['social'] }) => (
  <section style={{ padding: '100px 48px', background: 'white' }}>
    <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
      <h2 style={{ fontFamily: 'Georgia, "Times New Roman", serif', fontSize: 'clamp(1.8rem, 2.8vw, 2.4rem)', fontWeight: 700, color: '#1A1A1A', textAlign: 'center', margin: '0 0 56px', letterSpacing: '-0.02em' }}>
        {t.headline}
      </h2>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '24px' }}>
        {t.items.map(({ quote, name, role }) => (
          <div key={name} className="card-hover" style={{ background: '#FAFAF8', borderRadius: '20px', padding: '32px', border: '1px solid rgba(0,0,0,0.05)' }}>
            <p style={{ fontSize: '0.97rem', color: '#444', lineHeight: 1.7, margin: '0 0 24px', fontStyle: 'italic' }}>"{quote}"</p>
            <p style={{ fontWeight: 700, color: '#1A1A1A', margin: 0, fontSize: '0.92rem' }}>{name}</p>
            <p style={{ color: '#999', margin: '2px 0 0', fontSize: '0.82rem' }}>{role}</p>
          </div>
        ))}
      </div>
    </div>
  </section>
);

/* ─── Waitlist ───────────────────────────────────────────────────────────── */
const Waitlist = ({ t }: { t: Translations['waitlist'] }) => {
  const scriptLoaded = useRef(false);
  useEffect(() => {
    if (scriptLoaded.current) return;
    scriptLoaded.current = true;
    const s = document.createElement('script');
    s.src = 'https://tally.so/widgets/embed.js';
    s.async = true;
    document.body.appendChild(s);
    s.onload = () => {
      if (typeof window.Tally !== 'undefined') window.Tally.loadEmbeds();
    };
  }, []);

  return (
    <section id="waitlist" style={{ padding: '120px 48px 140px', background: '#F8F7F5' }}>
      <div style={{ maxWidth: '640px', margin: '0 auto', textAlign: 'center' }}>
        <p style={{ fontSize: '0.82rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: '#5C8A52', marginBottom: '16px' }}>{t.eyebrow}</p>
        <h2 style={{ fontFamily: 'Georgia, "Times New Roman", serif', fontSize: 'clamp(2rem, 3vw, 2.8rem)', fontWeight: 700, color: '#1A1A1A', margin: '0 0 20px', letterSpacing: '-0.02em', lineHeight: 1.2 }}>
          {t.headline}
        </h2>
        <p style={{ fontSize: '1.05rem', color: '#666', lineHeight: 1.65, margin: '0 0 32px' }}>{t.sub}</p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', justifyContent: 'center', marginBottom: '48px' }}>
          {t.tags.map((tag) => (
            <span key={tag} className="tag-pill" style={{ padding: '7px 14px', background: 'white', border: '1px solid rgba(0,0,0,0.10)', borderRadius: '100px', fontSize: '0.82rem', color: '#555' }}>
              "{tag}"
            </span>
          ))}
        </div>
        <div style={{ background: 'white', borderRadius: '24px', padding: '40px', boxShadow: '0 8px 40px rgba(0,0,0,0.08)', textAlign: 'left' }}>
          <p style={{ fontFamily: 'Georgia, serif', fontSize: '1.15rem', fontWeight: 600, color: '#1A1A1A', margin: '0 0 20px', textAlign: 'center' }}>{t.formTitle}</p>
          <iframe
            data-tally-src="https://tally.so/embed/kdZZW6?alignLeft=1&hideTitle=1&transparentBackground=1&dynamicHeight=1"
            loading="lazy"
            width="100%"
            height="284"
            style={{ border: 'none', display: 'block' }}
            title={t.formTitle}
          />
        </div>
        <p style={{ marginTop: '20px', fontSize: '0.82rem', color: '#aaa' }}>{t.footnote}</p>
      </div>
    </section>
  );
};

/* ─── Footer ─────────────────────────────────────────────────────────────── */
const Footer = ({ t }: { t: Translations['footer'] }) => (
  <footer style={{ padding: '32px 48px', background: '#1A1A1A', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px' }}>
    <span style={{ fontFamily: 'Georgia, serif', fontSize: '1rem', fontWeight: 700, color: 'white', letterSpacing: '-0.01em' }}>LifeOS</span>
    <p style={{ color: '#555', fontSize: '0.85rem', margin: 0 }}>{t.rights}</p>
    <div style={{ display: 'flex', gap: '24px' }}>
      {t.links.map((l) => (
        <a key={l} href="#" className="footer-link" style={{ color: '#666', fontSize: '0.85rem', textDecoration: 'none' }}>{l}</a>
      ))}
    </div>
  </footer>
);

/* ─── App ────────────────────────────────────────────────────────────────── */
export default function App() {
  const [lang, setLang] = useState<Lang>('en');
  const t = translations[lang];

  return (
    <div style={{ background: '#F8F7F5', overflowX: 'hidden' }}>
      <GlobalStyles />
      <Nav t={t.nav} lang={lang} setLang={setLang} />
      <Hero t={t.hero} />
      <Features t={t.features} />
      <HowItWorks t={t.howItWorks} />
      <InquiryDemo t={t.inquiry} />
      <SocialProof t={t.social} />
      <Waitlist t={t.waitlist} />
      <Footer t={t.footer} />
    </div>
  );
}
