# NextVibe Frontend — Performance, Common Mistakes & Debugging

Split out from the original flat `frontend-learning.md` (kept untouched in the project root).
See also `learning/frontend-routing.md` (Server/Client Component boundaries, which most of the
performance advice here is about), `learning/frontend-state-management.md` (RTK Query caching
knobs), `learning/frontend-realtime.md` (Socket.IO listener cleanup), and
`learning/frontend-payments-games.md` Part 13 for a real `useEffect` re-trigger bug this file's
"stale closures" section explains.

This file covers: what actually slows a Next.js app down and the fixes (Client Component
overuse, unoptimised images, blocking scripts, code splitting, missing Suspense boundaries, RTK
Query over-fetching, `ignoreBuildErrors`), where to push the `"use client"` boundary and how to
memoise correctly, the most common categories of React/Next.js mistakes (hooks in conditionals,
mutating Redux state outside a reducer, leaking Socket.IO listeners, `window` on the server,
stale closures, casing mismatches between environments), and a set of real production debugging
incidents — a middleware file with an unusual name, a wrong API endpoint hiding behind an empty
state, a missing `position: relative`, a `FormData`/JSON content-type mismatch, and a stale
`useEffect` dependency array.

---

## 18. Performance and Optimization

### What slows Next.js apps down

1. **Too many Client Components** — every `"use client"` adds JavaScript to the bundle. Move data fetching and static rendering to Server Components where possible.

2. **Unoptimised images** — this project has `unoptimized: true`. In production, remove it. A 1MB banner image served as a 50KB WebP makes a measurable difference.

3. **Blocking scripts** — `strategy="beforeInteractive"` blocks page rendering. Only use it for scripts that are truly needed before the page appears (like auth checks). Move analytics to `afterInteractive`.

4. **No code splitting** — Next.js splits by route automatically. But large components imported at the top level still ship in the main bundle. Use dynamic imports for heavy non-critical components:

```tsx
import dynamic from "next/dynamic";

const HeavyChart = dynamic(() => import("./HeavyChart"), {
  ssr: false,        // don't render on server (useful for canvas/D3/etc.)
  loading: () => <Skeleton className="h-64" />,
});
```

5. **Missing `Suspense` boundaries** — without them, the entire page waits for the slowest data fetch. Wrap slow parts in `<Suspense>`:

```tsx
<Suspense fallback={<EventListSkeleton />}>
  <EventList />  {/* async Server Component */}
</Suspense>
```

(See `learning/frontend-routing.md` Part 35 for the full Suspense deep dive.)

6. **RTK Query over-fetching** — each `useGetXQuery()` call subscribes to the cache. If a component unmounts and remounts quickly, it'll refetch. Use `keepUnusedDataFor` to extend cache lifetime:

```ts
getEvents: builder.query({
  query: () => "/v1/events",
  keepUnusedDataFor: 300,  // keep cache for 5 minutes after component unmounts
})
```

### TypeScript `ignoreBuildErrors: true`

This project has this in `next.config.ts`. It makes CI faster but lets type errors ship to production. Disable it once the project is stable:

```ts
// next.config.ts
typescript: {
  ignoreBuildErrors: false,  // turn this on in production
}
```

### `"use client"` placement

Push the boundary as deep as possible. If only a button is interactive, only the button needs `"use client"` — not the entire page.

```tsx
// Bad ❌ — whole page becomes client-side for one button
"use client";
export default function EventPage() {
  return <div><h1>Event</h1><FavouriteButton /></div>;
}

// Good ✅ — only the interactive piece is client-side
// event-page.tsx (Server Component)
export default function EventPage() {
  return <div><h1>Event</h1><FavouriteButton /></div>;
}

// favourite-button.tsx
"use client";
export function FavouriteButton() { ... }
```

### Memoisation

