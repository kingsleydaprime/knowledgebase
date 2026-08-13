# NextVibe — Backend Money: Ledgers, Multicurrency & Payouts

New file (2026-08-12), added when the payout system was built. See also
`learning/backend/03-modules.md` (the payments module this hooks into),
`learning/backend/01-core.md` (Prisma/NestJS module wiring),
`learning/00-sys-design.md`, `learning/09-devops.md` (Parts 56–57 — whether Docker applies
migrations, and Compose env precedence), and — for the frontend half of this system, including
money formatting and backend-driven forms — `learning/frontend/09-payouts-and-multicurrency-ui.md`.
For the attendee-facing payment UI, see `learning/frontend/07-payments-games.md`.

This file covers: why a balance should never be a column, the append-only ledger pattern and
what makes it auditable, using a unique constraint as an idempotency key so replayed webhooks
can't double-credit, how "reserve on request" structurally kills a whole class of
double-spend bug, why you must never sum money across currencies, the difference between
presentment and settlement currency, how to model bank accounts for countries whose
account numbers look nothing like a Nigerian NUBAN, why collecting money and sending money are
unrelated capabilities, why Prisma 7 needs a driver adapter in standalone scripts, and how to
run a write script against a production database without losing sleep.

---

## Part 27 — Why the Old Withdrawal Code Was Dangerous

Here is what the original `withdrawals.service.ts` did when an organizer asked for their money:

```typescript
const revenue = await this.prisma.ticketPurchase.aggregate({
  where: { eventId, paymentStatus: 'COMPLETED' },
  _sum: { totalAmount: true },
});

const totalAmount = revenue._sum.totalAmount ?? 0;

const withdrawal = await this.prisma.withdrawal.create({
  data: { eventId, organizerId, amount: totalAmount, /* ... */ },
});
```

Read it carefully. The payout amount is **recomputed from scratch every single time** as the
sum of all completed purchases. Nothing anywhere subtracts what has already been paid out.

So an organizer with ₦500,000 in sales can hit that endpoint five times and generate five
separate ₦500,000 withdrawal requests. The database happily stores all five. If an admin
processes them without noticing, the platform pays out ₦2,500,000 on ₦500,000 of revenue.

There's a second, quieter problem. The `WithdrawalStatus` enum had `APPROVED`, `REJECTED` and
`PAID` values — but grepping the entire `src/` tree showed the word "withdrawal" appearing
**only** inside its own module. No admin endpoint ever set those statuses. `processedAt` and
`notes` were columns that nothing ever wrote to. Every withdrawal sat at `PENDING` forever.

**The lesson:** an enum value with no code path that sets it is a lie in your schema. It
looks like the feature exists. Grep for where each status is actually written before you
trust a state machine.

### How to spot this class of bug yourself

Any time you compute an amount by aggregating source records, ask: *what subtracts the part
already consumed?* If the answer is "nothing," you have a double-spend. Real answers are
either a running balance, or — better — a ledger.

---

## Part 28 — Never Store a Balance as a Column

The obvious fix is a `balance` column on the user, incremented on sale and decremented on
payout. Resist it. A single mutable number has three failure modes:

1. **No history.** When the number is wrong — and eventually it will be — you have no way to
   discover *when* it went wrong or *why*. There is nothing to reconstruct it from.
2. **Silent drift.** A crashed process between "decrement balance" and "create payout" leaves
   the number permanently wrong, with nothing to detect it.
3. **No audit story.** "Why do I have ₦12,000?" has no answer beyond "because the column says so."

The alternative is the pattern every real financial system uses: an **append-only ledger**.
You store the *events*, and you *derive* the balance by summing them.

