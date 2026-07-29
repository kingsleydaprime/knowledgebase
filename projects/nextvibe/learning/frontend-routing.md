# NextVibe Frontend — Routing, App Router & Rendering Model

Split out from the original flat `frontend-learning.md` (kept untouched in the project root).
See also `learning/frontend-state-management.md`, `learning/frontend-auth.md`,
`learning/frontend-realtime.md`, `learning/frontend-forms-ui.md`,
`learning/frontend-uploads-errors.md`, `learning/frontend-payments-games.md`, and
`learning/frontend-performance-debugging.md` for the rest of the frontend material, and the
`learning/backend-*.md` / `learning/sys-design.md` / `learning/devops.md` files for the backend
and infrastructure side.

This file covers: what the project is and its tech stack, the Next.js App Router and why it
matters, file-based routing, route groups, dynamic routes, layouts and nesting, Server vs Client
Components, API route handlers, path aliases and project structure, Next.js concepts not used in
this project (parallel routes, intercepting routes, SSG/ISR, Server Actions), the real
`src/proxy.ts` middleware implementation, the `useSearchParams()` Suspense requirement, the
complete Next.js routing syntax reference, and a deep dive on `<Suspense>` itself.

---

## 1. What This Project Is

NextVibe is a social event platform. Users can discover events, RSVP, chat, buy tickets, and play games during events. Organizers can create and publish events, run gamification sessions, and track payments.

**Tech stack:**
- **Framework**: Next.js 16 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS v4 + shadcn/ui
- **State**: Redux Toolkit + RTK Query
- **Real-time**: Socket.IO client
- **Auth**: JWT in cookies, manual refresh token queue
- **Payments**: Ercaspay (redirect-based checkout)
- **Forms**: react-hook-form + zod

---

## 2. The App Router — Next.js 13+

Next.js has two routing systems. This project uses the **App Router** (introduced in Next.js 13), which lives inside `src/app/`. The older Pages Router (`pages/`) is not used.

### Why the App Router matters

The App Router is built around React Server Components. Every file in `src/app/` is a **Server Component by default** — meaning it renders on the server, sends HTML to the browser, and ships zero JavaScript unless you explicitly opt into the client.

```
src/app/
├── layout.tsx        ← Root layout (always rendered)
├── page.tsx          ← Home page "/"
├── dashboard/
│   └── page.tsx      ← "/dashboard"
└── (auth)/
    └── auth/
        └── login/
            └── page.tsx  ← "/auth/login"
```

The key files Next.js recognises inside a route folder:

| File | Purpose |
|---|---|
| `page.tsx` | The UI for that URL. Makes the route publicly accessible. |
| `layout.tsx` | Wraps children. Persists across navigations within its subtree. |
| `loading.tsx` | Automatic Suspense boundary. Shown while `page.tsx` is streaming. |
| `error.tsx` | Error boundary. Shown when the route throws. |
| `not-found.tsx` | Rendered when `notFound()` is called or no route matches. |
| `route.ts` | API endpoint (no UI). Handles HTTP requests. |

---

## 3. File-Based Routing

You don't configure routes anywhere. The folder structure **is** the route.

```
src/app/dashboard/events/[id]/page.tsx
                              ↑
               This renders at /dashboard/events/abc123
```

### Reading route params in a page

```tsx
// src/app/dashboard/events/[id]/page.tsx
export default function EventPage({ params }: { params: { id: string } }) {
  return <div>Event {params.id}</div>;
}
```

### Reading query params

```tsx
// /dashboard/events?tab=chat
export default function EventPage({ searchParams }: { searchParams: { tab?: string } }) {
  const tab = searchParams.tab ?? "overview";
}
```

> **In Client Components**, use `useSearchParams()` from `next/navigation` instead.
> `searchParams` as a prop only works in Server Components.

---

## 4. Route Groups

Folders wrapped in `(parentheses)` are **route groups**. They let you organise files and share layouts **without affecting the URL**.

```
src/app/
├── (auth)/            ← "(auth)" is invisible in the URL
│   ├── layout.tsx     ← Auth-specific layout (centered card, no navbar)
│   └── auth/
│       ├── login/page.tsx    → /auth/login
│       └── register/page.tsx → /auth/register
├── (admin)/           ← Admin section with its own layout
│   └── admin/
│       └── ...
└── dashboard/
    └── (dashboard-route)/   ← Dashboard routes with navbar + bottom nav
        ├── layout.tsx
        ├── events/page.tsx  → /dashboard/events
        └── messages/page.tsx → /dashboard/messages
```

