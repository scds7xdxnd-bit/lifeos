export type Lang = 'en' | 'zh';

export interface Translations {
  nav: { cta: string; login: string };
  hero: {
    badge: string; headline1: string; headline2: string; sub: string;
    primaryCta: string; secondaryCta: string; footnote: string;
    cardTag1: string; cardTag2: string; evidenceBadge: string;
    cards: {
      card1: { label: string; text: string };
      card2: { label: string; text: string };
      card3: { label: string; text: string };
    };
  };
  /* Legacy section types — kept for backward compatibility with unused files */
  features: { eyebrow: string; headline: string; items: { title: string; body: string }[] };
  howItWorks: { eyebrow: string; headline: string; steps: { step: string; title: string; body: string }[] };
  inquiry: { eyebrow: string; headline: string; sub: string; items: { q: string; a: string }[] };
  social: { headline: string; items: { quote: string; name: string; role: string }[] };
  waitlist: { eyebrow: string; headline: string; sub: string; tags: string[]; formTitle: string; footnote: string };
  /* New section types */
  domains: {
    eyebrow: string;
    headline: string;
    sub: string;
    items: { title: string; body: string; stat: string }[];
    comingSoon: string;
  };
  inquiryBento: {
    headline: string;
    sub: string;
    question: string;
    answer: string;
    sourceLabel: string;
    sourceValue: string;
    refLabel: string;
    refValue: string;
    evidence: string;
    evidenceCount: string;
    sidebar: { title: string; body: string }[];
  };
  timeline: {
    eyebrow: string;
    headline1: string;
    headline2: string;
    features: { title: string; body: string }[];
    cards: { month?: string; day?: string; title: string; sub: string }[];
  };
  cta: {
    headline: string;
    sub: string;
    formTitle: string;
    footnote: string;
  };
  footer: { rights: string; links: string[] };
}

