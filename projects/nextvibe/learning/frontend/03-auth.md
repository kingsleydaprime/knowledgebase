# NextVibe Frontend — Authentication, Tokens & Login Redirects

Split out from the original flat `frontend-learning.md` (moved to `learning/archive/`).
See also `learning/frontend/01-routing.md` (the `src/proxy.ts` middleware this auth system relies
on), `learning/frontend/02-state-management.md` (the `baseQueryWithReauth` RTK Query base query),
`learning/frontend/06-realtime.md` (Socket.IO auth handshake, which shares the same cookies), and
`learning/backend/02-auth.md` for the backend half of this same JWT system (Argon2 hashing, the
access/refresh token lifecycle, Google OAuth verification, the `@Public()` guard).

This file covers: the full login/refresh/logout flow and why cookies (not localStorage) are used,
the multi-role (user vs admin) cookie-prefixing strategy and the three-layer fix required to make
it work everywhere, the difference between cookie-based and Redux-based auth state on public
pages, the login redirect `?from=` logic and its role-specific defaults, a cookie-expiry bug that
silently killed WebSocket authentication, and a URL-encoding bug in the Google login redirect.

---

## 11. Authentication Flow

This is the most complex part of the frontend. Understanding it end-to-end is essential.

### Token storage — cookies, not localStorage

Tokens live in browser cookies managed by `js-cookie`. There are two tokens:

| Cookie | `httpOnly` | Purpose |
|---|---|---|
| `accessToken` | `false` — readable by JS | Sent in `Authorization: Bearer` on every request |
| `refreshToken` | `false` — readable by JS | Sent in POST body to `/v1/auth/refresh` when access token expires |

> **Why cookies over localStorage?** Cookies can be scoped to a path and sent automatically by the browser. `httpOnly` cookies are invisible to JavaScript, protecting against XSS. This project makes both cookies JS-readable because the refresh token must be read and sent in a POST body.

### Login flow

```
User submits email + password
    ↓
POST /v1/auth/login
    ↓
Backend returns { accessToken, refreshToken, user }
    ↓
Frontend calls POST /api/auth/store-token (Next.js API route)
    ↓
API route sets both as cookies with correct expiry + flags
    ↓
Redux: dispatch(setUser(user)), dispatch(setIsAuthenticated(true))
    ↓
router.push("/dashboard/events")
```

Why go through the Next.js API route instead of using `Cookies.set()` directly? So the cookie attributes (secure, sameSite, maxAge) are set server-side and consistently — `js-cookie` on the client can't set `maxAge` in seconds, and its `expires` is always in days. (See Part 37 below for a real production bug caused by bypassing this route and calling `Cookies.set()` directly with the wrong `expires` unit.)

### Refresh token flow (the queue pattern)

When an access token expires, the server returns 401. The `baseQueryWithReauth` intercepts this:

```
Request A → 401
Request B → 401 (arrives 5ms later, refresh hasn't started yet)
Request C → 401 (arrives 10ms later)

baseQueryWithReauth for A:
  isRefreshing is false → own the refresh
  isRefreshing = true
  POST /v1/auth/refresh { refreshToken }
  → new accessToken
  → store-token (update cookie)
  → flushQueue(true) — resolves B and C's promises
  → retry A with new cookie

baseQueryWithReauth for B:
  isRefreshing is true → push to pendingRequests, await
  [waits...]
  → resolve() called → retry B (cookie already updated)

baseQueryWithReauth for C:
  same as B
```

Without the queue, A, B, and C would each call `/refresh`, rotating the token 3 times and invalidating the first two. (See `learning/backend/02-auth.md` for the backend side of this exact rotation — the refresh token is deleted from Redis and reissued on every use, which is exactly why a client-side queue is required.)

### Redirect to login with `?from=`

When a 401 is unrecoverable (refresh token also expired), the user is sent to login. The current URL is preserved so they land back where they were:

```ts
const from = encodeURIComponent(window.location.pathname + window.location.search);
window.location.href = `/auth/login?from=${from}`;
```

The login page reads this and redirects after successful login, using role-specific fallbacks when `?from=` is absent:

```ts
const from = searchParams.get("from");  // null when not present — never default here
const validFrom = from && from.startsWith("/") && !from.startsWith("/auth");

if (isSuperAdmin) {
  router.push(validFrom ? from : "/admin");           // admin default
} else {
  router.push(validFrom ? from : "/dashboard/events"); // user default
}
```