In this project there are three route groups:
- `(auth)` — login, register, forgot-password, verify-email. Has a centred auth layout.
- `(admin)` — admin panel. Has an admin-specific layout.
- `(dashboard-route)` — the main app after login. Has `DashboardNavbar` + `BottomNav`.

**Rule of thumb**: use a route group any time a set of pages needs a shared layout that others don't.

---

## 5. Dynamic Routes

Square brackets create segments that match any value.

```
[id]          → matches /events/abc, /events/123, /events/anything
[...slug]     → catches all remaining segments: /docs/a/b/c → slug = ["a","b","c"]
[[...slug]]   → optional catch-all: matches / as well
```

In this project:
- `/dashboard/[eventId]/` — organiser event management page
- `/dashboard/events/[id]/` — attendee event detail page
- `/game/[token]/` — game session page
- `/admin/users/[id]/` — admin user detail

### Generating static paths at build time (not used here, but important)

```tsx
// For a page like /blog/[slug]
export async function generateStaticParams() {
  const posts = await fetchAllPosts();
  return posts.map((post) => ({ slug: post.slug }));
}
```

This tells Next.js which dynamic pages to pre-render at build time instead of on-demand.

---

## 6. Layouts and Nesting

A `layout.tsx` wraps all pages in its folder and below. It **persists between navigations** — the layout does not unmount when you navigate between its child pages. This is why nav bars don't flash when you change pages.

```tsx
// src/app/layout.tsx  — root layout, wraps everything
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ProviderWrapper>  {/* Redux + Google OAuth */}
          {children}
          <Toaster />
        </ProviderWrapper>
      </body>
    </html>
  );
}
```

Layouts nest automatically:

```
RootLayout                ← src/app/layout.tsx
└── DashboardLayout       ← src/app/dashboard/(dashboard-route)/layout.tsx
    └── EventsPage        ← src/app/dashboard/(dashboard-route)/events/page.tsx
```

When a user navigates from `/dashboard/events` to `/dashboard/messages`, `RootLayout` and `DashboardLayout` both stay mounted. Only the page content swaps.

### The `"use client"` in a layout

The dashboard layout is `"use client"` because it renders `DashboardNavbar` which uses React state (for the notification bell). This is a trade-off: the whole subtree loses server rendering benefits. The ideal pattern is to push `"use client"` as deep as possible — keep layouts as Server Components and only make the interactive parts client-side.

---

## 7. Server vs Client Components

This is the single most important concept in the App Router.

### Server Components (default)

- Render on the server only.
- Can `async/await` directly — no `useEffect` needed for data fetching.
- Can access environment variables, databases, file system.
- Ship **zero JavaScript** to the browser.
- **Cannot** use hooks (`useState`, `useEffect`, etc.), browser APIs (`window`, `document`), or event handlers.

```tsx
// Server Component — no "use client" needed
async function EventList() {
  const events = await fetch("https://api.nextvibe.com/v1/events").then(r => r.json());
  return <ul>{events.map(e => <li key={e.id}>{e.name}</li>)}</ul>;
}
```

### Client Components

Add `"use client"` at the very top of the file. Everything in that file (and everything it imports) becomes client-side.

```tsx
"use client";
import { useState } from "react";

export function Counter() {
  const [count, setCount] = useState(0);
  return <button onClick={() => setCount(c => c + 1)}>{count}</button>;
}
```

### The boundary rule

Once you add `"use client"` to a component, **all its imports become client-side too**. The boundary propagates downward, not upward.

```
ServerComponent            ← Server
└── ClientComponent        ← "use client" — everything below is client
    ├── AnotherClient      ← Client (inherited)
    └── ServerComponent2   ← ALSO client (imported by a client component)
```

To pass a Server Component into a Client Component without making it client-side, pass it as `children`:

```tsx
// layout.tsx (Server)
import ClientShell from "./ClientShell";
import ServerSidebar from "./ServerSidebar";

export default function Layout({ children }) {
  return (
    <ClientShell sidebar={<ServerSidebar />}>  {/* ServerSidebar stays server */}
      {children}
    </ClientShell>
  );
}
```

