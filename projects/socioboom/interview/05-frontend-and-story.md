# SocioBoom — Frontend & Project Story

From [`../learning/frontend/`](../learning/frontend/) — App Router, TanStack Query, feature
walkthroughs, honest UI, media uploads — plus the behavioural half.

---

### Q1. [Intermediate] 🔥 Why TanStack Query rather than fetching in `useEffect`?

**Strong answer covers:** it owns **server state** — caching keyed by query key, deduplication of
in-flight requests, background refetch, stale-while-revalidate, retries, and loading/error states you
don't hand-roll. Fetching in `useEffect` means reimplementing all of that badly, and typically
forgetting cancellation, so a fast navigation leaves a late response overwriting fresher data.

**The v5 detail worth knowing:** the object signature (`useQuery({ queryKey, queryFn })`), and
`isPending`/`isLoading` meaning different things — pending is "no data yet", loading is "pending and
actually fetching". Mutations invalidate query keys to trigger refetch, which is the mechanism that
keeps lists fresh after a write.

---

### Q2. [Advanced] 🔥🔥 An AI feature went from a 3-second request to a 1–3 minute background agent. How did the frontend contract change?

**Strong answer covers the shape change, not just the timing:** the old flow was one awaited
request — everything arrives at once, or it times out. That does not survive a three-minute run;
proxies and load balancers will kill it long before the agent finishes.

**The new flow is kickoff + poll:**
1. `POST /discovery/search` returns **immediately** (202) with a session id and status `running`.
2. The client polls `GET /discovery/:id` on an interval, up to a bounded maximum.
3. **Results grow between polls, because the agent saves findings incrementally** — so the UI
   updates progressively and *feels* like streaming with no WebSocket involved.
4. Polling stops when status is no longer `running` (`completed` or `failed`), and the summary is
   read from the session.

**The detail that shows care:** an `activeSearch` token guards the loop, so if the user starts a new
search the old poll loop exits instead of overwriting the new results with stale ones. That's the
same class of bug as an uncancelled `useEffect` fetch — and it's the one people forget.

**Why polling over WebSockets here:** far simpler, works through every proxy, and the update rate
needed is seconds not milliseconds. Reaching for a socket would add a connection lifecycle to manage
for no gain.

---

### Q3. [Advanced] 🔥🔥 `URL.createObjectURL` is not an upload. Explain the three-step upload and the bug in the obvious version.

**Strong answer covers the misconception first:** `URL.createObjectURL(file)` gives you a **local
blob URL** for previewing. It's a pointer into the browser's memory — it doesn't exist for anyone
else, and it dies with the page. Treating it as an uploaded asset produces a preview that works
perfectly for the person who selected the file and is broken for everyone else.

**The three steps:** ask the API for a presigned URL → `PUT` the bytes directly to R2 → tell the API
the resulting key so it records the metadata.

**The bug — a stale closure:**
```ts
// ❌ drops results
for (const file of files) {
  const item = await uploadFile(file);
  setMediaItems([...mediaItems, item]);
}
```
`mediaItems` is captured from the render that *started* the loop and never updates during it, so each
iteration builds its array from the same stale snapshot — after three uploads you have only the
third.

```ts
// ✅
setMediaItems((current) => [...current, item]);
```
The functional form receives React's **current** state instead of the closed-over value.

**The knock-on detail that makes this answer memorable:** the child component's prop was typed
`setMediaItems: (items: MediaItem[]) => void`, which **cannot express a functional update** — so the
prop type had to widen to `React.Dispatch<React.SetStateAction<MediaItem[]>>`. The general lesson:
*the "simpler" prop type `(v: T) => void` silently forbids functional updates — fine for synchronous
handlers, a bug factory for async ones.*

---

### Q4. [Intermediate] 🔥 Why `XMLHttpRequest` in 2026?

**Strong answer covers:** upload **progress**. `fetch` still has no upload-progress event — you can
stream a *response* but not observe request-body progress — and XHR's `upload.onprogress` gives
loaded/total for free. For a file upload where the user needs a percentage, that's decisive. XHR also
gives straightforward abort, though `fetch` has `AbortController` for that.

**The honest framing:** it's not nostalgia, it's the one thing the older API still does better, and
it's isolated behind an upload helper so nothing else in the codebase touches it.

---

