# NextVibe — Backend Payments: Stripe, PaymentIntents & Webhooks

New file (2026-09-25), started while adding Stripe for the mobile app. See also
`learning/backend/06-money-ledger-and-payouts.md` (Part 29 — a unique constraint as an
idempotency key, which this file builds on) and `learning/backend/03-modules.md` (the
payments module).

This file is written as we go. Entries marked **My answer** are my own reasoning, in my
words, from mentor questions — followed by the sharpened version.

---

## Part 39 — Who Decides That a Payment Succeeded?

With Stripe on mobile, the app talks to Stripe directly to confirm the card. Our server
never sees the card. So how does our server find out the payment worked? Two candidates:
the app calls our API saying "it worked", or Stripe calls our server (a **webhook** — an
HTTP request Stripe sends to a URL we give it) with the event `payment_intent.succeeded`.

**My answer:** Source of truth is `payment_intent.succeeded`, because the frontend request
can be tampered with.

**Sharpened:** Right — and there's a second reason that has nothing to do with attackers:
the app can *succeed and then die*. The user pays, loses signal, the app is killed before
it reaches our API. Stripe has the money, our database never heard. The webhook is the
only channel Stripe **retries** until we acknowledge it. So:

- The app's success callback = a **UX signal** (show "payment received", start polling).
- The webhook = the **state change** (mark paid, issue tickets).

Interview version: *"The client is untrusted and unreliable. The webhook is signed, so it
can't be forged, and retried, so it can't be lost. State changes go through the webhook."*

---

## Part 40 — Who Decides the Amount?

**My answer:** The amount is calculated on the backend. The value can be changed from the
request on the frontend.

**Sharpened:** Correct. Anything in a request body is attacker-controlled. The server
recomputes the total from the ticket tier rows in the database (`payments.service.ts`,
the pricing loop in `initiatePurchase`) and that number — never the client's — goes to
Stripe. The client should send *what* it wants (tier ids + quantities), never *how much*
it costs.

---

## Part 41 — Processing a Webhook Exactly Once

Stripe can deliver the same webhook more than once: it retries whenever it doesn't get a
2xx back, and occasionally double-delivers even on success. **Idempotent** = doing it twice
has the same effect as doing it once. Our handler must be idempotent.

### The bug in the original code

`payments.service.ts` (Bachs handler): read purchase → if `COMPLETED`, stop → else issue
tickets. Two copies arriving together:

| Time | Copy A | Copy B |
|---|---|---|
| .001 | reads `PENDING` | |
| .002 | | reads `PENDING` |
| .003 | issues 2 tickets | |
| .004 | | issues 2 tickets |

Both *read* before either *wrote*. This shape — read, decide, write — is a **race
condition**: the result depends on who gets there first.

### Option 1: conditional update

**My pick:** conditional update — "set status to COMPLETED **only if** it's PENDING, tell me
how many rows changed". Check and change become one database operation. Copy A changes 1
row and continues; Copy B changes 0 and stops. Fixes the concurrent case.

**But:** mark done → crash before tickets → Stripe retries → update changes 0 rows → stops.
Buyer paid, no tickets, forever.

### My first fix attempt, and why it failed

**My answer:** add an `isFulfilled` field — when the retry comes, check it; if fulfilled do
nothing, if not, fulfill.

**Tested against the concurrent table (my words):** *"isFulfilled is false in the second
row, then becomes true by the third row, but the fourth row fulfills the order again not
knowing the third has been updated."*

**Lesson:** it's the *same* race as the original — only the field name changed. Adding a
flag you read-then-check never fixes a race.

### Idempotency keys — useful, but not on their own

**My question:** doesn't that introduce the need for an idempotency key?