### In this project

Almost every component under `src/app/dashboard/` is `"use client"` because they use Redux (`useSelector`, `useDispatch`), RTK Query hooks, or React state. This is the pragmatic choice for a highly interactive app — don't fight it. (See `learning/frontend-state-management.md` for the Redux and RTK Query patterns that drive this.)

---

## 8. API Routes (Route Handlers)

Files named `route.ts` inside `src/app/` are server-side HTTP handlers, not pages.

```
src/app/api/auth/store-token/route.ts  →  POST /api/auth/store-token
src/app/api/auth/get-token/route.ts    →  GET /api/auth/get-token
src/app/api/media-proxy/route.ts       →  GET /api/media-proxy
```

### Writing a route handler

```ts
// src/app/api/auth/store-token/route.ts
import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  const { accessToken, refreshToken } = await request.json();

  const response = NextResponse.json({ message: "Stored" }, { status: 200 });

  // Set cookies server-side — only way to set httpOnly cookies from Next.js
  response.cookies.set("accessToken", accessToken, {
    httpOnly: false,   // false = readable by JS (needed for Authorization header)
    secure: process.env.NODE_ENV === "production",
    sameSite: "lax",
    path: "/",
    maxAge: 60 * 60 * 24 * 7,  // 7 days
  });

  return response;
}
```

### Why use an API route for storing cookies?

Setting cookies in a browser via `document.cookie` or `js-cookie` makes them readable by JavaScript. Setting them via a Next.js API route lets you choose `httpOnly: true`, which hides them from JavaScript entirely (XSS protection). In this project, the route is used to store tokens after login and after token refresh. (See `learning/frontend-auth.md` for the full login flow and why this specific route — `store-token` — must be the single source of truth for every code path that writes auth cookies.)

### Supported HTTP methods

Export named functions: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`.

```ts
export async function GET(request: NextRequest) { ... }
export async function POST(request: NextRequest) { ... }
```

---

## 17. Path Aliases and Project Structure

### The `@/` alias

`@/` maps to `src/`. Configured in `tsconfig.json`:

```json
{
  "compilerOptions": {
    "paths": { "@/*": ["./src/*"] }
  }
}
```

Instead of `../../../components/ui/button`, you write `@/components/ui/button`. Always use this.

### Project structure

```
src/
├── app/                    ← All routes live here (App Router)
│   ├── (admin)/            ← Admin panel routes
│   ├── (auth)/             ← Auth routes (login, register)
│   ├── api/                ← API routes (server-side handlers)
│   │   └── auth/
│   │       ├── store-token/route.ts
│   │       └── get-token/route.ts
│   ├── dashboard/          ← Main app
│   │   ├── (dashboard-route)/  ← Routes with navbar
│   │   └── [eventId]/          ← Organiser event management
│   ├── organizer/
│   │   └── payment/verify/page.tsx  ← Ercaspay redirect landing page
│   ├── provider/           ← Redux store + RTK Query APIs
│   │   ├── api/            ← One file per API domain
│   │   ├── slices/         ← Redux slices (local state)
│   │   ├── store.ts        ← Store configuration
│   │   └── provider.tsx    ← <Provider> wrapper component
│   └── layout.tsx          ← Root layout
├── components/
│   ├── navbar/             ← App-wide navigation components
│   └── ui/                 ← shadcn/ui components (button, card, etc.)
├── hooks/                  ← Custom React hooks
│   ├── useSocket.ts        ← Socket.IO connection manager
│   ├── getToken.ts         ← Cookie token reader
│   └── useWebSocket.ts     ← Legacy (native WebSocket, superseded)
├── lib/
│   └── utils.ts            ← cn() and other utilities
└── types/                  ← Shared TypeScript types
```

---

## 20. Concepts Not Used Here (But You Should Know)

### Middleware (`src/middleware.ts`)

Middleware runs on the **Edge Runtime** before a request reaches a page or API route. Use it for:
- Auth guards (redirect unauthenticated users before the page even renders)
- Geolocation-based routing
- Rate limiting
- A/B testing

```ts
// src/middleware.ts
import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(request: NextRequest) {
  const token = request.cookies.get("accessToken");

  if (!token && request.nextUrl.pathname.startsWith("/dashboard")) {
    return NextResponse.redirect(new URL("/auth/login", request.url));
  }
}