```prisma
model LedgerEntry {
  id          String          @id @default(uuid())
  organizerId String
  currency    String
  direction   LedgerDirection // CREDIT | DEBIT
  amount      Decimal         @db.Decimal(20, 4) // ALWAYS positive
  type        LedgerEntryType
  availableAt DateTime?
  sourceType  LedgerSourceType
  sourceId    String
  createdAt   DateTime        @default(now())

  @@unique([type, sourceType, sourceId])
}
```

Balance is then a query, never a column:

```typescript
const credits = await db.ledgerEntry.aggregate({
  where: { organizerId, currency, direction: 'CREDIT' },
  _sum: { amount: true },
});
const debits = await db.ledgerEntry.aggregate({
  where: { organizerId, currency, direction: 'DEBIT' },
  _sum: { amount: true },
});
return new Prisma.Decimal(credits._sum.amount ?? 0).minus(debits._sum.amount ?? 0);
```

### "Append-only" means what it says

The `LedgerService` deliberately exposes **no update and no delete method**. That's not an
oversight, it's the whole point. A ledger you can edit is not an audit trail — it's just a
table with extra steps.

When something is wrong, you don't fix the bad row. You **append a reversing entry**. The
mistake stays visible, the correction sits next to it, and the derived balance comes out
right. That's how a rejected payout returns money: the original `PAYOUT_RESERVED` debit stays
forever, and a `PAYOUT_REVERSED` credit cancels it.

### Why `amount` is always positive

Notice `amount` is always positive and `direction` carries the sign. It would be tempting to
allow negative amounts and drop the `direction` column. Don't. If a negative number ever
sneaks into a "credit," it silently becomes a debit and the balance is wrong with no error
anywhere. With this design, a negative amount is *impossible to express*, and the service
throws if you try:

```typescript
if (amount.isNegative() || amount.isZero()) {
  throw new Error(
    `Ledger amount must be positive, got ${amount.toString()}. ` +
    `Use direction: 'DEBIT' to take money out.`,
  );
}
```

**The general principle:** make the invalid state unrepresentable, rather than trying to
remember to check for it everywhere.

---

## Part 29 — A Unique Constraint as an Idempotency Key

Payment providers retry webhooks. This is normal, documented behaviour — if your endpoint is
slow, or returns a 500, or the provider just feels like it, the same "payment succeeded" event
arrives twice. If each delivery credits the organizer, they get paid twice for one sale.

The fix is small and very effective:

```prisma
@@unique([type, sourceType, sourceId])
```

A `TICKET_SALE` entry sourced from `TICKET_PURCHASE:abc-123` can exist exactly once. Full stop.
The database enforces it, so no amount of concurrency or retry logic can get around it.

Then catch the specific violation and treat it as success:

```typescript
try {
  return await db.ledgerEntry.create({ data: { /* ... */ } });
} catch (err) {
  if (err instanceof Prisma.PrismaClientKnownRequestError && err.code === 'P2002') {
    this.logger.warn(`Duplicate ledger entry ignored: ...`);
    return db.ledgerEntry.findUnique({ where: { type_sourceType_sourceId: { /* ... */ } } });
  }
  throw err;
}
```

Two details worth internalising:

- **`P2002` is Prisma's unique-constraint-violation code.** Catch that specific code — a bare
  `catch` would swallow genuine database failures and silently skip crediting someone.
- **Swallow it, don't throw.** A retried webhook is normal traffic and must still get a 200.
  If you throw, the provider sees an error and retries *even harder*.

This is the difference between "idempotent" and "usually fine." Application-level "check if it
exists, then insert" is *not* idempotent — two concurrent webhooks both pass the check before
either inserts. Only the database constraint actually holds.

---

## Part 30 — Reserve on Request, Not on Approval

This is the structural fix for the double-withdrawal bug, and it's worth understanding as a
general pattern.

When a payout is requested, the debit happens **immediately** — not when an admin approves it:

