# Monolith / Microservices / Serverless

> **[Intermediate]** · From the roadmap.sh system-design roadmap. The biggest structural decision in a system's architecture, and the one most often made for the wrong reasons. This lesson puts numbers on the trade-offs: how coordination grows with the number of people, how often a shared release breaks, what moving a module behind the network costs in latency and availability, when paying per request beats paying for a server, and how often a serverless function starts cold. It also builds the checker that keeps a modular monolith modular. The worked example follows the shop from four developers to six teams. The lab checks every number.

## Before you start

You can already:

- Explain what a synchronous chain does to availability and latency, and when to use a message instead → [[architecture/02-building-blocks/05-communication/index|communication]] and [[architecture/02-building-blocks/04-messaging-and-async/index|messaging and async]].
- Explain why a system is only as fast as its bottleneck → [[architecture/01-system-design-fundamentals/02-scalability-and-performance/index|scalability and performance]].
- Organise code into modules by feature → [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|modular monolith to services]] (helpful, not required).
- Run a TypeScript test file with Node 26 (`node --test`).

After this lesson you will be able to:

1. Say what problem microservices solve and what they cost, and state when you would *not* use them, as "I'd choose X because Y".
2. Work out what extracting a module costs in added latency and lost availability, and why the shape of its interface matters more than its size.
3. Work out when serverless is cheaper than a server, and how often a function will start cold at a given traffic level.
4. Check a modular monolith's boundaries automatically: no reaching inside another module, no cycles.

**Study route:** sections 1–4 cover monoliths and microservices. Stop at the predictions in sections 2, 4 and 6 and try them before reading on. Section 9 is the worked example and section 10 the lab. This week's closed-book question is *when would you not use microservices?* Answer it from memory before reading section 5.

## The kid version

A family kitchen has one cook who makes everything. It's fast and simple, until twenty people need feeding and the cooks keep bumping into each other. A food court gives every dish its own stall, own cook and own till, so the pizza stall can be busy while the curry stall is quiet, and a broken oven only closes one stall. But a meal needing three stalls means queueing at three tills, and someone has to run the whole food court. A pop-up chef who's only paid while cooking is cheap when you eat out once a month and expensive when you eat out every day, and they take a while to arrive when nobody's called them recently.

**Where the analogy stops working.** Walking between food stalls is easy. In software, every trip between services crosses a network that can be slow or broken, and the stalls must keep agreeing about the menu. Most of the cost of microservices is in those trips and agreements, not in the stalls themselves.

## 1. Why this exists

The shop has four developers and one codebase. Someone reads that large tech companies run hundreds of microservices, and proposes splitting the shop into twelve. Across town, a company with sixty engineers in eight teams has the opposite problem: one codebase, one weekly release, and every week someone's change breaks someone else's feature, so the whole release waits. Both are asking "should we use microservices?", and the right answers are opposite. This lesson is about telling which situation you're in, and putting numbers on it.

## Terms used in this lesson

1. **Monolith**: This is one application, built and deployed as one unit, containing all of a system's features.
2. **Module**: This is a part of a codebase that owns one area of the business, such as billing, and hides its inner workings behind a public interface.
3. **Modular monolith**: This is a monolith divided into modules with enforced boundaries: one deployment, but parts that could be separated later.
4. **Microservice**: This is a small application that owns one business capability and its own data, is deployed on its own, and talks to other services over the network.
5. **Independent deployment**: This means one team can release its service without waiting for, or coordinating with, other teams.
6. **Database per service**: This is the rule that each microservice owns its data and no other service reads its tables directly.
7. **Distributed monolith**: This is a system split into services that still have to be changed and deployed together: the costs of microservices without the benefits.
8. **Blast radius**: This is how much of a system one failure takes down.
9. **Conway's law**: This is the observation that a system's structure ends up mirroring the communication structure of the organisation that builds it.
10. **Serverless**: This is also called **FaaS (functions as a service)**. It's running code as functions that a platform starts on demand, scales automatically and bills per request and per running time, with no servers for you to manage.
11. **Cold start**: This is the delay when a serverless platform has to start a new instance of a function, because no warm one is available.
12. **Strangler fig**: This is a way to replace a system gradually: route one piece of functionality at a time to a new implementation, until the old system can be removed.

