import { test } from "node:test";
import assert from "node:assert/strict";
import * as grpc from "@grpc/grpc-js";
import protobuf from "protobufjs";
import { connect, startServer } from "./server.ts";
import { encodeOrderSummary } from "../typescript/communication.ts";

test("a unary call: one request, one typed response", async () => {
  const server = await startServer();
  const client = connect(server.port);
  assert.deepEqual(await client.getSummary(1), { id: 1, customer: "Gbenga Ali", totalPence: 8996 });
  client.close();
  await server.stop();
});

test("errors are status codes, not HTTP numbers: NOT_FOUND with details", async () => {
  const server = await startServer();
  const client = connect(server.port);
  await assert.rejects(client.getSummary(404), (err: grpc.ServiceError) => {
    assert.equal(err.code, grpc.status.NOT_FOUND);
    assert.equal(err.details, "no order 404");
    return true;
  });
  client.close();
  await server.stop();
});

test("a deadline: the client stops waiting, and the server learns the call was cancelled", async () => {
  const server = await startServer({ delayMs: 200 });
  const client = connect(server.port);
  await assert.rejects(client.getSummary(1, 50), (err: grpc.ServiceError) => err.code === grpc.status.DEADLINE_EXCEEDED);
  await new Promise((r) => setTimeout(r, 250)); // let the slow handler finish its wait
  assert.equal(server.seen.cancelled, 1); // it checked, and skipped the work
  client.close();
  await server.stop();
});

test("a server stream: one request, several responses in order", async () => {
  const server = await startServer();
  const client = connect(server.port);
  assert.deepEqual(await client.watchOrder(1), ["created", "paid", "shipped"]);
  client.close();
  await server.stop();
});

test("the bytes on the wire are exactly the ones the lesson encodes by hand", async () => {
  const root = await protobuf.load(new URL("./shop.proto", import.meta.url).pathname);
  const OrderSummary = root.lookupType("shop.v1.OrderSummary");
  const wire = OrderSummary.encode({ id: 1, customer: "Gbenga Ali", totalPence: 8996 }).finish();
  assert.deepEqual([...wire], encodeOrderSummary({ id: 1, customer: "Gbenga Ali", totalPence: 8996 }));
  assert.equal(wire.length, 17);
  // proto3 doesn't send fields at their zero value: an empty summary is zero bytes.
  assert.equal(OrderSummary.encode({ id: 0, customer: "", totalPence: 0 }).finish().length, 0);
});

test("adding a field: old readers skip it, new readers see a default for old messages", () => {
  const v1 = protobuf.parse(`syntax = "proto3"; message OrderSummary { uint32 id = 1; string customer = 2; uint32 total_pence = 3; }`).root.lookupType("OrderSummary");
  const v2 = protobuf.parse(`syntax = "proto3"; message OrderSummary { uint32 id = 1; string customer = 2; uint32 total_pence = 3; string currency = 4; }`).root.lookupType("OrderSummary");
  const fromNew = v2.encode({ id: 1, customer: "Gbenga Ali", totalPence: 8996, currency: "GBP" }).finish();
  const oldReads = v1.toObject(v1.decode(fromNew));
  assert.deepEqual(oldReads, { id: 1, customer: "Gbenga Ali", totalPence: 8996 }); // field 4 is skipped, no error
  const fromOld = v1.encode({ id: 1, customer: "Gbenga Ali", totalPence: 8996 }).finish();
  assert.equal(v2.toObject(v2.decode(fromOld), { defaults: true }).currency, ""); // missing: the zero value
});
