# DNS in Depth

**[Intermediate]** — The internet's naming system, and the single most common root cause of "the site is down". It's worth real study for one reason: **DNS is a globally distributed, eventually consistent, aggressively cached database that everything depends on and almost nobody monitors.** This lesson builds a DNS query byte by byte, runs a tiny DNS server that Node's own resolver queries, walks the resolution chain from the root, and puts numbers on caching: a migration done in the wrong order, a name that stays missing after you create it, and the four queries a Kubernetes pod sends for one lookup. The lab runs entirely on your machine.

## Before you start

You can already:

- Explain what an IP address and a port are, and that UDP sends single messages with no connection → [[networking/05-udp-and-ports|UDP and ports]].
- Explain what a cache and a TTL are, and why stale data is the price of caching → [[architecture/02-building-blocks/02-caching/index|caching]].
- Run a TypeScript test file with Node 26 (`node --test`).

After this lesson you will be able to:

1. Trace a lookup from your machine through a recursive resolver, the root, a top-level-domain server and the authoritative server, and say which steps a cache skips.
2. Read a DNS message: its header flags, question and answers, including a CNAME chain and a truncated reply.
3. Plan a DNS change around TTLs, including negative caching, so traffic moves when you expect.
4. Diagnose the classic DNS failures: stale records, NXDOMAIN after creation, search-list query storms, and DNS as a single point of failure.

**Study route:** sections 1–4 cover how a lookup works. Stop at the predictions in sections 3, 5 and 7 and try them before reading on. Section 9 is the lab. This week's "by Sunday" task, *what happens when I type google.com?*, starts here: write your answer before reading this lesson, and again after all three.

## The kid version first

You know your friend's *name* but not their *house number*, so you ask someone.

- You ask the local shopkeeper (your **resolver**). They've probably been asked before and remember (**cache**).
- If not, they ask the town hall: "who knows about Nigeria?" → "ask that office over there."
- That office: "who knows about `example.com`?" → "ask *their* office."
- That office, finally: "it's at 93.184.216.34."

Each office only knows **who to ask next**, not the answer, exactly like [[networking/04-routing|routing]]. And everyone writes the answer down for a while, so they don't have to ask again.

**Where the analogy stops working.** A shopkeeper would cross out an address they heard had changed. A DNS cache won't: it keeps serving what it wrote down until the time limit runs out, and nobody can tell it otherwise. That "writes it down for a while" is the source of nearly every DNS problem you'll ever have.

## 1. Why this exists

The shop is moving its servers to a new provider on Saturday. The plan: start the new servers, change the DNS record to point at them, switch off the old ones. On Saturday afternoon, half the customers still reach the old address, which is now switched off, and they will for up to a day. A colleague who checked the new subdomain on Friday, before it was created, still gets "no such site" on Monday. And the shop's own Kubernetes services make four DNS queries for every lookup of an external API. None of this is a bug in DNS; it's DNS doing exactly what it was designed to do. This lesson is about knowing what that is before Saturday.

## Terms used in this lesson

1. **DNS (Domain Name System)**: The letters stand for those words. It's the distributed system that turns names like `example.com` into IP addresses and other data.
2. **Record**: This is one piece of DNS data: a name, a type (such as `A` for an IPv4 address), a TTL, and a value.
3. **Zone**: This is the part of the name hierarchy one set of servers is responsible for, such as `example.com` and everything under it that isn't delegated elsewhere.
4. **Authoritative server**: This is a server that holds a zone's records and gives the real answers for it.
5. **Recursive resolver**: This is the server your machine asks, such as your ISP's, `8.8.8.8` or `1.1.1.1`. It does the whole lookup for you and caches the results.
6. **Delegation**: This is a zone saying "a sub-zone is handled by those servers", with `NS` records. The root delegates `com`; `com` delegates `example.com`.
7. **TTL (time to live)**: The letters stand for those words. It's how many seconds a resolver may cache a record before asking again.
8. **NXDOMAIN**: This is the answer "this name doesn't exist". It's cached too, for the zone's **negative TTL**.
9. **CNAME**: This is a record saying "this name is an alias: look up that other name instead".
10. **Stub resolver**: This is the small resolver built into your operating system, which forwards questions to a recursive resolver.
11. **Search list**: This is a list of domains a stub resolver appends to short names before trying them, set in `/etc/resolv.conf`, with `ndots` deciding when.
12. **Anycast**: This is announcing the same IP address from many places, so each packet reaches the nearest one.

