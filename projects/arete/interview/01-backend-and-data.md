# Arete — Backend & Data

From [`../learning/backend/01-fundamentals-and-nestjs.md`](../learning/backend/01-fundamentals-and-nestjs.md),
[`02-prisma-and-data-modeling.md`](../learning/backend/02-prisma-and-data-modeling.md),
[`04-auth.md`](../learning/backend/04-auth.md).

---

### Q1. [Beginner] 🔥 Describe the request path through the backend.

**Strong answer covers:** request → guard (authentication/authorisation, runs before the handler) →
DTO binding and validation via `class-validator` → controller (HTTP only: route, params, response
shape) → service (business logic, no HTTP knowledge) → Prisma → PostgreSQL. Modules wire it
together and declare what each part can inject.

**The rule to state:** the controller is the API, the service is the product. If a service returns
HTTP status codes or a controller contains business rules, the layering has failed and every test
gets harder.

---

### Q2. [Intermediate] What do guards, DTOs and validation each actually do?

**Strong answer covers:** a **guard** returns true/false before the handler runs — it's where
"is this request allowed?" lives, and returning false short-circuits with a 401/403 without the
handler ever executing. A **DTO** is the typed shape of the request body, decorated with
`class-validator` constraints. Validation only happens if the `ValidationPipe` is applied (globally
or per-route) — the decorators are inert on their own, which is the classic "my validation isn't
running" bug.

**Detail worth adding:** `whitelist: true` on the pipe strips properties not declared on the DTO, so
a client can't smuggle extra fields into an object you then spread into a database write. That's a
security setting, not a tidiness one.

---

### Q3. [Intermediate] 🔥 "The schema is the contract" — what does that mean with Prisma?

**Strong answer covers:** `schema.prisma` is the single declaration of the data model; the client is
**generated** from it, so every query is typed against the actual schema. Rename a column and every
reference fails to compile rather than returning `undefined` at runtime. Migrations are generated
from schema diffs, so the schema file and the database converge by construction rather than by
discipline.

**The habit that goes with it:** regenerate the client after every schema change, and treat the
generated diff as part of the same commit.

---

### Q4. [Intermediate] 🔥 What do Prisma transactions give you, and which of the two forms do you use when?

**Strong answer covers:** two forms —
- **Array form** — `$transaction([op1, op2])`: a set of independent operations, all-or-nothing, no
  logic between them. Simple and efficient.
- **Interactive form** — `$transaction(async (tx) => { ... })`: you get a transactional client and
  can read, branch, and write inside one transaction. Required whenever a later write depends on an
  earlier read.

The guarded decrement (see [02-patterns-and-postmortems.md](02-patterns-and-postmortems.md) Q1) uses
the interactive form because it needs to inspect the update's `count` and throw to roll back.

**The trap:** any query issued through the outer `prisma` client inside an interactive transaction
callback runs *outside* the transaction. It compiles, it works, and it silently isn't atomic.

---

### Q5. [Advanced] 🔥 Why does an empty `$transaction([])` matter?

**Strong answer covers:** it **succeeds**. That's the root of the launch-week seed race — a
`pillars.map(...)` over an empty array produced an empty transaction, nothing threw, and the code
continued to mark onboarding complete with zero pillars attached. **Vacuous success**: an operation
that did nothing reporting that it worked. Full story in
[02-patterns-and-postmortems.md](02-patterns-and-postmortems.md) Q7.

---

### Q6. [Beginner] 🔥 Explain the two-token JWT scheme.

**Strong answer covers:** an **access token** (15 minutes) sent on every request, and a **refresh
token** (30 days) sent only to `/auth/refresh` to mint new access tokens. The guard verifies the
access token's signature with no database hit, which is the whole point of JWT — stateless speed.

**The trade to name explicitly:** you cannot revoke an access token before it expires. That's why the
TTL is short: 15 minutes is the actual blast radius of a stolen token. The refresh token is
long-lived but touches exactly one endpoint, so it can be stored server-side and revoked there.

---

### Q7. [Intermediate] 🔥 bcrypt for passwords, SHA-256 for reset tokens. Why different algorithms?

