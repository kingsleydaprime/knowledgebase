import { test } from "node:test";
import assert from "node:assert/strict";
import { createLimiter, sendOtp, sendOtpWithSingleton } from "./limiter.ts";
import { EmailBuilder } from "./builder.ts";

// These two tests are identical. With the singleton, the second one inherits the first one's state.
test("singleton, test A: first three OTPs are sent", () => {
  assert.deepEqual([1, 2, 3].map(() => sendOtpWithSingleton("u1")), ["sent", "sent", "sent"]);
});
test("singleton, test B: same test, but state leaked from A", () => {
  assert.deepEqual([1, 2, 3].map(() => sendOtpWithSingleton("u1")), ["rate-limited", "rate-limited", "rate-limited"]);
});

test("factory, test A: first three OTPs are sent", () => {
  const limiter = createLimiter(3);
  assert.deepEqual([1, 2, 3].map(() => sendOtp(limiter, "u1")), ["sent", "sent", "sent"]);
});
test("factory, test B: a fresh limiter, so the same result", () => {
  const limiter = createLimiter(3);
  assert.deepEqual([1, 2, 3, 4].map(() => sendOtp(limiter, "u1")), ["sent", "sent", "sent", "rate-limited"]);
});

test("builder: build() rejects an incomplete or contradictory email", () => {
  assert.throws(() => new EmailBuilder().subject("Hi").build(), /at least one recipient/);
  assert.throws(() => new EmailBuilder().to("a@x.com").cc("a@x.com").subject("Hi").build(), /in both to and cc: a@x.com/);
  const email = new EmailBuilder().to("a@x.com").subject("Receipt").text("Thanks").build();
  assert.deepEqual(email, { to: ["a@x.com"], cc: [], subject: "Receipt", text: "Thanks", replyTo: undefined });
});