## 2. The resolution walk

```
browser → stub resolver (OS) → recursive resolver (ISP / 8.8.8.8 / 1.1.1.1)
                                    │
                                    ├─► root server (.)          "ask the .com servers"
                                    ├─► TLD server (.com)        "ask ns1.example.com"
                                    └─► authoritative server     "93.184.216.34"  ← the real answer

                                 caches it for TTL seconds, returns it to you
```

Two words to keep straight, because interviewers love this one:

- **Recursive**: "go and find the answer for me, I'll wait." That's what your machine asks its resolver.
- **Iterative**: "tell me what you know, I'll follow up." That's what the resolver does with each server in the chain. Root and TLD servers only answer iteratively; if they did recursion for everyone, they'd melt.

**Root servers** are the 13 *named* root servers, `a.root-servers.net` to `m.root-servers.net`, a limit set by what fitted in a 512-byte UDP packet, not by the number of machines. There are well over 1,000 physical instances, reachable because each name is announced by **[[networking/04-routing|anycast]]** from many locations. Your query goes to the nearest.

## 3. What the cache saves

A resolver caches not only answers but delegations: "the `.com` servers are these", "`example.com`'s servers are those".

**Predict before reading on.** A resolver with an empty cache looks up `www.example.com`, then `www.example.com` again, then `api.example.com`, then `www.shop.com`. How many queries does each lookup send?

<details>
<summary>After your prediction</summary>

**3, 0, 1, 2.** The first walks root → `.com` → `example.com`'s server. The second is answered from the cache. The third skips straight to `example.com`'s server, because that delegation is cached. The fourth skips the root, because the `.com` delegation is cached, and asks `.com` → `shop.com`. That's why a busy resolver almost never talks to the root: the `.com` delegation's TTL is two days. The lab's `IterativeResolver` counts exactly these.

</details>

## 4. A DNS message, byte by byte

Every DNS message, question or answer, has the same shape:

1. A **12-byte header**: a 16-bit ID, which the reply copies so the asker can match them up; flags; and four counts (questions, answers, authority records, additional records).
2. **The question**: a name, a type, and a class (`IN`, for internet).
3. **Answers**, each a name, type, class, TTL and value.

A name isn't sent as text with dots. It's a list of **labels**, each preceded by its length, ending with a zero byte. `www.example.com` is:

```
03 77 77 77 07 65 78 61 6d 70 6c 65 03 63 6f 6d 00
 3  w  w  w  7  e  x  a  m  p  l  e  3  c  o  m  0
```

To save space, a name in a reply can be a **pointer**: two bytes starting with the bits `11`, meaning "the rest of this name is at that offset in the message". The flags hold, among others, `QR` (this is a reply), `AA` (authoritative answer), `TC` (truncated), `RD` (recursion desired) and the **response code**: 0 for success, 3 for NXDOMAIN.

The lab builds queries this way, sends them over UDP to its own tiny authoritative server, and parses the replies. Asking for `www.example.com` returns two answers: a `CNAME` to `example.com` with a TTL of 3,600, and `example.com`'s `A` record with a TTL of 300. Node's own resolver, pointed at the same server, gets the same answer.

## 5. Record types worth knowing

| Record | Maps | Notes |
|---|---|---|
| **A / AAAA** | name → IPv4 / IPv6 address | the basic lookup |
| **CNAME** | name → another name | **can't coexist with other records at the same name**, which is why you can't put a `CNAME` on a bare domain (`example.com` must have `SOA` and `NS` records). Hence providers' `ALIAS`, `ANAME` and "CNAME flattening" |
| **NS** | zone → its authoritative servers | delegation: how the hierarchy is built |
| **MX** | domain → mail servers | with priority values |
| **TXT** | arbitrary text | SPF, DKIM, DMARC, and domain-ownership checks |
| **SRV** | service → host and port | service discovery; how [[devops/05-orchestration/index\|Kubernetes]] DNS exposes ports |
| **PTR** | IP → name | reverse lookups; mail servers check these |
| **CAA** | domain → which certificate authorities may issue for it | a real, cheap security control: set it |
| **SOA** | zone metadata | serial, refresh, and the **negative-caching TTL** |

## 6. TTL and caching: where the pain lives

Every record carries a **TTL**. Resolvers cache it for that long and won't ask again, whatever you do. **You can't revoke a DNS answer.** Once it's out, it's out until the TTL expires.

