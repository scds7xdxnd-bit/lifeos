'use client';

import { useState } from 'react';
import { translations, type Lang } from './translations';
import { colors } from './tokens';

import { NavBar } from './sections/NavBar';
import { Hero } from './sections/Hero';
import { Features } from './sections/Features';
import { InquiryDemo } from './sections/InquiryDemo';
import { SocialProof } from './sections/SocialProof';
import { Waitlist } from './sections/Waitlist';
import { Footer } from './sections/Footer';

export default function LandingPage() {
  const [lang, setLang] = useState<Lang>('en');
  const t = translations[lang];

  return (
    <div style={{ background: colors.background, overflowX: 'hidden' }}>
      <NavBar t={t.nav} lang={lang} setLang={setLang} />
      {/* key={lang} forces full remount on language switch so framer-motion
          animations (whileInView once:true) re-trigger for new content */}
      <div key={lang}>
        <Hero t={t.hero} />
        <Features t={t.domains} />
        <InquiryDemo t={t.inquiryBento} />
        <SocialProof t={t.timeline} />
        <Waitlist t={t.cta} />
      </div>
      <Footer t={t.footer} />
    </div>
  );
}
