import { test } from "node:test";
import assert from "node:assert/strict";
import { inMemoryRepository, makeOrdersController, makeOrdersService, OutOfStockError } from "./orders.ts";

test("service: the business rule is tested with plain calls, no HTTP", () => {
  const service = makeOrdersService(inMemoryRepository({ mug: 1 }));
  assert.throws(() => service.place("u1", [{ sku: "mug", quantity: 2 }]), OutOfStockError);
});

test("service: a successful order reserves stock", () => {
  const stock = { mug: 3 };
  const service = makeOrdersService(inMemoryRepository(stock));
  service.place("u1", [{ sku: "mug", quantity: 2 }]);
  assert.equal(stock.mug, 1);
});

test("controller: domain errors become status codes", () => {
  const controller = makeOrdersController(makeOrdersService(inMemoryRepository({ mug: 1 })));
  assert.equal(controller.create({ userId: "u1", body: { items: [] } }).status, 400);
  assert.deepEqual(controller.create({ userId: "u1", body: { items: [{ sku: "mug", quantity: 5 }] } }), {
    status: 409,
    body: { error: "out of stock: mug", sku: "mug" },
  });
  assert.deepEqual(controller.create({ userId: "u1", body: { items: [{ sku: "mug", quantity: 1 }] } }), {
    status: 201,
    body: { id: 1 },
  });
});