**Predict before reading on.** The shop's record has a TTL of 86,400 seconds (a day). A customer's resolver looks it up one minute before the move. The record is changed to the new address at the moment of the move. How long does that customer keep reaching the old server? And if the TTL had been lowered to 60 a day earlier?

<details>
<summary>After your prediction</summary>

With a day's TTL: **86,340 seconds**, nearly 24 hours, because the cached answer is valid until a day after it was fetched, whatever changed since. With the TTL lowered to 60 a day ahead (long enough for the *old* day-long TTL to run out everywhere): **0 seconds**, because no cached copy lasts past the move by more than a minute, and this one had already expired. The lab's `CachingResolver` replays both, minute by minute.

</details>

The operational discipline that follows:

- **Lower the TTL *before* a migration, not during.** Drop it to 60 a day or two ahead, migrate, then raise it again. Doing this in the wrong order is how "we changed DNS and half the traffic still went to the dead server for a day" happens.
- **Negative caching is real.** An NXDOMAIN is cached too, for the time set in the zone's `SOA` record. Create a record *after* someone has looked it up and failed, and they'll keep failing for a while. In the lab, a name looked up once before it existed stays missing for the full hour of the negative TTL. This is the classic "it works for me but not for my colleague" right after setting something up.
- **Nothing respects TTLs perfectly.** Browsers cache separately from the operating system, which caches separately from the resolver, and some resolvers clamp TTLs to their own minimums. Plan for "roughly", never "exactly".

## 7. Transport: UDP first

DNS uses **UDP port 53**, falling back to TCP when the response is too big: 512 bytes classically, or up to about 4,096 when both sides support **EDNS0**. A reply that didn't fit sets the `TC` bit, telling the client to ask again over TCP. In the lab, a name with 40 addresses (about 1 KB of answers) comes back with `TC` set and no answers.

Two consequences: **zone transfers** (`AXFR`) always use TCP, and firewalls that block TCP port 53 "because DNS is UDP" break DNSSEC and large responses in ways that are maddening to diagnose. And the amplification property (a small query, a big answer, no handshake to stop source spoofing) makes open resolvers a favourite [[cybersecurity/06-attacks-and-threats/index|DDoS amplifier]].

**Predict before reading on.** A pod in Kubernetes has `ndots:5` and the search list `default.svc.cluster.local svc.cluster.local cluster.local`. Code in it looks up `api.example.com`. How many queries does the stub resolver send before it gets the real answer? What about `api.example.com.`, with a trailing dot?

<details>
<summary>After your prediction</summary>

**Four**: `api.example.com` has 2 dots, fewer than 5, so each search domain is tried first (`api.example.com.default.svc.cluster.local`, and so on), each failing with NXDOMAIN, before the name itself. Often twice over, for `A` and `AAAA`. With a trailing dot, the name is taken as complete: **one** query. Combined with a race in older kernels' connection tracking, this produced Kubernetes' famous intermittent 5-second DNS timeouts. The fixes: `ndots:2`, fully qualified names with a trailing dot, or NodeLocal DNSCache. The lab's `searchCandidates` lists the queries.

</details>

## 8. Security, and why DNS causes so many outages

DNS was designed in 1983 with **no authentication whatsoever**. A resolver believes whatever answer arrives with a matching query ID and port:

- **Cache poisoning** races the real answer with a forged one. The **Kaminsky attack** (2008) made this dramatically practical, and the emergency mitigation was **source-port randomisation**, adding about 16 bits an attacker must guess. That's a mitigation, not a fix.
- **DNSSEC** is the real fix: records are signed, with a chain of trust from the root down. It authenticates *origin and integrity*; it **doesn't** encrypt anything. Adoption is partial, largely because it's operationally unforgiving: a botched key rollover takes your domain off the internet.
- **DNS over HTTPS and DNS over TLS** solve the *other* half: privacy from the network. Your ISP can no longer see or tamper with your lookups. They don't authenticate the answer: a lying resolver still lies, now privately. DNS over HTTPS is also contentious, because it moves resolution from your ISP to a few large providers and bypasses the network filtering that companies and parental controls relied on.

**These are orthogonal:** DNSSEC answers "is this answer genuine?", and DNS over HTTPS or TLS answers "who can see me asking?" You want both, and confusing them is a common interview stumble.

DNS causes outages because it's a dependency of *everything*, is cached invisibly, and fails in ways that don't look like DNS failures:

