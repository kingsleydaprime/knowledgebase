import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { chain, Db, encodeOrderSummary, execute, orderScreenRest, resolvers, RestApi, type Selection, varint } from "./communication.ts";

const shop = JSON.parse(readFileSync(new URL("../shared/shop.json", import.meta.url), "utf8"));

function db(): Db {
  const d = new Db();
  for (const c of shop.customers) d.customers.set(c.id, c);
  for (const p of shop.products) d.products.set(p.id, p);
  for (const o of shop.orders) d.orders.set(o.id, o);
  return d;
}

const ORDER_SCREEN: Selection = { id: true, totalPence: true, customer: { name: true }, items: { quantity: true, product: { name: true } } };

test("REST: five requests over two round trips, and most of the bytes go unused", () => {
  const api = new RestApi(db());
  const { screen, roundTrips } = orderScreenRest(api, "o1");
  assert.equal(screen.customer.name, "Gbenga Ali");
  assert.deepEqual(screen.items.map((i) => `${i.quantity} × ${i.product.name}`), ["1 × Kettle", "1 × Toaster", "2 × Mug set"]);
  assert.deepEqual({ requests: api.requests, roundTrips, bytes: api.bytes }, { requests: 5, roundTrips: 2, bytes: 912 });
  // The screen itself needs under a quarter of that: the descriptions, email and address were sent and thrown away.
  assert.equal(JSON.stringify(screen).length, 203);
});

test("a GraphQL-style query: the same screen in one request, with only the fields asked for", async () => {
  for (const batched of [false, true]) {
    const d = db();
    const [order] = d.findOrders(["o1"]);
    const screen = await execute(order, ORDER_SCREEN, resolvers(d, batched), "Order");
    assert.deepEqual(screen, orderScreenRest(new RestApi(db()), "o1").screen); // the same answer as REST
    assert.equal(JSON.stringify(screen).length, 203); // and nothing more is sent
    // The work moved to the server: an order, a customer and three products, or three queries with batching.
    assert.equal(d.queries, batched ? 3 : 5);
  }
});

test("the N+1 problem: a list of ten orders makes 41 queries one at a time, 3 when batched", async () => {
  for (const batched of [false, true]) {
    const d = db();
    const orders = d.findOrders(shop.orders.map((o: { id: string }) => o.id)); // 1 query for the list
    const page = await execute(orders, { id: true, customer: { name: true }, items: { product: { name: true } } }, resolvers(d, batched), "Order");
    assert.equal(page.length, 10);
    assert.equal(page[0].customer.name, "Gbenga Ali");
    assert.equal(d.queries, batched ? 3 : 1 + 10 + 30); // naive: + one per customer + one per item
  }
});

test("varints and tags, byte for byte as in the Protocol Buffers documentation", () => {
  assert.deepEqual(varint(1), [0x01]);
  assert.deepEqual(varint(150), [0x96, 0x01]);
  assert.deepEqual(varint(300), [0xac, 0x02]);
  assert.deepEqual(varint(2 ** 35), [0x80, 0x80, 0x80, 0x80, 0x80, 0x01]); // past 32 bits still works
  assert.throws(() => varint(-1), RangeError);
  const bytes = encodeOrderSummary({ id: 150, customer: "testing", totalPence: 1 });
  const hex = bytes.map((b) => b.toString(16).padStart(2, "0")).join(" ");
  assert.equal(hex, "08 96 01 12 07 74 65 73 74 69 6e 67 18 01");
});

test("the same order summary: 17 bytes as protobuf, 50 as JSON", () => {
  const summary = { id: 1, customer: "Gbenga Ali", totalPence: 8996 };
  assert.equal(encodeOrderSummary(summary).length, 17);
  assert.equal(JSON.stringify(summary).length, 50); // field names are sent with every message, and numbers as text
});

test("a synchronous chain: availabilities multiply and latencies add up", () => {
  const five = Array(5).fill({ availability: 0.999, ms: 20 });
  const c = chain(five);
  assert.equal((c.availability * 100).toFixed(2), "99.50"); // five 99.9% services: about 3.6 hours down a month
  assert.equal(c.sequentialMs, 100);
  assert.equal(chain([{ availability: 1, ms: 30 }, { availability: 1, ms: 50 }, { availability: 1, ms: 20 }]).parallelMs, 50);
});