## 2. The monolith, and what really hurts

One codebase, one process, one deployment. Despite its reputation, it's usually the right place to start:

- **Simple to build, test and debug.** A call between features is a function call: nanoseconds, typed, and it can't partly fail. A stack trace shows the whole story.
- **Transactions just work.** Saving an order and reducing stock is one database transaction.
- **One thing to deploy and monitor.**

The costs arrive with size, and mostly with *people*. Two numbers explain them.

**Coordination.** In words: the number of pairs of people who might need to talk grows with the square of the team, not in step with it. With $n$ people:

$$\text{links} = \frac{n(n - 1)}{2}$$

Four people have 6 links; eight have 28; fifty have 1,225. In one shared codebase, many of those links become "who changed this?" and "can I merge yet?".

**Shared releases.** In words: if every change has a small, independent chance of breaking something, the chance that a release containing many changes has at least one bad one grows quickly with the number of changes.

$$P(\text{release breaks}) = 1 - (1 - p)^{\text{changes}}$$

**Predict before reading on.** Eight teams put 40 changes a week into one release, and each change has a 1% chance of breaking something. How often is the release held up? How often would one team's own five changes be?

<details>
<summary>After your prediction</summary>

**33.1%**: one release in three. One team's five changes alone break **4.9%** of the time. Every team waits for the slowest, buggiest change in the release, and the more teams there are, the more often someone does. That waiting, not traffic, is the pain microservices relieve. The lab checks both numbers.

</details>

A monolith can also grow into a "big ball of mud", where every part calls every other part's internals. Then nothing can change without breaking something else, and nothing can ever be separated. The next section is about preventing that.

## 3. The modular monolith

Keep one deployment, but divide the code into modules by business capability (orders, billing, catalogue, customers), each with a **public interface** and private insides. That gives most of the *organisational* benefit of microservices, with teams owning modules and clear contracts between them, without any of the network. It's the underrated middle ground.

Boundaries rot unless a machine checks them. Two rules matter:

1. **No reaching inside.** `orders` may import `catalog`, the public face, but not `catalog/internal/prices`. If it does, catalogue can't change its internals without breaking orders.
2. **No cycles.** If orders uses billing, billing uses customers, and customers uses orders, none of the three can be understood, tested or extracted alone.

The lab's `boundaryViolations` and `findCycle` check both. In the shop's modules, `orders → catalog/internal/prices` is flagged. When `customers` starts importing `orders`, the cycle `orders → billing → customers → orders` is found. Run checks like these in CI; in a real TypeScript project, dependency-cruiser or ESLint boundary rules do it, and Java has ArchUnit. A module that passes both rules is one you *could* extract, which keeps that option cheap.

## 4. Microservices, and the network tax

Each service owns one capability and its own data, is deployed on its own, and talks to others with [[architecture/02-building-blocks/05-communication/index|REST or gRPC]] or [[architecture/02-building-blocks/04-messaging-and-async/index|events]]. What you buy:

- **Independent deployment.** A team releases when its own changes are ready: back to the 4.9%, not the 33%.
- **Independent scaling.** Scale the search service for a sale without scaling everything.
- **Fault isolation.** A crash in recommendations doesn't take checkout down, if checkout doesn't wait on it.
- **Freedom of technology**, per service.

What you pay is **distributed-systems complexity**:

- Calls can be slow or fail, so you need timeouts, retries and [[architecture/03-architectural-patterns/02-resilience-patterns/index|resilience patterns]].
- There are no transactions across services, so you need [[architecture/03-architectural-patterns/05-transactional-outbox/index|the outbox]] and [[architecture/03-architectural-patterns/03-data-and-integration-patterns|sagas]], and you get [[architecture/01-system-design-fundamentals/04-cap-and-consistency|eventual consistency]].
- A request crosses many services, so you need distributed tracing ([[devops/10-observability/index|observability]]).
- Something has to run it all: [[devops/05-orchestration/index|orchestration]], [[architecture/03-architectural-patterns/04-microservices-patterns|service discovery and gateways]].