- **It's first in the request path.** A slow resolver adds latency to every new connection, including your service's own calls to databases and APIs.
- **Load balancing through DNS is coarse.** Round-robin `A` records are cached at every layer, so traffic spreads unevenly and removing a failed host takes a full TTL. That's fine for rough geographic steering and bad for failover, which is why real load balancing happens at [[architecture/02-building-blocks/01-load-balancing-and-proxies/index|layer 4 or 7]], with DNS only pointing at the load balancer.
- **It's a single point of failure you don't own.** The 2016 Dyn DDoS took down Twitter, GitHub, Netflix and Reddit at once, none of which was attacked itself. Use two DNS providers if uptime genuinely matters.

## 9. The lab: DNS on your own machine

`dns.ts` builds and parses DNS messages, runs a tiny authoritative server over UDP on 127.0.0.1, models the iterative walk with delegation caching, models a caching resolver with a clock, and lists search-list candidates. `dns.test.ts` checks every number in this lesson, including a lookup through Node's built-in resolver, pointed at the lab's server.

```ts
// dns.ts — DNS on the wire, and the behaviour of the resolvers that cache it: building and reading DNS packets by
// hand, a tiny authoritative server over UDP, the iterative walk from the root, TTL and negative caching through a
// migration, and the query count a Kubernetes-style search list adds.
import dgram from "node:dgram";

export const TYPE = { A: 1, NS: 2, CNAME: 5, SOA: 6, TXT: 16 } as const;

/** A name on the wire is a list of labels, each prefixed by its length, ending with a zero: 3www7example3com0. */
export function encodeName(name: string): Buffer {
  const parts = name.replace(/\.$/, "").split(".").filter(Boolean);
  const bytes: number[] = [];
  for (const label of parts) {
    if (label.length > 63) throw new RangeError(`label too long: ${label}`);
    bytes.push(label.length, ...Buffer.from(label, "ascii"));
  }
  bytes.push(0);
  return Buffer.from(bytes);
}

/** A query: a 12-byte header (ID, flags, four counts), then one question (name, type, class IN = 1). */
export function buildQuery(id: number, name: string, type: number): Buffer {
  const header = Buffer.alloc(12);
  header.writeUInt16BE(id, 0);
  header.writeUInt16BE(0x0100, 2); // flags: RD, "recursion desired"
  header.writeUInt16BE(1, 4); // one question
  const tail = Buffer.alloc(4);
  tail.writeUInt16BE(type, 0);
  tail.writeUInt16BE(1, 2); // class IN
  return Buffer.concat([header, encodeName(name), tail]);
}

/** Reads a name, following compression pointers: two bytes starting 11 mean "the rest is at this offset". */
function readName(buf: Buffer, offset: number): [string, number] {
  const labels: string[] = [];
  let end = -1; // where the name ends in the place we started reading, once we've followed a pointer
  for (let jumps = 0; ; ) {
    const length = buf[offset];
    if (length === 0) {
      return [labels.join("."), end === -1 ? offset + 1 : end];
    }
    if ((length & 0xc0) === 0xc0) {
      if (end === -1) end = offset + 2;
      offset = buf.readUInt16BE(offset) & 0x3fff;
      if (++jumps > 20) throw new Error("compression loop");
      continue;
    }
    labels.push(buf.toString("ascii", offset + 1, offset + 1 + length));
    offset += 1 + length;
  }
}

export interface Answer {
  name: string;
  type: number;
  ttl: number;
  data: string;
}

export interface Message {
  id: number;
  truncated: boolean;
  authoritative: boolean;
  rcode: number; // 0 = no error, 3 = NXDOMAIN (the name doesn't exist)
  question: { name: string; type: number };
  answers: Answer[];
}

export function parseMessage(buf: Buffer): Message {
  const flags = buf.readUInt16BE(2);
  const [qname, afterName] = readName(buf, 12);
  const message: Message = {
    id: buf.readUInt16BE(0),
    truncated: (flags & 0x0200) !== 0,
    authoritative: (flags & 0x0400) !== 0,
    rcode: flags & 0x000f,
    question: { name: qname, type: buf.readUInt16BE(afterName) },
    answers: [],
  };
  let offset = afterName + 4;
  for (let i = 0; i < buf.readUInt16BE(6); i++) {
    const [name, next] = readName(buf, offset);
    const type = buf.readUInt16BE(next);
    const ttl = buf.readUInt32BE(next + 4);
    const length = buf.readUInt16BE(next + 8);
    const rdata = next + 10;
    const data = type === TYPE.A ? [...buf.subarray(rdata, rdata + 4)].join(".") : type === TYPE.CNAME ? readName(buf, rdata)[0] : buf.toString("hex", rdata, rdata + length);
    message.answers.push({ name, type, ttl, data });
    offset = rdata + length;
  }
  return message;
}

export interface ZoneRecord {
  type: number;
  ttl: number;
  data: string; // an IPv4 address for A, a name for CNAME
}

/**
 * A tiny authoritative server on 127.0.0.1 over UDP. It answers from `zone`, follows one CNAME, says NXDOMAIN for
 * unknown names, and sets the TC ("truncated") bit when the answer won't fit in 512 bytes, as classic DNS over UDP must.
 */
export async function startServer(zone: Map<string, ZoneRecord[]>): Promise<{ port: number; queries: number; close: () => void }> {
  const socket = dgram.createSocket("udp4");
  const state = { port: 0, queries: 0, close: () => socket.close() };
  socket.on("message", (query, peer) => {
    state.queries++;
    const { id, question } = parseMessage(query);
    const records: { name: string; record: ZoneRecord }[] = [];
    let name = question.name.toLowerCase();
    for (const r of zone.get(name) ?? []) {
      records.push({ name, record: r });
      if (r.type === TYPE.CNAME && question.type !== TYPE.CNAME) {
        name = r.data;
        for (const target of zone.get(name) ?? []) records.push({ name, record: target });
      }
    }
    const wanted = records.filter((r) => r.record.type === question.type || r.record.type === TYPE.CNAME);
    const body = wanted.map(({ name: n, record }) => {
      const rdata = record.type === TYPE.A ? Buffer.from(record.data.split(".").map(Number)) : encodeName(record.data);
      const fixed = Buffer.alloc(10);
      fixed.writeUInt16BE(record.type, 0);
      fixed.writeUInt16BE(1, 2);
      fixed.writeUInt32BE(record.ttl, 4);
      fixed.writeUInt16BE(rdata.length, 8);
      return Buffer.concat([encodeName(n), fixed, rdata]);
    });
    const questionBytes = query.subarray(12);
    let answerBytes = Buffer.concat(body);
    const truncated = 12 + questionBytes.length + answerBytes.length > 512;
    if (truncated) answerBytes = Buffer.alloc(0); // a truncated UDP reply carries no answers: "ask again over TCP"
    const header = Buffer.alloc(12);
    header.writeUInt16BE(id, 0);
    header.writeUInt16BE(0x8400 | (truncated ? 0x0200 : 0) | (zone.has(question.name.toLowerCase()) ? 0 : 3), 2); // QR, AA, TC, RCODE
    header.writeUInt16BE(1, 4);
    header.writeUInt16BE(truncated ? 0 : body.length, 6);
    socket.send(Buffer.concat([header, questionBytes, answerBytes]), peer.port, peer.address);
  });
  await new Promise<void>((resolve) => socket.bind(0, "127.0.0.1", resolve));
  state.port = socket.address().port;
  return state;
}

/** Sends one query over UDP and waits for the answer. */
export function ask(port: number, query: Buffer): Promise<Message> {
  const socket = dgram.createSocket("udp4");
  return new Promise((resolve, reject) => {
    socket.on("message", (reply) => {
      socket.close();
      resolve(parseMessage(reply));
    });
    socket.on("error", reject);
    socket.send(query, port, "127.0.0.1");
  });
}

/**
 * The iterative walk, against in-memory servers. Each server knows either the answer, or which server to ask next
 * (a delegation). The resolver caches both answers and delegations, so later lookups skip steps.
 */
export class IterativeResolver {
  queries = 0;
  #servers: Map<string, Map<string, string>>; // server → (name or zone → answer, or "→next-server")
  #cache = new Map<string, string>(); // name or zone → answer or delegation

  constructor(servers: Map<string, Map<string, string>>) {
    this.#servers = servers;
  }

  resolve(name: string): string {
    if (this.#cache.has(name)) return this.#cache.get(name)!; // answered from cache: no queries at all
    let server = "root";
    for (const zone of zonesAbove(name)) {
      const delegation = this.#cache.get(zone); // the closest cached delegation saves the walk above it
      if (delegation) server = delegation;
    }
    for (;;) {
      this.queries++;
      const knows = this.#servers.get(server)!;
      const exact = knows.get(name);
      if (exact) {
        this.#cache.set(name, exact);
        return exact;
      }
      const zone = zonesAbove(name).find((z) => knows.has(z))!; // the most specific zone this server delegates
      server = knows.get(zone)!.slice(1);
      this.#cache.set(zone, server);
    }
  }
}

/** "www.example.com" → ["com", "example.com"]: the zones above a name, from the top down. */
function zonesAbove(name: string): string[] {
  const labels = name.split(".");
  return labels.slice(1).map((_, i) => labels.slice(labels.length - 1 - i).join(".")).filter((z) => z !== name);
}

/** A caching stub resolver with a clock: answers live for their TTL, "no such name" for the negative TTL. */
export class CachingResolver {
  upstreamQueries = 0;
  #now: () => number;
  #upstream: (name: string) => { address?: string; ttl: number };
  #cache = new Map<string, { address?: string; expires: number }>();

  constructor(now: () => number, upstream: (name: string) => { address?: string; ttl: number }) {
    this.#now = now;
    this.#upstream = upstream;
  }

  lookup(name: string): string | undefined {
    const hit = this.#cache.get(name);
    if (hit && hit.expires > this.#now()) return hit.address; // fresh: the cached answer wins, right or wrong
    this.upstreamQueries++;
    const { address, ttl } = this.#upstream(name);
    this.#cache.set(name, { address, expires: this.#now() + ttl * 1000 });
    return address;
  }
}

/**
 * The names a resolver tries for `name` with a search list, the way /etc/resolv.conf's `ndots` works: a name with
 * fewer dots than `ndots` is tried with each search domain appended first. A trailing dot means "exactly this name".
 */
export function searchCandidates(name: string, ndots: number, search: string[]): string[] {
  if (name.endsWith(".")) return [name.slice(0, -1)];
  const dots = name.split(".").length - 1;
  const expanded = search.map((domain) => `${name}.${domain}`);
  return dots >= ndots ? [name, ...expanded] : [...expanded, name];
}
```

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { Resolver } from "node:dns/promises";
import { ask, buildQuery, CachingResolver, encodeName, IterativeResolver, parseMessage, searchCandidates, startServer, TYPE } from "./dns.ts";

