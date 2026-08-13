# NextVibe — Frontend: Payouts, Money Display & Backend-Driven Forms

New file (2026-08-12), added when the payout UI was built. See also
`learning/frontend/07-payments-games.md` (the attendee-facing payment flow),
`learning/frontend/02-state-management.md` (Redux/RTK Query basics), and — for the backend
half of this exact system (the ledger, idempotency, payout state machine) —
`learning/backend/06-money-ledger-and-payouts.md`.

This file covers: why money must never be a `number` in the client, formatting many
currencies without hardcoding symbols, letting the backend describe a form instead of
hardcoding one per country, RTK Query cache invalidation when one action changes three
screens, the "you might not need an effect" fix for derived state, and how to retire an old
API surface without breaking things.

---

## Part 41 — Money Is a String. Keep It That Way.

Every amount from the payouts API arrives as a **string**:

```json
{ "currency": "NGN", "available": "450000.00", "pending": "120000.00" }
```

That's deliberate. The backend stores money as Postgres `DECIMAL`; serialising it as a JSON
number would round-trip it through a JS double, and `0.1 + 0.2 !== 0.3`. Fractions of a kobo
don't matter once — they matter after ten thousand ticket sales.

So the client rule is: **format strings for display, never do arithmetic on them.**

```typescript
export type MoneyString = string;
```

The one place a `Number()` conversion is legitimate is a *comparison* — "is the requested
amount more than the available balance?" — and even then it's isolated in a named helper so
it's obvious where it happens:

```typescript
/** Parses a money string to a number, for comparisons only — never for display. */
export function toNumber(amount: string | number | null | undefined): number { /* ... */ }
```

If you ever need a genuine total, ask the server. It has the exact values; you have
approximations of them.

---

## Part 42 — Formatting Many Currencies Without Hardcoding Symbols

The old withdrawal UI did this:

```typescript
`₦${estimatedRevenue.toLocaleString("en-NG")}`
```

Two bugs baked into one line: the naira symbol is hardcoded, and so is the locale. A USD
balance renders as "₦300". `Intl.NumberFormat` already knows every currency's symbol,
placement and decimal count:

```typescript
new Intl.NumberFormat(undefined, {
  style: "currency",
  currency,                      // "NGN" | "USD" | "GBP" | ...
  minimumFractionDigits: decimals,
  maximumFractionDigits: decimals,
}).format(value);
```

Passing `undefined` as the locale means "use the viewer's locale" — so a user in Lagos and one
in Berlin each see their own grouping and decimal separators, while the *currency* stays
whatever the money actually is. Locale and currency are independent, and conflating them is
the mistake above.

### Wrap it in a try/catch

`Intl.NumberFormat` **throws** on a currency code it doesn't recognise. One unusual currency
would otherwise blank the entire earnings page:

```typescript
try {
  return new Intl.NumberFormat(/* ... */).format(value);
} catch {
  return `${currency} ${value.toLocaleString(/* ... */)}`;
}
```

**General principle:** any browser API that throws on bad input needs a fallback when the
input comes from a server you'll keep changing.

### Minor units differ per currency

`JPY: 0` sits in the decimals table next to `NGN: 2` for a reason. Assuming 2 decimals
everywhere means yen amounts get displayed 100x wrong. The table lives in
`src/utils/money.ts` and mirrors the backend's `SUPPORTED_CURRENCIES`.

---

## Part 43 — Never Sum Across Currencies (The UI Half)

The backend returns balances as an **array**, one entry per currency. The UI renders one card
each and never adds them:

```tsx
{balances.map((balance) => (
  <BalanceCard key={balance.currency} balance={balance} onRequestPayout={setPayoutTarget} />
))}
```

It's tempting to show a headline "Total earnings" figure. There isn't one. Adding ₦100,000 and
$100 requires an exchange rate, which changes hourly, which means the "total" is wrong
tomorrow and was never a fact in the first place.

The admin liability view has the same constraint — grouped by currency, one card per currency,
no grand total.

**When a designer asks for a single number**, the honest answer is a *reporting* view with an
explicitly displayed rate and an as-of timestamp — not a balance.

---

## Part 44 — Let the Backend Describe the Form

Payout accounts are the interesting UI problem: a Nigerian account needs `accountNumber` +
`bankCode`, a SEPA one needs an `iban`, a US one needs `routingNumber` + `accountType`.

The naive approach is a `switch` in the component with a hardcoded form per country. It means
every new country ships a frontend release, and the frontend's idea of "required" silently
drifts from the backend's.

Instead the backend exposes its own validation rules:

```
GET /v1/payout-accounts/supported
```

```json
{
  "rails": [
    { "rail": "NIGERIAN_BANK", "label": "Nigerian bank account",
      "requiredFields": ["accountNumber", "bankCode"], "optionalFields": ["bankName"] },
    { "rail": "SEPA", "label": "European bank account (SEPA)",
      "requiredFields": ["iban"], "optionalFields": ["bic", "bankName"] }
  ]
}
```

and the form renders itself from that:

```tsx
{[...(selectedRail?.requiredFields ?? []), ...(selectedRail?.optionalFields ?? [])].map((key) => {
  const meta = FIELD_META[key];
  return <Input key={key} placeholder={meta?.placeholder} /* ... */ />;
})}
```

`FIELD_META` maps a field *name* to a human label and input hints. Note the fallback:

