# Load Balancing & Proxies

> **[Intermediate]** · From the roadmap.sh system-design roadmap. The traffic-routing layer that makes [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|horizontal scaling]] possible: how a load balancer picks a server and why the choice matters most in the slow tail, how health checks take a broken server out and put it back, what layer 4 and layer 7 mean, and how consistent hashing spreads keys over cache nodes without moving most of them when one is added. Reverse proxies, API gateways and CDNs complete the picture. The worked example scales week 1's shop from one app server to four. Overlaps the operations view in [[devops/08-networking-and-web/02-web-servers-and-proxies|DevOps web servers and proxies]]; this is the system-design view.

## Before you start

You can already:

- Explain why horizontal scaling needs stateless servers, and read p50 and p99 → [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|scalability and performance]].
- Explain how a cache's hit ratio sets the database's load, and what a cold cache does → [[architecture/02-building-blocks/02-caching/index|caching]].
- Say what TCP, an IP address and a port are, and what an HTTP request contains (method, path, headers) → [[networking/11-http-evolution|HTTP and its evolution]] (a skim is enough).
- Run a TypeScript test file with Node 26 (`node --test`).

After this lesson you will be able to:

1. Choose a balancing algorithm for a workload, and explain from a simulation why round-robin's p99 is more than twice least-outstanding's when some requests are slow.
2. Trace a server through health checks as it fails and recovers, and say what the balancer does when every server is down.
3. Tell a layer 4 balancer from a layer 7 one, and a reverse proxy from an API gateway and a CDN, by what each can see and do.
4. Explain why hashing keys modulo the number of cache nodes moves 80% of them when a fifth node is added, and how a hash ring moves only about 20%.

**Study route:** sections 1–3 set up the picture. Stop at the predictions in sections 4, 6 and 7 and try them before reading on. Section 10 is the worked example and section 11 the lab. Sections 8 and 9, on proxies, gateways and CDNs, are shorter and can be read on their own.

## The kid version

A busy supermarket has eight tills and a person at the end of the aisles pointing each shopper to one. Pointing to each till in turn is fair, but if one shopper has a trolley piled high, everyone sent to that till after them waits. Pointing to the shortest queue works better. If a till breaks, the pointer stops sending people there, and starts again only once it's clearly fixed. And the pointer must never go on a break, because then no one gets to any till.

**Where the analogy stops working.** The pointer can see every queue and every trolley. A load balancer usually can't see how long a request will take, only how many it has sent to each server that haven't finished yet, and a busy site has several balancers, each seeing only its own share. Also, shoppers don't care which till they use. Some requests do, because the data they need lives on one particular server, and section 7 is about sending them to the right one.

## 1. Why this exists

In week 1, the shop's checkout needed a second server, and then four. Adding servers is easy. The hard part is that customers' browsers know one address. Something has to stand at that address, receive every request and hand each one to a server that's up and not overloaded. Without it, extra servers sit idle. And when one of the four servers crashes during a sale, a quarter of customers shouldn't see errors until someone wakes up and notices. That something is the load balancer.

## Terms used in load balancing

1. **Load balancer**: This is a component that receives requests at one address and passes each one to one of several servers, so that the servers share the work.
2. **Backend**: This is also known as an **upstream** server. This is one of the servers the load balancer sends requests to. The group of them is the **pool**.
3. **Outstanding requests**: This is the number of requests the balancer has sent to a server that haven't been answered yet. A balancer that counts open connections instead calls this **least connections**.
4. **Health check**: This is a small test request the balancer sends to each backend on a schedule, such as `GET /health` every few seconds, to decide whether the backend is fit to receive traffic.
5. **Draining**: This means letting a backend finish the requests it already has while sending it no new ones, so it can be stopped without cutting anyone off. It's used during deploys.
6. **L4 (layer 4)**: The name comes from the transport layer of the network model, the layer of TCP and UDP. A layer 4 balancer routes by IP address and port, without reading the request inside.
7. **L7 (layer 7)**: The name comes from the application layer of the network model, the layer of HTTP. A layer 7 balancer reads the request, so it can route by path, host name or header.
8. **TLS termination**: This means decrypting HTTPS at the balancer or proxy, so the servers behind it receive plain requests and don't each need the certificates.
9. **SPOF (single point of failure)**: The letters stand for those words. This is any one component whose failure takes the whole system down.
10. **Sticky session**: This is also known as **session affinity**. It means the balancer sends every request from one client to the same backend, usually by a cookie or by hashing the client's address.
11. **Consistent hashing**: This is a way of assigning keys to servers so that adding or removing a server moves only the keys that have to move, about one share's worth, instead of nearly all of them.
12. **Virtual node**: This is one of many positions a single server takes on a consistent-hashing ring. Giving each server many positions evens out how many keys each gets.
13. **Reverse proxy**: This is a server that receives requests on behalf of other servers and forwards them. The client talks only to the proxy. A load balancer is one kind.
14. **Forward proxy**: This is a server that sends requests out on behalf of clients, such as an office proxy that all browsers go through. It fronts the clients, not the servers.
15. **API gateway**: This is a reverse proxy that is the single entry point to many services, handling concerns they all share, such as checking who the caller is, limiting request rates and routing to the right service.
16. **CDN (content delivery network)**: The letters stand for those words. This is a network of servers spread around the world that keep copies of content close to users, so requests are answered nearby instead of by your servers.
17. **Origin**: This is your own server, the source a CDN or proxy fetches content from when it doesn't have a copy.