const ZONE = new Map([
  ["example.com", [{ type: TYPE.A, ttl: 300, data: "93.184.216.34" }]],
  ["www.example.com", [{ type: TYPE.CNAME, ttl: 3600, data: "example.com" }]],
  ["big.example.com", Array.from({ length: 40 }, (_, i) => ({ type: TYPE.A, ttl: 60, data: `10.0.0.${i + 1}` }))],
]);

test("a name on the wire is length-prefixed labels, and a query is 12 bytes of header plus the question", () => {
  assert.equal(encodeName("www.example.com").toString("hex"), "03777777076578616d706c6503636f6d00");
  const query = buildQuery(0xbeef, "example.com", TYPE.A);
  assert.equal(query.length, 12 + 13 + 4); // header, name (7example3com0), type and class
  assert.deepEqual(parseMessage(query).question, { name: "example.com", type: TYPE.A });
});

test("our server answers our hand-built query, following the CNAME", async () => {
  const server = await startServer(ZONE);
  try {
    const reply = await ask(server.port, buildQuery(42, "www.example.com", TYPE.A));
    assert.equal(reply.id, 42); // the reply carries the query's ID: how a resolver matches them up
    assert.equal(reply.authoritative, true);
    assert.deepEqual(reply.answers, [
      { name: "www.example.com", type: TYPE.CNAME, ttl: 3600, data: "example.com" },
      { name: "example.com", type: TYPE.A, ttl: 300, data: "93.184.216.34" },
    ]);
    const missing = await ask(server.port, buildQuery(43, "nope.example.com", TYPE.A));
    assert.equal(missing.rcode, 3); // NXDOMAIN
  } finally {
    server.close();
  }
});

