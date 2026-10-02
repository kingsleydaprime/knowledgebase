import { test } from "node:test";
import assert from "node:assert/strict";
import { atLeastOnceBus, inProcessBus } from "./src/shared/bus.ts";
import { makeOrders } from "./src/orders/api.ts";
import { makePayments } from "./src/payments/api.ts";

test("in-process: one payment, recorded once", async () => {
  const bus = inProcessBus();
  const orders = makeOrders(bus, { idempotent: false });
  await makePayments(bus).recordSuccess("o1", 500_000);
  assert.equal(orders.paidSoFar("o1"), 500_000);
});

test("at-least-once delivery + a naive consumer = the customer is credited twice", async () => {
  const bus = atLeastOnceBus();
  const orders = makeOrders(bus, { idempotent: false });
  await makePayments(bus).recordSuccess("o1", 500_000);
  assert.equal(orders.paidSoFar("o1"), 1_000_000);
});

test("at-least-once delivery + an idempotent consumer = correct", async () => {
  const bus = atLeastOnceBus();
  const orders = makeOrders(bus, { idempotent: true });
  const payments = makePayments(bus);
  await payments.recordSuccess("o1", 500_000);
  await payments.recordSuccess("o1", 250_000); // a genuinely second payment still counts
  assert.equal(orders.paidSoFar("o1"), 750_000);
});