## 2. What a load balancer does

It has three jobs:

1. **Spread the load** across the backends, using an algorithm (section 4).
2. **Route around failure.** Health checks find backends that are down and the balancer stops sending them traffic (section 6). This is the [[architecture/01-system-design-fundamentals/03-availability-and-reliability|failover]] mechanism for the servers behind it.
3. **Make the servers interchangeable.** Because any request can go to any server, the servers must be stateless: sessions and baskets live in a shared store, not in one server's memory. The balancer doesn't do this itself; it's what using one forces you to do.

The balancer is now in front of everything, so **it must not be a single point of failure itself**. The usual answers are a pair of balancers sharing one address that moves to the standby if the active one dies, several balancers behind DNS, or a cloud provider's managed balancer, which is redundant by design.

## 3. Layer 4 or layer 7

The difference is how much of the request the balancer reads:

- A **layer 4** balancer sees the connection: source and destination IP addresses and ports. It picks a backend when the connection opens and forwards its bytes without reading them. It's very fast and works for any protocol (databases, game servers, raw TCP), but it can't route by URL, and every request on a long-lived connection goes to the same backend.
- A **layer 7** balancer understands HTTP. It terminates TLS, reads each request, and can send `/api/*` to one pool and `/images/*` to another, route by host name, add headers, retry a failed request on another backend, and balance each request separately even when they share one connection. It costs more processing per request. It's the usual choice for web applications, and it's what Nginx, HAProxy in HTTP mode, Envoy and cloud application balancers are.

A common layout uses both: a layer 4 balancer spreads connections over several layer 7 balancers, which route the requests.

## 4. Choosing a server: the algorithms

How the balancer picks a backend for each request:

- **Round-robin.** Each server in turn: 1, 2, 3, 4, 1, 2, … It's simple and fair when every request costs the same.
- **Random.** Any server. Over many requests it evens out, with no shared counter to keep.
- **Least outstanding requests**, or least connections. The server with the fewest requests in progress. It adapts when requests vary in length or a server slows down.
- **Power of two choices.** Pick two servers at random and send the request to the less busy of the two. Section 5 explains why this is so good.
- **Weighted** versions of any of these, so a server with twice the capacity gets twice the share.
- **Hashing** on something in the request, so the same client or key always reaches the same server (section 7).

The choice matters when requests vary. Picture four servers, each working through its own queue one request at a time. Most requests take 10 ms, but 1 in 20 is a search that takes 200 ms. Server 1 has just received a search, and round-robin's turn comes back round to it.

**Predict before reading on.** What happens to the 10 ms request that round-robin sends to server 1 next? Rank round-robin, random, least-outstanding and two-choices by p99, best first.

<details>
<summary>After your prediction</summary>

It waits up to 200 ms behind the search, although three other servers may be idle. Round-robin keeps sending server 1 its turn because it never looks at the queues. The lab simulates 100,000 requests through four servers at 80% busy:

```
algorithm            mean    p50     p99    (ms)
round-robin           214    138   1,158
random                255    159   1,588
least-outstanding      68     17     466
two choices            96     25     495
```

Least-outstanding is best, with two choices close behind, and both beat round-robin by more than 2× at p99 and at least 5× at p50. Random is worst, because it can send several requests in a row to an already-long queue. At 50% busy the order is the same and the gaps smaller: p99s of 404, 476, 208 and 295 ms. **When request times vary, use an algorithm that looks at the queues.** When every request costs the same, round-robin is fine and simplest.

</details>

## 5. Why two random choices are nearly as good as all of them