The `!from.startsWith("/auth")` guard prevents redirect loops — if someone was redirected from an auth page itself, they get the role default instead. (See Part 33 below for the full bug history behind this exact logic, and Part 43 for a related URL-encoding bug in the Google login button.)

### Logout flow

```ts
// Call backend to invalidate the refresh token
await api.post("/v1/auth/logout", { refreshToken: Cookies.get("refreshToken") });

// Clear local state
Cookies.remove("accessToken");
Cookies.remove("refreshToken");
dispatch(logout());  // clear Redux user state
window.location.href = "/auth/login";
```

---

## 24. Multi-Role Auth Token Strategy

### The problem

This project has two user roles that need separate permissions: regular users and admins. The naive approach of one token caused a critical bug: **admins could not visit non-admin pages**.

### Why it broke

When an admin logged in, `store-token` prefixed the cookies with `admin_`:

```ts
// Before the fix — BAD
const prefix = isAdmin ? "admin_" : "";
response.cookies.set(`${prefix}accessToken`, accessToken);
// Admin gets: admin_accessToken
// Non-admin routes check: accessToken  ← undefined for admins → 401
```

Every API call on a non-admin page (`/dashboard`, `/profile`, etc.) had no token and immediately 401'd.

### The three-layer fix

The fix must be consistent across all three places that check for tokens:

#### Layer 1 — `store-token` route (cookie writing)

Write **both** the plain and the prefixed cookie whenever an admin logs in:

```ts
// Always write the unprefixed cookie
response.cookies.set("accessToken", accessToken, { ... });
if (refreshToken) response.cookies.set("refreshToken", refreshToken, { ... });

// Additionally write the admin-prefixed cookies
if (isAdmin) {
  response.cookies.set("admin_accessToken", accessToken, { ... });
  response.cookies.set("admin_refreshToken", refreshToken, { ... });
}
```

Non-admin pages find `accessToken`. Admin pages prefer `admin_accessToken` but fall back to `accessToken`.

#### Layer 2 — middleware (server-side page guard)

Fall back to admin tokens when checking non-admin routes:

```ts
const accessToken =
  req.cookies.get("accessToken")?.value ??
  req.cookies.get("admin_accessToken")?.value;  // fallback for admin users

const refreshToken =
  req.cookies.get("refreshToken")?.value ??
  req.cookies.get("admin_refreshToken")?.value;
```

This allows existing admin sessions (that only have `admin_accessToken`) to access non-admin pages without requiring a re-login. (This is the `src/proxy.ts` middleware described in `learning/frontend/01-routing.md` Part 23.)

#### Layer 3 — `baseQuery` (client-side API calls)

Same fallback pattern in `prepareHeaders` and the refresh token lookup:

```ts
// prepareHeaders
const accessToken = isAdminRoute
  ? (Cookies.get("admin_accessToken") ?? Cookies.get("accessToken"))
  : (Cookies.get("accessToken") ?? Cookies.get("admin_accessToken")); // ← fallback added

// refresh token lookup
const refreshToken = isAdminRoute
  ? (Cookies.get("admin_refreshToken") ?? Cookies.get("refreshToken"))
  : (Cookies.get("refreshToken") ?? Cookies.get("admin_refreshToken")); // ← fallback added
```

### Why all three layers matter

| Layer | Catches what |
|---|---|
| `store-token` | New logins — sets cookies correctly from day one |
| Middleware | Server-side redirect before page renders |
| `baseQuery` | Client-side API calls after page loads |

If only middleware is fixed, the page renders but every API call 401s. If only `baseQuery` is fixed, the middleware blocks the page before it renders. You need all three consistent.

### Token priority table

| Route | Access token used | Refresh token used |
|---|---|---|
| `/admin/*` | `admin_accessToken` → `accessToken` | `admin_refreshToken` → `refreshToken` |
| Everything else | `accessToken` → `admin_accessToken` | `refreshToken` → `admin_refreshToken` |

---

## 32. Auth State on Public Pages — Cookies vs Redux

### The two layers of auth state

| Layer | Where | Survives page refresh? | When populated |
|---|---|---|---|
| Cookies (`accessToken`) | Browser storage | Yes — until expiry (7 days) | After login, via `store-token` route |
| Redux (`isAuthenticated`) | JavaScript memory | No — reset on every mount | After login, via `dispatch(setIsAuthenticated(true))` |

### The bug this caused

