---
id: 95c42c75-5bd0-4eff-be94-40a8d2d9f03d
---

# Network Performance

Network performance is how quickly data gets from one place to another, and it depends on two different things: how much data can flow at once, and how long each trip takes. A faster internet plan does not always make an app feel faster. This lesson shows which of the two really matters for what you build.

## The kid version first
<!-- bite: 344a37d8-db25-4a84-9a23-bd88bce6593e -->

Two ways to move data:

- **A truck full of hard drives driving across the country.** Enormous **bandwidth** (petabytes), terrible **latency** (two days).
- **A person shouting across a room.** Tiny bandwidth, near-zero latency.

Now: which one do you want for a conversation? Not the truck — even though it moves vastly more data. Because a conversation is **many small exchanges that each depend on the last**, and every exchange costs one full trip.

Nearly everything an application does over a network is a conversation. That's why **latency, not bandwidth, is what makes things feel slow** — and why buying a faster connection so often changes nothing.

## The two dimensions, and why one is fixable
<!-- bite: 56d1de0e-6229-4c05-ba51-61192f3cf61b -->

- **Bandwidth** — bytes per second. Improvable: lay more fibre, buy a bigger link. It has roughly doubled every couple of years for decades.
- **Latency** — time for one round trip. **Bounded by physics.** Light in fibre travels ~200,000 km/s. Lagos → London is ~5,000 km, so ~25ms one way, **~50ms round trip minimum**, before any router, queue, or server. You cannot buy your way under it.

Lagos → US East is ~110ms RTT. Lagos → Singapore ~250ms. Those numbers are permanent facts about your users' experience, and they're why **CDNs and edge compute exist** — the only way to reduce distance is to move the data closer.