```tsx
import { memo, useMemo, useCallback } from "react";

// Prevent re-render when parent re-renders but props haven't changed
const PlanCard = memo(function PlanCard({ plan, selected, onSelect }) { ... });

// Expensive calculation — recompute only when deps change
const sortedPlans = useMemo(() =>
  plans.sort((a, b) => a.finalAmount - b.finalAmount),
  [plans]
);

// Stable function reference — prevents child re-renders
const handleSelect = useCallback((planType: PlanType) => {
  setSelectedPlan(planType);
}, []);
```

---

## 21. Common Mistakes and How to Avoid Them

### 1. Calling hooks inside conditionals or loops

```tsx
// ❌ Wrong
if (user) {
  const data = useGetEventsQuery();
}

// ✅ Right — hooks must always be called at the top level
const { data } = useGetEventsQuery(undefined, { skip: !user });
```

### 2. Mutating state directly in a reducer

RTK uses Immer under the hood, which allows direct mutation inside `createSlice`. But this only works inside reducers — not outside.

```ts
// ✅ Inside a reducer — Immer handles this
setUser(state, action) {
  state.user = action.payload;  // fine
}

// ❌ Outside Redux — this mutates the reference React holds
const user = useSelector(state => state.user.user);
user.name = "New Name";  // don't do this
```

(See `learning/frontend-state-management.md` for the full Redux Toolkit slice pattern this rule applies to.)

### 3. Not cleaning up Socket.IO listeners

```tsx
// ❌ Leak — handleMessage accumulates on every render
useEffect(() => {
  socket.on("new:dm", handleMessage);
}, [isConnected]);

// ✅ Return cleanup
useEffect(() => {
  socket.on("new:dm", handleMessage);
  return () => socket.off("new:dm", handleMessage);
}, [isConnected]);
```

(See `learning/frontend-realtime.md` for the corrected, event-driven version of socket effects generally — the `isConnected` dependency shown here is actually a known source of a race condition, not just a cleanup risk.)

### 4. `window.location.href` inside Server Components

`window` doesn't exist on the server. Any code using browser globals must be inside a Client Component or guarded:

```ts
if (typeof window !== "undefined") {
  window.location.href = "/auth/login";
}
```

### 5. Stale closures in `useEffect`

When a `useEffect` captures a value that changes later, it sees the old value:

```tsx
// ❌ Stale — count is always 0 inside this effect
const [count, setCount] = useState(0);
useEffect(() => {
  const interval = setInterval(() => {
    console.log(count);  // always logs 0
  }, 1000);
  return () => clearInterval(interval);
}, []);  // count missing from deps

// ✅ Fix — add count to deps, or use functional update
useEffect(() => {
  const interval = setInterval(() => {
    setCount(c => c + 1);  // functional update avoids stale closure
  }, 1000);
  return () => clearInterval(interval);
}, []);
```

### 6. Sending `Authorization` header to Ercaspay webhook endpoints

