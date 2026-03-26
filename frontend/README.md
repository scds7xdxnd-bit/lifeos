# LifeOS Frontend

LifeOS frontend is a Next.js 16 + React 19 application that implements the Botanical Editorial design system and consumes the LifeOS Flask API.

## Stack

- Next.js 16 (App Router)
- React 19 + TypeScript
- Tailwind CSS v4
- React Query v5
- shadcn/ui + Base UI

## Local Development

```bash
cd frontend
npm install
npm run dev
```

App runs at `http://localhost:3000`.

## Build

```bash
cd frontend
npm run build
```

## App Route Groups

- `(auth)` for login and invite flows
- `(onboarding)` for first-run onboarding
- `(app)` for authenticated product surfaces

## Calendar Surface

Path: `/calendar`

Current capabilities:
- Month-grid calendar with previous/next navigation and Today jump
- Per-day event density indicators on grid cells
- Day selection with same-day agenda view
- Create event flow (title, location, start/end, all-day)
- Inline event edit flow in the agenda list
- Delete event flow from agenda rows

Calendar data integration:
- API module: `lib/api/calendar.ts`
- Page implementation: `app/(app)/calendar/page.tsx`
- Server state: React Query (`calendar-events` query key)

## Design Requirements

This repo uses The Botanical Editorial style language.

Key requirements:
- Newsreader + Manrope typography pairing
- Cards with clipped-specimen radius (`0 16px 16px 16px`)
- Pill buttons (`rounded-full`)
- Sage-first palette and tinted shadows

Reference:
- `DESIGN.md` (project root)
- `frontend/CLAUDE.md`

## Notes

- Keep API access through `lib/api/*` modules.
- Keep protected pages under `app/(app)`.
- Prefer deterministic UI behavior and explicit user actions over hidden automation.
