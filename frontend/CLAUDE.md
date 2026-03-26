# LifeOS Frontend Context

This is the Next.js frontend for LifeOS. Read `DESIGN.md` (project root) before building any page or component.

## Structure

```
frontend/
├── app/               # Next.js App Router
│   ├── (app)/         # Protected routes (calendar, habits, projects, skills, insights)
│   ├── (auth)/        # Auth routes (login)
│   ├── layout.tsx     # Root layout
│   ├── providers.tsx  # Context providers (React Query, etc.)
│   └── globals.css    # Tailwind base styles
├── components/
│   ├── shell/         # Layout shells, navigation
│   └── ui/            # shadcn/ui component library
└── lib/
    ├── api/           # Fetch wrappers, API client
    ├── auth/          # Auth context, token management
    └── utils.ts       # Common utilities
```

## Tech Stack
- Next.js 16 + React 19 + TypeScript
- Tailwind CSS v4 + shadcn/ui + Base UI
- React Query v5 for server state
- lucide-react for icons

## Design System: The Botanical Editorial

Always follow `DESIGN.md`. Non-negotiable rules:
- Cards: `border-radius: 0 16px 16px 16px` (sharp top-left). Never `clip-path`.
- Buttons: `rounded-full` always. No exceptions.
- Typography: Newsreader (headlines, -0.03em) + Manrope (body/labels).
- Colors: Sage palette only. No `#000000`, no zinc/slate grays.
- Borders: Background color shifts, not 1px lines.
- Shadows: Tinted `rgba(46,52,43,0.06)`. Never pure grey.

## Key Rules
- Auth context must stay swappable (future Clerk migration planned).
- API client lives in `lib/api/`. Use React Query for all server state.
- Protected routes go in `(app)/` group, auth routes in `(auth)/`.

## Calendar Route Notes
- Calendar page lives at `app/(app)/calendar/page.tsx`.
- Current UX includes a month grid, day selection, event density dots, and same-day agenda list.
- Event CRUD on this page is wired through `lib/api/calendar.ts`.
- Inline event editing is supported in agenda rows and uses `calendarApi.update(...)`.
