# NextVibe — Wishlist, Spin the Wheel & Multi-tenancy Planning

Built 2026-11-02. From
[`../learning/backend/10-wishlist-and-spin-wheel.md`](../learning/backend/10-wishlist-and-spin-wheel.md),
[`../learning/frontend/14-wheel-ui-and-list-vs-detail-data.md`](../learning/frontend/14-wheel-ui-and-list-vs-detail-data.md),
[`../learning/11-multi-tenancy-planning.md`](../learning/11-multi-tenancy-planning.md).

Three features and one bug, all in one day. The technical questions come first, then the
"tell me about a time…" stories at the bottom.

---

## Wishlist (event gift registry)

### Q1. [Intermediate] 🔥🔥 You built a gift registry where the money never touches your platform. How do you track progress you can't see?

**Strong answer covers:** guests transfer straight to the organizer's bank account, so NextVibe has
no webhook, no ledger entry, nothing to verify. Three options: the guest reports it and the
organizer confirms it, the guest's report counts straight away, or no tracking at all. I picked
**report-then-confirm**: a contribution starts `PENDING` and the organizer marks it `CONFIRMED` or
`REJECTED` after checking their bank app. Only confirmed amounts count toward the progress bar and
"goal reached".

**Detail worth adding:** this is a **state machine where the trusted party is a person, not a
payment provider.** The design question was "who is allowed to move it to CONFIRMED?", the same
question as webhook verification, with the organizer playing the role Stripe normally plays.
Reports that count immediately would let anyone push an item to "fulfilled" as a prank.

---

### Q2. [Intermediate] 🔥 The organizer's bank details have to be public. How did you still protect them?

**Strong answer covers:**
- **Separate public data from private data at the table level.** Organizers already had a
  `PayoutAccount` table built so the full account number never leaves the server (lists show only
  `last4`). I stored the wishlist's bank details **on the wishlist row** instead of reusing it. One
  wrong `select` on a shared table would leak payout details.
- **Keep them out of the default response.** Events are public by default, so anything in the
  event or wishlist payload is scrapeable. The details come from a separate
  `GET …/wishlist/payment-details`, called only when someone taps Contribute, rate-limited to
  10/min per IP.
- **Guard the one join that could leak them.** Event details needed a `hasWishlist` flag, so that
  query does `wishlist: { select: { isEnabled: true } }`, with a comment saying never to widen it.

**Detail worth adding:** "you can't make it secret, the organizer *wants* guests to see it" is
the honest framing. The goal is to stop **casual collection** (bots crawling event pages), not to
hide it. Saying what a control does *not* protect against is what makes the answer credible.

---

### Q3. [Advanced] 🔥 How do you attach a guest's past actions to their account later, without letting someone steal them?

**Strong answer covers:** guests can give with just a name and an optional email. Later, when
someone signs in, `linkGuestContributions(userId, email)` sets `userId` on matching guest rows
(`userId IS NULL`, case-insensitive email). It's called on login, email verification and both
Google sign-in paths.

**The security catch:** linking by email is only safe if the email is **verified**. Otherwise I
could register with *your* address and inherit your gift history. So password login links only
when `isEmailVerified`; Google sign-ins count as verified because Google has already proved the
address.

**Detail worth adding:** it's **best-effort**. It catches and logs its own errors, because a
nice-to-have side effect must never break the sign-in it runs inside. Same principle as "a failed
notification must not fail the payment".

---

### Q4. [Intermediate] Why did the server compute "remaining amount" instead of the frontend?

**Strong answer covers:** the frontend has a written rule (`shared/lib/money.ts`): the backend
sends money as **strings** (Postgres `DECIMAL`), and the client formats them but never does
arithmetic on them, because JS numbers can't represent every decimal exactly. So "Pay in full"
fills in a `remainingAmount` the server computed with `Prisma.Decimal`
(`max(price − confirmed, 0)`).

**Detail worth adding:** the progress bar width *is* computed client-side
(`confirmed / price × 100`). That's fine because it's a **display ratio, not money**. Being able
to say where the line is matters more than following the rule everywhere.

---

### Q5. [Intermediate] Why does the reorder endpoint take the whole order instead of "swap A and B"?

**Strong answer covers:** `PUT /items/order` takes every live item's id in display order and sets
`sortOrder = index` in one transaction. It validates that the list is exactly the live set: same
size, no duplicates, nothing missing.

**Detail worth adding:** a swap works on positions you *think* exist. If two items ever share a
`sortOrder` (an organizer set one by hand, or a delete left gaps), swapping their values does
nothing. Sending the whole order makes the operation **idempotent and self-healing**: whatever
state the data was in, it ends up correct.

---

## Spin the wheel

### Q6. [Advanced] 🔥🔥 Two people spin for the last VIP prize at the same instant. How do you make sure only one wins?

