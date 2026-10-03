import { test } from "node:test";
import assert from "node:assert/strict";
import { BoundedQueue, Broker, idempotent, levelLoad, partitionFor, PartitionedLog } from "./broker.ts";

function broker(clock = { now: 0 }) {
  return new Broker({ now: () => clock.now, visibilityMs: 30_000, maxAttempts: 3 });
}

test("a queue gives each message to one consumer; a topic copies it to every subscription", () => {
  const b = broker();
  b.subscribe("orders", "invoices");
  b.subscribe("orders", "analytics");
  b.publish("orders", "order 1");
  b.publish("orders", "order 2");
  // Two invoice workers share the invoices subscription: they split the messages.
  assert.equal(b.receive("invoices")?.body, "order 1");
  assert.equal(b.receive("invoices")?.body, "order 2");
  assert.equal(b.receive("invoices"), undefined); // both are taken, though not yet acknowledged
  // Analytics has its own copy of everything.
  assert.deepEqual([b.receive("analytics")?.body, b.receive("analytics")?.body], ["order 1", "order 2"]);
  // A topic with no subscribers keeps nothing.
  b.publish("refunds", "refund 1");
  assert.equal(b.depth("invoices") + b.depth("analytics"), 4);
});

test("a message that isn't acknowledged comes back, and after three tries goes to the dead-letter queue", () => {
  const clock = { now: 0 };
  const b = broker(clock);
  b.subscribe("orders", "invoices");
  b.publish("orders", "order 1");
  const first = b.receive("invoices")!;
  assert.equal(first.attempt, 1);
  assert.equal(b.receive("invoices"), undefined); // hidden while a consumer works on it
  clock.now = 30_000; // no ack in time: the consumer is presumed dead
  assert.equal(b.receive("invoices")?.attempt, 2);
  clock.now = 60_000;
  assert.equal(b.receive("invoices")?.attempt, 3);
  clock.now = 90_000;
  assert.equal(b.receive("invoices"), undefined); // three tries are enough
  assert.deepEqual(b.deadLetters("invoices"), ["order 1"]);
  assert.equal(b.depth("invoices"), 0);
});

test("at least once means sometimes twice: a crash before the ack charges twice, unless the handler is idempotent", () => {
  for (const safe of [false, true]) {
    const clock = { now: 0 };
    const b = broker(clock);
    b.subscribe("orders", "payments");
    b.publish("orders", "charge £40 for order 1");
    let charges = 0;
    const charge = () => void charges++;
    const handle = safe ? idempotent(charge, new Set()) : (d: { body: string }) => charge();
    handle(b.receive("payments")!); // charged, then the consumer crashes before acknowledging
    clock.now = 30_000;
    const again = b.receive("payments")!; // so the broker delivers it again
    handle(again);
    b.ack("payments", again.id);
    assert.equal(charges, safe ? 1 : 2);
  }
});

test("a queue absorbs a sale spike that a synchronous service would turn away", () => {
  // 10 seconds at 300 orders a second, then 50 seconds at 20. Two workers at 50 a second each.
  const spike = [...Array(10).fill(300), ...Array(50).fill(20)];
  const two = levelLoad(spike, 100);
  assert.deepEqual(two.sync, { served: 2_000, rejected: 2_000 }); // half the spike gets errors
  assert.deepEqual(two.queued, { peakDepth: 2_000, clearedAfterSeconds: 35, maxWaitSeconds: 20 });
  // Nobody is turned away. The backlog is gone 35 seconds in, but the last spike orders waited 20 seconds.
  const four = levelLoad(spike, 200); // competing consumers: twice the workers
  assert.deepEqual(four.queued, { peakDepth: 1_000, clearedAfterSeconds: 16, maxWaitSeconds: 5 });
});

test("redelivery reorders one key's events; a partition keeps them in order, and a new group replays them", () => {
  const clock = { now: 0 };
  const b = broker(clock);
  b.subscribe("orders", "shipping");
  for (const e of ["created", "paid", "shipped"]) b.publish("orders", `order 7 ${e}`, "order-7");
  const seen: string[] = [];
  const created = b.receive("shipping")!;
  seen.push(created.body);
  b.ack("shipping", created.id);
  b.receive("shipping"); // "paid": the handler fails, so it isn't acknowledged
  const shipped = b.receive("shipping")!; // meanwhile the next message is free to go
  seen.push(shipped.body);
  b.ack("shipping", shipped.id);
  clock.now = 30_000;
  const paid = b.receive("shipping")!;
  seen.push(paid.body);
  assert.deepEqual(seen, ["order 7 created", "order 7 shipped", "order 7 paid"]); // shipped before paid

  const log = new PartitionedLog(4);
  for (const e of ["created", "paid", "shipped"]) log.append("order-7", `order 7 ${e}`);
  const p = partitionFor("order-7", 4);
  const inOrder: string[] = [];
  let failedOnce = false;
  for (let m = log.poll("shipping", p); m !== undefined; m = log.poll("shipping", p)) {
    if (m.endsWith("paid") && !failedOnce) {
      failedOnce = true; // fails once: no commit, so the partition waits and the same message comes back
      continue;
    }
    inOrder.push(m);
    log.commit("shipping", p);
  }
  assert.deepEqual(inOrder, ["order 7 created", "order 7 paid", "order 7 shipped"]);
  assert.equal(log.poll("analytics", p), "order 7 created"); // a group that has never read starts at the beginning
});

test("a key always lands in the same partition", () => {
  assert.equal(partitionFor("order-7", 4), partitionFor("order-7", 4));
  const counts = [0, 0, 0, 0];
  for (let i = 0; i < 10_000; i++) counts[partitionFor(`order-${i}`, 4)]++;
  assert.ok(counts.every((n) => Math.abs(n - 2_500) < 200), `${counts}`); // and keys spread evenly
});

test("a bounded queue pushes back: a fast producer waits for a slow consumer", async () => {
  const q = new BoundedQueue<number>(3);
  assert.deepEqual([1, 2, 3, 4].map((n) => q.tryPut(n)), [true, true, true, false]); // full: the fourth is refused
  assert.deepEqual([await q.take(), await q.take(), await q.take()], [1, 2, 3]);

  const events: string[] = [];
  const producer = (async () => {
    for (let n = 1; n <= 5; n++) {
      await q.put(n);
      events.push(`put ${n}`);
    }
  })();
  await new Promise((resolve) => setImmediate(resolve)); // let the producer run until it's blocked
  assert.deepEqual(events, ["put 1", "put 2", "put 3"]); // it stopped at the limit
  events.push(`took ${await q.take()}`);
  await new Promise((resolve) => setImmediate(resolve));
  assert.deepEqual(events.slice(3), ["took 1", "put 4"]); // one out, one more in
  for (let i = 0; i < 4; i++) events.push(`took ${await q.take()}`);
  await producer;
  assert.equal(events.filter((e) => e.startsWith("put")).length, 5); // all five got in, never more than 3 waiting
  assert.equal(q.size, 0);
});