The network tax depends on the interface. In words: every in-process call that becomes a network call adds its round-trip time to the request, and adds one more chance for the request to fail, so availabilities multiply.

**Predict before reading on.** Checkout calls the pricing module 40 times per request, once per line and discount rule. Pricing is extracted into a service: each call takes 1 ms and succeeds 99.99% of the time. What does that add to checkout's latency, and what's the chance a checkout gets all its prices?

<details>
<summary>After your prediction</summary>

**40 ms** more, and $0.9999^{40}$ = **99.60%** of checkouts get every price: forty chances to fail, where in-process there were none. A **coarse** interface, one "price this basket" call, adds 1 ms and keeps 99.99%. The lesson: **extract along boundaries where the conversation is short.** A chatty module behind a network becomes slow and fragile. If extracted services must call each other synchronously for every request and must be deployed together, you've built a **distributed monolith**: microservices' costs with a monolith's coupling. That's the most common way microservices go wrong.

</details>

## 5. When to use them, and when not

**Microservices solve an organisational problem, not a traffic problem.** The pain they relieve is many teams blocked on each other in one codebase and one release. A monolith can handle enormous traffic: scale it out behind a [[architecture/02-building-blocks/01-load-balancing-and-proxies/index|load balancer]], add [[architecture/02-building-blocks/02-caching/index|caches]] and read replicas.

By **Conway's law**, a system ends up shaped like the teams that build it, so draw service boundaries along team boundaries, and expect a service shared by several teams to cause the same coordination pain as a monolith.

**I wouldn't use microservices when:**

- the team is small (one or two teams), because nobody is blocked on anyone, and the network tax buys nothing;
- the product is new and the boundaries are still moving, because moving a boundary between modules is a refactor, while moving one between services is a migration;
- there's no platform to run them (deployment pipelines, tracing, on-call for many services);
- the parts need strong consistency with each other, such as an order and its payment, because splitting them means sagas and eventual consistency.

The widely endorsed path: **start with a modular monolith and keep its boundaries clean. Extract a service when you feel a specific pain:** a module that needs to scale on its own, a team that needs to release on its own, or a part with different reliability or security needs. Extract it with the [[architecture/03-architectural-patterns/03-data-and-integration-patterns|strangler fig]] pattern, one route at a time.

## 6. Serverless

Deploy functions; the platform starts instances when requests arrive, scales them, stops them when idle, and bills per request plus per **gigabyte-second** (memory × running time). [[devops/03-cloud/02-serverless|Serverless in depth]] covers the platforms.

In words: serverless cost grows in step with use, while a server costs the same whether it's busy or idle. So serverless is cheaper below some request rate and dearer above it. With a price per million requests and per gigabyte-second:

$$\text{monthly cost} = \frac{\text{requests}}{10^6} \times \text{price per million} + \text{requests} \times \text{seconds each} \times \text{GB} \times \text{price per GB-second}$$

**Predict before reading on.** The shop renders invoices in 200 ms with 512 MB. With prices close to AWS Lambda's list ($0.20 per million requests, $0.0000166667 per gigabyte-second), what do a million invoices a month cost? Roughly how many a month before a $30 server is cheaper?

<details>
<summary>After your prediction</summary>

A million invoices cost **$1.87**: $0.20 for the requests and $1.67 for the running time. Break-even with a $30 server is about **16 million a month**, roughly 6 a second all day and night. Fifty million cost $93.33, three times the server. Serverless wins for spiky and modest workloads, and loses for steady heavy ones. These prices are illustrative; check the provider's page before relying on them.

</details>

**Cold starts.** After a request, an instance stays warm for a while, and the platform decides how long. A request that arrives after it has gone cold waits for a new one to start: tens of milliseconds for a small function, seconds for a large runtime. In words: with requests arriving at random, the chance the gap before a request is longer than the warm window falls exponentially with the traffic. With $\lambda$ requests a minute and a warm window of $W$ minutes:

$$P(\text{cold}) = e^{-\lambda W}$$