**Strong answer covers:**
- **The race:** both requests read "1 left", both pass the check, both create a reward. Classic
  **check-then-act**. The same race lets one person double-tap and get two spins.
- **The fix:** every spin runs in a transaction that first takes a **row lock on the wheel
  round**: ``SELECT id FROM game_rounds WHERE id = $1 FOR UPDATE``. The second spin waits until
  the first commits, then re-reads stock and spin counts.
- **Why that lock and not another:** a unique constraint can't express "at most N rewards for this
  tier", and optimistic retries add complexity for no gain. Serialising per wheel is cheap
  because a wheel at a party sees a few spins a second at most, and different wheels don't block
  each other.

**Detail worth adding:** stock isn't a decremented counter. It's **derived**: `quantity` minus the
number of `Reward` rows for that tier. Deriving it means there's no second number that can drift
out of sync with the rewards themselves, and the lock is what makes deriving it safe.

---

### Q7. [Advanced] 🔥 How does the server pick a weighted random result, and why not let the client do it?

**Strong answer covers:**
- **Server-authoritative:** the client calls `POST /spin`, gets the slice, then animates to it.
  If the browser chose, anyone could edit the request and win the VIP upgrade every time.
- **Weighted pick:** rarity maps to weights in code (`COMMON 10 : RARE 3 : VERY_RARE 1`). Sum the
  weights of the slices still in stock, draw `crypto.randomInt(total)`, and walk the slices
  subtracting weights until the draw goes below zero.
- **Weights in code, rarity in the database.** The schema stores `rarity` as an enum, and the
  numbers live in `spin-wheel.constants.ts`, so tuning odds doesn't need a migration.

**Detail worth adding:**
- **Fairness disclosure:** every slice is drawn the same size, so slice size doesn't show your
  chance. Rare and very-rare slices therefore carry a visible label. Equal slices with hidden
  weights would feel like a trick, and labels keep the wheel readable *and* honest.
- **The edge case:** if only "Retry" slices are left in stock, a spin would hand out retries
  forever. So "no prize slices left" ends the wheel instead.

---

### Q8. [Advanced] 🔥 You added a new game type to an existing games system. How did you decide what to reuse?

**Strong answer covers:** my first instinct was a separate module, because a wheel has no
questions, answers or scores. The product owner pushed back that it's a *game*. When I looked
again, I'd been judging the wrong layer: the **round internals** don't fit, but the **layer around
them** fits almost perfectly:
- `GameSession` gives plan quota, scheduling and open/close status, and the Games tab.
- `GameRound` has its own `gameType`, so a wheel is just one round type inside a session.
- `GameRewardTier` already supports per-round prizes, so they became the wheel's slices.
- `Reward` already tracks WON → CLAIMED → APPROVED → FULFILLED, with an organizer queue.

What I added: a `SPIN_WHEEL` type, `rarity`/`isRetry` on tiers, `quantity` made nullable to mean
unlimited, a `claimCode` on `Reward`, and a `WheelSpin` table. `GameEntry` is unique per
(round, user), so it can't record a retry.

**Detail worth adding:** reuse also means **turning off behaviour that doesn't apply**. When a
round ends, the existing code hands out that round's tiers by leaderboard rank. A wheel has no
leaderboard, so `distributeRoundRewards` returns early for wheel rounds, and the normal
answer/submit endpoints reject them. Plugging into a system means checking every place it acts
on its own, not just the places you call.

---

### Q9. [Intermediate] Design a claim code that bar staff can use.

**Strong answer covers:**
- **Format:** `XXX-XXX` from an alphabet with no `0/O` or `1/I/L`, so it can't be misheard at a
  loud venue. Generated with `nanoid`'s `customAlphabet`, which uses a cryptographic random source
  without bias. 31⁶ ≈ 887 million combinations.
- **Uniqueness:** `@unique` on `Reward.claimCode`. Inside a transaction, a unique violation
  aborts everything, so the code checks first and retries up to 5 times rather than catching the
  error.
- **Forgiving input:** staff type `vx7k2p` or `VX7 K2P`. Normalise by uppercasing and stripping
  separators.
- **Single use:** redeem moves the reward straight to `FULFILLED` using
  `updateMany where status in (WON, CLAIMED, APPROVED)`. If two staff redeem at once, one update
  matches zero rows and gets "already redeemed".

**Detail worth adding:** lookup and redeem are **separate calls**, so staff see who won what
before committing. Merging them would save a tap but lose the chance to check.

---

## Bugs and planning

### Q10. [Intermediate] 🔥 "Multi-photo postcards only show one slide, but it used to work." Find it.

**Strong answer covers:** the viewer built the carousel from the `postcard` prop. Opened from the
feed, that prop comes from the **list** endpoint, and `findAll` fetches
`media: { take: 1 }` for thumbnails. The viewer *did* fetch the full postcard
(`GET /postcards/:id`, every media item) and polled it every 5 s, but only used it for author and
comments. Fix: build slides from `freshData.media`, and fall back to the prop while it loads.

