# 10 — Wishlist & Spin the Wheel

*Written 2026-11-02, from building both features in one day.*

See also: [[projects/nextvibe/learning/backend/04-games-ai|04 — Games & AI]],
[[projects/nextvibe/learning/backend/06-money-ledger-and-payouts|06 — Money, Ledger & Payouts]],
[[projects/nextvibe/learning/backend/08-payments-and-webhooks|08 — Payments & Webhooks]],
interview: [[projects/nextvibe/interview/06-wishlist-spin-wheel-and-multitenancy|06 — Wishlist, Wheel & Multi-tenancy]]

---

## Part 1 — The wishlist in one paragraph

An organizer turns on a wishlist for an event (a free toggle, unlike gamification), lists items,
and enters bank details. Guests send money **straight to that account** and then report "I sent
₦X" with their name, an optional email, an optional message, and an "anonymous" checkbox. The
organizer confirms or rejects each report. Only confirmed money counts.

```
Wishlist (1 per event)       ─ isEnabled, bankName, accountNumber, accountName, currency
  └─ WishlistItem (many)     ─ name, price? (null = "just give"), sortOrder, fulfilledAt?, deletedAt?
       └─ WishlistContribution ─ userId?, name, email?, message?, isAnonymous, amount,
                                 status PENDING|CONFIRMED|REJECTED, reviewedAt?
```

---

## Part 2 — Decisions, and why

| Decision | Chosen | Rejected, and why |
|---|---|---|
| Who confirms money | Organizer confirms each report | Counting reports immediately: anyone could fake "fulfilled" |
| Bank details storage | On the wishlist row | Reusing `PayoutAccount`: it's private by design (only `last4` leaves the server) |
| Who sees bank details | Separate endpoint when Contribute is tapped, 10/min per IP | In the wishlist response: events are public, so it's scrapeable |
| Guest identity | Name required, email + message optional | Email required: scares off people who just want to give |
| Public contributor list | Names + messages, no amounts, opt-in "Anonymous" | Amounts: people compare, and the ₦5k giver feels small |
| What's public | Only CONFIRMED contributions | Pending ones: a rude fake message would show before review |
| At 100% | Stays open until the organizer closes it | Auto-close: "people wanna give", and the money all lands in one account anyway |
| Pending total for guests | Hidden | Shown: product owner preferred organizer-only |
| Currency | One per wishlist, copied from the event's `settlementCurrency` at creation, never changed | Changeable: would silently re-price every item and contribution |

**The overfunding lesson.** I proposed auto-closing items. The product owner disagreed, and was
right: per-item totals are just labels on money that all goes to one account. Ask *where the money
actually lands* before writing a rule about it.

---

## Part 3 — Patterns worth keeping

### 3.1 Public and private data don't share a table
`PayoutAccount` keeps the full account number server-side and shows `last4`. The wishlist needs
the full number shown to guests. Putting both in one table means one careless `select` leaks
payout data. **Separate tables per audience** is cheaper than auditing every query forever.

### 3.2 The one join that could leak gets a comment
`hasWishlist` on event details is computed from:
```ts
wishlist: { select: { isEnabled: true } }, // never widen: the row holds bank details
```
A bare `include: { wishlist: true }` would have put bank details into every public event response.

### 3.3 404, not 403, for things that shouldn't be discoverable
A disabled wishlist, or one on a draft event, answers **404 "not found"** to guests. A 403 would
tell them it exists.

### 3.4 Denormalise for the hot query, document the invariant
`WishlistContribution` stores `wishlistId` as well as `itemId`, so "all pending gifts for my event"
is one indexed query (`@@index([wishlistId, status])`). The cost is an invariant that the service
must keep: `contribution.wishlistId === item.wishlistId`. It's written next to the field.

### 3.5 Soft delete when history points at you
Items use `deletedAt`, the same rule as `PayoutAccount`. Contributions that already happened must
keep pointing at the item they were for.

### 3.6 Reorder by sending the whole order
`PUT /items/order` takes every live id, validates it's exactly the live set, and writes
`sortOrder = index` in one transaction. A swap breaks as soon as two rows share a value. A full
order is idempotent and fixes any drift.

### 3.7 Link guest activity on **verified** email only
`WishlistService.linkGuestContributions(userId, email)` sets `userId` on guest rows with a
matching email (case-insensitive, `userId IS NULL`). Called from:
- `login`, but only if `isEmailVerified`
- `verifyEmail`
- both Google paths (`googleAuth`, `handleGoogleCallback`), since Google verifies the address

Unverified linking would let anyone register with your email and inherit your history. It's
**best-effort**: it logs errors and never throws, so it can't break sign-in.

### 3.8 Money arithmetic stays on the server
`remainingAmount = max(price − confirmedTotal, 0)` is computed with `Prisma.Decimal` and sent as a
string. The frontend's rule is to format money and never calculate with it.