**The latency numbers worth memorising** (Jeff Dean's list, roughly):

| Operation | Time | In "if L1 were 1 second" terms |
|---|---|---|
| L1 cache reference | 1 ns | 1 second |
| Main memory | 100 ns | 100 seconds |
| SSD random read | 16 µs | 4.5 hours |
| Same-datacentre round trip | 500 µs | 6 days |
| Disk seek | 2 ms | 23 days |
| **Lagos → London round trip** | **~50 ms** | **~19 months** |
| **Lagos → US East round trip** | **~110 ms** | **~3.5 years** |

The point of the right-hand column: a network round trip isn't "a bit slower" than a memory access — it's *four to six orders of magnitude* slower. An N+1 query that makes 50 sequential calls across a WAN isn't inefficient, it's a different category of program.

## Bandwidth-delay product — the pipe you must keep full
<!-- bite: 9573f284-c731-4c4e-9ee2-76ad3c1258e9 -->

```text
BDP = bandwidth × RTT
```

This is how much data must be **in flight** to keep a link saturated. On a 1 Gbps link with 100ms RTT: `1,000,000,000 / 8 × 0.1 = 12.5 MB`.

If your [[networking/07-tcp-reliability-and-flow-control|TCP window]] is smaller than the BDP, you **cannot** use the full bandwidth no matter what — the sender stalls waiting for ACKs. The unscaled 64 KB window maxes out at 640 KB/s on a 100ms path, which is why window scaling is essential and why a stripped window-scale option produces "fast locally, mysteriously slow long-distance."

This is the "**long fat network**" problem, and it's the reason bulk transfers between continents need tuned buffers, parallel streams, or protocols designed for it.

## Where the time actually goes on a first page load
<!-- bite: d2e3bdb4-b248-4558-b98e-8abb5fb448a0 -->

Count the round trips before the first byte of HTML:

```text
DNS lookup                     1 RTT   (or more, if uncached up the chain)
TCP handshake                  1 RTT
TLS 1.3 handshake              1 RTT
HTTP request → first byte      1 RTT
                              ──────
                               4 RTT   ≈ 440ms at 110ms RTT — before any content
```

Then [[networking/08-congestion-control|slow start]] means the first response is capped around 14 KB, doubling per RTT afterwards. A 100 KB HTML file takes ~3 more round trips *even on a gigabit link*.

**This is why the entire web performance industry is about eliminating round trips, not adding bandwidth:**

| Technique | Round trips saved |
|---|---|
| Connection reuse / keep-alive | TCP + TLS on every subsequent request |
| **CDN / edge** | reduces the RTT itself — the only fix for physics |
| TLS 1.3 | 1 RTT vs 1.2 |
| [[networking/13-quic-and-modern-transport\|QUIC]] 0-RTT | the entire handshake on resumption |
| DNS prefetch / `preconnect` | overlaps DNS+TCP+TLS with page parse |
| HTTP/2 multiplexing | removes serialised request queuing |
| Caching (`immutable`, `ETag`) | the request entirely — unbeatable |

Note the ranking: **not making the request at all > making it closer > making it in fewer trips > making it faster.** Optimise in that order.

## Throughput ceilings you should be able to derive
<!-- bite: 241176db-a722-472f-9c3e-ca5a9ef18f2f -->

The **Mathis equation** approximates loss-based TCP throughput:

```text
throughput ≈ MSS / (RTT × √p)        p = packet loss probability
```

The `√p` is the striking part. At 1500-byte MSS and 100ms RTT: 0.01% loss gives ~120 Mbps; **0.1% loss gives ~38 Mbps; 1% loss gives ~12 Mbps.** A "barely noticeable" 1% loss rate costs you 90% of your throughput.

This is why **packet loss matters far more than users expect**, why a marginally lossy Wi-Fi link tanks a download while a video call still works (UDP doesn't care), and why [[networking/08-congestion-control|BBR]] — which doesn't treat loss as the sole congestion signal — can dramatically outperform CUBIC on lossy paths.

## Tail latency, and why averages lie
<!-- bite: b083d3db-c265-43c0-90b5-7c528bee6510 -->

In [[architecture/index|distributed systems]], p99 matters more than the mean, for a reason that's easy to miss: **if one user request fans out to 100 backend calls, the user waits for the slowest.** With a p99 of 1 second, a 100-call fan-out has a ~63% chance of hitting at least one — so your *median* user experiences your *p99* backend.

Tail latency sources are disproportionately network- and transport-level: [[networking/08-congestion-control|RTO timeouts]] after tail loss, incast at a top-of-rack switch, bufferbloat, garbage collection pauses coinciding with a retransmit, [[networking/10-dns-in-depth/index|DNS]] timeouts.

The standard mitigations — **hedged requests** (send to a second replica after p95 elapses, take the first answer), **tied requests**, and shrinking the fan-out — are all about not letting one slow path dominate. Jeff Dean's "The Tail at Scale" is the paper.

## The mental model to keep
<!-- bite: bd6ee19d-bac1-4132-aa60-88daddf40ece -->

1. **Round trips dominate.** Count them before optimising anything else.
2. **Latency has a floor set by distance.** Only moving closer helps.
3. **Bandwidth is usually not your problem.** Measure before you buy.
4. **Small loss rates destroy TCP throughput** (the `√p`).
5. **Averages hide the problem.** Look at p99.
6. **The fastest request is the one you don't make.** Cache.

## Key insight
<!-- bite: c70817b0-5d5f-4c60-8580-2529f247d419 -->

Bandwidth has improved by orders of magnitude in thirty years; **latency has improved barely at all, and cannot**, because it's bounded by the speed of light in glass. Every serious performance technique in modern networking — CDNs, caching, 0-RTT handshakes, multiplexing, prefetching, edge compute — is an attempt to work around one unfixable physical constant. Design as if a round trip is the expensive operation, because it is the *only* one you can't make faster.

## Check your understanding
<!-- bite: 14681ba1-aeb7-4bfc-8f82-4bfa4dc5b412 -->

Try each one before you open the answer.

1. <!-- q: exact id="d5fb57fa" answer="60" -->
   Light in fibre travels about 200,000 km/s. Two cities are 6,000 km apart along the fibre. What is the minimum round-trip time, in milliseconds, before any router or server adds delay?

   <details><summary>Answer</summary>

   60 ms. One way is 6,000 / 200,000 = 0.03 s = 30 ms, and a round trip is twice that. No upgrade can beat it; only moving the data closer (a CDN or edge server) helps.

   </details>

2. <!-- q: exact id="9aad316f" answer="6.25" accept="6.25 MB|6.25MB" -->
   A link runs at 500 Mbps with a 100 ms round trip. What is the bandwidth-delay product, in megabytes (1 MB = 1,000,000 bytes)?

   <details><summary>Answer</summary>

   6.25 MB. 500,000,000 bits/s ÷ 8 = 62,500,000 bytes/s, times 0.1 s = 6,250,000 bytes. That much must be in flight to fill the link, so the TCP window has to be at least that big.

   </details>

3. <!-- q: exact id="24d92bcd" answer="320" -->
   A first page load needs 4 round trips (DNS, TCP, TLS 1.3 and the request) before the first byte of HTML arrives. The round trip is 80 ms. How many milliseconds pass before any content arrives?

   <details><summary>Answer</summary>

   320 ms (4 × 80), and that's before slow start limits how fast the rest arrives. That's why the techniques that help most remove round trips rather than add bandwidth.

   </details>

4. <!-- q: mcq id="95fd9d20" -->
   By the Mathis equation, TCP throughput falls with the square root of the packet loss rate. Loss rises from 0.01% to 1%, a hundredfold increase. Roughly what happens to throughput?

   - [ ] It halves
   - [x] It falls to about a tenth
   - [ ] It falls to a hundredth
   - [ ] It stays the same

   <details><summary>Answer</summary>

   About a tenth, because √100 = 10. In the lesson's example, 120 Mbps falls to about 12 Mbps. Small loss rates cost TCP far more than people expect.

   </details>

5. <!-- q: mcq id="949094a6" -->
   Put these from most to least effective at speeding up a request. Which comes first?

   - [x] Not making the request at all, because it's cached
   - [ ] Making it to a closer server
   - [ ] Making it in fewer round trips
   - [ ] Making it over a faster link

   <details><summary>Answer</summary>

   Not making it. The order is: don't make it (cache), make it closer (CDN), make it in fewer trips (reuse, TLS 1.3, QUIC), then make it faster.

   </details>

6. <!-- q: open id="c0a6afc0" -->
   Each user request fans out to 100 backend calls in parallel, and each backend is slow 1% of the time. Why does this make p99 the number that matters, rather than the average?

   <details><summary>Answer</summary>

   The user waits for the slowest of the 100 calls. The chance that all 100 are fast is 0.99¹⁰⁰ ≈ 37%, so about 63% of user requests hit at least one slow call. Your typical user experiences your backend's p99. Hedged requests and smaller fan-outs help.

   </details>

## Related
<!-- bite: 85aceb36-8886-440b-aeef-cb79e5f608e7 -->
- [[networking/08-congestion-control|Congestion Control]] — slow start and the first-response ceiling
- [[networking/13-quic-and-modern-transport|QUIC]] — the round-trip reduction endgame
- [[architecture/02-building-blocks/02-caching/index|Caching]] — the request you don't make
- [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|Scalability & Performance]] — the system-design framing

## About this lesson
<!-- bite: 87b3e856-eea3-4210-a6a5-cdf4ae19b8cd -->

**Level:** Intermediate→Advanced. **Covers:** the note that changes how you build things. Most engineers optimise the wrong dimension for years, because the intuition ("faster internet = faster app") is wrong in a specific, expensive way.
