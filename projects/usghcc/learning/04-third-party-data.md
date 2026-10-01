# 04 — Third-party data

Reading a vendor API (Eventzilla) from a Next.js server component: where the
trust boundary sits, how it should fail, and the caching that makes a vendor
outage invisible.

See also: [02-content-modelling.md](02-content-modelling.md) ·
[03-frontend.md](03-frontend.md) · [index.md](index.md)

---

## 1. The central idea: two validation boundaries, opposite failure modes

The site has two places where data enters. They validate the same way and fail
in **deliberately opposite** directions:

| Boundary | Source | On failure |
|---|---|---|
| `src/lib/content.ts` | our own JSON | **throws** — fails `next build` |
| `src/lib/eventzilla.ts` | a vendor's REST API | **never throws** — degrades |

The reasoning is about *who can fix it*:

- Our content is **our** mistake. Failing the build means we see it in CI and a
  visitor never does. Loud is correct.
- A vendor's API is neither our mistake nor our responsibility. It **will** be
  slow, rate-limited or down. A page that 500s because a ticketing provider is
  having a bad afternoon is strictly worse than one showing a slightly stale
  list.

Getting this backwards is a common and expensive mistake — treating a third
party as if it were reliable infrastructure, so their outage becomes your
outage.

---

## 2. Validate a vendor payload *loosely*

```ts
const eventzillaEventSchema = z
  .object({
    id: z.union([z.number(), z.string()]).transform(String),
    title: z.string().min(1),
    start_date: z.string().min(1),
    venue: z.string().optional(),
    // ...
  })
  .catchall(z.unknown());
```

Three choices worth understanding:

**Only require what you render.** Every required field is a way the page can
break. `title` and `start_date` are load-bearing; `twitter_hashtag` is not, so
it is not in the schema at all.

**`.catchall(z.unknown())` keeps unknown fields instead of stripping them.**
Zod's default `.strip()` silently drops anything undeclared. A third party adds
fields whenever they like, and that must never be an error *or* a surprise.

**`z.union([z.number(), z.string()]).transform(String)`** — a defensive parse.
IDs come back as numbers or numeric strings depending on the endpoint and the
day. Normalising at the boundary means one type downstream instead of
`String(id)` scattered through components.

### Skip the bad row, keep the good ones

```ts
for (const row of rows) {
  const parsed = eventzillaEventSchema.safeParse(row);
  if (!parsed.success) {
    console.warn("[eventzilla] skipping unparseable event:", ...);
    continue;                    // ← not `throw`, not `return []`
  }
  // ...
}
```

`safeParse` returns a result object instead of throwing, which is what makes
per-row recovery possible. One malformed event must not cost the visitor the
other thirteen.

---

## 3. Anti-corruption: their shape is not your shape

The adapter returns a type the app defines, not the vendor's:

```ts
export type ChamberEvent = {
  id: string;
  title: string;
  when: string;          // pre-formatted, timezone included
  startsAt: Date;        // for sorting and <time datetime>
  registrationUrl?: string;
  isPast: boolean;
};
```

Nothing outside `eventzilla.ts` knows the words `bgimage_url` or `dateid`.
That is the **anti-corruption layer** pattern: a vendor rename becomes a
one-file change instead of a search across every component.

It also puts derived facts where they belong. `isPast` is computed once at the
boundary, not recomputed by each component with a slightly different rule.

---

## 4. Caching: ISR is the outage-absorbing layer

```ts
await fetch(url, {
  headers: { "x-api-key": apiKey },
  next: { revalidate: 900, tags: ["events"] },
});
```

- **`revalidate: 900`** — the page is regenerated at most every 15 minutes.
  Events change rarely; a quarter-hour of staleness is invisible.
- **The property that matters:** while a revalidation is *failing*, Next keeps
  serving the last page that generated successfully. The vendor can be down for
  an hour and visitors see a slightly stale list rather than an error. This is
  the whole reason to prefer ISR over per-request fetching here.
