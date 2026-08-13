# NextVibe — Frontend: Next.js & State

From [`../learning/frontend/01-routing.md`](../learning/frontend/01-routing.md),
[`02-state-management.md`](../learning/frontend/02-state-management.md),
[`04-forms-ui.md`](../learning/frontend/04-forms-ui.md),
[`05-uploads-errors.md`](../learning/frontend/05-uploads-errors.md),
[`08-performance-debugging.md`](../learning/frontend/08-performance-debugging.md).

---

### Q1. [Beginner] 🔥 Server Components vs Client Components — how do you decide?

**Strong answer covers:** Server Components are the **default**; they run on the server, can query
data directly, and ship **no JavaScript** to the browser. `"use client"` marks the boundary where
interactivity begins — state, effects, event handlers, browser APIs.

**The decision rule:** push the boundary as far down the tree as possible. A page that's mostly
static with one interactive widget should be a Server Component rendering a small client child, not a
client component all the way up. The consequence people miss: `"use client"` is **contagious
downward** — everything imported by a client component becomes client code too, so one misplaced
directive near the root ships the whole subtree.

---

### Q2. [Beginner] Route groups, dynamic routes, and layouts — what does each give you?

**Strong answer covers:** `(group)` folders organise routes and give them a shared layout **without
appearing in the URL** — so `(auth)` and `(dashboard)` can have completely different chrome.
`[param]` is a dynamic segment; `[...slug]` catches the rest of the path. Layouts nest and — this is
the important part — **persist across navigation between their children**, which is why they're the
right home for navigation and the wrong home for anything that changes with the child.

**The rule from the notes:** route-group layouts own the chrome; pages render only content.

---

### Q3. [Intermediate] 🔥 How does Next.js middleware actually work, and what belongs in it?

**Strong answer covers:** it runs **before** the request is handled, on every matching path, in the
edge runtime — so it's fast, has no Node APIs, and can't touch a database. What belongs: cheap
redirect and rewrite decisions based on cookies or headers — auth gating, locale routing, A/B
bucketing. What doesn't: anything requiring a real database call or heavy computation, because it's
on the critical path of every request.

**The security caveat to volunteer:** middleware auth is a **UX** gate, not an authorisation
boundary. It can redirect an unauthenticated user away from a page, but the API endpoint behind that
page must still verify the token — otherwise the protection is "the client didn't navigate there."

---

### Q4. [Intermediate] 🔥 `useSearchParams()` requires a Suspense boundary. Why?

**Strong answer covers:** it makes the component depend on request-time information, so Next can't
statically prerender it. Wrapping it in `<Suspense>` lets the rest of the page prerender while that
subtree is deferred — without the boundary, the build fails or the **entire route** opts out of
static rendering, which quietly degrades every page that touches search params.

**The general point:** Suspense isn't only a loading-spinner mechanism; it's the unit of "this part
can resolve later", which is what lets the rest of the page not wait.

---

### Q5. [Intermediate] 🔥 Redux Toolkit *and* RTK Query — what does each own?

**Strong answer covers:** RTK slices own **client** state — the things only the browser knows: UI
state, session, in-progress selections. RTK Query owns **server** state — fetching, caching,
deduplication of in-flight requests, invalidation, loading/error flags.

**The failure this split prevents:** hand-writing thunks to fetch data into a slice means you also
hand-write caching, refetching, dedupe and invalidation, badly. Server data in a slice becomes stale
with no mechanism to notice.

---

### Q6. [Advanced] 🔥 Explain RTK Query cache invalidation with tags, with the rewards example.

**Strong answer covers:** queries declare `providesTags` for the data they return; mutations declare
`invalidatesTags` for what they change. Invalidating a tag marks every query providing it as stale,
so any mounted component refetches automatically — no manual "and also refresh this list" wiring.

**Worked shape:** a rewards list query provides `[{ type: 'Reward', id: 'LIST' }]`; a specific reward
provides `[{ type: 'Reward', id }]`. Claiming a reward invalidates that id *and* the LIST tag, so
both the detail view and the list update.

**The two failure modes to name:** invalidating too broadly (a `LIST` tag on every mutation) causes a
refetch storm; invalidating too narrowly means the UI shows a stale value and the bug report is "I
have to refresh the page." Tag design is the actual work.

---

### Q7. [Intermediate] Why react-hook-form + zod rather than controlled state?

**Strong answer covers:** react-hook-form keeps inputs **uncontrolled** and subscribes per-field, so
typing in one field doesn't re-render the whole form — which matters a lot on the long forms in this
app. zod defines the schema once and infers the TypeScript type from it, so the validation rules and
the form's type can't drift. And the same schema can validate on the server, so client and server
agree on what's valid by construction rather than by discipline.

---

### Q8. [Advanced] 🔥 Explain presigned upload URLs and why you migrated to them.

