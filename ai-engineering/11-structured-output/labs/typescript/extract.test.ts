import { test } from "node:test";
import assert from "node:assert/strict";
import { extractInvoice, type Message, type Reply, parseModelJson } from "./extract.ts";
import { checkInvariants, validateInvoice } from "./invoice.ts";

const good = {
  vendor: "Brightline Studio Ltd",
  invoice_number: "INV-2041",
  currency: "GBP",
  due_date: "2026-10-15",
  line_items: [
    { description: "Logo design", amount_cents: 45000 },
    { description: "Two revisions", amount_cents: 12000 },
    { description: "Brand guide PDF", amount_cents: 8550 },
  ],
  total_cents: 65550,
};

/** A scripted model: replies in order and keeps every conversation it was sent. */
function scripted(...replies: Reply[]) {
  const seen: Message[][] = [];
  const model = async (messages: Message[]) => {
    seen.push(structuredClone(messages));
    return replies.shift()!;
  };
  return { model, seen };
}
const say = (text: string): Reply => ({ text, finishReason: "stop" });

test("parseModelJson digs the object out of fences and chatter", () => {
  assert.deepEqual(parseModelJson('Sure! Here it is:\n```json\n{"a": 1}\n```\nAnything else?'), { a: 1 });
  assert.throws(() => parseModelJson("I can't find an invoice."), /no JSON object/);
  assert.throws(() => parseModelJson('{"a": 1,}'), SyntaxError); // a trailing comma is still invalid
});

test("the validator lists every shape problem, in words a model can act on", () => {
  assert.deepEqual(validateInvoice(good), { ok: true, value: good });
  const result = validateInvoice({ ...good, currency: "pounds", due_date: "15 October 2026", total_cents: 655.5, notes: "thanks" });
  assert.deepEqual(result, { ok: false, errors: [
    'unexpected field "notes"',
    '"currency" must be one of GBP, USD, EUR, NGN',
    '"due_date" must be a date like 2026-10-15',
    '"total_cents" must be a whole number of cents',
  ] });
});

test("schema-valid isn't the same as right: the items must add up", () => {
  const wrong = { ...good, total_cents: 65500 };
  assert.equal(validateInvoice(wrong).ok, true);
  assert.deepEqual(checkInvariants(wrong), { ok: false, errors: ["line items add up to 65550 cents but total_cents is 65500"] });
});

test("first try good: one call", async () => {
  const { model } = scripted(say(JSON.stringify(good)));
  assert.deepEqual(await extractInvoice(model, "…"), { ok: true, invoice: good, attempts: 1 });
});

test("a bad reply is retried with the specific errors fed back", async () => {
  const { model, seen } = scripted(say(JSON.stringify({ ...good, total_cents: 65500 })), say(JSON.stringify(good)));
  const outcome = await extractInvoice(model, "…");
  assert.equal(outcome.ok && outcome.attempts, 2);
  const feedback = seen[1].at(-1)!;
  assert.equal(feedback.role, "user");
  assert.match(feedback.content, /line items add up to 65550 cents but total_cents is 65500/);
});

test("a truncated reply is retried, not parsed", async () => {
  const { model, seen } = scripted({ text: '{"vendor": "Brightline', finishReason: "length" }, say(JSON.stringify(good)));
  assert.equal((await extractInvoice(model, "…")).ok, true);
  assert.match(seen[1].at(-1)!.content, /cut off/);
});

test("a refusal stops immediately: retrying won't change it", async () => {
  const { model, seen } = scripted({ text: "", finishReason: "stop", refusal: "I can't help with that." });
  assert.deepEqual(await extractInvoice(model, "…"), { ok: false, reason: "refused", detail: "I can't help with that.", attempts: 1 });
  assert.equal(seen.length, 1);
});

test("retries are capped, and the last problem is reported", async () => {
  const { model } = scripted(say("nope"), say("still no"), say('{"vendor": 1}'));
  const outcome = await extractInvoice(model, "…", 3);
  assert.equal(outcome.ok, false);
  assert.equal(!outcome.ok && outcome.attempts, 3);
  assert.match(!outcome.ok ? outcome.detail : "", /"vendor" must be a string/);
});