With a 5-minute window: at 10 requests a minute, cold starts are effectively 0%; at 1 a minute, 0.67%; at 1 every 10 minutes, **60.65%**. The lab's simulation agrees within half a percentage point. Cold starts hurt **quiet** functions most, and 0.67% is enough to show up in p99. The fixes are keeping instances warm (paid provisioned concurrency), smaller deployments, faster runtimes, or not putting a quiet function on a latency-critical path.

Other limits: a maximum run time (15 minutes on Lambda), no state kept between requests, harder local testing, and tight coupling to one provider's events and services. Serverless is great for event-driven glue, spiky work and scheduled jobs. It's poor for latency-critical, steady, heavy services.

## 7. Choosing

| Situation | Reach for |
|---|---|
| New product, one or two teams, boundaries still moving | **Modular monolith** |
| Many teams blocked on each other; parts with clearly different scaling or reliability needs | **Microservices**, extracted one at a time |
| Spiky, event-driven or scheduled work; little steady load | **Serverless** |

The mature answer is usually **a mix**: a core modular monolith, a few services extracted where they've earned it, and functions for event glue, chosen per part from the [[architecture/01-system-design-fundamentals/01-how-to-approach-system-design/index|requirements]], not from fashion.

## 8. A note on migrating

The strangler fig works like this: put a proxy or gateway in front of the monolith, build the new service, route one path (`/search`) to it, watch it, and repeat until the monolith's version can be deleted. The monolith keeps working the whole time, and each step can be rolled back by changing the route. The hard part is data: the new service needs its own copy of the data it owns, kept in step during the move, usually with events from the [[architecture/03-architectural-patterns/05-transactional-outbox/index|outbox]] or with change data capture.

## 9. Worked example: the shop from four developers to six teams

**Stage 1: four developers.** A modular monolith with five modules: orders, billing, catalogue, customers, search. `boundaryViolations` and `findCycle` run in CI, so a pull request that reaches into another module's internals, or creates a cycle, fails. That's 6 coordination links, and one release a day with a handful of changes. Microservices would add a network, a platform and eventual consistency, and fix no problem they have.

**Stage 2: invoices become a function.** The invoice consumer from [[architecture/02-building-blocks/04-messaging-and-async/index|messaging]] runs as a serverless function triggered by the queue. A million invoices a month cost about $1.87 against $30 for a server that idles most of the day. The spike during a sale scales out automatically. Cold starts don't matter, because no customer waits on an invoice.

**Stage 3: forty engineers in six teams.** A shared weekly release with about 30 changes breaks $1 - 0.99^{30}$ ≈ 26% of the time, and the search team, whose service needs ten times the servers during a sale, is blocked by everyone. Search is extracted first: it has its own team, its own scaling profile, and a short conversation with the rest ("search these words, return product IDs"). It's moved with a strangler fig: the gateway sends `/search` to the new service, which builds its own index from catalogue events.

**What stays.** Pricing stays in the monolith. Checkout calls it 40 times per request, and extracting it would add 40 ms and cut availability to 99.60%. If it's ever extracted, it will be behind a coarse "price this basket" call. Orders and billing stay together, because an order and its payment need one transaction.

## 10. Runnable example: the arithmetic of architecture

`architecture.ts` has the coordination and release formulas, the cost of extracting a module, serverless cost and break-even, cold-start chances with a seeded simulation, and the modular-monolith boundary checker. `architecture.test.ts` checks every number in this lesson.