Least-outstanding needs an accurate, up-to-date count for every server. With one balancer that's easy. A busy site has several balancers, though, each seeing only its own requests. Worse, if they all see the same "least busy" server, they all send to it at the same moment and pile it up, which is called herding.

Two choices sidesteps both. Each balancer looks at only two random servers, so different balancers usually pick different pairs and don't herd. And avoiding the worse of two random servers turns out to be most of the benefit: in the lab, two choices gets p99 to 495 ms against least-outstanding's 466, from round-robin's 1,158. That's why Envoy's least-request balancer compares two random servers by default instead of checking them all, and why many large systems balance the same way.

## 6. Health checks: taking a server out and putting it back

The balancer checks each backend on a schedule, say every 2 seconds. Two thresholds decide when to act:

- **Fall:** how many failed checks in a row before the server is marked down. One slow check during a garbage-collection pause shouldn't remove a healthy server.
- **Rise:** how many good checks in a row before a down server is put back. A server that's crash-looping, up for a second then down again, shouldn't keep receiving traffic between crashes.

HAProxy's defaults are a fall of 3 and a rise of 2. Follow one server with those settings through these check results: fail, fail, pass, fail, fail, fail, pass, pass.

**Predict before reading on.** After which check is it marked down, and after which is it back?

<details>
<summary>After your prediction</summary>

The pass at check 3 resets the count, so the two early failures don't add up to three. It's marked down after check 6, the third failure in a row, and back after check 8, the second pass in a row. With checks every 2 seconds, a crashed server keeps receiving traffic for up to about 6 seconds before it's removed. That's the cost of not overreacting, and why it pays to also watch real responses: a balancer can mark a server down quickly if its live requests start failing (passive checking), without waiting for the scheduled checks.

</details>

Two more rules complete it:

1. **When every server is down, there is nowhere to send traffic.** The lab's `pickHealthy` answers with a 503 error. Some balancers instead send traffic to all servers anyway, on the theory that the checks are probably what's broken. Either way, decide it on purpose.
2. **The health check must test what matters, but not too much.** A `/health` that returns 200 while the database connection is dead keeps a broken server in the pool. One that fails whenever the database is slow takes *every* server out at once, which turns a slow database into a total outage. Check the server's own ability to work, and handle a dependency's failure in the request path.

## 7. When the same key must reach the same server

Section 2 said servers should be stateless, and for app servers they should. Sticky sessions, which pin each user to one server, are a way to avoid moving session state out of server memory. But they spread load unevenly, and when that server dies its users lose their sessions. Prefer stateless servers with a shared session store.

Some servers are stateful by design, though: **cache nodes.** When the shop's cache grows past one Redis node, each product must live on exactly one of four nodes, and every app server must agree which. The obvious rule is to hash the key and take the remainder: node = hash(key) mod 4.

**Predict before reading on.** The sale needs a fifth cache node. With the mod rule, what share of keys now map to a different node?

<details>
<summary>After your prediction</summary>

About **four in five**. A key stays put only if hash mod 4 equals hash mod 5, which happens for 4 of every 20 values. In the lab, 7,961 of 10,000 keys move. Every one of them is a miss on its new node, so adding capacity has turned most of the cache cold, in the middle of a sale, and the database gets nearly the full read rate. Section 3 of [[architecture/02-building-blocks/02-caching/index|caching]] showed what that does.

</details>

**Consistent hashing** fixes this. Picture the hash values as a circle, from 0 round to the largest value and back to 0. Each node is placed on the circle at the hash of its name. Each key is hashed onto the same circle and belongs to the **first node clockwise** from it. Adding node E puts E at one point on the circle, and only the keys between E and the node before it change owner, all of them moving to E. Every other key stays where it was. With five nodes, E takes about a fifth of the keys; the lab measures 1,864 of 10,000, and checks that every key that moved went to E.

One position per node leaves the arcs uneven: by chance one node might own a third of the circle. The fix is **virtual nodes**: each node is placed at many points, `cache-a#0`, `cache-a#1` and so on up to 100. Its share is then the sum of many small arcs, which averages out. In the lab, with one point each the busiest of four nodes gets 1.7 times its fair share of keys; with 100 points each it gets 1.14 times.

The same idea shows up whenever keys must be spread over machines that come and go: distributed caches, [[architecture/04-distributed-systems/13-partitioning|partitioned databases]] such as Cassandra and DynamoDB, and balancers that route each user to the server holding their warm cache.

## 8. Reverse proxies and API gateways

