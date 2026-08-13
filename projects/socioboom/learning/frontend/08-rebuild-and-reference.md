# SocioBoom Frontend — Rebuild From Scratch & Reference Appendices

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`). See also
every other file in `learning/frontend/` — this one is the synthesis layer that assumes them, and
`learning/backend/09-decisions-and-mastery.md` (the matching backend rebuild path).

This file covers: a step-by-step path to recreating the SocioBoom frontend from scratch, a key file
reference mapping every important file to what it does, and a dependency reference explaining why
each package in `package.json` is there.

---

## 18. Recreating the Frontend From Scratch

If you wanted to build this exact frontend from zero, here are the steps in order.

### Step 1: Bootstrap Next.js

```bash
npx create-next-app@latest frontend \
  --typescript \
  --tailwind \
  --eslint \
  --app \
  --src-dir \
  --import-alias "@/*"
```

Select "Yes" for the App Router when prompted. This sets up the `src/app/` structure and basic tsconfig aliases.

### Step 2: Update the tsconfig.json Paths

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/shared/*", "./src/*"]
    }
  }
}
```

### Step 3: Install Dependencies

```bash
pnpm add @tanstack/react-query axios sonner next-themes date-fns react-day-picker recharts lucide-react class-variance-authority clsx tailwind-merge tailwindcss-animate
pnpm add -D @tailwindcss/postcss
```

### Step 4: Install shadcn/ui

```bash
npx shadcn-ui@latest init
```

Then add components as needed:
```bash
npx shadcn-ui@latest add button card input textarea label badge tabs separator
npx shadcn-ui@latest add sidebar dialog dropdown-menu popover select
npx shadcn-ui@latest add calendar avatar checkbox skeleton sonner tooltip
```

Move the generated `components/ui/` folder to `src/shared/components/ui/`.

### Step 5: Set Up globals.css

Replace the generated Tailwind config with the v4 CSS-first approach. Define all CSS variables in `:root` and `.dark`, wire them into `@theme {}`, and add the dark variant:

```css
@import "tailwindcss";
@plugin "tailwindcss-animate";

@custom-variant dark (&:is(.dark *));

:root {
  --background: 250 100% 99%;
  --foreground: 240 10% 20%;
  /* ... all variables ... */
}

.dark {
  --background: 240 10% 8%;
  /* ... dark overrides ... */
}

@theme {
  --color-background: hsl(var(--background));
  /* ... wire vars to utilities ... */
}
```

### Step 6: Create the Shared Infrastructure

In order:

1. `src/shared/lib/utils.ts` — the `cn()` function
2. `src/shared/hooks/use-mobile.tsx` — the `useIsMobile()` hook
3. `src/shared/components/theme/ModeToggle.tsx` — the theme toggle
4. `src/shared/providers/index.tsx` — QueryClientProvider
5. `src/shared/components/layout/sidebar.tsx` — the sidebar
6. `src/shared/components/layout/navbar.tsx` — the top navbar
7. `src/shared/components/layout/MainLayout.tsx` — wraps sidebar + navbar

### Step 7: Create the App Route Group Layouts

1. `src/app/layout.tsx` — root layout (fonts, metadata)
2. `src/app/(app)/layout.tsx` — uses MainLayout
3. `src/app/(marketing)/layout.tsx` — uses MarketingLayout
4. `src/app/(auth)/layout.tsx` — plain (no nav)

### Step 8: Create the Dashboard

Start with the feature:
- `src/features/dashboard/components/OverviewCard.tsx`
- `src/features/dashboard/components/PostsActivity.tsx`
- `src/features/dashboard/components/ScheduledPostsList.tsx`
- `src/features/dashboard/components/UpcomingContent.tsx`

Then create the thin page: `src/app/(app)/dashboard/page.tsx` that imports and renders the dashboard.

### Step 9: Create the Create Post Feature

Sub-components first:
- `src/features/posts/components/PlatformSelector.tsx`
- `src/features/posts/components/PostContent.tsx`
- `src/features/posts/components/PostScheduler.tsx`
- `src/features/posts/components/PostPreview.tsx`

Then the page: `src/features/posts/pages/create-post.page.tsx`

Then the route: `src/app/(app)/posts/new/page.tsx` (with Suspense)