test("Node's own resolver, pointed at our server, gets the same answer", async () => {
  const server = await startServer(ZONE);
  try {
    const resolver = new Resolver();
    resolver.setServers([`127.0.0.1:${server.port}`]);
    assert.deepEqual(await resolver.resolve4("example.com", { ttl: true }), [{ address: "93.184.216.34", ttl: 300 }]);
    await assert.rejects(resolver.resolve4("nope.example.com"), { code: "ENOTFOUND" });
  } finally {
    server.close();
  }
});

test("an answer too big for 512 bytes of UDP comes back truncated: retry over TCP", async () => {
  const server = await startServer(ZONE);
  try {
    const reply = await ask(server.port, buildQuery(7, "big.example.com", TYPE.A)); // 40 A records: about 1 KB
    assert.equal(reply.truncated, true);
    assert.equal(reply.answers.length, 0);
  } finally {
    server.close();
  }
});

test("the iterative walk: three queries the first time, fewer once delegations are cached", () => {
  const servers = new Map([
    ["root", new Map([["com", "→tld-com"], ["org", "→tld-org"]])],
    ["tld-com", new Map([["example.com", "→ns1.example.com"], ["shop.com", "→ns.shop.com"]])],
    ["ns1.example.com", new Map([["www.example.com", "93.184.216.34"], ["api.example.com", "93.184.216.35"]])],
    ["ns.shop.com", new Map([["www.shop.com", "198.51.100.7"]])],
  ]);
  const resolver = new IterativeResolver(servers);
  const counts = [];
  for (const name of ["www.example.com", "www.example.com", "api.example.com", "www.shop.com"]) {
    const before = resolver.queries;
    resolver.resolve(name);
    counts.push(resolver.queries - before);
  }
  // root → .com → example.com; then the cache; then straight to example.com's server; then .com → shop.com
  assert.deepEqual(counts, [3, 0, 1, 2]);
});