A **reverse proxy** sits in front of servers, receives clients' requests and forwards them; the client never talks to the backends directly. A layer 7 load balancer is a reverse proxy, and the term also covers a single proxy fronting one app. It's where you put concerns that don't belong in application code: TLS termination, compression, caching responses, limiting request rates, and routing. A *forward* proxy is the reverse: it fronts clients, not servers (see [[devops/08-networking-and-web/02-web-servers-and-proxies|proxies]]).

For [[architecture/03-architectural-patterns/04-microservices-patterns|microservices]], an **API gateway** is a reverse proxy that's the single entry point for all clients. It handles what every service would otherwise repeat: checking who the caller is, limiting request rates, routing to the right service, combining several service calls into one response, and translating between protocols. Clients then don't need to know how the services are laid out. The trap is putting business logic in the gateway. It then becomes a bottleneck that every team must change, a monolith in disguise, so keep it thin.

## 9. CDNs

A **CDN** is caching at the edge of the network for content that many users share: images, scripts, style sheets, video, and increasingly whole pages. Servers near the user hold copies, so a request from Lagos is answered in Lagos, not by your origin in Frankfurt. It cuts latency, because the content is physically closer, and takes enormous traffic off your servers. It's the first lever for any site that's read-heavy or has users far from its servers.

- **Pull CDN.** The CDN fetches from your origin on the first request and caches the response, using the `Cache-Control` rules from the [[architecture/02-building-blocks/02-caching/index|caching lesson]]. The first user in each region pays the full latency. It suits large catalogues where most items are rarely requested.
- **Push CDN.** You upload content to the CDN in advance. It suits a small set of files that rarely change, and nothing ever misses.

The caching lesson's problems apply in full: a CDN copy can be stale for its TTL, and purging it across hundreds of edge servers takes time. That's why static files are usually given a version in their name (`app.3f9c2a.js`) and cached for a year: a new version is a new name, so nothing ever needs purging.

## 10. Worked example: the shop on four servers

**Step 1: the front door.** A managed cloud layer 7 balancer, redundant by design, terminates TLS and forwards HTTP to four app servers. Before this works, the basket moves out of server memory into Redis (week 1, step 3), so any server can take any request.

**Step 2: the algorithm.** Product pages take about 10 ms. Search, which some customers use, takes about 200 ms. Request times vary, so round-robin would put fast page loads behind slow searches. Choose least-outstanding requests, which is one setting on most balancers. A larger second-generation server added later gets a weight of 2.

**Step 3: health checks and deploys.** `GET /health` every 2 seconds, fall 3, rise 2. It checks that the server can answer and that its connection pool is alive, not that the payment provider is up. A deploy drains one server at a time: no new requests, finish the ones in flight, restart, wait for two good checks, then move on. Customers see nothing.

**Step 4: the cache tier.** The product cache has grown to four Redis nodes. The app servers use a client library that places keys with consistent hashing, so when the sale needs a fifth node, about a fifth of keys miss once and move, instead of four-fifths. Add the node before the sale starts, not during it, so the misses land while traffic is low.

**Step 5: the edge.** Product images and the site's scripts go through a CDN with versioned file names. Most of the shop's bytes now never reach the balancer at all.

## 11. Runnable example: picking, checking, hashing

`balancer.ts` has the four picking algorithms, smooth weighted round-robin, the simulation behind section 4's table, the fall-and-rise health tracker, and a hash ring with virtual nodes, alongside the mod rule for comparison. `balancer.test.ts` checks every number in this lesson. The simulation reuses the seeded random number generator and percentile function from [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|week 1's lab]].

Smooth weighted round-robin is how Nginx spreads weighted turns. With weights a = 5, b = 1 and c = 1, a naive version sends a five requests in a row, then b, then c. The smooth version adds each server's weight to its running score, picks the highest, and takes the total weight (7) off the winner. Trace it:

```
pick   scores after adding weights   chosen   scores after paying 7
1        5   1   1                    a        -2   1   1
2        3   2   2                    a        -4   2   2
3        1   3   3                    b         1  -4   3
4        6  -3   4                    a        -1  -3   4
5        4  -2   5                    c         4  -2  -2
6        9  -1  -1                    a         2  -1  -1
7        7   0   0                    a         0   0   0   ← back to the start
```

a gets 5 of 7 turns, but never more than two in a row.