The home page navbar had:
```ts
const [isAuthenticated] = useState(false); // hardcoded false
```

This meant logged-in users always saw "Login / Sign Up" on the home page instead of a "Dashboard" button.

Attempting to fix it with Redux:
```ts
const { isAuthenticated } = useSelector((state: RootState) => state.auth.isAuthenticated);
```
…would fix it immediately after login, but break again after any page refresh — because Redux resets to `initialState: { isAuthenticated: false }` on every cold mount and there is no rehydration mechanism.

### The correct fix — read the cookie

```ts
"use client";
import Cookies from "js-cookie";
import { useState, useEffect } from "react";

export default function Navbar() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Cookies survive page refreshes — this is the source of truth
    const token = Cookies.get("accessToken") ?? Cookies.get("admin_accessToken");
    setIsAuthenticated(!!token);
  }, []);

  // ...
}
```

Why `useEffect` instead of reading directly?

- `Cookies.get()` is a browser API — it doesn't exist on the server
- The component starts server-rendered with `false`, then hydrates with the real value
- This avoids hydration mismatches between server HTML and client HTML

### When to use Redux vs cookies for auth state

| Use case | Use |
|---|---|
| Rendering user's name, avatar, role | Redux `user` slice (populated after login, or after a `getMe` call) |
| Showing/hiding Login button | Cookie check — survives refreshes |
| API auth headers | Cookie directly via `js-cookie` in `baseQuery` |
| Route guards | Middleware reads cookie server-side |

---

## 33. Login Redirect — Role-Specific Defaults and the `?from=` Bug

### The full redirect lifecycle

```
1. User visits /dashboard without being logged in
2. Middleware redirects: /auth/login?from=%2Fdashboard
3. User logs in
4. Login page reads ?from= and redirects back to /dashboard
```

### The bug

```ts
// ❌ Bug: defaulting to "/events" for everyone
const from = searchParams.get("from") || "/events";

if (isSuperAdmin) {
  router.push(from.startsWith("/") && !from.startsWith("/auth") ? from : "/admin");
}
```

When an admin visits the login page **directly** (no `?from=`), `from` defaults to `"/events"`. The condition `"/events".startsWith("/")` is `true`, so the admin gets sent to `/events` instead of `/admin`.

### The fix

```ts
// ✅ Read as nullable — no default here
const from = searchParams.get("from");  // null when absent

// Validate: must be an internal path and not another auth page
const validFrom = from && from.startsWith("/") && !from.startsWith("/auth");

// Role-specific fallbacks
if (isSuperAdmin) {
  router.push(validFrom ? from : "/admin");          // admin's home
} else {
  router.push(validFrom ? from : "/dashboard/events"); // user's home
}
```

### The `!from.startsWith("/auth")` guard

Prevents infinite redirect loops. Without it:
1. User is on `/auth/login`
2. Middleware redirects to `/auth/login?from=%2Fauth%2Flogin`
3. After login, pushed back to `/auth/login`
4. Middleware redirects again... forever

### Also fix the register link

The register URL on the login page forwards `?from=` to the register page so that after registering, the user also lands in the right place:

```ts
const queryParams = new URLSearchParams();
if (from) queryParams.set("from", from);  // from is null-safe now
const registerUrl = `/auth/register${queryParams.toString() ? `?${queryParams.toString()}` : ""}`;
```

(See Part 43 below for a second, related bug in this same flow — the `?from=` value arrives URL-encoded and must be decoded before the `startsWith("/")` check works at all.)

---

## 37. Cookie Expiry Killing Socket Auth — The 1/96 Bug

### The symptom

Socket connections would work for ~15 minutes after Google login, then silently fail. `useSocket` would log `status → error` immediately on the next page load, even though the user was clearly logged in (REST calls worked).

### Why `status → "error"` happens in useSocket

```ts
// src/hooks/useSocket.ts
const token = Cookies.get("accessToken");
if (!token) {
  setStatus("error");  // ← this fires when the cookie is missing
  return;              // socket is never created
}
```

`"error"` is the sentinel for "no token". The socket never attempts to connect. (See `learning/frontend/06-realtime.md` for the full `useSocket` hook this snippet belongs to.)

### Root cause — wrong cookie expiry in Google login

```ts
// ❌ src/app/(auth)/components/google-login-button.tsx — BEFORE FIX
Cookies.set("accessToken", res?.data?.accessToken, {
  expires: 1 / 96,  // ← 1/96 of a day = 15 MINUTES
});
```