export const config = {
  matcher: ["/dashboard/:path*", "/organizer/:path*"],
};
```

This project **does** have middleware at `src/proxy.ts` — see section 23 below for how it works. Auth guards run server-side before any page renders.

### Server Components with direct data fetching

Instead of fetching data in `useEffect`, fetch it directly in a Server Component:

```tsx
// No RTK Query needed — just async/await
async function EventPage({ params }: { params: { id: string } }) {
  const event = await fetch(`https://api.nextvibe.com/v1/events/${params.id}`, {
    headers: { Authorization: `Bearer ${getTokenFromCookie()}` },
    cache: "no-store",  // always fresh, or "force-cache" for static
  }).then(r => r.json());

  return <EventDetail event={event.data} />;
}
```

### Parallel Routes (`@slot` folders)

Display multiple pages simultaneously in the same layout (e.g. a dashboard with a main panel and a side panel, both independently navigable).

```
app/dashboard/
├── @main/
│   └── page.tsx
├── @sidebar/
│   └── page.tsx
└── layout.tsx   ← receives { main, sidebar } as props
```

### Intercepting Routes

Show a modal for a route when navigating from within the app, but the full page when navigated to directly (e.g. clicking an image shows a modal, but opening the direct URL shows the full image page).

### Static Site Generation (SSG) and ISR

```tsx
// Force static rendering
export const dynamic = "force-static";

// Incremental Static Regeneration — rebuild every 60 seconds
export const revalidate = 60;

// On-demand revalidation
import { revalidatePath } from "next/cache";
revalidatePath("/events");
```

### Server Actions

Run server-side code directly from a form, without writing an API route:

```tsx
// In a Server Component
async function createEvent(formData: FormData) {
  "use server";
  const name = formData.get("name");
  await db.events.create({ name });
  revalidatePath("/events");
}

export default function CreateForm() {
  return <form action={createEvent}><input name="name" /><button>Create</button></form>;
}
```

### React Query / TanStack Query

An alternative to RTK Query. Better suited when you don't need Redux for local state — lighter and simpler API. RTK Query is the right choice when you already have Redux in the project (like here). (See `learning/frontend-state-management.md` for the RTK Query patterns actually used in this project.)

---

## 23. Next.js Middleware — How It Really Works

### The actual file convention

Section 20 described middleware as a concept not used here. That was wrong — this project has middleware at `src/proxy.ts`. Here is how Next.js picks it up.

Next.js recognises middleware in two ways:
1. A file named `middleware.ts` at `src/` or project root that exports `middleware` (the standard)
2. **Any file** that exports `export const config = { matcher: [...] }` — Turbopack treats the file that has this shape as the middleware module regardless of its name

In this project, `src/proxy.ts` exports:

```ts
export async function proxy(req: NextRequest) { ... }  // function can be named anything
export const config = { matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"] };
```

Next.js/Turbopack compiles `proxy.ts` as the middleware entry point because of the `config` export. The function name (`proxy`) is just a convention documented by Next.js — it does not have to be `middleware`.

(See `learning/frontend-performance-debugging.md` Part 27 for a real debugging incident that hinged on recognising `proxy.ts` as live middleware despite its unusual name.)

### What middleware can do

Middleware runs on the **Edge Runtime** — a lightweight V8 environment, not full Node.js. It executes **before** a request is matched to a page or API route. This makes it perfect for:

- **Auth guards** — redirect before the page renders (server-side, not client-side)
- **Token refresh** — check expiry, refresh silently, set new cookie, continue
- **Geo-routing** — redirect based on country header

### What middleware cannot do

- No Node.js APIs (no `fs`, no `Buffer`, no `crypto` from Node)
- No `import` of large npm packages (Edge runtime has a strict size limit)
- No `console.log` visible in browser devtools (logs appear in the server terminal)

### The `config.matcher` pattern

```ts
export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"],
};
```

This regex matches every path **except** Next.js static files, optimised images, and favicon. Without this, middleware would run on every asset request — including JS bundles.

### Reading and setting cookies in middleware

```ts
import { NextRequest, NextResponse } from "next/server";

