const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const BASE = process.env.QA_BASE_URL || 'http://127.0.0.1:3000';
const API_BASE = process.env.QA_API_BASE_URL || 'http://127.0.0.1:5001';
const VIEWPORTS = [
  { name: '375x812', width: 375, height: 812 },
  { name: '414x896', width: 414, height: 896 },
  { name: '768x1024', width: 768, height: 1024 },
  { name: '1024x768', width: 1024, height: 768 },
  { name: '1440x900', width: 1440, height: 900 },
];

const REPO_ROOT = path.resolve(__dirname, '..', '..');

async function getDemoTokens() {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: 'demo@lifeos.test',
      password: 'demo12345',
    }),
  });
  if (!res.ok) {
    throw new Error(`Login failed for QA: ${res.status}`);
  }
  return res.json();
}

async function run() {
  const browser = await chromium.launch({ headless: true });
  const all = [];

  for (const vp of VIEWPORTS) {
    const context = await browser.newContext({ viewport: { width: vp.width, height: vp.height } });
    const page = await context.newPage();
    const consoleErrors = [];
    const http422 = [];

    page.on('console', (msg) => {
      if (msg.type() === 'error') {
        consoleErrors.push(msg.text());
      }
    });
    page.on('response', (resp) => {
      if (resp.status() === 422) {
        http422.push({
          status: resp.status(),
          method: resp.request().method(),
          url: resp.url(),
        });
      }
    });

    const row = {
      viewport: vp.name,
      status: 'ok',
      reason: '',
      horizontalScroll: null,
      hasLogButton: null,
      minLogButtonHeight: null,
      minPrimaryActionHeight: null,
      detailPanelVisible: null,
      consoleErrors,
      http422,
    };

    try {
      const tokens = await getDemoTokens();
      await context.addInitScript((stored) => {
        window.localStorage.setItem('lifeos_tokens', JSON.stringify(stored));
      }, {
        access_token: tokens.access_token,
        refresh_token: tokens.refresh_token,
        csrf_token: tokens.csrf_token,
      });

      await page.goto(`${BASE}/habits`, { waitUntil: 'networkidle', timeout: 45000 });

      const metrics = await page.evaluate(() => {
        const html = document.documentElement;
        const horizontalScroll = html.scrollWidth > window.innerWidth;

        const buttons = Array.from(document.querySelectorAll('button'));
        const buttonText = (b) => (b.textContent || '').toLowerCase().trim();

        const logButtons = buttons.filter((b) => {
          const txt = buttonText(b);
          return txt.includes('log') || txt.includes('undo');
        });

        const primaryButtons = buttons.filter((b) => {
          const txt = buttonText(b);
          return (
            txt.includes('create') ||
            txt.includes('new habit') ||
            txt.includes('log') ||
            txt.includes('undo') ||
            txt.includes('save')
          );
        });

        const visible = (el) => el.offsetParent !== null && el.getBoundingClientRect().height > 0;

        const minHeight = (arr) => {
          if (arr.length === 0) return null;
          const vis = arr.filter(visible);
          if (vis.length === 0) return null;
          return Math.min(
            ...vis.map((el) => Math.round(el.getBoundingClientRect().height))
          );
        };

        const detailPanelVisible = Array.from(document.querySelectorAll('p,h1,h2,h3,span,div'))
          .some((el) => {
            const text = (el.textContent || '').trim();
            return visible(el) && (
              text === 'Habit Detail' ||
              text === 'Select a habit to see its analytics'
            );
          });

        return {
          horizontalScroll,
          hasLogButton: logButtons.length > 0,
          minLogButtonHeight: minHeight(logButtons),
          minPrimaryActionHeight: minHeight(primaryButtons),
          detailPanelVisible,
        };
      });

      Object.assign(row, metrics);
    } catch (err) {
      row.status = 'blocked';
      row.reason = err && err.message ? err.message : String(err);
    }

    all.push(row);
    await context.close();
  }

  await browser.close();

  const out = {
    generatedAt: new Date().toISOString(),
    baseUrl: BASE,
    results: all,
  };

  const reportDir = path.join(REPO_ROOT, 'docs', 'runbooks');
  fs.mkdirSync(reportDir, { recursive: true });
  const jsonPath = path.join(reportDir, 'phase12d_habits_manual_qa_matrix.json');
  fs.writeFileSync(jsonPath, JSON.stringify(out, null, 2), 'utf8');

  console.log(JSON.stringify(out, null, 2));
}

run().catch((err) => {
  console.error(err);
  process.exit(1);
});
