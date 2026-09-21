# 07 — Validation & Query Contracts

*Written 2026-09-21, from fixing the postcard phase filters.*

See also: [[projects/nextvibe/learning/backend/01-core|01 — Core]],
[[projects/nextvibe/learning/backend/02-auth|02 — Auth]],
[[projects/nextvibe/learning/backend/03-modules|03 — Modules]],
[[projects/nextvibe/learning/frontend/10-typed-api-contracts|frontend 10 — Typed API Contracts]]

---

## The bug that started it

Postcard galleries have four tabs — All / Pre / Main / Post. Every tab showed
the same postcards. The interesting part is that **nothing was broken in the
obvious place**. The filtering logic existed and was correct. What failed was
the contract between the two halves of the app.

Three separate mismatches, each individually invisible:

| Layer | What it said |
|---|---|
| Database enum | `PRE_EVENT` `DURING_EVENT` `POST_EVENT` `BOTH` |
| Frontend tabs | `all` `pre-event` `main-event` `post-event` |
| Param name | frontend sent `?phase=`, backend read `@Query('timing')` |

And the route the UI actually called took no query parameters at all:

```ts
getEventPostcards(@Param('id') eventId: string) {
  return this.eventsService.getEventPostcards(eventId);   // no filters, no paging
}
```

**The lesson is about where bugs live.** A three-layer feature can have correct
code at every layer and still not work, because the *seams* are not typed. Any
place a string crosses a process boundary — HTTP query, env var, webhook body,
queue message — is a place where two correct programs can disagree forever
without either one erroring.

---

## Why a bare `@Query('x')` is a liability

This is the single most useful thing learned here.

```ts
// ✗ no validation happens
findAll(@Query('timing') timing: string) { … }

// ✓ validated
findAll(@Query() dto: ListPostcardsDto) { … }
```

Nest's global `ValidationPipe` (registered in `main.ts`) validates **DTO
classes**. It works by reading `class-validator` metadata off a class. A bare
`@Query('timing') timing: string` has no class and therefore no metadata — so
the pipe has nothing to check and passes the raw string straight through.

Consequences of the bare form:

- `?timing=garbage` reaches Prisma, which throws on an invalid enum value → a
  **500**, when the honest answer is **400 Bad Request**
- TypeScript will happily type it `string` even though only four values are
  legal, so the compiler can't help either
- no Swagger documentation for the parameter
- no default values, no coercion (`?page=2` stays the *string* `"2"`)

With a DTO you get all four for free:

```ts
export class ListPostcardsDto extends PaginationDto {
  @IsOptional()
  @IsUUID()
  eventId?: string;

  @IsOptional()
  @IsEnum(GameActivityTiming)
  timing?: GameActivityTiming;
}
```

`extends PaginationDto` is worth noticing — inheritance on DTOs means
`page`/`limit` with their `@Min`/`@Max` and `@Type(() => Number)` coercion are
declared once and reused by every paginated endpoint. The `@Type` decorator is
what turns the query string `"2"` into the number `2`; without it, `page - 1`
silently produces `"2" - 1`.

---

## `as const`, and how a missing one collapsed a union

A real compile error from this session:

```
postcards.service.ts(38,5): error TS2322:
  Type 'string' is not assignable to type 'GameActivityTiming | undefined'.
```

The cause was two files away:

```ts
// ✗ every value widens to `string`
export const PostcardTiming = {
  ...GameActivityTiming,
  MAIN_EVENT: 'MAIN_EVENT',
};

export type PostcardTiming =
  (typeof PostcardTiming)[keyof typeof PostcardTiming];   // → string
```

TypeScript infers the *widest* type for a mutable object property. `'MAIN_EVENT'`
is a `string` as far as it's concerned, because you could reassign the property
later. So `typeof PostcardTiming` is `{ PRE_EVENT: string; … }`, the indexed
access yields `string`, and the derived union is simply `string` — which accepts
anything, silently destroying the type safety the pattern was meant to provide.

Adding `as const` marks every property `readonly` with a literal type:

```ts
export const PostcardTiming = { … } as const;   // → 'PRE_EVENT' | … | 'MAIN_EVENT'
```

**Rule of thumb:** the const-object-plus-derived-union pattern is *always*
wrong without `as const`. And its failure mode is the dangerous kind — not a
compile error at the definition, but a union that quietly degrades to `string`
and surfaces as a confusing error somewhere else entirely.

---

## Two types for one concept: wire vs internal

`MAIN_EVENT` is not a database value. It's a frontend nickname for
`DURING_EVENT`. The service tolerated it and folded it back:

```ts
private normalizeTiming(t?: PostcardTiming): GameActivityTiming | undefined {
  if (!t) return undefined;
  if (t === 'MAIN_EVENT') return 'DURING_EVENT';
  return t;
}
```

