import { test } from "node:test";
import assert from "node:assert/strict";
import { keywords } from "../../../12-evals/labs/typescript/baselines.ts";
import { loadGolden } from "../../../12-evals/labs/typescript/harness.ts";
import { cascade, type Tier } from "./cascade.ts";
import { type CallRecord, percentile, summarise, timeStream } from "./meter.ts";
import { divergence, sharedPrefix, stableJson } from "./prefix.ts";
import { batchPrice, breakEvenCalls, cost, PRICES } from "./pricing.ts";

const cents = (usd: number) => Math.round(usd * 100);

test("output tokens cost five times as much as input tokens", () => {
  const sonnet = PRICES["claude-sonnet-5-5"];
  assert.equal(cost({ inputTokens: 1_000_000, outputTokens: 0 }, sonnet), 2);
  assert.equal(cost({ inputTokens: 0, outputTokens: 1_000_000 }, sonnet), 10);
  assert.equal(cost({ inputTokens: 2000, outputTokens: 500 }, sonnet), 0.009); // the output is a fifth of the tokens and over half the cost
});

test("caching a 6,000-token prefix across 1,000 calls", () => {
  const sonnet = PRICES["claude-sonnet-5-5"];
  const calls = 1000;
  const [prefix, question, answer] = [6000, 150, 100];
  const uncached = calls * cost({ inputTokens: prefix + question, outputTokens: answer }, sonnet);
  const first = cost({ cacheWriteTokens: prefix, inputTokens: question, outputTokens: answer }, sonnet);
  const rest = (calls - 1) * cost({ cacheReadTokens: prefix, inputTokens: question, outputTokens: answer }, sonnet);
  assert.equal(cents(uncached), 1330); // $13.30
  assert.equal(cents(first + rest), 251); // $2.51: over five times cheaper
  const outputShare = (calls * cost({ inputTokens: 0, outputTokens: answer }, sonnet)) / (first + rest);
  assert.equal(Math.round(outputShare * 100), 40); // now the output is the biggest line on the bill
});

test("a cache write pays for itself on the second call", () => {
  assert.equal(breakEvenCalls(PRICES["claude-sonnet-5-5"]), 2);
  const oneHour = { ...PRICES["claude-sonnet-5-5"], cacheWrite: 4 }; // 1-hour entries cost 2× to write
  assert.equal(breakEvenCalls(oneHour), 3);
  assert.equal(batchPrice(PRICES["claude-sonnet-5-5"]).output, 5);
});

test("a timestamp at the front of a prompt leaves nothing to cache", () => {
  const system = "You classify support tickets. Label by what the team has to do next. ".repeat(20);
  const front = (date: string, q: string) => `Today is ${date}.\n${system}\n${q}`;
  const end = (date: string, q: string) => `${system}\nToday is ${date}.\n${q}`;
  const [a, b] = [["2026-10-02T09:00:00Z", "help"], ["2026-10-02T09:00:07Z", "help"]] as const;
  assert.equal(sharedPrefix(front(...a), front(...b)), 27); // "Today is 2026-10-02T09:00:0", then the seconds differ
  assert.equal(sharedPrefix(end(...a), end(...b)), system.length + 28); // everything up to the seconds
  assert.equal(divergence("abc", "abd", 1), 'differ at character 2: "bc" vs "bd"');
});

test("unsorted JSON changes the bytes even when the data is the same", () => {
  const a = { tools: ["search"], user: { tier: "pro", id: 7 } };
  const b = { user: { id: 7, tier: "pro" }, tools: ["search"] };
  assert.notEqual(JSON.stringify(a), JSON.stringify(b));
  assert.equal(stableJson(a), stableJson(b));
  assert.equal(stableJson(b), '{"tools":["search"],"user":{"id":7,"tier":"pro"}}');
});

test("a cascade: keyword rules first, a big model only when they fall through to 'other'", async () => {
  const golden = loadGolden();
  const label = new Map(golden.map((c) => [c.ticket, c.label]));
  // A stand-in for a big model that is always right, so this test measures the cascade, not the model.
  const big: Tier = { name: "big", costUsd: 0.002, answer: async (t) => label.get(t)!, accept: () => true };
  const cheap: Tier = { name: "keywords", costUsd: 0, answer: keywords, accept: (a) => a !== "other" };

  const results = await Promise.all(golden.map(async (c) => ({ c, ...(await cascade(c.ticket, [cheap, big])) })));
  const escalated = results.filter((r) => r.by === "big").map((r) => r.c.id);
  const wrong = results.filter((r) => r.answer !== r.c.label).map((r) => r.c.id);
  assert.deepEqual(escalated, ["t04", "t10", "t12", "t14", "t17", "t19"]);
  assert.deepEqual(wrong, ["t15", "t20"]); // confidently wrong, so never escalated: the check, not the model, limits the cascade
  assert.equal(results.reduce((total, r) => total + r.costUsd, 0).toFixed(3), "0.012"); // against $0.040 for the big model alone
});

test("p95 shows the slow call that the median hides", () => {
  const ms = [1200, 900, 1100, 1000, 950, 1050, 980, 1020, 990, 9000];
  assert.equal(percentile(ms, 50), 1000);
  assert.equal(percentile(ms, 95), 9000);
  const record = (ms: number, cacheRead: number): CallRecord => ({
    feature: "triage",
    model: "claude-sonnet-5-5",
    ms,
    usage: { inputTokens: 150, cacheReadTokens: cacheRead, cacheWriteTokens: cacheRead ? 0 : 6000, outputTokens: 100 },
    costUsd: 0.002,
    ok: true,
  });
  const summary = summarise(ms.map((m, i) => record(m, i === 0 ? 0 : 6000)));
  assert.deepEqual([summary.p50Ms, summary.p95Ms, summary.meanMs], [1000, 9000, 1819]); // the mean blends both
  assert.equal(Math.round(summary.cacheReadShare * 100), 88);
});

test("time to first token is measured apart from the total", async () => {
  let t = 0;
  async function* stream() {
    t += 800; // the model reads the prompt before the first token appears
    yield "Your";
    for (const word of [" refund", " is", " on", " its", " way."]) {
      t += 100;
      yield word;
    }
  }
  assert.deepEqual(await timeStream(stream(), () => t), { text: "Your refund is on its way.", ttftMs: 800, totalMs: 1300 });
});