```typescript
return this.prisma.$transaction(async (tx) => {
  const available = await this.ledger.getAvailableBalance(organizerId, dto.currency, tx);

  if (requested.greaterThan(available)) {
    throw new BadRequestException(/* ... */);
  }

  const payout = await tx.payout.create({ /* ... */ });

  await this.ledger.recordEntry({
    direction: 'DEBIT',
    type: 'PAYOUT_RESERVED',
    // ...
  }, tx);

  return payout;
});
```

Two things make this safe, and both matter:

1. **The balance is read *inside* the transaction**, using the same `tx` handle. Two concurrent
   requests can't both see the full balance — the second one reads a balance already reduced
   by the first one's debit, and correctly fails.
2. **The debit lands at request time.** So a second request for the same money finds it gone.
   The old code could be called infinitely because nothing was ever consumed.

If the payout is later rejected or the transfer bounces, a `PAYOUT_REVERSED` credit gives the
money back. And when it's marked `PAID`, **no new ledger entry is written** — the money was
already debited at reserve time. Marking it paid confirms that debit was real; it doesn't move
more money. Getting that backwards would double-count every payout.

### Passing `tx` around

Notice `recordEntry` takes an optional transaction client:

```typescript
type Db = PrismaService | Prisma.TransactionClient;

async recordEntry(input: RecordEntryInput, db: Db = this.prisma) { /* ... */ }
```

This is a genuinely useful NestJS/Prisma idiom. It lets one service method participate in a
caller's transaction *or* run standalone. Without it you'd either duplicate the logic or lose
atomicity. In the payments module, the ledger credit runs inside the same transaction that
issues the tickets — so tickets and the money that paid for them can never disagree.

---

## Part 31 — Never Sum Money Across Currencies

The single most important multicurrency rule: **₦100,000 + $100 is not a number.**

There is no correct single figure for "this organizer's balance" once more than one currency is
involved. Any code that produces one has either silently picked a conversion rate (which
changes hourly, so the number is wrong tomorrow) or has added unlike quantities (which is
just a bug).

So every balance is scoped to a `(organizerId, currency)` pair, and the API returns an array:

```typescript
[
  { currency: 'NGN', available: '450000.00', pending: '120000.00', ... },
  { currency: 'USD', available: '300.00',    pending: '0.00',      ... },
]
```

The same applies to the admin's outstanding-liability view — grouped by currency, never
totalled into one headline number. When you see a design that wants "total platform
liability" as one figure, that's a **reporting** question with an explicitly chosen rate and
an as-of date, not a balance query.

### Presentment vs. settlement

Two different currencies are in play in one transaction, and conflating them causes real
money errors:

- **Presentment currency** — what the *buyer* is charged. A US attendee sees and pays USD.
- **Settlement currency** — what the *organizer* is credited and paid out in.

The purchase record stores both, plus the rate used:

```prisma
// Presentment: what the BUYER is charged
totalAmount   Decimal @db.Decimal(20, 2)
currency      String  @default("NGN")

// Settlement: what the ORGANIZER is credited
settlementAmount   Decimal @default(0) @db.Decimal(20, 2)
settlementCurrency String  @default("NGN")
fxRate             Decimal @default(1) @db.Decimal(20, 10)
```

**Always snapshot the rate onto the transaction.** If you look the rate up fresh when
displaying an old order, a rate change silently rewrites history and the receipt you show
someone stops matching what their card was charged. The rate used is a *fact about that
transaction*, so it gets stored on it. (The existing `Pledge` model in this codebase already
did this correctly with its `exchangeRate` column — it was the one model that got
multicurrency right.)

### Decimal, never float

Money is `Decimal` in Prisma, never `Float`. `0.1 + 0.2 !== 0.3` in binary floating point, and
those fractions of a kobo accumulate into real discrepancies. Use `Prisma.Decimal` for
arithmetic too, not `Number()`:

```typescript
new Prisma.Decimal(credits).minus(debits);  // exact
Number(credits) - Number(debits);           // drifts
```