Webhook routes are called by Ercaspay's servers, not by your users. They don't have your JWT. Don't put them behind `baseQueryWithReauth`. They're public routes secured by HMAC signature verification on the backend. (See `learning/backend-modules.md` Part 12 for the backend's HMAC webhook verification this rule protects.)

### 7. Forgetting `?from=` on auth redirects

Any time your code redirects to `/auth/login`, include the current path. The user expects to land back where they were after logging in.

```ts
// ❌
window.location.href = "/auth/login";

// ✅
const from = encodeURIComponent(window.location.pathname + window.location.search);
window.location.href = `/auth/login?from=${from}`;
```

(See `learning/frontend-auth.md` Part 33 and Part 43 for the full history of bugs found in this exact flow.)

### 8. Using `"PENDING"` vs `"pending"` — casing bugs

Backend enums are often uppercase (`"PENDING"`, `"COMPLETED"`), but some endpoints return lowercase (`"pending"`, `"completed"`). Always check the actual API response — don't assume.

In this project, `POST /organizer-payments/plan/initiate` returns uppercase `"PENDING"` / `"COMPLETED"`, but `GET /organizer-payments/verify/:id` returns lowercase `"completed"` / `"pending"` / `"failed"`. Mixing these up will break status checks silently.

---

## Quick Reference

### Most-used Next.js imports

```ts
import { useRouter, useSearchParams, useParams, usePathname } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import { redirect, notFound } from "next/navigation";  // server-side
```

---

## 27. Debugging Real-World Production Issues

These are patterns that came up during active development of this project. Each one is a category of bug you will encounter.

### Dead code that looks live

`src/proxy.ts` exports `export const config = { matcher: [...] }`. This is a Next.js/Turbopack convention — the file was compiled as middleware because of this export shape, even though it's not named `middleware.ts`. The bugs inside it (no `?from=`, admin cookie not checked) were real and silent.

**Lesson**: When debugging redirect issues, always search for ALL places that call `redirect`, `router.push`, and `window.location.href`. Don't assume a file isn't running just because it has an unusual name. (See `learning/frontend-routing.md` Part 23 for the full explanation of how `src/proxy.ts` gets picked up as middleware.)

### Wrong API endpoint buried in a query

The notification bell wasn't showing any notifications. The actual API call was:

```ts
// Wrong — this is a cron/admin trigger endpoint, not the user's notification list
query: () => "/v1/notifications/trigger-reminders",

// Right
query: () => "/v1/notifications",
```

The UI showed "All caught up!" correctly (empty state rendered properly) so no error appeared. The bug was invisible until you compared the endpoint against the API spec.

**Lesson**: When a feature shows empty state but you expect data, check the actual network request in devtools before assuming the UI is broken.

### Absolute-positioned badge with no relative parent

The notification count badge:

```tsx
// ❌ — badge floats away from the bell icon
<div aria-label="Notifications">
  <Bell />
  <span className="absolute top-1 right-1 ...">3</span>
</div>

// ✅ — relative creates the positioning context
<div aria-label="Notifications" className="relative cursor-pointer p-1.5">
  <Bell />
  <span className="absolute top-1 right-1 ...">3</span>
</div>
```

`absolute` positions an element relative to its **nearest ancestor with `position` set** (`relative`, `absolute`, `fixed`, `sticky`). Without `relative` on the parent, the badge positions relative to the page or a far-off ancestor.

**Lesson**: When an absolutely positioned element is in the wrong place, check its parent chain for `position: relative`.

### FormData vs JSON — silent backend mismatch

After the backend removed `FileFieldsInterceptor`, it expected `Content-Type: application/json` for event creation. The frontend was still sending `multipart/form-data` (FormData). The backend may have returned a 400 or silently ignored file fields. No explicit error was thrown on the frontend.

**Lesson**: When a backend changes its expected content type, the frontend must change too. Check the `Content-Type` header in devtools whenever a create/update flow breaks. (See `learning/backend-core.md` Part 32 and `learning/frontend-uploads-errors.md` Part 22 for the presigned-URL migration that caused this exact mismatch.)

### Stale `useEffect` not re-triggering

```tsx
// ❌ "Check again" resets state but the effect doesn't re-run
const [pollState, setPollState] = useState("polling");
useEffect(() => { poll(); }, [paymentId]);  // paymentId never changes

// ✅ Add a retryKey to force the effect to re-run
const [retryKey, setRetryKey] = useState(0);
useEffect(() => { poll(); }, [paymentId, retryKey]);

// "Check again" button:
onClick={() => {
  attemptRef.current = 0;
  setPollState("polling");
  setRetryKey(k => k + 1);  // dependency changes → effect fires again
}}
```

**Lesson**: If a `useEffect` isn't re-running when you expect it to, the issue is almost always its dependency array. Add a counter state (`retryKey`, `refreshKey`, `key`) to its deps when you need to force a re-run without changing the actual data. (See `learning/frontend-payments-games.md` Part 13 for the real payment-verification page this exact bug and fix came from.)
