---
name: nextjs-saas
description: "Generate a production-quality Next.js SaaS application scaffold from a project name and a description or PRD. Use when the user wants to bootstrap a new Next.js startup/SaaS app, scaffold a web product, create a marketing site plus an authenticated dashboard, or turn a PRD into a working Next.js foundation. Drives the create-next-app and shadcn CLIs on the latest stable releases, defaults to Server Components, establishes semantic design tokens, mobile-first responsive behavior, and a data-access boundary, and produces a maintainable, extensible codebase. Triggers on requests like 'scaffold a Next.js SaaS app', 'bootstrap a startup web app', or 'build the foundation for <product>'."
argument-hint: "<project-name> [description or PRD path]"
---

# Next.js SaaS Scaffold Generator

**Governing principle:** Generate the smallest production-grade architecture justified by the PRD. Prefer Next.js platform capabilities and Server Components. Establish strong domain boundaries, semantic design tokens, mobile-first responsive behavior, accessibility, and automated verification. Add client-state or infrastructure libraries only when the product requires them.

The result should feel like the foundation of a real startup product a professional engineering team could continue building — not an AI demo. Do not hand-write boilerplate that a CLI can generate.

Detailed rules live in supporting files — read each one before doing the corresponding work:

- [references/architecture.md](references/architecture.md) — Server Component rules, folder structure, feature/domain boundaries, data access layer, error/loading conventions
- [references/styling.md](references/styling.md) — semantic token architecture, theming, responsive requirements
- [references/auth.md](references/auth.md) — authentication scaffold (AscendKit) behind a stable adapter boundary
- [references/testing.md](references/testing.md) — test setup, smoke tests, definition of done

---

## Required Inputs

1. **Project name** — human-readable product name (e.g. `Acme Analytics`). Used for the package name (kebab-case), titles, and copy.
2. **Project description or PRD** — short description, product brief, PRD, existing site copy, or functional requirements. Infer architecture from whatever is supplied.

If the description is missing, ask for one sentence on what the product does and who it's for before proceeding.

---

## Phase 1 — Analyze

Derive from the brief:

- **Product category** — e.g. Developer Tool, AI Application, B2B SaaS, Healthcare, Marketplace, Internal Platform, Consumer, Fintech.
- **Target audience** — primary user personas.
- **Core entities** — e.g. User, Team, Organization, Project, Workspace. These drive types and feature folders.
- **Feature modules** — e.g. Dashboard, Analytics, Settings, Billing, Teams, Admin. These drive navigation and `features/`.
- **Navigation hierarchy** — derived from feature modules; lives in `config/navigation.ts`.
- **Theme direction** — distinctive, category-appropriate palette (see styling reference). Avoid generic AI-default palettes (the indigo/purple gradient look).

Print a concise architecture summary, then **proceed**. Only stop for confirmation when a decision would materially alter the product architecture and cannot reasonably be inferred from the brief (e.g. multi-tenancy model, payments provider, unusual auth requirements).

---

## Phase 2 — Bootstrap (CLI-driven)

Use the latest stable releases supported by `create-next-app@latest`. Never select canary/beta versions unless the user asks. Do not pin framework versions in advance — after bootstrap, record the actual installed versions (Next.js, React, Tailwind, etc.) in `ARCHITECTURE.md`.

```bash
npx create-next-app@latest <kebab-name> \
  --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*" --use-npm
cd <kebab-name>
npx shadcn@latest init
```

Then add the shadcn components the inferred feature set needs, e.g.:

```bash
npx shadcn@latest add button card input form dialog dropdown-menu \
  table badge avatar sheet tabs sonner skeleton
```

Base runtime deps beyond what the CLIs install: `zod` and `lucide-react`. Everything else is governed by Dependency Discipline below.

> Tailwind v4 is **CSS-first**. Design tokens are defined in `globals.css` — do **not** generate `themes.ts` / `tokens.ts` JS token files (that is the v3 pattern). Full token architecture in [references/styling.md](references/styling.md).

## Dependency Discipline

Do not install a dependency merely because it is popular in SaaS stacks. Only add:

- **TanStack Query** — when meaningful client-side server-state synchronization exists. For most screens, Server Component → DAL → database beats Client → TanStack Query → API route → database.
- **Zustand** — when meaningful cross-component client state exists (rarely at scaffold time; a sidebar toggle doesn't need a store).
- **React Hook Form** — when the product's forms justify it.
- **Charting libraries** — when charts exist in the brief.
- **Database/ORM packages** — when persistence is required now.

Prefer platform and framework capabilities before introducing abstractions.

---

## What to Generate

Follow [references/architecture.md](references/architecture.md) for structure and boundaries. Highlights:

- **Marketing site** — one landing page under `(marketing)` with realistic placeholder copy derived from the description. Sections: Hero · Social Proof · Features · Benefits · How It Works · Screenshots · Testimonials · Pricing · FAQ · CTA · Footer.
- **Authenticated app** — `(app)` route group. Header: logo, search placeholder, notifications placeholder, theme switch, user menu. Sidebar: collapsible, Sheet/drawer on mobile, **navigation driven entirely by `config/navigation.ts`** — never hardcode nav items in components.
- **Auth** — per [references/auth.md](references/auth.md), isolated behind `lib/auth`, authorization enforced at the data/action boundary.
- **Common components** — `PageHeader`, `DataTable`, `EmptyState`, `LoadingState`, `ErrorState`, `ConfirmDialog`, `ThemeToggle`.
- **Error/loading/not-found** — App Router convention files per the architecture reference.

## Cross-Cutting

- **SEO:** metadata, OpenGraph, Twitter cards, `sitemap.ts`, `robots.ts`, `manifest.webmanifest`, favicon.
- **Env:** `.env.example` + `lib/env.ts` validating all vars with Zod (fail fast at startup).
- **Analytics:** `lib/analytics` exposing `track()`, `identify()`, `page()` — interface only, no provider.
- **Feature flags:** `lib/flags` exposing `isEnabled("feature-name")`.

## Documentation

Generate `README.md` (setup + scripts), `ARCHITECTURE.md` (folders, data flow, auth boundary, **actual installed versions**), `THEMING.md` (tokens + how to add a theme).

---

## Output Process

1. Analyze the brief; print the architecture summary; proceed (stop only for material ambiguity).
2. Bootstrap via the CLIs above.
3. Layer the structure per the reference files.
4. Set up tests per [references/testing.md](references/testing.md).
5. Generate docs.
6. Run the Definition of Done checks below.

## Definition of Done

Before declaring success, verify:

- `npm install` completes clean.
- `npm run build` passes (no type or build errors).
- `npm run lint` passes.
- Unit tests and Playwright smoke tests pass ([references/testing.md](references/testing.md)).
- App starts; marketing page and a protected route behave (redirect when logged out); mobile navigation works.

Report any failing step with its output rather than claiming completion.