Scale choices here: `Decimal(20, 4)` for ledger amounts (4 places leaves room for fractional
minor units in intermediate math), `Decimal(20, 10)` for FX rates — thinly-traded pairs need
the precision, e.g. NGN→USD is around 0.00065.

### Minor units are a per-currency fact

Payment providers take amounts in *minor units*. It is very tempting to write `amount * 100`.
That is wrong for currencies with a different minor-unit count — 1000 minor units is ₦10 (2
decimals) but ¥1000 (0 decimals). A 100x billing error. So the decimals live in a table:

```typescript
export const SUPPORTED_CURRENCIES = {
  NGN: { decimals: 2, symbol: '₦', name: 'Nigerian Naira' },
  USD: { decimals: 2, symbol: '$', name: 'US Dollar' },
  // ...
} as const;

export function toMinorUnits(amount: number, currency: SupportedCurrency): number {
  const { decimals } = SUPPORTED_CURRENCIES[currency];
  return Math.round(amount * 10 ** decimals);
}
```

---

## Part 32 — Modelling Bank Accounts That Aren't Nigerian

A NUBAN is 10 digits plus a bank code. That's the only shape the old `Withdrawal` model knew:

```prisma
bankName      String
accountNumber String
accountName   String
```

Foreign accounts look nothing like this:

| Country | What you actually need |
|---|---|
| Nigeria | 10-digit NUBAN + bank code |
| UK | 8-digit account number + 6-digit sort code |
| US (ACH) | account number + 9-digit routing number + checking/savings |
| Eurozone | IBAN (up to 34 chars, with a checksum) + optional BIC |
| Elsewhere | account/IBAN + 8 or 11 char SWIFT-BIC |

Two ways to model this, and the naive one is a trap:

**Nullable column sprawl** — add `iban`, `sortCode`, `routingNumber`, `swiftBic`, `accountType`,
`bic`… You end up with ~15 columns, of which 12 are always null on any given row, and the
database can't tell you which combination is valid for which country.

**Discriminator + validated JSON** — one `rail` enum saying *how* money gets there, and a
`details` JSON blob whose required keys are determined by the rail:

```prisma
rail     PayoutRail  // NIGERIAN_BANK | US_ACH | SEPA | SWIFT | ...
details  Json        // shape depends on rail
last4    String      // safe to display
```

The trade-off is that the database no longer validates the shape, so **the application must**.
That validation is declared as data, which also means the frontend can fetch it and render the
right form per country instead of hardcoding the shapes:

```typescript
export const RAIL_REQUIREMENTS = {
  NIGERIAN_BANK: { required: ['accountNumber', 'bankCode'], /* ... */ },
  SEPA:          { required: ['iban'], optional: ['bic', 'bankName'], /* ... */ },
  US_ACH:        { required: ['accountNumber', 'routingNumber', 'accountType'], /* ... */ },
};
```

Also note the allowlist when saving — only known keys are persisted, so a caller can't stash
arbitrary JSON on a financial record.

### The IBAN checksum is worth implementing

IBANs carry a built-in mod-97 check (ISO 13616) that catches transposed digits — the exact
typo that sends money to the wrong person. It's about ten lines:

```typescript
private isValidIban(raw: string): boolean {
  const iban = raw.replace(/[\s-]/g, '').toUpperCase();
  if (!/^[A-Z]{2}\d{2}[A-Z0-9]{10,30}$/.test(iban)) return false;

  // Move the first 4 chars to the end, then letters become numbers (A=10..Z=35).
  const rearranged = iban.slice(4) + iban.slice(0, 4);
  const numeric = rearranged.replace(/[A-Z]/g, (ch) => String(ch.charCodeAt(0) - 55));

  // The result is far past Number.MAX_SAFE_INTEGER, so take mod 97 digit by digit.
  let remainder = 0;
  for (const digit of numeric) {
    remainder = (remainder * 10 + Number(digit)) % 97;
  }
  return remainder === 1;  // valid IBANs always leave remainder 1
}
```

