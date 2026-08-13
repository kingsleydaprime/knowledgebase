# SocioBoom Frontend: A Complete Learning Guide

From absolute beginner to expert contributor. After reading this guide you should be able to understand every file in the codebase, extend it confidently, and replicate the entire frontend from scratch.

---

## Table of Contents

1. [Mental Model: What is the Frontend Doing?](#1-mental-model-what-is-the-frontend-doing)
2. [TypeScript Fundamentals](#2-typescript-fundamentals)
3. [React Fundamentals](#3-react-fundamentals)
4. [JSX: What You're Actually Writing](#4-jsx-what-youre-actually-writing)
5. [Next.js 16 App Router In Depth](#5-nextjs-16-app-router-in-depth)
6. [TailwindCSS v4 Concepts](#6-tailwindcss-v4-concepts)
7. [shadcn/ui: What It Is and Why We Use It](#7-shadcnui-what-it-is-and-why-we-use-it)
8. [The `@/` Path Alias and Why It Matters](#8-the--path-alias-and-why-it-matters)
9. [Project Architecture Decisions](#9-project-architecture-decisions)
10. [Tanstack Query v5 Patterns](#10-tanstack-query-v5-patterns)
11. [The Sidebar and Navigation System](#11-the-sidebar-and-navigation-system)
12. [Dark Mode with Custom Theme Toggle](#12-dark-mode-with-custom-theme-toggle)
13. [The Create-Post Page: A Full Walkthrough](#13-the-create-post-page-a-full-walkthrough)
14. [The AI Features: Review Poster and Pain-Point Discovery](#14-the-ai-features-review-poster-and-pain-point-discovery)
15. [The URL Params Pattern: How AI and Scheduler Connect](#15-the-url-params-pattern-how-ai-and-scheduler-connect)
16. [Common Pitfalls and How to Avoid Them](#16-common-pitfalls-and-how-to-avoid-them)
17. [How to Add a New Feature](#17-how-to-add-a-new-feature)
18. [Recreating the Frontend From Scratch](#18-recreating-the-frontend-from-scratch)
19. [Polling a Background Agent: Async Job UX](#19-polling-a-background-agent-async-job-ux)
20. [Send What You Collect: Payload Lessons](#20-send-what-you-collect-payload-lessons)
21. [Honest UI: Only Offer What the Backend Can Do](#21-honest-ui-only-offer-what-the-backend-can-do)

---

## 1. Mental Model: What is the Frontend Doing?

SocioBoom is a social media scheduling SaaS. The frontend is a **Next.js application** that lets users:

- Create and schedule posts to multiple social platforms at once
- View analytics, a calendar of posts, team settings
- Use AI to turn customer reviews into social posts (Review Poster)
- Use AI to find pain points on Reddit/Twitter and respond to them (Pain-Point Discovery)

Think of the frontend as three distinct zones rendered by three distinct URL groups:

| Zone | URLs | Purpose |
|---|---|---|
| Marketing | `/`, `/features`, `/pricing`, `/faq`, etc. | Public landing pages for non-logged-in visitors |
| Auth | `/login`, `/register`, `/verify-email` | Authentication flows |
| App | `/dashboard`, `/posts/new`, `/settings`, `/reviews`, `/discovery`, etc. | The actual product, for logged-in users |

Every zone has its own layout, which means different wrapping UI (the app zone has a sidebar + navbar; the marketing zone has a marketing navbar; the auth zone has no nav at all).

---

## 2. TypeScript Fundamentals

The project uses TypeScript 5 with `"strict": true`. You cannot escape TypeScript here. Here is what you need to know.

### Types and Interfaces

TypeScript lets you describe the shape of data. An interface describes an object:

```typescript
interface Review {
  reviewerName?: string;   // optional (can be undefined)
  reviewText: string;      // required
  rating?: number;
  source: "google" | "yelp" | "manual";  // union type: only these three strings
  businessName?: string;
}
```

The `?` suffix means a property can be absent. Without it the property is required and TypeScript will error if you forget it.

### Generics

Generics let you write code that works for any type while preserving type information:

```typescript
// useState<string[]> means: state is an array of strings
const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);

// useState<Date | undefined> means: state is either a Date or undefined
const [postDate, setPostDate] = useState<Date>();
```

Without the generic, TypeScript would infer the type from the initial value. `useState([])` would infer `never[]` which is almost never what you want.

### React.FC and Props

Every component accepts typed props:

```typescript
interface PlatformSelectorProps {
  selectedPlatforms: string[];
  onPlatformToggle: (platform: string) => void;  // a function that receives a string
}

const PlatformSelector = ({
  selectedPlatforms,
  onPlatformToggle,
}: PlatformSelectorProps) => {
  // ...
};
```

The `(platform: string) => void` syntax means "a function that takes one string argument and returns nothing."

### Type Assertions and Non-null

When TypeScript cannot prove something is not null, you use `!`:

```typescript
// TypeScript knows .generatedResponse might be undefined
// The ! tells TS "trust me, it exists at this point"
navigator.clipboard.writeText(painPoint.generatedResponse!);
```

Use this sparingly. It is a promise to TypeScript that you have checked the value is not null elsewhere.

### Record Type

`Record<KeyType, ValueType>` is a typed dictionary:

```typescript
const platformColors: Record<string, string> = {
  reddit: "bg-orange-500",
  twitter: "bg-sky-500",
};
```

This says: an object whose keys are strings and whose values are strings.

---

## 3. React Fundamentals

React is a library for building user interfaces. The core idea is simple: **your UI is a function of your state**.

```
UI = f(state)
```

When state changes, React re-runs the function (your component) and figures out what changed in the output, then updates only those parts of the real DOM. This is called reconciliation.

### Components

A component is a JavaScript function that returns JSX (covered in the next section). Here is the simplest possible component:

```typescript
function Hello() {
  return <h1>Hello, World</h1>;
}
```

Components can be composed — you use one component inside another:

```typescript
function App() {
  return (
    <div>
      <Hello />
      <Hello />
    </div>
  );
}
```

### State: `useState`

State is data that belongs to a component and can change over time. When it changes, React re-renders the component.

```typescript
import { useState } from "react";

function Counter() {
  const [count, setCount] = useState(0);  // initial value is 0

  return (
    <button onClick={() => setCount(count + 1)}>
      Clicked {count} times
    </button>
  );
}
```

`useState` returns a pair: the current value, and a function to update it. Always use the setter function — never mutate state directly (`count = count + 1` will not cause a re-render).

### Effects: `useEffect`

Effects let you run code in response to renders or state changes — things like fetching data, subscribing to events, or reading from localStorage.

```typescript
useEffect(() => {
  const prefill = searchParams.get("content");
  if (prefill) setPostContent(decodeURIComponent(prefill));
}, [searchParams]);  // runs when searchParams changes
```

The second argument is the **dependency array**. The effect runs:
- Once on mount if the array is `[]`
- Every render if you omit the array entirely (almost never what you want)
- Whenever any value in the array changes

### Props

Props are how components communicate. A parent passes data to a child via props:

```typescript
// Parent passes the values
<OverviewCard
  title="Total Engagement"
  value="28.4k"
  icon={<Activity className="h-4 w-4" />}
  trend={{ value: 12, positive: true }}
/>

// Child receives them as a typed object
const OverviewCard = ({ title, value, icon, trend }: OverviewCardProps) => {
  return (
    <Card>
      <CardTitle>{title}</CardTitle>
      {/* ... */}
    </Card>
  );
};
```

Props flow down. For data to go up (child to parent), you pass a function as a prop:

```typescript
// Parent defines the function and passes it down
<PlatformSelector
  selectedPlatforms={selectedPlatforms}
  onPlatformToggle={handlePlatformToggle}  // function prop
/>

// Child calls it when the user interacts
onClick={() => onPlatformToggle(platform)}
```

### Custom Hooks

A custom hook is just a function whose name starts with `use` and that calls other hooks. It is a way to extract reusable stateful logic:

```typescript
// src/shared/hooks/use-mobile.tsx
export function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(undefined);

  React.useEffect(() => {
    const mql = window.matchMedia(`(max-width: 767px)`);
    const onChange = () => setIsMobile(window.innerWidth < 768);
    mql.addEventListener("change", onChange);
    setIsMobile(window.innerWidth < 768);
    return () => mql.removeEventListener("change", onChange);
  }, []);

  return !!isMobile;
}
```

Usage anywhere in the app:

```typescript
const isMobile = useIsMobile();
if (isMobile) { /* render mobile layout */ }
```

---

## 4. JSX: What You're Actually Writing

JSX is not HTML. It is a syntax extension that compiles to `React.createElement(...)` calls. Here are the key differences to remember:

| HTML | JSX | Reason |
|---|---|---|
| `class="foo"` | `className="foo"` | `class` is a reserved JS keyword |
| `for="id"` | `htmlFor="id"` | `for` is a reserved JS keyword |
| `<br>` | `<br />` | JSX requires all tags to be self-closed |
| Inline styles as string | Inline styles as object | `style={{ color: "red" }}` |
| Event: `onclick` | Event: `onClick` | camelCase in JSX |

### Expressions in JSX

Curly braces `{}` let you embed any JavaScript expression inside JSX:

```typescript
// Displaying a value
<div>{count}</div>

// Calling a function
<div>{formatDate(postDate)}</div>

// Conditional rendering
{trend && <span>{trend.value}%</span>}

// Ternary
{isLoading ? <Spinner /> : <Content />}

// Mapping arrays to JSX
{platforms.map((platform) => (
  <div key={platform}>{platform}</div>
))}
```

The `key` prop on mapped elements is required — it tells React how to identify each element when the list changes. Use a stable unique identifier, never the array index if the list can be reordered.

### Fragments

Components must return a single root element. Wrap siblings in a Fragment when you do not want a real DOM node:

```typescript
// Long form
return (
  <React.Fragment>
    <Header />
    <Main />
  </React.Fragment>
);

// Short form (same thing)
return (
  <>
    <Header />
    <Main />
  </>
);
```

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

## 6. TailwindCSS v4 Concepts

Tailwind is a utility-first CSS framework. Instead of writing custom CSS, you compose small single-purpose classes directly in your JSX.

### The Utility-First Philosophy

Traditional CSS:

```css
.card {
  padding: 1.5rem;
  border-radius: 0.5rem;
  background-color: white;
  border: 1px solid #e2e8f0;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}
```

Tailwind equivalent:

```typescript
<div className="p-6 rounded-lg bg-white border border-slate-200 shadow-sm">
```

The classes encode the CSS properties directly. You read the JSX and immediately see the styles.

### TailwindCSS v4 Differences from v3

SocioBoom uses Tailwind v4, which has meaningful differences from v3:

**No `tailwind.config.js`**: Configuration moved entirely into the CSS file. Design tokens are defined using CSS custom properties inside `@theme {}`:

```css
/* src/app/globals.css */
@import "tailwindcss";
@plugin "tailwindcss-animate";

@theme {
  --font-family-sans: "Inter", sans-serif;
  --font-family-heading: "Poppins", sans-serif;
  --breakpoint-2xl: 1400px;
  --color-brand-purple: var(--brand-purple);
  /* All design tokens live here */
}
```

**CSS Variables for colors**: Colors are defined as HSL CSS variables in `:root` and `.dark`, then wired into Tailwind's color system via `@theme`:

```css
:root {
  --primary: 252 100% 69%;   /* HSL values without hsl() wrapper */
}

@theme {
  --color-primary: hsl(var(--primary));  /* Tailwind now generates bg-primary, text-primary, etc. */
}
```

This is why changing `--primary` in CSS immediately updates every `bg-primary`, `text-primary`, `ring-primary` utility across the app — and switching to dark mode just redefines those variables.

**`@layer` still works**: You can still define components and base styles in layers:

```css
@layer base {
  body {
    @apply bg-background text-foreground font-sans;
  }
}

@layer components {
  .card-hover {
    @apply transition-all duration-200 hover:shadow-md hover:-translate-y-1;
  }
}
```

### Common Utility Patterns Used in SocioBoom

**Layout:**
```
flex items-center justify-between  → horizontal centering with space-between
grid grid-cols-1 md:grid-cols-3   → 1 column on mobile, 3 on medium screens
gap-4                              → gap between grid/flex children
space-y-6                         → vertical spacing between children
min-h-screen                      → at least full viewport height
```

**Sizing:**
```
h-4 w-4    → 1rem × 1rem (16px)
h-8 w-8    → 2rem × 2rem (32px)
max-w-4xl  → max-width: 56rem
w-full     → width: 100%
```

**Responsive prefixes:**
```
md:p-6     → applies p-6 on medium screens (≥768px) and up
lg:col-span-2  → applies col-span-2 on large screens (≥1024px) and up
hidden md:block  → hidden on mobile, block on md+
```

**Semantic color utilities (from CSS variables):**
```
bg-background       → var(--background), changes with dark mode
text-foreground     → var(--foreground)
text-muted-foreground  → dimmed text
bg-primary          → brand purple
bg-card             → card background
border-border       → standard border color
```

**Tailwind Merge and clsx:**

When combining conditional classes, naive string concatenation fails:

```typescript
// WRONG: both classes applied even when isActive is false
className={"flex " + (isActive ? "bg-accent" : "")}
```

SocioBoom uses the `cn()` utility from `src/shared/lib/utils.ts`:

```typescript
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

`clsx` handles conditional class logic (arrays, objects, booleans). `twMerge` resolves Tailwind conflicts — if you pass `p-4` and `p-6`, twMerge keeps only `p-6` instead of generating two conflicting padding declarations.

Usage:

```typescript
className={cn(
  "flex items-center gap-3 w-full",        // always applied
  isActive === item.path && "bg-accent text-accent-foreground",  // conditional
)}
```

---

## 7. shadcn/ui: What It Is and Why We Use It

### What shadcn/ui Actually Is

shadcn/ui is **not a component library you install as a package**. It is a collection of component source code that you copy into your project. When you run `npx shadcn-ui@latest add button`, it copies `button.tsx` into your project (in SocioBoom's case, `src/shared/components/ui/`).

You own the code. You can read it, modify it, understand exactly what it does. There is no black box.

### Why Not Raw Radix UI?

Radix UI provides fully accessible, unstyled primitives — keyboard navigation, focus management, ARIA attributes all handled correctly. The trade-off is they ship with zero styles, so they are invisible by default.

shadcn/ui layers Tailwind CSS onto Radix UI primitives, giving you accessible + styled components:

```typescript
// src/shared/components/ui/tabs.tsx
import * as TabsPrimitive from "@radix-ui/react-tabs";
import { cn } from "@/lib/utils";

function TabsList({ className, ...props }: React.ComponentProps<typeof TabsPrimitive.List>) {
  return (
    <TabsPrimitive.List
      className={cn(
        "bg-muted text-muted-foreground inline-flex h-9 items-center justify-center rounded-lg p-[3px]",
        className  // caller can override or extend
      )}
      {...props}
    />
  );
}
```

The Radix primitive handles all the accessibility (keyboard navigation, ARIA roles, focus trapping). The Tailwind classes handle appearance. `cn(baseClasses, className)` allows callers to extend or override.

### The `cva` Pattern (Class Variance Authority)

Components with multiple visual variants use `cva()` to manage the class combinations cleanly:

```typescript
// src/shared/components/ui/button.tsx
const buttonVariants = cva(
  // Base classes applied to every button
  "inline-flex items-center justify-center gap-2 whitespace-nowrap rounded-md text-sm font-medium transition-all disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground shadow-xs hover:bg-primary/90",
        destructive: "bg-destructive text-white shadow-xs hover:bg-destructive/90",
        outline: "border bg-background shadow-xs hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground shadow-xs hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-9 px-4 py-2",
        sm: "h-8 rounded-md gap-1.5 px-3",
        lg: "h-10 rounded-md px-6",
        icon: "size-9",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
);
```

Usage is type-safe:

```typescript
<Button variant="outline" size="sm">Cancel</Button>
<Button variant="destructive">Delete</Button>
<Button>Submit</Button>  // uses defaultVariants: default, default
```

TypeScript will error if you pass a variant that doesn't exist.

### The `asChild` Prop

Several shadcn/ui components support `asChild`. This uses Radix's `Slot` component to forward all props and behavior to the child element instead of rendering a default element:

```typescript
// Without asChild: renders a <button> wrapping a <Link>
<Button>
  <Link href="/posts/new">Create Post</Link>
</Button>

// With asChild: the Button's styles apply to the Link directly (single element)
<Button asChild>
  <Link href="/posts/new">Create Post</Link>
</Button>
```

`asChild` is commonly used when you want a `Link` to look like a `Button`, or a `label` to work like a `Button`. SocioBoom uses it extensively in the sidebar and navbar.

### How to Add New shadcn/ui Components

```bash
cd frontend
npx shadcn-ui@latest add <component-name>
```

This copies the component source into `src/shared/components/ui/`. You then import it with `@/components/ui/<name>`.

Currently available in the project (in `src/shared/components/ui/`):
`accordion`, `alert`, `avatar`, `badge`, `button`, `calendar`, `card`, `checkbox`, `dialog`, `dropdown-menu`, `input`, `label`, `navigation-menu`, `popover`, `select`, `separator`, `sheet`, `sidebar`, `skeleton`, `sonner`, `switch`, `tabs`, `textarea`, `toast`, `tooltip`

### Real Usage Examples from the Codebase

**Card with header, content, footer:**
```typescript
<Card>
  <CardHeader>
    <CardTitle>Post Content</CardTitle>
    <CardDescription>Create and preview your post</CardDescription>
  </CardHeader>
  <CardContent>
    {/* content goes here */}
  </CardContent>
  <CardFooter>
    <Button variant="outline">Save as Draft</Button>
    <Button>Schedule Post</Button>
  </CardFooter>
</Card>
```

**Tabs:**
```typescript
<Tabs value={tabValue} onValueChange={setTabValue}>
  <TabsList className="grid w-full grid-cols-2">
    <TabsTrigger value="compose">Compose</TabsTrigger>
    <TabsTrigger value="preview">Preview</TabsTrigger>
  </TabsList>
  <TabsContent value="compose" className="pt-4">
    {/* compose panel */}
  </TabsContent>
  <TabsContent value="preview" className="pt-4">
    {/* preview panel */}
  </TabsContent>
</Tabs>
```

Note that `value` + `onValueChange` makes it a **controlled** component — the parent holds the active tab in state. You can also use `defaultValue` for an uncontrolled component where you don't need to know which tab is active from the parent.

**Badge:**
```typescript
<Badge variant="secondary">{selectedReviews.length} selected</Badge>
<Badge variant="outline">Draft</Badge>
<Badge variant="destructive">Error</Badge>
<Badge>Default (primary)</Badge>
```

**Input with icon:**
```typescript
<div className="relative">
  <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-muted-foreground" />
  <Input
    type="search"
    placeholder="Search..."
    className="pl-8"  // padding-left to make room for the icon
  />
</div>
```

**Popover (used for date picker):**
```typescript
<Popover>
  <PopoverTrigger asChild>
    <Button variant="outline" className={cn(!postDate && "text-muted-foreground")}>
      <CalendarIcon className="mr-2 h-4 w-4" />
      {postDate ? format(postDate, "PPP") : "Select date"}
    </Button>
  </PopoverTrigger>
  <PopoverContent className="w-auto p-0">
    <Calendar
      mode="single"
      selected={postDate}
      onSelect={setPostDate}
      disabled={(date) => date < new Date()}
    />
  </PopoverContent>
</Popover>
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

## 9. Project Architecture Decisions

### Feature-Based Folders vs Route-Based

SocioBoom separates UI into **two layers**:

1. `src/app/` — Next.js routing layer (thin files that define URLs)
2. `src/features/` — Feature logic layer (the actual components and pages)

This is sometimes called the "smart pages pattern" or "feature-based architecture." Why do it?

**Testability**: `features/` components are plain React components. They can be imported and tested in a unit test without any Next.js routing machinery.

**Portability**: If you decide to migrate from Next.js App Router to Pages Router, or to a completely different framework, the feature logic in `features/` does not change. Only the thin `app/` layer changes.

**Colocation**: All files for the Reviews feature live in `features/reviews/` — page, sub-components, types, hooks. You do not have to hunt across the project to find related files.

**Prevents coupling**: `app/` pages should not contain business logic. If a page grows complex, the complexity goes into `features/`, not into `app/`.

### Why Client Components for Everything

The decision to make all feature pages `"use client"` is pragmatic: every page has interactive state (form inputs, selected platforms, loading states). A mixed strategy (server for initial fetch, client for interaction) would require significantly more complexity — passing server data to client components, handling hydration carefully, etc.

For a CRUD application like SocioBoom, the performance cost of client-side rendering is minimal compared to the developer-experience cost of managing the server/client boundary on every page. When pages genuinely benefit from server rendering (for SEO), like the marketing pages, those are server components by default.

### Route Groups as Architectural Boundaries

```
(app)/    ← authenticated product
(auth)/   ← authentication flows  
(marketing)/  ← public marketing
```

These groups enforce a clean separation:
- Each has its own `layout.tsx` with completely different chrome (sidebar vs. marketing nav vs. no nav)
- Adding a new marketing page never risks accidentally inheriting the sidebar layout
- The group structure communicates intent to other developers immediately

### `shared/` Contains Truly Shared Code

The rule: if a file is only used by one feature, it lives in `features/`. If it is used by multiple features (or by the layout itself), it lives in `shared/`. This prevents circular dependencies and keeps the dependency graph clean.

---

## 10. Tanstack Query v5 Patterns

Tanstack Query (formerly React Query) manages server state — data that comes from an API. It handles caching, background refetching, loading states, and error states, removing the need to manually manage these with `useState` + `useEffect`.

### Setup

The `QueryClient` is configured in `src/shared/providers/index.tsx`:

```typescript
"use client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

const queryClient = new QueryClient();

export default function Providers({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
}
```

This wraps the application so every component can use Tanstack Query hooks.

Note: The `queryClient` is defined outside the component. This is intentional — it should not be re-created on every render. In a Next.js app with multiple users, you would create it inside the component with a `useState` to ensure each user gets their own instance, but for a client-side app this pattern is fine.

### `useQuery` for Fetching Data

```typescript
import { useQuery } from "@tanstack/react-query";
import axios from "axios";

function PostsList() {
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ["posts"],        // cache key — must be unique per query
    queryFn: async () => {
      const response = await axios.get("/api/v1/posts");
      return response.data;
    },
  });

  if (isLoading) return <Skeleton />;
  if (isError) return <div>Error: {error.message}</div>;

  return (
    <ul>
      {data.posts.map((post) => (
        <li key={post.id}>{post.title}</li>
      ))}
    </ul>
  );
}
```

The `queryKey` is how TQ identifies and caches queries. Include any dynamic values that affect the result:

```typescript
// This query re-fetches when businessName changes
const { data } = useQuery({
  queryKey: ["reviews", businessName],
  queryFn: () => fetchReviews(businessName),
  enabled: !!businessName,  // don't run if businessName is empty
});
```

### `useMutation` for Creating/Updating/Deleting

```typescript
import { useMutation, useQueryClient } from "@tanstack/react-query";
import axios from "axios";
import { toast } from "sonner";

function CreatePost() {
  const queryClient = useQueryClient();

  const { mutate, isPending } = useMutation({
    mutationFn: async (postData: CreatePostDTO) => {
      const response = await axios.post("/api/v1/posts", postData);
      return response.data;
    },
    onSuccess: () => {
      toast.success("Post scheduled!");
      // Invalidate the posts list so it re-fetches with the new post
      queryClient.invalidateQueries({ queryKey: ["posts"] });
    },
    onError: (error) => {
      toast.error("Failed to schedule post.");
    },
  });

  return (
    <Button
      disabled={isPending}
      onClick={() => mutate({ content: "Hello world", platforms: ["twitter"] })}
    >
      {isPending ? "Scheduling..." : "Schedule Post"}
    </Button>
  );
}
```

### v5 API Changes from v4

Tanstack Query v5 changed the API slightly from v4:

```typescript
// v4 (old)
const { isLoading } = useQuery(["key"], fetchFn);

// v5 (current in SocioBoom)
const { isLoading } = useQuery({
  queryKey: ["key"],
  queryFn: fetchFn,
});

// isPending replaces isLoading for mutations in v5
const { isPending } = useMutation({ mutationFn: ... });
```

### Why Not `useEffect` + `fetch`?

You could write this manually:

```typescript
const [data, setData] = useState(null);
const [isLoading, setIsLoading] = useState(true);

useEffect(() => {
  fetch("/api/posts")
    .then(r => r.json())
    .then(d => { setData(d); setIsLoading(false); });
}, []);
```

But this misses: caching (re-fetch every render), background updates, deduplication (two components fetching the same endpoint make two requests), error handling, stale-while-revalidate, and more. Tanstack Query handles all of this automatically.

---

## 11. The Sidebar and Navigation System

The sidebar is one of the most complex components in the app. Understanding it teaches several key patterns.

### Component Tree

```
(app)/layout.tsx
  └── MainLayout (client component, src/shared/components/layout/MainLayout.tsx)
        └── SidebarProvider (from shadcn/ui sidebar primitive)
              ├── Sidebar (src/shared/components/layout/sidebar.tsx)
              │     ├── SidebarHeader (logo + avatar)
              │     ├── SidebarContent
              │     │     ├── SidebarGroup "Navigation" (navItems)
              │     │     ├── SidebarGroup "AI Tools" (aiItems)
              │     │     ├── SidebarGroup "Quick Actions"
              │     │     └── SidebarGroup "Connected Platforms"
              │     └── SidebarFooter (ModeToggle + Logout)
              └── main content area
                    ├── Navbar
                    └── {children} (the active page)
```

### The Navigation Item Pattern

Navigation items are defined as arrays of objects, then `.map()`ped into JSX. This is more maintainable than writing out each item manually:

```typescript
// Define the items (data)
const navItems = [
  { title: "Dashboard", path: "/dashboard", icon: Home },
  { title: "Calendar",  path: "/calendar",  icon: Calendar },
  { title: "Analytics", path: "/analytics", icon: LineChart },
  { title: "Teams",     path: "/teams",     icon: Users },
  // ...
];

// Render them (view)
{navItems.map((item) => (
  <SidebarMenuItem key={item.title}>
    <SidebarMenuButton asChild>
      <Link
        href={item.path}
        className={cn(
          "flex items-center gap-3 w-full",
          isActive === item.path && "bg-accent text-accent-foreground",
        )}
      >
        <item.icon className="h-4 w-4" />  {/* icon is a React component */}
        <span>{item.title}</span>
      </Link>
    </SidebarMenuButton>
  </SidebarMenuItem>
))}
```

`item.icon` is a Lucide React component stored as a reference (not JSX). `<item.icon />` renders it with the specified props.

### AI Tools Group

The two AI features (Review Poster, Pain-Point Discovery) are surfaced as a distinct sidebar group:

```typescript
const aiItems = [
  { title: "Review Poster", path: "/reviews", icon: Star },
  { title: "Pain Points",   path: "/discovery", icon: Telescope },
];
```

This group signals to users that these are AI-powered features distinct from the core scheduling workflows.

### Mobile vs Desktop Behavior

`useIsMobile()` is used to conditionally render elements:

```typescript
const isMobile = useIsMobile();

// Show avatar in desktop sidebar header, not on mobile
{!isMobile && (
  <div className="px-3 pt-3">
    <Avatar>...</Avatar>
  </div>
)}

// Show ModeToggle in sidebar footer on desktop; floating button on mobile
{isMobile && (
  <div className="fixed bottom-4 right-4 z-50">
    <ModeToggle />
  </div>
)}
```

The `SidebarTrigger` button (hamburger) is shown on mobile to open/close the sidebar:

```typescript
// In Navbar.tsx — only shown on mobile
<SidebarTrigger className="md:hidden mr-2" />
```

### `SidebarMenuButton asChild` Pattern

`SidebarMenuButton` renders a `<button>` by default. `asChild` makes it render its child instead (in this case a `<Link>`), so you get sidebar button styling on a Next.js link — keyboard accessible, correct ARIA role, client-side navigation:

```typescript
<SidebarMenuButton asChild>
  <Link href="/posts/new">
    <PlusSquare className="h-4 w-4" />
    <span>Create Post</span>
  </Link>
</SidebarMenuButton>
```

---

## 12. Dark Mode with Custom Theme Toggle

SocioBoom implements dark mode without next-themes (despite it being in `package.json`). Instead it uses a custom implementation in `src/shared/components/theme/ModeToggle.tsx`.

### How It Works

The mechanism:
1. CSS variables in `globals.css` define two sets of values: `:root` (light) and `.dark` (dark)
2. Adding or removing the `dark` class on `<html>` switches between them
3. The `ModeToggle` component manages this class and persists the choice in `localStorage`

```typescript
const setMode = (newTheme: "light" | "dark" | "system") => {
  localStorage.setItem("theme", newTheme);
  setTheme(newTheme);

  if (
    newTheme === "dark" ||
    (newTheme === "system" && window.matchMedia("(prefers-color-scheme: dark)").matches)
  ) {
    document.documentElement.classList.add("dark");
  } else {
    document.documentElement.classList.remove("dark");
  }
};
```

On mount, it reads the stored preference and applies it:

```typescript
useEffect(() => {
  const storedTheme = localStorage.getItem("theme") as "light" | "dark" | "system" | null;
  const systemPrefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
  const initialTheme = storedTheme || (systemPrefersDark ? "dark" : "light");
  
  setTheme(initialTheme as "light" | "dark" | "system");
  
  if (initialTheme === "dark" || (initialTheme === "system" && systemPrefersDark)) {
    document.documentElement.classList.add("dark");
  }
}, []);
```

### The CSS Dark Mode Variant

In `globals.css`, Tailwind's dark variant is configured:

```css
@custom-variant dark (&:is(.dark *));
```

This means the `dark:` prefix in Tailwind classes activates when the element is inside a `.dark` element. Since we add/remove `dark` on `<html>`, every element on the page is affected:

```typescript
// These classes change with dark mode automatically
<div className="bg-white dark:bg-gray-900">
<p className="text-gray-900 dark:text-gray-100">

// For semantic color utilities, dark mode is already handled by CSS variables:
<div className="bg-background">  // automatically light or dark
```

### Why the ModeToggle Has Two Icons

```typescript
<Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
<Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
```

Both icons are always in the DOM. In light mode: Sun is visible (`scale-100`), Moon is hidden (`scale-0`). In dark mode: Sun shrinks and rotates away, Moon grows and rotates in. The `absolute` positioning on Moon makes them overlay each other. This is an animated icon swap — pure CSS, zero JavaScript.

---

## 13. The Create-Post Page: A Full Walkthrough

`src/features/posts/pages/create-post.page.tsx` is the most important feature page in the app. Walk through it line by line.

### File Structure

```typescript
"use client"  // Must be first: this is a client component
import React, { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardFooter, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { useToast } from "@/hooks/use-toast";
import PlatformSelector from "../components/PlatformSelector";
import PostScheduler from "../components/PostScheduler";
import PostContent from "../components/PostContent";
import PostPreview from "../components/PostPreview";
import { useRouter } from "next/navigation";
```

All shadcn/ui imports use the short `@/components/ui/...` alias. Sub-components (PlatformSelector, PostScheduler, etc.) are imported with relative paths since they are siblings in the same feature folder.

### State Declaration

```typescript
const CreatePostPage = () => {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { toast } = useToast();

  const [selectedPlatforms, setSelectedPlatforms] = useState<string[]>([]);
  const [postContent, setPostContent] = useState("");
  const [postDate, setPostDate] = useState<Date>();
  const [postTime, setPostTime] = useState<string>("12:00");
  const [tabValue, setTabValue] = useState("compose");
  const [mediaPreview, setMediaPreview] = useState<string | null>(null);
  const [postLink, setPostLink] = useState<string>("");
  const [displayLinks, setDisplayLinks] = useState<string[]>([]);
```

All form state lives at this component level and is passed down to sub-components. This is **lifting state up** — state is kept at the lowest common ancestor of all components that need it. PlatformSelector needs `selectedPlatforms`; PostPreview also needs it; therefore it must live in their shared parent (CreatePostPage).

### The URL Param Effect

```typescript
useEffect(() => {
  const prefill = searchParams.get("content");
  if (prefill) setPostContent(decodeURIComponent(prefill));
}, [searchParams]);
```

This effect runs whenever `searchParams` changes. When the user navigates to `/posts/new?content=Hello%20World`, `searchParams.get("content")` returns `"Hello World"`, which pre-fills the textarea. `decodeURIComponent` converts URL encoding (`%20` → space, `%0A` → newline).

This is the bridge between the AI features and the scheduler.

### Validation and Submission

```typescript
const handleSchedulePost = () => {
  if (selectedPlatforms.length === 0) {
    toast({
      variant: "destructive",
      title: "Error",
      description: "Please select at least one platform to post to.",
    });
    return;
  }
  // ... more validation
  toast({
    title: "Post Scheduled",
    description: `Your post has been scheduled for ${postDate?.toLocaleDateString()} at ${postTime}`,
  });
  router.push("/");
};
```

The validation pattern: check the condition, show an error toast, and `return` early. All validations run before the actual submit. After success, navigate with `router.push("/")`.

Note: This uses `useToast()` from `@/hooks/use-toast` (the older toast hook from shadcn). The newer AI feature pages use `toast` from `sonner` directly (`import { toast } from "sonner"`). Both work; the newer pages use the simpler API.

### The Two-Column Grid Layout

```typescript
<div className="grid grid-cols-1 md:grid-cols-3 gap-6">
  {/* Main card: takes 2 of 3 columns */}
  <Card className="md:col-span-2">
    {/* Post content + tabs */}
  </Card>

  {/* Sidebar card: takes 1 of 3 columns */}
  <Card>
    {/* Platform selection + scheduling */}
  </Card>
</div>
```

On mobile (1 column): both cards stack vertically. On medium+ screens (3 columns): the main card takes 2 columns and the settings card takes 1.

### Sub-Component Communication

PlatformSelector needs to both display state and update it:

```typescript
// Parent passes state + setter
<PlatformSelector
  selectedPlatforms={selectedPlatforms}
  onPlatformToggle={handlePlatformToggle}
/>

// handlePlatformToggle is defined in the parent
const handlePlatformToggle = (platform: string) => {
  if (selectedPlatforms.includes(platform)) {
    setSelectedPlatforms(selectedPlatforms.filter((p) => p !== platform));
  } else {
    setSelectedPlatforms([...selectedPlatforms, platform]);
  }
};
```

The `filter` removes a platform; `[...selectedPlatforms, platform]` adds one. Never mutate the array directly — always create a new array.

---

## 14. The AI Features: Review Poster and Pain-Point Discovery

Both AI features follow the same architectural pattern. Understanding one means understanding both.

### Review Poster Architecture (`src/features/reviews/pages/review-poster.page.tsx`)

The page is divided into three sequential steps, each gated on the previous:

```
Step 1: Fetch Reviews (always visible)
  ├── Search by business name (Google, Yelp, Twitter, Reddit buttons)
  └── Or paste manually

Step 2: Select Reviews (visible only when fetchedReviews.length > 0)
  └── ReviewCard for each fetched review (click to select)

Step 3: Generate Posts (visible only when selectedReviews.length > 0)
  ├── Tone selector (Tabs: professional / casual / excited)
  └── Generate button

Right Column: Generated Posts (empty state or GeneratedPostCard list)
```

This progressive disclosure pattern guides users through the workflow without overwhelming them.

### Axios for API Calls

```typescript
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001/api/v1";

const fetchGoogle = async () => {
  if (!businessName.trim()) return;  // guard: do nothing if no input
  setFetching(true);
  try {
    const { data } = await axios.post(`${API}/reviews/fetch-google`, { businessName });
    setFetchedReviews(data.reviews ?? []);  // ?? [] means "use [] if null/undefined"
    if (!data.reviews?.length) toast.info("No Google reviews found.");
  } catch {
    toast.error("Failed to fetch Google reviews.");
  } finally {
    setFetching(false);  // always runs, even if try threw
  }
};
```

`axios.post(url, body)` makes a POST request. The response body is automatically parsed as JSON and available as `data`. The `finally` block ensures `setFetching(false)` always runs — even if the request threw an error — so the loading spinner never gets stuck.

### Sonner Toast API

Review Poster and Pain-Point Discovery use `sonner` (not the older shadcn toast):

```typescript
import { toast } from "sonner";

toast.success("Copied to clipboard");
toast.error("AI generation failed. Check your API key.");
toast.info("No Google reviews found for that business name.");
toast.warning("Something might be wrong");
toast("Plain message with no icon");
```

Sonner toasts appear in the bottom-right of the screen. They auto-dismiss after ~4 seconds. Unlike the older shadcn `useToast()`, you just call `toast.*()` directly — no hook needed.

For sonner to work, you need the `<Toaster>` component mounted once. It is typically placed in the root layout. If you see toasts not appearing, check that `<Toaster />` is in the component tree.

### The `loading/disabled` Pattern

Buttons that trigger async operations follow a consistent pattern:

```typescript
<Button onClick={generate} disabled={generating} className="w-full">
  {generating ? (
    <><Loader2 className="h-4 w-4 animate-spin mr-2" /> Generating...</>
  ) : (
    "Generate Social Posts"
  )}
</Button>
```

- `disabled={generating}` prevents double-clicks while the request is in flight
- `Loader2` with `animate-spin` is the Lucide spinner icon
- The button text changes to provide feedback

### Pain-Point Discovery Architecture (`src/features/discovery/pages/pain-point.page.tsx`)

The same progressive pattern, but simpler:

```
Describe your app (Textarea)
Select platforms (Reddit / Twitter toggle buttons)
Search button → calls /api/v1/discovery/search
  → returns painPoints[]

For each pain point:
  PainPointCard
    ├── Shows platform badge, author, post content
    └── "Generate Reply" button → calls /api/v1/discovery/generate-response
          → fills in generatedResponse on the pain point
          └── Shows "Copy" + "Schedule" buttons
```

The `updateResponse` pattern is worth studying:

```typescript
const updateResponse = (id: number, response: string) => {
  setPainPoints((prev) => prev.map((p) => (p.id === id ? { ...p, generatedResponse: response } : p)));
};
```

This immutably updates one item in an array. `prev.map(...)` creates a new array. For the matching item, `{ ...p, generatedResponse: response }` creates a new object with all the same properties but with `generatedResponse` updated. For non-matching items, it returns them unchanged. This is the standard pattern for updating an item in a state array.

---

## 15. The URL Params Pattern: How AI and Scheduler Connect

The most elegant design decision in the codebase: the AI features communicate with the post scheduler through URL parameters instead of shared state or an event bus.

### The Problem

The Review Poster and Pain-Point Discovery features generate text content. That content needs to get into the Create Post form so the user can schedule it. How?

Options:
1. **Global state (Redux/Zustand/Context)**: Complex. Requires setting up a store, connecting both pages, cleaning up when done.
2. **Clipboard + manual paste**: Requires user action. Error-prone.
3. **URL params**: Simple. Works across page navigations. No state management overhead.

### How It Works

In the AI feature (sender):

```typescript
// In GeneratedPostCard (inside review-poster.page.tsx)
const copyAndSchedule = () => {
  router.push(`/posts/new?content=${encodeURIComponent(post.content)}`);
};

// In PainPointCard (inside pain-point.page.tsx)
const scheduleResponse = () => {
  if (!painPoint.generatedResponse) return;
  router.push(`/posts/new?content=${encodeURIComponent(painPoint.generatedResponse)}`);
};
```

`encodeURIComponent` converts the text to URL-safe encoding:
- Spaces → `%20`
- Newlines → `%0A`
- Colons → `%3A`
- etc.

In the scheduler (receiver):

```typescript
// In create-post.page.tsx
useEffect(() => {
  const prefill = searchParams.get("content");
  if (prefill) setPostContent(decodeURIComponent(prefill));
}, [searchParams]);
```

`decodeURIComponent` reverses the encoding, restoring the original text.

### Why This Works Well

- **No coupling**: The AI features do not import anything from the scheduler. The scheduler does not import anything from the AI features.
- **Bookmarkable**: Users could bookmark `/posts/new?content=Hello` and return to a pre-filled form.
- **Shareable**: A teammate could send a link with pre-filled content.
- **No cleanup needed**: When the user edits the content and schedules the post, the URL param is irrelevant. When they navigate away, the state is garbage collected naturally.
- **Works with Next.js navigation**: `router.push()` updates the URL client-side without a full page reload.

### The Suspense Requirement

This is why `useSearchParams()` requires Suspense. The Next.js page at `app/(app)/posts/new/page.tsx`:

```typescript
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

During SSR (server-side rendering), the server does not know the URL params the client will have. Next.js throws if `useSearchParams()` is called in a component not wrapped in `<Suspense>`. The Suspense boundary tells Next.js: "Render the fallback skeleton on the server. When the client hydrates and knows the actual URL, render the real component."

---

## 16. Common Pitfalls and How to Avoid Them

### 1. Forgetting `"use client"` on Components that Use Hooks

**Symptom**: Error like `useState can only be used in a Client Component`

**Cause**: You created a component with `useState`, `useEffect`, or event handlers but forgot `"use client"` at the top.

**Fix**: Every component that uses React hooks or browser APIs needs `"use client"` as its very first line (before any imports).

### 2. Calling `useSearchParams()` Without Suspense

**Symptom**: Build error: `useSearchParams() should be wrapped in a suspense boundary`

**Fix**: In the `app/(app)/.../page.tsx`, wrap the feature component in `<Suspense>`:

```typescript
import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import MyFeaturePage from "@/features/my-feature/pages/my-feature.page";

export default function Page() {
  return (
    <Suspense fallback={<Skeleton className="h-96 w-full" />}>
      <MyFeaturePage />
    </Suspense>
  );
}
```

### 3. Mutating State Directly

**Symptom**: UI does not update after you change state; or updates are inconsistent.

**Cause**: Direct mutation does not trigger re-renders.

```typescript
// WRONG
selectedPlatforms.push("instagram");  // mutates array, no re-render

// RIGHT
setSelectedPlatforms([...selectedPlatforms, "instagram"]);  // new array, triggers re-render
```

Same for objects:

```typescript
// WRONG
user.name = "Alice";  // mutates object
setUser(user);  // React thinks nothing changed (same reference)

// RIGHT
setUser({ ...user, name: "Alice" });  // new object reference
```

### 4. Missing `key` on Mapped Elements

**Symptom**: React console warning `Each child in a list should have a unique "key" prop`; potentially incorrect updates when list items move.

**Fix**: Add `key` with a stable unique value. Prefer IDs over array indices.

```typescript
// WRONG
{posts.map((post) => <PostCard post={post} />)}

// WRONG (index as key — breaks when list is reordered/filtered)
{posts.map((post, i) => <PostCard key={i} post={post} />)}

// RIGHT
{posts.map((post) => <PostCard key={post.id} post={post} />)}
```

### 5. Stale Closures in `useEffect`

**Symptom**: An effect uses a state variable but always sees the initial value.

**Cause**: The effect closure captured the variable at the time the effect was created, not the current value. This happens when a variable is missing from the dependency array.

```typescript
// WRONG: count will always be 0 inside the effect
useEffect(() => {
  const id = setInterval(() => console.log(count), 1000);
  return () => clearInterval(id);
}, []);  // empty deps: count not tracked

// RIGHT
useEffect(() => {
  const id = setInterval(() => console.log(count), 1000);
  return () => clearInterval(id);
}, [count]);  // effect re-runs when count changes
```

### 6. Using `<a>` Instead of `<Link>` for Internal Navigation

**Symptom**: Page fully reloads on navigation instead of client-side transition; no prefetching; layout re-mounts.

**Fix**: Always use `<Link href="...">` from `next/link` for internal routes. Only use `<a>` for external URLs.

### 7. TailwindCSS v4 Config Gotchas

**Symptom**: Custom colors or utilities not generated; `@apply` not working.

The v4 config is in `globals.css`, not `tailwind.config.js`. Custom tokens must be in `@theme {}`. The import order matters:

```css
/* MUST be first */
@import "tailwindcss";

/* Plugins after */
@plugin "tailwindcss-animate";

/* Then your custom variant */
@custom-variant dark (&:is(.dark *));

/* Then :root variables */
:root { ... }

/* Then @theme — wires CSS vars into Tailwind utilities */
@theme { ... }

/* Then @layer base/components/utilities */
@layer base { ... }
```

### 8. Incorrect `@/` Alias Usage

**Symptom**: TypeScript can find the file but you're confused about which path is correct.

Remember: `@/` resolves to `src/shared/` first, then `src/`. So:
- `@/components/ui/button` → `src/shared/components/ui/button` ✓
- `@/features/posts/...` → `src/features/posts/...` ✓ (shared/ has no `features/` folder)
- `@/shared/components/ui/button` → `src/shared/components/ui/button` ✓ (via `src/*`)

Do not create a `src/shared/features/` folder — it would shadow `src/features/` for `@/features/...` imports.

### 9. `process.env.NEXT_PUBLIC_*` at Build Time

**Symptom**: API URL is `undefined` in production.

Next.js only embeds environment variables that start with `NEXT_PUBLIC_` in client-side code. Variables without that prefix are server-only. The API URL pattern in the feature pages:

```typescript
const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001/api/v1";
```

In production, set `NEXT_PUBLIC_API_URL` in your hosting environment. The `??` fallback ensures local development works without a `.env` file.

### 10. `asChild` Without a Single Child

**Symptom**: Runtime error or no rendering.

`asChild` requires exactly one child element. Multiple children will throw.

```typescript
// WRONG
<Button asChild>
  <span>one</span>
  <span>two</span>
</Button>

// RIGHT
<Button asChild>
  <Link href="/somewhere">Text</Link>
</Button>
```

---

## 17. How to Add a New Feature

Use this checklist when adding a feature like a new AI tool or a new settings panel.

### Step 1: Create the Feature Folder

```bash
mkdir -p src/features/my-feature/pages
mkdir -p src/features/my-feature/components  # if needed
```

### Step 2: Create the Page Component

`src/features/my-feature/pages/my-feature.page.tsx`:

```typescript
"use client";
import React, { useState } from "react";
import { useRouter } from "next/navigation";
import axios from "axios";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { toast } from "sonner";
import { Loader2 } from "lucide-react";

const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:3001/api/v1";

export default function MyFeaturePage() {
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleAction = async () => {
    setLoading(true);
    try {
      const { data } = await axios.post(`${API}/my-feature/action`, { payload: "value" });
      toast.success("Action completed!");
    } catch {
      toast.error("Action failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="animate-in space-y-6 max-w-4xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">My Feature</h1>
        <p className="text-muted-foreground mt-1">Description of what this does.</p>
      </div>

      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base">Do The Thing</CardTitle>
          <CardDescription>Explain what happens.</CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={handleAction} disabled={loading}>
            {loading ? <><Loader2 className="h-4 w-4 animate-spin mr-2" />Working...</> : "Go"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
```

### Step 3: Create the App Route

`src/app/(app)/my-feature/page.tsx`:

```typescript
import { Suspense } from "react";
import { Skeleton } from "@/components/ui/skeleton";
import MyFeaturePage from "@/features/my-feature/pages/my-feature.page";

export default function Page() {
  return (
    <Suspense fallback={<Skeleton className="h-96 w-full rounded-lg" />}>
      <MyFeaturePage />
    </Suspense>
  );
}
```

Always include `<Suspense>` even if you don't use `useSearchParams` today — it's cheap insurance and follows the established pattern.

### Step 4: Add to the Sidebar

In `src/shared/components/layout/sidebar.tsx`, add to the appropriate group:

```typescript
import { Star, Telescope, Wrench } from "lucide-react";

const aiItems = [
  { title: "Review Poster",    path: "/reviews",    icon: Star },
  { title: "Pain Points",      path: "/discovery",  icon: Telescope },
  { title: "My Feature",       path: "/my-feature", icon: Wrench },  // add here
];
```

### Step 5: Link to the Scheduler (if applicable)

If your feature generates content that should be scheduled, use the URL params pattern:

```typescript
import { useRouter } from "next/navigation";

const router = useRouter();

const scheduleContent = (content: string) => {
  router.push(`/posts/new?content=${encodeURIComponent(content)}`);
};
```

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

## 19. Polling a Background Agent: Async Job UX

When Pain-Point Discovery became a background agent (1–3 minute runs), the frontend contract changed completely. The old flow was one awaited request:

```ts
const { data } = await axios.post(`${API}/discovery/search`, {...});
setPainPoints(data.painPoints);   // everything arrives at once, or times out
```

The new flow is **kickoff + poll**:

```ts
// 1. Kickoff — returns immediately with 202 and a session in status "running"
const { data } = await axios.post(`${API}/discovery/search`, { appDescription, platforms, searchProvider });
const sessionId: number = data.session.id;

// 2. Poll — results GROW while the agent works, because it saves incrementally
for (let i = 0; i < MAX_POLLS && activeSearch.current === searchToken; i++) {
  await new Promise((r) => setTimeout(r, POLL_INTERVAL_MS));
  const { data: snap } = await axios.get(`${API}/discovery/${sessionId}`);
  setPainPoints(snap.painPoints ?? []);           // streaming feel, no WebSockets
  if (snap.session.status !== "running") {        // completed | failed
    setAgentSummary(snap.session.summary ?? null);
    break;
  }
}
```

### The cancellation token pattern

The subtle bug in any polling loop: the user starts a search, gets bored, starts *another* search — now two loops are alive, and the old one keeps overwriting state with stale results. Or the user navigates away and the loop calls `setState` on an unmounted component.

The fix is a **ref token**:

```ts
const activeSearch = React.useRef(0);

// on unmount, invalidate whatever loop is running
useEffect(() => () => { activeSearch.current = -1; }, []);

const search = async () => {
  const searchToken = Date.now();
  activeSearch.current = searchToken;      // claiming the "current search" slot
  ...
  // inside the loop AND after it:
  if (activeSearch.current !== searchToken) return;   // someone superseded us — stop silently
  ...
  finally {
    if (activeSearch.current === searchToken) setSearching(false);
  }
};
```

Why a **ref** and not state? Because the check happens *inside an async closure*. State captured in a closure is frozen at the moment the closure was created; a ref is a live pointer — reading `.current` always gives the latest value. This is the canonical fix for "stale closure" bugs in async React code.

### Status-driven UX decisions

- Poll interval **4 s**: fast enough to feel live, slow enough that a 3-minute run costs ~45 requests against the backend's 200-per-15-min rate limit. Polling frequency is a rate-limit budget decision, not a taste decision.
- One **combined endpoint** (`{ session, painPoints }`) instead of two — halves request volume.
- Cap the loop (`MAX_POLLS`) and handle the timeout case explicitly ("still working — check Saved Sessions") instead of spinning forever.
- Distinguish all three endings with different toasts: `failed` (check API keys), `completed` with results, `completed` empty (refine the description). Every terminal state the backend can produce needs a UI sentence.
- Show partial results *while* `searching` — the render gate changed from `searched && painPoints.length > 0` to `(searching || searched) && painPoints.length > 0`. The whole point of incremental saves is lost if the UI hides them until the end.

---

## 20. Send What You Collect: Payload Lessons

A bug worth studying because it produced **zero errors**: the AI panel generated per-platform post variants and stored them in state —

```ts
const [platformContent, setPlatformContent] = useState<Record<string, string>>({});
// filled by AIGeneratePanel's onGenerate callback, shown in PostPreview…
```

— and then the schedule request sent only `content: postContent`. The variants were collected, previewed… and thrown away. Every platform received the same text, silently contradicting the product's whole pitch ("never the same post twice"). No console error, no failed request. The only way to catch this class of bug is to **read the request payload and ask: is everything the user built actually in here?**

The fix, and the pattern for conditional payloads:

```ts
// Only send variants for platforms actually selected, and only non-empty ones
const buildContentByPlatform = () => {
  const map: Record<string, string> = {};
  for (const p of selectedPlatforms) {
    if (platformContent[p]?.trim()) map[p] = platformContent[p];
  }
  return Object.keys(map).length ? map : undefined;   // undefined = key omitted from JSON
};

const body = {
  content: postContent,                      // fallback for platforms without a variant
  contentByPlatform: buildContentByPlatform(),
  subreddit: subreddit.trim() || undefined,  // "" would fail backend validation; undefined won't
  ...
};
```

Two idioms to keep:
- **`undefined` means "omit"** — `JSON.stringify` drops `undefined` values, so optional fields stay clean instead of arriving as `""` or `{}` and confusing backend validation.
- **Round-trip symmetry**: whatever you send on create, you must restore on edit. The edit loader gained `setPlatformContent(post.contentByPlatform ?? {})` and `setSubreddit(post.subreddit ?? "")` — forgetting this half means editing a post silently discards its variants.

---

## 21. Honest UI: Only Offer What the Backend Can Do

The platform selector offered **Instagram**. The publish worker supported twitter, linkedin, reddit, facebook — Instagram fell through to `default: throw 'Publishing not yet supported'`. So a user could select Instagram, write a post, schedule it, and get a silent failure days later. Meanwhile **Reddit**, which the worker fully supported, wasn't offered at all.

The frontend's option lists are a *promise about backend capability*. When they drift, users experience it as your product lying to them. The fix was mechanical — swap Instagram for Reddit in `PlatformSelector`, `AIGeneratePanel`'s meta map, and the connections card — but the lesson is the audit: for every option you render, find the backend `switch` that handles it.

The Reddit swap also demonstrates **conditional required fields** done properly, on both sides:

```tsx
{selectedPlatforms.includes("reddit") && (
  <div className="space-y-2">
    <Label htmlFor="subreddit">Subreddit</Label>
    <Input
      id="subreddit"
      placeholder="e.g. smallbusiness"
      value={subreddit}
      onChange={(e) => setSubreddit(e.target.value.replace(/^r\//, ""))}  // normalize "r/foo" → "foo"
    />
    <p className="text-xs text-muted-foreground">
      The community your Reddit post will be submitted to. The first line of your post becomes the title.
    </p>
  </div>
)}
```

- The field **appears only when relevant** (Reddit selected) instead of sitting permanently in the form as noise.
- Input is **normalized at the edge** — users will type `r/smallbusiness`; strip the prefix rather than erroring on it.
- Client validates before submit (instant toast) **and** the backend validates again (`400` if reddit ∈ platforms and no subreddit) — client validation is UX, server validation is the actual guarantee. Never rely on the first for the second.
- The helper text explains a non-obvious backend behavior (first line becomes the Reddit title) *at the moment it's relevant*, not in documentation nobody reads.

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
