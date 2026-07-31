# Caching

**[reference]** — from the roadmap.sh system-design roadmap. The highest-leverage performance tool in system design — and, per the famous quip, home to one of the two hard problems in computer science (invalidation).

## Why caching dominates

Most systems are **read-heavy** (far more reads than writes), and reads often hit the same hot data repeatedly. A **cache** stores the result of expensive work (a DB query, a computation, a rendered page) in fast storage (memory) so repeat requests skip the expense. Done well, it takes enormous load off the [[architecture/02-building-blocks/03-databases-at-scale|database]] (usually the first bottleneck) and slashes latency. It's usually the *first* thing you add when a system slows under read load.

## Where to cache (every layer)

Caching happens at every level of the stack:

- **Client / browser** — cache responses locally (HTTP cache headers), zero network for repeats.
- **CDN / edge** — static content near the user ([[architecture/02-building-blocks/01-load-balancing-and-proxies|CDN]]).
- **Reverse-proxy** — Nginx/Varnish caching full responses.
- **Application** — an in-process cache, or a shared cache like **Redis**/**Memcached** (the workhorse: a fast in-memory key-value store in front of the database).
- **Database** — the DB's own query/buffer cache.

More layers = more speed but more places for data to go stale.

## Caching strategies

How the cache and database stay coordinated — the core design choice:

- **Cache-aside (lazy loading)** — the app checks the cache; on a **miss**, it reads the DB, populates the cache, and returns. The most common pattern. Only requested data is cached (efficient), but the first request is slow (miss), and stale data is possible until eviction/invalidation.
- **Read-through** — the cache itself loads from the DB on a miss (the app only talks to the cache). Similar to cache-aside, encapsulated in the cache layer.
- **Write-through** — writes go to the cache *and* the DB synchronously. Cache is always fresh, but writes are slower (two writes).
- **Write-behind (write-back)** — writes go to the cache, which flushes to the DB asynchronously. Fast writes, higher throughput — but risk of data loss if the cache dies before flushing. (This is exactly the [[languages/01-java/06-applied-systems/03-batch-processing-and-performance|batched-write]] tradeoff.)
- **Refresh-ahead** — proactively refresh popular entries before they expire, so hot data never causes a miss.

## Eviction — the cache is finite

Memory is limited, so a cache must evict entries. Policies:

- **LRU (Least Recently Used)** — evict what hasn't been touched longest. The common default; good for temporal locality.
- **LFU (Least Frequently Used)** — evict the least-accessed. Better for stable hot sets.
- **FIFO / TTL** — evict oldest / expire after a time-to-live.

**TTL** (time-to-live) is the pragmatic tool for staleness: set a max age so data self-refreshes, trading a bounded window of staleness for simplicity.

## The hard problem: invalidation

The famous difficulty: **keeping the cache consistent with the source of truth.** When the underlying data changes, cached copies are now wrong. Approaches, none perfect:

- **TTL / expiration** — accept staleness up to the TTL. Simple, and usually good enough.
- **Explicit invalidation** — delete/update the cache entry when the DB changes. Correct but easy to miss a path (and hard across [[architecture/02-building-blocks/01-load-balancing-and-proxies|many cache nodes]]).
- **Write-through** — never stale, at the cost of write latency.

The judgment call is **how much staleness this data tolerates** — the same [[architecture/01-system-design-fundamentals/04-cap-and-consistency|consistency]] question as everywhere. A stock price needs seconds; a user's avatar can be stale for an hour.

## The gotchas

- **Cache stampede / thundering herd** — a popular key expires and thousands of simultaneous requests all miss and hit the DB at once, crushing it. Fixes: request coalescing (one fetch, others wait), staggered TTLs, refresh-ahead.
- **Caching is not free** — it adds a component, a consistency problem, and a failure mode (what happens when the cache is down? — the DB must survive the full load, or you have a new SPOF). Don't cache what isn't hot.

## Related
- [[architecture/02-building-blocks/03-databases-at-scale|Databases at Scale]] — what caching protects
- [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP & Consistency]] — the staleness tradeoff caching embodies
- [[devops/08-networking-and-web/02-web-servers-and-proxies|Web Servers & Proxies (devops)]] — proxy/CDN caching in practice
