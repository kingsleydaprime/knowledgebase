import { test } from "node:test";
import assert from "node:assert/strict";
import { applyLoyaltyDiscount, isLoyal, placeOrder, subtotal, toPence } from "./after.mjs";

const loyal = { active: true, orderCount: 11, email: "a@b.c" };
const newbie = { active: true, orderCount: 2, email: "n@b.c" };

test("subtotal multiplies price by quantity", () => {
  assert.equal(subtotal([{ price: 2.5, quantity: 2 }, { price: 1, quantity: 3 }]), 8);
});

test("loyalty needs more than 10 orders AND an active account", () => {
  assert.equal(isLoyal(loyal), true);
  assert.equal(isLoyal({ ...loyal, orderCount: 10 }), false); // boundary: exactly 10 is not loyal
  assert.equal(isLoyal({ ...loyal, active: false }), false);
});

test("discount applies only to loyal customers", () => {
  assert.equal(applyLoyaltyDiscount(100, loyal), 90);
  assert.equal(applyLoyaltyDiscount(100, newbie), 100);
});

test("toPence rounds away floating-point noise", () => {
  assert.equal(toPence(0.1 + 0.2), 30);
});

test("placeOrder saves and emails the same total", () => {
  const orders = [], mailer = [];
  const total = placeOrder({ id: 1, items: [{ price: 10, quantity: 2 }], customer: loyal }, { orders, mailer });
  assert.equal(total, 1800);
  assert.deepEqual(orders, [{ id: 1, totalPence: 1800 }]);
  assert.equal(mailer[0].body, "Your total is 1800p");
});

test("an empty order is rejected before anything is saved", () => {
  const orders = [];
  assert.throws(() => placeOrder({ id: 2, items: [], customer: newbie }, { orders, mailer: [] }), /bad order/);
  assert.equal(orders.length, 0);
});
