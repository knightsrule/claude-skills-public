---
name: nextjs-saas
description: "Generate a production-quality Next.js SaaS application scaffold from a project name and a description or PRD. Use when the user wants to bootstrap a new Next.js startup/SaaS app, scaffold a web product, create a marketing site plus an authenticated dashboard, or turn a PRD into a working Next.js foundation. Drives the create-next-app and shadcn CLIs (Next.js 15, React 19, Tailwind v4), infers architecture from the brief, and produces a config-driven, themeable, extensible codebase. Triggers on requests like 'scaffold a Next.js SaaS app', 'bootstrap a startup web app', or 'build the foundation for <product>'."
---

# Next.js SaaS Scaffold Generator

Generate a production-quality Next.js application scaffold from a **project name** and a **description or PRD**. The result should feel like the foundation of a real startup product — not an AI demo. Prioritize maintainability, extensibility, and production readiness over visual flashiness.

The skill works in two phases: **analyze the brief and confirm an architecture**, then **bootstrap via CLIs and layer opinionated structure on top**. Do not hand-write boilerplate that a CLI can generate.

---

## Required Inputs

1. **Project name** — human-readable product name (e.g. `Acme Analytics`). Used for the package name (kebab-case), titles, and copy.
2. **Project description or PRD** — short description, product brief, PRD, existing site copy, marketing copy, or functional requirements. Infer architecture from whatever is supplied.

If the description is missing, ask for one sentence on what the product does and who it's for before proceeding.

---

## Phase 1 — Analyze & Confirm

Before generating anything, derive and then **present a short architecture summary for confirmation**:

- **Product category** — e.g. Developer Tool, AI Application, B2B SaaS, Healthcare, Marketplace, Internal Platform, Consumer, Fintech.
- **Target audience** — primary user personas.
- **Core entities** — e.g. User, Team, Organization, Project, Workspace, Campaign. These drive types and feature folders.
- **Feature modules** — e.g. Dashboard, Analytics, Settings, Billing, Teams, Users, Admin, Reports. These drive navigation and `features/`.
- **Navigation hierarchy** — derived from feature modules; lives in `config/navigation.ts`.
- **Theme recommendation** — infer a distinctive palette and feel from the category:
  - Developer Tool → darker, denser, monospace accents
  - Healthcare → clean, trustworthy, high contrast
  - Enterprise → restrained, professional
  - Fintech → premium, minimal
  - Avoid generic AI-default palettes (the indigo/purple gradient look).

Wait for the user to confirm or adjust before generating code. Keep the summary tight.

---

## Phase 2 — Bootstrap (CLI-driven)

Use the official CLIs; do not regenerate what they produce. Pin to the latest stable line: **Next.js 15, React 19, Tailwind v4**.

```bash
npx create-next-app@latest <kebab-name> \
  --typescript --tailwind --eslint --app --src-dir \
  --import-alias "@/*" --use-npm
cd <kebab-name>
npx shadcn@latest init
```

Then add the components the inferred feature set needs, e.g.:

```bash
npx shadcn@latest add button card input form dialog dropdown-menu \
  table badge avatar sheet tabs sonner skeleton
```

Add remaining runtime deps:

```bash
npm i @tanstack/react-query zustand react-hook-form zod lucide-react
```

> Tailwind v4 is **CSS-first**. Define design tokens with `@theme` in `globals.css` — do **not** generate `themes.ts` / `tokens.ts` JS token files (that is the v3 pattern). Use CSS variables + semantic token names; no hardcoded component colors.

---

## Technology Stack

- Next.js 15 (App Router) + React 19
- TypeScript (strict)
- Tailwind CSS v4
- shadcn/ui
- React Hook Form + Zod
- TanStack Query (server state)
- Zustand (client state)
- Lucide icons

---

## Folder Structure

```
src/
  app/                # routes (marketing, auth, dashboard groups)
  features/           # domain modules: dashboard/ analytics/ settings/ billing/
  components/         # shared UI (incl. shadcn under components/ui)
  layouts/            # MarketingLayout, AuthLayout, DashboardLayout
  lib/                # auth, env, analytics, flags, query client, utils
  hooks/
  config/             # navigation.ts, site.ts
  styles/             # globals.css (Tailwind v4 @theme tokens)
  types/
```

