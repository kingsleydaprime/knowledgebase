# 10 — Typed API Contracts

*Written 2026-09-21, from fixing the postcard phase filters.*

See also: [[projects/nextvibe/learning/frontend/02-state-management|02 — State Management]],
[[projects/nextvibe/learning/frontend/08-performance-debugging|08 — Performance & Debugging]],
[[projects/nextvibe/learning/backend/07-validation-and-query-contracts|backend 07 — Validation & Query Contracts]]

---

## The problem: one concept, two vocabularies

Event phases exist twice in this app, and they have to.

- The **database** says `PRE_EVENT` `DURING_EVENT` `POST_EVENT` `BOTH`
- The **UI** says `All` `Pre` `Main` `Post`, with URL slugs `all`
  `pre-event` `main-event` `post-event`

Neither is wrong. `?phase=pre-event` is the right thing for a URL a user can see
and share; `PRE_EVENT` is the right thing for a Postgres enum. `main-event` and
`DURING_EVENT` are the *same phase* under two names, because product language
and schema language drifted — which is normal and not worth "fixing" by
renaming a database column.

**The mistake is not having two vocabularies. It's having no typed boundary
between them.** What actually shipped was four vocabularies in eight files, two
of which disagreed about whether `BOTH` existed.

---

## The pattern: two types, one bridge

```ts
/** The four values `?timing=` accepts. Mirrors Prisma's GameActivityTiming. */
export const PostcardTiming = {
  PRE_EVENT: "PRE_EVENT",
  DURING_EVENT: "DURING_EVENT",
  POST_EVENT: "POST_EVENT",
  BOTH: "BOTH",
} as const;
export type PostcardTiming =
  (typeof PostcardTiming)[keyof typeof PostcardTiming];

/** Tab values and URL slugs. `all` means "send no filter at all". */
export const POSTCARD_PHASES = [
  "all", "pre-event", "main-event", "post-event",
] as const;
export type PostcardPhase = (typeof POSTCARD_PHASES)[number];
```

Two types, deliberately incompatible. A `PostcardPhase` cannot be passed where a
`PostcardTiming` is wanted, so **sending a UI value to the API is a compile
error rather than a 400 at runtime.**

That is the whole point. The first attempt at this file put all five values
(including `MAIN_EVENT`) in one union — and because everything was assignable to
everything, TypeScript couldn't distinguish a valid request from an invalid one.
One union doing two jobs provides no safety at all.

### Why a const object instead of `enum`

```ts
const X = { A: "A" } as const;   // ✓ plain object, erased at runtime
enum X { A = "A" }               // ✗ emits a runtime object, nominal typing
```

`as const` + `keyof typeof` gives a union type *and* an iterable runtime value
with zero emitted code. TS `enum`s are nominally typed (a string literal
`"PRE_EVENT"` is **not** assignable to `enum.PRE_EVENT`), which fights every API
response, and `const enum` breaks under `isolatedModules`. The const-object
idiom is the modern default.

⚠️ `as const` is load-bearing, not decoration. Without it every value widens to
`string`, the derived union collapses to `string`, and the type silently accepts
anything — see backend 07 for the compile error this caused two files away.

### `as const satisfies` — the bit worth stealing

```ts
export const PHASE_TO_TIMING = {
  "pre-event": PostcardTiming.PRE_EVENT,
  "main-event": PostcardTiming.DURING_EVENT,
  "post-event": PostcardTiming.POST_EVENT,
} as const satisfies Record<FilterablePostcardPhase, PostcardTiming>;
```

Three different things, easily confused:

| Form | Effect |
|---|---|
| `const x: T = {…}` | checks against `T`, but **widens** — literal types lost |
| `const x = {…} as const` | keeps literals, but **nothing is checked** |
| `const x = {…} as const satisfies T` | keeps literals **and** checks against `T` |

`satisfies` (TS 4.9+) validates without widening. Here it enforces at compile
time that **every** filterable phase has a mapping and **every** value is a real
wire value. Add a fifth phase to `POSTCARD_PHASES` and this map fails to
compile until it's handled — the map can never silently fall behind the union.

That exhaustiveness is the actual benefit. A plain `Record` annotation would
have widened the values back to `string` and lost it.

### `Exclude` for the `all` case

```ts
export type FilterablePostcardPhase = Exclude<PostcardPhase, "all">;
```

`all` is a real UI state but has **no** wire value. Modelling it as a phase that
merely maps to `undefined` invites someone to send `?timing=ALL`. Excluding it
from the map's key type makes it unrepresentable, and the conversion function
handles it explicitly instead:

