# Sorepoint — Pipeline & Crawling

From [`../learning/backend.md`](../learning/backend.md). Stage 1 (Places pull) and Stage 2 (crawl).

---

### Q1. [Intermediate] 🔥 Why is the pipeline a standalone script rather than a Next.js API route?

**Strong answer covers:** the external calls — geocode, POI query, then a fetch per business site —
can outlive a serverless request, and the work must be **resumable** across crashes and reruns. So
it runs as `npm run pull` → `tsx src/pipeline/pull.ts`, writing to Postgres, and the Next app only
ever *reads* what the worker wrote. That split also means the web tier has no long-running work in
it at all, so it can stay on a serverless deployment target.

**Detail worth adding:** `tsx` runs TypeScript directly with no build step and resolves
extensionless relative imports, so worker files use `./x` / `../lib/x` rather than the `@/` alias
(which is a Next/tsconfig concern). Same import works under both runtimes.

---

### Q2. [Intermediate] The worker runs outside Next, so `.env.local` isn't loaded automatically. How did you handle that without adding `dotenv`?

**Strong answer covers:** Node's built-in `process.loadEnvFile('.env.local')` (Node 20.12+). One
line, no dependency.

**The more interesting half — lazy getters:** `env` exposes **getters**, not eager values, so
`required('GOOGLE_PLACES_API_KEY')` only throws when that value is actually *read*. Eager
validation at import time would make an OSM-only run fail for want of a Google key it never
touches. Small change, real decoupling — validation scoped to the code path that needs the value.

**Follow-up:** *"How does that compare to strictenv's fail-at-boot philosophy?"* — genuinely
opposite, and both are right in context. A single-config app wants everything checked at boot; a
multi-source worker where each source needs different credentials wants per-path validation.
Naming that tension unprompted is a strong move.

---

### Q3. [Intermediate] 🔥 Describe the source-adapter pattern and what it actually bought you.

**Strong answer covers:** every source returns the same shape — `NormalizedBusiness` — and the core
adds `tenant_id` / `scan_id` / `is_grid_centroid`. Sources live in a lookup
(`{ osm: fetchFromOsm, places: fetchFromPlaces }`), so switching is `--source osm|places` with no
change to the scan lifecycle, grid-centroid detection, or upsert logic.

**What it bought:** Google Places requires a billing account. When billing blocked the project, the
whole source swapped to OpenStreetMap in an afternoon — and could swap back later — without
touching the core.

**The rule:** put the **volatile** dependency behind a narrow, normalised interface. Not every
dependency; the one whose availability, pricing, or terms you don't control.

---

### Q4. [Intermediate] Walk me through getting real business data with no API key and no billing.

**Strong answer covers:** two free OSM services, in sequence —
1. **Nominatim** (geocoder): city string → bounding box, returned as
   `[min_lat, max_lat, min_lon, max_lon]`.
2. **Overpass** (the OSM query engine): POIs inside that box, via an Overpass QL query POSTed to
   the interpreter.

The generated query uses `nwr` (node + way + relation in one shorthand) filtered by tag, bounded by
`(south,west,north,east)`, with `out center tags;` — `center` because ways and relations have no
single lat/lon, so you need the centroid; `tags` because that's what you map from. A niche maps to
a tag via a small dictionary (`dentist → amenity=dentist`) with a regex-across-category-keys
fallback for anything unmapped.

**Fair-use detail an interviewer will like:** send an identifying `User-Agent`, one request each per
scan. Firing many Overpass calls fast (a debug loop) gets you rate-limited with a non-JSON error
body — so the failure doesn't even look like a rate limit unless you're expecting it.

---

### Q5. [Advanced] 🔥 Your first run returned zero dentists in Lagos. How did you know it wasn't a bug?

**Strong answer covers:** by testing the hypothesis rather than assuming either way — the same
bounding box queried for `restaurant` returned 131 results, so the query, the box, and the parsing
were all fine. Lagos OSM genuinely has zero tagged dentists. **OSM coverage varies wildly by region
and category**, and that's a data property, not a defect.

**Why it suits the product:** an empty result is a *real, honest* empty. Google-only signals
(reviews, owner replies) that OSM simply lacks become `unscanned` downstream rather than a faked
zero. The general habit: when a query returns nothing, suspect data coverage before code — but
**verify it** with a control query rather than believing your first guess.

---

### Q6. [Intermediate] 🔥 What makes `runPull` safe to run repeatedly?

**Strong answer covers:** three properties working together —
- **get-or-create the scan** for `(tenant, city, niche)` — reuse the existing scan rather than
  spawning duplicates on every invocation;
- **cache-first** — if that scan already has businesses, skip the external fetch entirely unless
  `--force`, so iterating on later stages costs no external calls;