```ts
// architecture.ts — the arithmetic behind choosing a monolith, microservices or serverless: how coordination grows
// with people, how often a shared release breaks, what moving a module behind the network costs, when paying per
// request beats paying for a server, how often a function starts cold, and a checker that keeps a modular
// monolith's boundaries honest. Every function is a model; each says what it assumes.

/** Pairs of people who may need to talk: n(n − 1)/2. It grows with the square of the team, not in step with it. */
export function coordinationLinks(people: number): number {
  return (people * (people - 1)) / 2;
}

/** The chance a release containing `changes` independent changes, each bad with probability p, has at least one bad one. */
export function releaseBreaks(changes: number, p: number): number {
  return 1 - (1 - p) ** changes;
}

/**
 * Moving a module behind the network: every in-process call becomes a network call, which adds time and can
 * fail. Returns the time added to a request and the chance all of its calls succeed.
 */
export function extract(callsPerRequest: number, networkMs: number, callAvailability: number) {
  return { addedMs: callsPerRequest * networkMs, availability: callAvailability ** callsPerRequest };
}

export interface Pricing {
  perMillionRequests: number; // dollars
  perGbSecond: number; // dollars for one second of one gigabyte of memory
}

/** A function platform charges per request plus per gigabyte-second of running time. */
export function serverlessMonthly(requests: number, ms: number, memoryGb: number, price: Pricing): number {
  return (requests / 1e6) * price.perMillionRequests + requests * (ms / 1000) * memoryGb * price.perGbSecond;
}

/** The monthly request count at which paying per request costs the same as a server that's always on. */
export function breakEvenRequests(serverMonthly: number, ms: number, memoryGb: number, price: Pricing): number {
  return serverMonthly / (price.perMillionRequests / 1e6 + (ms / 1000) * memoryGb * price.perGbSecond);
}

/**
 * One function instance stays warm for `warmMinutes` after each request. With requests arriving at random at
 * `perMinute`, a request finds it cold when the gap before it is longer than that: probability e^(−rate × window).
 */
export function coldShare(perMinute: number, warmMinutes: number): number {
  return Math.exp(-perMinute * warmMinutes);
}

/** The same, request by request, with a seeded generator (mulberry32, as in week 1's lab). */
export function simulateColdShare(perMinute: number, warmMinutes: number, requests: number, seed: number): number {
  let a = seed >>> 0;
  const random = () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  let cold = 0;
  for (let i = 0; i < requests; i++) {
    const gapMinutes = -Math.log(1 - random()) / perMinute;
    if (gapMinutes > warmMinutes) cold++;
  }
  return cold / requests;
}

/** A module of a modular monolith, and what it imports: "billing" is billing's public face; "billing/x" is inside it. */
export interface Module {
  name: string;
  imports: string[];
}

/** Imports that reach inside another module instead of going through its public face. */
export function boundaryViolations(modules: readonly Module[]): string[] {
  const names = new Set(modules.map((m) => m.name));
  const violations: string[] = [];
  for (const m of modules) {
    for (const imp of m.imports) {
      const [target, ...inside] = imp.split("/");
      if (target !== m.name && names.has(target) && inside.length > 0) violations.push(`${m.name} → ${imp}`);
    }
  }
  return violations;
}

/** A cycle in the modules' dependencies, as a path that starts and ends at the same module, or undefined if none. */
export function findCycle(modules: readonly Module[]): string[] | undefined {
  const deps = new Map(modules.map((m) => [m.name, [...new Set(m.imports.map((i) => i.split("/")[0]))].filter((d) => d !== m.name)]));
  const state = new Map<string, "visiting" | "done">();
  const path: string[] = [];
  const visit = (name: string): string[] | undefined => {
    if (state.get(name) === "done") return undefined;
    if (state.get(name) === "visiting") return [...path.slice(path.indexOf(name)), name]; // back to a module on the path
    state.set(name, "visiting");
    path.push(name);
    for (const d of deps.get(name) ?? []) {
      const cycle = visit(d);
      if (cycle) return cycle;
    }
    path.pop();
    state.set(name, "done");
    return undefined;
  };
  for (const m of modules) {
    const cycle = visit(m.name);
    if (cycle) return cycle;
  }
  return undefined;
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { boundaryViolations, breakEvenRequests, coldShare, coordinationLinks, extract, findCycle, releaseBreaks, serverlessMonthly, simulateColdShare } from "./architecture.ts";

test("coordination grows with the square of the people", () => {
  assert.deepEqual([4, 8, 50].map(coordinationLinks), [6, 28, 1_225]);
});

test("a shared release breaks far more often than one team's", () => {
  // Eight teams put 40 changes a week into one monolith release; each change has a 1% chance of breaking something.
  assert.equal((releaseBreaks(40, 0.01) * 100).toFixed(1), "33.1"); // one release in three is held up
  assert.equal((releaseBreaks(5, 0.01) * 100).toFixed(1), "4.9"); // one team's own five changes
});

test("a chatty module gets slow and fragile behind the network; a coarse interface doesn't", () => {
  // Checkout asks pricing 40 times per request. In process, that's nanoseconds and can't fail on its own.
  const chatty = extract(40, 1, 0.9999);
  assert.equal(chatty.addedMs, 40);
  assert.equal((chatty.availability * 100).toFixed(2), "99.60"); // forty chances to fail
  const coarse = extract(1, 1, 0.9999); // one call that prices the whole basket
  assert.deepEqual({ ms: coarse.addedMs, pct: (coarse.availability * 100).toFixed(2) }, { ms: 1, pct: "99.99" });
});

test("pay per request until the traffic is steady, then a server is cheaper", () => {
  const price = { perMillionRequests: 0.2, perGbSecond: 0.0000166667 }; // illustrative, close to AWS Lambda's list price
  // Invoice rendering: 200 ms at 512 MB.
  assert.equal(serverlessMonthly(1_000_000, 200, 0.5, price).toFixed(2), "1.87"); // a million invoices: under $2
  assert.equal(serverlessMonthly(50_000_000, 200, 0.5, price).toFixed(2), "93.33"); // fifty million: three times a $30 server
  const breakEven = breakEvenRequests(30, 200, 0.5, price);
  assert.equal(Math.round(breakEven / 1e5) / 10, 16.1); // about 16 million a month: 6 a second, around the clock
});

test("cold starts hit quiet functions hardest", () => {
  // An instance stays warm for 5 minutes after a request.
  assert.deepEqual([10, 1, 0.1].map((perMinute) => (coldShare(perMinute, 5) * 100).toFixed(2)), ["0.00", "0.67", "60.65"]);
  for (const perMinute of [1, 0.1]) {
    const simulated = simulateColdShare(perMinute, 5, 100_000, 7);
    assert.ok(Math.abs(simulated - coldShare(perMinute, 5)) < 0.005, `${perMinute}/min: ${simulated}`);
  }
});

test("a modular monolith's boundaries: no reaching inside, no cycles", () => {
  const shop = [
    { name: "orders", imports: ["billing", "catalog/internal/prices"] }, // reaches inside catalog
    { name: "billing", imports: ["customers"] },
    { name: "catalog", imports: ["catalog/internal/prices"] }, // inside itself: fine
    { name: "customers", imports: [] },
  ];
  assert.deepEqual(boundaryViolations(shop), ["orders → catalog/internal/prices"]);
  assert.equal(findCycle(shop), undefined);
  shop[3].imports.push("orders"); // customers now needs orders: orders → billing → customers → orders
  assert.deepEqual(findCycle(shop), ["orders", "billing", "customers", "orders"]);
});
```