```ts
// balancer.ts — how a load balancer picks a server: the common algorithms, health checks that take a failing
// server out and put it back, and consistent hashing, which keeps a key on the same server as servers come and go.

import { mean, percentile, seeded } from "../../../../01-system-design-fundamentals/02-scalability-and-performance/labs/typescript/scaling.ts";

/** What a balancer can see when it picks: how many requests each server is still working on. */
export type Pick = (outstanding: readonly number[], random: () => number) => number;

/** Each server in turn, ignoring how busy they are. */
export function roundRobin(): Pick {
  let next = 0;
  return (outstanding) => next++ % outstanding.length;
}

/** The server with the fewest requests in progress (least connections). Ties go to the lowest number. */
export const leastOutstanding: Pick = (outstanding) => outstanding.indexOf(Math.min(...outstanding));

/** Any server, at random. */
export const random: Pick = (outstanding, rand) => Math.floor(rand() * outstanding.length);

/** Two servers at random, then the less busy of the two ("power of two choices"). */
export const twoChoices: Pick = (outstanding, rand) => {
  const a = Math.floor(rand() * outstanding.length);
  const b = Math.floor(rand() * outstanding.length);
  return outstanding[b] < outstanding[a] ? b : a;
};

/**
 * Sends random traffic through a balancer to `servers` servers, each working through its own queue one request at
 * a time. Most requests take 10 ms, but 1 in 20 takes 200 ms (a search, a report), which is what makes the
 * algorithms differ. `busy` is the utilisation of the whole pool. Returns latency (wait plus work) in ms.
 */
export function simulate(pick: Pick, servers: number, busy: number, requests: number, seed: number) {
  const rand = seeded(seed);
  const meanWorkMs = 0.95 * 10 + 0.05 * 200;
  const gapMs = meanWorkMs / (busy * servers); // average time between arrivals
  const finishes: number[][] = Array.from({ length: servers }, () => []); // per server: when each queued request ends
  let now = 0;
  const times: number[] = [];
  for (let i = 0; i < requests; i++) {
    now += -gapMs * Math.log(1 - rand());
    for (const queue of finishes) while (queue.length > 0 && queue[0] <= now) queue.shift(); // drop finished ones
    const s = pick(finishes.map((queue) => queue.length), rand);
    const workMs = rand() < 0.05 ? 200 : 10;
    const ends = Math.max(now, finishes[s].at(-1) ?? 0) + workMs; // starts when the server's queue ahead of it is done
    finishes[s].push(ends);
    times.push(ends - now);
  }
  return { mean: Math.round(mean(times)), p50: Math.round(percentile(times, 50)), p99: Math.round(percentile(times, 99)) };
}

/**
 * Weighted round-robin that spreads each server's turns out instead of bunching them (nginx's "smooth" method):
 * every pick, each server gains its weight; the highest is chosen and pays back the total.
 */
export function smoothWeighted(weights: Record<string, number>): () => string {
  const names = Object.keys(weights);
  const total = names.reduce((sum, n) => sum + weights[n], 0);
  const current = new Map(names.map((n) => [n, 0]));
  return () => {
    for (const n of names) current.set(n, current.get(n)! + weights[n]);
    const best = names.reduce((a, b) => (current.get(b)! > current.get(a)! ? b : a));
    current.set(best, current.get(best)! - total);
    return best;
  };
}

/**
 * Tracks one server's health checks. It takes `fall` failures in a row to mark a server down, so one slow
 * check doesn't remove it, and `rise` successes in a row to bring it back, so a flapping server stays out.
 */
export class Health {
  up = true;
  #fall: number;
  #rise: number;
  #streak = 0; // consecutive results that disagree with the current state

  constructor(fall = 3, rise = 2) {
    this.#fall = fall;
    this.#rise = rise;
  }

  record(ok: boolean): void {
    if (ok === this.up) {
      this.#streak = 0; // agrees with what we already believe
      return;
    }
    this.#streak++;
    if (this.#streak >= (this.up ? this.#fall : this.#rise)) {
      this.up = !this.up;
      this.#streak = 0;
    }
  }
}

/** Round-robin over the servers that are up. With none up, there is nowhere to send the request. */
export function pickHealthy(servers: readonly { name: string; health: Health }[], turn: number): string {
  const up = servers.filter((s) => s.health.up);
  if (up.length === 0) throw new Error("no healthy servers: answer 503");
  return up[turn % up.length].name;
}

/** FNV-1a: a small, fast, non-cryptographic hash from a string to a 32-bit number. */
export function hash(text: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) h = Math.imul(h ^ text.charCodeAt(i), 0x01000193) >>> 0;
  // FNV-1a mixes its last characters poorly, which matters for keys like "user:1", "user:2"; finish with a mix step.
  h = Math.imul(h ^ (h >>> 16), 0x85ebca6b) >>> 0;
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35) >>> 0;
  return (h ^ (h >>> 16)) >>> 0;
}

/** The naive way to spread keys: hash mod the number of servers. Changing the count moves almost every key. */
export function modulo(key: string, servers: readonly string[]): string {
  return servers[hash(key) % servers.length];
}

/**
 * Consistent hashing: servers and keys are placed on the same circle of hash values, and a key belongs to the
 * first server clockwise from it. Each server is placed `replicas` times (virtual nodes) to even out the arcs.
 * Adding a server takes keys only from its new neighbours.
 */
export class HashRing {
  #points: { at: number; server: string }[] = [];
  #replicas: number;

  constructor(servers: readonly string[], replicas = 100) {
    this.#replicas = replicas;
    for (const s of servers) this.add(s);
  }

  add(server: string): void {
    for (let r = 0; r < this.#replicas; r++) this.#points.push({ at: hash(`${server}#${r}`), server });
    this.#points.sort((a, b) => a.at - b.at);
  }

  remove(server: string): void {
    this.#points = this.#points.filter((p) => p.server !== server);
  }

  serverFor(key: string): string {
    if (this.#points.length === 0) throw new Error("the ring is empty");
    const h = hash(key);
    let lo = 0;
    let hi = this.#points.length; // binary search for the first point at or after h
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (this.#points[mid].at < h) lo = mid + 1;
      else hi = mid;
    }
    return this.#points[lo % this.#points.length].server; // past the last point, wrap round to the first
  }
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { HashRing, Health, leastOutstanding, modulo, pickHealthy, random, roundRobin, simulate, smoothWeighted, twoChoices } from "./balancer.ts";

test("round-robin takes turns; least-outstanding looks at the queues", () => {
  const pick = roundRobin();
  const queues = [5, 0, 0]; // server 0 is stuck on slow requests
  assert.deepEqual([1, 2, 3, 4, 5, 6].map(() => pick(queues, Math.random)), [0, 1, 2, 0, 1, 2]); // still gets its turn
  assert.equal(leastOutstanding(queues, Math.random), 1);
});

test("smooth weighted round-robin gives a bigger server more turns, spread out", () => {
  const pick = smoothWeighted({ a: 5, b: 1, c: 1 });
  assert.equal(Array.from({ length: 7 }, pick).join(""), "aabacaa"); // 5 of 7 to a, but never five in a row
});

test("when some requests are slow, the algorithms that look at the queues win, most of all in the tail", () => {
  // 4 servers, 80% busy, 100,000 requests: 95% take 10 ms and 5% take 200 ms. Latency in ms.
  const run = (pick: Parameters<typeof simulate>[0]) => simulate(pick, 4, 0.8, 100_000, 7);
  assert.deepEqual(run(roundRobin()), { mean: 214, p50: 138, p99: 1_158 }); // a fast request waits behind a slow one
  assert.deepEqual(run(random), { mean: 255, p50: 159, p99: 1_588 });
  assert.deepEqual(run(leastOutstanding), { mean: 68, p50: 17, p99: 466 }); // sees every queue
  assert.deepEqual(run(twoChoices), { mean: 96, p50: 25, p99: 495 }); // sees only two queues, and gets most of the gain
});

test("a server needs three failed checks to go down and two good ones to come back", () => {
  const health = new Health(3, 2);
  for (const ok of [false, false, true, false, false]) health.record(ok); // a success resets the count
  assert.equal(health.up, true);
  health.record(false);
  assert.equal(health.up, false); // three failures in a row
  health.record(true);
  assert.equal(health.up, false); // one success isn't enough
  health.record(true);
  assert.equal(health.up, true);
});

test("the balancer skips servers that are down, and has nothing to offer when all are", () => {
  const servers = ["app-1", "app-2", "app-3"].map((name) => ({ name, health: new Health(3, 2) }));
  for (let i = 0; i < 3; i++) servers[1].health.record(false);
  assert.deepEqual([0, 1, 2, 3].map((turn) => pickHealthy(servers, turn)), ["app-1", "app-3", "app-1", "app-3"]);
  for (const s of servers) for (let i = 0; i < 3; i++) s.health.record(false);
  assert.throws(() => pickHealthy(servers, 0), /no healthy servers/);
});

test("adding a fifth server: modulo hashing moves 4 keys in 5, a hash ring moves about 1 in 5", () => {
  const keys = Array.from({ length: 10_000 }, (_, i) => `user:${i}`);
  const four = ["cache-a", "cache-b", "cache-c", "cache-d"];
  const five = [...four, "cache-e"];
  const movedByModulo = keys.filter((k) => modulo(k, four) !== modulo(k, five)).length;
  assert.ok(Math.abs(movedByModulo - 8_000) < 200, `modulo moved ${movedByModulo}`);

  const ring = new HashRing(four, 100);
  const before = keys.map((k) => ring.serverFor(k));
  ring.add("cache-e");
  const after = keys.map((k) => ring.serverFor(k));
  const moved = keys.filter((_, i) => before[i] !== after[i]);
  assert.ok(Math.abs(moved.length - 2_000) < 300, `ring moved ${moved.length}`);
  assert.ok(moved.every((k) => ring.serverFor(k) === "cache-e")); // every key that moved went to the new server

  ring.remove("cache-e"); // and taking it out puts them back where they were
  assert.deepEqual(keys.map((k) => ring.serverFor(k)), before);
});

test("virtual nodes even out how many keys each server gets", () => {
  const keys = Array.from({ length: 10_000 }, (_, i) => `user:${i}`);
  const busiest = (replicas: number) => {
    const ring = new HashRing(["cache-a", "cache-b", "cache-c", "cache-d"], replicas);
    const counts = new Map<string, number>();
    for (const k of keys) counts.set(ring.serverFor(k), (counts.get(ring.serverFor(k)) ?? 0) + 1);
    return Math.max(...counts.values()) / (keys.length / 4); // 1.0 would be perfectly even
  };
  assert.ok(busiest(1) > 1.4, `one point each: busiest ${busiest(1)}`);
  assert.ok(busiest(100) < 1.2, `100 points each: busiest ${busiest(100)}`);
});
```

**Lab:** the code is in [`architecture/02-building-blocks/01-load-balancing-and-proxies/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/02-building-blocks/01-load-balancing-and-proxies/labs/typescript). From the vault root, `python3 labs/run.py load-balancing-and-proxies/typescript` runs the tests and checks this page still shows the same code. Inside the folder, `node --test` runs the tests alone. Expect seven passing tests in under a second.