export async function proxy(req: NextRequest) {
  // Read
  const token = req.cookies.get("accessToken")?.value;

  // Redirect
  if (!token) {
    const from = encodeURIComponent(req.nextUrl.pathname + req.nextUrl.search);
    return NextResponse.redirect(new URL(`/auth/login?from=${from}`, req.url));
  }

  // Set cookie on the continuing response
  const response = NextResponse.next();
  response.cookies.set("newCookie", "value", {
    httpOnly: true,
    maxAge: 3600,
  });
  return response;
}
```

> **Important**: `req.cookies` is read-only. To set cookies you must return a `NextResponse` and call `.cookies.set()` on it.

### Server-side token refresh in middleware

When an access token is expired at page-load time, middleware can refresh it before the page even starts rendering:

```ts
const refreshRes = await fetch(`${API_URL}/v1/auth/refresh`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    cookie: req.headers.get("cookie") ?? "",  // forward the browser's cookies
  },
});

if (refreshRes.ok) {
  const { data } = await refreshRes.json();
  const response = NextResponse.next();
  response.cookies.set("accessToken", data.accessToken, { ... });
  return response;
}
```

This is more efficient than the client-side queue pattern — the page receives a fresh token in its very first request and never gets a 401 at all. (See `learning/frontend-auth.md` for the client-side `baseQueryWithReauth` queue pattern this middleware refresh complements.)

### The `?from=` requirement

Every redirect to `/auth/login` must include the current path so the user lands back where they were after logging in:

```ts
// ❌ Bad — user loses context
return NextResponse.redirect(new URL("/auth/login", req.url));

// ✅ Good
const from = encodeURIComponent(req.nextUrl.pathname + req.nextUrl.search);
return NextResponse.redirect(new URL(`/auth/login?from=${from}`, req.url));
```

The login page reads `searchParams.get("from")` and calls `router.push(from)` after a successful login. (See `learning/frontend-auth.md` Part 33 and Part 43 for the full set of bugs found in this exact `?from=` flow — an un-decoded value, a bad default, and a redirect loop guard.)

---

## 25. `useSearchParams()` and the Suspense Requirement

### The build error

```
useSearchParams() should be wrapped in a suspense boundary at page "/organizer/payment/verify"
```

This is a Next.js hard requirement, not a warning. Any page that uses `useSearchParams()` must have a `<Suspense>` boundary wrapping the component that calls it, or the build will fail with `exit code 1`.

### Why Next.js requires this

During static site generation (SSG), Next.js pre-renders pages at build time. `useSearchParams()` reads from the URL — but there is no URL at build time. Next.js needs a `<Suspense>` boundary so it can render the fallback statically while deferring the actual content (which needs the URL) to the client.

### The fix pattern

Split the page into a thin shell (exported default, no hooks) and the real component (does the work):

```tsx
// page.tsx
"use client";
import { Suspense } from "react";

// ✅ Default export — no useSearchParams here
export default function PaymentVerifyPage() {
  return (
    <Suspense fallback={<LoadingShell />}>
      <VerifyPageInner />
    </Suspense>
  );
}

// The real component — useSearchParams is safe here because it's inside Suspense
function VerifyPageInner() {
  const searchParams = useSearchParams();
  const paymentId = searchParams.get("paymentId");
  // ... rest of the component
}
```

### This also applies to

- `usePathname()` — same requirement in some configurations
- Any component that reads query params at mount time

### The pattern generalises to any "loading" state

`<Suspense>` + a fallback is the correct way to handle async boundaries in the App Router:

```tsx
// For Server Components that fetch data:
<Suspense fallback={<EventListSkeleton />}>
  <EventList />  {/* async component — can await inside */}
</Suspense>

// For client components that need URL params:
<Suspense fallback={<Spinner />}>
  <ComponentThatUsesSearchParams />
</Suspense>
```

(See section 35 below for a full deep dive on `<Suspense>` itself, and `learning/frontend-payments-games.md` Part 53 for another real page — the ticket purchase confirmation page — that needed this exact wrapper.)

---

## 34. Next.js Routing Syntax — Complete Reference

Next.js uses folder and file names as a routing DSL. Here is every piece of syntax:

### `[param]` — Dynamic segment

Matches any single path segment. The matched value is available as a prop.

```
src/app/dashboard/[eventId]/page.tsx  →  /dashboard/abc123
src/app/users/[id]/page.tsx           →  /users/42
```

```tsx
// page.tsx
export default function Page({ params }: { params: { eventId: string } }) {
  return <div>Event: {params.eventId}</div>;
}
```

In client components, use `useParams()`:
```ts
import { useParams } from "next/navigation";
const { eventId } = useParams();
```

### `[...slug]` — Catch-all segment (required)

Matches **one or more** path segments. The value is an array.

```
src/app/docs/[...slug]/page.tsx  →  /docs/a
                                 →  /docs/a/b
                                 →  /docs/a/b/c
                                 ✗  /docs  (does NOT match — needs at least one segment)