**Strong answer covers:** they're solving opposite problems.
- **Passwords** are low-entropy and human-chosen, so the hash must be **deliberately slow** —
  bcrypt has a tunable work factor and a built-in per-password salt, making offline brute force
  expensive.
- **Reset tokens** are high-entropy random values you generated. There's nothing to brute-force, so
  slowness buys nothing; you just need a one-way digest so a database leak doesn't hand out valid
  reset links. SHA-256 is fast and sufficient.

**The one-line version:** slow hashing defends against weak inputs; fast hashing is fine when the
input is already random. Using bcrypt for tokens would just make your reset endpoint slow;
using SHA-256 for passwords would be a serious vulnerability.

---

### Q8. [Intermediate] How does the refresh flow work server-side, and what can go wrong?

**Strong answer covers:** the client posts its refresh token, the server validates it (signature,
expiry, and ideally that it hasn't been revoked), and issues a new access token. Failure means a
forced logout. The problems worth naming: a refresh token that never rotates is a 30-day credential
that survives every access-token expiry; and without server-side tracking there's no way to log a
user out of a stolen session. Rotation-on-use plus reuse detection (an old refresh token being
presented means it was stolen — revoke the family) is the standard fix.

The client-side half of this is the more interesting story — see
[03-mobile-react-native.md](03-mobile-react-native.md) Q3.

---

### Q9. [Intermediate] 🔥 How is scheduled work registered, and why "idempotently on boot"?

**Strong answer covers:** BullMQ schedulers are upserted at startup:

```ts
await this.questQueue.upsertJobScheduler('daily-quest-gen', { pattern: '0 0 * * *' }, {...});
```

**Upsert, not add** — because boot happens on every deploy and every restart. `add` would accumulate
duplicate schedulers, and duplicate schedulers mean every user's quests generated twice. Idempotent
registration means the schedule is declared in code and converges to the same state no matter how
many times the process starts.

**The schedule worth knowing:** midnight quest generation, 23:59 streak evaluation, 7am and 10pm
reminders, hourly XP aggregation, six-hourly leaderboard updates — all in UTC, with Lagos at UTC+1,
which is exactly the sort of offset that produces "why did the reminder arrive at the wrong hour"
bugs.

---

### Q10. [Advanced] 🔥 One user's data breaks a batch job. What happens?

**Strong answer covers:** each processor extends `WorkerHost` and wraps **per-user** work in
try/catch, counting successes and failures:

```ts
for (const user of users) {
  try { await this.quests.generateQuestsForUser(user.id); generated++; }
  catch (e) { failed++; this.logger.error(...); }
}
```

Without that, one bad row aborts the loop and every user after them silently gets no quests that
day — and the failure looks like "the job crashed" rather than "user X has bad data." The logged
counts are what make the difference visible.

**Same principle, different project:** `Promise.allSettled` over `Promise.all` in `my-applicant`.
Decide per item whether a failure is fatal or degrading.

---

### Q11. [Advanced] The streak evaluator runs at 23:59. What's fragile about time-based batch logic?

**Strong answer covers:** timezones (23:59 UTC is not midnight for the user, so "yesterday" is
ambiguous), a run that overlaps midnight and evaluates the wrong day, a missed run leaving a day
un-evaluated forever, and daylight-saving shifts producing a duplicated or skipped hour. The robust
shape is to make the job **idempotent and date-parameterised** — it evaluates a specified date and
can be re-run for a missed one — rather than implicitly evaluating "now minus a bit". The ledger
(`StreakEvent` rows per day) is what makes that possible, because "was this day already evaluated?"
is a query rather than an assumption.

---

### Q12. [Intermediate] Which queries do you actually use daily, and where do people get Prisma wrong?

**Strong answer covers:** `findUnique`/`findMany`/`create`/`update`/`updateMany`/`upsert`, with
`select` and `include` controlling the shape. The mistakes worth naming: **N+1** from looping and
querying instead of using `include` or a single `findMany` with an `in` filter; over-fetching by
omitting `select` so every column crosses the wire; and confusing `update` (throws if not found)
with `updateMany` (returns a count, and returning `count: 0` is exactly what makes the guarded
decrement work).