- **`tags: ["events"]`** — leaves room for `revalidateTag("events")` from a
  webhook later, so a new event can appear immediately instead of waiting out
  the window.

**The trade-off to state out loud:** because the page is statically generated,
"now" is frozen at generation time. An event that starts ten minutes after a
revalidation still shows as upcoming for up to fifteen minutes. Acceptable
here; it would not be for a live scoreboard.

---

## 5. `server-only` — turning a possible leak into a build error

```ts
import "server-only";
```

A module holding an API key must never end up in a client bundle. Import
`server-only` at its top and any client component that pulls it in **fails the
build** with a clear message.

This is a guard, not documentation. Without it the failure mode is silent: the
key is inlined into the JavaScript sent to every visitor, and nothing looks
wrong.

The related rule: **`NEXT_PUBLIC_` is a publication instruction**, not a
namespace. Anything prefixed with it is substituted into the browser bundle at
build time. A secret with that prefix is a published secret.

### The `.gitignore` trap that nearly ate the template

`.gitignore` contained:

```
.env*
```

which matches `.env.example` as well. The only record of *which* variables the
app needs would never have reached the repo. Fix:

```
.env*
!.env.example
```

Check with `git check-ignore -v <path>` — it prints the file and line number of
the rule that matched, which is much faster than reading the patterns.

---

## 6. Timezones: format in the event's zone, always explicitly

```ts
new Intl.DateTimeFormat("en-US", {
  hour: "numeric",
  minute: "2-digit",
  timeZoneName: "short",
  timeZone: timeZone || "UTC",   // ← from the API, never implicit
}).format(startsAt);
```

Two separate problems solved by one argument:

**Correctness.** The chamber runs events in Philadelphia and Accra, several
hours apart. "10:00 AM" with no zone is ambiguous to precisely the audience
that needs it. `timeZoneName: "short"` appends EST / GMT.

**Hydration.** Omit `timeZone` and `Intl` uses the *runtime's* zone — UTC on a
typical Node host, the visitor's local zone in the browser. Server HTML and
client render disagree, and React reports a hydration mismatch. Any date
formatted on both sides needs an explicit zone.

Wrapped in try/catch: an unrecognised IANA name throws a `RangeError`, and a
vendor's bad timezone string must not take the page down.

---

## 7. Small things

**`<time dateTime={iso}>`** — the visible text is human-formatted with a
timezone; the attribute carries a machine-readable ISO string for assistive
tech and crawlers.

**`rel="noopener noreferrer"` on any cross-origin `target="_blank"`.** Without
`noopener`, the opened page receives a `window.opener` handle and can navigate
the original tab somewhere else — a live phishing vector, and it matters most
on pages about money or registration. Modern browsers imply it for
`target="_blank"`, but stating it is free and covers older ones.

**Filter by status before rendering.** `status` can be Draft or Unpublished —
content the organiser has explicitly not published. Never render it because it
happened to come back in the payload.

**Deciding against `next/image`.** Event artwork lives on a CDN whose hostname
was not confirmed from a real response. An unconfigured host makes `next/image`
**throw at request time** — a hard failure handed over by a third party. A
plain `<img loading="lazy">` degrades to a broken image instead. Reach for the
optimiser once the host is known; do not let it become a new failure mode.

---

## Outstanding — promote to the general vault

- [ ] Two validation boundaries with opposite failure modes (own data vs
      vendor data) → `concepts/04-best-practices/`
- [ ] Anti-corruption layer / adapter pattern → `architecture/`
- [ ] ISR as outage absorption; `revalidate` + tags → `frontend/02-rendering/`
- [ ] `server-only`, `NEXT_PUBLIC_` semantics, `git check-ignore -v` →
      `devops/09-secret-management/`
- [ ] `Intl.DateTimeFormat` explicit `timeZone` and the hydration-mismatch
      class of bug → `frontend/`
