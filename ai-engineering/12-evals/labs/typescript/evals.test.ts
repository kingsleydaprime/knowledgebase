import { test } from "node:test";
import assert from "node:assert/strict";
import { keywords, majority } from "./baselines.ts";
import { compare, gate, loadGolden, parseLabel, runEval, wilson } from "./harness.ts";
import { agreement, judge, pairwise } from "./judge.ts";

const golden = loadGolden();
const round = (xs: number[]) => xs.map((x) => Math.round(x * 100) / 100);

test("the golden set: 20 cases, every label, and the hard kinds tagged", () => {
  assert.equal(golden.length, 20);
  assert.deepEqual(new Set(golden.map((c) => c.label)), new Set(["bug", "billing", "feature", "other"]));
  assert.equal(new Set(golden.map((c) => c.id)).size, 20);
  for (const tag of ["no-keywords", "two-topics", "other-language", "sarcasm", "injection", "vague"]) {
    assert.ok(golden.some((c) => c.tags.includes(tag)), `no ${tag} case`);
  }
});

test("a closed set of labels makes scoring an exact match", () => {
  assert.equal(parseLabel("Billing."), "billing");
  assert.equal(parseLabel("Category: BUG"), "bug");
  assert.equal(parseLabel("bug or billing"), null);
  assert.equal(parseLabel("I'm not sure."), null);
});

test("small samples have wide error bars", () => {
  assert.deepEqual(round(wilson(17, 20)), [0.64, 0.95]);   // "85%" could be anywhere from 64% to 95%
  assert.deepEqual(round(wilson(170, 200)), [0.79, 0.89]); // ten times the cases, a third of the width
});

test("the baselines a model has to beat", async () => {
  const always = await runEval(majority(golden), golden);
  assert.equal(always.results[0].reply, "billing");
  assert.equal(always.passed, 8); // 40% for answering "billing" every time
  const rules = await runEval(keywords, golden);
  assert.equal(rules.passed, 15); // 75%: a model has to beat this to earn its cost
  assert.deepEqual(rules.byTag["easy"], { passed: 7, total: 7 });
  assert.deepEqual(rules.byTag["other-language"], { passed: 0, total: 2 });
  const misses = rules.results.filter((r) => !r.pass).map((r) => `${r.id}:${r.got}`);
  assert.deepEqual(misses, ["t10:other", "t12:other", "t14:other", "t15:feature", "t20:billing"]);
  // t15 is Italian: "addebitato" contains "add", so it looks like a feature request. t20 mentions Apple Pay.
});

test("compare shows what a change fixed and what it broke", async () => {
  const before = await runEval(keywords, golden);
  const after = await runEval(async (t) => (t.startsWith("La aplicación") ? "bug" : await keywords(t)), golden);
  assert.deepEqual(compare(before, after), { fixed: ["t14"], broke: [] });
  const worse = await runEval(async (t) => (t.includes("charged twice") ? "bug" : await keywords(t)), golden);
  assert.deepEqual(compare(before, worse), { fixed: [], broke: ["t02"] });
});

test("the gate: a floor, no regressions, and must-pass cases", async () => {
  const base = await runEval(keywords, golden);
  assert.deepEqual(gate(base, { minRate: 0.6 }), { ok: true, reasons: [] });
  const worse = await runEval(async (t) => (t.includes("charged twice") ? "bug" : await keywords(t)), golden);
  assert.deepEqual(gate(worse, { minRate: 0.75, baseline: base, mustPass: ["t02", "t18"] }), {
    ok: false,
    reasons: ["pass rate 70% is below the floor of 75%", "regressed on t02", "must-pass case t02 failed"],
  });
});

test("the judge gives one verdict per criterion, and silence is a fail", async () => {
  const ask = async () => "1: PASS\n2: FAIL\n3: PASS"; // never answered criterion 4
  const result = await judge(ask, "I was charged twice.", "Sorry! We've refunded you and added a free month.");
  assert.deepEqual(result.verdicts.map((v) => [v.pass, v.answered]), [[true, true], [false, true], [true, true], [false, false]]);
  assert.equal(result.pass, false);
});

test("pairwise in both orders exposes position bias", async () => {
  const biased = async () => "FIRST"; // prefers whatever it sees first
  assert.equal(await pairwise(biased, "ticket", "reply A", "reply B"), "inconsistent");
  const fair = async (prompt: string) => (prompt.indexOf("reply B") < prompt.indexOf("reply A") ? "FIRST" : "SECOND");
  assert.equal(await pairwise(fair, "ticket", "reply A", "reply B"), "b");
});

test("agreement with a human: kappa catches a lenient judge", () => {
  const human = [true, true, false, false, true, false, true, false, false, true];
  const lenient = [true, true, true, true, true, true, true, true, false, true];
  assert.deepEqual(round(Object.values(agreement(lenient, human))), [0.6, 0.2]);   // 60% agreement, kappa 0.2: weak
  const careful = [true, true, false, false, true, false, true, true, false, true];
  assert.deepEqual(round(Object.values(agreement(careful, human))), [0.9, 0.8]);   // kappa 0.8: worth trusting
});
