# Backend — Sorepoint

The pipeline worker: Stage 1 (Places pull) and onward. A `tsx` script, cache-first
against Postgres, run outside Next.js. Teaching *why*, newest topics appended.

Layout as of Stage 1:

```
src/lib/env.ts            # env loading + validation (lazy getters)
src/lib/supabase-admin.ts # typed service-role client (bypasses RLS)
src/lib/osm.ts            # OSM source: Nominatim geocode + Overpass query
src/lib/places.ts         # Google Places source (deferred behind --source places)
src/pipeline/normalized.ts# NormalizedBusiness — the source-agnostic shape
src/pipeline/pull-core.ts # runPull: scan lifecycle, grid detection, upsert
src/pipeline/pull.ts      # CLI entry (npm run pull)
```

---

## 1. Why the pipeline is a script, not an API route

External calls (geocode, POI query, later per-site crawls) can outlive a
serverless request and must be resumable. So Stage 1 runs as `npm run pull` →
`tsx src/pipeline/pull.ts`, writing to Postgres. The Next app only ever *reads*
what the worker wrote. (See DECISIONS.md, "worker-not-route".)

`tsx` runs TypeScript directly — no build step, no `ts-node` config faff. It
resolves extensionless relative imports, so worker files use `./x` / `../lib/x`
rather than the `@/` alias (which is a Next/tsconfig concern); that keeps the
same import working under both `tsx` and Next.

---

## 2. Loading env without Next — Node's native env file

The worker runs outside Next, so Next's automatic `.env.local` loading doesn't
apply. Instead of adding `dotenv`, we use Node's built-in (Node 20.12+):

```ts
process.loadEnvFile('.env.local');   // reads the file into process.env
```

### Lazy getters so a source only needs its own key

`env` exposes **getters**, not eager values:

```ts
export const env = {
  get googlePlacesApiKey() { return required('GOOGLE_PLACES_API_KEY'); },
  // …
};
```

Why: an eager `required('GOOGLE_PLACES_API_KEY')` would throw at import time, so
an **OSM-only** run (which never touches Google) would fail for want of a key it
doesn't use. A getter validates only when the value is actually read — i.e. only
on the Google code path. Small change, real decoupling.

---

## 3. The source-adapter pattern

Stage 1 must not care *where* businesses come from. Every source returns the same
shape, `NormalizedBusiness`, and the core adds `tenant_id` / `scan_id` /
`is_grid_centroid`:

```ts
const SOURCES: Record<BusinessSource, (city, niche) => Promise<NormalizedBusiness[]>> = {
  osm: fetchFromOsm,
  places: fetchFromPlaces,
};
```

So switching source is `--source osm|places` — no change to the scan lifecycle,
grid-centroid detection, or upsert. This is what let us swap Google → OSM in an
afternoon when billing blocked us, and swap back later without touching the core.
The lesson: **put the volatile dependency behind a narrow, normalized interface.**

---

## 4. Getting real data free — OpenStreetMap (Nominatim + Overpass)

Google Places needs a billing account. OSM needs neither key nor billing, via two
free services:

1. **Nominatim** (geocoder): city string → bounding box.
   `GET nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=<city>`
   `boundingbox` comes back as `[min_lat, max_lat, min_lon, max_lon]`.
2. **Overpass** (the OSM query engine): POIs inside that box.
   `POST overpass-api.de/api/interpreter` with `data=<Overpass QL>`.

Overpass QL, generated per scan:

```
[out:json][timeout:25];
(
  nwr["amenity"="dentist"](6.29,3.23,6.61,3.55);   // (south,west,north,east)
);
out center tags;
```

- `nwr` = node + way + relation in one shorthand.
- `out center tags;` returns each element's centroid coordinate (ways/relations
  have no single lat/lon) plus its tags — exactly what we map from.
- A niche maps to a tag: a small dictionary (`dentist → amenity=dentist`), with a
  regex-across-category-keys fallback for anything unmapped.

