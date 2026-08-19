# Testing & Quality Gates

Testing is part of the Definition of Done, not an afterthought.

## Setup

Configure per current official Next.js guidance:

- **Vitest + React Testing Library** for unit/component tests.
- **Playwright** for critical user journeys.

Add npm scripts: `test` (vitest), `test:e2e` (playwright).

## Minimum Unit/Component Tests

- One test per common component that has logic (e.g. `EmptyState` renders CTA, `DataTable` renders rows).
- Schema tests for any Zod schemas with non-trivial refinement.

## Minimum Playwright Smoke Tests

1. Marketing homepage renders.
2. Login page renders.
3. Protected route redirects when unauthenticated.
4. Mobile navigation opens/closes correctly.
5. Primary dashboard renders without console errors.

Test critical screens at mobile **and** desktop viewport sizes.

## Verification Order

1. `npm run lint`
2. `npm run build`
3. `npm test`
4. `npm run test:e2e` (against a local dev or built server)

Report any failing step with its actual output. Do not claim completion with failing gates.
