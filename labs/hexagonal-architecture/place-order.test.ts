import { test } from "node:test";
import assert from "node:assert/strict";
import { makePlaceOrder } from "./src/application/place-order.ts";
import { FakePayments, InMemoryOrders } from "./src/adapters/in-memory.ts";
import { InvalidTotalError, PaymentDeclinedError } from "./src/domain/order.ts";

function setup(declineAbove = 1_000_000) {
  const orders = new InMemoryOrders();
  const placeOrder = makePlaceOrder({ orders, payments: new FakePayments(declineAbove), nextId: () => "o1" });
  return { orders, placeOrder };
}

test("a paid order is saved with status paid", async () => {
  const { orders, placeOrder } = setup();
  await placeOrder("c1", 250_000);
  assert.deepEqual(orders.saved, [{ id: "o1", customerId: "c1", totalKobo: 250_000, status: "paid" }]);
});

test("a declined payment saves nothing", async () => {
  const { orders, placeOrder } = setup(100);
  await assert.rejects(placeOrder("c1", 250_000), PaymentDeclinedError);
  assert.equal(orders.saved.length, 0);
});

test("the domain rejects a fractional total before any payment is attempted", async () => {
  const { orders, placeOrder } = setup();
  await assert.rejects(placeOrder("c1", 99.5), InvalidTotalError);
  assert.equal(orders.saved.length, 0);
});