## Common pitfalls

1. **A single load balancer.** It's now the single point of failure for everything behind it. Use a redundant pair or a managed balancer.
2. **Round-robin for requests of very different lengths.** Fast requests queue behind slow ones. Use least-outstanding or two choices.
3. **Sticky sessions instead of stateless servers.** Load spreads unevenly and a server's death logs its users out. Move the state to a shared store.
4. **A health check that tests a shared dependency.** When the database is slow, every server fails its check and the balancer removes the whole pool.
5. **A fall of 1.** One slow check removes a healthy server, and under load the remaining servers then get busier and slower, and fail too.
6. **Hashing keys mod N over cache nodes.** Adding or removing one node moves most keys and turns the cache cold. Use consistent hashing.
7. **Business logic in the API gateway.** It becomes a shared monolith that every team must change and every request waits on.

## Check your understanding

1. When is round-robin a perfectly good choice?
2. Why do two random choices get most of the benefit of checking every server, and why might they beat it with several balancers?
3. A layer 4 balancer is in front of servers that use one long-lived HTTP/2 connection per client. What goes wrong with the spread of load?
4. With fall 3, rise 2 and checks every 5 seconds, roughly how long can a crashed server keep receiving traffic?
5. Why should `/health` not fail when the database is down?
6. Six cache nodes, keys placed by hash mod 6. A seventh is added. Roughly what share of keys move? With a hash ring?
7. What problem do virtual nodes solve?