`js-cookie`'s `expires` is in **days**, not seconds. `1/96` was clearly intended to be something else but evaluates to 15 minutes. After that the cookie expired and the socket could never connect.

The regular login used the `store-token` API route which sets `maxAge: 60 * 60 * 24 * 7` (7 days). Google login bypassed that route and set its own cookies directly.

### The fix

Make Google login use the same `store-token` route as regular login:

```ts
// ✅ AFTER FIX — consistent, 7-day expiry, correct cookie name
await fetch("/api/auth/store-token", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    accessToken: res?.data?.accessToken,
    refreshToken: res?.data?.refreshToken,
    isAdmin: isSuperAdmin,
  }),
});
// No direct Cookies.set() — the API route handles expiry and naming consistently
```

### Second issue — admin users' cookie name mismatch

Google login also had:

```ts
const cookiePrefix = isSuperAdmin ? "admin_" : "";
Cookies.set(`${cookiePrefix}accessToken`, ...);
```

Admin users got cookie `admin_accessToken`. `useSocket` only checked `Cookies.get("accessToken")` → undefined → error. Fixed by:

1. Using `store-token` which always sets the plain `accessToken` (plus `admin_accessToken` for admins)
2. Making `useSocket` try both names as a fallback:

```ts
// useSocket.ts
const token = Cookies.get("accessToken") ?? Cookies.get("admin_accessToken");
```

### Rule

**All token storage must go through the `store-token` API route.** Never call `Cookies.set("accessToken", ...)` directly from client code. The route is the single source of truth for expiry, naming, and flags.

---

## 43. Google Login Redirect — The `?from=` Encoding Bug

### The full redirect flow

When a user visits a protected route without being logged in:

```
1. User visits /messages
2. Middleware redirects: /auth/login?from=%2Fmessages
   (the path is encoded with encodeURIComponent so "/" becomes "%2F")
3. User logs in (email/password or Google)
4. Login page reads ?from= and redirects back to /messages
```

Step 2 is important: `encodeURIComponent("/messages")` produces `"%2Fmessages"`, not `"/messages"`. The `?from=` value in the URL is encoded.

### The bug

The login page was reading `?from=` and checking if it started with `"/"`:

```ts
// ❌ Bug — reads raw encoded value, checks for "/"
const from = searchParams.get("from");  // returns "%2Fmessages"

const validFrom = from && from.startsWith("/");  // "%2Fmessages".startsWith("/") → FALSE
// validFrom is false → user gets sent to default (/events) instead of /messages
```

`"%2Fmessages"` starts with `%`, not `/`. So `startsWith("/")` returned `false` for every redirect. Every user after being sent to login would land on `/events` regardless of where they came from.

The same bug existed in the Google login button — it received `?from=` in the URL and had the same encoded check.

### The fix — decode before checking

```ts
// ✅ Fix — decode first, then check
const rawFrom = searchParams.get("from");  // "%2Fmessages"

const from = rawFrom
  ? (() => {
      try { return decodeURIComponent(rawFrom); }  // → "/messages"
      catch { return rawFrom; }  // malformed encoding — fall back to raw
    })()
  : null;

const validFrom = from && from.startsWith("/") && !from.startsWith("/auth");
// "/messages".startsWith("/") → TRUE ✓
// Then redirect to "/messages" ✓
```

The `try/catch` around `decodeURIComponent` is important: if someone manually crafts a URL with a broken encoding like `?from=%GG`, `decodeURIComponent` throws a `URIError`. Without the catch, the whole login would crash.

### Why `!from.startsWith("/auth")` matters

Without this guard:

```
1. User is on /auth/login
2. Middleware (confusingly) redirects to /auth/login?from=%2Fauth%2Flogin
3. User logs in
4. from = "/auth/login"
5. validFrom = true (it starts with "/")
6. router.push("/auth/login")
7. Middleware redirects back to /auth/login?from=...
8. → Infinite loop
```

The `!from.startsWith("/auth")` guard short-circuits this: if you came from an auth page, just use the role default (`/events` or `/admin`) instead.

### The role-specific default bug (also fixed)

Before the fix, the default was set with `||`:

```ts
// ❌ Bug — defaults to "/events" for everyone including admins
const from = searchParams.get("from") || "/events";

if (isSuperAdmin) {
  router.push(from.startsWith("/") ? from : "/admin");
  // When no ?from= param: from = "/events"
  // "/events".startsWith("/") = true → admin sent to /events ❌
}
```

