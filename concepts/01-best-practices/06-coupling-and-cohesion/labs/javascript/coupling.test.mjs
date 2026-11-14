import { test } from "node:test";
import assert from "node:assert/strict";
import { analyse } from "./coupling.mjs";

const { rows, cycles } = analyse("sample/src");
const byName = Object.fromEntries(rows.map((r) => [r.module, r]));

test("shared is depended on by everyone and depends on nothing: maximally stable", () => {
  assert.deepEqual(byName.shared, { module: "shared", afferent: 3, efferent: 0, instability: 0 });
});

test("orders depends on three modules and is depended on by one", () => {
  assert.deepEqual(byName.orders, { module: "orders", afferent: 1, efferent: 3, instability: 0.75 });
});

test("the orders <-> payments cycle is found; packages and aliases are handled", () => {
  assert.deepEqual(cycles, [["orders", "payments"]]);
  assert.equal(byName.users.efferent, 1); // only shared — "express" is not one of our modules
});
