# SocioBoom Frontend — Next.js 16 App Router & Path Aliases

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`). See also
`learning/frontend/01-foundations.md` (React basics this assumes),
`learning/frontend/04-architecture.md` (how routes map onto the `features/` folder structure), and
`learning/frontend/05-data-fetching.md` (fetching inside client components).

This file covers: the Next.js 16 App Router in depth — the file-system routing conventions, route
groups like `(app)` / `(auth)` / `(marketing)` and why SocioBoom uses them, layouts and nesting,
server vs client components and the `"use client"` boundary, dynamic route segments such as
`platform/[platform]`, `useParams` and `useSearchParams`, plus the `@/` path alias, how it is
configured, and why it matters.

---

## 5. Next.js 16 App Router In Depth

Next.js builds on React and adds routing, server-side rendering, API routes, and more. SocioBoom uses the **App Router** introduced in Next.js 13 and matured in 15/16.

### File-Based Routing

Every file named `page.tsx` inside `src/app/` becomes a route. The folder structure defines the URL:

```
src/app/
  (app)/
    dashboard/
      page.tsx     →  /dashboard
    posts/
      new/
        page.tsx   →  /posts/new
    reviews/
      page.tsx     →  /reviews
  (auth)/
    login/
      page.tsx     →  /login
  (marketing)/
    page.tsx       →  /  (root)
    features/
      page.tsx     →  /features
```

The folders in parentheses — `(app)`, `(auth)`, `(marketing)` — are **Route Groups**. The parentheses mean they do NOT appear in the URL. They only exist to group routes that share a common layout without polluting the URL.

### Layouts

A `layout.tsx` file wraps all routes in its folder and sub-folders. Layouts are **persistent** — they do not unmount when you navigate between routes in the same group. This is why the sidebar never flashes or re-renders when you click between pages.

```
src/app/
  layout.tsx           ← Root layout: wraps everything (html, body, fonts)
  (app)/
    layout.tsx         ← App layout: wraps with Sidebar + Navbar
  (marketing)/
    layout.tsx         ← Marketing layout: wraps with MarketingNavbar
```

The root layout (`src/app/layout.tsx`):

```typescript
// This file is a SERVER COMPONENT by default (no "use client" directive)
import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "SocioBoom",
  description: "SocioBoom is a scheduling tool for social media posts.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className={`${geistSans.variable} ${geistMono.variable} antialiased`}>
        {children}
      </body>
    </html>
  );
}
```

The App zone layout (`src/app/(app)/layout.tsx`) is three lines:

```typescript
import MainLayout from "@/components/layout/MainLayout";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return <MainLayout>{children}</MainLayout>;
}
```

`MainLayout` lives in `src/shared/components/layout/MainLayout.tsx`. Because it uses `useIsMobile()` (a hook), it must be a client component. But the layout file itself can be a server component — it just delegates to a client component.

### Server Components vs Client Components

This is the most important concept in the App Router.

**Server Components** (default):
- Run only on the server
- Cannot use `useState`, `useEffect`, event handlers, or browser APIs
- Can be async (can `await` database calls directly)
- Send only rendered HTML to the browser — no JS bundle
- Good for: layouts, static content, data fetching

**Client Components** (`"use client"` at the top of the file):
- Run in the browser (and also on the server for the initial HTML)
- Can use all React hooks
- Can handle user interactions
- Are included in the JS bundle sent to the browser

```typescript
// Server component: no directive needed, can be async
export default async function Page() {
  const data = await fetch("...");  // direct server-side fetch
  return <div>{data.title}</div>;
}

// Client component: needs directive
"use client";
import { useState } from "react";

export default function Page() {
  const [count, setCount] = useState(0);  // hooks are fine here
  return <button onClick={() => setCount(count + 1)}>{count}</button>;
}
```

### Why SocioBoom's Feature Pages are All Client Components

Every feature page in SocioBoom is marked `"use client"` and imported from `features/`. The reason: they all use state (form values, loading states, selected options) and call browser APIs. The Next.js `page.tsx` files in `app/` are intentionally thin — they just import and re-export the feature page component, sometimes wrapping it in Suspense:

```typescript
// src/app/(app)/posts/new/page.tsx
import { Suspense } from "react";
import CreatePostPage from "@/features/posts/pages/create-post.page";
import { Skeleton } from "@/components/ui/skeleton";

