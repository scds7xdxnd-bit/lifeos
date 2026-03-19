'use client';

import { useState } from 'react';
import { translations, type Lang } from './translations';
import { colors } from './tokens';

import { NavBar } from './sections/NavBar';
import { Hero } from './sections/Hero';
import { Features } from './sections/Features';
import { HowItWorks } from './sections/HowItWorks';
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