### Q5. [Advanced] "Slot accounting with files in flight" — what's the problem?

**Strong answer covers:** platforms cap attachments (e.g. four images), so the UI must enforce a
limit — but during upload some items are *in flight* and not yet in the confirmed list. Counting only
completed uploads lets the user start a fifth; counting optimistically without reconciling leaves
phantom slots when one fails. The fix is to count **committed + in-flight** against the cap, and to
release the slot explicitly on failure — which means in-flight uploads need to be real entries in
state with a status, not an untracked promise.

---

### Q6. [Advanced] 🔥🔥 "Honest UI" — give me the concrete example.

**The best product-engineering story in this project.**

**Strong answer covers:** the platform selector offered **Instagram**. The publish worker supported
twitter, linkedin, reddit and facebook — Instagram hit `default: throw 'Publishing not yet
supported'`. So a user could select Instagram, write a post, schedule it, and get a **silent failure
days later**. Meanwhile **Reddit**, which the worker fully supported, wasn't offered at all.

**The framing to state:** the frontend's option lists are a **promise about backend capability**.
When they drift, users experience it as the product lying to them. The fix was mechanical — swap
Instagram for Reddit in the platform selector, the AI panel's meta map, and the connections card —
but the real output is **the audit**: for every option you render, find the backend `switch` that
handles it.

**The bonus detail:** the Reddit swap demonstrates conditional required fields done properly on both
sides — a subreddit input appears only when Reddit is selected, normalises `r/foo` → `foo` on input,
and explains that the first line becomes the title. A conditionally-required field that's only
enforced on the client is the next version of the same dishonesty.

---

### Q7. [Intermediate] What are the common frontend pitfalls you'd warn a new team member about here?

**Strong answer covers, from the notes:** stale closures in async loops (Q3); the `(v: T) => void`
prop type that forbids functional updates; server state stored in component state instead of a query
cache, so two components disagree; `"use client"` placed too high, shipping a whole subtree to the
browser; and sending less than you collected — a form that gathers fields the submit payload silently
drops, which produces "I set that and it didn't save."

---

### Q8. [Intermediate] Tailwind v4 and shadcn/ui — what's actually different?

**Strong answer covers:** Tailwind v4 is **CSS-first** — theme tokens are declared with `@theme` in
the stylesheet and there's no `tailwind.config.js`, so half the answers online tell you to edit a
file that doesn't exist. shadcn/ui **copies component source into your repo** rather than installing a
package: you own and edit the files, at the cost of no upstream updates. Dark mode is a class on the
root plus CSS-variable token pairs, which is why theming works without touching component code.

---

### Q9. [Advanced] 🔥 What's the single most valuable lesson from this project?

**Strong answer covers — pick one and commit:**
- **"Retries demand idempotency."** Adding retries to a non-idempotent multi-platform publish turned a
  visible failure into invisible duplication. It's the most broadly applicable thing here.
- **"You cannot validate provenance with a format check."** The hallucinated URL passed a regex
  perfectly, and the fix — an allowlist of what the system actually observed — is the general shape of
  grounding any model output.
- **"The UI is a promise about backend capability."** Offering Instagram when the worker couldn't
  publish to it was a product bug with no failing code anywhere.

---

### Q10. [Advanced] What would you do differently if you rebuilt SocioBoom?

**Strong answer covers concrete, defensible items:**
- **A capability registry as the single source of truth** — one place declaring which platforms are
  publishable, consumed by both the worker's dispatch and the frontend's selector, so the honest-UI
  drift becomes structurally impossible rather than an audit you have to remember.
- **Encrypt platform tokens at rest and add a refresh lock** before scaling to multiple workers.
- **Build the platform integrations against real accounts from day one** — Facebook's publisher was
  "complete" and could never have worked.
- **An evaluation set for the AI features**, so a model or prompt change is measurable rather than a
  bet.

---

### Q11. [Beginner] 🔥 Explain SocioBoom to a non-technical interviewer.

**Strong answer covers:** it's a tool for scheduling social media posts across several networks at
once, with AI features that research what people are complaining about online and help draft
content. The engineering challenge is that each network works completely differently — different
login systems, different rules about what you're allowed to post and from what kind of account — and
that anything published is permanent, so the system has to be very careful never to post the same
thing twice when it retries after a failure.

That last clause is the hook. It names the hard problem in words anyone understands.