**Lab:** the code is in [`architecture/03-architectural-patterns/01-monolith-microservices-serverless/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/architecture/03-architectural-patterns/01-monolith-microservices-serverless/labs/typescript). From the vault root, `python3 labs/run.py monolith-microservices-serverless/typescript` runs the tests and checks this page still shows the same code. Inside the folder, `node --test` runs the tests alone. Expect six passing tests in well under a second.

## Common pitfalls

1. **Microservices for traffic.** Scale a monolith out first; split for teams, not for load.
2. **Microservices for a new product.** Boundaries move while you learn the domain, and moving them between services is a migration.
3. **Chatty services.** Many calls per request multiply latency and failure. Extract where the conversation is short, or design a coarse interface.
4. **Shared databases between services.** Two services reading the same tables must change together: a distributed monolith.
5. **A modular monolith with no enforced boundaries.** Without a check in CI, the modules blur within months.
6. **Serverless for steady heavy load.** Above break-even, it's several times the cost of a server.
7. **Serverless on a quiet, latency-critical path.** Most requests may hit a cold start.

## Check your understanding

1. What problem do microservices actually solve? Why isn't high traffic, on its own, a reason to adopt them?
2. Twelve teams put 60 changes a week into one release, each 1% likely to break something. Roughly how often does the release break?
3. A module is called 10 times per request. Extracted, each call takes 2 ms and succeeds 99.95% of the time. What's added, and what's the request's chance of getting all its answers?
4. When does a system of services become a distributed monolith?
5. A function gets 2 requests a minute and stays warm for 5 minutes. What share of requests are cold? And at 1 request an hour?
6. Give two reasons, in "I'd choose X because Y" form, not to use microservices for a new product with one team.

<details>
<summary>Answers — after your attempt</summary>

1. Many teams blocking each other in one codebase and one release: coordination and shared releases. Traffic can be handled by scaling a monolith out with load balancers, caches and replicas; splitting it adds network latency and failure without adding capacity a monolith couldn't have.
2. $1 - 0.99^{60}$ ≈ 45%: almost every other release.
3. 20 ms added, and $0.9995^{10}$ ≈ 99.50%.
4. When its services can't be changed or deployed independently, because they share a database, call each other synchronously for every request, or must be released together.
5. $e^{-2 \times 5} = e^{-10}$ ≈ 0.005%, effectively never. At 1 an hour (1/60 a minute), $e^{-5/60}$ ≈ 92%: almost every request is cold.
6. For example: "I'd choose a modular monolith because one team isn't blocked by anyone, so independent deployment buys nothing and the network adds latency and failure." And: "I'd choose a monolith because the boundaries will move while we learn the domain, and moving a module is a refactor while moving a service is a migration."

</details>

## Practice — independent task

**Check your own project's module boundaries.**

1. Pick your flagship or any project with a `src/` folder divided by feature. List each top-level module and, from its imports, the modules it depends on. A one-line `grep -rho "from '\.\./[a-z-]*" src/<module>` per module gets you most of the way.
2. Feed that list to `boundaryViolations` and `findCycle`.
3. Add a third rule: an `allowed` map saying which modules each may depend on, such as `orders: ["billing", "catalog"]`, and report any dependency outside it. Test it with the shop example.

**A smaller step first:** in the lab, add an import from `catalog` to `orders` and predict what `findCycle` returns before running it.

**Done when:** you have your project's dependency list with every violation and cycle named, your `allowed` rule passes its tests, and one sentence names the module you would extract first and why, or why none.

## Tradeoffs, limits and extensions

- **The release formula assumes independent changes**, each with the same chance of breaking something. Real changes interact, and good tests lower $p$. The shape (more changes in one release, more breakage) holds.
- **Microservices aren't the only way to deploy independently.** Feature flags, trunk-based development and a fast pipeline let many teams share a monolith well.
- **Serverless prices and limits change**, and vary by provider and region. Recompute break-even with current prices and your real duration and memory.
- **Platform cost is real.** Each service needs a pipeline, monitoring, alerts and someone on call. With 20 services and 4 engineers, the platform is the job.

## Before moving on

You can explain what microservices solve and cost, say when you wouldn't use them, work out the network tax of extracting a module, compute serverless break-even and cold-start chances, and keep a modular monolith's boundaries enforced.

**Recap.** Start with a modular monolith: one deployment, modules with public interfaces, and a CI check against reaching inside or cycles. Its real limits are organisational: coordination grows with the square of the people, and a release with many changes breaks often (40 changes at 1% each: 33%). Microservices fix that with independent deployment and scaling, at the price of a network that adds latency and failure to every call: 40 chatty calls cost 40 ms and drop availability to 99.60%. So extract along short conversations, one at a time, with a strangler fig. Serverless costs in step with use: cheap below break-even (about 16 million invoices a month against a $30 server), dear above it, and cold for quiet functions.

**Next.** [[architecture/03-architectural-patterns/05-transactional-outbox/index|Transactional outbox]], this week's other core lesson: how a service saves its data and publishes an event without losing either. Then week 5, databases.

## Related

- [[architecture/03-architectural-patterns/04-microservices-patterns|Microservices patterns]]: the machinery microservices require
- [[architecture/03-architectural-patterns/03-data-and-integration-patterns|Data and integration patterns]]: strangler fig and saga
- [[backend/03-structuring-a-backend/05-modular-monolith-to-services/index|Modular monolith to services]]: the same question at the code level
- [[devops/05-orchestration/index|Orchestration (DevOps)]]: what microservices run on
- [[devops/03-cloud/02-serverless|Serverless (DevOps)]]: the platforms
