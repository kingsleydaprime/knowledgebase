# NextVibe — Frontend Learning Reference

A complete guide to the patterns, decisions, and concepts used in this codebase.
Written for someone who has never touched Next.js but wants to understand it from first principles through to advanced production patterns.

---

## Table of Contents

1. [What This Project Is](#1-what-this-project-is)
2. [The App Router — Next.js 13+](#2-the-app-router--nextjs-13)
3. [File-Based Routing](#3-file-based-routing)
4. [Route Groups](#4-route-groups)
5. [Dynamic Routes](#5-dynamic-routes)
6. [Layouts and Nesting](#6-layouts-and-nesting)
7. [Server vs Client Components](#7-server-vs-client-components)
8. [API Routes (Route Handlers)](#8-api-routes-route-handlers)
9. [State Management — Redux Toolkit](#9-state-management--redux-toolkit)
10. [Data Fetching — RTK Query](#10-data-fetching--rtk-query)
11. [Authentication Flow](#11-authentication-flow)
12. [Real-Time with Socket.IO](#12-real-time-with-socketio)
13. [Payment Integration Pattern](#13-payment-integration-pattern)
14. [Forms — react-hook-form + zod](#14-forms--react-hook-form--zod)
15. [UI Layer — shadcn/ui + Tailwind](#15-ui-layer--shadcnui--tailwind)
16. [Fonts, Images, and Scripts](#16-fonts-images-and-scripts)
17. [Path Aliases and Project Structure](#17-path-aliases-and-project-structure)
18. [Performance and Optimization](#18-performance-and-optimization)
19. [Scaling Patterns](#19-scaling-patterns)
20. [Concepts Not Used Here (But You Should Know)](#20-concepts-not-used-here-but-you-should-know)
21. [Common Mistakes and How to Avoid Them](#21-common-mistakes-and-how-to-avoid-them)
22. [Presigned Upload URLs](#22-presigned-upload-urls--streaming-files-directly-to-storage)
23. [Next.js Middleware — How It Really Works](#23-nextjs-middleware--how-it-really-works)
24. [Multi-Role Auth Token Strategy](#24-multi-role-auth-token-strategy)
25. [useSearchParams() and the Suspense Requirement](#25-usesearchparams-and-the-suspense-requirement)
26. [Discriminated AI Responses](#26-discriminated-ai-responses--handling-type-specific-shapes)
27. [Debugging Real-World Production Issues](#27-debugging-real-world-production-issues)
28. [Universal Error Handler — Full Implementation](#28-universal-error-handler--full-implementation)
29. [Network Status Detection — Online / Offline](#29-network-status-detection--online--offline)
30. [Error Logging — Fire-and-Forget Pattern](#30-error-logging--fire-and-forget-pattern)
31. [Immediate Upload on File Selection — UX State Machine](#31-immediate-upload-on-file-selection--ux-state-machine)
32. [Auth State on Public Pages — Cookies vs Redux](#32-auth-state-on-public-pages--cookies-vs-redux)
33. [Login Redirect — Role-Specific Defaults and the ?from= Bug](#33-login-redirect--role-specific-defaults-and-the-from-bug)
34. [Next.js Routing Syntax — Complete Reference](#34-nextjs-routing-syntax--complete-reference)
35. [Suspense — Deep Dive](#35-suspense--deep-dive)
36. [Socket.IO — Event-Driven Join (The isConnected Race Condition)](#36-socketio--event-driven-join-the-isconnected-race-condition)
37. [Cookie Expiry Killing Socket Auth — The 1/96 Bug](#37-cookie-expiry-killing-socket-auth--the-196-bug)
38. [Optimistic Messages — Deduplication Pattern](#38-optimistic-messages--deduplication-pattern)
39. [Chat UI — Grouped Bubbles, Avatars, and Full-Screen Escape](#39-chat-ui--grouped-bubbles-avatars-and-full-screen-escape)
40. [Synthesised Notification Sounds — Web Audio API](#40-synthesised-notification-sounds--web-audio-api)
41. [Real-Time Notification Badge — pendingIds vs Counter](#41-real-time-notification-badge--pendingids-vs-counter)
42. [WebSockets from First Principles — ws, wss, and Socket.IO](#42-websockets-from-first-principles--ws-wss-and-socketio)
43. [Google Login Redirect — The `?from=` Encoding Bug](#43-google-login-redirect--the-from-encoding-bug)
44. [Conversations List — Real-Time Updates and Stale Cache](#44-conversations-list--real-time-updates-and-stale-cache)
45. [Per-Conversation Unread Badge — Local + Server Merge](#45-per-conversation-unread-badge--local--server-merge)
46. [Bottom Nav Real-Time Badge — Shared Cache + Conditional Socket](#46-bottom-nav-real-time-badge--shared-cache--conditional-socket)
47. [Event Chat — Message Order and Prepend vs Append](#47-event-chat--message-order-and-prepend-vs-append)
48. [Tab Switching and Sockets — Effect Dependencies](#48-tab-switching-and-sockets--effect-dependencies)
49. [Word Puzzle — Auditing an Implementation Against a Design Spec](#49-word-puzzle--auditing-an-implementation-against-a-design-spec)
50. [Dead Code — Recognising and Removing Unreachable Functions](#50-dead-code--recognising-and-removing-unreachable-functions)

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

Almost every component under `src/app/dashboard/` is `"use client"` because they use Redux (`useSelector`, `useDispatch`), RTK Query hooks, or React state. This is the pragmatic choice for a highly interactive app — don't fight it.

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

Setting cookies in a browser via `document.cookie` or `js-cookie` makes them readable by JavaScript. Setting them via a Next.js API route lets you choose `httpOnly: true`, which hides them from JavaScript entirely (XSS protection). In this project, the route is used to store tokens after login and after token refresh.

### Supported HTTP methods

Export named functions: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`, `HEAD`, `OPTIONS`.

```ts
export async function GET(request: NextRequest) { ... }
export async function POST(request: NextRequest) { ... }
```

---

## 9. State Management — Redux Toolkit

Redux Toolkit (RTK) is the official, modern way to use Redux. This project has two categories of Redux state:

### Slices — local UI state

Slices hold state that doesn't come from the API: who is logged in, the current event form values, canvas state, UI flags.

```ts
// src/app/provider/slices/user.ts
const authSlice = createSlice({
  name: "auth",
  initialState: { user: null, isAuthenticated: false },
  reducers: {
    setUser(state, action: PayloadAction<IUser | null>) {
      state.user = action.payload;  // Immer allows direct mutation
    },
    logout(state) {
      state.user = null;
      state.isAuthenticated = false;
    },
  },
});
```

**Slices in this project:**

| Slice | Purpose |
|---|---|
| `user` | Auth state: who is logged in, their role |
| `eventForm` | Multi-step event creation form values |
| `location` | User's selected location |
| `canvas` | Fabric.js canvas state for postcard editor |
| `ui` | UI flags like `hideHeader` |

### Using slice state in a component

```tsx
"use client";
import { useSelector, useDispatch } from "react-redux";
import { RootState } from "@/app/provider/store";
import { logout } from "@/app/provider/slices/user";

function ProfileButton() {
  const user = useSelector((state: RootState) => state.user.user);
  const dispatch = useDispatch();

  return (
    <div>
      <p>{user?.username}</p>
      <button onClick={() => dispatch(logout())}>Log out</button>
    </div>
  );
}
```

### The store — wiring everything together

```ts
// src/app/provider/store.ts
export const store = configureStore({
  reducer: {
    user: authReducer,
    eventForm: eventFormReducer,
    [authApi.reducerPath]: authApi.reducer,  // RTK Query APIs also go in the reducer
    // ... all other APIs
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware().concat(
      authApi.middleware,
      // ... all other API middlewares (required for caching, invalidation)
    ),
});
```

The store is provided to the app through `<Provider store={store}>` inside `ProviderWrapper`, which wraps the entire app in the root layout.

---

## 10. Data Fetching — RTK Query

RTK Query is a data fetching and caching layer built into Redux Toolkit. It replaces `useEffect + fetch + useState` for API calls.

### Defining an API

```ts
// src/app/provider/api/eventApi.ts
export const eventsApi = createApi({
  reducerPath: "eventsApi",       // key in the Redux store
  baseQuery: baseQueryWithReauth, // all requests go through this
  tagTypes: ["Events"],           // for cache invalidation
  endpoints: (builder) => ({

    // Query = GET — reads data, caches it
    getEvents: builder.query<EventsResponse, void>({
      query: () => "/v1/events",
      providesTags: ["Events"],
    }),

    // Mutation = POST/PUT/DELETE — writes data, can invalidate cache
    createEvent: builder.mutation<Event, CreateEventBody>({
      query: (body) => ({ url: "/v1/events", method: "POST", body }),
      invalidatesTags: ["Events"],  // clears the events cache after creating one
    }),
  }),
});

export const { useGetEventsQuery, useCreateEventMutation } = eventsApi;
```

### Using queries in components

```tsx
function EventList() {
  const { data, isLoading, isError, refetch } = useGetEventsQuery();

  if (isLoading) return <Spinner />;
  if (isError) return <ErrorMessage onRetry={refetch} />;

  return <ul>{data?.data.map(e => <EventCard key={e.id} event={e} />)}</ul>;
}
```

RTK Query automatically:
- Deduplicates identical requests (if 3 components call `useGetEventsQuery()`, only 1 HTTP request goes out)
- Caches results
- Refetches when the cache is invalidated
- Manages loading/error state

### Using mutations

```tsx
function CreateEventButton() {
  const [createEvent, { isLoading }] = useCreateEventMutation();

  const handleCreate = async () => {
    try {
      const newEvent = await createEvent({ name: "My Event" }).unwrap();
      toast.success("Created!");
    } catch (err: any) {
      toast.error(err?.data?.message ?? "Something went wrong");
    }
  };

  return <button onClick={handleCreate} disabled={isLoading}>Create</button>;
}
```

`.unwrap()` throws on error instead of returning it — lets you use `try/catch`.

### Lazy queries — fetch on demand

```tsx
const [verifyPayment, { isLoading }] = useLazyVerifyOrganizerPaymentQuery();

// Called imperatively, not on mount
const result = await verifyPayment(paymentId).unwrap();
```

Used in the payment verify page to poll manually instead of fetching on mount.

### The `baseQueryWithReauth`

Every RTK Query API in this project uses a shared `baseQueryWithReauth` instead of a plain `fetchBaseQuery`. It adds:

1. **Token attachment** — reads `accessToken` from the cookie and adds `Authorization: Bearer <token>` to every request
2. **Token refresh** — on a 401, automatically calls `/v1/auth/refresh`, stores the new token, and retries the original request
3. **Queue pattern** — if multiple requests 401 at the same time, only one refresh happens; the rest wait

```
Request → prepareHeaders (attach token) → API → 401?
                                                  ↓
                                         isRefreshing?
                                           Yes → queue the request, wait
                                           No  → call /refresh, update cookie,
                                                 flush queue, retry all
```

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

Why go through the Next.js API route instead of using `Cookies.set()` directly? So the cookie attributes (secure, sameSite, maxAge) are set server-side and consistently — `js-cookie` on the client can't set `maxAge` in seconds, and its `expires` is always in days.

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

Without the queue, A, B, and C would each call `/refresh`, rotating the token 3 times and invalidating the first two.

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

The `!from.startsWith("/auth")` guard prevents redirect loops — if someone was redirected from an auth page itself, they get the role default instead.

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

## 12. Real-Time with Socket.IO

The backend exposes two Socket.IO namespaces:

| Namespace | Purpose |
|---|---|
| `/messaging` | DM conversations + event chat rooms |
| `/notifications` | Per-user real-time notifications |

### Why Socket.IO, not raw WebSocket?

Socket.IO adds on top of WebSocket:
- Automatic reconnection
- Room management (server-side groups)
- Named events (`.emit("join:dm", data)` vs parsing JSON manually)
- Fallback to HTTP long-polling if WebSocket is blocked

The earlier implementation used native `WebSocket` with JSON-wrapped events — this was fundamentally wrong for a Socket.IO backend.

### The `useSocket` hook

```ts
// src/hooks/useSocket.ts
export function useSocket(namespace: "messaging" | "notifications", { enabled = true } = {}) {
  const [status, setStatus] = useState<SocketStatus>("disconnected");
  const socketRef = useRef<Socket | null>(null);

  useEffect(() => {
    if (!enabled) return;
    const token = Cookies.get("accessToken");
    if (!token) { setStatus("error"); return; }

    const socket = io(`${SOCKET_BASE}/${namespace}`, {
      auth: { token },          // ← sent in the handshake, not a query param
      transports: ["websocket"],
    });
    socketRef.current = socket;

    socket.on("connect", () => setStatus("connected"));
    socket.on("disconnect", () => setStatus("disconnected"));

    return () => { socket.disconnect(); socketRef.current = null; };
  }, [namespace, enabled]);

  return { socketRef, status, isConnected: status === "connected" };
}
```

**Key design decisions:**
- `socketRef` is a `useRef` (not `useState`) so the socket instance doesn't cause re-renders. `status` is `useState` so components can react when connection state changes.
- Auth is via `auth: { token }` in the handshake — this is what the Socket.IO server reads. Query params (the old approach `?token=...`) are less secure and non-standard.

### Registering event handlers

There are two approaches. The first looks sensible but has a subtle flaw. The second is correct.

#### ❌ Approach 1 — Guard with `isConnected` (has a race condition)

```tsx
const { socketRef, isConnected, status } = useSocket("messaging");

useEffect(() => {
  if (!isConnected) return;      // ← "only run if connected"
  const socket = socketRef.current;
  if (!socket) return;

  socket.emit("join:event-chat", { eventId, section: "PRE_EVENT" });

  const handleMessage = (msg: ChatMessage) => {
    setMessages(prev => [...prev, msg]);
  };
  socket.on("new:event-chat", handleMessage);

  return () => {
    socket.off("new:event-chat", handleMessage);
  };
}, [isConnected, status, eventId, socketRef]);
```

**Why this seems to work**: `isConnected` is React state. When the socket connects, `setStatus("connected")` fires → React re-renders → `isConnected` becomes `true` → the effect re-runs and emits `join:event-chat`.

**Why it sometimes doesn't work**: `isConnected` changing from `false` to `true` is a React state update. React may batch that update with other renders, or the timing between the socket's internal connect event and React's re-render cycle may not align. If the effect's re-run is delayed or missed, `join:event-chat` is never emitted and the user is in the chat screen but the server never put them in the room — messages arrive for the other person but not for this user.

This produced the symptom: "messages work sometimes, not others, the socket status shows `connected` but messages don't come through."

#### ✅ Approach 2 — Listen on the socket's own `"connect"` event (correct)

```tsx
const { socketRef } = useSocket("messaging");

useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  // joinRoom is called every time the socket connects (including reconnects)
  const joinRoom = () => {
    socket.emit("join:event-chat", { eventId, section: "PRE_EVENT" });
  };

  const handleMessage = (msg: ChatMessage) => {
    setMessages(prev => [...prev, msg]);
  };

  // Register the join as a handler for the socket's "connect" event
  socket.on("connect", joinRoom);
  socket.on("new:event-chat", handleMessage);

  // If the socket was ALREADY connected when this effect ran,
  // "connect" won't fire again — so call joinRoom() immediately
  if (socket.connected) {
    joinRoom();
  }

  return () => {
    socket.off("connect", joinRoom);
    socket.off("new:event-chat", handleMessage);
  };
}, [eventId]);  // no need for isConnected/status in deps — we use events now
```

**Why this works**: `socket.on("connect", joinRoom)` registers `joinRoom` as a listener inside **socket.io's own event system**, not React's. When the socket successfully connects, socket.io fires this event synchronously and `joinRoom` runs immediately — no waiting for React to re-render and re-run an effect. The `if (socket.connected)` fallback handles the case where the socket connected before this effect even ran (both `useSocket`'s effect and this effect run after the same render — if the connection is instant, `connected` is already `true`).

**Bonus — reconnects are free**: If the network drops and the socket reconnects, socket.io fires `"connect"` again. `joinRoom` runs again automatically. The old `isConnected` approach would also handle this via `false → true`, but the event-driven approach is guaranteed to work even if React batching delays the state update.

`socket.on("new:event-chat", handleMessage)` registers a passive listener. It doesn't fire anything to the server — it just waits. Socket.io keeps this listener alive across disconnect/reconnect cycles. You don't need to re-register it on reconnect.

### Enum values matter

The backend uses uppercase enums. The UI uses readable strings. Map them explicitly:

```ts
const SECTION_KEY = {
  "pre-event":  "PRE_EVENT",
  "during":     "DURING_EVENT",
  "post-event": "POST_EVENT",
} as const;

// Wrong ❌
socket.emit("join:event-chat", { section: "pre-event" });

// Right ✅
socket.emit("join:event-chat", { section: SECTION_KEY[activeSection] });
```

---

## 13. Payment Integration Pattern

### Why redirect-based, not widget-based

The original implementation used Juicyway's inline widget (a JS popup). Ercaspay uses a full redirect to a hosted payment page. The hosted approach is:
- More secure (card details never touch your app)
- PCI-compliant by default
- Works across all devices without JS compatibility issues

### The complete flow

```
1. User clicks "Pay & Publish"

2. POST /v1/organizer-payments/plan/initiate
   Body: { eventId, planType, couponCode? }
   Response: { paymentId, checkoutUrl, status, expiresAt }

3. Check status:
   - "COMPLETED" or checkoutUrl is null → coupon covered full cost, show success
   - "PENDING" → redirect: window.location.href = checkoutUrl

4. User pays on Ercaspay's page

5. Ercaspay redirects user back to:
   {FRONTEND_URL}/organizer/payment/verify?paymentId=<id>

6. Verify page polls GET /v1/organizer-payments/verify/:paymentId
   every 2 seconds, up to 10 attempts

7. Status:
   - "completed"  → show success, auto-redirect to /dashboard after 3s
   - "failed"     → show error, offer retry
   - "pending"    → keep polling
   - 10 attempts exhausted → show timeout message + "Check again" button
```

### The retry button bug (and the fix)

A subtle bug: when the polling times out and you click "Check again", the `useEffect` won't re-run because its dependency (`paymentId`) hasn't changed. Fix: add a `retryKey` state to the dependency array.

```tsx
const [retryKey, setRetryKey] = useState(0);

useEffect(() => {
  // polling logic
}, [paymentId, verifyPayment, retryKey]); // retryKey makes this re-trigger

// In the "Check again" button:
onClick={() => {
  attemptRef.current = 0;
  setPollState("polling");
  setRetryKey(k => k + 1);  // ← triggers the effect
}}
```

### Free publish path

When a coupon covers 100% of the cost, the backend returns `{ status: "COMPLETED", checkoutUrl: null }` immediately. The frontend must handle this without redirecting:

```tsx
const { status, checkoutUrl } = res.data;
if (status === "COMPLETED" || !checkoutUrl) {
  toast.success("Event published!");
  return;
}
window.location.href = checkoutUrl;
```

---

## 14. Forms — react-hook-form + zod

### Why react-hook-form?

The native `<form>` with `useState` for every field is verbose and re-renders on every keystroke. `react-hook-form` uses uncontrolled inputs internally — it only re-renders when validation state changes.

### Basic setup

```tsx
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";

const schema = z.object({
  email: z.string().email({ message: "Invalid email" }),
  password: z.string().min(8, { message: "At least 8 characters" }),
});

type FormValues = z.infer<typeof schema>;  // ← derive type from schema

function LoginForm() {
  const form = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { email: "", password: "" },
  });

  const onSubmit = async (values: FormValues) => {
    // values is fully typed and validated
    await login(values);
  };

  return (
    <form onSubmit={form.handleSubmit(onSubmit)}>
      <input {...form.register("email")} />
      {form.formState.errors.email && (
        <p>{form.formState.errors.email.message}</p>
      )}
      <button type="submit">Login</button>
    </form>
  );
}
```

### With shadcn/ui Form components

shadcn provides `Form`, `FormField`, `FormItem`, `FormLabel`, `FormControl`, `FormMessage` that wire into react-hook-form automatically:

```tsx
<Form {...form}>
  <form onSubmit={form.handleSubmit(onSubmit)}>
    <FormField
      control={form.control}
      name="email"
      render={({ field }) => (
        <FormItem>
          <FormLabel>Email</FormLabel>
          <FormControl>
            <Input {...field} />
          </FormControl>
          <FormMessage />  {/* auto-shows validation error */}
        </FormItem>
      )}
    />
  </form>
</Form>
```

### Zod schema tips

```ts
// Optional fields
z.string().optional()

// With transformation
z.string().trim().toLowerCase().email()

// Nested objects
z.object({
  address: z.object({
    city: z.string(),
    country: z.string(),
  }),
})

// Arrays
z.array(z.object({ tierId: z.string(), quantity: z.number().int().min(1) }))

// Conditional validation
z.object({
  hasTickets: z.boolean(),
  ticketPrice: z.number().optional(),
}).refine(
  (data) => !data.hasTickets || data.ticketPrice !== undefined,
  { message: "Price required when selling tickets", path: ["ticketPrice"] }
)
```

---

## 15. UI Layer — shadcn/ui + Tailwind

### What shadcn/ui is (and is not)

shadcn/ui is **not** an npm package. It's a collection of copy-paste components built on Radix UI primitives and styled with Tailwind. When you run `npx shadcn add button`, it copies `src/components/ui/button.tsx` into your project.

This means:
- You own the component — edit it however you like
- No version lock-in
- The component is Radix UI under the hood (fully accessible, keyboard-navigable)

### `cn()` — the utility you'll use everywhere

```ts
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

`clsx` handles conditionals. `twMerge` resolves Tailwind conflicts (e.g. `"p-4 p-2"` → `"p-2"`).

```tsx
<div className={cn(
  "rounded-xl border p-3",                    // always
  selected && "border-primary bg-primary/5",  // conditional
  className                                   // override from props
)} />
```

### Tailwind v4 (used in this project)

Tailwind v4 is configured via CSS, not `tailwind.config.js`:

```css
/* globals.css */
@import "tailwindcss";
@import "tw-animate-css";
```

Custom variables are defined in `@layer base` as CSS custom properties and referenced as Tailwind utilities.

### Component patterns from this project

**Skeleton loading:**
```tsx
if (isLoading) return <Skeleton className="h-16 w-full rounded-xl" />;
```

**Conditional badge:**
```tsx
<Badge className={cn(
  "text-xs",
  status === "PUBLISHED" ? "bg-green-500/10 text-green-600" : "bg-amber-500/10 text-amber-600"
)}>
  {status}
</Badge>
```

**Toast notifications** (via sonner):
```tsx
import { toast } from "sonner";

toast.success("Event published!");
toast.error("Payment failed. Try again.");
```

---

## 16. Fonts, Images, and Scripts

### Fonts — `next/font`

```ts
// src/app/layout.tsx
import { Nunito_Sans } from "next/font/google";

const nunitoSans = Nunito_Sans({
  weight: ["400", "600", "700"],
  variable: "--font-nunito-sans",
  subsets: ["latin"],
});
```

`next/font` downloads the font at build time and self-hosts it. No request to Google Fonts at runtime = better privacy and performance. The `variable` option creates a CSS custom property, used as `font-[--font-nunito-sans]` in Tailwind.

### Images — `next/image`

```tsx
import Image from "next/image";

<Image
  src="https://res.cloudinary.com/..."
  alt="Event banner"
  width={800}
  height={400}
  className="rounded-xl object-cover"
/>
```

`next/image` automatically:
- Lazy-loads (off-screen images don't load until near the viewport)
- Resizes to the needed dimensions
- Converts to WebP
- Prevents Cumulative Layout Shift (CLS) via `width`/`height`

External domains must be whitelisted in `next.config.ts`:

```ts
images: {
  remotePatterns: [{ protocol: "https", hostname: "res.cloudinary.com" }],
}
```

> This project has `unoptimized: true` — skipping image optimisation for faster builds. Remove this in production for real performance gains.

### Scripts — `next/script`

```tsx
import Script from "next/script";

// Load before any page rendering (blocks)
<Script src="https://..." strategy="beforeInteractive" />

// Load after page is interactive (default, good for analytics)
<Script src="https://..." strategy="afterInteractive" />

// Load during browser idle time
<Script src="https://..." strategy="lazyOnload" />
```

This project loads Google Maps and the old Juicyway script as `beforeInteractive` because they need to be available immediately. Analytics (Google Tag Manager) is `afterInteractive`.

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

## 19. Scaling Patterns

### Split RTK Query APIs by domain

Each API file in this project covers one domain (`eventApi.ts`, `paymentApi.ts`, `messagingApi.ts`). This keeps files manageable and allows independent cache invalidation. Never put everything in one giant `api.ts`.

### Centralise error handling

All API errors flow through `baseQueryWithReauth`. Add global error handling there instead of duplicating `try/catch` everywhere:

```ts
// In baseQueryWithReauth — handle 403 globally
if (result.error?.status === 403) {
  toast.error("You don't have permission to do that.");
}
```

### Environment variables

Next.js has two types:

| Variable | Accessible |
|---|---|
| `NEXT_PUBLIC_*` | Browser + server. Baked into the client bundle at build time. |
| Everything else | Server only. Never exposed to the browser. |

```ts
// Safe to use in browser code
const apiUrl = process.env.NEXT_PUBLIC_API_URL;

// Server-only (API routes, Server Components)
const secretKey = process.env.ERCASPAY_SECRET_KEY;
```

Never put secrets in `NEXT_PUBLIC_` variables — they'll appear in the compiled JavaScript.

### Avoid prop drilling with context or Redux

When state needs to travel more than 2-3 levels, put it in Redux or a React Context instead of threading it through props:

```tsx
// Instead of: <A eventId={eventId}><B eventId={eventId}><C eventId={eventId} /></B></A>
// Use: useSelector or useContext inside C directly
```

### Debounce user inputs

Heavy operations (search, map panning, canvas manipulation) should be debounced:

```tsx
import { useDebouncedCallback } from "use-debounce";

const handleSearch = useDebouncedCallback((value: string) => {
  setQuery(value);
}, 300);  // wait 300ms after user stops typing
```

This project includes `use-debounce` — use it anywhere you're calling APIs or doing expensive work on keystrokes.

### Socket.IO reconnection

When a user's network drops and reconnects, Socket.IO auto-reconnects the socket. But **room membership is not preserved** — you must re-join. Always put your `socket.emit("join:*", ...)` inside the effect that depends on `isConnected`, so it fires again after every reconnection.

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

This project **does** have middleware at `src/proxy.ts` — see section 23 for how it works. Auth guards run server-side before any page renders.

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

An alternative to RTK Query. Better suited when you don't need Redux for local state — lighter and simpler API. RTK Query is the right choice when you already have Redux in the project (like here).

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

Webhook routes are called by Ercaspay's servers, not by your users. They don't have your JWT. Don't put them behind `baseQueryWithReauth`. They're public routes secured by HMAC signature verification on the backend.

### 7. Forgetting `?from=` on auth redirects

Any time your code redirects to `/auth/login`, include the current path. The user expects to land back where they were after logging in.

```ts
// ❌
window.location.href = "/auth/login";

// ✅
const from = encodeURIComponent(window.location.pathname + window.location.search);
window.location.href = `/auth/login?from=${from}`;
```

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

### Most-used RTK Query patterns

```ts
// Query (read)
const { data, isLoading, isError, refetch } = useGetSomethingQuery(arg);

// Lazy query (on demand)
const [trigger, { data, isLoading }] = useLazyGetSomethingQuery();
await trigger(arg).unwrap();

// Mutation (write)
const [mutate, { isLoading }] = useSomeMutation();
await mutate(body).unwrap();
```

### Most-used Redux patterns

```ts
const value = useSelector((state: RootState) => state.sliceName.field);
const dispatch = useDispatch();
dispatch(someAction(payload));
```

### Socket.IO pattern

```tsx
const { socketRef, isConnected } = useSocket("messaging");

useEffect(() => {
  if (!isConnected) return;
  const socket = socketRef.current!;
  socket.emit("join:event-chat", { eventId, section: "PRE_EVENT" });
  const handler = (msg) => setMessages(prev => [...prev, msg]);
  socket.on("new:event-chat", handler);
  return () => socket.off("new:event-chat", handler);
}, [isConnected, eventId, socketRef]);
```

### Auth token access

```ts
import Cookies from "js-cookie";
const accessToken = Cookies.get("accessToken");
const refreshToken = Cookies.get("refreshToken");
```

---

## 22. Presigned Upload URLs — Streaming Files Directly to Storage

### The problem with the old approach

The original event creation sent files through the NestJS server as `multipart/form-data`:

```
Browser ──── POST (FormData, 200MB video) ──→ NestJS ──→ MinIO
```

Every byte of the file occupied NestJS process memory. A 350MB video would:
- Exhaust server memory on concurrent uploads (OOM kills)
- Hit Nginx/NestJS payload size limits
- Block the event loop for seconds

### The presigned URL architecture

The backend generates a short-lived signed URL that authorises the browser to write directly to MinIO:

```
Browser ─── POST /upload-intent ──→ NestJS (tiny JSON, fast)
Browser ←── { uploadUrl, fileUrl } ── NestJS
Browser ─────── PUT (binary) ──────→ MinIO  (NestJS never sees the file)
Browser ─── POST /v1/events (JSON) → NestJS  (fileUrl is now a plain string)
```

### Step A — request the presigned URL

```ts
// eventApi.ts
uploadIntent: builder.mutation<
  { success: boolean; data: { uploadUrl: string; fileUrl: string } },
  { filename: string; contentType: string; folder: string }
>({
  query: (body) => ({
    url: "/v1/events/upload-intent",
    method: "POST",
    body,
  }),
}),
```

```ts
const intent = await uploadIntent({
  filename: file.name,
  contentType: file.type,  // e.g. "video/mp4"
  folder: "events",
}).unwrap();

// intent.data.uploadUrl — sign PUT to MinIO
// intent.data.fileUrl   — the final CDN URL to store in the database
```

### Step B — stream the binary directly to storage

`fetch` cannot report upload progress. Use `XMLHttpRequest`:

```ts
const uploadFile = (
  file: File,
  uploadUrl: string,
  onProgress?: (pct: number) => void
): Promise<void> =>
  new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("PUT", uploadUrl);
    xhr.setRequestHeader("Content-Type", file.type); // must match contentType from Step A

    if (onProgress) {
      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable)
          onProgress(Math.round((e.loaded * 100) / e.total));
      };
    }

    xhr.onload = () =>
      xhr.status >= 200 && xhr.status < 300
        ? resolve()
        : reject(new Error(`Upload failed: ${xhr.status}`));
    xhr.onerror = () => reject(new Error("Upload network error"));
    xhr.send(file);
  });
```

> **Why XHR and not fetch?** `fetch` only has `response.body` (a readable stream for downloads). `XMLHttpRequest.upload` exposes progress events for uploads. There is no native upload progress API in the Fetch standard as of 2026.

### Step C — submit plain JSON

Once both uploads resolve, the event body is clean text:

```ts
const body = {
  name: "Tech Summit 2026",
  mode: "ONSITE",
  flierUrl: "https://cdn.nextvibe.com/events/17164-flier.jpg",    // from Step A
  promoVideoUrl: "https://cdn.nextvibe.com/events/17164-promo.mp4",
};

await createEvent(body).unwrap();
```

The backend no longer needs `FileFieldsInterceptor` — it just receives a JSON object.

### Showing upload progress in the UI

```tsx
const [uploadProgress, setUploadProgress] = useState<number | null>(null);

// In onSubmit:
setUploadProgress(0);
await uploadFile(file, intent.data.uploadUrl, setUploadProgress);
setUploadProgress(null);

// In JSX:
{uploadProgress !== null && (
  <div className="space-y-1">
    <div className="flex justify-between text-xs text-muted-foreground">
      <span>Uploading video…</span>
      <span>{uploadProgress}%</span>
    </div>
    <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
      <div
        className="h-full bg-primary transition-all duration-150"
        style={{ width: `${uploadProgress}%` }}
      />
    </div>
  </div>
)}
```

The submit button should be `disabled={isLoading || uploadProgress !== null}` so the user can't double-submit while the upload is in progress.

### Full onSubmit flow

```ts
const onSubmit = async (values: FormValues) => {
  try {
    let flierUrl: string | undefined;
    let promoVideoUrl: string | undefined;

    if (values.flier) {
      const intent = await uploadIntent({
        filename: values.flier.name,
        contentType: values.flier.type,
        folder: "events",
      }).unwrap();
      await uploadFile(values.flier, intent.data.uploadUrl);
      flierUrl = intent.data.fileUrl;
    }

    if (values.promoVideo) {
      setUploadProgress(0);
      const intent = await uploadIntent({
        filename: values.promoVideo.name,
        contentType: values.promoVideo.type,
        folder: "events",
      }).unwrap();
      await uploadFile(values.promoVideo, intent.data.uploadUrl, setUploadProgress);
      promoVideoUrl = intent.data.fileUrl;
      setUploadProgress(null);
    }

    await createEvent({
      name: values.name,
      mode: values.eventMode,
      ...(flierUrl && { flierUrl }),
      ...(promoVideoUrl && { promoVideoUrl }),
    }).unwrap();

  } catch (err: any) {
    setUploadProgress(null);
    toast.error(err?.data?.message ?? err?.message ?? "Failed to create event");
  }
};
```

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

This is more efficient than the client-side queue pattern — the page receives a fresh token in its very first request and never gets a 401 at all.

### The `?from=` requirement

Every redirect to `/auth/login` must include the current path so the user lands back where they were after logging in:

```ts
// ❌ Bad — user loses context
return NextResponse.redirect(new URL("/auth/login", req.url));

// ✅ Good
const from = encodeURIComponent(req.nextUrl.pathname + req.nextUrl.search);
return NextResponse.redirect(new URL(`/auth/login?from=${from}`, req.url));
```

The login page reads `searchParams.get("from")` and calls `router.push(from)` after a successful login.

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

This allows existing admin sessions (that only have `admin_accessToken`) to access non-admin pages without requiring a re-login.

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

---

## 26. Discriminated AI Responses — Handling Type-Specific Shapes

### The problem with a single schema

The AI game generator returns different shapes depending on the game type. The old code used a single mapping and tried to find the correct answer by string-matching:

```ts
// Old approach — fragile
const correctIdx = options.findIndex(
  (o) => o.toLowerCase().trim() === correctAnswerStr.toLowerCase().trim()
);
```

If the AI phrased the answer slightly differently from the option text, the match failed silently and `correctIdx` defaulted to `0` — wrong answer selected.

### The new backend — per-type schemas

The backend now returns clean, type-specific shapes:

| Game type | `options` | `correctAnswerIndex` | `clue` | `correctAnswer` |
|---|---|---|---|---|
| `TRIVIA` | 4 items | 0–3 (the right answer) | — | — |
| `TWO_TRUTHS_ONE_LIE` | 3 items | index of the **lie** | — | — |
| `WORD_PUZZLE` | absent | absent | hint string | exact answer string |
| `THIS_OR_THAT` | 2 items | absent (opinion poll) | — | — |

### The correct mapping pattern — branch per type

```ts
if (gameType === "word-puzzle") {
  return {
    ...base,
    question: q.clue ?? q.text ?? "",
    clue: q.clue ?? q.text ?? "",
    correctAnswer: q.correctAnswer ?? q.answer ?? "",
    options: undefined,
    correctIndex: undefined,
  };
}

if (gameType === "two-truths") {
  const options: string[] = q.options ?? [];
  // Backend tells us exactly which index is the lie
  const lieIndex = q.correctAnswerIndex ??
    options.findIndex(o => o.toLowerCase() === (q.correctAnswer ?? "").toLowerCase());
  return {
    ...base,
    question: q.text ?? q.question ?? "",
    options,
    correctIndex: lieIndex >= 0 ? lieIndex : 0,
    correctAnswer: options[lieIndex >= 0 ? lieIndex : 0] ?? "",
  };
}

if (gameType === "this-or-that") {
  // Opinion poll — there is no correct answer
  return {
    ...base,
    question: q.text ?? q.question ?? "",
    options: q.options ?? [],
    correctIndex: undefined,
    correctAnswer: undefined,
  };
}

// TRIVIA — correctAnswerIndex is definitive
const options: string[] = q.options ?? [];
const correctIdx = q.correctAnswerIndex >= 0 ? q.correctAnswerIndex : 0;
return {
  ...base,
  question: q.text ?? q.question ?? "",
  options,
  correctIndex: correctIdx,
  correctAnswer: options[correctIdx] ?? "",
};
```

### Key lesson: prefer index over string matching

When a backend returns a numeric index (`correctAnswerIndex: 2`), use it directly. String matching is a fragile fallback — keep it only for backwards compatibility with old response shapes, and always prefer the index:

```ts
const correctIdx =
  q.correctAnswerIndex ??           // new backend: use directly
  options.findIndex(o => ...);      // old backend: fall back to string match
```

---

## 27. Debugging Real-World Production Issues

These are patterns that came up during active development of this project. Each one is a category of bug you will encounter.

### Dead code that looks live

`src/proxy.ts` exports `export const config = { matcher: [...] }`. This is a Next.js/Turbopack convention — the file was compiled as middleware because of this export shape, even though it's not named `middleware.ts`. The bugs inside it (no `?from=`, admin cookie not checked) were real and silent.

**Lesson**: When debugging redirect issues, always search for ALL places that call `redirect`, `router.push`, and `window.location.href`. Don't assume a file isn't running just because it has an unusual name.

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

**Lesson**: When a backend changes its expected content type, the frontend must change too. Check the `Content-Type` header in devtools whenever a create/update flow breaks.

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

**Lesson**: If a `useEffect` isn't re-running when you expect it to, the issue is almost always its dependency array. Add a counter state (`retryKey`, `refreshKey`, `key`) to its deps when you need to force a re-run without changing the actual data.

---

## Updated Quick Reference

### Presigned upload flow

```ts
// 1. Get permission
const intent = await uploadIntent({ filename, contentType, folder }).unwrap();

// 2. Stream to storage (with progress)
await new Promise((resolve, reject) => {
  const xhr = new XMLHttpRequest();
  xhr.open("PUT", intent.data.uploadUrl);
  xhr.setRequestHeader("Content-Type", file.type);
  xhr.upload.onprogress = (e) => setProgress(Math.round(e.loaded * 100 / e.total));
  xhr.onload = () => resolve();
  xhr.onerror = () => reject();
  xhr.send(file);
});

// 3. Submit JSON
await createEvent({ flierUrl: intent.data.fileUrl, ... }).unwrap();
```

### Middleware redirect with `?from=`

```ts
const from = encodeURIComponent(req.nextUrl.pathname + req.nextUrl.search);
return NextResponse.redirect(new URL(`/auth/login?from=${from}`, req.url));
```

### `useSearchParams()` page wrapper

```tsx
export default function Page() {
  return (
    <Suspense fallback={<LoadingState />}>
      <PageInner />  {/* useSearchParams() lives here */}
    </Suspense>
  );
}
```

### Admin token fallback (both middleware and baseQuery)

```ts
const accessToken =
  Cookies.get("accessToken") ??
  Cookies.get("admin_accessToken");  // admin users can visit non-admin pages
```

---

---

## 28. Universal Error Handler — Full Implementation

A single function that accepts any `unknown` error and returns a human-readable string. Used everywhere a `catch` block needs to show a message.

### Why one central handler?

Without it, every `catch` block has its own ad-hoc logic:
```ts
// Scattered everywhere — inconsistent, hard to maintain
toast.error(err?.data?.message ?? err?.message ?? "Something went wrong");
```

A central handler means: fix the logic in one place, every caller benefits.

### Full implementation (`src/utils/errorHandler.ts`)

```ts
import axios, { AxiosError } from "axios";
import { ZodError } from "zod";

// HTTP status codes → user-friendly messages
const HTTP_STATUS_MESSAGES: Record<number, string> = {
  400: "Bad request. Please check your input.",
  401: "You are not authenticated. Please log in.",
  403: "You do not have permission to perform this action.",
  404: "The requested resource was not found.",
  405: "This action is not allowed.",
  408: "The request timed out. Please try again.",
  409: "A conflict occurred. The resource may already exist.",
  410: "This resource no longer exists.",
  422: "Validation failed. Please check your input.",
  429: "Too many requests. Please slow down and try again.",
  500: "An internal server error occurred. Please try again later.",
  502: "Bad gateway. The server is temporarily unavailable.",
  503: "Service unavailable. Please try again later.",
  504: "Gateway timeout. The server took too long to respond.",
};

// Walks common API response shapes to find a human-readable message.
function extractMessage(data: unknown): string | null {
  if (typeof data === "string" && data) return data;
  if (!data || typeof data !== "object") return null;
  const d = data as Record<string, any>;

  if (typeof d.message === "string" && d.message) return d.message;
  if (typeof d.error === "string" && d.error) return d.error;
  // { error: { message } } — RTK Query / this project's backend shape
  if (d.error && typeof d.error === "object") {
    const nested = d.error as Record<string, any>;
    if (typeof nested.message === "string" && nested.message) return nested.message;
  }
  // { errors: [] } — validation arrays
  if (Array.isArray(d.errors) && d.errors.length > 0) {
    const first = d.errors[0];
    if (typeof first === "string") return first;
    if (typeof first?.message === "string") return first.message;
    if (typeof first?.msg === "string") return first.msg;
  }
  if (typeof d.detail === "string" && d.detail) return d.detail;       // FastAPI / DRF
  if (typeof d.details === "string" && d.details) return d.details;
  if (typeof d.err === "string" && d.err) return d.err;
  if (typeof d.statusMessage === "string" && d.statusMessage) return d.statusMessage; // Nuxt/H3
  return null;
}

// Fire-and-forget log to /api/log-error. Never throws, never blocks.
function fireLog(message: string, error: unknown): void {
  if (typeof fetch === "undefined") return;
  fetch("/api/log-error", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      context: error instanceof Error
        ? { name: error.name, stack: error.stack }
        : undefined,
    }),
  }).catch(() => {});
}

// Inner detection — pure sync, all branches return a string.
function detectMessage(error: unknown): string {
  try {
    // ── RTK Query: { status, data } ─────────────────────────────────────────
    if (error !== null && typeof error === "object" && "status" in error && "data" in error) {
      const e = error as { status: number | string; data: unknown; error?: string };
      const extracted = extractMessage(e.data);
      if (extracted) return extracted;
      const status = typeof e.status === "number" ? e.status : null;
      if (status && HTTP_STATUS_MESSAGES[status]) return HTTP_STATUS_MESSAGES[status];
      if (typeof e.error === "string" && e.error) return e.error; // FETCH_ERROR
      if (e.status === "PARSING_ERROR") return "Failed to parse server response.";
      if (e.status === "TIMEOUT_ERROR") return "Request timed out. Please try again.";
      return "Request failed. Please try again.";
    }

    // ── Axios ────────────────────────────────────────────────────────────────
    if (axios.isAxiosError(error)) {
      const e = error as AxiosError<unknown>;
      if (e.response) {
        const extracted = extractMessage(e.response.data);
        if (extracted) return extracted;
        return HTTP_STATUS_MESSAGES[e.response.status] ?? `Request failed with status ${e.response.status}.`;
      }
      if (e.code === "ECONNABORTED" || e.message.toLowerCase().includes("timeout"))
        return "Request timed out. Please try again.";
      if (e.code === "ERR_NETWORK") return "Network error. Please check your connection.";
      if (e.code === "ERR_CANCELED") return "Request was cancelled.";
      if (e.request) return "No response from the server. Please check your connection.";
      return e.message || "An unknown network error occurred.";
    }

    // ── Zod ──────────────────────────────────────────────────────────────────
    if (error instanceof ZodError) {
      const first = error.issues?.[0];
      if (first?.message) return first.message;
      return "Validation failed. Please check your input.";
    }

    // ── DOM exceptions (AbortError, QuotaExceededError, etc.) ────────────────
    if (error instanceof DOMException) {
      if (error.name === "AbortError") return "Request was cancelled.";
      if (error.name === "QuotaExceededError") return "Storage quota exceeded.";
      if (error.name === "NotAllowedError") return "Permission denied.";
      return error.message || "A browser error occurred.";
    }

    // ── TypeError (fetch failures, network errors) ───────────────────────────
    if (error instanceof TypeError) {
      const msg = error.message.toLowerCase();
      if (msg.includes("failed to fetch") || msg.includes("fetch"))
        return "A network error occurred. Please check your connection.";
      if (msg.includes("networkerror")) return "Network error. Please try again.";
      if (msg.includes("load")) return "Failed to load the resource. Please try again.";
    }

    // ── Generic Error ────────────────────────────────────────────────────────
    if (error instanceof Error) {
      const msg = error.message.toLowerCase();
      if (msg.includes("timeout")) return "Request timed out. Please retry.";
      if (msg.includes("json") || msg.includes("parse")) return "Failed to parse the server response.";
      if (msg.includes("unauthorized") || msg.includes("unauthenticated"))
        return "You are not authenticated. Please log in.";
      if (msg.includes("forbidden")) return "You do not have permission to perform this action.";
      return error.message || "An unexpected error occurred.";
    }

    // ── Custom error-like objects ─────────────────────────────────────────────
    if (typeof error === "object" && error !== null) {
      const extracted = extractMessage(error);
      if (extracted) return extracted;
    }

    if (typeof error === "string" && error) return error;

    return "Something went wrong. Please try again later.";
  } catch {
    return "An unexpected error occurred while handling another error.";
  }
}

// Public API — checks offline first, then detects, then logs.
export function errorHandler(error: unknown): string {
  if (typeof navigator !== "undefined" && !navigator.onLine) {
    return "You are offline. Please check your internet connection.";
  }
  const message = detectMessage(error);
  fireLog(message, error);
  return message;
}
```

### Usage

```ts
} catch (err) {
  toast.error(errorHandler(err));
}
```

### What each branch covers

| Branch | Catches |
|---|---|
| `navigator.onLine` | Any error while the device is offline |
| RTK Query `{ status, data }` | All RTK Query errors including `FETCH_ERROR`, `PARSING_ERROR` |
| Axios | `AxiosError` with response, timeout, network, cancellation |
| Zod | Validation errors from form schemas |
| `DOMException` | `AbortError` (cancelled fetch/XHR), storage quota, permissions |
| `TypeError` | Native `fetch` network failures |
| `Error` | Any thrown `new Error(...)` |
| Plain object | Custom API errors thrown as objects |
| String | Errors thrown as plain strings |

---

## 29. Network Status Detection — Online / Offline

### How browsers know the connection status

The browser tracks network interface availability and exposes it in two ways:

```ts
navigator.onLine  // boolean — true if any network interface is up
```

And two window events:
```ts
window.addEventListener("online", handler);   // fires when connection is restored
window.addEventListener("offline", handler);  // fires when connection is lost
```

### Important limitation

`navigator.onLine: true` only means a network interface exists — **not** that the internet is reachable. A device connected to a WiFi router that has no upstream internet will still show `onLine: true`. The only way to confirm real connectivity is to ping a known endpoint.

### The hook — `src/hooks/useNetworkStatus.ts`

```ts
"use client";
import { useEffect, useState } from "react";
import { toast } from "sonner";

export const useNetworkStatus = () => {
  const [isOnline, setIsOnline] = useState(
    typeof window !== "undefined" ? navigator.onLine : true
  );

  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      toast.success("Connection restored", { description: "You're back online" });
    };

    const handleOffline = () => {
      setIsOnline(false);
      toast.error("No internet connection", {
        description: "Please check your network",
        duration: Infinity,  // stays until they come back online
      });
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);
    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, []);

  return { isOnline };
};
```

### The banner — `src/components/network-status-banner.tsx`

```tsx
"use client";
import { useNetworkStatus } from "@/hooks/useNetworkStatus";
import { WifiOff } from "lucide-react";

export const NetworkStatusBanner = () => {
  const { isOnline } = useNetworkStatus();
  if (isOnline) return null;

  return (
    <div className="fixed top-0 left-0 right-0 z-50 bg-red-600 text-white px-4 py-2 text-center text-sm font-medium flex items-center justify-center gap-2">
      <WifiOff className="w-4 h-4" />
      <span>No internet connection. Some features may not work.</span>
    </div>
  );
};
```

The banner renders at the very top of the screen (`fixed top-0 z-50`) and disappears automatically when the `online` event fires.

### How this ties into errorHandler

`errorHandler` checks `navigator.onLine` as its very first step. Any error thrown while the device is offline returns "You are offline…" regardless of the actual error shape — the root cause is obvious and the message is the most useful one.

### Extending to real connectivity checks (ping pattern)

```ts
async function checkRealConnectivity(): Promise<boolean> {
  try {
    await fetch("/api/healthz", { method: "HEAD", cache: "no-store" });
    return true;
  } catch {
    return false;
  }
}
```

Use this when you need to distinguish "no interface" from "interface up, internet down".

---

## 30. Error Logging — Fire-and-Forget Pattern

### The problem

`console.log` errors disappear when devtools is closed. In production, you have no visibility into what errors users are seeing.

### The pattern

**Fire-and-forget** means: start an async operation but don't `await` it. The operation runs in the background and the calling code continues immediately.

```ts
// Fire-and-forget — returns void, never blocks
function fireLog(message: string, error: unknown): void {
  fetch("/api/log-error", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message }),
  }).catch(() => {}); // swallow log failures — never let logging crash the app
  // ↑ No await — execution continues immediately
}
```

The `.catch(() => {})` at the end is critical. Without it, a failed log write would become an unhandled promise rejection.

### The API route — `src/app/api/log-error/route.ts`

```ts
import { appendFileSync, existsSync, mkdirSync, readFileSync } from "fs";
import { join } from "path";
import { NextRequest, NextResponse } from "next/server";

const LOG_DIR = join(process.cwd(), "logs");
const LOG_FILE = join(LOG_DIR, "errors.log");

// GET /api/log-error — view all logged errors in the browser
export async function GET() {
  try {
    if (!existsSync(LOG_FILE)) return NextResponse.json({ entries: [] });
    const raw = readFileSync(LOG_FILE, "utf8");
    const entries = raw
      .split("\n")
      .filter(Boolean)
      .map((line) => {
        try { return JSON.parse(line); }
        catch { return { raw: line }; }
      });
    return NextResponse.json({ total: entries.length, entries });
  } catch {
    return NextResponse.json({ error: "Could not read log file." }, { status: 500 });
  }
}

// POST /api/log-error — write a new log entry
export async function POST(req: NextRequest) {
  try {
    const { message, context } = await req.json();
    const line = JSON.stringify({
      ts: new Date().toISOString(),
      message,
      ...(context && { context }),
    });
    mkdirSync(LOG_DIR, { recursive: true });
    appendFileSync(LOG_FILE, line + "\n", "utf8"); // sync — fast for a single append
    return NextResponse.json({ ok: true });
  } catch {
    return NextResponse.json({ ok: false });
  }
}
```

### Log format

Each entry is newline-delimited JSON (NDJSON):
```
{"ts":"2026-05-22T10:23:01.123Z","message":"You are not authenticated.","context":{"name":"Error","stack":"Error: ..."}}
{"ts":"2026-05-22T10:24:15.456Z","message":"Request timed out. Please try again."}
```

Visit `/api/log-error` in the browser while the dev server is running to see all entries.

### Why `appendFileSync` and not `appendFile` (async)?

For a single log line append, the synchronous version is:
- Fast enough (microseconds for one line)
- Simpler — no `await`, no promise
- Safe — the response is only sent after the write completes, so the line is guaranteed to be written

For high-throughput production logging, use a proper log sink (Logtail, Sentry, Datadog) instead of the filesystem.

### Production caveat

Platforms like Vercel use **ephemeral filesystems** — writes to `logs/` don't survive function restarts. On such platforms, swap `appendFileSync` for a database insert or an external logging service. The `fireLog` function in `errorHandler.ts` doesn't need to change at all.

---

## 31. Immediate Upload on File Selection — UX State Machine

### The old UX (bad)

1. User picks a file → nothing visible happens
2. User fills in all other fields
3. User clicks "Create Event"
4. Only now does the upload start
5. Button shows a spinner for 30+ seconds on a large video
6. User has no idea if the upload is working

### The new UX (good)

1. User picks a file → upload starts immediately
2. Progress bar overlaid on the preview — user can see 23%... 47%... 91%... ✓
3. User fills in other fields **while upload runs in the background**
4. Submit button becomes active once upload finishes
5. Clicking Create Event is instant — URLs are already stored

### The state machine

Each file field has its own `UploadState`:

```ts
interface UploadState {
  status: "idle" | "uploading" | "done" | "error";
  progress: number;    // 0–100
  url: string | null;  // the CDN URL returned by the backend
}

const IDLE: UploadState = { status: "idle", progress: 0, url: null };
```

State transitions:
```
idle ──(file selected)──→ uploading ──(XHR done)──→ done
                                    ──(XHR error)──→ error ──(retry)──→ uploading
idle ←──────────────────────────────────────(remove)──────────────────────────
```

### The handler — called directly from onChange

```ts
const handleFlierChange = async (file: File) => {
  // 1. Set in form (for validation + preview)
  setValue("flier", file, { shouldValidate: true });

  // 2. Transition to uploading
  setFlierUpload({ status: "uploading", progress: 0, url: null });

  try {
    // 3. Get presigned URL from backend
    const intent = await uploadIntent({
      filename: file.name,
      contentType: file.type,
      folder: "events",
    }).unwrap();

    // 4. Stream to storage with live progress
    await uploadFile(file, intent.data.uploadUrl, (pct) =>
      setFlierUpload((prev) => ({ ...prev, progress: pct }))
    );

    // 5. Transition to done — store the final CDN URL
    setFlierUpload({ status: "done", progress: 100, url: intent.data.fileUrl });

  } catch {
    setFlierUpload({ status: "error", progress: 0, url: null });
    toast.error("Flyer upload failed. You can retry.");
  }
};
```

Note: the handler is called directly from `onChange` — not inside a `useEffect`. This is intentional. User action triggers upload; reactive effects would cause double-uploads when the component re-renders.

### Inline progress overlay

The file preview shows a dark overlay with spinner + progress bar while uploading:

```tsx
{flierUpload.status === "uploading" && (
  <div className="absolute inset-0 bg-black/50 flex flex-col items-center justify-center gap-3 p-6">
    <Loader2 className="h-7 w-7 text-white animate-spin" />
    <div className="w-4/5 space-y-1.5">
      <div className="flex justify-between text-white text-xs font-medium">
        <span>Uploading…</span>
        <span>{flierUpload.progress}%</span>
      </div>
      <div className="h-1.5 rounded-full bg-white/30 overflow-hidden">
        <div
          className="h-full bg-white transition-all duration-150"
          style={{ width: `${flierUpload.progress}%` }}
        />
      </div>
    </div>
  </div>
)}

{flierUpload.status === "done" && (
  <div className="absolute top-2 right-2 bg-green-500/90 backdrop-blur-sm rounded-full p-1">
    <CheckCircle2 className="h-4 w-4 text-white" />
  </div>
)}

{flierUpload.status === "error" && (
  <div className="absolute inset-0 bg-red-900/60 flex flex-col items-center justify-center gap-3">
    <AlertCircle className="h-7 w-7 text-white" />
    <p className="text-white text-sm font-medium">Upload failed</p>
    <Button type="button" size="sm" variant="secondary"
      onClick={() => handleFlierChange(flier)}>  {/* retry with same file */}
      Retry
    </Button>
  </div>
)}
```

### Submit uses stored URLs — no re-upload

```ts
const onSubmit = async (values: BasicInfoFormValues) => {
  // Guard: don't submit while uploading
  if (flierUpload.status === "uploading" || videoUpload.status === "uploading") {
    toast.warning("Please wait for uploads to finish.");
    return;
  }
  // Guard: don't submit if upload failed
  if ((values.flier && flierUpload.status === "error") ||
      (values.promoVideo && videoUpload.status === "error")) {
    toast.error("Some uploads failed. Please retry before submitting.");
    return;
  }

  const body = {
    name: values.name,
    // ...other fields
    ...(flierUpload.url && { flierUrl: flierUpload.url }),       // already uploaded
    ...(videoUpload.url && { promoVideoUrl: videoUpload.url }),  // already uploaded
  };

  await createEventMutation(body).unwrap(); // instant — just JSON
};
```

### Button state

```tsx
<Button
  type="submit"
  disabled={isLoading || anyUploading}
>
  {isLoading ? "Creating event…"
   : anyUploading ? "Uploading files…"
   : "Create Event"}
</Button>
```

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

As covered in section 25 — any component using `useSearchParams()` must be wrapped in `<Suspense>` or the build fails.

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

Suspense is for **reading** async data, not for tracking pending writes.

---

---

## 36. Socket.IO — Event-Driven Join (The isConnected Race Condition)

### Background — what is a "room"?

In Socket.IO, a **room** is a server-side group that a socket can join. When the server calls `socket.join("room-abc")`, that socket starts receiving any event the server broadcasts to `"room-abc"`. Rooms are how one-to-one DMs work: User A and User B both join the room for their conversation, and when either sends a message the server emits it to the room so both receive it.

The client tells the server "put me in this room" by emitting a named event — in this project `join:dm` for DMs and `join:event-chat` for event chats. If you forget to emit that event, or if it fails to reach the server, you never get added to the room and you never receive messages.

### The symptom

Messages would work sometimes, fail others. The socket status showed `"connected"` in the UI. The server was clearly receiving messages (the other person could see them). But the recipient's screen stayed blank. Intermittent — worked on first load, broke after navigating away and back, or after the socket reconnected.

### Why the original pattern was fragile

```ts
// ❌ Original — guards the join behind React state
useEffect(() => {
  if (!isConnected) return;   // ← "only proceed if connected"
  const socket = socketRef.current;
  if (!socket) return;

  socket.emit("join:dm", { conversationId }); // ← join the room
  socket.on("new:dm", handler);               // ← listen for messages
  return () => socket.off("new:dm", handler);

}, [isConnected, status, conversationId, socketRef]);
```

On paper, this looks fine: `isConnected` is `false` on mount (socket is still connecting), the effect bails. When the socket connects, `setStatus("connected")` fires inside `useSocket`, React re-renders, `isConnected` becomes `true`, the effect re-runs, and `join:dm` gets emitted.

The problem is that this re-run goes through **React's rendering pipeline**:

```
Socket connects (socket.io event loop)
  ↓
setStatus("connected") called inside useSocket
  ↓
React schedules a re-render (batched with other state updates)
  ↓
React commits the render
  ↓
useEffect cleanup runs (removes old listeners)
  ↓
useEffect setup runs (emits join:dm, adds new listeners)
```

Every step in that chain is a potential point of failure. React 18's concurrent rendering can batch or defer updates. The timing between step 1 (socket.io event loop) and step 6 (effect runs) is non-deterministic. If anything in between delays or skips a step — maybe the component re-renders for a different reason at the wrong moment, maybe React batches the state update together with another re-render that short-circuits the effect — `join:dm` never fires.

This is a **race condition** between socket.io's event system and React's rendering pipeline.

### The fix — use socket.io's own event system

```ts
// ✅ Event-driven — bypasses React's rendering pipeline entirely
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const joinRoom = () => {
    // This runs inside socket.io's event loop — guaranteed timing
    socket.emit("join:dm", { conversationId });
  };

  const handleNewDm = (msg: Message) => {
    setLocalMessages(prev => [...prev, msg]);
  };

  // Register joinRoom as a handler for the socket's OWN "connect" event.
  // socket.io fires this immediately when the handshake completes.
  socket.on("connect", joinRoom);
  socket.on("new:dm", handleNewDm);

  // The socket might already be connected when this effect runs
  // (both useSocket's effect and this effect run after the same render).
  // If it is, "connect" won't fire again — so join right now.
  if (socket.connected) {
    joinRoom();
  }

  return () => {
    socket.off("connect", joinRoom);
    socket.off("new:dm", handleNewDm);
  };
}, [conversationId]);
// socketRef is a stable useRef — it never changes, so no need in deps
// isConnected / status removed — we don't need React to mediate anymore
```

**What changed and why it works:**

`socket.on("connect", joinRoom)` registers `joinRoom` as a listener inside **socket.io's own internal event emitter**. When the socket successfully handshakes with the server, socket.io fires `"connect"` synchronously in its own event loop — completely outside React's rendering cycle. `joinRoom` runs immediately. No batching, no deferred renders, no race.

`socket.on("new:dm", handleNewDm)` registers a passive listener. Socket.io keeps this alive across disconnect/reconnect cycles — you don't need to re-register it. It just sits there waiting for the server to push messages.

The `if (socket.connected)` check handles the case where `useSocket`'s effect already ran and the socket is already up by the time this effect runs. Since "connect" already fired, it won't fire again — so we call `joinRoom()` directly.

**Reconnects are free:** if the network drops and socket.io reconnects, it fires `"connect"` again. `joinRoom` emits `join:dm` again. The server adds this socket back to the room. No extra code needed.

### For passive listeners (no join emit needed)

Some namespaces put you in a room automatically based on who you are (the server reads your JWT on connect and adds you to your personal notification room). In that case there's no join event to emit — just register the listener:

```ts
// Notifications — server handles room assignment on auth
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const handler = (notif: Notification) => {
    setPendingIds(prev => new Set([...prev, notif.id]));
    refetch();
  };

  // No join needed — just listen
  // Socket.io keeps this registered across disconnects/reconnects
  socket.on("notification", handler);
  return () => socket.off("notification", handler);
}, [socketRef]);
// ❌ Don't add isConnected to deps — it's not needed and causes the same race condition
```

### Quick reference — both patterns

```ts
// ── Room-based (DMs, event chat) — must emit join ──────────────────────────
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const join = () => socket.emit("join:room", { roomId });
  const onMessage = (msg) => setMessages(prev => [...prev, msg]);

  socket.on("connect", join);     // fires on connect AND reconnect
  socket.on("new:message", onMessage);
  if (socket.connected) join();   // already connected? join right now

  return () => {
    socket.off("connect", join);
    socket.off("new:message", onMessage);
  };
}, [roomId]);

// ── Passive (notifications, server decides room) — no join needed ───────────
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const onNotif = (n) => handleNotif(n);
  socket.on("notification", onNotif);
  return () => socket.off("notification", onNotif);
}, [socketRef]);
```

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

`"error"` is the sentinel for "no token". The socket never attempts to connect.

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

## 38. Optimistic Messages — Deduplication Pattern

### The double-bubble problem

When you send a message via Socket.IO:
1. Frontend adds an optimistic bubble locally (instant feedback)
2. Server receives `send:dm`, saves it, and broadcasts `new:dm` to everyone in the room — **including the sender**
3. `handleNewDm` appends the server message as another bubble

Result: the sender sees the message twice. The server stores it once (correct), but the UI shows two bubbles.

### The fix — replace, don't append

Track optimistic messages in a `Map` keyed by body text. When `new:dm` arrives from yourself, look up the pending entry and **replace** the optimistic bubble with the real one:

```ts
// Track: body text → optimistic id
const pendingOptimisticRef = useRef<Map<string, string>>(new Map());

// On send:
const optimisticId = `opt-${Date.now()}`;
pendingOptimisticRef.current.set(body, optimisticId);
const optimistic: Message = {
  id: optimisticId,
  senderId: currentUserId,
  body,
  createdAt: new Date().toISOString(),
};
setLocalMessages(prev => [...prev, optimistic]);

// In handleNewDm:
const handleNewDm = (msg: Message) => {
  if (msg.senderId === currentUserId) {
    const optId = pendingOptimisticRef.current.get(msg.body);
    if (optId) {
      pendingOptimisticRef.current.delete(msg.body);
      // Replace the optimistic bubble with the real one (correct id + server timestamp)
      setLocalMessages(prev => prev.map(m => m.id === optId ? msg : m));
      return;
    }
  }
  // Message from the other person — just append + play sound
  setLocalMessages(prev => [...prev, msg]);
};
```

### Why a ref, not state?

`pendingOptimisticRef` is a `useRef<Map>`. It needs to be:
- **Readable inside the `new:dm` socket handler** (a closure that runs async)
- **Writable without triggering a re-render** (it's bookkeeping, not UI state)

If it were `useState`, the handler would close over a stale snapshot of the Map and the lookup would fail. Refs are mutable and always current.

### Benefits of replacement over skipping

Replacing with the real server message means:
- The message gets the real server-assigned `id` (important for dedup on future page loads)
- The timestamp becomes the server's authoritative time
- If the server modifies the body (e.g. trims it), the UI reflects that

---

## 39. Chat UI — Grouped Bubbles, Avatars, and Full-Screen Escape

### Grouped message bubbles

WhatsApp/iMessage style: consecutive messages from the same sender form a "group". The avatar appears only on the last message of each group; the bubble corners flatten on connecting sides.

```tsx
{localMessages.map((message, index) => {
  const isMine = message.senderId === currentUserId;
  const prev = localMessages[index - 1];
  const next = localMessages[index + 1];
  const isFirstInGroup = !prev || prev.senderId !== message.senderId;
  const isLastInGroup  = !next || next.senderId !== message.senderId;

  return (
    <div key={message.id} className={cn(
      "flex items-end gap-2",
      isMine ? "justify-end" : "justify-start",
      isLastInGroup && index !== localMessages.length - 1 && "mb-2",
    )}>
      {/* Fixed-width avatar column keeps all received bubbles aligned */}
      {!isMine && (
        <div className="w-7 shrink-0 self-end">
          {isLastInGroup ? (
            <Avatar className="h-7 w-7">
              <AvatarImage src={conversation.participant.avatarUrl} />
              <AvatarFallback>{conversation.participant.username?.[0]}</AvatarFallback>
            </Avatar>
          ) : null /* spacer is always rendered, avatar only on last */}
        </div>
      )}

      <div className={cn("flex flex-col max-w-[75%]", isMine && "items-end")}>
        <div className={cn(
          "px-4 py-2 text-sm rounded-2xl",
          isMine ? "bg-primary text-primary-foreground" : "bg-muted text-foreground",
          // Flatten connecting corners within a group
          isMine  && !isFirstInGroup && "rounded-tr-[6px]",
          isMine  && !isLastInGroup  && "rounded-br-[6px]",
          !isMine && !isFirstInGroup && "rounded-tl-[6px]",
          !isMine && !isLastInGroup  && "rounded-bl-[6px]",
        )}>
          {message.body}
        </div>
        {/* Timestamp only at the bottom of each group */}
        {isLastInGroup && (
          <p className="text-[10px] mt-1 px-1 text-muted-foreground">
            {formatTime(message.createdAt)}
          </p>
        )}
      </div>
    </div>
  );
})}
```

**Key insight**: the `w-7` spacer div is rendered for **every** received message, even ones that don't show the avatar. This keeps all received bubbles horizontally aligned — without it, bubbles shift left on non-avatar rows.

### `min-h-0` for scrollable flex children

A common Tailwind trap: a `flex-1 overflow-y-auto` div inside a flex column doesn't scroll.

```tsx
{/* ❌ Doesn't scroll — flex-1 grows the div but doesn't cap its height */}
<div className="flex-1 overflow-y-auto">

{/* ✅ min-h-0 overrides flex's default min-height: auto, capping the height */}
<div className="flex-1 min-h-0 overflow-y-auto">
```

**Why**: In a flex column, `flex-1` makes the child expand to fill available space. But flex items have `min-height: auto` by default, which means they can grow beyond their container to fit content. `overflow-y-auto` only activates when height is explicitly constrained. `min-h-0` overrides the default and lets the flex container actually cap the height.

### Escaping the layout chrome for full-screen views

The messages chat view needs to cover the entire viewport — no navbar, no bottom nav. Two approaches:

**Approach 1 — `fixed inset-0` with high z-index**

```tsx
<div className="fixed inset-0 z-[1100000] bg-background flex flex-col">
```

The z-index must be higher than the navbar (`z-[1000000]` in this project). Easy to mess up — if you use `z-[9999]` you get the navbar bleeding through.

**Approach 2 — Redux `setHideHeader` (recommended)**

```ts
// In the full-screen component:
const dispatch = useDispatch();
useEffect(() => {
  dispatch(setHideHeader(true));
  return () => { dispatch(setHideHeader(false)); };
}, [dispatch]);
```

The `DashboardNavbar` and `BottomNav` both read `hideHeader` from Redux and return `null` when it's true. No z-index battle. The UI components completely unmount, freeing memory and preventing any bleed-through. Used in the vibetag editor, postcard viewer, and now the chat view.

**Rule**: use `setHideHeader` when you control the navigation chrome. Use `fixed inset-0 z-[...]` only for components that render outside the normal layout tree (e.g. portals, dialogs).

---

## 40. Synthesised Notification Sounds — Web Audio API

### No files needed

Instead of shipping an audio file in `/public`, use the Web Audio API to synthesise a notification ping in code:

```ts
function playNotifSound() {
  try {
    const AudioCtx = window.AudioContext ?? (window as any).webkitAudioContext;
    if (!AudioCtx) return;
    const ctx = new AudioCtx() as AudioContext;

    const osc = ctx.createOscillator();
    const gain = ctx.createGain();
    osc.connect(gain);
    gain.connect(ctx.destination);

    // 1400 Hz → 900 Hz sweep over 120ms = a classic "ding"
    osc.type = "sine";
    osc.frequency.setValueAtTime(1400, ctx.currentTime);
    osc.frequency.exponentialRampToValueAtTime(900, ctx.currentTime + 0.12);

    // Short attack, longer decay
    gain.gain.setValueAtTime(0, ctx.currentTime);
    gain.gain.linearRampToValueAtTime(0.18, ctx.currentTime + 0.01);
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + 0.35);

    osc.start(ctx.currentTime);
    osc.stop(ctx.currentTime + 0.35);
  } catch {
    // Browsers may block AudioContext without a prior user gesture — fail silently
  }
}
```

### How Web Audio works

- `AudioContext` is the engine. Create one per sound (or reuse a persistent one).
- `OscillatorNode` generates a waveform. `type: "sine"` is smooth; `"square"` is harsher.
- `GainNode` controls volume. `gain.gain` is an `AudioParam` — you can schedule ramp animations on it using `linearRampToValueAtTime` and `exponentialRampToValueAtTime`.
- Connect nodes: `oscillator → gain → ctx.destination` (speakers).
- `start()` / `stop()` use `ctx.currentTime` (the audio clock, not wall time).

### The user gesture requirement

Browsers block `new AudioContext()` until the user has interacted with the page. In a chat app this is never a problem — the user had to tap a conversation to get to the chat screen. The `try/catch` handles the rare case where sound is blocked silently.

### When to play it

Only play for messages from the other person — never for your own sends:

```ts
const handleNewDm = (msg: Message) => {
  if (msg.senderId === currentUserId) {
    // echo of own message — dedup it, don't sound
    return;
  }
  playNotifSound();  // incoming message from other person
  setLocalMessages(prev => [...prev, msg]);
};
```

---

## 41. Real-Time Notification Badge — pendingIds vs Counter

### The double-count problem

The original notification bell used a `realtimeCount` counter:

```ts
const [realtimeCount, setRealtimeCount] = useState(0);

// On new notification:
setRealtimeCount(c => c + 1);
refetch();  // ← pulls updated list from server

// Badge:
const unreadCount = (data?.data?.meta?.unreadCount ?? 0) + realtimeCount;
```

When `refetch()` resolves, `meta.unreadCount` from the server already includes the new notification. But `realtimeCount` still holds 1. Result: the badge shows `serverCount + 1` — one too many.

### The fix — track pending IDs, subtract once fetched

```ts
const [pendingIds, setPendingIds] = useState<Set<string>>(new Set());

// On new notification:
const handleNotification = (notif: Notification) => {
  setPendingIds(prev => new Set([...prev, notif.id ?? `rt-${Date.now()}`]));
  refetch();
};

// Once REST data comes back, remove IDs that are now in the list:
useEffect(() => {
  if (!data) return;
  const fetchedIds = new Set(notifications.map(n => n.id));
  setPendingIds(prev => {
    const stillPending = new Set([...prev].filter(id => !fetchedIds.has(id)));
    return stillPending.size === prev.size ? prev : stillPending;  // avoid re-render if unchanged
  });
}, [data]);

// Badge — only count IDs not yet confirmed by the server
const unreadCount = restUnread + pendingIds.size;
```

### Why this works

- When a notification arrives, it's added to `pendingIds`. Badge increments immediately.
- `refetch()` runs. The server response includes the new notification in `meta.unreadCount`.
- The cleanup effect sees the notification's `id` in the fetched list and removes it from `pendingIds`.
- Badge = `restUnread + 0` = correct value, no double count.

### The `stillPending.size === prev.size ? prev : stillPending` optimisation

Returning the **same Set reference** when nothing changed prevents React from re-rendering. `new Set([...prev])` always creates a new object even if the contents are identical — React would see a new reference and re-render unnecessarily.

### Notification badge — full pattern

```
New notification arrives via socket
  ↓
Add id to pendingIds → badge shows +1 immediately
  ↓
refetch() — pulls updated list from server
  ↓
Server responds with new unreadCount + notification in list
  ↓
Cleanup effect: id is in fetchedIds → remove from pendingIds
  ↓
Badge = server's unreadCount + 0 (pending now empty)  ← correct
```

---

---

## 42. WebSockets from First Principles — ws, wss, and Socket.IO

If you have never touched real-time communication before, start here. This explains the whole stack from the protocol up.

### The problem HTTP has

Every HTTP request follows this pattern:

```
Browser:  "Hey server, give me the events list"
Server:   "Here you go" → closes connection
```

The server can only talk to the browser when the browser asks first. If something changes on the server (new message, new notification), the server has no way to tell the browser. The browser has to keep asking ("polling"):

```
Browser → "any new messages?" → Server: "no"
Browser → "any new messages?" → Server: "no"
Browser → "any new messages?" → Server: "yes, here's one"
```

Polling every second is wasteful — 999 out of 1000 requests get "no". Polling every 30 seconds means 30-second delays on messages.

### What WebSocket is

WebSocket is a different protocol that creates a **persistent two-way connection**:

```
Browser → Server: "I want to upgrade this HTTP connection to WebSocket"
Server:           "Agreed"
─────────────── connection stays open ───────────────
Server → Browser: "New message from Alice: hey!"   (any time)
Browser → Server: "I'm typing..."                  (any time)
Server → Browser: "Alice is also typing"           (any time)
─────────────── either side can close it ────────────
```

Once the upgrade handshake happens, either side can send data to the other at any time without waiting to be asked. This is what makes chat, live notifications, and collaborative editing possible.

### `ws://` and `wss://`

WebSocket has its own URL schemes:

| Scheme | What it is | When to use |
|---|---|---|
| `ws://` | Plain WebSocket — data travels unencrypted | Development only (`ws://localhost:3000`) |
| `wss://` | WebSocket **Secure** — encrypted with TLS (same as HTTPS) | Always in production |

The relationship mirrors HTTP/HTTPS exactly:
- `http://` → unencrypted → `https://` → encrypted
- `ws://` → unencrypted → `wss://` → encrypted

In production, using `ws://` means anyone between the browser and server (WiFi router, ISP, CDN) can read every message. Always use `wss://` in production.

You don't usually set `ws://` or `wss://` manually in this project — the Socket.IO client derives it automatically from `NEXT_PUBLIC_API_URL`. If that URL starts with `https://`, socket.io uses `wss://`. If it starts with `http://` (local dev), it uses `ws://`.

### What Socket.IO is (and how it relates to WebSocket)

Raw WebSocket is just a pipe — it sends raw bytes or strings. You have to invent your own protocol on top of it:

```js
// Raw WebSocket — you have to parse everything yourself
const ws = new WebSocket("wss://api.nextvibe.com");
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);   // hope it's JSON
  if (data.type === "new_message") { ... }
  if (data.type === "user_joined") { ... }
  // ... handle every type manually
};
ws.send(JSON.stringify({ type: "join_room", roomId: "abc" }));
```

Socket.IO wraps WebSocket (and falls back to HTTP long-polling if WebSocket is blocked) and gives you:

| Feature | Raw WebSocket | Socket.IO |
|---|---|---|
| Named events | ❌ manual JSON parsing | ✅ `socket.on("new:dm", handler)` |
| Rooms (server-side groups) | ❌ must implement yourself | ✅ built in |
| Auto reconnect | ❌ must implement yourself | ✅ built in, with backoff |
| Namespaces | ❌ must implement yourself | ✅ `/messaging`, `/notifications` |
| Auth in handshake | ❌ manual | ✅ `io(url, { auth: { token } })` |
| Fallback transports | ❌ | ✅ falls back to polling if WS blocked |

Socket.IO's "named events" are the key win for this project:

```ts
// Socket.IO — clean and readable
socket.emit("join:dm", { conversationId: "abc123" });
socket.on("new:dm", (message) => { /* ... */ });

// Equivalent raw WebSocket — verbose and fragile
ws.send(JSON.stringify({ event: "join:dm", data: { conversationId: "abc123" } }));
ws.onmessage = (e) => {
  const parsed = JSON.parse(e.data);
  if (parsed.event === "new:dm") { /* ... */ }
};
```

### The connection lifecycle

```
1. io() called
   ↓ Socket.IO tries WebSocket first (wss://)
   ↓ If blocked, falls back to HTTP long-polling

2. HTTP upgrade handshake
   Client → Server: "Upgrade: websocket"
   Server → Client: "101 Switching Protocols"
   ↓ Connection is now a persistent WebSocket

3. Socket.IO auth
   Client sends: { auth: { token } }
   Server validates JWT — if invalid, closes the connection

4. "connect" event fires on client
   → This is when it's safe to emit join:* events

5. Normal operation
   Either side can emit named events at any time

6. Disconnect (network drop, server restart, etc.)
   → Socket.IO automatically tries to reconnect (exponential backoff)
   → "connect" fires again on successful reconnect
   → Must re-emit join:* events (rooms are not persisted across connections)
```

Step 6 is why `socket.on("connect", joinRoom)` is the correct pattern — it fires at step 4 and again after every step 6 reconnect.

### How this project's `useSocket` hook works under the hood

```ts
const socket = io(`${SOCKET_BASE}/${namespace}`, {
  auth: { token },            // sent in the handshake (step 3)
  transports: ["websocket"],  // skip long-polling, go straight to WebSocket
});
```

`transports: ["websocket"]` skips Socket.IO's default "try polling first, then upgrade" behaviour. This is faster but means if WebSocket is blocked (rare in modern environments), the connection simply fails rather than falling back. Acceptable for this project.

`auth: { token }` sends the JWT during the handshake. The server reads it and can reject the connection before a single event is exchanged. This is more secure than query params (`?token=...`) which appear in server logs.

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

## 44. Conversations List — Real-Time Updates and Stale Cache

### The symptom

Two separate bugs that felt like one:

1. You open the messages page. Someone sends you a message. The list doesn't update — the last message preview and unread count stay stale until you manually refresh.
2. You open a conversation you last visited 10 minutes ago. It shows the old messages from 10 minutes ago, then a moment later jumps to the latest. Confusing.

### Why both happened

**Bug 1 — stale list:** The `Messages` component (the conversation list) used `useGetConversationsQuery()` once on mount. No socket was connected at list level. The socket only existed inside `ChatView`, and only for real-time message delivery. Nobody was listening for "new message arrived, refresh the list."

**Bug 2 — stale chat:** RTK Query caches query results. By default, `useGetMessagesQuery({ conversationId })` returns the cached result from the last time you visited that conversation and fetches a fresh copy in the background. The user sees old data first, then it updates. This is called "stale-while-revalidate" and it's the default RTK Query behaviour.

### Fix 1 — real-time list: add a socket at list level

```ts
// ❌ Before — no socket at the list level, list only updates on page refresh
const { data, isLoading, isError, refetch } = useGetConversationsQuery();
// ...no socket...
```

```ts
// ✅ After — socket connected while list is visible
const { data, isLoading, isError, refetch } = useGetConversationsQuery();
const conversations = data?.data ?? [];

// Disabled when ChatView is open — ChatView has its own socket,
// and we don't want two simultaneous connections to the same namespace.
const { socketRef: listSocketRef } = useSocket("messaging", {
  enabled: !selectedConversation,
});

useEffect(() => {
  if (selectedConversation) return;
  const socket = listSocketRef.current;
  if (!socket) return;

  // Join every conversation room so the server sends new:dm for any of them
  const joinAll = () => {
    conversations.forEach((c) => {
      socket.emit("join:dm", { conversationId: c.id });
    });
  };

  const handleNewDm = (msg: any) => {
    refetch(); // pull fresh lastMessage + unreadCount for all conversations
    // (also bump local badge — see section 45)
  };

  socket.on("connect", joinAll);
  socket.on("new:dm", handleNewDm);
  if (socket.connected) joinAll();

  return () => {
    socket.off("connect", joinAll);
    socket.off("new:dm", handleNewDm);
  };
}, [selectedConversation, listSocketRef, conversations, refetch]);
```

**Key insight:** you join ALL conversation rooms at once. The server sends `new:dm` events to each room. Joining multiple rooms from the same socket is cheap — it's just the server routing events to this socket's session.

**Why `enabled: !selectedConversation`?** When `ChatView` is open, `selectedConversation` is non-null. `ChatView` has its own `useSocket("messaging")` call. If the list also kept its socket alive, you'd have two sockets connected to the same namespace from the same user at the same time. That works, but it wastes a connection. Disabling the list socket when the chat is open means exactly one socket is active at all times.

### Fix 2 — stale chat: force fresh fetch on mount

```ts
// ❌ Before — RTK Query returns cached data first, fetches fresh in background
const { data, isLoading } = useGetMessagesQuery({ conversationId: conversation.id });
```

```ts
// ✅ After — always fetch fresh messages when opening a conversation
const { data, isLoading } = useGetMessagesQuery(
  { conversationId: conversation.id },
  { refetchOnMountOrArgChange: true }
);
```

`refetchOnMountOrArgChange: true` tells RTK Query: "every time this component mounts or the argument changes, fire a fresh request — don't serve cache." The user always sees up-to-date messages when they open a chat.

The trade-off: one extra network request per chat open. That's acceptable — messages must be fresh.

---

## 45. Per-Conversation Unread Badge — Local + Server Merge

### The problem

The `Conversation` type has an `unreadCount` field from the server. The badge showed `conversation.unreadCount`. But:

- The server count only updates after `refetch()` completes (network round-trip takes ~200–500ms)
- Some backends don't reliably track `unreadCount` per user at all
- Between the socket event and the refetch landing, there's a window where the badge shows the wrong number

### The two-layer approach

**Layer 1 — server count (authoritative):** `conversation.unreadCount` from RTK Query. Accurate after refetch.

**Layer 2 — local count (instant):** A `Record<string, number>` state that increments the moment a `new:dm` socket event arrives (if the server includes `conversationId` in the payload).

```ts
const [localUnread, setLocalUnread] = useState<Record<string, number>>({});

// In the socket handler:
const handleNewDm = (msg: any) => {
  refetch();
  const convId: string | undefined = msg?.conversationId;
  if (convId) {
    setLocalUnread((prev) => ({
      ...prev,
      [convId]: (prev[convId] ?? 0) + 1,
    }));
  }
};

// In the render, merge both:
const unread = (conversation.unreadCount ?? 0) + (localUnread[conversation.id] ?? 0);
```

### Preventing double-count

After `refetch()` lands, the server's `unreadCount` now includes the new message. If we kept the local count too, we'd show `server(1) + local(1) = 2` for a single unread. Fix: clear local entries once the server confirms them.

```ts
useEffect(() => {
  if (!conversations.length) return;
  setLocalUnread((prev) => {
    const changed = conversations.some((c) => c.unreadCount > 0 && prev[c.id]);
    if (!changed) return prev; // avoid re-render if nothing changed
    const next = { ...prev };
    conversations.forEach((c) => {
      // Server now tracks this conversation's unread — our local copy is redundant
      if (c.unreadCount > 0) delete next[c.id];
    });
    return next;
  });
}, [conversations]);
```

**The fallback:** if the server always returns 0 (backend doesn't track reads), the local count stays and the badge still works.

### Clear on open

When the user taps a conversation, clear its local count immediately — they're about to read those messages.

```ts
const handleSelectConversation = (conv: Conversation) => {
  setLocalUnread((prev) => {
    if (!prev[conv.id]) return prev; // nothing to clear, don't re-render
    const next = { ...prev };
    delete next[conv.id];
    return next;
  });
  setSelectedConversation(conv);
};
```

### Badge design (WhatsApp style)

Moved from avatar corner → right side of the row, next to the last message preview. Also bold name + bold preview text when unread.

```tsx
const unread = (conversation.unreadCount ?? 0) + (localUnread[conversation.id] ?? 0);

<Card className={cn("cursor-pointer", unread > 0 && "border-primary/30 bg-primary/5")}>
  <div className="flex items-center gap-3">
    <Avatar className="h-12 w-12 shrink-0">...</Avatar>

    <div className="flex-1 min-w-0">
      <div className="flex items-center justify-between gap-2">
        <h3 className={cn("truncate", unread > 0 ? "font-bold" : "font-semibold")}>
          {conversation.participant.username}
        </h3>
        <span className={cn("text-xs shrink-0", unread > 0 ? "text-primary font-semibold" : "text-muted-foreground")}>
          {formatTime(conversation.lastMessage?.createdAt)}
        </span>
      </div>

      <div className="flex items-center justify-between gap-2 mt-0.5">
        <p className={cn("text-sm truncate", unread > 0 ? "text-foreground font-medium" : "text-muted-foreground")}>
          {conversation.lastMessage?.body}
        </p>
        {unread > 0 && (
          <span className="shrink-0 min-w-5 h-5 rounded-full bg-primary text-primary-foreground text-[11px] font-bold flex items-center justify-center px-1.5 leading-none">
            {unread > 99 ? "99+" : unread}
          </span>
        )}
      </div>
    </div>
  </div>
</Card>
```

---

## 46. Bottom Nav Real-Time Badge — Shared Cache + Conditional Socket

### The goal

The Messages icon in the bottom nav should show a badge with the total unread count, updating in real time — even when the user is on the events page, profile page, or anywhere else.

### The shared cache trick

RTK Query caches query results globally. Every component that calls `useGetConversationsQuery()` shares the same cached data. When the messages page calls `refetch()` on a new `new:dm` event, the cache updates — and every other component reading that cache updates too, for free.

This means the bottom nav badge doesn't need its own fetch. It just reads the same cache:

```ts
const { data, refetch } = useGetConversationsQuery();
const conversations = data?.data ?? [];
const serverUnread = conversations.reduce((s, c) => s + (c.unreadCount ?? 0), 0);
```

### The gap: when not on /messages

When the user is on `/events` or `/profile`, the messages page isn't mounted, so its socket isn't active. Nobody is calling `refetch()`. The cache goes stale. The bottom nav badge doesn't update.

Fix: the bottom nav runs its own socket — but only when NOT on `/messages`, to avoid a double connection.

```ts
function useUnreadMessages(isOnMessagesPage: boolean) {
  const { data, refetch } = useGetConversationsQuery();
  const conversations = data?.data ?? [];
  const serverUnread = conversations.reduce((s, c) => s + (c.unreadCount ?? 0), 0);

  const [pendingNew, setPendingNew] = useState(false);

  // Once server confirms the count, clear the optimistic dot
  useEffect(() => {
    if (serverUnread > 0) setPendingNew(false);
  }, [serverUnread]);

  // Socket — disabled when /messages is open (that page has its own socket)
  const { socketRef } = useSocket("messaging", { enabled: !isOnMessagesPage });

  useEffect(() => {
    if (isOnMessagesPage) return;
    const socket = socketRef.current;
    if (!socket) return;

    const joinAll = () => {
      conversations.forEach((c) => socket.emit("join:dm", { conversationId: c.id }));
    };

    const handleNewDm = () => {
      setPendingNew(true); // dot appears immediately
      refetch();           // server count updates ~200ms later
    };

    socket.on("connect", joinAll);
    socket.on("new:dm", handleNewDm);
    if (socket.connected) joinAll();

    return () => {
      socket.off("connect", joinAll);
      socket.off("new:dm", handleNewDm);
    };
  }, [isOnMessagesPage, socketRef, conversations, refetch]);

  return { unread: serverUnread, pendingNew };
}
```

In the bottom nav:

```tsx
const isOnMessagesPage = pathname.startsWith("/messages");
const { unread, pendingNew } = useUnreadMessages(isOnMessagesPage);
const showBadge = unread > 0 || pendingNew;
```

Badge renders:

```tsx
{isMessages && showBadge && (
  <span className="absolute -top-1.5 -right-1.5 min-w-4 h-4 rounded-full bg-primary text-primary-foreground text-[9px] font-bold flex items-center justify-center px-0.5 leading-none">
    {unread > 0 ? (unread > 99 ? "99+" : unread) : ""}
  </span>
)}
```

When `pendingNew` is true but `unread` is still 0 (refetch in flight), the badge renders as an empty red dot — instant visual feedback, no stale count shown.

### Socket coverage summary

| Where the user is | Which socket runs | What triggers refetch |
|---|---|---|
| `/messages` list view | List-level socket (`enabled: !selectedConversation`) | `handleNewDm` in Messages component |
| `/messages` chat open (ChatView) | ChatView socket | Dedicated to real-time messages, list updates when back |
| Any other page | Bottom nav socket (`enabled: !isOnMessagesPage`) | `handleNewDm` in `useUnreadMessages` |

No page ever runs two sockets to the same namespace simultaneously.

---

## 47. Event Chat — Message Order and Prepend vs Append

### The symptom

"When I add a new message it shows at the bottom, but when I refresh it shows at the top."

### Why it happened

The server returns event chat history **newest-first** (most recent message at index 0). The history was stored directly: `setMessages(json?.data?.data ?? [])`. When rendered top-to-bottom, the newest message appears at the top. That's the intended design — it's a comment section, not a chat bubble list.

But the socket handler did:

```ts
// ❌ Appending — puts new message at the end (bottom)
return [...prev, msg];
```

And the optimistic bubble also appended:

```ts
// ❌ Appending
setMessages((prev) => [...prev, optimistic]);
```

Result: history renders newest-at-top, but new messages land at the bottom. They disagree.

### The fix: prepend

```ts
// ✅ Prepend — new message goes to the front (index 0 = top of list)
return [msg, ...prev];
```

```ts
// ✅ Optimistic bubble also prepended
setMessages((prev) => [optimistic, ...prev]);
```

No reversal of the history array needed. The server already gave us the right order. We just had to match it.

### Why not reverse the history?

An alternative would be to `.reverse()` the history on load (oldest first) and keep appending. This is what DM chat does — oldest at top, newest at bottom, scroll-to-bottom pattern.

For event chat, the user specifically wanted "newest at top, like a comment section." Reversing would be:
1. Extra computation on every history load (not huge, but unnecessary)
2. Requires keeping the `bottomRef` + scroll-to-bottom behaviour
3. Goes against what the server already gives you

The server chose newest-first for a reason. Trust it, match it with prepend.

### Scroll behaviour

With newest at top, there's nothing to scroll to on new messages. They just appear at the top where the user is already looking. So the `bottomRef` div and the `scrollIntoView` effects were removed entirely.

```ts
// ❌ Before — scroll to bottom on every new message
useEffect(() => {
  bottomRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages.length]);

// ...
<div ref={bottomRef} />  // sentinel div at the end

// ✅ After — nothing needed, newest is already at the top
// No auto-scroll comment left to explain the decision:
// "No auto-scroll needed — newest messages appear at the top naturally."
```

### Optimistic bubbles for event chat

Added the same `pendingOptimisticRef` Map pattern as DM chat:

```ts
const pendingOptimisticRef = useRef<Map<string, string>>(new Map());

const handleSend = () => {
  const text = message.trim();
  if (!text || !isConnected) return;

  socket?.emit("send:event-chat", { eventId, section: SECTION_KEY[activeSection], body: text });

  const optimisticId = `opt-${Date.now()}`;
  pendingOptimisticRef.current.set(text, optimisticId);

  const me = meData?.data as any;
  const optimistic: ChatMessage = {
    id: optimisticId,
    body: text,
    senderId: myId,
    sender: { id: myId, displayName: me?.displayName, username: me?.username, avatarUrl: me?.avatarUrl },
    createdAt: new Date().toISOString(),
  };
  setMessages((prev) => [optimistic, ...prev]); // prepend
  setMessage("");
};
```

When the server echoes the message back via `new:event-chat`, the deduplication in `handleNewMessage` finds the matching body in `pendingOptimisticRef` and replaces the optimistic entry with the real message (correct server ID and timestamp) instead of creating a duplicate.

Clear pending optimistics when switching sections (pre-event → during → post-event):

```ts
useEffect(() => {
  setMessages([]);
  pendingOptimisticRef.current.clear(); // stale optimistics from old section
  fetchHistory(activeSection);
}, [activeSection, fetchHistory]);
```

---

## 48. Tab Switching and Sockets — Effect Dependencies

### The question

"If I switch between Pre-Event / During / Post-Event tabs and come back, will the socket still work? Will real-time messages still come through?"

### Yes — because `activeSection` is in the effect dependency array

The socket effect in `EventChatTab` has this signature:

```ts
useEffect(() => {
  // ...
}, [eventId, activeSection, socketRef]);
```

When `activeSection` changes (user switches tabs), React:
1. Runs the **cleanup** of the old effect — `socket.off("connect", oldJoinRoom)` and `socket.off("new:event-chat", oldHandler)`, where `oldJoinRoom` is the closure that captured the old section value
2. Runs the **new effect** — registers new listeners that capture the new section, and emits `join:event-chat` with the new section key

The socket itself **does not disconnect or reconnect**. It stays alive. Only the room membership changes.

```ts
useEffect(() => {
  const socket = socketRef.current;
  if (!socket) return;

  const section = SECTION_KEY[activeSection]; // captures current section

  const joinRoom = () => {
    socket.emit("join:event-chat", { eventId, section }); // joins the right room
  };

  const handleNewMessage = (msg: ChatMessage) => {
    // This handler only runs while this section is active.
    // When the tab switches, this specific closure is removed and replaced.
    setMessages((prev) => {
      if (msg.id && prev.some((m) => m.id === msg.id)) return prev;
      // ... dedup and prepend
    });
  };

  socket.on("connect", joinRoom);
  socket.on("new:event-chat", handleNewMessage);
  if (socket.connected) joinRoom(); // already connected → join immediately

  return () => {
    // Cleanup: remove THIS section's listeners
    socket.off("connect", joinRoom);
    socket.off("new:event-chat", handleNewMessage);
  };
}, [eventId, activeSection, socketRef]); // ← activeSection here is the key
```

### What would happen without `activeSection` in the deps

```ts
// ❌ Missing activeSection in deps — stale closure bug
useEffect(() => {
  const section = SECTION_KEY[activeSection]; // captured once, never updated

  const joinRoom = () => {
    socket.emit("join:event-chat", { eventId, section }); // always "PRE_EVENT"!
  };

  socket.on("connect", joinRoom);
  socket.on("new:event-chat", handleNewMessage);
  if (socket.connected) joinRoom();

  return () => { /* only runs on unmount */ };
}, [eventId, socketRef]); // activeSection NOT here
```

The closure captures `section = "PRE_EVENT"` on first render and never updates. Switching to "During" tab → `setActiveSection("during")` → `section` in the closure is still `"PRE_EVENT"` → socket is still joined to the pre-event room → real-time messages from "during" never arrive.

### The general rule

Any value used inside a `useEffect` that can change over time must be in the dependency array. React will re-run the effect (running cleanup first) whenever any dep changes. For socket effects this means: closing old listeners, opening new ones, re-joining the correct room.

### Stale closure — the broader concept

A **stale closure** is when a function captures a variable from its surrounding scope, but that variable later changes and the function doesn't know about it.

```ts
let count = 0;
const log = () => console.log(count); // captures count = 0

count = 5;
log(); // logs 0, not 5 — stale closure
```

In React, every render creates new function instances. If your effect uses a function from the current render, the deps array tells React when to create a fresh one. Missing a dep = stale closure = bugs that are hard to track down because the code looks correct.

---

## 49. Word Puzzle — Auditing an Implementation Against a Design Spec

### The exercise

A PDF spec was handed over describing how the word-puzzle game should work. The task: read the spec, check the code, and identify what's missing.

This is a real-world skill — product or backend teams often hand over requirements as documents rather than tickets. Knowing how to read a spec and map it against code methodically is as important as knowing how to write code.

### What the spec required

The PDF described five things:

1. **API response shape** — `{ grid: string[][], hiddenWords: [{word, clue, startCell, endCell, direction}], points }`
2. **2D grid render** — CSS Grid, dynamic column count, per-cell state (`isIdle`, `isHovered`, `isSelected`, `isPartofCorrectWord`)
3. **Pointer event listeners** — `onPointerDown`, `onPointerMove/Enter`, `onPointerUp` to track drag lines across letters
4. **Client-side word validation** — compare user's start/end cell coordinates against `hiddenWords`, no API call needed
5. **UI layout** — grid canvas, word/clue sidebar (strikethrough when found), score + timer panel

### How to audit systematically

Go through each requirement and find the corresponding code:

```
Requirement 1 — API shape
  → Search for where game data is consumed
  → Found: buildGridFromQuestions() in page.tsx and event-game-tab.tsx
  → Status: ✅ — server sends flat question objects with word/startCell/endCell;
    client builds the grid itself (smarter than spec's approach)

Requirement 2 — 2D grid render
  → Search for gridTemplateColumns
  → Found: style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
  → Cell states: CellState = "idle" | "hovered" | "selected" | "correct" | "wrong-flash"
  → Status: ✅

Requirement 3 — Pointer events
  → Search for onPointerDown, onPointerMove, onPointerUp
  → Found: all three on the container div in WordPuzzleGrid
  → Also: setPointerCapture (spec didn't mention this but it's required for mobile)
  → Status: ✅ — better than spec

Requirement 4 — Client-side validation
  → Search for handleSelectionComplete
  → Found: coordinate matching with forward + reverse support
  → Status: ✅

Requirement 5 — Sidebar
  → Found: "Words to Find" section — shows hw.word
  → Spec said to show item.clue OR item.word
  → hw.clue is stored (q.text ?? q.clue ?? q.word) but never rendered
  → Status: ⚠️ — gap found

Score/timer panel
  → Found: countdown timer + progress bar in WordPuzzleRoundPlayer
  → Status: ✅
```

### The gap — sidebar showed word only, not clue

The spec said to show `item.clue` (hints like "King of the jungle") so finding the word is an actual puzzle. Showing "LION" in the word list makes it trivial — users just scan for each word they can read.

`hw.clue` was already stored in the data structure:

```ts
// In buildGridFromQuestions:
clue: q.text ?? q.clue ?? q.word,  // already there, just never rendered
```

### The fix — show both word and clue

The old sidebar was a flat flex-wrap pill list — too cramped to show two lines per item. Changed to a 2-column grid so each item has room for both:

```tsx
// ❌ Before — word only, pill layout
<div className="flex flex-wrap gap-1.5">
  {hiddenWords.map((hw, idx) => {
    const found = foundWords.has(hw.word.toUpperCase());
    return (
      <div key={`${hw.word}-${idx}`} className={cn(
        "flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium border",
        found ? "border-green-500/40 bg-green-500/10 text-green-700 line-through"
               : "border-border bg-muted text-muted-foreground"
      )}>
        {found && <CheckCircle2 className="h-3 w-3 shrink-0" />}
        {hw.word}
      </div>
    );
  })}
</div>
```

```tsx
// ✅ After — word + clue, 2-column grid layout
<div className="grid grid-cols-2 gap-1.5">
  {hiddenWords.map((hw, idx) => {
    const found = foundWords.has(hw.word.toUpperCase());
    // Only show clue if it's different from the word itself
    // (when no clue was provided, clue falls back to the word — no need to repeat it)
    const hasClue = hw.clue && hw.clue.toUpperCase() !== hw.word.toUpperCase();
    return (
      <div key={`${hw.word}-${idx}`} className={cn(
        "flex items-start gap-1.5 rounded-xl px-2.5 py-2 text-xs border transition-all",
        found ? "border-green-500/40 bg-green-500/10 text-green-700"
               : "border-border bg-muted/50 text-foreground"
      )}>
        <div className="shrink-0 mt-0.5">
          {found
            ? <CheckCircle2 className="h-3 w-3 text-green-600" />
            : <span className="block h-3 w-3 rounded-full border border-current opacity-40" />}
        </div>
        <div className="min-w-0">
          <p className={cn("font-bold leading-tight", found && "line-through")}>
            {hw.word}
          </p>
          {hasClue && (
            <p className={cn(
              "text-[10px] leading-tight mt-0.5 truncate",
              found ? "text-green-600/70" : "text-muted-foreground"
            )}>
              {hw.clue}
            </p>
          )}
        </div>
      </div>
    );
  })}
</div>
```

The `hasClue` check prevents redundancy: if no clue was authored (`clue` falls back to `word`), showing both would repeat the same text twice.

### How the game is played (mobile and laptop)

Understanding the interaction model is essential before auditing pointer event code.

**On mobile (touch):**
- Press and hold your finger on the starting letter
- Drag across the grid letters in a straight line
- Lift your finger on the last letter of the word
- If your start/end cells match a hidden word's coordinates, that word is found

**On laptop (mouse):**
- Click and hold on the starting letter
- Drag to the last letter
- Release

The cells highlight as you drag (`"hovered"` state). A correct match turns green (`"correct"`). A miss flashes red (`"wrong-flash"`) and clears after 500ms.

**Why `setPointerCapture` matters on mobile:** Without it, if your finger moves slightly off a cell edge, the browser treats it as leaving the element and `onPointerMove` stops firing mid-drag. `setPointerCapture` locks the pointer events to the grid container for the lifetime of the drag, no matter where the finger moves. The spec didn't mention this — it's a mobile-specific detail that the code handles correctly.

### Key lesson — specs describe what, code must handle how

The spec said "implement pointer event listeners." The code went further:
- Used container-level events (not per-cell) — essential for touch drag reliability
- Added `setPointerCapture` — handles finger drift
- Added `onPointerLeave` — commits the selection if the user drags off the grid edge

A spec describes the intended behaviour. Implementation must account for the real environment (mobile browsers, edge cases, timing).

---

## 50. Dead Code — Recognising and Removing Unreachable Functions

### What dead code is

Dead code is any code that can never execute at runtime. It compiles, it looks correct, but no code path ever reaches it. It's harmless to behaviour but harmful to maintenance: future readers assume it matters, spend time understanding it, and may accidentally try to wire it up.

### The `handleWordSubmit` example

In `RoundPlayer` (inside both `page.tsx` and `event-game-tab.tsx`), there was a function:

```ts
const handleWordSubmit = () => {
  if (flash || !wordInput.trim()) return;
  const correctAnswer: string = q?.correctAnswer ?? q?.answer ?? "";
  const isCorrect = wordInput.trim().toLowerCase() === correctAnswer.trim().toLowerCase();
  const newAnswers = [...answers];
  newAnswers[currentQ] = wordInput;
  setAnswers(newAnswers);
  setFlash({ selected: wordInput, correct: correctAnswer, isCorrect });
  setTimeout(() => advance(wordInput, newAnswers), 800);
};
```

It looks reasonable — it handles submitting a typed word answer. But it was never called.

**Why it could never be called:** `RoundPlayer` handles multiple game types. When `gameType === "word-puzzle"`, the component exits early:

```ts
// ── Word Puzzle: delegate entirely to the grid player ──────────────────────
if (gameType === "word-puzzle") {
  if (finalScore !== null) {
    // fall through to score screen
  } else if (!waitingForResult) {
    return (
      <WordPuzzleRoundPlayer   // ← exits here — renders the grid player
        questions={questions}
        onAllComplete={async (wordAnswers) => { ... }}
      />
    );
  }
}
```

The execution path for word-puzzle never reaches the rest of `RoundPlayer`. There's no text input rendered. `handleWordSubmit` is wired to nothing. It's unreachable.

### How to identify dead code

**Signal 1 — TypeScript hints**

TypeScript reports `'handleWordSubmit' is declared but its value is never read` as a hint (code `6133`). This is TypeScript telling you directly that nothing references this identifier. Treat these hints seriously — they're almost always pointing at real dead code.

**Signal 2 — Early returns that bypass everything**

When a function has an early return that covers a whole case:

```ts
if (gameType === "word-puzzle") {
  return <WordPuzzleRoundPlayer ... />;  // exits here for ALL word-puzzle games
}

// Everything below here is never reached for word-puzzle
const handleWordSubmit = () => { ... };  // dead
```

Trace the control flow for each case. If a case exits early and a function is only relevant to that case, the function is dead.

**Signal 3 — Nothing calls it**

Search the file for the function name. If the only match is the declaration, it's dead.

```bash
grep -n "handleWordSubmit" event-game-tab.tsx
# 807:  const handleWordSubmit = () => {
# Only one result — the declaration. Nothing calls it.
```

### What to do about dead code

**Delete it.** Don't comment it out, don't add a `// TODO: use this later` comment, don't leave it "just in case." If it's unreachable now, it will stay unreachable — and if you genuinely need it later, git history has it.

The one exception: if there's a real, imminent plan to wire it up (e.g. "we're adding a text input mode for word puzzle next sprint"), keep it and add a comment explaining why. But "might be useful someday" is not a reason to keep dead code.

### Handling truly unused parameters

Sometimes a function signature must match a certain shape even when you don't use all the parameters. TypeScript's convention is to prefix unused parameters with `_`:

```ts
// ❌ Unused parameter — TypeScript reports hint 6133
const advance = async (selectedAnswer: number | string, allAnswers: (number | string)[]) => {
  // selectedAnswer is never used inside the function body
};

// ✅ Underscore prefix — tells TypeScript (and readers) "intentionally unused"
const advance = async (_selectedAnswer: number | string, allAnswers: (number | string)[]) => {
  // The _ prefix suppresses the hint and communicates intent
};
```

The underscore is a widely recognised convention across TypeScript, JavaScript, Python, Rust, and Go. It means "I know this parameter exists and I'm deliberately not using it."

**When to use `_` vs just removing the parameter:**
- Use `_` when the parameter is part of a required signature (callback shape, interface, event handler)
- Delete the parameter entirely when it's your own internal function and you can freely change the signature

In this project, `advance` is called via `setTimeout(() => advance(idx, newAnswers), 800)` and the first arg is passed even though `advance` doesn't use it. Changing the call site to `advance(newAnswers)` would also work, but the `_` approach is simpler and makes the intent obvious without restructuring the calls.

### Also cleaned up — inline event handlers

```tsx
// ❌ Unused event parameter
onPointerLeave={(e) => {
  if (isDrawing.current && startCell.current) { ... }
}}

// ✅ Remove unused param
onPointerLeave={() => {
  if (isDrawing.current && startCell.current) { ... }
}}
```

Same principle: if you're not using the event object, don't declare it. Keeps the code honest.

### Summary — dead code checklist

When reviewing code:

1. **Check TypeScript hints** — `'X' is declared but its value is never read` means dead code
2. **Trace early returns** — any function that "handles" a case already covered by an early return is dead
3. **Search for callers** — if nothing calls a function, it's dead
4. **Remove it** — don't leave "just in case" dead code; use git history if you ever need it back
5. **Prefix unused params** — `_paramName` instead of deleting when the signature must match a required shape

---

*This guide covers the NextVibe frontend as of May 2026. Update it when significant architectural changes are made.*