**Strong answer covers:** originally files went to the API as multipart, so the server received the
bytes, buffered them, and forwarded them to storage — paying double bandwidth, holding memory
proportional to file size, and hitting whatever body-size limit the platform enforces.

**The presigned flow:** the client asks the API for a URL; the API (which holds the credentials)
signs a time-limited, operation-scoped URL for a specific key; the client **uploads directly to
storage**; then the client tells the API the resulting key so it can record the metadata. The bytes
never touch your server.

**The properties to name:** the signature encodes the bucket, key, method and expiry, so it can't be
reused for a different object or after it expires; the API keeps full control of *what* may be
uploaded and *where*, without ever handling the payload; and it scales because storage, not your
dyno, absorbs the traffic.

**Follow-up:** *"What can go wrong?"* — the client can lie about having uploaded, so metadata should
be verified (or confirmed by a storage event); and CORS on the bucket must allow the browser's
direct PUT, which is the usual reason a correct implementation still fails.

---

### Q9. [Intermediate] 🔥 Describe the universal error handler. What problem does it solve?

**Strong answer covers:** without one, every component invents its own error message from whatever
shape the failure happens to have — an axios error, an RTK Query error, a thrown `Error`, a network
failure with no response at all. The universal handler normalises those into one shape and one
user-facing message, so errors are consistent and each component isn't reimplementing "is this a
401?".

**What it must distinguish:** no response at all (offline/DNS) from a response with a status; 401
(re-authenticate) from 403 (you're logged in and not allowed) from 422 (fix your input) from 5xx (not
your fault, retry). Collapsing those into "Something went wrong" is what makes an app feel broken
even when it's behaving correctly.

---

### Q10. [Intermediate] Online/offline detection and fire-and-forget error logging — why both?

**Strong answer covers:** the browser's `online`/`offline` events let the UI say "you're offline"
instead of "request failed", which is the difference between a user waiting and a user filing a bug.
Error logging is **fire-and-forget** — the log request must never block the UI or, worse, throw and
trigger another log. The rule: a logging call is a side effect (same family as the notification
`.catch(() => null)` on the backend), and a logger that can fail the thing it's observing is worse
than no logger.

---

### Q11. [Intermediate] "Immediate upload on file selection" is described as a UX state machine. Explain.

**Strong answer covers:** uploading when the file is chosen, rather than on submit, means the form
now has states — `idle → selected → uploading → uploaded → failed` — and each has different rules:
submit must be disabled while uploading, a failed upload needs a retry that doesn't lose the rest of
the form, and cancelling has to clean up a partially uploaded object. Modelling it explicitly is what
prevents the classic bugs: double submission, a submit that succeeds with a missing attachment, or a
spinner that never resolves.

---

### Q12. [Advanced] What's actually slow in a Next.js app, and how do you find it?

**Strong answer covers:** the usual culprits — too much client JavaScript because the `"use client"`
boundary is too high; unnecessary re-renders from unstable props; unoptimised images; and waterfalls
where a component fetches, renders a child, and *that* fetches. Diagnosis in order: the bundle
analyser for shipped JS, React DevTools' profiler for re-renders, and the network waterfall for
sequential fetches.

**The Next-specific point:** the biggest performance lever is usually **rendering strategy**, not
micro-optimisation — moving work to a Server Component removes its JavaScript from the client
entirely, which no amount of memoisation matches.

---

### Q13. [Advanced] 🔥 Tell me about a frontend bug that wasn't where you first looked.

**Strong answer covers — the strongest available, told compactly:**
- **The socket that said "connected" but received nothing** — the bug was in React's rendering
  pipeline being too slow to trigger a room join, not in the socket
  ([03-realtime-and-notifications.md](03-realtime-and-notifications.md) Q4).
- **The socket that died after exactly 15 minutes** — the bug was `js-cookie`'s `expires` being in
  days, in a *different* login path ([02-auth-and-security.md](02-auth-and-security.md) Q5).
- **Notifications that "didn't work"** — the entire frontend was fine; the backend never produced
  them.

**The connecting observation, which is the real answer:** in all three, the symptom appeared in the
realtime/UI layer and the cause was somewhere else entirely — a cookie helper, a render scheduler, a
missing service call. The habit that finds them is to **verify each stage's input independently**
rather than debugging the stage where the symptom shows up.

---

### Q14. [Beginner] Which Next.js concepts do you *not* use here, and would you want to?

**Strong answer covers:** name a few honestly — ISR/revalidation, parallel and intercepting routes,
and heavy use of Server Actions for mutations. Then say where they'd help: ISR for public event
pages, which are read-mostly and currently rendered more dynamically than they need to be;
intercepting routes for modal detail views that should still be linkable. Knowing what you didn't use
and why is more convincing than claiming to have used everything.