**Detail worth adding:** two things made it confusing.
- `take: 1` had been there since April, so the backend didn't change. Something on the frontend
  must have stopped passing full data.
- There was a **file and a folder with the same name**: `postcard-viewer.tsx` and
  `postcard-viewer/index.tsx`. The import resolves to the **file**. The folder's `index.tsx` was
  1,250 lines of commented-out code, an easy place to read the wrong viewer.

The general lesson: **list payloads and detail payloads are different shapes**. A component that
can be opened from both must say which one it trusts.

---

### Q11. [Advanced] 🔥 How would you turn a single-tenant app into a white-label, multi-tenant platform?

**Strong answer covers (the order to say it in):**
1. **Choose the isolation model first:** a shared schema with `tenantId`, a schema per tenant, or
   a database per tenant. Shared-schema is cheapest and the usual starting point.
2. **Enforce it centrally, not by discipline.** On Prisma, a client extension can add the
   `tenantId` filter automatically, but `$queryRaw` bypasses it. **Postgres Row-Level Security**
   is the database-level backstop, with the catch that you set the tenant per transaction, which
   connection pooling complicates. Best answer: both.
3. **Resolve the tenant for every request:** custom domain, then subdomain, then a header for
   mobile. A header must be checked against the tenant inside the JWT, or it can be spoofed.
4. **Don't forget inbound callbacks:** payment webhooks and OAuth redirects arrive with no tenant
   Host header. With per-tenant payment keys, you need the tenant *before* you can check the
   webhook signature.
5. **Treat cross-tenant identity as a product decision:** can one person use two tenants' apps
   with one account?
6. **Migrate in phases:** create tenant #1, backfill `tenantId`, then add NOT NULL, with a
   rollback at each step.

**Detail worth adding:** I reviewed a planning prompt for exactly this. Its biggest flaw was that
it **chose the solution before the discovery step**: it told the agent to use an ORM subscriber
and nestjs-cls before the agent had looked at the stack. That would have steered the agent past
the most important trade-off, RLS versus app-layer filtering.

---

## Behavioural stories

### S1. A product decision where the stakeholder was right and I was wrong
*Answers: "a time you changed your mind", "working with stakeholders", "a trade-off".*

Designing the wishlist, I recommended that an item **close automatically** once its confirmed
total hit the price, to stop overfunding. The product owner chose the opposite: items stay open
until the organizer closes them, because "people wanna give". At weddings and birthdays,
stopping a guest from giving is the real failure. When I traced the money, the argument held:
every contribution lands in **one bank account**, so per-item totals are only labels. Overfunding
a blender costs nobody anything. I'd been designing as if each item were its own pot. We kept
items open, made "Goal reached 🎉" a celebration rather than a stop, and added a "just give"
item with no price for people who don't want to pick one.
**What I'd do differently:** ask "where does the money actually end up?" before proposing a rule
about money.

### S2. Reusing a system I'd first dismissed
*Answers: "a design you'd do differently", "receiving feedback", "working in an existing codebase".*

For spin the wheel I first proposed a standalone module, since a wheel has none of the games
system's questions or scores. The product owner said it's a game, so it belongs in gamification.
They then sharpened it: not a whole game session, but **a round inside one**. Reading the code
again, the layer around rounds (paid plan quota, scheduling, open/close, the rewards queue) was
exactly what the wheel needed. I'd only compared the inside of a round. The result reuses five
existing models and adds one table. I also had to switch off behaviour that would have fired
wrongly: rank-based prize distribution when a round ends.
**What I'd do differently:** compare against the whole system, not the nearest component.

### S3. A bug the user remembered working
*Answers: "a bug you're proud of finding", "debugging under ambiguity".*

"Postcards with several photos show only one, it was there before." I traced the viewer's data
source rather than the carousel markup, and found the slides came from list data that only ever
contains one media item, while the full postcard was already being fetched and ignored. The fix
was one `useMemo`. The detective work was ruling out the backend (`take: 1` unchanged since
April) and spotting that a dead, same-named folder could have sent me into the wrong file.

### S4. Planning a high-risk change with an AI agent
*Answers: "how do you use AI tools", "planning a large change".*

I wrote a planning-only prompt for making NextVibe white-label, then had it reviewed before
running it. The review found it was too big for one pass and should be split into discovery
then plan. It also named a solution before discovery, missed webhook and OAuth tenant
resolution, and left out offboarding and data-protection requirements. It also recommended
fixing existing security debt as a "phase 0" before any multi-tenant work.
**What I learned:** a prompt for an agent is a spec. It deserves review like one, and "don't
assume the stack" means not prescribing the tools either.
