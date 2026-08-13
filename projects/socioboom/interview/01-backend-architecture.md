# SocioBoom — Backend Architecture

From [`../learning/backend/01-foundations.md`](../learning/backend/01-foundations.md),
[`02-architecture-and-modules.md`](../learning/backend/02-architecture-and-modules.md),
[`03-database-prisma.md`](../learning/backend/03-database-prisma.md),
[`04-auth-and-security.md`](../learning/backend/04-auth-and-security.md).

---

### Q1. [Intermediate] 🔥 Describe the five-file module pattern and why you standardised on it.

**Strong answer covers:** each feature is a folder with the same five files — **routes** (paths and
middleware), **controller** (HTTP in, HTTP out, no business logic), **service** (the actual logic, no
knowledge of req/res), **types/DTOs** (the contract), and **validation** (schema for the input).

**Why it's worth the ceremony:** every feature looks the same, so finding "where does X happen" is
mechanical rather than exploratory; the service is unit-testable without HTTP; and adding a feature
is filling in a known shape rather than making five design decisions. Express gives you no structure
at all, so you either impose one or end up with routes that call Prisma inline.

**The honest cost:** a two-endpoint feature gets five files. That's the price of uniformity, and
it's a deliberate trade rather than an oversight.

---

### Q2. [Intermediate] 🔥 Walk me through the middleware chain in order, and explain why the order matters.

**Strong answer covers:** roughly — security headers (Helmet) → CORS → body parsing → rate limiting →
authentication → routes → 404 handler → error handler. Order is functional, not cosmetic:

- **Helmet first**, so headers are set even on responses that never reach a route.
- **CORS before anything that can reject**, or a rejection response arrives without CORS headers and
  the browser reports a CORS error instead of the real 401 — which sends you debugging the wrong
  thing entirely.
- **Body parsing before validation**, obviously, but *after* any route that needs the raw body (a
  webhook signature check needs unparsed bytes).
- **Rate limiting before auth**, so an unauthenticated flood is cheap to reject.
- **The error handler last**, because Express identifies it by its four-argument signature and only
  reaches it if it's registered after everything that might throw.

---

### Q3. [Beginner] What does the TypeScript configuration actually buy you here?

**Strong answer covers:** `strict` (the whole point — without it `strictNullChecks` is off and
`undefined` slips everywhere, which is the bug family in half of this vault), path aliases so imports
don't become `../../../`, and a build that emits to `dist/` with the runtime entry points that the
Docker image and the worker's start command reference. The detail that matters operationally: the
**worker** is a second entry point compiled from the same source, which is why `dist/worker.js` has
to exist and be started explicitly (see
[02-queues-and-deployment.md](02-queues-and-deployment.md) Q3).

---

### Q4. [Intermediate] 🔥 How does authentication work, and why Passport JWT?

**Strong answer covers:** Passport with a JWT strategy — the strategy verifies the token's signature
and attaches the decoded user to the request, and a middleware guards protected routes. Passport
earns its place mainly by giving one place where "how do we identify a user" lives, and by making it
cheap to add another strategy later (OAuth logins) without rewriting the auth middleware.

**The detail to volunteer:** the user id used in queries comes from the **verified token**, never
from a request body or param. A route that accepts `userId` from the client is an authorisation
bypass regardless of how good the token verification is.

---

### Q5. [Intermediate] 🔥 What does Helmet, CORS and rate limiting each actually protect against?

**Strong answer covers them as three distinct threats:**
- **Helmet** sets response headers that constrain the *browser* — `X-Content-Type-Options`, frame
  options against clickjacking, HSTS, a CSP if configured. It's defence in the client, not the
  server.
- **CORS** controls which **origins** may read your responses from a browser. It is not a security
  boundary against non-browser clients — curl ignores it entirely — so it protects users, not the
  API.
- **Rate limiting** protects availability and slows credential stuffing. The nuance: limits keyed by
  IP behind a proxy require `trust proxy` to be set correctly, or every request appears to come from
  the load balancer and one user's limit applies to everyone.

Saying "CORS is not an API security mechanism" unprompted is the line that lands.

---

### Q6. [Intermediate] How do you handle secrets and environment variables?

**Strong answer covers:** never in the repo; a committed `.env.example` documents required keys;
platform secret stores hold the real values. Two project-specific traps worth naming — the **worker
is a separate process and doesn't inherit the API's `dotenv` call**, so it needs its own
`import 'dotenv/config'` at the top; and a shared local `.env` between API and worker means port
collisions unless the worker's health port is env-gated.

**The most important secret in this system:** platform OAuth tokens, which are stored *at rest* in
the database (see [04-social-publishing-and-media.md](04-social-publishing-and-media.md) Q2) — that's
a different problem from an env var and deserves encryption and a rotation story.

---

### Q7. [Intermediate] 🔥 What does Prisma give you, and where does it get in the way?

**Strong answer covers:** a schema that generates a fully typed client, migrations derived from
schema diffs, and relations expressed declaratively — so a renamed column is a compile error rather
than a runtime `undefined`. Where it gets in the way: complex analytical queries where you end up
in `$queryRaw` anyway, and its JSON handling (Q9 in
[04-social-publishing-and-media.md](04-social-publishing-and-media.md)), which has genuinely
surprising semantics.

---

### Q8. [Advanced] 🔥 How do you verify a migration without access to your dev database?

**Strong answer covers:** don't confuse "the migration file exists" with "the schema changed."
`prisma migrate diff` compares two states — schema files, a live database, or migration history —
and prints the SQL to get from one to the other, so you can verify that your migration history
actually produces the schema in `schema.prisma`, with no database to connect to. `migrate status`
tells you what's applied where.

**The general principle:** a repo describes *intent*; only the database describes *state*. Verifying
against the running database (or a diff of it) is a separate act from reading the migration.

---

### Q9. [Intermediate] How do you model per-platform content in the schema?

**Strong answer covers:** a post has shared content plus `contentByPlatform` — a JSON column keyed by
platform, because each network has different length limits, formatting and mention syntax. JSON is
the right call here specifically because the shape is **open-ended and per-platform**, and adding a
seventh network shouldn't be a migration.

**The cost to name:** JSON columns aren't validated by the database and are awkward to query, so the
validation must be enforced in application code — and the `null`/`undefined`/`DbNull` distinction
becomes a real trap the moment a field needs to be *cleared*.

---

### Q10. [Advanced] Give me the tour: what modules exist and how do they relate?

**Strong answer covers a shape, not a list:** auth and users at the base; a **posts/scheduling** core
that owns content and its per-platform variants; a **connections/OAuth** module owning platform
credentials and refresh; a **publishing** layer that turns a scheduled post into platform API calls;
**queues/worker** driving the scheduled execution; **AI/agents** for review posting and pain-point
discovery; and **media** for uploads. The dependency direction worth stating: publishing depends on
connections (for tokens) and is invoked by the worker; the AI modules produce *content*, and never
publish directly — which keeps the one irreversible action (posting publicly) behind a single path.

---

### Q11. [Intermediate] 🔥 How would you add a new feature to this backend?

**Strong answer covers:** create the module folder with the five files; define the validation schema
and DTO first, because that's the contract; write the service against Prisma with no HTTP knowledge;
wire the controller and routes; register the routes in the app; add the migration if the schema
changed and regenerate the client. If it touches publishing, the platform adapter goes behind the
same interface as the existing ones so the worker needs no changes.

**The thing to emphasise:** the answer is boring, and that's the point — a good module pattern makes
"add a feature" a mechanical procedure instead of a design exercise.
