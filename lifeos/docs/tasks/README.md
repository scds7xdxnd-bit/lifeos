# LifeOS Task Hub

This folder is the single place where each team reads and posts task definitions. New tasks live here; completed or superseded tasks move into the `archive/` subfolder.

Scope:
- Audience: Backend, Frontend, ML, QA, DevOps, Database, and Architecture.
- Use: Create task briefs, cross-team handoffs, and status notes.
- History: When a task is done or replaced, move its file into `archive/` to keep the active list lean and auditable.

Why this exists:
- Calendar refactor and other subsystem corrections now require a shared, deterministic task site.
- Prevents task sprawl across PRs, chat, and ad-hoc docs.
- Keeps task history preserved for replay and accountability.

Rules of engagement:
- One task per file; include owners, due date, status, and links to specs/PRs.
- Do not delete tasks; archive them when finished or superseded.
- Keep content concise and actionable; no UI mockups or code in this folder.