---

## Part 4 — Spin the wheel

### The design, decided one question at a time
- **Organizer sets the prizes.** Each checked-in attendee gets **one spin**, plus one more for
  each **Retry** slice they land on.
- **Prize stock:** each prize is either limited (`quantity`) or unlimited (`quantity = null`).
  Sold-out slices stay on the wheel, greyed out as "Gone", and are never picked.
- **Odds:** rarity `COMMON / RARE / VERY_RARE` → weights `10 : 3 : 1`. Slices are drawn the same
  size, so rare ones get a visible label.
- **Who can spin:** checked-in attendees only (logged in, with a `CheckIn` row), because prizes are
  physical and claimed at the venue.
- **Where it lives:** a `SPIN_WHEEL` **round** inside a game session, so it's paid through the
  gamification plan. Quota counts sessions, so a wheel round costs no extra slot.
- **Claiming:** wins are ordinary `Reward`s with a `claimCode`.

### The data model
```
GameRound (gameType = SPIN_WHEEL)
  ├─ GameRewardTier  = a slice: rank (position), title, rarity, isRetry, quantity? (null = unlimited)
  └─ WheelSpin       = one spin: userId, rewardTierId (landed), rewardId? (null if retry)
Reward               = a win: claimCode @unique, status WON → … → FULFILLED
```
Why a new `WheelSpin` table: `GameEntry` is `@@unique([gameRoundId, userId])`, one row per person
per round, and a retry means a second spin.

### The spin, step by step (`spin-wheel.service.ts`)
1. Load the round. It must be `SPIN_WHEEL`, the round `ACTIVE`, and the session `ACTIVE`.
2. Check the `CheckIn` for (user, event) exists, or return 403.
3. In a transaction:
   1. `SELECT id FROM game_rounds WHERE id = $1 FOR UPDATE` serialises spins on this wheel.
   2. Spins allowed = 1 + retries landed. If none left, return 409.
   3. Stock per slice = `quantity − count(Reward for that tier)`, derived and not stored.
   4. If no **prize** slice has stock, return 409 "all prizes won". Otherwise retries would loop
      forever.
   5. Weighted pick over the in-stock slices using `crypto.randomInt`.
   6. If it's a prize: create the `Reward` with a claim code. Write the `WheelSpin` either way.
4. After the commit: send the winner email with a headline and the claim code, best-effort.

### The race the lock prevents
Without step 3.1, two concurrent spins both read "1 VIP left" and both win it. The same goes for
one user double-tapping. This is **check-then-act**. The row lock makes the check and the act
atomic per wheel, and different wheels don't block each other.

### Turning off inherited behaviour
Reusing the games system meant switching off parts of it for wheels:
- `distributeRoundRewards` (hands out round tiers **by rank** when a round ends) returns early for
  wheels.
- `submitRound`, `answerQuestion` and `submitRoundAnonymously` reject wheel rounds.
- `createSession` only reads `rounds[].rewardTiers` for wheels. The wizard sends the session's
  ranked prizes on *every* round, so reading them for other types would hand out each prize once
  per round.
- `updateRound` refuses to turn a round into or out of a wheel, because its slices live in tiers,
  not in config.

### Claim codes
`XXX-XXX` from `ABCDEFGHJKMNPQRSTUVWXYZ23456789`, with no 0/O/1/I/L, generated by `nanoid`
`customAlphabet`. Uniqueness is checked before insert, because a unique-violation inside a
transaction aborts it. Input is normalised: uppercased, separators stripped. Redeeming is one step
from any open state to `FULFILLED`, guarded with `updateMany where status in (…)` so it can't
happen twice.

---

## Part 5 — Things found along the way (not fixed)

- `addRound` creates non-wheel round tiers **without** `gameSessionId`, so the organizer's rewards
  overview, which filters by session, misses them.
- `deleteRewardTier` hard-deletes, and `Reward → rewardTier` is `onDelete: Cascade`, so deleting a
  tier deletes prizes already won. Only reachable while the game is `PENDING`.
- (Two security findings are tracked privately until they're fixed. Unfixed security issues in a
  live app don't go in a public vault.)
- In this setup `prisma migrate dev` didn't regenerate `src/generated/prisma`; run
  `npx prisma generate` after migrations.

---

## Check yourself

1. Why does the wishlist store bank details on its own row instead of reusing `PayoutAccount`?
2. Linking guest gifts by email: what attack does "verified only" prevent?
3. What would go wrong in `spin()` without `FOR UPDATE`? Give two different failures.
4. Why is stock derived from `Reward` rows instead of decremented in a column?
5. Why does a wheel with only Retry slices left stop instead of spinning?
6. Which existing games behaviour had to be switched off for wheel rounds, and why?