Organize app routes with route groups: `(marketing)`, `(auth)`, `(app)`.

---

## Authentication — AscendKit (ascendkit.dev)

Default provider: **AscendKit** (https://ascendkit.dev). Isolate all of it behind `src/lib/auth` so it can be swapped later.

Install and configure via the AscendKit CLI:

```bash
npm install @ascendkit/nextjs
npx ascendkit init
npx ascendkit auth --providers google,linkedin   # adjust providers to the brief
```

> The CLI scaffolds the provider wiring and env vars. Confirm the exact session/component API and env var names from the AscendKit docs (https://ascendkit.dev/docs) before hand-writing the adapter — do not invent the API. The shape below is the **adapter contract** the rest of the app depends on — keep it stable regardless of provider internals.

Generate behind `src/lib/auth`:
- `src/lib/auth/client.ts` — AscendKit client init (reads env).
- `src/lib/auth/session.ts` — server helpers: `getSession()` and `requireAuth()` (redirects to `/login` when unauthenticated).
- `src/lib/auth/provider.tsx` — client provider wrapper for the app tree.

Generate pages/components:
- Login, Signup, Forgot Password pages under `(auth)`.
- Protected routes via `requireAuth()` in the `(app)` layout (and/or middleware).
- User menu wired to the current session + sign-out.

Env vars for AscendKit go in `.env.example` and are validated in `lib/env.ts` — use the exact variable names from the AscendKit docs.

---

## Marketing Site

One landing page under `(marketing)` with realistic placeholder copy derived from the description. Sections (single canonical list):

Hero · Social Proof · Features · Benefits · How It Works · Screenshots · Testimonials · Pricing · FAQ · CTA · Footer

---

## Authenticated Experience

**Header:** logo, search placeholder, notifications placeholder, theme switch, user menu.

**Sidebar:** collapsible, mobile-responsive (Sheet on mobile), **navigation driven entirely by `config/navigation.ts`** — never hardcode nav items in components.

---

## Theme System (Tailwind v4)

- Light + dark themes via CSS variables and a `data-theme` / class strategy.
- Semantic tokens defined in `globals.css` `@theme` (background, foreground, primary, muted, border, etc.).
- A `ThemeToggle` component.
- Distinctive, category-appropriate palette — no hardcoded colors in components.

---

## Common Components

`PageHeader`, `DataTable`, `EmptyState`, `LoadingState`, `ErrorState`, `ConfirmDialog`, `ThemeToggle`.

---

## State, Forms, Data

- TanStack Query provider + an example query/mutation.
- A Zustand store example (e.g. UI/sidebar state).
- One example form with React Hook Form + Zod schema and inline validation.

---

## Cross-Cutting

- **SEO:** metadata, OpenGraph, Twitter cards, `sitemap.ts`, `robots.ts`, `manifest.webmanifest`, favicon.
- **Env:** `.env.example` + `lib/env.ts` validating all vars with Zod (fail fast at startup).
- **Analytics:** `lib/analytics` exposing `track()`, `identify()`, `page()` — interface only, no provider.
- **Feature flags:** `lib/flags` exposing `isEnabled("feature-name")`.

---

## Documentation

Generate `README.md` (setup + scripts), `ARCHITECTURE.md` (folders, data flow, auth boundary), `THEMING.md` (tokens + how to add a theme).

---

## Output Process

1. Analyze the brief.
2. Present the inferred architecture summary; get confirmation.
3. Bootstrap via the CLIs above.
4. Layer the opinionated structure and scaffolded code.
5. Generate docs and setup instructions.

## Definition of Done

Before declaring success, verify:
- `npm install` completes clean.
- `npm run build` passes (no type or build errors).
- `npm run lint` passes.
- App starts and the marketing page + a protected route behave (redirect when logged out).

Report any failing step with its output rather than claiming completion.