**Answer:** a key (like Stripe's `evt_123`) is just a label. "Look up the key, if not seen,
do the work and save it" is read-decide-write again — same race. A key only protects you
if the **database** refuses a duplicate (unique constraint — see `06-...` Part 29).

### The real problem: two writes, and a crash between them

| Order | Crash in the middle | Retry |
|---|---|---|
| Mark done → issue tickets | done, no tickets | skips → buyer has nothing |
| Issue tickets → mark done | tickets, not marked | issues again → duplicates |

No ordering is safe. The writes must happen **together or not at all**.

**My answer:** transactions — *"a database transaction where multiple operations go as one."*

**Sharpened:** correct. If anything fails before the transaction commits, the database
**rolls back** every write in it, as if none happened. The formal name for all-or-nothing
is **atomicity** — the A in **ACID** (a common interview question).

### Does a transaction alone stop the race?

**My answer:** *"It doesn't prevent it still, because if another one comes and both
transactions start at the same time, it doesn't prevent both from seeing a wrong state."*

**Sharpened:** correct. A transaction promises **all-or-nothing**, not **one-at-a-time**.
Two transactions can run side by side; neither sees the other's uncommitted writes, so
both read `PENDING`. (How much concurrent transactions can see of each other is called
**isolation** — the I in ACID. Postgres's default level lets exactly this happen.)

The conditional update is different: when two `UPDATE`s target the same row, Postgres
**locks the row** — the second waits until the first transaction commits, then re-checks
its `WHERE status = 'PENDING'` against the new value, finds `COMPLETED`, and changes 0 rows.

### The final design — two tools, two problems

| Problem | Fixed by |
|---|---|
| Two copies at the same moment (race) | **Conditional update** — the database lets only one win |
| Crash between marking done and issuing tickets | **Transaction** — partial work is rolled back, so the retry redoes it cleanly |

Neither alone is enough. Inside one transaction:
1. Conditional update `PENDING → COMPLETED`. If 0 rows changed → someone else did it → stop.
2. Issue tickets.
3. Commit.

Interview version: *"Webhooks are at-least-once, so the handler must be idempotent. I
claim the work with a conditional update so only one delivery can win the race, and I do
the claim and the fulfilment in one transaction so a crash rolls both back and the retry
starts clean."*

### Side question: does Postgres lock rows by default?

**My question:** is that the default behaviour of Postgres — when it's processing a row, it
locks it?

**Answer:** for **writes**, yes — automatically, no code needed. For **reads**, no.

- `UPDATE` / `DELETE` take a **row lock** on every row they change. Another write to the
  same row waits.
- The lock is held until the **transaction ends** (commit or rollback), not just until the
  statement finishes. Outside an explicit transaction, each statement is its own tiny
  transaction, so the lock is released right away.
- A plain `SELECT` takes no row lock and is never blocked by one. It reads the last
  committed version of the row. (Postgres keeps multiple versions of a row around to make
  this possible — called **MVCC**, multi-version concurrency control.)

This is *why* read-then-check breaks and the conditional update doesn't: the check in
read-then-check is a `SELECT`, and nothing stops two `SELECT`s seeing the same `PENDING`.

`SELECT ... FOR UPDATE` makes a read take the write lock, so the second reader waits. It's
another valid fix for read-then-check.

---

## Part 42 — Missing Secrets: Fail Fast

`bachs.service.ts` loads its key like this:

```ts
this.apiKey = this.configService.get<string>('BACHS_API_KEY') || '';
```

**My answer:** it falls back to an empty string so it fails silently. There is no env
validation.

**Sharpened:** right — and confirmed: `ConfigModule.forRoot` in `app.module.ts` has no
`validate` / `validationSchema`, so nothing checks env vars at startup. Precisely:

- Startup: the app boots happily with `apiKey = ''`. Health checks pass. Deploy looks green.
- First payment: Bachs rejects the empty key (401). **The first person to find out is a
  customer at checkout.**

**Fail fast** = if the app can't work correctly, refuse to start. A missing secret should
crash the boot, so the *deploy* fails loudly (you notice in minutes) instead of a customer
hitting it (you notice when someone complains). `|| ''` is the opposite: it hides the
problem until the worst possible moment.

### Where should the check live?

Options: (1) throw in the `StripeService` constructor, (2) a `stripe.config.ts` with
`registerAs`, (3) app-wide `validate` in `ConfigModule.forRoot`.

**My answer:** option 3 — the app doesn't start at all. With option 1, I think the app
starts but the bug is only found when the service is called.

**Correction (misconception):** option 1 *also* crashes at startup. NestJS creates every
provider (services are **singletons** by default — one shared instance) while the app is
booting, inside `NestFactory.create()`, before it accepts a single request. A `throw` in a
constructor therefore kills the boot. It would only be "found when called" if the service
were request-scoped or lazily loaded — which ours aren't.

What *is* true: without an explicit throw, `new Stripe('')` doesn't check the key, so a
missing key would only fail on the first API call. The fail-fast comes from the `throw`,
not from where it lives.

So the real difference between the options isn't *when* it fails — it's **scope**: one
service's keys vs. every env var in the app, checked in one central place.

### The risk of option 3

**Question:** prod has been running for months without some env var you now mark
required. What happens on deploy day?

**My answer:** it won't boot, so check prod env vars first.

**Sharpened:** yes. Plus two more guards:
- **Required vs optional.** Only mark a var required if the app genuinely can't work
  without it. Legacy/fallback vars (old Monnify keys, the four `BACHS_*_WEBHOOK_SECRET`
  fallbacks) stay optional.
- **Know what your deploy does when the new version won't boot.** Some setups keep the old
  version running until the new one is healthy; others stop the old one first → outage.

Lesson: a validation that makes things *stricter* is a breaking change to every
environment that was quietly relying on the old looseness.

**Decision:** option 3 — central `validate` in `ConfigModule.forRoot`.

---

## Part 43 — Reviewing a Fix: Check the Code, Not the Commit Message

Added 2026-10-05, after reviewing a teammate's payment commits (`59003d6` "fixed payment
races", `d53c409`, `361c003`). The messages said the races were fixed. Reading the code
showed one of four backlog items was attempted, and that one had two gaps.

**How to review a fix:**
1. Restate the bug as a concrete failure ("two requests at the same instant both create a
   purchase"), not as a label ("payment races").
2. Walk that failure through the *new* code, step by step, with two requests side by side.
3. Check every path, not only the one that was edited. Here Stripe was safe and Bachs wasn't.
4. Look for what the change touched without saying so. `361c003` silently swapped
   `pnpm-lock.yaml` for `package-lock.json`.

A commit message describes what someone *meant* to do. Only the code tells you what it does.

---

## Part 44 — A Success Path That Never Sets the Final State

The Bachs handler issued tickets but **never set the purchase to `COMPLETED`**. Stripe's
path did. The two providers looked parallel, but one skipped the last step.

Consequences:
- `GET /payments/verify` told paid buyers "pending" forever.
- Every webhook retry and every callback-page poll re-ran ticket issuance.

### Why there weren't duplicate tickets anyway: accidental safety

The retry's ledger credit hit the unique index `(type, sourceType, sourceId)`. In Postgres,
**any error inside a transaction aborts the whole transaction**. Even the ledger service's
`catch (P2002) → findUnique` fails, with "current transaction is aborted". So the tickets
created earlier in that transaction rolled back too.

That's safety by accident. Move the ledger write outside the transaction, or make it skip
duplicates with `ON CONFLICT DO NOTHING`, and duplicate tickets start immediately.

**Rule:** if correctness depends on a side effect you didn't design for, it isn't correct
yet. Make the guard explicit: the claim (Part 41) at the *top* of the transaction.

**Fix:** the Bachs path now calls the same `fulfilPurchase` as Stripe. The old unguarded
functions were deleted so nobody calls them again.

---

## Part 45 — A Lock Only Covers Its Own Transaction

`pg_advisory_xact_lock(key)` = "only one transaction holding this key at a time". The
`xact` matters: **it's released when the transaction commits.**

The teammate's version:

```ts
const order = await this.prisma.$transaction(async (tx) => {
  await tx.$executeRaw`SELECT pg_advisory_xact_lock(hashtext(${eventId}))`;
  // ...check availability...
});                                      // ← commit: lock released here
const purchase = await createPendingPurchase(order);   // ← reservation written here
```

The lock guarded the *check* but not the *write*. A double tap:

| Step | Tap A | Tap B |
|---|---|---|
| 1 | lock → check (no pending) → commit, lock released | waiting |
| 2 | writing purchase row… | lock → check: still sees nothing |
| 3 | committed | writes a second purchase |

**Rule:** a lock protects only what happens *before its transaction commits*. Everything
the lock is meant to make safe has to be inside that transaction:
check → decide → **write**.

**Fix:** `priceOrder` + `createPendingPurchase` merged into `reserveOrder`, with one
transaction for the lock, the check and the insert.

---

## Part 46 — Shared Resources Need Global Counts

Seats belong to the **event**, not to a buyer. The held-seat count was filtered by
`userId`, so it only saw *this* buyer's checkouts. Two strangers could both get the last
seat.

Two different questions were mixed together in one query:
- "Has **this buyer** already got this cart open?" → filter by user. Used to reuse a double tap.
- "How many seats are **held by anyone**?" → no user filter. Used for availability.

**Rule:** for every filter in a query, ask whose resource it is. Capacity, stock, and
unique usernames are global. Carts, drafts and preferences are per user.

---

## Part 47 — Money Is Never a Float

```js
1.15 * 3        // 3.4499999999999997
0.1 + 0.2       // 0.30000000000000004
```

Binary floats can't represent most decimals exactly. The checkout summed
`Number(price) * qty`. `toStripeAmount` (correctly) throws if an amount has more decimal
places than the currency allows, so **some prices couldn't be paid by card at all**.
The error was a 500, not a wrong charge, but only because of that strict check.

**Rule:** keep money in a decimal type (`Prisma.Decimal`) or integer minor units (kobo,
cents) the whole way through, and convert to a JS number once, at the edge, only where an
API demands it. See also `06-money-ledger-and-payouts.md` (the ledger stores money as Decimal).

---

## Part 48 — 404, Not 403, for Other People's Records

`GET /payments/verify/:purchaseId` required a login but never checked *whose* purchase it
was. Any signed-in user with an id got the buyer's tickets, including the QR codes used at
the door. This is an **IDOR** (insecure direct object reference): authenticated, but not
authorised for *that object*.

Fix: compare `purchase.userId` with the caller. Then decide which status to return:
- `403 Forbidden` says "it exists, but it's not yours". That still leaks that the id is real.
- `404 Not Found` makes someone else's record identical to a missing one. **Preferred.**

Also: run the ownership check **before** any side effect (here, a Stripe lookup that can
trigger fulfilment).

**Rule:** for every route that takes an id, ask: "who is allowed to see *this* row?"
Logging in answers "who are you", not "can you see this".

---

## Part 49 — Resume, Don't Refuse

The double-tap guard found an open checkout and said "already in progress" for 30
minutes, even when the buyer had just closed the Payment Sheet and wanted to try again.
The guard was correct but made for a bad experience.

Better: an idempotent checkout **gives back the same in-flight thing**:
- Bachs: the same `checkoutUrl`.
- Stripe: the same PaymentIntent's `client_secret`. It's refused only if Stripe says it's
  already `succeeded`/`processing`, since paying again would double-charge.

Two follow-ons:
- The provider is part of the cart key. A web checkout page must never be handed back to
  the mobile app.
- A checkout that can never complete (the provider setup failed) is marked `FAILED`
  straight away, so its seats aren't held for nothing.

---

### Self-quiz (answer on paper, then check the Parts above)

1. A handler reads `status`, and if it isn't `COMPLETED`, issues tickets. Name the bug and
   the one-statement fix. (Part 41)
2. Why didn't the Bachs path create duplicate tickets, even though it never set
   `COMPLETED`? Why is that not good enough? (Part 44)
3. An advisory lock is taken, the check runs, the transaction commits, then the row is
   inserted. What can still go wrong? (Part 45)
4. Which filter belongs on "held seats", and which on "my open cart"? (Part 46)
5. What does `1.15 * 3` give in JS, and what broke because of it? (Part 47)
6. Another user's purchase id: 403 or 404, and why? (Part 48)
7. The buyer closes the Payment Sheet and taps Buy again. What should the server return?
   When should it refuse? (Part 49)
