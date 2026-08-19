# Architecture Rules

## Next.js Architecture Rules

- **Server Components are the default.**
- Add `"use client"` only where browser APIs, event handlers, hooks, or client-side state require it.
- Keep client boundaries as low in the component tree as practical. Do not make an entire page or layout a Client Component because one nested control is interactive.
- Fetch initial page data in Server Components whenever possible.
- Perform mutations through Server Actions or Route Handlers as appropriate.
- Do not introduce client-side fetching simply because a fetching library is installed.

Preferred data flow for most SaaS screens:

```
Server Component → DAL/domain function → database or external service
```

not:

```
Client Component → TanStack Query → API route → database
```

## Folder Structure

```
src/
  app/                  # routing and route composition ONLY
    (marketing)/
      layout.tsx
      page.tsx
    (auth)/
      layout.tsx
      login/ signup/ forgot-password/
    (app)/
      layout.tsx        # protected shell; calls requireAuth()
      loading.tsx
      error.tsx
      ...feature routes
    error.tsx
    global-error.tsx
    not-found.tsx
  features/             # domain-specific behavior
    projects/
      components/
      schemas/
      actions/
      queries/
      types.ts
    billing/
    onboarding/
  components/           # reusable application UI
    layout/
      app-shell.tsx
      app-sidebar.tsx
      app-header.tsx
    ui/                 # design-system primitives (shadcn)
  lib/                  # infrastructure and cross-cutting capabilities
    auth/
    db/
    dal/
    analytics/
    flags/
    env/
    utils.ts            # cn() etc.
  hooks/
  config/               # navigation.ts, site.ts
  styles/               # globals.css (tokens)
  types/
```

There is **no separate `layouts/` folder**. Route layouts live in the App Router as `layout.tsx` inside route groups; reusable shell pieces live in `components/layout/`.

## Ownership Rules

- `app/` owns routing and route composition.
- `features/` owns domain-specific behavior.
- `components/` owns reusable application UI.
- `components/ui/` owns design-system primitives.
- `lib/` owns infrastructure and cross-cutting capabilities.
- **Do not place business logic directly inside route components.** Route components compose; features and the DAL do the work.

## Data Access Layer

- All database and privileged external-service access stays server-side.
- Pages and Server Actions call a DAL/domain function (`lib/dal/` or `features/<domain>/queries|actions`) rather than accessing the database directly throughout the codebase.
- **Authorization is enforced at the data/action boundary**, not only through protected layouts. Every DAL function that touches tenant data takes the current session/tenant and scopes the query — a protected layout is a UX convenience, not a security boundary.

## Error / Loading / Not-Found Conventions

A production foundation includes the App Router convention files by default:

- `app/error.tsx`, `app/global-error.tsx`, `app/not-found.tsx`
- `(app)/loading.tsx`, `(app)/error.tsx`
- Feature-level `<Suspense>` boundaries where a slow section shouldn't block the page.

Error components show a useful message and a retry affordance; loading states use skeletons consistent with the design system, not spinners everywhere.