```

```tsx
export default function Page({ params }: { params: { slug: string[] } }) {
  // /docs/next/routing → slug = ["next", "routing"]
  return <div>{params.slug.join(" / ")}</div>;
}
```

**In this project**: `src/app/dashboard/[eventId]/` uses a single `[eventId]` — catch-all would be overkill.

### `[[...slug]]` — Optional catch-all

Same as `[...slug]` but also matches the parent path (zero segments).

```
src/app/shop/[[...filters]]/page.tsx  →  /shop           (filters = undefined)
                                      →  /shop/shoes      (filters = ["shoes"])
                                      →  /shop/shoes/red  (filters = ["shoes", "red"])
```

```tsx
export default function ShopPage({ params }: { params: { filters?: string[] } }) {
  const filters = params.filters ?? [];
  // /shop          → filters = []        → show everything
  // /shop/shoes    → filters = ["shoes"] → filter by shoes
  // /shop/shoes/red → filters = ["shoes","red"] → filter by shoes + red

  return (
    <div>
      <h1>Shop</h1>
      {filters.length > 0 && (
        <p>Filtering by: {filters.join(" → ")}</p>
      )}
    </div>
  );
}
```

Used for pages like filter UIs, documentation trees, or any route where the number of path segments is variable and zero is a valid state.

### `(group)` — Route group

Parentheses create a folder that is **invisible in the URL**. Used purely for organisation and shared layouts.

```
src/app/(auth)/auth/login/page.tsx   →  /auth/login   ← "(auth)" not in URL
src/app/(admin)/admin/page.tsx       →  /admin
src/app/dashboard/(dashboard-route)/events/page.tsx  →  /dashboard/events
```

Each route group can have its own `layout.tsx` that only applies to routes inside that group.

**In this project:**
| Group | Purpose |
|---|---|
| `(auth)` | Centred login/register layout, no navbar |
| `(admin)` | Admin panel layout |
| `(dashboard-route)` | Main app with `DashboardNavbar` + `BottomNav` |

### `_private` — Private folder (not a route)

Prefixing a folder with `_` opts it out of routing entirely. Useful for co-locating utilities and components with a route without accidentally exposing them.

```
src/app/dashboard/_components/event-card.tsx  →  not a route, just a component
src/app/dashboard/_utils/format-date.ts       →  not a route, just a utility
src/app/dashboard/_hooks/use-event.ts         →  not a route, just a hook
```

Without `_`, a folder named `components` inside `app/` would technically be part of the route tree (though only `page.tsx` files create actual routes — so the risk is low, but `_` makes the intent explicit).

### `@slot` — Parallel routes

Render multiple independent pages in the same layout simultaneously. Each `@slot` folder becomes a prop on the parent `layout.tsx`.

```
src/app/dashboard/
├── @feed/page.tsx      → rendered as "feed" prop
├── @sidebar/page.tsx   → rendered as "sidebar" prop
└── layout.tsx          → receives { feed, sidebar, children }
```

```tsx
// layout.tsx
export default function Layout({ feed, sidebar }: { feed: React.ReactNode; sidebar: React.ReactNode }) {
  return (
    <div className="grid grid-cols-[1fr_300px]">
      <main>{feed}</main>
      <aside>{sidebar}</aside>
    </div>
  );
}
```

Each slot can have its own loading and error states. Useful for dashboards with independently loading panels.

### `(.)` Intercepting routes — the modal URL trick

This is exactly what you described. The URL changes in the browser, but instead of navigating to a full new page, a modal opens over the current page. If you paste that same URL in a new tab, you get the real full page — not the modal.

**Instagram does this.** Click a photo → URL becomes `/photos/123`, modal opens. Open `/photos/123` in a new tab → full photo page renders.

The way Next.js implements it: you create two `page.tsx` files for the same route. One is the real full page. The other, inside a `(.)` folder, is the modal version shown during client navigation.

```
src/app/
├── photos/
│   ├── page.tsx              ← /photos — the grid
│   └── [id]/
│       └── page.tsx          ← /photos/123 — FULL page (opened in new tab or refresh)
│
└── photos/                   ← same "photos" folder name
    └── (.)photos/            ← (.) means "intercept the sibling photos route"
        └── [id]/
            └── page.tsx      ← /photos/123 — MODAL (during client navigation from /photos)