When an admin visited the login page directly (no `?from=`), `from` defaulted to `"/events"`. The guard `from.startsWith("/")` was satisfied, so the admin got redirected to `/events` instead of `/admin`.

```ts
// ✅ Fix — null when absent, then use role-specific fallback
const from = searchParams.get("from");  // null when absent — no default

const validFrom = from && from.startsWith("/") && !from.startsWith("/auth");

if (isSuperAdmin) {
  router.push(validFrom ? from : "/admin");   // null → "/admin" ✓
} else {
  router.push(validFrom ? from : "/events");  // null → "/events" ✓
}
```

Key insight: **never default `?from=` to a path string**. Default to `null`. Let the role-specific fallback handle the "no redirect target" case separately.

### Summary — the three things that must be right

| Step | What it does | What can go wrong |
|---|---|---|
| Middleware encodes the path | `encodeURIComponent(pathname)` → `%2Fmessages` | Nothing — this is correct |
| Login reads and decodes | `decodeURIComponent(rawFrom)` → `/messages` | Forgetting to decode → `startsWith("/")` fails |
| Login validates | `startsWith("/") && !startsWith("/auth")` | Missing the auth guard → infinite loop |
| Login applies role default | `null → "/admin"` or `null → "/events"` | Using `|| "/events"` as default → admins go to wrong page |

---

## Quick Reference

### Middleware redirect with `?from=`

```ts
const from = encodeURIComponent(req.nextUrl.pathname + req.nextUrl.search);
return NextResponse.redirect(new URL(`/auth/login?from=${from}`, req.url));
```

### Admin token fallback (both middleware and baseQuery)

```ts
const accessToken =
  Cookies.get("accessToken") ??
  Cookies.get("admin_accessToken");  // admin users can visit non-admin pages
```

### Auth token access

```ts
import Cookies from "js-cookie";
const accessToken = Cookies.get("accessToken");
const refreshToken = Cookies.get("refreshToken");
```

---

## The 401 refresh loop: latch a dead session (2026-08-21)

The console showed the same three lines over and over:

```
GET  /v1/users/me       401
POST /api/auth/refresh  401
GET  /v1/conversations  401
POST /api/auth/refresh  401
...
```

### Why it looped

`baseQueryWithReauth` had a queue so that simultaneous 401s share one refresh:

```ts
let isRefreshing = false;
// ...
} finally {
  isRefreshing = false;
}
```

That correctly deduplicates requests that 401 *at the same moment*. What it
doesn't do is remember the **outcome**. Once the refresh failed, `isRefreshing`
went back to `false`, so the next component to mount and fire a query hit a 401,
saw no refresh in flight, and started its own — which failed identically. Every
query in the app got its own doomed refresh, forever.

The queue is a *concurrency* guard. What was missing is a *state* guard:

```ts
let refreshRejected = false;

// in the handler, before starting a refresh:
if (refreshRejected) return result;   // session is known dead — fail fast
```

Plus a way back, called on a fresh login so the module-level flag doesn't
outlive the dead session:

```ts
export function resetAuthRefreshState() {
  refreshRejected = false;
}
```

**Module-level mutable state in a base query is a latch, not a cache** — it
survives every component unmount and every route change, so anything you set
there needs an explicit reset path. Forgetting that is how you ship an app that
can't log back in without a hard reload.

### Two related mistakes in the same handler

**1. Treating every failure as a dead session.** The `catch` covered network
errors and the abort timeout, and responded by deleting the user's cookies:

```ts
} catch {
  flushQueue(false);
  clearSessionAndRedirect(isAdminRoute);   // ← logs you out over a blip
  return result;
}
```

An abort tells you nothing about whether the session is valid. Now the catch
leaves credentials alone, and only an explicit 401/403 from the refresh route
ends the session.

**2. An abort timeout shorter than the server's worst case.** The cap was 10 s
against an API that cold-starts on Render's free tier. The abort didn't cancel
the server's work — the backend still processed the refresh and rotated the
token away, leaving the client holding a token the server had just deleted.
Raised to 20 s, and the backend now keeps a replay window (see
[backend/02-auth.md](../backend/02-auth.md)).

**Aborting a request does not undo it.** The server may well have completed the
work. For anything that mutates state — and rotating a refresh token mutates
state — the client and server need to agree on what happens when the response
is lost.