export default function CreatePost() {
  return (
    <Suspense fallback={<Skeleton className="h-96 w-full rounded-lg" />}>
      <CreatePostPage />
    </Suspense>
  );
}
```

This pattern keeps feature logic in `features/` (importable from anywhere, testable in isolation) while Next.js routing lives in `app/`.

### Suspense and Streaming

`<Suspense>` is a React concept for handling asynchronous rendering. You wrap a component that might "suspend" (pause rendering while waiting for something) in a `<Suspense>` boundary, and provide a `fallback` to show while it waits.

In SocioBoom, `Suspense` is required wherever `useSearchParams()` is called. This is because `useSearchParams()` reads the URL at render time, which can vary between server and client. Next.js requires any component that uses `useSearchParams` to be wrapped in `<Suspense>` so the server can render the fallback until the client hydrates and the URL is known.

If you forget the Suspense boundary, Next.js will throw this error at build time:

```
Error: useSearchParams() should be wrapped in a suspense boundary
```

The fix, always:

```typescript
// In the page.tsx (which can be a server component)
import { Suspense } from "react";
import MyClientPage from "@/features/.../my-page";

export default function Page() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <MyClientPage />  {/* This uses useSearchParams internally */}
    </Suspense>
  );
}
```

### Dynamic Routes

The `[platform]` folder creates a dynamic segment:

```
src/app/(app)/platform/[platform]/page.tsx → /platform/instagram, /platform/twitter, etc.
```

In the page component, you access the segment through `params`:

```typescript
// Server component approach
export default function PlatformPage({ params }: { params: { platform: string } }) {
  return <div>Viewing: {params.platform}</div>;
}
```

### next/navigation

The App Router provides client-side navigation through `next/navigation`:

```typescript
import { useRouter, useSearchParams, usePathname } from "next/navigation";

// useRouter — for programmatic navigation
const router = useRouter();
router.push("/dashboard");   // navigate
router.back();               // go back
router.replace("/login");    // navigate without adding to history

// useSearchParams — read URL query params (?key=value)
const searchParams = useSearchParams();
const content = searchParams.get("content");  // null if not present

// usePathname — current URL path
const pathname = usePathname();  // e.g. "/dashboard"
```

### next/link

For links in JSX, use `<Link>` from Next.js instead of `<a>`. It handles client-side navigation automatically:

```typescript
import Link from "next/link";

<Link href="/dashboard">Go to Dashboard</Link>
```

Next.js prefetches the destination when the link enters the viewport, making navigation feel instant.

### Metadata

Page metadata (title, description, Open Graph) is exported from layout or page files as a named export. Since metadata runs on the server, it cannot use client-side hooks:

```typescript
export const metadata: Metadata = {
  title: "SocioBoom",
  description: "SocioBoom is a scheduling tool for social media posts.",
  authors: [{ name: "Spectroniq", url: "https://www.spectroniq.com" }],
};
```

---


## 8. The `@/` Path Alias and Why It Matters

### The Problem Without Aliases

Without path aliases, imports look like this:

```typescript
import { Button } from "../../../../shared/components/ui/button";
import { cn } from "../../../shared/lib/utils";
```

This is fragile — moving a file breaks all its relative imports — and unreadable.

### How `@/` Works in SocioBoom

The `tsconfig.json` defines:

```json
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/shared/*", "./src/*"]
    }
  }
}
```

The key detail: **two paths in the array**. TypeScript/Next.js resolves them in order:
1. First tries `./src/shared/*`
2. If not found, tries `./src/*`

This means:

| Import | Resolves to |
|---|---|
| `@/components/ui/button` | `src/shared/components/ui/button.tsx` |
| `@/lib/utils` | `src/shared/lib/utils.ts` |
| `@/hooks/use-mobile` | `src/shared/hooks/use-mobile.tsx` |
| `@/features/posts/pages/create-post.page` | `src/features/posts/pages/create-post.page.tsx` |
| `@/shared/components/ui/button` | `src/shared/components/ui/button.tsx` (via src/*) |

### Why Some Files Use `@/components/ui/` and Others Use `@/shared/components/ui/`

You will notice inconsistency in the codebase. Some files (like `create-post.page.tsx`) import from `@/components/ui/button` (the short form), while others (like `review-poster.page.tsx`) import from `@/shared/components/ui/button` (the explicit form). Both resolve to the same file because of the dual-path alias.

The short form `@/components/ui/...` is preferred for conciseness. The explicit `@/shared/components/ui/...` form is used in files inside the `shared/` directory itself (to avoid confusion about whether `@/` refers to `shared/` or the root).

### The Resolution Logic

```
@/components/ui/button
  → try src/shared/components/ui/button  ✓ FOUND → use this
  (never checks src/components/ui/button)

@/features/posts/pages/create-post.page
  → try src/shared/features/posts/...    ✗ not found
  → try src/features/posts/...           ✓ FOUND → use this
```

---