```

How to build it:

```tsx
// src/app/photos/[id]/page.tsx — the full page
export default function PhotoPage({ params }: { params: { id: string } }) {
  return (
    <div>
      <h1>Photo {params.id}</h1>
      <img src={`/img/${params.id}.jpg`} alt="" className="w-full" />
      <p>Full page — all the details, comments, etc.</p>
    </div>
  );
}
```

```tsx
// src/app/(.)photos/[id]/page.tsx — the modal intercept
"use client";
import { useRouter } from "next/navigation";

export default function PhotoModal({ params }: { params: { id: string } }) {
  const router = useRouter();

  return (
    // Dark backdrop
    <div
      className="fixed inset-0 z-50 bg-black/70 flex items-center justify-center"
      onClick={() => router.back()}  // clicking backdrop goes back
    >
      <div
        className="bg-white rounded-2xl p-6 max-w-lg w-full"
        onClick={(e) => e.stopPropagation()}  // don't close when clicking content
      >
        <img src={`/img/${params.id}.jpg`} alt="" className="w-full rounded-xl" />
        <button onClick={() => router.back()} className="mt-4 text-sm text-gray-500">
          Close
        </button>
      </div>
    </div>
  );
}
```

The modal is rendered **in the layout of the current page** — the grid stays visible behind the backdrop. The URL changes to `/photos/123` but the grid doesn't unmount.

**The intercept levels:**

| Syntax | What it intercepts | Example |
|---|---|---|
| `(.)segment` | Route at the **same** folder level | `/photos` intercepting `/photos/[id]` |
| `(..)segment` | Route **one level up** | `/dashboard/(.)events/[id]` intercepting `/events/[id]` |
| `(..)(..)segment` | Route **two levels up** | Rare |
| `(...)segment` | Route from the **root** | Anywhere in the app intercepting a root route |

**When to use this pattern:**
- Photo / media galleries (click → modal, share URL → full page)
- Event detail previews from a list
- User profile cards (hover or click on a username → profile modal)
- Any "quick look" UI where you want shareable URLs without full navigation

**Gotcha — refresh shows the modal version:**
If you're inside the modal and refresh the page, Next.js serves the real `[id]/page.tsx`, not the intercepted version. This is the desired behaviour — the URL is the source of truth.

**Gotcha — parallel routes required for the backdrop:**
The grid staying visible behind the modal requires `@slot` (parallel routes) so both the grid and the modal render at the same time. Without it, the current page unmounts when the modal route activates.

### Summary table

| Syntax | What it matches | Example |
|---|---|---|
| `page.tsx` | Exact path | `/about` |
| `[param]` | Any single segment | `/users/42` |
| `[...slug]` | One or more segments | `/docs/a/b/c` |
| `[[...slug]]` | Zero or more segments | `/shop` or `/shop/red` |
| `(group)` | Nothing — org only | Invisible in URL |
| `@slot` | Parallel render | Layout prop |
| `_private` | Nothing — excluded | Never a route |
| `(.)path` | Intercepted modal | Same-level route |

---

## 35. Suspense — Deep Dive

### What Suspense is

`<Suspense>` is a React boundary that catches components that are "not ready yet" and shows a fallback while they load. When the component finishes loading, the real content replaces the fallback.

```tsx
<Suspense fallback={<Spinner />}>
  <SlowComponent />
</Suspense>
```

### The three use cases

#### 1. Async Server Components (App Router)

Server Components can `await` directly. `<Suspense>` lets the page stream — the shell renders immediately and the slow parts fill in when their data arrives.

```tsx
// No useEffect needed — just await
async function EventList() {
  const events = await fetch("https://api.nextvibe.com/v1/events").then(r => r.json());
  return <ul>{events.data.map(e => <EventCard key={e.id} event={e} />)}</ul>;
}

