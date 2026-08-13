# NextVibe — Backend: NestJS Core & Prisma

From [`../learning/backend/01-core.md`](../learning/backend/01-core.md) and
[`../learning/00-sys-design.md`](../learning/00-sys-design.md).

---

### Q1. [Beginner] 🔥 How do you approach reading someone else's codebase?

**Strong answer covers a method, not a vibe:** start from the entry point (`main.ts`) and the root
module to learn what's globally wired — pipes, guards, interceptors, config. Then read the **module
list**, because in NestJS the modules *are* the feature map. Then pick one vertical slice and follow
it end to end: controller → service → Prisma → schema. Read the schema early; the data model
constrains everything above it. Only then start reading breadth-first.

**The point to make:** you learn a codebase by tracing **one request all the way down**, not by
skimming every file. And `grep` for a distinctive string from the UI is usually the fastest route
into unfamiliar code.

---

### Q2. [Beginner] 🔥 Why NestJS rather than plain Express?

**Strong answer covers:** structure that a team doesn't have to invent — modules with explicit
dependency boundaries, DI so services are testable without manual wiring, decorator-based routing,
and first-class cross-cutting concerns (guards, pipes, interceptors, filters) instead of ad-hoc
middleware ordering. Plus TypeScript everywhere by default.

**The honest counterweight:** it's opinionated and heavier — more concepts to learn, more
boilerplate for a small service, and a layer of indirection between "a request arrives" and "this
function runs." For a five-endpoint service, Express wins; for a platform with a dozen feature
modules and shared concerns, the structure pays for itself.

---

### Q3. [Intermediate] 🔥 Explain the module system. What do `imports`, `providers`, `exports` do?

**Strong answer covers:** `providers` are what this module can inject; `exports` are what *other*
modules may inject from it; `imports` are the other modules whose exports you want. Nest builds a
DI container per module, so a provider not exported is genuinely private — which is the mechanism
that keeps feature boundaries real rather than conventional.

**The common error to name:** "Nest can't resolve dependencies of X" almost always means the
provider exists but its module didn't `export` it, or the consuming module didn't `import` that
module. And `forwardRef` exists for circular imports, which is usually a signal that two modules
should be one, or that a third shared module is missing.

---

### Q4. [Intermediate] 🔥 What are the cross-cutting concerns and where does each belong?

**Strong answer covers the four and their distinct jobs:**
- **Guards** — "may this request proceed?" Run before the handler, return boolean. Auth lives here.
- **Pipes** — transform and validate inputs. `ValidationPipe` + `class-validator` on DTOs.
- **Interceptors** — wrap the handler; response shaping, logging, timing, caching.
- **Exception filters** — turn thrown errors into HTTP responses consistently.

**The rule:** if it applies to many endpoints and isn't business logic, it belongs in one of these,
not copy-pasted into controllers.

---

### Q5. [Intermediate] How does `class-validator` actually work in NestJS?

**Strong answer covers:** decorators on the DTO record validation metadata; `ValidationPipe` reads
that metadata, instantiates the DTO from the incoming JSON, and validates it, throwing a 400 with
the details on failure. Two things people miss: **the pipe must be applied** (globally or
per-route) or the decorators are inert; and `transform: true` is what actually converts the plain
object into an instance of your class (and coerces types) — without it, a `@Type`-decorated nested
object never becomes what you think it is.

**Security-relevant setting:** `whitelist: true` strips undeclared properties, so a client can't
smuggle extra fields into an object you later spread into a database write.

---

### Q6. [Advanced] 🔥🔥 `GET /users/me` returns 404 with "user not found". Why?

**Strong answer covers:** NestJS matches routes **in declaration order**, and `:id` is a wildcard
that matches *any* segment — including the literal `"me"`. If `@Get(':id')` is declared before
`@Get('me')`, the parameterised route intercepts, the service calls `findById("me")`, Prisma finds
nothing, and you get a `NotFoundException`.

**The rule:** **static routes must be declared before parameterised ones** in the same controller.
This applies to every `/resource/:id` versus `/resource/some-word` pair, and it's a silent bug —
nothing warns you, and the error you get points at the database.

---

### Q7. [Advanced] 🔥 "Duplicate controller routes: the silent killer." What happens?

**Strong answer covers:** if two handlers (in the same controller, or in two controllers sharing a
path prefix) register the same method + path, **the first one registered wins and the second is
never called** — with no warning at startup. So you edit the handler you found, redeploy, and
nothing changes, because the request is being served by a different function entirely.