```ts
export function phaseToTiming(phase?: PostcardPhase): PostcardTiming | undefined {
  if (!phase || phase === "all") return undefined;
  return PHASE_TO_TIMING[phase];   // narrowed to FilterablePostcardPhase here
}
```

Note the narrowing: after the `=== "all"` check, TypeScript knows `phase` is
`FilterablePostcardPhase`, so indexing the map type-checks with no assertion.

---

## One choke point for the conversion

The conversion happens in exactly one place — the RTK Query endpoint:

```ts
getEventPostcards: builder.query<any, { eventId: string; phase?: PostcardPhase; … }>({
  query: ({ eventId, phase, page = 1, limit = 20 }) => {
    const params = new URLSearchParams({ page: String(page), limit: String(limit) });
    const timing = phaseToTiming(phase);
    if (timing) params.set("timing", timing);
    return `/v1/events/${eventId}/postcards?${params.toString()}`;
  },
}),
```

Components pass the slug their tabs already hold. They never import
`PostcardTiming`, never see the enum, never write `=== "all" ? undefined : …`.

Before this, four call sites each did their own `phase === "all" ? undefined :
phase` dance — four chances to get it wrong, and two of them *had*. **The API
layer is the correct home for vocabulary translation**, because it is the
narrowest waist every request passes through. Same reasoning as putting
`snake_case` → `camelCase` in one interceptor rather than in every component.

---

## Narrow untrusted input, don't assert it

The initial phase comes from the URL, so it's user input:

```ts
// ✗ a lie — the user can type anything
const p = searchParams.get("phase") as Phase;

// ✓ narrowed
export function isPostcardPhase(value: unknown): value is PostcardPhase {
  return typeof value === "string" &&
    (POSTCARD_PHASES as readonly string[]).includes(value);
}

const initialPhase = (): PostcardPhase => {
  const p = searchParams.get("phase");
  return isPostcardPhase(p) ? p : "all";
};
```

`as Phase` is an *assertion* — it silences the compiler without checking
anything, so `?phase=lol` flows through as a valid phase and reaches the API. A
**type guard** (`value is PostcardPhase`) actually checks at runtime and narrows
the type as a result.

> Anywhere a string enters from outside the program — URL params, `localStorage`,
> an API response, a `postMessage` — a type *assertion* is a bug waiting and a
> type *guard* is the fix. shadcn's `Tabs onValueChange` is the same situation:
> it hands back a bare `string`, so narrow it rather than cast it.

The `as readonly string[]` inside the guard is the one unavoidable cast:
`.includes()` on a `readonly ["all", …]` tuple won't accept an arbitrary
`string` as its argument, since the tuple's element type is the narrow union.
Widening only the *array* keeps the cast contained and the return type honest.

---

## Reverse maps are lossy — say so

```ts
export const TIMING_TO_PHASE = {
  PRE_EVENT: "pre-event",
  DURING_EVENT: "main-event",
  POST_EVENT: "post-event",
  BOTH: "main-event",     // ← lossy: BOTH genuinely spans pre AND during
} as const satisfies Record<PostcardTiming, FilterablePostcardPhase>;
```

A `BOTH`-tagged vibe tag spans two phases, so there is no single correct slug.
Picking `main-event` is a **display choice, not a fact**, and a round trip
through both maps won't return `BOTH`.

The general point: a bidirectional mapping is only safe when it's a bijection.
The moment two keys share a value (here, both `main-event` and a hypothetical
`during-event` slug wanting `DURING_EVENT`), the reverse direction needs a
documented tie-break — or the duplicate slug needs deleting, which is what
happened here.

---

## The bug class this all prevents

Worth naming, because it recurs:

```ts
// frontend sent:
`?activityTiming=${activityTiming}`
// backend read:
@Query('timing') timing
```

Two correct programs, one dead parameter, **no error anywhere**. The backend
saw no `timing`, applied its default, and returned plausible-looking data. The
leaderboard's phase tabs "worked" — they just always showed the same phase.

Query parameters are untyped by nature: an unrecognised one is silently ignored
on both sides. Nothing in TypeScript spans the HTTP boundary, so the only
defences are (a) one shared module naming the params, (b) a single choke point
building the URL, and (c) actually watching the Network tab when a filter
"doesn't do anything".

**Debugging heuristic learned here:** when a filter appears to do nothing,
check the request before reading any logic. If the param isn't on the wire, the
bug is in the contract, not the query.
