# SocioBoom Frontend — Project Architecture, Navigation & Adding Features

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`). See also
`learning/frontend/02-nextjs-app-router.md` (the routing layer this structure sits on),
`learning/frontend/06-feature-walkthroughs.md` (the pattern applied in anger), and
`learning/backend/02-architecture-and-modules.md` (the matching module discipline on the server).

This file covers: the project architecture decisions — the thin `app/` route files delegating to
`features/<domain>/pages/` split, why `shared/` exists and what belongs there — the sidebar and
navigation system including the platform list, and a step-by-step recipe for adding a new feature
that follows the existing conventions instead of fighting them.

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