export const translations: Record<Lang, Translations> = {
  en: {
    nav: { cta: 'Get Alpha Access', login: 'Log in' },
    hero: {
      badge: 'Private Alpha \u00b7 Limited Spots',
      headline1: 'Your life,',
      headline2: 'beautifully organized.',
      sub: 'LifeOS transforms your scattered records into evidence-based briefs. No chatbots, no guesswork \u2014 just clarity.',
      primaryCta: 'Start Your Archive',
      secondaryCta: 'The Manifesto',
      footnote: 'Free to join \u00b7 Private alpha \u00b7 Limited spots',
      cardTag1: 'Archive',
      cardTag2: 'Pattern',
      evidenceBadge: 'Evidence Synthesis',
      cards: {
        card1: { label: 'Cross-Domain Pattern', text: 'Your productivity drops on weeks when sleep averages under 6 hrs.' },
        card2: { label: 'Inquiry', text: '\u201cWhy am I always behind?\u201d \u2192 Your top 3 goals haven\u2019t moved in 3 weeks \u2014 your schedule is reactive.' },
        card3: { label: 'Habit Signal', text: 'Your habits hold on days you train. Consistency drops when exercise stops.' },
      },
    },
    features: {
      eyebrow: 'The four things LifeOS does',
      headline: 'Life is a system. LifeOS treats it like one.',
      items: [
        { title: 'Centralise your life', body: 'Goals, habits, tasks, calendar, finances, health, journaling, relationships, learning \u2014 brought into one structured environment instead of scattered across disconnected tools.' },
        { title: 'Make the invisible visible', body: 'Most people aren\u2019t lost because they\u2019re lazy. They\u2019re lost because they can\u2019t see the system clearly. LifeOS shows you what\u2019s changing, what\u2019s being neglected, and what\u2019s creating downstream problems.' },
        { title: 'Ask questions that actually matter', body: 'Ask things like \u201cWhere is my time really going?\u201d, \u201cWhat\u2019s driving my low energy?\u201d or \u201cAm I building the life I said I wanted?\u201d and get answers grounded in your actual data.' },
      ],
    },
    howItWorks: {
      eyebrow: 'How it works',
      headline: 'From scattered to structured.',
      steps: [
        { step: '01', title: 'Bring your life in', body: 'Add your goals, habits, schedule, finances, and reflections. LifeOS becomes the single environment where your life is structured \u2014 not just stored.' },
        { step: '02', title: 'See how it connects', body: 'LifeOS surfaces relationships you\u2019d never notice manually. Poor sleep affects focus. Chaotic weeks spike spending. Weak habits slow long-term goals. Now you can see it.' },
        { step: '03', title: 'Act with the full picture', body: 'Make decisions based on your whole life, not a fragment of it. Move from reactive to intentional \u2014 from overwhelmed to structured.' },
      ],
    },
    inquiry: {
      eyebrow: 'Inquiry Engine',
      headline: 'Ask questions you\u2019ve never been able to ask.',
      sub: 'Generic AI assistants know nothing about your life. LifeOS does. Every answer is grounded in your actual goals, habits, patterns, and history.',
      items: [
        { q: 'Why am I always behind on my goals?', a: 'Your top 3 goals haven\u2019t moved in 3 weeks. In that period, 80% of your logged time went to reactive tasks \u2014 not priorities. Your schedule is driving you, not the other way around.' },
        { q: 'What\u2019s actually draining my energy?', a: 'Your lowest-energy days follow nights under 6 hours of sleep, and correlate with skipped morning routines. On days you train, your focus score is 40% higher and habit completion doubles.' },
        { q: 'Am I building the life I said I wanted?', a: 'You\u2019ve stated growth, health, and deep work as priorities. In the last 30 days, 12% of your time went to deep work, 6% to health, and 67% to tasks you haven\u2019t linked to any goal.' },
      ],
    },
    social: {
      headline: 'For people who felt the problem.',
      items: [
        { quote: 'I had ambition and twelve different apps. I was busy but going nowhere. LifeOS was the first time I could actually see my life as a system \u2014 and see where it was breaking.', name: 'Maya R.', role: 'Product designer' },
        { quote: 'I realised I\u2019d been tracking tasks for years without ever moving my actual priorities. LifeOS showed me the gap between the life I said I wanted and how I was actually spending my time.', name: 'James T.', role: 'Builder' },
        { quote: 'It\u2019s not just an app. It changed how I think about my days. I stopped reacting and started running my life deliberately. That shift is hard to explain but very easy to feel.', name: 'Priya N.', role: 'Creative director' },
      ],
    },
    waitlist: {
      eyebrow: 'Private Alpha',
      headline: 'Stop living in fragments.',
      sub: 'LifeOS is opening access to a small group of people who are done with scattered tools and ready to run their life as an integrated whole.',
      tags: ['I have ambition, but not enough structure', 'My tools don\u2019t talk to each other', 'I want to understand myself better', 'I want growth, not just productivity', 'My life feels scattered'],
      formTitle: 'Join the Waitlist',
      footnote: 'We\u2019ll reach out personally when your spot is ready. No newsletters, no noise.',
    },
    domains: {
      eyebrow: 'Holistic Archiving',
      headline: 'The Domains of Human Experience',
      sub: 'Every aspect of your existence, meticulously organized yet infinitely alive.',
      items: [
        { title: 'Finance', body: 'Accounts, transactions, and forecasts \u2014 your complete financial narrative, not just numbers.', stat: 'Full Ledger' },
        { title: 'Journal', body: 'A sanctuary for thoughts, reflections, mood, and the signals between the lines.', stat: 'Mood Integrated' },
        { title: 'Health', body: 'Biometrics, workouts, and nutrition \u2014 your body\u2019s story, tracked and understood.', stat: 'HealthSync Live' },
        { title: 'Relationships', body: 'Map connections, track interactions, and nurture the bonds that matter most.', stat: 'Network Ready' },
      ],
      comingSoon: 'Calendar, Projects, Habits, Skills \u2014 and more domains coming soon.',
    },
    inquiryBento: {
      headline: 'Inquiry-First Intelligence',
      sub: 'Ask the archive. We don\u2019t guess \u2014 we synthesize from your own verified history.',
      question: 'What did I learn about focus this year?',
      answer: '12 journal entries suggest your deep work peaks between 7\u202fAM and 9\u202fAM. Interestingly, every record mentions morning exercise as a significant trigger.',
      sourceLabel: 'Primary Source',
      sourceValue: 'Journal Archive',
      refLabel: 'Reference Point',
      refValue: 'October 14, 2025',
      evidence: 'Evidence-based brief generated from',
      evidenceCount: '84 distinct data points.',
      sidebar: [
        { title: 'The Digital Sanctuary', body: 'A place where your memories are treated with the reverence of a museum archive.' },
        { title: 'Authenticity Protocol', body: 'We prioritize your actual records over AI hallucinations. Pure truth, indexed.' },
      ],
    },
    timeline: {
      eyebrow: 'Timeline Continuity',
      headline1: 'Your life isn\u2019t a list.',
      headline2: 'It\u2019s a story.',
      features: [
        { title: 'Chronological Clarity', body: 'See the thread of your ideas across days, months, and years. No more searching \u2014 just scrolling through your lived experience.' },
        { title: 'Auto-Contextualization', body: 'LifeOS understands the relationship between your calendar and your notes. It groups relevant memories so you see the full picture.' },
      ],
      cards: [
        { month: 'Oct', day: '22', title: 'The Midnight Walk', sub: '3 related files attached automatically' },
        { title: 'Archival Review', sub: 'Synthesizing 142 records from October' },
      ],
    },
    cta: {
      headline: 'Enter the Digital Sanctuary.',
      sub: 'Limited Alpha access is now opening. Secure your place in the future of evidence-based living.',
      formTitle: 'Join the Waitlist',
      footnote: 'A thoughtfully curated experience awaits.',
    },
    footer: {
      rights: '\u00a9 2026 LifeOS. All rights reserved.',
      links: ['Privacy', 'Terms'],
    },
  },

  zh: {
    nav: { cta: '\u83b7\u53d6\u62a2\u5148\u4f53\u9a8c', login: '\u767b\u5f55' },
    hero: {
      badge: '\u79c1\u5bc6 Alpha \u5185\u6d4b \u00b7 \u540d\u989d\u6709\u9650',
      headline1: '\u4f60\u7684\u751f\u6d3b\uff0c',
      headline2: '\u4f18\u96c5\u5730\u7ec4\u7ec7\u3002',
      sub: 'LifeOS \u5c06\u4f60\u6563\u843d\u7684\u8bb0\u5f55\u8f6c\u5316\u4e3a\u57fa\u4e8e\u8bc1\u636e\u7684\u7b80\u62a5\u3002\u6ca1\u6709\u804a\u5929\u673a\u5668\u4eba\uff0c\u6ca1\u6709\u731c\u6d4b\u2014\u2014\u53ea\u6709\u6e05\u6670\u3002',
      primaryCta: '\u5f00\u59cb\u4f60\u7684\u6863\u6848',
      secondaryCta: '\u5ba3\u8a00',
      footnote: '\u514d\u8d39\u52a0\u5165 \u00b7 \u79c1\u5bc6 Alpha \u5185\u6d4b \u00b7 \u540d\u989d\u6709\u9650',
      cardTag1: '\u5f52\u6863',
      cardTag2: '\u6a21\u5f0f',
      evidenceBadge: '\u8bc1\u636e\u7efc\u5408',
      cards: {
        card1: { label: '\u8de8\u9886\u57df\u6a21\u5f0f', text: '\u5f53\u4e00\u5468\u5e73\u5747\u7761\u7720\u4f4e\u4e8e 6 \u5c0f\u65f6\u65f6\uff0c\u4f60\u7684\u6548\u7387\u4f1a\u660e\u663e\u4e0b\u964d\u3002' },
        card2: { label: '\u95ee\u8be2', text: '\u201c\u4e3a\u4ec0\u4e48\u6211\u603b\u662f\u843d\u5728\u540e\u9762\uff1f\u201d\u2192 \u4f60\u6700\u91cd\u8981\u7684 3 \u4e2a\u76ee\u6807\u5df2\u7ecf 3 \u5468\u6ca1\u6709\u63a8\u8fdb\u2014\u2014\u4f60\u7684\u65e5\u7a0b\u5728\u9a71\u52a8\u4f60\uff0c\u800c\u4e0d\u662f\u4f60\u5728\u4e3b\u5bfc\u65e5\u7a0b\u3002' },
        card3: { label: '\u4e60\u60ef\u4fe1\u53f7', text: '\u4f60\u5728\u8bad\u7ec3\u7684\u65e5\u5b50\u91cc\u66f4\u80fd\u4fdd\u6301\u4e60\u60ef\uff1b\u4e00\u65e6\u505c\u6b62\u8fd0\u52a8\uff0c\u7a33\u5b9a\u6027\u5c31\u4f1a\u4e0b\u964d\u3002' },
      },
    },
    features: {
      eyebrow: 'LifeOS \u80fd\u4e3a\u4f60\u505a\u4ec0\u4e48',
      headline: '\u751f\u6d3b\u662f\u4e00\u4e2a\u7cfb\u7edf\uff0cLifeOS \u5c31\u6309\u7cfb\u7edf\u6765\u5bf9\u5f85\u5b83\u3002',
      items: [
        { title: '\u628a\u751f\u6d3b\u6574\u5408\u5230\u4e00\u8d77', body: '\u76ee\u6807\u3001\u4e60\u60ef\u3001\u4efb\u52a1\u3001\u65e5\u5386\u3001\u8d22\u52a1\u3001\u5065\u5eb7\u3001\u65e5\u8bb0\u3001\u5173\u7cfb\u3001\u5b66\u4e60\u2014\u2014\u4e0d\u518d\u6563\u843d\u5728\u5f7c\u6b64\u5272\u88c2\u7684\u5de5\u5177\u4e2d\u3002' },
        { title: '\u8ba9\u770b\u4e0d\u89c1\u7684\u95ee\u9898\u6d6e\u73b0\u51fa\u6765', body: '\u5927\u591a\u6570\u4eba\u4e0d\u662f\u56e0\u4e3a\u61d2\u800c\u8ff7\u5931\uff0c\u800c\u662f\u56e0\u4e3a\u4ed6\u4eec\u770b\u4e0d\u6e05\u6574\u4e2a\u7cfb\u7edf\u3002' },
        { title: '\u63d0\u51fa\u771f\u6b63\u91cd\u8981\u7684\u95ee\u9898', body: '\u4f60\u53ef\u4ee5\u95ee\uff1a\u201c\u6211\u7684\u65f6\u95f4\u5230\u5e95\u82b1\u5230\u54ea\u91cc\u53bb\u4e86\uff1f\u201d\u2014\u2014\u5e76\u5f97\u5230\u57fa\u4e8e\u4f60\u771f\u5b9e\u6570\u636e\u7684\u56de\u7b54\u3002' },
      ],
    },
    howItWorks: {
      eyebrow: '\u5982\u4f55\u8fd0\u4f5c',
      headline: '\u4ece\u788e\u7247\u5316\uff0c\u8d70\u5411\u7ed3\u6784\u5316\u3002',
      steps: [
        { step: '01', title: '\u628a\u4f60\u7684\u751f\u6d3b\u653e\u8fdb\u6765', body: '\u52a0\u5165\u4f60\u7684\u76ee\u6807\u3001\u4e60\u60ef\u3001\u65e5\u7a0b\u3001\u8d22\u52a1\u548c\u53cd\u601d\u3002' },
        { step: '02', title: '\u770b\u89c1\u5b83\u4eec\u5982\u4f55\u5f7c\u6b64\u5173\u8054', body: 'LifeOS \u4f1a\u5448\u73b0\u90a3\u4e9b\u4f60\u9760\u624b\u52a8\u51e0\u4e4e\u4e0d\u53ef\u80fd\u53d1\u73b0\u7684\u5173\u7cfb\u3002' },
        { step: '03', title: '\u5728\u5b8c\u6574\u89c6\u89d2\u4e0b\u884c\u52a8', body: '\u4e0d\u518d\u53ea\u6839\u636e\u751f\u6d3b\u7684\u67d0\u4e2a\u7247\u6bb5\u505a\u51b3\u5b9a\u3002' },
      ],
    },
    inquiry: {
      eyebrow: '\u95ee\u8be2\u5f15\u64ce',
      headline: '\u95ee\u51fa\u90a3\u4e9b\u4f60\u8fc7\u53bb\u6839\u672c\u65e0\u4ece\u53d1\u95ee\u7684\u95ee\u9898\u3002',
      sub: '\u901a\u7528 AI \u52a9\u624b\u5e76\u4e0d\u4e86\u89e3\u4f60\u7684\u751f\u6d3b\uff0c\u4f46 LifeOS \u4e86\u89e3\u3002',
      items: [
        { q: '\u4e3a\u4ec0\u4e48\u6211\u603b\u662f\u8d76\u4e0d\u4e0a\u81ea\u5df1\u7684\u76ee\u6807\uff1f', a: '\u4f60\u6700\u91cd\u8981\u7684 3 \u4e2a\u76ee\u6807\u5df2\u7ecf 3 \u5468\u6ca1\u6709\u63a8\u8fdb\u3002' },
        { q: '\u5230\u5e95\u662f\u4ec0\u4e48\u5728\u6d88\u8017\u6211\u7684\u7cbe\u529b\uff1f', a: '\u4f60\u7cbe\u529b\u6700\u4f4e\u7684\u65e5\u5b50\u901a\u5e38\u51fa\u73b0\u5728\u524d\u4e00\u665a\u7761\u7720\u4e0d\u8db3 6 \u5c0f\u65f6\u4e4b\u540e\u3002' },
        { q: '\u6211\u771f\u7684\u5728\u6784\u5efa\u81ea\u5df1\u60f3\u8981\u7684\u4eba\u751f\u5417\uff1f', a: '\u4f60\u66fe\u628a\u6210\u957f\u3001\u5065\u5eb7\u548c\u6df1\u5ea6\u5de5\u4f5c\u5217\u4e3a\u4f18\u5148\u4e8b\u9879\u3002' },
      ],
    },
    social: {
      headline: '\u732e\u7ed9\u90a3\u4e9b\u771f\u6b63\u611f\u53d7\u8fc7\u8fd9\u4e2a\u95ee\u9898\u7684\u4eba\u3002',
      items: [
        { quote: '\u6211\u6709\u91ce\u5fc3\uff0c\u4e5f\u88c5\u4e86\u5341\u51e0\u4e2a\u5e94\u7528\u3002LifeOS \u662f\u7b2c\u4e00\u6b21\u8ba9\u6211\u771f\u6b63\u628a\u4eba\u751f\u770b\u4f5c\u4e00\u4e2a\u7cfb\u7edf\u3002', name: 'Maya R.', role: '\u4ea7\u54c1\u8bbe\u8ba1\u5e08' },
        { quote: '\u6211\u540e\u6765\u624d\u53d1\u73b0\uff0c\u81ea\u5df1\u8fd9\u4e9b\u5e74\u4e00\u76f4\u5728\u8ffd\u8e2a\u4efb\u52a1\uff0c\u5374\u4ece\u6765\u6ca1\u6709\u771f\u6b63\u63a8\u8fdb\u8fc7\u6700\u91cd\u8981\u7684\u4f18\u5148\u4e8b\u9879\u3002', name: 'James T.', role: '\u521b\u9020\u8005' },
        { quote: '\u5b83\u4e0d\u53ea\u662f\u4e00\u4e2a\u5e94\u7528\u3002\u5b83\u6539\u53d8\u4e86\u6211\u7406\u89e3\u81ea\u5df1\u6bcf\u4e00\u5929\u7684\u65b9\u5f0f\u3002', name: 'Priya N.', role: '\u521b\u610f\u603b\u76d1' },
      ],
    },
    waitlist: {
      eyebrow: '\u79c1\u5bc6 Alpha \u5185\u6d4b',
      headline: '\u522b\u518d\u628a\u751f\u6d3b\u8fc7\u6210\u4e00\u5806\u788e\u7247\u3002',
      sub: 'LifeOS \u6b63\u5728\u5411\u4e00\u5c0f\u7fa4\u4eba\u5f00\u653e\u4f53\u9a8c\u8d44\u683c\u3002',
      tags: ['\u6211\u6709\u91ce\u5fc3\uff0c\u4f46\u8fd8\u4e0d\u591f\u6709\u7ed3\u6784', '\u6211\u7684\u5de5\u5177\u5f7c\u6b64\u4e4b\u95f4\u5b8c\u5168\u4e0d\u8fde\u901a', '\u6211\u60f3\u66f4\u6df1\u5165\u5730\u7406\u89e3\u81ea\u5df1', '\u6211\u60f3\u8981\u7684\u662f\u6210\u957f\uff0c\u800c\u4e0d\u53ea\u662f\u6548\u7387', '\u6211\u7684\u751f\u6d3b\u59cb\u7ec8\u5f88\u5206\u6563'],
      formTitle: '\u52a0\u5165\u7b49\u5019\u540d\u5355',
      footnote: '\u8f6e\u5230\u4f60\u65f6\uff0c\u6211\u4eec\u4f1a\u4eb2\u81ea\u8054\u7cfb\u4f60\u3002',
    },
    domains: {
      eyebrow: '\u5168\u65b9\u4f4d\u5f52\u6863',
      headline: '\u4eba\u7c7b\u4f53\u9a8c\u7684\u6838\u5fc3\u9886\u57df',
      sub: '\u4f60\u5b58\u5728\u7684\u6bcf\u4e00\u4e2a\u65b9\u9762\uff0c\u90fd\u88ab\u7cbe\u5fc3\u7ec4\u7ec7\uff0c\u5374\u53c8\u65e0\u9650\u9c9c\u6d3b\u3002',
      items: [
        { title: '\u8d22\u52a1', body: '\u8d26\u6237\u3001\u4ea4\u6613\u548c\u9884\u6d4b\u2014\u2014\u4f60\u5b8c\u6574\u7684\u8d22\u52a1\u53d9\u4e8b\uff0c\u4e0d\u53ea\u662f\u6570\u5b57\u3002', stat: '\u5b8c\u6574\u8d26\u672c' },
        { title: '\u65e5\u8bb0', body: '\u601d\u60f3\u3001\u53cd\u601d\u3001\u60c5\u7eea\u548c\u5b57\u91cc\u884c\u95f4\u4fe1\u53f7\u7684\u5e87\u62a4\u6240\u3002', stat: '\u60c5\u7eea\u6574\u5408' },
        { title: '\u5065\u5eb7', body: '\u751f\u7269\u6307\u6807\u3001\u8fd0\u52a8\u548c\u8425\u517b\u2014\u2014\u4f60\u8eab\u4f53\u7684\u6545\u4e8b\uff0c\u88ab\u8ffd\u8e2a\u548c\u7406\u89e3\u3002', stat: '\u5065\u5eb7\u540c\u6b65' },
        { title: '\u5173\u7cfb', body: '\u6620\u5c04\u8fde\u63a5\uff0c\u8ffd\u8e2a\u4e92\u52a8\uff0c\u5475\u62a4\u6700\u91cd\u8981\u7684\u7ebd\u5e26\u3002', stat: '\u793e\u4ea4\u56fe\u8c31' },
      ],
      comingSoon: '\u65e5\u5386\u3001\u9879\u76ee\u3001\u4e60\u60ef\u3001\u6280\u80fd\u2014\u2014\u66f4\u591a\u9886\u57df\u5373\u5c06\u63a8\u51fa\u3002',
    },
    inquiryBento: {
      headline: '\u8be2\u95ee\u4f18\u5148\u7684\u667a\u80fd',
      sub: '\u5411\u6863\u6848\u63d0\u95ee\u3002\u6211\u4eec\u4e0d\u731c\u6d4b\u2014\u2014\u6211\u4eec\u4ece\u4f60\u81ea\u5df1\u9a8c\u8bc1\u8fc7\u7684\u5386\u53f2\u4e2d\u7efc\u5408\u3002',
      question: '\u4eca\u5e74\u6211\u5bf9\u4e13\u6ce8\u529b\u6709\u4ec0\u4e48\u53d1\u73b0\uff1f',
      answer: '12\u7bc7\u65e5\u8bb0\u663e\u793a\u4f60\u7684\u6df1\u5ea6\u5de5\u4f5c\u5728\u65e9\u4e0a7\u70b9\u52309\u70b9\u4e4b\u95f4\u8fbe\u5230\u5cf0\u503c\u3002\u6709\u8da3\u7684\u662f\uff0c\u6bcf\u6761\u8bb0\u5f55\u90fd\u63d0\u5230\u6668\u95f4\u8fd0\u52a8\u662f\u4e00\u4e2a\u91cd\u8981\u89e6\u53d1\u56e0\u7d20\u3002',
      sourceLabel: '\u4e3b\u8981\u6765\u6e90',
      sourceValue: '\u65e5\u8bb0\u6863\u6848',
      refLabel: '\u53c2\u8003\u65f6\u95f4',
      refValue: '2025\u5e7410\u670814\u65e5',
      evidence: '\u57fa\u4e8e\u8bc1\u636e\u7684\u7b80\u62a5\uff0c\u6765\u81ea',
      evidenceCount: '84\u4e2a\u4e0d\u540c\u6570\u636e\u70b9\u3002',
      sidebar: [
        { title: '\u6570\u5b57\u5723\u6bbf', body: '\u4e00\u4e2a\u7528\u535a\u7269\u9986\u6863\u6848\u822c\u7684\u656c\u610f\u5bf9\u5f85\u4f60\u8bb0\u5fc6\u7684\u5730\u65b9\u3002' },
        { title: '\u771f\u5b9e\u6027\u534f\u8bae', body: '\u6211\u4eec\u4f18\u5148\u4f7f\u7528\u4f60\u7684\u771f\u5b9e\u8bb0\u5f55\uff0c\u800c\u975eAI\u5e7b\u89c9\u3002\u7eaf\u7cb9\u7684\u771f\u76f8\uff0c\u5df2\u7d22\u5f15\u3002' },
      ],
    },
    timeline: {
      eyebrow: '\u65f6\u95f4\u7ebf\u5ef6\u7eed',
      headline1: '\u4f60\u7684\u4eba\u751f\u4e0d\u662f\u4e00\u4efd\u6e05\u5355\u3002',
      headline2: '\u5b83\u662f\u4e00\u4e2a\u6545\u4e8b\u3002',
      features: [
        { title: '\u65f6\u95f4\u987a\u5e8f\u7684\u6e05\u6670', body: '\u770b\u89c1\u4f60\u7684\u60f3\u6cd5\u5728\u65e5\u3001\u6708\u3001\u5e74\u4e4b\u95f4\u7684\u8109\u7edc\u3002\u4e0d\u518d\u641c\u7d22\u2014\u2014\u53ea\u9700\u6eda\u52a8\u6d4f\u89c8\u4f60\u7684\u751f\u6d3b\u7ecf\u5386\u3002' },
        { title: '\u81ea\u52a8\u8bed\u5883\u5316', body: 'LifeOS\u7406\u89e3\u4f60\u7684\u65e5\u5386\u548c\u7b14\u8bb0\u4e4b\u95f4\u7684\u5173\u7cfb\u3002\u5b83\u5c06\u76f8\u5173\u8bb0\u5fc6\u5206\u7ec4\uff0c\u8ba9\u4f60\u770b\u5230\u5b8c\u6574\u7684\u753b\u9762\u3002' },
      ],
      cards: [
        { month: '\u5341\u6708', day: '22', title: '\u5348\u591c\u6f2b\u6b65', sub: '3\u4e2a\u76f8\u5173\u6587\u4ef6\u5df2\u81ea\u52a8\u5173\u8054' },
        { title: '\u6863\u6848\u56de\u987e', sub: '\u6b63\u5728\u7efc\u5408\u5341\u6708\u7684142\u6761\u8bb0\u5f55' },
      ],
    },
    cta: {
      headline: '\u8fdb\u5165\u6570\u5b57\u5723\u6bbf\u3002',
      sub: '\u9650\u91cfAlpha\u8bbf\u95ee\u5373\u5c06\u5f00\u653e\u3002\u5728\u8bc1\u636e\u9a71\u52a8\u751f\u6d3b\u7684\u672a\u6765\u4e2d\u9884\u5b9a\u4f60\u7684\u4f4d\u7f6e\u3002',
      formTitle: '\u52a0\u5165\u7b49\u5019\u540d\u5355',
      footnote: '\u4e00\u6bb5\u7cbe\u5fc3\u7b56\u5212\u7684\u4f53\u9a8c\u7b49\u5f85\u7740\u4f60\u3002',
    },
    footer: {
      rights: '\u00a9 2026 LifeOS. \u4fdd\u7559\u6240\u6709\u6743\u5229\u3002',
      links: ['\u9690\u79c1\u653f\u7b56', '\u670d\u52a1\u6761\u6b3e'],
    },
  },
};
