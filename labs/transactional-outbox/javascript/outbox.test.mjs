import { test } from "node:test";
import assert from "node:assert/strict";
import {
  Crash, fakeBroker, idempotentConsumer, openDb,
  placeOrderPublishThenSave, placeOrderSaveThenPublish, placeOrderWithOutbox, relay,
} from "./outbox.mjs";

const countOrders = (db) => db.prepare("SELECT COUNT(*) AS n FROM orders").get().n;

test("dual write, save then publish: a crash in between LOSES the event", async () => {
  const db = openDb(), broker = fakeBroker();
  await assert.rejects(placeOrderSaveThenPublish(db, broker, { id: "o1", totalKobo: 500_000 }, { crashBetween: true }), Crash);
  assert.equal(countOrders(db), 1);      // the order exists...
  assert.equal(broker.sent.length, 0);   // ...but nobody will ever hear about it
});

test("dual write, publish then save: a failed save leaves a PHANTOM event", async () => {
  const db = openDb(), broker = fakeBroker();
  await assert.rejects(placeOrderPublishThenSave(db, broker, { id: "o2", totalKobo: -1 }), /CHECK constraint failed/);
  assert.equal(countOrders(db), 0);      // no order...
  assert.equal(broker.sent.length, 1);   // ...but the warehouse was told to ship it
});

test("outbox: a crash before the relay runs loses nothing — the relay sends it later", async () => {
  const db = openDb(), broker = fakeBroker();
  placeOrderWithOutbox(db, { id: "o3", totalKobo: 500_000 });
  // the process dies here; on restart the relay picks up where it left off
  assert.equal(await relay(db, broker), 1);
  assert.deepEqual(broker.sent, [{ eventId: "evt-o3", type: "OrderPlaced", orderId: "o3" }]);
  assert.equal(await relay(db, broker), 0); // already marked: not sent again
});

test("outbox: a failed order rolls back its event too — no phantom", async () => {
  const db = openDb(), broker = fakeBroker();
  assert.throws(() => placeOrderWithOutbox(db, { id: "o4", totalKobo: -1 }), /CHECK constraint failed/);
  assert.equal(countOrders(db), 0);
  assert.equal(await relay(db, broker), 0);
});

test("relay crash after publish: the event is sent twice, the idempotent consumer applies it once", async () => {
  const db = openDb(), broker = fakeBroker();
  placeOrderWithOutbox(db, { id: "o5", totalKobo: 500_000 });
  await assert.rejects(relay(db, broker, { crashBeforeMark: true }), Crash);
  await relay(db, broker); // restart: the row was never marked, so it goes again
  assert.equal(broker.sent.length, 2);

  const consumer = idempotentConsumer();
  assert.deepEqual(broker.sent.map((e) => consumer.handle(e)), ["applied", "duplicate"]);
  assert.deepEqual(consumer.applied, ["o5"]);
});
