import { test } from "node:test";
import assert from "node:assert/strict";
import { estimateTokens, generate, greedy, sample, seededRandom, softmax, topK, topP, trainBigrams } from "./decoding.ts";

// Scores loosely like the local model's real ones for "The capital of France is" (see live.ts).
const scores = new Map([["Paris", 4.0], ["a", 2.0], ["the", 1.5], ["Lyon", 0.5]]);
const round = (d: Map<string, number>) => Object.fromEntries([...d].map(([t, p]) => [t, Math.round(p * 1000) / 1000]));

test("temperature reshapes the same scores", () => {
  assert.deepEqual(round(softmax(scores, 1)), { Paris: 0.802, a: 0.108, the: 0.066, Lyon: 0.024 });
  assert.deepEqual(round(softmax(scores, 0.5)), { Paris: 0.975, a: 0.018, the: 0.007, Lyon: 0.001 }); // sharper
  assert.deepEqual(round(softmax(scores, 2)), { Paris: 0.547, a: 0.201, the: 0.157, Lyon: 0.095 });   // flatter
});

test("top-k keeps a fixed number; top-p keeps however many reach p", () => {
  const dist = softmax(scores, 1);
  assert.deepEqual([...topK(dist, 2).keys()], ["Paris", "a"]);
  assert.deepEqual([...topP(dist, 0.9).keys()], ["Paris", "a"]);       // 0.802 + 0.108 >= 0.9
  assert.deepEqual([...topP(dist, 0.97).keys()], ["Paris", "a", "the"]);
});

test("greedy always picks the top token; sampling sometimes doesn't", () => {
  const dist = softmax(scores, 1);
  assert.equal(greedy(dist), "Paris");
  const random = seededRandom(42);
  const picks = Array.from({ length: 1000 }, () => sample(dist, random));
  const parisShare = picks.filter((t) => t === "Paris").length / 1000;
  assert.ok(parisShare > 0.76 && parisShare < 0.85, `Paris picked ${parisShare}`); // ~0.802 expected
});

const corpus = "the cat sat on the mat . the cat ate the fish . the dog sat on the log .";
const model = trainBigrams(corpus);

test("temperature 0 generates the same text every time", () => {
  const a = generate(model, "the", { temperature: 0, maxTokens: 6 }, seededRandom(1));
  const b = generate(model, "the", { temperature: 0, maxTokens: 6 }, seededRandom(999));
  assert.deepEqual(a, b);
  assert.deepEqual(a, ["the", "cat", "sat", "on", "the", "cat", "sat"]); // greedy loops: a known failure mode
});

test("with temperature, the seed decides the text; max tokens and stop sequences end it", () => {
  const opts = { temperature: 1, maxTokens: 20, stop: "." };
  const first = generate(model, "the", opts, seededRandom(7));
  assert.deepEqual(first, generate(model, "the", opts, seededRandom(7))); // same seed, same text
  assert.ok(!first.includes("."));                                         // stopped at the stop sequence
  assert.ok(generate(model, "the", { temperature: 1, maxTokens: 3 }, seededRandom(7)).length <= 4);
});

test("about four characters per token", () => {
  assert.equal(estimateTokens("I love transformers"), 5); // a real tokenizer gives 4: I, love, transform, ers
});
