# NextVibe — Auth & Security

From [`../learning/backend/02-auth.md`](../learning/backend/02-auth.md) and
[`../learning/frontend/03-auth.md`](../learning/frontend/03-auth.md).

---

### Q1. [Intermediate] 🔥 Walk me through authentication end to end.

**Strong answer covers:** credentials (or Google OAuth) → backend verifies and issues a JWT →
the token is stored client-side in a cookie → every subsequent request carries it → a **global
guard** verifies the signature and attaches the payload to the request → controllers read the user
from the request rather than from anything the client sent in a body or param.

**The critical detail:** the user id used in queries comes from the **verified token**, never from a
request parameter. Q9 in [01-backend-nestjs-core.md](01-backend-nestjs-core.md) is what happens when
that payload doesn't arrive intact.

---

### Q2. [Intermediate] 🔥 Explain the `@Public()` pattern. Why opt-out rather than opt-in?

**Strong answer covers:** the JWT guard is registered **globally**, so every endpoint is protected by
default, and `@Public()` sets metadata the guard reads (via `Reflector`) to skip the check for
specific routes.

**Why the polarity matters:** with opt-*in* auth, forgetting a decorator leaves an endpoint wide
open — a silent, invisible security hole. With opt-*out*, forgetting a decorator makes a public
endpoint return 401, which someone notices in about a minute. **Make the failure mode of forgetting
be "too strict," never "too permissive."**

That single sentence is the answer; everything else is implementation.

---

### Q3. [Advanced] 🔥 You have multiple roles — attendee, organiser, admin. How do the tokens work?

**Strong answer covers:** the role is part of the verified token payload, so authorisation checks
read it from the token rather than from a database lookup on every request or from anything the
client asserts. Role-specific guards then gate routes.

**The trade to name:** a role baked into a JWT is **stale until the token expires** — demote someone
and they keep their old privileges for the remaining TTL. Mitigations: short access-token lifetimes,
a revocation list for the sensitive transitions, or re-checking role from the database on the
highest-risk operations only. Being able to state that trade-off is what distinguishes this from
"we put the role in the JWT."

---

### Q4. [Advanced] 🔥 Public pages need to know if you're logged in, and Redux hasn't hydrated yet. How do you handle that?

**Strong answer covers:** Redux state is client-side and only populates after hydration, so a public
page rendered on the server (or on first paint) has no idea. The cookie is the durable, available-
immediately source of truth. So auth state on public pages reads the cookie, and Redux becomes the
in-app cache for it — not the authority.

**The failure this prevents:** a flash of the wrong UI — a "Sign in" button rendering for a
logged-in user for a few hundred milliseconds, or worse, a redirect firing before hydration
concludes.

**The rule:** **the cookie is the source of truth; the store is a convenience.** Anything that
decides *rendering* before hydration must read the cookie.

---

### Q5. [Advanced] 🔥🔥 Sockets worked for exactly 15 minutes after Google login, then failed silently. Debug it.

**The best auth bug in the project. Tell it in this order.**

1. **The symptom:** `useSocket` logged `status → error` immediately, while REST calls kept working —
   so the session was clearly alive.
2. **What `"error"` actually meant:** in the hook, `error` is the sentinel for *"no token"* —
   `Cookies.get("accessToken")` returned nothing, so the socket was never even created. The status
   name was misleading: nothing had errored, something was absent.
3. **The root cause:** `js-cookie`'s `expires` option is in **days**, not seconds. The Google login
   button set `expires: 1/96` — which is 15 minutes. Regular login went through a `store-token` API
   route setting `maxAge: 60*60*24*7` (7 days) instead.
4. **The real problem underneath:** **two login paths setting cookies two different ways.** Google
   login bypassed the shared route and rolled its own.
5. **The fix:** make Google login use the same `store-token` route as regular login — one place that
   knows how session cookies are set.

**The two lessons to state:** a unit mismatch (days vs seconds) is invisible to the type system
because both are numbers; and **any duplicated auth path will eventually diverge** — the fix isn't a
corrected constant, it's removing the second path.

---

### Q6. [Intermediate] 🔥 Tell me about the `?from=` redirect bugs.

**Strong answer covers:** the login flow preserves the intended destination in a `?from=` query
param and redirects there after auth. Two things went wrong —
- **Encoding:** a destination URL that itself contains query params must be
  `encodeURIComponent`-ed. Unencoded, its `&` and `?` are parsed as part of the *login* page's query
  string, so `from` is truncated and the user lands somewhere half-right.
- **Role-specific defaults:** with no `from`, different roles belong on different landing pages, so
  "redirect to `/`" is wrong for at least one role.

**The security point worth volunteering unprompted:** a redirect target taken from a query param is
an **open-redirect** risk — validate that it's a relative path on your own origin before following
it, or an attacker sends a login link that bounces the user to their site with the referrer intact.

---

### Q7. [Intermediate] Walk me through debugging a 401 on login.

**Strong answer covers a method:** bisect the chain rather than guessing. Is the request even
reaching the endpoint (method, path, global prefix)? Is the body arriving in the shape the DTO
expects? Is the failure in credential verification or in token issuance? Is the guard rejecting a
route that should be public? Then on the client: was the cookie actually set (domain, path,
`SameSite`, `Secure` over http in dev), and is it being *sent* on the next request?

**The specific detail that catches people:** `Secure` cookies aren't stored over plain http, and
`SameSite=None` requires `Secure` — so a cookie can be "set" successfully and never come back.

---

### Q8. [Intermediate] Where do you store the token, and what's the honest trade-off?

**Strong answer covers:** this project uses a cookie readable by JS (`js-cookie`), because the
Socket.IO client needs the token to authenticate its connection and Redux/RTK Query need it for
headers. The honest cost: a JS-readable cookie is **XSS-exposed** — any injected script can read it.
`httpOnly` would remove that exposure but the socket handshake and client-side fetch would need a
different mechanism (a short-lived socket ticket issued by an authenticated endpoint).

**What makes this a good answer:** naming the actual attack (XSS), the actual reason the weaker
option was chosen (the socket handshake), and the concrete alternative. "We use cookies because
they're more secure than localStorage" without that nuance is the weak version.

---

### Q9. [Advanced] What's the biggest remaining security risk in this system?

**Strong answer covers — pick one and be specific:**
- **`undefined` reaching a Prisma `where`** is the pattern that already caused one cross-user data
  leak; anywhere a user id flows from token to query without validation is the same bug waiting.
- **No refresh-token rotation**, so a stolen token is valid for its full lifetime with no
  revocation path.
- **Webhook endpoints**, which are unauthenticated by definition and must be verified by signature
  — an unverified payment webhook is an endpoint that grants entitlements to anyone who can POST.

Ranking them by blast radius rather than listing them is the difference between an audit and an
answer.
