import { test } from "node:test";
import assert from "node:assert/strict";
import { fee, feeRules } from "./fees.mjs";
import { makeCheckout } from "./checkout.mjs";

test("existing fee rules", () => {
  assert.equal(fee({ type: "card", amountPence: 10000 }), 290);
  assert.equal(fee({ type: "transfer", amountPence: 10000 }), 50);
});

test("a new method is added without editing fee()", () => {
  const rules = { ...feeRules, ussd: () => 25 };
  assert.equal(fee({ type: "ussd", amountPence: 10000 }, rules), 25);
});

test("unknown methods fail loudly instead of charging nothing", () => {
  assert.throws(() => fee({ type: "crypto", amountPence: 1 }), /no fee rule for crypto/);
});

test("checkout runs with fakes — no payment provider, no email", async () => {
  const charged = [], sent = [];
  const checkout = makeCheckout({
    payments: { charge: async (id, pence) => { charged.push([id, pence]); return "ref_1"; } },
    receipts: { send: async (id, text) => { sent.push(text); } },
  });
  const result = await checkout({ customerId: "c1", totalPence: 10000, payment: { type: "transfer", amountPence: 10000 } });
  assert.deepEqual(result, { charge: 10050, ref: "ref_1" });
  assert.deepEqual(charged, [["c1", 10050]]);
  assert.equal(sent[0], "Charged 10050p (ref ref_1)");
});

class Rectangle {
  setWidth(w) { this.w = w; }
  setHeight(h) { this.h = h; }
  area() { return this.w * this.h; }
}
class Square extends Rectangle {
  setWidth(w) { this.w = w; this.h = w; }
  setHeight(h) { this.w = h; this.h = h; }
}
function stretch(rect) { rect.setWidth(5); rect.setHeight(4); return rect.area(); }

test("LSP: Square breaks a caller written for Rectangle", () => {
  assert.equal(stretch(new Rectangle()), 20);
  assert.equal(stretch(new Square()), 16);
});
