import { test } from "node:test";
import assert from "node:assert/strict";
import { IllegalTransitionError, Order } from "./order-state.ts";

test("happy path, with two observers that don't know about each other", () => {
  const emails: string[] = [];
  const audit: string[] = [];
  const order = new Order("o1");
  order.onChange((e) => { if (e.to === "shipped") emails.push(`${e.orderId} is on its way`); });
  order.onChange((e) => audit.push(`${e.from}->${e.to}`));

  order.apply("pay");
  order.apply("ship");
  order.apply("deliver");

  assert.equal(order.status, "delivered");
  assert.deepEqual(emails, ["o1 is on its way"]);
  assert.deepEqual(audit, ["pending->paid", "paid->shipped", "shipped->delivered"]);
});

test("a shipped order cannot be cancelled, and nothing is announced", () => {
  const audit: string[] = [];
  const order = new Order("o2");
  order.onChange((e) => audit.push(`${e.from}->${e.to}`));
  order.apply("pay");
  order.apply("ship");
  assert.throws(() => order.apply("cancel"), IllegalTransitionError);
  assert.equal(order.status, "shipped");
  assert.deepEqual(audit, ["pending->paid", "paid->shipped"]);
});

test("the UI can ask which buttons to show", () => {
  const order = new Order("o3");
  assert.deepEqual(order.allowedActions(), ["pay", "cancel"]);
  order.apply("pay");
  assert.deepEqual(order.allowedActions(), ["ship", "cancel"]);
});
