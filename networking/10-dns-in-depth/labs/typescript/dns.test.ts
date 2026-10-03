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
