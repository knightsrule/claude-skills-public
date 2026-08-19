# Styling & Design System

Use Tailwind CSS (v4, CSS-first) with a **semantic token architecture**. One styling API throughout the application.

## Rules

- Never use arbitrary product colors directly in components — no `bg-blue-600`, `text-slate-500`, or hex values in JSX.
- Components consume semantic utilities: `bg-background`, `bg-card`, `text-foreground`, `text-muted-foreground`, `border-border`, `bg-primary`, `text-primary-foreground`, etc.
- Brand and theme values live in CSS variables only.
- Light/dark values live in `:root` and `.dark`.
- Map semantic CSS variables into Tailwind using `@theme inline`.
- Use `@theme` for reusable Tailwind design tokens: fonts, spacing, breakpoints, radius, shadows.
- Avoid component-specific global CSS.
- Use Tailwind utilities for component composition.
- Use `cn()` for conditional class composition.
- Use CVA for reusable components with meaningful variants.
- Do **not** generate `themes.ts` / `tokens.ts` JS token files — that is the Tailwind v3 pattern.

## Token Architecture

This matches shadcn's Tailwind v4 guidance (`:root`/`.dark` + `@theme inline`):

```css
:root {
  --background: oklch(...);
  --foreground: oklch(...);
  --primary: oklch(...);
  --primary-foreground: oklch(...);
  /* card, muted, border, ring, destructive, ... */
}

.dark {
  --background: oklch(...);
  --foreground: oklch(...);
  --primary: oklch(...);
}

@theme inline {
  --color-background: var(--background);
  --color-foreground: var(--foreground);
  --color-primary: var(--primary);
  --color-primary-foreground: var(--primary-foreground);
}
```

Include a `ThemeToggle` component wired to the class strategy.

## Palette Direction

Infer a distinctive palette from the product category:

- Developer Tool → darker, denser, monospace accents
- Healthcare → clean, trustworthy, high contrast
- Enterprise → restrained, professional
- Fintech → premium, minimal

Avoid the generic AI-default indigo/purple gradient look.

## Responsive UI Requirements

Design **mobile-first**. Every generated page must work at:

- 320–375px (mobile)
- 768px (tablet)
- 1024px (laptop)
- 1440px+ (desktop)

Rules:

- No unintended horizontal page scrolling.
- Content containers use consistent responsive max-width and gutters.
- Sidebar becomes Sheet/drawer navigation on mobile.
- Multi-column layouts collapse intentionally.
- Tables scroll horizontally or switch to a mobile presentation.
- Dialogs fit small screens.
- Forms become single-column on narrow screens unless inherently compact.
- Touch targets remain usable on mobile.
- Navigation, forms, modals, and menus are keyboard accessible.