<details>
<summary>Answers — after your attempt</summary>

1. When requests cost about the same and the servers are the same size, so taking turns gives every server the same work.
2. The big losses come from sending a request to an already-long queue, and comparing two random servers almost always avoids the longest. With several balancers, all of them picking "the least busy" can send to the same server at once (herding); random pairs differ, so they don't.
3. A layer 4 balancer picks a backend once per connection. Every request on that connection goes to the same backend, so a few busy clients can overload one server while others idle. A layer 7 balancer would balance each request.
4. Up to about 15 seconds: three failed checks 5 seconds apart, depending on where in the cycle it crashed.
5. Every server shares the database, so they would all fail at once and the balancer would remove the whole pool. A database outage would become a total outage with no error pages. Handle a down database in the request path, with errors or degraded responses.
6. With mod: a key stays only if hash mod 6 equals hash mod 7, which happens for 6 in 42 values, so about 6 in 7 keys (86%) move. With a ring: about 1 in 7 (14%), all to the new node.
7. With one point per node, the arcs between points are uneven, so some nodes own far more of the circle, and get far more keys, than others. Many points per node average the arcs out.

</details>

## Practice — independent task

**Build a small layer 7 load balancer and break it on purpose.**

1. In a scratch folder, start three copies of a tiny Node HTTP server on ports 3001–3003. Each answers `GET /` with its own port number after a delay you choose, and `GET /health` with 200.
2. Write a balancer on port 3000, with `node:http` and no frameworks, that forwards each request to a backend picked by least-outstanding requests, and health-checks every backend each second with fall 3, rise 2.
3. Send steady load at it with `autocannon` or a loop of `curl`. Kill one backend, then restart it.
4. Make one backend slow (200 ms instead of 10 ms) and compare the latency of round-robin with least-outstanding.

