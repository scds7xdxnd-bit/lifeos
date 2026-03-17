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
      badge: 'Private Alpha · Limited Spots',
      headline1: 'Your life is a system.',
      headline2: 'Start running it like one.',
      sub: 'Most people manage life in fragments — tasks in one app, money in another, goals only in their head. LifeOS integrates your goals, habits, time, health, finances, and reflection into one coherent system, so you can finally see what\'s actually happening and act on it.',
      primaryCta: 'Join the Private Alpha',
      secondaryCta: 'See how it works ↓',
      footnote: 'Free to join · Private alpha · Limited spots',
      cards: {
        card1: { label: 'Cross-Domain Pattern', text: 'Your productivity drops on weeks when sleep averages under 6 hrs.' },
        card2: { label: 'Inquiry', text: '"Why am I always behind?" → Your top 3 goals haven\'t moved in 3 weeks — your schedule is reactive.' },
        card3: { label: 'Habit Signal', text: 'Your habits hold on days you train. Consistency drops when exercise stops.' },
      },
    },
    features: {
      eyebrow: 'The four things LifeOS does',
      headline: 'Life is a system. LifeOS treats it like one.',
      items: [
        {
          title: 'Centralise your life',
          body: 'Goals, habits, tasks, calendar, finances, health, journaling, relationships, learning — brought into one structured environment instead of scattered across disconnected tools.',
        },
        {
          title: 'Make the invisible visible',
          body: 'Most people aren\'t lost because they\'re lazy. They\'re lost because they can\'t see the system clearly. LifeOS shows you what\'s changing, what\'s being neglected, and what\'s creating downstream problems.',
        },
        {
          title: 'Ask questions that actually matter',
          body: 'Ask things like "Where is my time really going?", "What\'s driving my low energy?" or "Am I building the life I said I wanted?" and get answers grounded in your actual data.',
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
          body: 'Add your goals, habits, schedule, finances, and reflections. LifeOS becomes the single environment where your life is structured — not just stored.',
        },
        {
          step: '02',
          title: 'See how it connects',
          body: 'LifeOS surfaces relationships you\'d never notice manually. Poor sleep affects focus. Chaotic weeks spike spending. Weak habits slow long-term goals. Now you can see it.',
        },
        {
          step: '03',
          title: 'Act with the full picture',
          body: 'Make decisions based on your whole life, not a fragment of it. Move from reactive to intentional — from overwhelmed to structured.',
        },
      ],
    },
    inquiry: {
      eyebrow: 'Inquiry Engine',
      headline: 'Ask questions you\'ve never been able to ask.',
      sub: 'Generic AI assistants know nothing about your life. LifeOS does. Every answer is grounded in your actual goals, habits, patterns, and history.',
      items: [
        {
          q: 'Why am I always behind on my goals?',
          a: 'Your top 3 goals haven\'t moved in 3 weeks. In that period, 80% of your logged time went to reactive tasks — not priorities. Your schedule is driving you, not the other way around.',
        },
        {
          q: 'What\'s actually draining my energy?',
          a: 'Your lowest-energy days follow nights under 6 hours of sleep, and correlate with skipped morning routines. On days you train, your focus score is 40% higher and habit completion doubles.',
        },
        {
          q: 'Am I building the life I said I wanted?',
          a: 'You\'ve stated growth, health, and deep work as priorities. In the last 30 days, 12% of your time went to deep work, 6% to health, and 67% to tasks you haven\'t linked to any goal.',
        },
      ],
    },
    social: {
      headline: 'For people who felt the problem.',
      items: [
        {
          quote: 'I had ambition and twelve different apps. I was busy but going nowhere. LifeOS was the first time I could actually see my life as a system — and see where it was breaking.',
          name: 'Maya R.',
          role: 'Product designer',
        },
        {
          quote: 'I realised I\'d been tracking tasks for years without ever moving my actual priorities. LifeOS showed me the gap between the life I said I wanted and how I was actually spending my time.',
          name: 'James T.',
          role: 'Builder',
        },
        {
          quote: 'It\'s not just an app. It changed how I think about my days. I stopped reacting and started running my life deliberately. That shift is hard to explain but very easy to feel.',
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
        'My tools don\'t talk to each other',
        'I want to understand myself better',
        'I want growth, not just productivity',
        'My life feels scattered',
      ],
      formTitle: 'Join the Waitlist',
      footnote: 'We\'ll reach out personally when your spot is ready. No newsletters, no noise.',
    },
    footer: {
      rights: '© 2026 LifeOS. All rights reserved.',
      links: ['Privacy', 'Terms'],
    },
  },

  zh: {
    nav: {
      cta: '获取抢先体验资格',
    },
    hero: {
      badge: '私密 Alpha 内测 · 名额有限',
      headline1: '你的生活，本就是一个系统。',
      headline2: '现在开始，像对待系统一样管理它。',
      sub: '大多数人都在碎片化地管理生活——任务放在一个应用里，金钱放在另一个，目标只存在脑海中。LifeOS 将你的目标、习惯、时间、健康、财务与反思整合进一个连贯的系统，让你终于看清生活里究竟发生了什么，并据此行动。',
      primaryCta: '加入私密 Alpha 内测',
      secondaryCta: '看看它如何运作 ↓',
      footnote: '免费加入 · 私密 Alpha 内测 · 名额有限',
      cards: {
        card1: { label: '跨领域模式', text: '当一周平均睡眠低于 6 小时时，你的效率会明显下降。' },
        card2: { label: '问询', text: '“为什么我总是落在后面？”→ 你最重要的 3 个目标已经 3 周没有推进——你的日程在驱动你，而不是你在主导日程。' },
        card3: { label: '习惯信号', text: '你在训练的日子里更能保持习惯；一旦停止运动，稳定性就会下降。' },
      },
    },
    features: {
      eyebrow: 'LifeOS 能为你做什么',
      headline: '生活是一个系统，LifeOS 就按系统来对待它。',
      items: [
        {
          title: '把生活整合到一起',
          body: '目标、习惯、任务、日历、财务、健康、日记、关系、学习——不再散落在彼此割裂的工具中，而是进入一个统一且结构化的环境。',
        },
        {
          title: '让看不见的问题浮现出来',
          body: '大多数人不是因为懒而迷失，而是因为他们看不清整个系统。LifeOS 帮你看见什么正在变化、什么被忽略了、以及什么正在引发后续问题。',
        },
        {
          title: '提出真正重要的问题',
          body: '你可以问：“我的时间到底花到哪里去了？”“是什么在拖垮我的精力？”“我真的在构建自己想要的人生吗？”——并得到基于你真实数据的回答。',
        },
      ],
    },
    howItWorks: {
      eyebrow: '如何运作',
      headline: '从碎片化，走向结构化。',
      steps: [
        {
          step: '01',
          title: '把你的生活放进来',
          body: '加入你的目标、习惯、日程、财务和反思。LifeOS 会成为你整理生活的统一环境——不只是存放信息的地方。',
        },
        {
          step: '02',
          title: '看见它们如何彼此关联',
          body: 'LifeOS 会呈现那些你靠手动几乎不可能发现的关系：睡不好会削弱专注，混乱的一周会推高支出，薄弱的习惯会拖慢长期目标。现在，这些都能被看见。',
        },
        {
          step: '03',
          title: '在完整视角下行动',
          body: '不再只根据生活的某个片段做决定，而是基于整体来判断。你会从被动应付，转向有意识地主导——从混乱失控，转向清晰有序。',
        },
      ],
    },
    inquiry: {
      eyebrow: '问询引擎',
      headline: '问出那些你过去根本无从发问的问题。',
      sub: '通用 AI 助手并不了解你的生活，但 LifeOS 了解。每一个回答都建立在你真实的目标、习惯、模式与历史之上。',
      items: [
        {
          q: '为什么我总是赶不上自己的目标？',
          a: '你最重要的 3 个目标已经 3 周没有推进。在这段时间里，你记录的时间有 80% 都花在了被动应对型任务上，而不是优先事项。是日程在推着你走，而不是你在掌控日程。',
        },
        {
          q: '到底是什么在消耗我的精力？',
          a: '你精力最低的日子，通常都出现在前一晚睡眠不足 6 小时之后，并且常常伴随着晨间例程被跳过。而在你训练的日子里，专注得分会高出 40%，习惯完成率也会翻倍。',
        },
        {
          q: '我真的在构建自己想要的人生吗？',
          a: '你曾把成长、健康和深度工作列为优先事项。但在过去 30 天里，你只有 12% 的时间投入深度工作，6% 投入健康，而 67% 的时间则花在了那些没有关联到任何目标的任务上。',
        },
      ],
    },
    social: {
      headline: '献给那些真正感受过这个问题的人。',
      items: [
        {
          quote: '我有野心，也装了十几个应用。我一直很忙，却始终没有真正前进。LifeOS 是第一次让我真正把人生看作一个系统——也第一次看清它到底卡在了哪里。',
          name: 'Maya R.',
          role: '产品设计师',
        },
        {
          quote: '我后来才发现，自己这些年一直在追踪任务，却从来没有真正推进过最重要的优先事项。LifeOS 让我看见了“我口中想要的人生”和“我实际上如何分配时间”之间的巨大落差。',
          name: 'James T.',
          role: '创造者',
        },
        {
          quote: '它不只是一个应用。它改变了我理解自己每一天的方式。我不再只是被动反应，而是开始有意识地经营自己的人生。这种转变很难解释，但你会非常清楚地感觉到它。',
          name: 'Priya N.',
          role: '创意总监',
        },
      ],
    },
    waitlist: {
      eyebrow: '私密 Alpha 内测',
      headline: '别再把生活过成一堆碎片。',
      sub: 'LifeOS 正在向一小群人开放体验资格——他们已经受够了彼此割裂的工具，准备开始把人生当作一个整合的整体来运行。他们有野心、会反思，也想要结构，但不想活得像机器。',
      tags: [
        '我有野心，但还不够有结构',
        '我的工具彼此之间完全不连通',
        '我想更深入地理解自己',
        '我想要的是成长，而不只是效率',
        '我的生活始终很分散',
      ],
      formTitle: '加入等候名单',
      footnote: '轮到你时，我们会亲自联系你。没有新闻邮件，没有噪音。',
    },
    footer: {
      rights: '© 2026 LifeOS. 保留所有权利。',
      links: ['隐私政策', '服务条款'],
    },
    },
};