test("a migration: lower the TTL a day ahead, or wait out the old one", () => {
  for (const [oldTtl, staleSeconds] of [[86_400, 86_340], [60, 0]] as const) {
    let now = 0; // milliseconds
    let address = "198.51.100.1"; // the old server
    let ttl = oldTtl;
    const resolver = new CachingResolver(() => now, () => ({ address, ttl }));
    assert.equal(resolver.lookup("shop.example"), "198.51.100.1"); // a client looks it up just before the move
    now = 60_000;
    address = "203.0.113.9"; // the move, a minute later
    ttl = 60;
    let stale = 0;
    for (let t = 60; t < 86_400 + 60; t += 60) {
      now = t * 1000;
      if (resolver.lookup("shop.example") === "198.51.100.1") stale += 60;
    }
    assert.equal(stale, staleSeconds, `old TTL ${oldTtl}`); // a day of the dead server, or none
  }
});

test("negative caching: a name created after a failed lookup stays missing for the negative TTL", () => {
  let now = 0;
  let exists = false;
  const resolver = new CachingResolver(() => now, () => (exists ? { address: "203.0.113.9", ttl: 300 } : { ttl: 3600 }));
  assert.equal(resolver.lookup("new.example"), undefined); // NXDOMAIN, cached for the SOA's negative TTL: an hour
  exists = true; // the record is created a moment later...
  now = 1_000;
  assert.equal(resolver.lookup("new.example"), undefined); // ...but this client keeps getting "no such name"
  now = 3_600_000;
  assert.equal(resolver.lookup("new.example"), "203.0.113.9");
  assert.equal(resolver.upstreamQueries, 2);
});

test("ndots:5 turns one lookup into four queries; a trailing dot makes it one", () => {
  const search = ["default.svc.cluster.local", "svc.cluster.local", "cluster.local"];
  const candidates = searchCandidates("api.example.com", 5, search); // 2 dots, fewer than 5
  assert.deepEqual(candidates, [
    "api.example.com.default.svc.cluster.local", // three NXDOMAINs first...
    "api.example.com.svc.cluster.local",
    "api.example.com.cluster.local",
    "api.example.com", // ...then the real name
  ]);
  assert.equal(searchCandidates("api.example.com", 2, search)[0], "api.example.com"); // ndots:2: the real name first
  assert.deepEqual(searchCandidates("api.example.com.", 5, search), ["api.example.com"]);
});
```

**Lab:** the code is in [`networking/10-dns-in-depth/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/networking/10-dns-in-depth/labs/typescript). From the vault root, `python3 labs/run.py dns-in-depth/typescript` runs the tests and checks this page still shows the same code. Inside the folder, `node --test` runs them alone. Expect eight passing tests in well under a second. Nothing leaves your machine.

## Common pitfalls

1. **Changing a record without lowering its TTL first.** Clients keep the old answer for the old TTL.
2. **Testing a new name before creating it.** You've cached its NXDOMAIN for the negative TTL.
3. **Using DNS round-robin as failover.** Removing a dead host takes a whole TTL, and caches spread load unevenly.
4. **Blocking TCP port 53.** Large answers and DNSSEC need it.
5. **Short names in containers with a high `ndots`.** Every external lookup becomes several failed queries first.
6. **Confusing DNSSEC with DNS over HTTPS.** One proves the answer is genuine; the other hides the question.
7. **One DNS provider for a service that must stay up.**