**A smaller step first:** in the lab, change the simulation from 80% to 50% busy. Predict the order of the four algorithms by p99 before running it, then check against section 4.

**Done when:** you have the number of failed requests between killing a backend and its removal, and an explanation of that number from your fall and interval settings; the restarted backend is back in rotation after the expected two checks; and you have a p99 for round-robin and least-outstanding with one slow backend, with a sentence on why they differ.

<details>
<summary>Hints — after your attempt</summary>

- Forwarding: `http.request({ host: "localhost", port, path: req.url, method: req.method, headers: req.headers })`, then pipe the client's request into it and its response back to the client. Count a request as outstanding from when you send it until the backend's response ends or errors.
- Requests sent to a dead backend fail with `ECONNREFUSED`. You can count those as failed checks too (passive checking), which removes it faster than waiting for three scheduled checks.
- Failures between kill and removal should be roughly the request rate to that server times the time to three failed checks, so up to about 3 seconds' worth.

</details>

## Tradeoffs, limits and extensions

- **A balancer sees counts, not costs.** Least-outstanding treats a 10 ms and a 200 ms request alike. Balancers that track each server's recent latency, such as "peak EWMA" in some proxies, do better when servers slow down unevenly.
- **Consistent hashing can still overload one node with one hot key.** All of that key's traffic goes to one node, however even the ring is. Hot keys need replicating to several nodes, or a small in-process cache in front.
- **Global balancing** across regions is done with DNS that answers each user with their nearest healthy region, and with anycast, where many sites share one IP address and the network delivers to the nearest. [[networking/10-dns-in-depth|DNS in depth]] covers how.
- **Retries at the balancer** hide one failed backend, but multiply load when every backend is struggling. [[architecture/03-architectural-patterns/02-resilience-patterns/index|Resilience patterns]] covers retry budgets.

## Before moving on

You can choose a balancing algorithm for a workload and explain the simulation behind the choice, trace health checks through a failure and recovery, tell layer 4 from layer 7 and a reverse proxy from a gateway and a CDN, and explain why consistent hashing moves a fifth of keys where mod N moves four-fifths.

**Recap.** A load balancer receives every request at one address and passes it to a healthy backend, which is what makes adding servers useful; it must be redundant itself. Layer 4 routes connections; layer 7 reads each HTTP request and can route by path. Round-robin is fine for equal requests; when they vary, use least-outstanding or two random choices, which wins most of the gain without herding. Health checks use fall and rise thresholds, and must not depend on shared dependencies. Keep app servers stateless rather than sticky. Spread keys over cache nodes with consistent hashing and virtual nodes, so adding a node moves only its share. Reverse proxies centralise TLS and routing, API gateways front many services and should stay thin, and CDNs cache shared content near users.

**Next.** The week's optional lessons, [[architecture/01-system-design-fundamentals/03-availability-and-reliability|availability]] and [[architecture/01-system-design-fundamentals/04-cap-and-consistency|CAP and consistency]], put numbers on what health checks and redundancy buy. Then week 3, [[architecture/02-building-blocks/04-messaging-and-async|messaging]], moves slow work off the request path altogether.

## Related

- [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|Scalability and performance]]: why load balancing enables scale
- [[architecture/02-building-blocks/02-caching/index|Caching]]: CDNs are caching at the edge, and the cache tier is what consistent hashing spreads
- [[devops/08-networking-and-web/02-web-servers-and-proxies|Web servers and proxies (DevOps)]]: running Nginx and HAProxy in practice
- [[architecture/04-distributed-systems/13-partitioning|Partitioning]]: consistent hashing for databases
