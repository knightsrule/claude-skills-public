# Authentication — AscendKit (ascendkit.dev)

Default provider: **AscendKit** (https://ascendkit.dev). Isolate all of it behind `src/lib/auth` so it can be swapped later.

Install and configure via the AscendKit CLI:

```bash
npm install @ascendkit/nextjs
npx ascendkit init
npx ascendkit auth --providers google,linkedin   # adjust providers to the brief
```

> The CLI scaffolds the provider wiring and env vars. Confirm the exact session/component API and env var names from the AscendKit docs (https://ascendkit.dev/docs) before hand-writing the adapter — do not invent the API. The shape below is the **adapter contract** the rest of the app depends on — keep it stable regardless of provider internals.

## Adapter Boundary

Generate behind `src/lib/auth`:

- `src/lib/auth/client.ts` — AscendKit client init (reads env).
- `src/lib/auth/session.ts` — server helpers: `getSession()` and `requireAuth()` (redirects to `/login` when unauthenticated).
- `src/lib/auth/provider.tsx` — client provider wrapper for the app tree.

## Pages & Protection

- Login, Signup, Forgot Password pages under `(auth)`.
- Protected routes via `requireAuth()` in the `(app)` layout (and/or middleware).
- User menu wired to the current session + sign-out.
- **Authorization is additionally enforced at the data/action boundary** (see architecture reference) — the protected layout alone is not a security boundary.

Env vars for AscendKit go in `.env.example` and are validated in `lib/env.ts` — use the exact variable names from the AscendKit docs.
