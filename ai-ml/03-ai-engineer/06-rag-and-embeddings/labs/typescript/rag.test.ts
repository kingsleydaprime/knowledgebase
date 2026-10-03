import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { chunkDoc, loadHelp, withContext } from "./chunk.ts";
import { checkCitations, docsOf, groundedPrompt, mrr, type Question, recallAtK } from "./rag.ts";
import { bm25, cosine, rrf, toyEmbed, vectorSearch } from "./search.ts";

const docs = loadHelp();
const chunks = docs.flatMap((d) => chunkDoc(d).map((c) => ({ id: c.id, text: withContext(c, d.title) })));
const questions: Question[] = JSON.parse(readFileSync(new URL("../shared/questions.json", import.meta.url), "utf8"));
const round = (x: number) => Math.round(x * 1000) / 1000;

test("one chunk per section, each prefixed with where it came from", () => {
  assert.deepEqual(chunks.map((c) => c.id), [
    "refunds#1", "refunds#2", "refunds#3", "password#1", "password#2", "export#1", "export#2", "appearance#1", "shipping#1", "shipping#2",
  ]);
  assert.equal(chunks[1].text, "Refunds > How long a refund takes\nMost refunds arrive within 5 to 10 working days. Your bank may take a few more days to show it.");
});

test("a long section is split on paragraphs, and each piece repeats the one before", () => {
  const doc = { id: "long", title: "Long", body: "## Part\none two three four\n\nfive six seven eight\n\nnine ten eleven twelve" };
  assert.deepEqual(chunkDoc(doc, 8).map((c) => c.text), [
    "one two three four\n\nfive six seven eight",
    "five six seven eight\n\nnine ten eleven twelve", // the overlap: "five six seven eight" appears in both
  ]);
});

test("cosine measures direction, not length", () => {
  assert.equal(cosine([1, 0], [5, 0]), 1);
  assert.equal(cosine([1, 0], [0, 1]), 0);
  assert.equal(round(cosine([1, 0], [1, 1])), 0.707);
  assert.equal(cosine([0, 0], [1, 1]), 0); // an empty vector matches nothing
});

test("the hand-made embedding: different words, same meaning, nearby vectors", () => {
  assert.deepEqual(toyEmbed("My login doesn't work any more."), [1, 0, 0, 0, 0, 0]); // account
  assert.equal(cosine(toyEmbed("My login doesn't work any more."), toyEmbed("Reset your password")), 1); // no shared words
  assert.deepEqual(toyEmbed("What does E1042 mean?"), [0, 0, 0, 0, 0, 0]); // and nothing at all for an error code
});

async function rankings(q: string) {
  const keyword = bm25(q, chunks);
  const vector = await vectorSearch(q, chunks, toyEmbed);
  return { keyword: docsOf(keyword), vector: docsOf(vector), hybrid: docsOf(rrf([keyword, vector])) };
}

test("each method misses something; together they find every answer", async () => {
  // Keyword search nails the exact code; the embedding has no idea what E1042 is.
  assert.deepEqual(await rankings("What does E1042 mean?"), { keyword: ["export"], vector: [], hybrid: ["export"] });
  // The embedding understands "login"; keyword search matched "more" ("a few more days") and ranked refunds first.
  assert.deepEqual(await rankings("My login doesn't work any more."), { keyword: ["refunds"], vector: ["password"], hybrid: ["refunds", "password"] });
  // Common words like "can" and "the" put refunds above appearance for keywords; meaning puts appearance first.
  const darker = await rankings("Can I make the app darker?");
  assert.deepEqual([darker.keyword[0], darker.vector[0], darker.hybrid[0]], ["refunds", "appearance", "appearance"]);
});

test("retrieval, scored on its own: recall and mean reciprocal rank", async () => {
  const results = { keyword: new Map<string, string[]>(), vector: new Map<string, string[]>(), hybrid: new Map<string, string[]>() };
  for (const q of questions) {
    const r = await rankings(q.question);
    for (const k of ["keyword", "vector", "hybrid"] as const) results[k].set(q.id, r[k]);
  }
  const score = (r: Map<string, string[]>) => [recallAtK(r, questions, 1), recallAtK(r, questions, 3), round(mrr(r, questions))];
  assert.deepEqual(score(results.keyword), [0.6, 0.8, 0.7]);
  assert.deepEqual(score(results.vector), [0.8, 0.8, 0.8]);
  assert.deepEqual(score(results.hybrid), [0.8, 1, 0.9]); // every answer in the top 3, though not always first
  // Search always returns something: for a question the help centre can't answer, keywords still found "matches".
  assert.deepEqual(results.keyword.get("q6")?.slice(0, 1), ["refunds"]);
});

test("the grounded prompt numbers its sources and says what to do when they don't help", () => {
  const prompt = groundedPrompt("How long does a refund take?", [{ id: "refunds#2", text: "Most refunds arrive within 5 to 10 working days." }]);
  assert.match(prompt, /using only the sources below/);
  assert.match(prompt, /reply exactly: "I don't know\."/);
  assert.match(prompt, /\[S1\] \(refunds#2\)\nMost refunds arrive within 5 to 10 working days\./);
});

test("citations are checked before an answer is shown", () => {
  assert.deepEqual(checkCitations("Most refunds arrive within 5 to 10 working days [S1].", 2), { ok: true, problems: [] });
  assert.deepEqual(checkCitations("I don't know.", 2), { ok: true, problems: [] });
  assert.deepEqual(checkCitations("Refunds are instant.", 2), { ok: false, problems: ["no citations"] });
  assert.deepEqual(checkCitations("Refunds take a week [S3].", 2), { ok: false, problems: ["cites S3, which wasn't given"] });
});
