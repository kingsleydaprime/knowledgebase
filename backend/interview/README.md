# Backend / Node — Interview Prep

**Built from a real interview (August 2026) that went badly** — every question in these two files was actually asked. That makes this the most useful bank in the vault, because it's not a guess at what gets asked.

## Files
1. [[backend/interview/01-production-debugging|Production Debugging]] — p99 spikes, per-AZ metrics, AZ impairment vs bad deploy, N+1 regressions, retry safety, retry storms
2. [[backend/interview/02-node-runtime-and-api|Node Runtime & API]] — `Promise.all` at scale, `Buffer` allocation, the event loop, streams, error handling

## What that interview was actually testing

Not Node trivia. **Production debugging judgment** — can you narrow a search space instead of guessing? Look at the shape of it:

- *p99 spikes → what do you check?* — bisect a latency distribution
- *AZ impaired or recent deploy?* — bisect by metric dimension
- *N+1 caused a regression* — bisect to a code change
- *retry safety, retry storms* — don't make it worse while you're diagnosing
- *`Promise.all` with 200 requests* — do you understand what your own code does to a downstream
- *`new Buffer` vs `Buffer.alloc`* — do you know why an API was deprecated, not just that it was

That's [[PRIMETECHIE|Rank II — the Diagnostician]], almost item for item. It's the rank the path calls "unglamorous and the one that separates people," and it's the one to drill.

## The three highest-leverage things to fix

1. **Instrument event loop delay** in a real service and watch it. Node's signature failure — p99 spikes, flat p50, low CPU — is invisible until you measure this, and it's the answer to the first question they asked.
2. **Tag metrics with `az` and `version`.** That one design decision turns "is it the AZ or the deploy?" from an investigation into a dashboard query.
3. **Know the retry trio cold:** full jitter, retry budgets, and *retry at one layer only*. Amplification is the thing that turns a blip into an outage.

## Related
- [[foundations/networking/interview/04-debugging-and-scenarios|Networking: debugging scenarios]] — the same bisecting method, one layer down
- [[databases/interview/01-sql-modelling-and-internals|Databases]] — connection pool sizing, query plans
- [[devops/interview/01-linux-containers-and-operations|DevOps]] — incident response, cgroup CPU throttling
- [[architecture/interview/01-system-design-round|Architecture]] — resilience patterns, caching
- [[INTERVIEW|Interview index]]