Both services are fair-use: send an identifying `User-Agent`, one request each per
scan. (Firing many Overpass calls fast — as in a debug loop — gets you rate-limited
with a non-JSON error body; the real pipeline makes a single call, so it's fine.)

### OSM coverage is uneven — and that's honest, not broken

First run: **0 dentists in Lagos**. Not a bug — Lagos OSM has 131 restaurants but
0 tagged dentists. Coverage varies wildly by region and category. This suits the
product's ethos: an empty result is a *real, honest* empty, and Google-only signals
(reviews, owner replies) that OSM lacks become `unscanned` downstream rather than a
faked zero. When a query returns nothing, suspect data coverage before code — but
verify (we compared `dentist` vs `restaurant` in the same box to prove it).

---

## 5. Cache-first + resumable, and idempotent upserts

`runPull` is safe to run repeatedly:

- **get-or-create the scan** for `(tenant, city, niche)` — reuse the existing one
  rather than spawning duplicates.
- **cache-first:** if that scan already has businesses, skip the fetch entirely
  (unless `--force`). No wasted external calls while iterating.
- **idempotent write:** `upsert(rows, { onConflict: 'scan_id,place_id' })` against
  the `unique (scan_id, place_id)` key — `--force` re-fetched 123 rows and the
  total stayed 123, no duplicates.

This is the "DB is the cache" idea: every stage does only the missing work and
writes back, so a re-run is cheap and a crash is recoverable.

---

## 6. Stage 2 — one crawl, three signals, honest failures

`src/lib/crawl.ts` does **one** `fetch` per business (SPEC §3.1) and derives three
agents' inputs from it. The point is cheap + honest, not a real headless browser.

- **Only businesses with a `website_url` are crawled.** No website = nothing to
  fetch; that's the `site` agent's job straight from the listing.
- **Signals** from a successful 2xx HTML response:
  - `mobile_ready` = does the HTML contain `<meta name="viewport">`. A heuristic,
    not a true mobile-friendliness test — but cheap and a strong proxy.
  - `slow` = TTFB > 3s. `fetch` resolves when response headers arrive (before the
    body), so timing to that point ≈ time-to-first-byte.
  - `social_links_json` = hrefs matching known social domains; `booking_signal` =
    booking keywords/widget domains in the HTML.
- **Signals are `null` when we couldn't determine them** (non-2xx, non-HTML, or
  never connected) — never a defaulted `false`. `null` = "unknown" feeds
  `unscanned`; `false` would be a lie.

### Honest failure classification (the important bit)

A fetch can fail three very different ways, and conflating them would be
dishonest:

- **401 / 403 / 429** → `blocked = true`, `loaded = true`. The site answered; it
  just refused *us*. That's evidence about our crawler, so downstream it's
  `unscanned`, never a flaw of theirs (SPEC §3.3).
- **Network throw** (DNS, connection refused, TLS, timeout) → `loaded = false`,
  and the cause is labelled in `raw_meta_json.error` via `err.cause.code`
  (`ENOTFOUND`→`dns`, `ECONNREFUSED`→`refused`, `AbortError`→`timeout`, …). This
  is about *their* site being unreachable — a real flaw the `site` agent can flag.
- **2xx** → loaded and analysable.

`AbortController` + `setTimeout(() => controller.abort(), 10_000)` gives the
timeout; `clearTimeout` in `finally` so a fast success doesn't leak a timer.

### A real data-quality catch

First crawl produced `ERR_INVALID_URL` on two sites: OSM `website` tags are often
**bare domains** (`foo.com`, no scheme), which `fetch()` rejects. Fix — default a
missing scheme to `https://` before fetching. After that, those two resolved to
their true state: `dns` failures (the domains genuinely don't exist). The lesson:
external free data is messy at the edges — normalize inputs, and a fixed bug often
just reveals the *honest* underlying state.

### Concurrency without a library

21 sites sequentially is slow; unbounded is rude. A tiny fixed-size pool — N
workers pulling from a shared index until the list is exhausted — caps in-flight
requests at 6 with no dependency:

```ts
let next = 0;
async function worker() { while (next < items.length) { const i = next++; results[i] = await fn(items[i]); } }
await Promise.all(Array.from({ length: 6 }, worker));
```

---

## See also

- `supabase.md` — the service_role GRANTs-vs-RLS bug this worker hit, TypeGen, local stack
- app repo `~/code/spectroniq/sorepoint/DECISIONS.md` — worker-not-route, OSM-vs-Places