// In the page:
export default function Page() {
  return (
    <div>
      <h1>Events</h1>
      <Suspense fallback={<EventListSkeleton />}>
        <EventList />  {/* streams in when data arrives */}
      </Suspense>
    </div>
  );
}
```

The user sees the heading instantly. The list appears once the fetch resolves. No blank screen.

#### 2. `useSearchParams()` (Next.js requirement)

As covered in section 25 above — any component using `useSearchParams()` must be wrapped in `<Suspense>` or the build fails.

```tsx
export default function Page() {
  return (
    <Suspense fallback={<LoadingShell />}>
      <PageInner />  {/* useSearchParams() lives here */}
    </Suspense>
  );
}
```

#### 3. Dynamic imports / code splitting

`React.lazy` + `<Suspense>` defers loading a heavy component until it's needed:

```tsx
import dynamic from "next/dynamic";

// The fabric.js canvas is large — don't include it in the initial bundle
const PostcardEditor = dynamic(() => import("./PostcardEditor"), {
  ssr: false,                                    // canvas needs browser APIs
  loading: () => <Skeleton className="h-96" />, // Suspense fallback
});

export default function Page() {
  return <PostcardEditor />;  // loaded only when this page is visited
}
```

### Nested Suspense — granular loading states

Multiple `<Suspense>` boundaries give independent loading states. Each resolves independently.

```tsx
export default function Dashboard() {
  return (
    <div className="grid grid-cols-2 gap-4">
      <Suspense fallback={<CardSkeleton />}>
        <RevenueCard />     {/* loads independently */}
      </Suspense>
      <Suspense fallback={<CardSkeleton />}>
        <AttendeeCount />   {/* loads independently */}
      </Suspense>
      <Suspense fallback={<ChartSkeleton />}>
        <SalesChart />      {/* loads independently */}
      </Suspense>
    </div>
  );
}
```

Without nested boundaries, the slowest component blocks all three from showing.

### Suspense vs Error Boundary — they are different

| | `<Suspense>` | `<ErrorBoundary>` |
|---|---|---|
| Catches | Components that are loading | Components that threw an error |
| Fallback prop | `fallback` | `fallback` or `FallbackComponent` |
| When it shows | While loading | After an error |
| Auto-recovers | Yes — when loading finishes | No — must reset manually |
| Next.js built-in | `loading.tsx` | `error.tsx` |

In the App Router, `loading.tsx` is a file-based `<Suspense>` wrapper for the whole route. `error.tsx` is a file-based `<ErrorBoundary>`.

```
src/app/dashboard/events/
├── page.tsx        ← the page
├── loading.tsx     ← shown while page.tsx is streaming (Suspense)
└── error.tsx       ← shown if page.tsx throws (ErrorBoundary)
```

### The `loading.tsx` shortcut

Instead of wrapping every page in `<Suspense>` manually, create `loading.tsx`:

```tsx
// src/app/dashboard/events/loading.tsx
export default function Loading() {
  return <EventListSkeleton />;
}
```

Next.js automatically wraps `page.tsx` with this as the `<Suspense>` fallback.

### Common mistakes

```tsx
// ❌ useSearchParams() outside Suspense — build error
export default function Page() {
  const params = useSearchParams(); // ← throws at build time
  return <div>{params.get("tab")}</div>;
}

// ✅ useSearchParams() inside Suspense
export default function Page() {
  return (
    <Suspense fallback={null}>
      <Inner />
    </Suspense>
  );
}
function Inner() {
  const params = useSearchParams(); // ← safe here
  return <div>{params.get("tab")}</div>;
}
```

```tsx
// ❌ Suspense with no fallback — blank flash
<Suspense>
  <SlowComponent />
</Suspense>

// ✅ Always provide a meaningful fallback
<Suspense fallback={<Skeleton className="h-32 w-full rounded-xl" />}>
  <SlowComponent />
</Suspense>
```

### When NOT to use Suspense

- Around synchronous components (no benefit — they never suspend)
- Instead of loading state in RTK Query (use `isLoading` from the hook)
- Around mutations (`useCreateEventMutation` — mutations don't suspend)

Suspense is for **reading** async data, not for tracking pending writes. (See `learning/frontend-state-management.md` for the RTK Query loading/error state patterns that cover the mutation case instead.)