## Check your understanding

1. What's the difference between the recursive query your laptop sends and the iterative queries its resolver sends?
2. A resolver has just looked up `www.example.com`. Which servers does it ask for `mail.example.com`, and why not the root?
3. A record's TTL is 3,600. You change its value at noon. When can you be sure every well-behaved resolver sees the new value?
4. You create `beta.shop.example` at 10:00. A colleague says it doesn't exist; they'd tried it at 9:55. Why, and how long until it works for them?
5. Why can't you put a `CNAME` on `example.com` itself?
6. A DNS reply has the `TC` bit set and no answers. What should the client do?

<details>
<summary>Answers — after your attempt</summary>

1. Recursive: "give me the final answer", and the resolver does all the work. Iterative: each server answers with what it knows, either the answer or "ask those servers instead", and the resolver follows up itself.
2. Only `example.com`'s authoritative servers. The resolver cached the delegation for `example.com` (and for `com`) during the first lookup, so it starts as far down the tree as its cache allows.
3. At 13:00, an hour after the change: a resolver that fetched the old value just before noon may keep it for the full 3,600 seconds. (In practice, plan for some caches to ignore TTLs and take longer.)
4. Their resolver cached the NXDOMAIN at 9:55, for the zone's negative TTL from its `SOA` record. It will keep saying "doesn't exist" until that runs out, perhaps an hour, regardless of the record now existing.
5. A `CNAME` can't share a name with any other record, and a zone's top name must have `SOA` and `NS` records. Providers offer `ALIAS`, `ANAME` or "CNAME flattening", which they resolve themselves and serve as plain `A` records.
6. Ask again over TCP, which has no size limit, and use that answer.

</details>

## Practice — independent task

**Watch real DNS with `dig`.**

1. Run `dig +trace example.com` and identify the root, TLD and authoritative steps, and which server answered each.
2. Run `dig example.com` twice, a few seconds apart, against `1.1.1.1` (`dig @1.1.1.1 example.com`), and explain why the TTL in the answer went down.
3. Find a domain's negative TTL: `dig nonexistent-name-$RANDOM.example.com` and read the `SOA` record in the authority section.
4. Run `dig +short TXT` and `dig +short CAA` for two domains you use, and say what each record is for.

**A smaller step first:** in the lab, add an `AAAA` record for `example.com` and a query for it, predicting the bytes of the question before running it.

**Done when:** you have the `+trace` output annotated with the three steps, the decreasing TTL explained in one sentence, a negative TTL found, and the purpose of every `TXT` and `CAA` record you found.

## Tradeoffs, limits and extensions

- **The lab's server is authoritative only.** It doesn't recurse, cache, or answer over TCP. Real resolvers (Unbound, BIND, CoreDNS) do all three.
- **TTLs are a staleness bound, not a schedule.** Some resolvers and clients ignore or clamp them; measure with `dig` against several public resolvers after a change.
- **DNS-based service discovery** (Consul, Kubernetes) uses short TTLs and its own resolvers, accepting more queries for faster change.

## Before moving on

You can trace a lookup and say which steps the cache skips, read a DNS message, plan a change around TTLs and negative caching, and recognise the classic DNS failures.

**Recap.** DNS resolves names by walking delegations from the root: your stub asks a recursive resolver, which asks root, TLD and authoritative servers iteratively and caches both answers and delegations. Messages are a 12-byte header, a question and answers, with names as length-prefixed labels. Every answer, and every NXDOMAIN, is cached for its TTL and can't be recalled, so lower TTLs well before a change. UDP comes first, with TCP for anything truncated. Search lists multiply queries. DNSSEC authenticates answers, DNS over HTTPS or TLS hides questions, and DNS is a dependency of everything: monitor it, and don't depend on one provider.

**Next.** [[networking/11-http-evolution/index|HTTP and its evolution]]: what travels over the connection once the name is resolved.

## Related

- [[networking/04-routing|Routing]]: anycast, which DNS depends on
- [[networking/15-network-performance|Network performance]]: DNS as the first round trip
- [[cybersecurity/03-network-security/index|Network security]]: poisoning, DNSSEC, exfiltration over DNS
- [[devops/08-networking-and-web/01-networking-and-protocols|Networking and protocols (DevOps)]]: the operator's DNS record cheat sheet