### Step 10: Create the AI Feature Pages

- `src/features/reviews/pages/review-poster.page.tsx`
- `src/features/discovery/pages/pain-point.page.tsx`

And their routes:
- `src/app/(app)/reviews/page.tsx`
- `src/app/(app)/discovery/page.tsx`

### Step 11: Create the Remaining Pages

Settings, Teams, Calendar, Analytics, Notifications — each follows the same pattern:
1. Feature component in `src/features/<name>/pages/<name>.page.tsx`
2. Thin route in `src/app/(app)/<name>/page.tsx`

### Step 12: Marketing Pages

- `src/features/marketing/pages/landing.page.tsx`
- `src/features/marketing/pages/faq.page.tsx`
- `src/features/marketing/pages/testimonials.page.tsx`

Routes in `src/app/(marketing)/`.

### Step 13: Auth Pages

`src/app/(auth)/login/page.tsx`, `register/page.tsx`, `verify-email/page.tsx` — these can live directly in `app/` (no feature folder needed if they're simple) or in `src/features/auth/`.

---


## Appendix: Key File Reference

| File | Purpose |
|---|---|
| `src/app/layout.tsx` | Root HTML shell, fonts, metadata |
| `src/app/(app)/layout.tsx` | App zone layout (delegates to MainLayout) |
| `src/app/(app)/posts/new/page.tsx` | Create Post route (Suspense boundary) |
| `src/app/(app)/reviews/page.tsx` | Review Poster route |
| `src/app/(app)/discovery/page.tsx` | Pain-Point Discovery route |
| `src/app/globals.css` | All CSS: variables, @theme, @layer, keyframes |
| `src/shared/lib/utils.ts` | `cn()` utility |
| `src/shared/providers/index.tsx` | QueryClientProvider setup |
| `src/shared/hooks/use-mobile.tsx` | `useIsMobile()` hook |
| `src/shared/components/layout/MainLayout.tsx` | Sidebar + Navbar wrapper |
| `src/shared/components/layout/sidebar.tsx` | Full sidebar with all nav groups |
| `src/shared/components/layout/navbar.tsx` | Top sticky navigation bar |
| `src/shared/components/theme/ModeToggle.tsx` | Dark/light/system theme switcher |
| `src/shared/components/ui/` | All shadcn/ui component source files |
| `src/features/posts/pages/create-post.page.tsx` | The create/schedule post form |
| `src/features/reviews/pages/review-poster.page.tsx` | AI review → social post |
| `src/features/discovery/pages/pain-point.page.tsx` | AI pain-point discovery + reply |
| `src/features/dashboard/components/` | Dashboard widget components |
| `src/features/settings/pages/settings.page.tsx` | Tabbed settings page |
| `tsconfig.json` | `@/*` alias pointing to `shared/` first, then `src/` |

## Appendix: Dependency Purpose Reference

| Package | Version | Purpose |
|---|---|---|
| `next` | 16.2.10 | Framework: routing, SSR, build |
| `react` / `react-dom` | 19.2.7 | UI rendering |
| `typescript` | 5 | Type safety |
| `tailwindcss` | 4.3.2 | Utility CSS |
| `@tailwindcss/postcss` | 4 | Tailwind v4 PostCSS plugin |
| `tailwind-merge` | 3.0.2 | Resolve conflicting Tailwind classes |
| `clsx` | 2.1.1 | Conditional class building |
| `class-variance-authority` | 0.7.1 | Type-safe component variants (cva) |
| `@radix-ui/*` | various | Accessible unstyled primitives |
| `@tanstack/react-query` | 5.101.2 | Server state, caching, mutations |
| `axios` | 1.18.1 | HTTP client for API calls |
| `sonner` | 2.0.7 | Toast notifications |
| `next-themes` | 0.4.6 | (Installed but not used; custom ModeToggle instead) |
| `lucide-react` | 1.23.0 | SVG icon library |
| `date-fns` | 4.4.0 | Date formatting (`format(date, "PPP")`) |
| `react-day-picker` | 8.10.1 | Calendar UI (used inside shadcn Calendar) |
| `recharts` | 2.15.1 | Charts (AreaChart in PostsActivity) |
| `tailwindcss-animate` | 1.0.7 | Animation utilities (`animate-spin`, `animate-in`) |