```tsx
{meta?.label ?? key}
```

A field the backend adds before the frontend knows about it still renders — just with a raw
label instead of a pretty one. **Degrade, don't crash.** That's what makes it safe for the
backend to move first.

### Still validate client-side

The dialog mirrors the backend's format checks (NUBAN = 10 digits, routing = 9, IBAN shape).
This is *not* redundant:

- **Client-side validation is UX** — catch the typo before a network round trip.
- **Server-side validation is correctness** — it's the only one that can't be bypassed.

You need both, and the server always wins. What you must never do is validate *only* on the
client.

---

## Part 45 — RTK Query: One Action, Three Stale Screens

Requesting a payout changes three things at once: the payout list, the balance (money is
reserved immediately), and the statement (a new ledger entry). Tag invalidation expresses that
in one place:

```typescript
requestPayout: builder.mutation({
  query: (body) => ({ url: "/v1/payouts", method: "POST", body }),
  invalidatesTags: ["Payouts", "Balance", "Statement"],
}),
```

Every query that declared `providesTags: ["Balance"]` refetches automatically. No manual
`refetch()` calls, no prop-drilling a callback down to the dialog, no stale balance sitting on
screen after a withdrawal.

**Getting this wrong is the most common RTK Query bug**: the mutation succeeds, the server is
correct, and the UI keeps showing the old number — so it looks like the backend failed. If a
screen looks stale after a mutation, check the tags before you debug the API.

### `keepUnusedDataFor` for static config

The supported-currencies endpoint is configuration, not data:

```typescript
getSupportedPayoutOptions: builder.query({
  query: () => "/v1/payout-accounts/supported",
  keepUnusedDataFor: 3600,   // seconds
}),
```

No point refetching a list of countries every time a dialog opens.

---

## Part 46 — You Might Not Need an Effect

ESLint's `react-hooks/set-state-in-effect` caught two real mistakes here. The first was
preselecting the organizer's default payout account:

```tsx
// ✗ Wrong — an extra render pass every time the data arrives
const [accountId, setAccountId] = useState("");
useEffect(() => {
  if (!accountId && accounts.length > 0) {
    setAccountId((accounts.find((a) => a.isDefault) ?? accounts[0]).id);
  }
}, [accounts, accountId]);
```

The bug is conceptual, not stylistic: this treats "which account is selected" as something to
*synchronise*, when it's something to *compute*. State should hold only the user's explicit
choice; the effective selection is derived:

```tsx
// ✓ Right — no effect, no extra render
const [accountId, setAccountId] = useState("");

const selectedAccountId =
  accountId ||                                              // explicit choice wins
  (accounts.find((a) => a.isDefault) ?? accounts[0])?.id ||  // else the default
  "";
```

It renders correctly on the very first paint after the accounts load, instead of rendering
empty and then re-rendering.

The second was resetting a form when a dialog closes. Same fix — do it in the close *handler*,
which is an event, rather than in an effect watching `open`:

```tsx
const handleOpenChange = (next: boolean) => {
  if (!next) resetForm();
  onOpenChange(next);
};
```

**The heuristic:** an effect is for synchronising with something *outside* React (the DOM, a
socket, a timer). If you're reacting to a user action, that belongs in the event handler. If
you're deriving a value from props/state, just compute it during render.

### Also: `useMemo` and array identity

```tsx
const accounts = useMemo(() => accountsData?.data ?? [], [accountsData]);
```

Without `useMemo`, `?? []` creates a **brand new array on every render**. Any hook depending
on `accounts` then sees a changed dependency every time and re-runs forever. This is the
classic `??`/`||` default-value trap in a dependency array.

---

## Part 47 — Retiring an Old API Surface

The old `requestWithdrawal` / `getWithdrawals` endpoints in `eventApi.ts` became dead once the
payout system landed. Two options: delete them, or deprecate them.

Deprecating is the safer first move, because deleting exports is how you discover an import
you missed. They were marked with `@deprecated` JSDoc, which makes editors strike them through
at every call site, plus a note explaining *why* the old design was wrong:

```typescript
/**
 * @deprecated Superseded by the payout system in `./payoutApi`.
 *
 * The old flow recomputed payout as the gross sum of an event's completed
 * purchases on every request, never subtracting what had already been paid — so
 * the same revenue could be requested repeatedly. [...]
 */
```

A deprecation note that only says "use X instead" gets ignored. One that says what *broke*
stops someone reintroducing the same pattern somewhere else.

Delete them for real once the backend's `withdrawals` table is confirmed empty and dropped.

---

## Part 48 — Verify the Build, Not Just the Types

`npx tsc --noEmit` passing does **not** mean the app builds. It only checks types — it doesn't
resolve CSS imports, run the bundler, or prerender pages. Running the real build caught
something typecheck never would:

```
Module not found: Can't resolve 'react-day-picker/style.css'
```

`react-day-picker` was listed in `package.json` but missing from `node_modules` — someone had
added the dependency without the install being committed/synced. `npm install` fixed it.

The confirmation that the new routes actually work is in the build output:

```
├ ○ /admin/payouts
├ ○ /dashboard/earnings
```

**Habit worth keeping:** typecheck while iterating (fast), build before saying it's done
(honest). And when a build error names a file you never touched, check whether it's a missing
install before assuming your change caused it.