That chunked-mod trick is worth remembering generally: **to take a huge number mod something
without a bignum library, process it a digit at a time.** `(remainder * 10 + digit) % 97` is
mathematically identical to taking the whole number mod 97, but never overflows.

### Soft delete, because history must resolve

`PayoutAccount` has a `deletedAt` rather than being hard-deleted. A payout sent last month must
still show where the money went, and a foreign key to a deleted row can't do that.

For the same reason, `Payout` stores a `destinationSnapshot` JSON — a frozen copy of the
account details *as they were at request time*. If the organizer edits the account tomorrow,
the historical record still shows the account the money actually went to. **Financial records
snapshot; they don't join to live data.**

### Don't echo secrets back

The organizer already knows their own account number. Returning it on every list call just
widens the blast radius of a leaked token or a logged response. So the service masks it:

```typescript
maskedAccount: `••••${account.last4}`,
```

Same reasoning applies to the admin notification email — the old code put the full account
number, name and bank in an email body. An inbox is not a safe store for financial details, and
you don't control forwarding. The new email says "review in dashboard" and carries no account
data at all.

---

## Part 33 — Encoding a State Machine as Data

Payout statuses aren't freely interchangeable — you must not be able to move a `PAID` payout
back to `REQUESTED` and re-reserve funds. Rather than scattering `if` checks:

```typescript
const ALLOWED_TRANSITIONS: Record<PayoutStatus, PayoutStatus[]> = {
  REQUESTED:  ['APPROVED', 'REJECTED'],
  APPROVED:   ['PROCESSING', 'PAID', 'FAILED', 'REJECTED'],
  PROCESSING: ['PAID', 'FAILED'],
  PAID:       [],            // terminal
  REJECTED:   [],            // terminal
  FAILED:     ['APPROVED'],  // retryable after fixing the destination
};
```

One lookup guards every transition, terminal states are obvious at a glance, and the error
message can tell the caller what *is* allowed:

```typescript
throw new BadRequestException(
  `Cannot move a payout from ${payout.status} to ${target}. ` +
  `Allowed from ${payout.status}: ${allowed.join(', ') || 'nothing (terminal)'}.`,
);
```

Compare that to the original enum, which had four states and no transition logic at all.

---

## Part 34 — Backfilling a Ledger onto Existing Data

Introducing a ledger to a system that already has completed sales creates a problem: those
sales produced no ledger entries, so every organizer's balance reads zero and nobody can
withdraw money they genuinely earned.

The backfill (`prisma/backfill-ledger.ts`) has three properties worth copying for any data
migration:

1. **Dry run by default.** It prints what it *would* write and only commits with an explicit
   `--commit` flag. The destructive path should never be the one you get by accident.
2. **Re-runnable.** Because of the idempotency constraint from Part 29, running it twice
   creates nothing the second time. A backfill that can't be safely re-run is a backfill you
   can't recover from when it dies halfway.
3. **Handles the pre-migration default.** New columns like `settlementAmount` default to `0` on
   existing rows, so it falls back to `totalAmount`:

   ```typescript
   const settlement = new Prisma.Decimal(p.settlementAmount ?? 0);
   const amount = settlement.isZero() ? new Prisma.Decimal(p.totalAmount) : settlement;
   ```

That third point is a general migration trap: **a `DEFAULT` in an `ALTER TABLE` backfills old
rows with a value that is structurally valid but semantically wrong.** Zero is a real amount.
Always ask what the default means for rows that predate the column.

---

## Part 35 — Generating Migration SQL Without Touching Production

`prisma migrate dev` connects to the database in your env and *writes* to it. If that env
points at production — as it did here, an Aiven-hosted Postgres — running it is a genuinely
bad afternoon.

To get the SQL without applying anything, diff the live schema against your models:

