# Arete — Mobile (React Native / Expo)

From [`../learning/mobile/`](../learning/mobile/) — fundamentals, navigation/state, the API layer,
UI patterns, push notifications, and the Home Trail case study.

---

### Q1. [Beginner] What is React Native actually doing, and what are the three primitives?

**Strong answer covers:** you write React, and the components render to **real native views** — not
a webview. `View` (a layout box, like a `div`), `Text` (all text must be inside one, unlike the
web), and `Image`. Styling is a JS object subset of CSS with no cascade and no inheritance except
for some text properties, so every component styles itself.

**The Flexbox difference worth knowing:** `flexDirection` defaults to `column` in React Native, not
`row`. That single default catches everyone coming from the web.

---

### Q2. [Beginner] 🔥 Expo Router uses file-based routing. How do you pass data between screens?

**Strong answer covers:** two mechanisms with a clear rule for choosing —
- **Route params** for the identity of what's being shown (`/quest/[id]`). They survive deep links
  and app restarts, and are serialisable by definition.
- **Global state (Zustand)** for anything shared across screens — the current user, auth state,
  in-flight progress.

**The rule:** params carry *what to look at*; the store carries *what the app knows*. Passing a whole
object through params is the common mistake — it bloats the URL, can't survive a deep link from
outside the app, and goes stale the moment the underlying record changes.

---

### Q3. [Advanced] 🔥🔥 Your access token expires. Five requests fire at once and all get 401. What happens?

**The naive failure:** five parallel refresh calls, and four of them may invalidate each other —
with rotation, the winner's token is immediately superseded and the user gets logged out despite
holding a valid session.

**Strong answer covers the queue:** one refresh, everyone else parks.

```ts
let isRefreshing = false;
let refreshQueue: Array<(token: string) => void> = [];

// on 401:
if (originalRequest._retry) return Promise.reject(error);  // never retry twice
originalRequest._retry = true;

if (isRefreshing) {
  return new Promise((resolve) => {
    refreshQueue.push((token) => {                          // park
      originalRequest.headers.Authorization = `Bearer ${token}`;
      resolve(client(originalRequest));                     // replay when the token arrives
    });
  });
}
isRefreshing = true;
try {
  const { accessToken } = await refreshCall();
  refreshQueue.forEach(cb => cb(accessToken));              // release everyone
  refreshQueue = [];
  return client(originalRequest);
} catch { clearAuth(); }                                     // refresh failed → log out
finally { isRefreshing = false; }
```

**The three details an interviewer will check for:**
1. `_retry` on the request config, so a refreshed-then-still-401 request can't loop forever.
2. The queue holds **callbacks that replay the original request**, not just promises — each parked
   request needs its own header updated and its own replay.
3. `finally { isRefreshing = false }` — without it, one failed refresh wedges every future request
   in the queue permanently.

This is the best pure-frontend question in the vault. It's a real concurrency problem in a place
people don't expect one.

---

### Q4. [Intermediate] 🔥 Why is there one axios instance rather than fetch calls scattered around?

**Strong answer covers:** the instance owns base URL, timeouts, the request interceptor that attaches
the auth header, and the response interceptor that implements the refresh queue. That means auth is
impossible to forget on a new endpoint, and the refresh logic exists exactly once. Typed endpoint
modules sit on top, so screens call `questsApi.complete(id)` and never touch HTTP.

**The line from the notes:** it's the most reusable file in the app — it moves to the next project
essentially unchanged.

---

### Q5. [Advanced] 🔥🔥 A quest timer must survive the app being backgrounded for an hour. How?

**The wrong way:** `setInterval(() => setElapsed(e => e + 1), 1000)`. The OS pauses JS timers when
the app backgrounds, so the accumulated count silently drifts — and it drifts *downward*, so the user
gets credit for less time than they spent.

**Arete's way — the server's `startedAt` is the source of truth, and the interval only forces
re-renders:**
```tsx
const [tick, setTick] = useState(0);           // exists only to trigger a re-render
useEffect(() => { const id = setInterval(() => setTick(t => t + 1), 1000); return () => clearInterval(id); }, []);

const rawElapsedMs = Date.now() - new Date(quest.startedAt).getTime();
const elapsed = Math.floor((rawElapsedMs - quest.totalPausedMs - currentPauseMs) / 1000);
```

Kill the app, reopen it an hour later, and elapsed is still correct — because it's **computed from
timestamps, not accumulated**.

**The principle to state:** derive state from durable facts; never accumulate state you can compute.

