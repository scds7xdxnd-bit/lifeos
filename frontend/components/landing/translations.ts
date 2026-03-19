export type Lang = 'en' | 'zh';

export interface Translations {
  nav: { cta: string };
  hero: {
    badge: string; headline1: string; headline2: string; sub: string;
    primaryCta: string; secondaryCta: string; footnote: string;
    cards: {
      card1: { label: string; text: string };
      card2: { label: string; text: string };
      card3: { label: string; text: string };
    };
  };
  features: { eyebrow: string; headline: string; items: { title: string; body: string }[] };
  howItWorks: { eyebrow: string; headline: string; steps: { step: string; title: string; body: string }[] };
  inquiry: { eyebrow: string; headline: string; sub: string; items: { q: string; a: string }[] };
  social: { headline: string; items: { quote: string; name: string; role: string }[] };
  waitlist: { eyebrow: string; headline: string; sub: string; tags: string[]; formTitle: string; footnote: string };
  footer: { rights: string; links: string[] };
}

export const translations: Record<Lang, Translations> = {
  en: {
    nav: {
      cta: 'Get Alpha Access',
    },
    hero: {
      badge: 'Private Alpha \u00b7 Limited Spots',
      headline1: 'Your life is a system.',
      headline2: 'Start running it like one.',
      sub: 'Most people manage life in fragments \u2014 tasks in one app, money in another, goals only in their head. LifeOS integrates your goals, habits, time, health, finances, and reflection into one coherent system, so you can finally see what\u2019s actually happening and act on it.',
      primaryCta: 'Join the Private Alpha',
      secondaryCta: 'See how it works \u2193',
      footnote: 'Free to join \u00b7 Private alpha \u00b7 Limited spots',
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
        {
          title: 'Centralise your life',
          body: 'Goals, habits, tasks, calendar, finances, health, journaling, relationships, learning \u2014 brought into one structured environment instead of scattered across disconnected tools.',
        },
        {
          title: 'Make the invisible visible',
          body: 'Most people aren\u2019t lost because they\u2019re lazy. They\u2019re lost because they can\u2019t see the system clearly. LifeOS shows you what\u2019s changing, what\u2019s being neglected, and what\u2019s creating downstream problems.',
        },
        {
          title: 'Ask questions that actually matter',
          body: 'Ask things like \u201cWhere is my time really going?\u201d, \u201cWhat\u2019s driving my low energy?\u201d or \u201cAm I building the life I said I wanted?\u201d and get answers grounded in your actual data.',
        },
      ],
    },
    howItWorks: {
      eyebrow: 'How it works',
      headline: 'From scattered to structured.',
      steps: [
        {
          step: '01',
          title: 'Bring your life in',
          body: 'Add your goals, habits, schedule, finances, and reflections. LifeOS becomes the single environment where your life is structured \u2014 not just stored.',
        },
        {
          step: '02',
          title: 'See how it connects',
          body: 'LifeOS surfaces relationships you\u2019d never notice manually. Poor sleep affects focus. Chaotic weeks spike spending. Weak habits slow long-term goals. Now you can see it.',
        },
        {
          step: '03',
          title: 'Act with the full picture',
          body: 'Make decisions based on your whole life, not a fragment of it. Move from reactive to intentional \u2014 from overwhelmed to structured.',
        },
      ],
    },
    inquiry: {
      eyebrow: 'Inquiry Engine',
      headline: 'Ask questions you\u2019ve never been able to ask.',
      sub: 'Generic AI assistants know nothing about your life. LifeOS does. Every answer is grounded in your actual goals, habits, patterns, and history.',
      items: [
        {
          q: 'Why am I always behind on my goals?',
          a: 'Your top 3 goals haven\u2019t moved in 3 weeks. In that period, 80% of your logged time went to reactive tasks \u2014 not priorities. Your schedule is driving you, not the other way around.',
        },
        {
          q: 'What\u2019s actually draining my energy?',
          a: 'Your lowest-energy days follow nights under 6 hours of sleep, and correlate with skipped morning routines. On days you train, your focus score is 40% higher and habit completion doubles.',
        },
        {
          q: 'Am I building the life I said I wanted?',
          a: 'You\u2019ve stated growth, health, and deep work as priorities. In the last 30 days, 12% of your time went to deep work, 6% to health, and 67% to tasks you haven\u2019t linked to any goal.',
        },
      ],
    },
    social: {
      headline: 'For people who felt the problem.',
      items: [
        {
          quote: 'I had ambition and twelve different apps. I was busy but going nowhere. LifeOS was the first time I could actually see my life as a system \u2014 and see where it was breaking.',
          name: 'Maya R.',
          role: 'Product designer',
        },
        {
          quote: 'I realised I\u2019d been tracking tasks for years without ever moving my actual priorities. LifeOS showed me the gap between the life I said I wanted and how I was actually spending my time.',
          name: 'James T.',
          role: 'Builder',
        },
        {
          quote: 'It\u2019s not just an app. It changed how I think about my days. I stopped reacting and started running my life deliberately. That shift is hard to explain but very easy to feel.',
          name: 'Priya N.',
          role: 'Creative director',
        },
      ],
    },
    waitlist: {
      eyebrow: 'Private Alpha',
      headline: 'Stop living in fragments.',
      sub: 'LifeOS is opening access to a small group of people who are done with scattered tools and ready to run their life as an integrated whole. Ambitious, reflective people who want structure without feeling robotic.',
      tags: [
        'I have ambition, but not enough structure',
        'My tools don\u2019t talk to each other',
        'I want to understand myself better',
        'I want growth, not just productivity',
        'My life feels scattered',
      ],
      formTitle: 'Join the Waitlist',
      footnote: 'We\u2019ll reach out personally when your spot is ready. No newsletters, no noise.',
    },
    footer: {
      rights: '\u00a9 2026 LifeOS. All rights reserved.',
      links: ['Privacy', 'Terms'],
    },
  },

  zh: {
    nav: {
      cta: '\u83b7\u53d6\u62a2\u5148\u4f53\u9a8c\u8d44\u683c',
    },
    hero: {
      badge: '\u79c1\u5bc6 Alpha \u5185\u6d4b \u00b7 \u540d\u989d\u6709\u9650',
      headline1: '\u4f60\u7684\u751f\u6d3b\uff0c\u672c\u5c31\u662f\u4e00\u4e2a\u7cfb\u7edf\u3002',
      headline2: '\u73b0\u5728\u5f00\u59cb\uff0c\u50cf\u5bf9\u5f85\u7cfb\u7edf\u4e00\u6837\u7ba1\u7406\u5b83\u3002',
      sub: '\u5927\u591a\u6570\u4eba\u90fd\u5728\u788e\u7247\u5316\u5730\u7ba1\u7406\u751f\u6d3b\u2014\u2014\u4efb\u52a1\u653e\u5728\u4e00\u4e2a\u5e94\u7528\u91cc\uff0c\u91d1\u94b1\u653e\u5728\u53e6\u4e00\u4e2a\uff0c\u76ee\u6807\u53ea\u5b58\u5728\u8111\u6d77\u4e2d\u3002LifeOS \u5c06\u4f60\u7684\u76ee\u6807\u3001\u4e60\u60ef\u3001\u65f6\u95f4\u3001\u5065\u5eb7\u3001\u8d22\u52a1\u4e0e\u53cd\u601d\u6574\u5408\u8fdb\u4e00\u4e2a\u8fde\u8d2f\u7684\u7cfb\u7edf\uff0c\u8ba9\u4f60\u7ec8\u4e8e\u770b\u6e05\u751f\u6d3b\u91cc\u7a76\u7adf\u53d1\u751f\u4e86\u4ec0\u4e48\uff0c\u5e76\u636e\u6b64\u884c\u52a8\u3002',
      primaryCta: '\u52a0\u5165\u79c1\u5bc6 Alpha \u5185\u6d4b',
      secondaryCta: '\u770b\u770b\u5b83\u5982\u4f55\u8fd0\u4f5c \u2193',
      footnote: '\u514d\u8d39\u52a0\u5165 \u00b7 \u79c1\u5bc6 Alpha \u5185\u6d4b \u00b7 \u540d\u989d\u6709\u9650',
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
        {
          title: '\u628a\u751f\u6d3b\u6574\u5408\u5230\u4e00\u8d77',
          body: '\u76ee\u6807\u3001\u4e60\u60ef\u3001\u4efb\u52a1\u3001\u65e5\u5386\u3001\u8d22\u52a1\u3001\u5065\u5eb7\u3001\u65e5\u8bb0\u3001\u5173\u7cfb\u3001\u5b66\u4e60\u2014\u2014\u4e0d\u518d\u6563\u843d\u5728\u5f7c\u6b64\u5272\u88c2\u7684\u5de5\u5177\u4e2d\uff0c\u800c\u662f\u8fdb\u5165\u4e00\u4e2a\u7edf\u4e00\u4e14\u7ed3\u6784\u5316\u7684\u73af\u5883\u3002',
        },
        {
          title: '\u8ba9\u770b\u4e0d\u89c1\u7684\u95ee\u9898\u6d6e\u73b0\u51fa\u6765',
          body: '\u5927\u591a\u6570\u4eba\u4e0d\u662f\u56e0\u4e3a\u61d2\u800c\u8ff7\u5931\uff0c\u800c\u662f\u56e0\u4e3a\u4ed6\u4eec\u770b\u4e0d\u6e05\u6574\u4e2a\u7cfb\u7edf\u3002LifeOS \u5e2e\u4f60\u770b\u89c1\u4ec0\u4e48\u6b63\u5728\u53d8\u5316\u3001\u4ec0\u4e48\u88ab\u5ffd\u7565\u4e86\u3001\u4ee5\u53ca\u4ec0\u4e48\u6b63\u5728\u5f15\u53d1\u540e\u7eed\u95ee\u9898\u3002',
        },
        {
          title: '\u63d0\u51fa\u771f\u6b63\u91cd\u8981\u7684\u95ee\u9898',
          body: '\u4f60\u53ef\u4ee5\u95ee\uff1a\u201c\u6211\u7684\u65f6\u95f4\u5230\u5e95\u82b1\u5230\u54ea\u91cc\u53bb\u4e86\uff1f\u201d\u201c\u662f\u4ec0\u4e48\u5728\u62d6\u57ae\u6211\u7684\u7cbe\u529b\uff1f\u201d\u201c\u6211\u771f\u7684\u5728\u6784\u5efa\u81ea\u5df1\u60f3\u8981\u7684\u4eba\u751f\u5417\uff1f\u201d\u2014\u2014\u5e76\u5f97\u5230\u57fa\u4e8e\u4f60\u771f\u5b9e\u6570\u636e\u7684\u56de\u7b54\u3002',
        },
      ],
    },
    howItWorks: {
      eyebrow: '\u5982\u4f55\u8fd0\u4f5c',
      headline: '\u4ece\u788e\u7247\u5316\uff0c\u8d70\u5411\u7ed3\u6784\u5316\u3002',
      steps: [
        {
          step: '01',
          title: '\u628a\u4f60\u7684\u751f\u6d3b\u653e\u8fdb\u6765',
          body: '\u52a0\u5165\u4f60\u7684\u76ee\u6807\u3001\u4e60\u60ef\u3001\u65e5\u7a0b\u3001\u8d22\u52a1\u548c\u53cd\u601d\u3002LifeOS \u4f1a\u6210\u4e3a\u4f60\u6574\u7406\u751f\u6d3b\u7684\u7edf\u4e00\u73af\u5883\u2014\u2014\u4e0d\u53ea\u662f\u5b58\u653e\u4fe1\u606f\u7684\u5730\u65b9\u3002',
        },
        {
          step: '02',
          title: '\u770b\u89c1\u5b83\u4eec\u5982\u4f55\u5f7c\u6b64\u5173\u8054',
          body: 'LifeOS \u4f1a\u5448\u73b0\u90a3\u4e9b\u4f60\u9760\u624b\u52a8\u51e0\u4e4e\u4e0d\u53ef\u80fd\u53d1\u73b0\u7684\u5173\u7cfb\uff1a\u7761\u4e0d\u597d\u4f1a\u524a\u5f31\u4e13\u6ce8\uff0c\u6df7\u4e71\u7684\u4e00\u5468\u4f1a\u63a8\u9ad8\u652f\u51fa\uff0c\u8584\u5f31\u7684\u4e60\u60ef\u4f1a\u62d6\u6162\u957f\u671f\u76ee\u6807\u3002\u73b0\u5728\uff0c\u8fd9\u4e9b\u90fd\u80fd\u88ab\u770b\u89c1\u3002',
        },
        {
          step: '03',
          title: '\u5728\u5b8c\u6574\u89c6\u89d2\u4e0b\u884c\u52a8',
          body: '\u4e0d\u518d\u53ea\u6839\u636e\u751f\u6d3b\u7684\u67d0\u4e2a\u7247\u6bb5\u505a\u51b3\u5b9a\uff0c\u800c\u662f\u57fa\u4e8e\u6574\u4f53\u6765\u5224\u65ad\u3002\u4f60\u4f1a\u4ece\u88ab\u52a8\u5e94\u4ed8\uff0c\u8f6c\u5411\u6709\u610f\u8bc6\u5730\u4e3b\u5bfc\u2014\u2014\u4ece\u6df7\u4e71\u5931\u63a7\uff0c\u8f6c\u5411\u6e05\u6670\u6709\u5e8f\u3002',
        },
      ],
    },
    inquiry: {
      eyebrow: '\u95ee\u8be2\u5f15\u64ce',
      headline: '\u95ee\u51fa\u90a3\u4e9b\u4f60\u8fc7\u53bb\u6839\u672c\u65e0\u4ece\u53d1\u95ee\u7684\u95ee\u9898\u3002',
      sub: '\u901a\u7528 AI \u52a9\u624b\u5e76\u4e0d\u4e86\u89e3\u4f60\u7684\u751f\u6d3b\uff0c\u4f46 LifeOS \u4e86\u89e3\u3002\u6bcf\u4e00\u4e2a\u56de\u7b54\u90fd\u5efa\u7acb\u5728\u4f60\u771f\u5b9e\u7684\u76ee\u6807\u3001\u4e60\u60ef\u3001\u6a21\u5f0f\u4e0e\u5386\u53f2\u4e4b\u4e0a\u3002',
      items: [
        {
          q: '\u4e3a\u4ec0\u4e48\u6211\u603b\u662f\u8d76\u4e0d\u4e0a\u81ea\u5df1\u7684\u76ee\u6807\uff1f',
          a: '\u4f60\u6700\u91cd\u8981\u7684 3 \u4e2a\u76ee\u6807\u5df2\u7ecf 3 \u5468\u6ca1\u6709\u63a8\u8fdb\u3002\u5728\u8fd9\u6bb5\u65f6\u95f4\u91cc\uff0c\u4f60\u8bb0\u5f55\u7684\u65f6\u95f4\u6709 80% \u90fd\u82b1\u5728\u4e86\u88ab\u52a8\u5e94\u5bf9\u578b\u4efb\u52a1\u4e0a\uff0c\u800c\u4e0d\u662f\u4f18\u5148\u4e8b\u9879\u3002\u662f\u65e5\u7a0b\u5728\u63a8\u7740\u4f60\u8d70\uff0c\u800c\u4e0d\u662f\u4f60\u5728\u638c\u63a7\u65e5\u7a0b\u3002',
        },
        {
          q: '\u5230\u5e95\u662f\u4ec0\u4e48\u5728\u6d88\u8017\u6211\u7684\u7cbe\u529b\uff1f',
          a: '\u4f60\u7cbe\u529b\u6700\u4f4e\u7684\u65e5\u5b50\uff0c\u901a\u5e38\u90fd\u51fa\u73b0\u5728\u524d\u4e00\u665a\u7761\u7720\u4e0d\u8db3 6 \u5c0f\u65f6\u4e4b\u540e\uff0c\u5e76\u4e14\u5e38\u5e38\u4f34\u968f\u7740\u6668\u95f4\u4f8b\u7a0b\u88ab\u8df3\u8fc7\u3002\u800c\u5728\u4f60\u8bad\u7ec3\u7684\u65e5\u5b50\u91cc\uff0c\u4e13\u6ce8\u5f97\u5206\u4f1a\u9ad8\u51fa 40%\uff0c\u4e60\u60ef\u5b8c\u6210\u7387\u4e5f\u4f1a\u7ffb\u500d\u3002',
        },
        {
          q: '\u6211\u771f\u7684\u5728\u6784\u5efa\u81ea\u5df1\u60f3\u8981\u7684\u4eba\u751f\u5417\uff1f',
          a: '\u4f60\u66fe\u628a\u6210\u957f\u3001\u5065\u5eb7\u548c\u6df1\u5ea6\u5de5\u4f5c\u5217\u4e3a\u4f18\u5148\u4e8b\u9879\u3002\u4f46\u5728\u8fc7\u53bb 30 \u5929\u91cc\uff0c\u4f60\u53ea\u6709 12% \u7684\u65f6\u95f4\u6295\u5165\u6df1\u5ea6\u5de5\u4f5c\uff0c6% \u6295\u5165\u5065\u5eb7\uff0c\u800c 67% \u7684\u65f6\u95f4\u5219\u82b1\u5728\u4e86\u90a3\u4e9b\u6ca1\u6709\u5173\u8054\u5230\u4efb\u4f55\u76ee\u6807\u7684\u4efb\u52a1\u4e0a\u3002',
        },
      ],
    },
    social: {
      headline: '\u732e\u7ed9\u90a3\u4e9b\u771f\u6b63\u611f\u53d7\u8fc7\u8fd9\u4e2a\u95ee\u9898\u7684\u4eba\u3002',
      items: [
        {
          quote: '\u6211\u6709\u91ce\u5fc3\uff0c\u4e5f\u88c5\u4e86\u5341\u51e0\u4e2a\u5e94\u7528\u3002\u6211\u4e00\u76f4\u5f88\u5fd9\uff0c\u5374\u59cb\u7ec8\u6ca1\u6709\u771f\u6b63\u524d\u8fdb\u3002LifeOS \u662f\u7b2c\u4e00\u6b21\u8ba9\u6211\u771f\u6b63\u628a\u4eba\u751f\u770b\u4f5c\u4e00\u4e2a\u7cfb\u7edf\u2014\u2014\u4e5f\u7b2c\u4e00\u6b21\u770b\u6e05\u5b83\u5230\u5e95\u5361\u5728\u4e86\u54ea\u91cc\u3002',
          name: 'Maya R.',
          role: '\u4ea7\u54c1\u8bbe\u8ba1\u5e08',
        },
        {
          quote: '\u6211\u540e\u6765\u624d\u53d1\u73b0\uff0c\u81ea\u5df1\u8fd9\u4e9b\u5e74\u4e00\u76f4\u5728\u8ffd\u8e2a\u4efb\u52a1\uff0c\u5374\u4ece\u6765\u6ca1\u6709\u771f\u6b63\u63a8\u8fdb\u8fc7\u6700\u91cd\u8981\u7684\u4f18\u5148\u4e8b\u9879\u3002LifeOS \u8ba9\u6211\u770b\u89c1\u4e86\u201c\u6211\u53e3\u4e2d\u60f3\u8981\u7684\u4eba\u751f\u201d\u548c\u201c\u6211\u5b9e\u9645\u4e0a\u5982\u4f55\u5206\u914d\u65f6\u95f4\u201d\u4e4b\u95f4\u7684\u5de8\u5927\u843d\u5dee\u3002',
          name: 'James T.',
          role: '\u521b\u9020\u8005',
        },
        {
          quote: '\u5b83\u4e0d\u53ea\u662f\u4e00\u4e2a\u5e94\u7528\u3002\u5b83\u6539\u53d8\u4e86\u6211\u7406\u89e3\u81ea\u5df1\u6bcf\u4e00\u5929\u7684\u65b9\u5f0f\u3002\u6211\u4e0d\u518d\u53ea\u662f\u88ab\u52a8\u53cd\u5e94\uff0c\u800c\u662f\u5f00\u59cb\u6709\u610f\u8bc6\u5730\u7ecf\u8425\u81ea\u5df1\u7684\u4eba\u751f\u3002\u8fd9\u79cd\u8f6c\u53d8\u5f88\u96be\u89e3\u91ca\uff0c\u4f46\u4f60\u4f1a\u975e\u5e38\u6e05\u695a\u5730\u611f\u89c9\u5230\u5b83\u3002',
          name: 'Priya N.',
          role: '\u521b\u610f\u603b\u76d1',
        },
      ],
    },
    waitlist: {
      eyebrow: '\u79c1\u5bc6 Alpha \u5185\u6d4b',
      headline: '\u522b\u518d\u628a\u751f\u6d3b\u8fc7\u6210\u4e00\u5806\u788e\u7247\u3002',
      sub: 'LifeOS \u6b63\u5728\u5411\u4e00\u5c0f\u7fa4\u4eba\u5f00\u653e\u4f53\u9a8c\u8d44\u683c\u2014\u2014\u4ed6\u4eec\u5df2\u7ecf\u53d7\u591f\u4e86\u5f7c\u6b64\u5272\u88c2\u7684\u5de5\u5177\uff0c\u51c6\u5907\u5f00\u59cb\u628a\u4eba\u751f\u5f53\u4f5c\u4e00\u4e2a\u6574\u5408\u7684\u6574\u4f53\u6765\u8fd0\u884c\u3002\u4ed6\u4eec\u6709\u91ce\u5fc3\u3001\u4f1a\u53cd\u601d\uff0c\u4e5f\u60f3\u8981\u7ed3\u6784\uff0c\u4f46\u4e0d\u60f3\u6d3b\u5f97\u50cf\u673a\u5668\u3002',
      tags: [
        '\u6211\u6709\u91ce\u5fc3\uff0c\u4f46\u8fd8\u4e0d\u591f\u6709\u7ed3\u6784',
        '\u6211\u7684\u5de5\u5177\u5f7c\u6b64\u4e4b\u95f4\u5b8c\u5168\u4e0d\u8fde\u901a',
        '\u6211\u60f3\u66f4\u6df1\u5165\u5730\u7406\u89e3\u81ea\u5df1',
        '\u6211\u60f3\u8981\u7684\u662f\u6210\u957f\uff0c\u800c\u4e0d\u53ea\u662f\u6548\u7387',
        '\u6211\u7684\u751f\u6d3b\u59cb\u7ec8\u5f88\u5206\u6563',
      ],
      formTitle: '\u52a0\u5165\u7b49\u5019\u540d\u5355',
      footnote: '\u8f6e\u5230\u4f60\u65f6\uff0c\u6211\u4eec\u4f1a\u4eb2\u81ea\u8054\u7cfb\u4f60\u3002\u6ca1\u6709\u65b0\u95fb\u90ae\u4ef6\uff0c\u6ca1\u6709\u566a\u97f3\u3002',
    },
    footer: {
      rights: '\u00a9 2026 LifeOS. \u4fdd\u7559\u6240\u6709\u6743\u5229\u3002',
      links: ['\u9690\u79c1\u653f\u7b56', '\u670d\u52a1\u6761\u6b3e'],
    },
  },
};