```bash
npx prisma migrate diff \
  --from-config-datasource \
  --to-schema ./prisma/schema \
  --script \
  -o prisma/migrations/20260812120000_add_ledger_and_payouts/migration.sql
```

This only *reads* the database (introspects its current shape) and writes SQL to a file. You
then read that SQL yourself before anything runs.

**Prisma 7 renamed these flags.** The older `--from-url` and `--to-schema-datamodel` were
removed; it's now `--from-config-datasource` (reads the datasource from `prisma.config.ts`) and
`--to-schema`. If you find a tutorial using the old flags, it predates v7.

### Read the generated SQL before you run it

What to look for, in order of danger:

- `DROP COLUMN` / `DROP TABLE` — data loss. Never in a routine migration.
- `ALTER COLUMN ... SET NOT NULL` without a default — fails outright if any row is null.
- Type narrowing — `DECIMAL(20,2)` → `DECIMAL(10,2)` truncates. *Widening* (10,2) → (20,2), as
  this migration does to `totalAmount`, is safe.
- New `NOT NULL` columns — need a `DEFAULT`, or the migration fails on a non-empty table.

This migration is entirely additive: new enums, new tables, and new columns that all carry
defaults. That's what a safe migration looks like.

---

## Part 36 — Collection Is Not Disbursement

The instinct when adding payouts is "we already have Ercaspay, so payouts go through Ercaspay."
That instinct is wrong, and untangling it is what made the foreign-organizer problem solvable.

**Collecting money and sending money are different products**, often with different licensing,
different rails, and different country coverage. A gateway that can charge a Nigerian card may
have no ability to send money to a UK account — those are unrelated capabilities that happen to
be sold by the same company.

In this codebase, `ercaspay.service.ts` calls exactly three endpoints:

```
POST /payment/initiate                       → money IN
GET  /payment/transaction/verify/{ref}       → money IN
     transaction details                     → money IN
```

All inbound. `PayoutsService` injects no HTTP client and imports no `HttpModule` at all — it
writes ledger entries and updates rows. Money physically leaves via a human using a bank portal
or Wise, and `markPaid` records the reference afterwards.

```
Attendee → Ercaspay → platform account       (collection — automated)
platform account → bank/Wise → organizer     (payout — manual, any country)
                    ↑ recorded via externalReference
```

### Why the decoupling is the point

The original worry was "Ercaspay doesn't help with foreign accounts, so how do I pay foreign
organizers?" Once payouts are a *manual* rail, that question dissolves — you can pay a UK
organizer via Wise today without any provider supporting it. The system's job is narrower than
it first appears:

1. Compute the right amount (the ledger)
2. Capture correct destination details per country (`PayoutAccount` + per-rail validation)
3. Record that money actually left (`status` + `externalReference`)

None of that needs a provider API. And because `Payout` already carries `PROCESSING` and
`externalReference`, wiring an automated rail in later is a service change with **no
migration**.

**The transferable lesson:** when a third-party integration blocks a feature, check whether the
integration is actually on the critical path or whether you assumed it was. Often the manual
version of a workflow is worth building first — it works everywhere from day one, and it
defines the data model the automated version will need anyway.

### On verifying provider capabilities

Don't assert what a provider's API can do from memory, including your own memory of their
marketing site. Check the API reference, or ask their support. Note that many payment providers
publish docs as client-rendered SPAs that return nothing to a fetcher or curl — so "I couldn't
find it in the docs" is not evidence it doesn't exist. Get a definitive answer from the
dashboard or a human before designing around it.

---

## Part 37 — Prisma Driver Adapters: Why `new PrismaClient()` Throws

Writing a standalone script against this project's Prisma setup fails immediately:

```
PrismaClientInitializationError: `PrismaClient` needs to be constructed with a
non-empty, valid `PrismaClientOptions`
```

The error message is actively unhelpful — it prints generic constructor examples and never
mentions the real cause. The real cause is in the schema:

```prisma
datasource db {
  provider = "postgresql"
  // note: no `url`
}
```

**There is no `url`.** For the CLI it comes from `prisma.config.ts`. But at *runtime* Prisma 7
has nothing to connect with, so it requires a **driver adapter** — an explicitly constructed
database client you hand it. `PrismaService` does this correctly:

```typescript
const pool = new Pool({
  connectionString,
  ssl: connectionString.startsWith('postgres') ? { rejectUnauthorized } : undefined,
});

const adapter = new PrismaPg(pool);
super({ adapter });
```

So a standalone script must build the same thing rather than calling `new PrismaClient()`:

```typescript
import { PrismaClient } from '../src/generated/prisma/client';
import { PrismaPg } from '@prisma/adapter-pg';
import { Pool } from 'pg';

const pool = new Pool({ connectionString: process.env.DATABASE_URL, ssl: { rejectUnauthorized } });
const prisma = new PrismaClient({ adapter: new PrismaPg(pool) });
```

### Close the pool, or the script hangs

```typescript
.finally(async () => {
  await prisma.$disconnect();
  await pool.end();     // the pool is yours, not Prisma's
});
```

`$disconnect()` only releases Prisma's side. Since *you* created the pool, its open sockets keep
the Node event loop alive and the script prints its results then never exits. Any time you
construct a connection pool yourself, you own closing it.

**The general habit this teaches:** before writing a standalone script against an app's
database, go read how the app itself constructs its client. Copy that construction. Config
lives in more places than the schema file, and guessing costs a debugging round trip.

---

## Part 38 — Running Scripts Against Production

The backfill was always going to run against production — that's where the real purchase history
lives, so running it locally would have credited nothing. That makes the safety properties of
the script the only thing standing between you and a bad afternoon.

### Dry run by default, writes behind an explicit flag

```typescript
const COMMIT = process.argv.includes('--commit');

// ... later, inside the loop:
if (!COMMIT) {
  written++;
  continue;      // the create below is unreachable without the flag
}

await prisma.ledgerEntry.create({ /* ... */ });
```

The destructive path must never be the one you get by accident. Note the shape: the guard
`continue`s *before* the write, so in dry-run mode the write is structurally unreachable rather
than conditionally skipped. When you need to reassure yourself (or someone else) that a run was
safe, you can point at the control flow instead of arguing about it.

### Verify idempotency on the real database

Running the backfill a second time with `--commit`:

```
Found 5 completed purchase(s).
Wrote 0 entries, skipped 5.
```

Zero written. That confirms the `@@unique([type, sourceType, sourceId])` constraint from Part 29
works against real data — and that constraint isn't just for backfills. **It's the same
mechanism that stops a retried payment webhook crediting an organizer twice for one sale.**
Re-running a safe backfill is a cheap way to test a guarantee you're otherwise trusting blindly
in production.

### The dry run / commit figures must match

```
DRY RUN:  Would write 5 entries, skipped 0.   NGN 30300.00
COMMIT:   Wrote 5 entries, skipped 0.         NGN 30300.00
```

If those disagree, something changed between the two runs and the commit deserves scrutiny.
Print the same summary in both modes specifically so they can be compared.

### Make hitting production deliberate

The sharpest edge here is that `.env` points at production, so *any* script run with no extra
arguments hits the live database. Safer setup: keep a local database in `.env`, and pass the
production URL explicitly when you genuinely mean it:

```bash
DATABASE_URL='<prod-url>' npx tsx prisma/backfill-ledger.ts
```

Then hitting production is an act you have to perform, not the default you fall into.

### Corrections are append-only too

If a backfill turns out wrong, the fix is a **reversing entry**, never
`DELETE FROM ledger_entries`. Deleting destroys the audit trail the whole design exists to
provide — and an incorrect entry plus its correction is a more honest record than a row that
silently vanished.