**How to catch it:** enumerate the registered routes at boot (Nest's router explorer, or the startup
log) rather than trusting the file you're reading. The diagnostic instinct — "am I even editing the
code that runs?" — is what the question is really testing.

---

### Q8. [Intermediate] 🔥 Why does a wrong HTTP method give 404 rather than 405?

**Strong answer covers:** routing matches on **method + path together**. A `POST` to a path that
only has a `GET` handler doesn't match any route, so it falls through to the not-found handler — the
framework never concludes "the path exists but the method is wrong", because it isn't doing a
two-stage lookup. Practical consequence: a 404 during integration work usually means a **method**
mismatch or a **prefix** mismatch (a missing global prefix like `/api`), not a missing endpoint.

---

### Q9. [Advanced] 🔥🔥 New users appeared to have thousands of followers. What was the bug?

**The best backend bug in the project. Tell it precisely.**

**Strong answer covers:** in Prisma, `undefined` and `null` in a `where` clause mean completely
different things —

```ts
where: { followerId: undefined }  // field IGNORED — equivalent to where: {}
where: { followerId: null }       // filters for rows where the column IS NULL
```

So when the JWT payload wasn't parsed correctly at the social controller layer and `userId` arrived
as `undefined`, `findMany({ where: { followingId: userId } })` degraded into `findMany({})` — and
returned **every follow record in the database**. A brand-new user appeared to be followed by the
entire platform.

**Why it's a *security* bug, not just a display bug:** the same pattern on any user-scoped query
returns other people's rows. `undefined` in a filter is a silent authorisation bypass.

**The fix pattern:** validate that the identifier is actually a string before it reaches Prisma —
guard at the controller boundary, and treat "missing user id" as a 401, not as an empty filter.

---

### Q10. [Intermediate] 🔥 Prisma transactions — two patterns, two use cases.

**Strong answer covers:**
- **Array/batch form** — `$transaction([a, b, c])`: independent operations, all-or-nothing, no logic
  between them. Efficient, single round trip.
- **Interactive form** — `$transaction(async (tx) => {...})`: read, branch, then write inside one
  transaction. Required whenever a later write depends on an earlier read.

**The trap:** inside the interactive callback you must use `tx`, not the outer `prisma` client. A
query issued through the outer client runs **outside** the transaction — it compiles, it works, and
it silently isn't atomic. Also: interactive transactions hold a connection and have a timeout, so
nothing slow (an HTTP call to a payment provider) belongs inside one.

---

### Q11. [Advanced] 🔥 What's the tier-capacity pattern, and why derive values server-side?

**Strong answer covers:** capacity is a function of the tier the organiser selected, so the server
looks up the tier and derives the capacity itself rather than accepting a `capacity` field from the
client. Any value the client sends is a value the client can lie about — accepting it means a
crafted request buys a bigger event than it paid for.

**The general rule:** **derive anything with commercial or security consequences from server-side
state.** The client sends *intent* (which tier), never *consequences* (how many seats, what price,
what role).

---

### Q12. [Intermediate] What are NestJS lifecycle hooks and where did you actually need one?

**Strong answer covers:** `onModuleInit` / `onApplicationBootstrap` for setup once dependencies are
resolved (connecting a client, registering schedulers, warming a cache), and
`onModuleDestroy` / `beforeApplicationShutdown` for graceful teardown — closing DB and socket
connections, draining in-flight work. The point of the shutdown half: a process killed without
closing connections leaves sockets hanging and in-flight requests dropped, which shows up as
mysterious errors in whatever was talking to you during a deploy.

---

### Q13. [Intermediate] 🔥 "The Prisma schema-code sync error" — what is it?

**Strong answer covers:** the generated Prisma client is a build artefact of the schema. Edit the
schema without regenerating and the client's types no longer describe the database — you get errors
about fields that plainly exist, or worse, code that compiles against a stale client and fails at
runtime. The rule: **`prisma generate` after every schema change**, and treat the generated diff as
part of the same commit. In CI, generation must be a build step, not something assumed to have
happened locally.

---

### Q14. [Advanced] What's missing from this backend, and what would you build first?

**Strong answer covers — pick real gaps and rank them:** automated tests around the money and
authorisation paths first (payments and role checks are where silent bugs cost the most);
structured logging with request correlation, because debugging a distributed flow across webhook →
service → socket currently means reading three unlinked log streams; rate limiting on the public and
auth endpoints; and a consistent error-shape contract so the frontend's universal handler has
something reliable to switch on.

**The framing that lands:** rank by *cost of being wrong*, not by effort. Payments and auth first,
conveniences later.