- **idempotent write** — `upsert(rows, { onConflict: 'scan_id,place_id' })` against a
  `unique (scan_id, place_id)` constraint. Verified: `--force` re-fetched 123 rows and the total
  stayed 123.

**The idea to name:** "the DB is the cache." Every stage does only the missing work and writes back,
so a re-run is cheap and a crash is recoverable.

---

### Q7. [Advanced] 🔥 You derive three agents' inputs from *one* fetch per business. Why one, and what do you extract?

**Strong answer covers:** one `fetch` per business, deliberately — cheap and honest rather than a
real headless browser. Only businesses with a `website_url` are crawled at all (no website means
nothing to fetch; that's a signal in itself, straight from the listing). From a successful 2xx HTML
response:
- `mobile_ready` — does the HTML contain `<meta name="viewport">`. Explicitly a **heuristic**, not a
  true mobile-friendliness test, but cheap and a strong proxy.
- `slow` — TTFB > 3s. `fetch` resolves when response *headers* arrive, before the body, so timing to
  that point approximates time-to-first-byte.
- `social_links_json` and `booking_signal` — hrefs matching known social domains, and booking
  keywords/widget domains in the HTML.

**Say the heuristic word out loud.** Claiming `<meta viewport>` proves mobile-friendliness is the
wrong answer; knowing it's a proxy and choosing it anyway for cost reasons is the right one.

---

### Q8. [Advanced] 🔥🔥 A fetch can fail three different ways. Why does conflating them matter?

**Strong answer covers:** because the product's output is an accusation about someone's website, so
the difference between "their site is broken" and "their site refused *us*" is the difference
between a valid finding and a libel.

- **401 / 403 / 429** → `blocked = true`, `loaded = true`. The site answered; it just refused our
  crawler. That's evidence about **us**, so downstream it's `unscanned` — never a flaw of theirs.
- **Network throw** (DNS, connection refused, TLS, timeout) → `loaded = false`, with the cause
  labelled from `err.cause.code` (`ENOTFOUND`→`dns`, `ECONNREFUSED`→`refused`, `AbortError`→
  `timeout`). That's about *their* site being unreachable — a real flaw an agent can flag.
- **2xx** → loaded and analysable.

**The companion rule:** signals are `null` when undeterminable (non-2xx, non-HTML, never connected)
— **never a defaulted `false`**. `null` means unknown and feeds `unscanned`; `false` would be a lie
that later gets rendered as a finding.

---

### Q9. [Intermediate] How do you implement the crawl timeout, and what's the leak to avoid?

**Strong answer covers:** `AbortController` plus `setTimeout(() => controller.abort(), 10_000)`
passed as the fetch `signal` — and `clearTimeout` in a `finally`, so a fast success doesn't leave a
pending timer holding the event loop open. That's the bit people forget; the timeout works either
way, but without the clear, a short run doesn't exit when it should.

---

### Q10. [Intermediate] 🔥 Two sites failed with `ERR_INVALID_URL`. What was wrong and what did the fix reveal?

**Strong answer covers:** OSM `website` tags are frequently **bare domains** (`foo.com`, no scheme),
which `fetch()` rejects outright. Fix: default a missing scheme to `https://` before fetching. After
that, those two resolved to their *true* state — `dns` failures, because the domains genuinely
don't exist.

**The lesson to state:** free external data is messy at the edges, so normalise inputs at the
boundary — and a fixed bug often just reveals the honest underlying state rather than turning a
failure into a success. If you'd "fixed" it by skipping malformed URLs, you'd have lost two real
findings.

---

### Q11. [Intermediate] You capped crawl concurrency at 6 with no library. Show me the shape and justify the number.

**Strong answer covers:** a fixed-size worker pool over a shared index —

```ts
let next = 0;
async function worker() { while (next < items.length) { const i = next++; results[i] = await fn(items[i]); } }
await Promise.all(Array.from({ length: 6 }, worker));
```

N workers pull from one cursor until the list is exhausted; in-flight requests never exceed N, and
results stay index-aligned with inputs. Sequential is too slow for ~21 sites; unbounded is rude to
the sites being crawled and to whatever network you're on. The number is a politeness/latency
trade-off, not a computed optimum — say that rather than inventing a justification.

**Follow-up:** *"Why not `p-limit`?"* — six lines versus a dependency, in a worker that already has
a "no unnecessary deps" posture. If back-pressure, retries, or per-host limits were needed, the
calculus flips.

---

### Q12. [Advanced] How would you make the crawl polite per-host rather than globally?

**Strong answer covers:** the current pool caps *total* in flight, which is fine when every business
is on a different domain but wrong if many share a host (agency-built sites, shared platforms).
Per-host politeness needs a queue keyed by hostname with its own concurrency of one or two and a
minimum delay between requests to the same host — plus honouring `robots.txt` and `Retry-After`.
Worth naming even if unbuilt: knowing the limit of your own concurrency model reads better than
defending it as complete.