The temptation is to let the DTO validate against that same tolerant type. Doing
so would be a mistake, and naming why is the useful bit:

- **`GameActivityTiming`** is the *wire contract* — what the API promises to
  accept. Four values. Public, versioned-by-implication, hard to change.
- **`PostcardTiming`** is an *internal convenience* — tolerant of a legacy alias
  so older in-process callers keep compiling.

Validate the DTO against the wire contract, and the alias becomes unsendable.
One spelling per phase crosses the boundary; translation stays on the client,
where the UI vocabulary already lives. The tolerant type survives only as a
shim, and can be deleted once nothing internal passes it.

> **Generalisation:** a public boundary should accept the *narrowest* set of
> values that satisfies real callers. Every extra accepted spelling is a
> permanent compatibility obligation.

---

## Route shape: nest for identity, query for filters

The API had grown three different readers for one resource — a paginated feed, a
stub that took no filters, and a third that returned pre-bucketed groups. The
instinct when this happens is to name methods after their filter combination:

```
getAllPostcards
getAllEventPostcards
getAllUserPostcardsForSpecificEvent
getAllUserPostcardsForSpecificEventAndPhase   ← it never ends
```

Three optional filters means eight names, all wrapping one query. The principle
that dissolves it:

> **Nest routes for identity. Use query parameters for filters.**

"Which event" and "which user" are identity — they belong in the path, where
they read naturally and can carry their own auth rules. "Which phase", "which
page" are filters — they belong in the query string, where they compose.

```
GET /postcards?timing=&page=                      the global feed
GET /events/:eventId/postcards?timing=            one event's gallery
GET /events/:eventId/postcards?userId=            one author, in that event
GET /users/:userId/postcards?timing=              one author, everywhere
```

Every route is a thin handler over **one** service method. Adding a fourth
filter adds zero new names. The service method should be named for what it does
— `findPostcards`, not `findAll`, because "all" is exactly what it doesn't do.

---

## Composable `where` clauses

The pattern that makes one method serve every route:

```ts
const where: any = {
  visibility: 'PUBLIC',
  ...(eventId ? { eventId } : {}),
  ...(userId ? { authorId: userId } : {}),
  ...(timing ? { vibeTag: this.timingFilter(timing) } : {}),
};
```

Spreading an empty object contributes nothing, so each filter is independently
optional and they combine without a matrix of `if` branches. Compare the
alternative — one query per combination — and the reason this scales is obvious.

Note `visibility: 'PUBLIC'` is *unconditional*. It is not a filter the caller
chooses; it's an invariant of the endpoint. **Authorisation rules belong outside
the optional-spread section**, where no caller can omit them. The stub route
this work replaced lacked that line, and as a result any link-holder could read
`PRIVATE` postcards.

---

## Global guards, and where to look for them

`@Public()` only means something if a guard reads its metadata. Worth knowing
that a global guard can be registered in **two** places:

```ts
// app.module.ts — DI-aware, can inject services
providers: [{ provide: APP_GUARD, useClass: ThrottlerGuard }]

// main.ts — hand-constructed, no DI
app.useGlobalGuards(new JwtGuard(reflector));
```

This project uses both. Grepping only `app.module.ts` for `APP_GUARD` suggested
there was no auth guard at all — a genuinely alarming and wrong conclusion. The
JWT guard was in `main.ts`.

**Check both before concluding anything about a project's auth posture.** The
`main.ts` form can't inject providers, which is exactly why the
`HttpExceptionFilter` in this project was *moved* to `app.module.ts` — it needed
`PrismaService`, and hand-constructing it left the dependency undefined so the
filter threw while handling every error, turning structured errors into bare
500s. That comment is still in `app.module.ts` and is worth reading.

### Optional user on a public route

```ts
@Public()
@Get(':id/postcards')
getEventPostcards(
  @Param('id') eventId: string,
  @Query() dto: ListEventPostcardsDTO,
  @CurrentUser() user?: JwtPayload,   // ← optional, not `user: JwtPayload`
) {
```

`@CurrentUser()` just reads `request.user`, which the guard populates. On a
`@Public()` route there may be no user at all, so typing it non-optional is a
lie the compiler will believe — and `user.sub` then throws at runtime for
exactly the guests the route exists to serve.

### The positional-argument trap

```ts
findAll(page, limit, eventId?, userId?, timing?, requestingUserId?)
```

`userId` filters by **author**. `requestingUserId` resolves "did *I* like this".
Both are "a user id" and they sit four positions apart. The original call passed
the viewer's id to **both**, so a public feed silently returned only the
viewer's own postcards.

Six positional parameters of which four are optional strings is the real defect
— no type can catch a swap between two `string | undefined` slots. An options
object would have made it impossible:

```ts
findPostcards({ page, limit, eventId, authorId, timing, viewerId })
```

**Heuristic: past three parameters, or any two adjacent ones of the same type,
switch to an options object.**
