# USGHCC — learning

Replatforming **usghcc.org** (US-Ghana Chamber of Commerce) off a compromised
WordPress install onto Next.js 16, with content held as validated JSON in the
repo and Sanity deferred.

The app repo is `~/code/usghcc/usghcc.org`. Architectural *decisions* live in
that repo's `DECISIONS.md` — this folder is the teaching counterpart: it
explains the ideas well enough to rebuild them from scratch.

| File | What it covers |
|---|---|
| [01-shell.md](01-shell.md) | Heredocs, `python3 -` as an editing tool, reading a 300-item XML export with grep, diagnosing a blocked download from HTTP headers |
| [02-content-modelling.md](02-content-modelling.md) | Blocks vs named fields, Zod as the runtime boundary, cross-field validation, why the type and the validator must be one definition |
| [03-frontend.md](03-frontend.md) | `next/image` with fixed-background logos, the YouTube facade, alt text vs `aria-label`, grid orphans, presentational props vs content |
| [04-third-party-data.md](04-third-party-data.md) | Reading a vendor API: loose validation, anti-corruption layers, ISR as outage absorption, `server-only`, timezone formatting |
| [05-maps-and-structured-data.md](05-maps-and-structured-data.md) | Web Mercator and map tiles, pre-rendering a static map, storing address parts vs display text, JSON-LD and the `<script>` injection escape, NAP consistency |

## See also (general vault)

Material here that is **not** specific to this project also belongs in the
general folders. Outstanding promotions are listed at the bottom of each file.