**The pause detail that shows depth:** pause time stacks three buckets — server-committed
(`totalPausedMs`), pauses completed this session, and the currently-running pause
(`Date.now() - pauseStart`). Each is derived from timestamps, so the same guarantee holds across a
background/foreground cycle mid-pause.

---

### Q6. [Intermediate] 🔥 Explain optimistic updates as used here, and when they're a bad idea.

**Strong answer covers:** on tap, mark it complete locally and immediately, then fire the API call;
if it fails, the next fetch reconciles. The app *feels* instant, which on mobile matters more than
almost any other performance work.

**When it's wrong:** when the server may legitimately reject the action (insufficient gems — see the
guarded decrement), or when the optimistic state is hard to unwind visually, or when a wrong optimistic
result would be acted on by the user. The honest note about Arete's version: it swallows the error and
relies on a later refetch, which is fine for "mark complete" and would be unacceptable for anything
involving a balance.

---

### Q7. [Intermediate] Zustand rather than Redux — why, and what goes in the store?

**Strong answer covers:** the app's genuinely global state is small — auth/session, user profile,
some cross-screen progress — and Zustand gives that with a hook and no provider, no action types, no
reducer boilerplate. Redux earns its complexity with large state graphs, extensive middleware, or
time-travel debugging needs; none applied.

**The discipline:** server data should mostly *not* live in a global store, because then you own
caching and invalidation by hand. Store the session; fetch the rest.

---

### Q8. [Intermediate] Two animation libraries — when is each right?

**Strong answer covers:** the RN `Animated` API is built in and fine for simple, self-contained
transitions, but driving animations from JS risks dropped frames when the JS thread is busy.
Reanimated runs animations on the **UI thread** via worklets, so they stay smooth regardless of what
JS is doing — which is what you need for gesture-driven and continuous animation. The rule: reach for
the built-in for a one-off fade; reach for Reanimated when the animation must never stutter or follows
a finger.

---

### Q9. [Intermediate] 🔥 Walk me through push notifications end to end.

**Strong answer covers:** request permission (which on iOS you get exactly one chance at, so ask at a
moment the user understands why) → obtain an Expo push token → send it to the backend and store it
against the user → backend sends to Expo's push service, which forwards to APNs/FCM → the app handles
the notification both in foreground (where it doesn't display by default) and on tap, routing to the
relevant screen.

**The operational details that matter:** tokens change, so re-register on launch rather than once;
a device can be shared or a user can log out, so stale tokens must be cleaned up; and delivery is
best-effort, so a notification is never the only way a user learns something.

---

### Q10. [Intermediate] Deep links and the URL scheme — what breaks, and what needs a new build?

**Strong answer covers:** a deep link maps a URL to a route, and combined with a notification payload
it's how a tap lands on the right screen. The critical operational distinction:
**JS-only changes ship over the air; anything touching native configuration requires a new build.**
That includes the URL scheme, notification entitlements, permissions strings, and adding a native
module. Knowing which side of that line a change falls on is what determines whether a fix takes five
minutes or two days of review.

---

### Q11. [Advanced] 🔥 The Home Trail — you built a full feature with zero new backend endpoints. How?

**Strong answer covers:** the trail is **derived** from data the client already has — quest
completion state and progression — rather than fetched as a new resource. That's the same
"derive, don't store" instinct as the deterministic missions and the timestamp-based timer, applied
to UI.

**Why it's a good decision to defend:** no migration, no endpoint, no versioning problem between app
versions, and the feature can be reshaped without touching the server. **When it stops being right:**
as soon as the derivation needs data the client shouldn't have, or the computation gets expensive
enough to matter on a low-end device, or two clients need to agree on the result.

**The supporting details worth mentioning:** empty states were designed first, because they're the
first thing a new user sees and a trail with no progress is the default experience on day one; and
tap-to-preview uses a small client-side cache so repeated taps don't refetch.

---

### Q12. [Intermediate] What's on your React Native performance checklist?

**Strong answer covers:** use `FlatList` (windowed) rather than mapping over an array in a
`ScrollView`; give list items stable `key`s and memoise rows so a parent re-render doesn't re-render
every row; keep animations on the UI thread; avoid inline object/array/function literals in props on
hot paths, since they create a new identity each render and defeat memoisation; and size images
appropriately, because a full-resolution image in a 60px avatar costs real memory on a phone.

**The framing:** on mobile the budget is a 60fps frame — 16ms — on hardware much slower than your
laptop, and the JS thread is shared with everything else the app is doing.
