# How LLMs Work

> **[Beginner]** · Covers what a large language model actually does: tokens, the context window, attention, generating one token at a time, and the decoding settings you choose in every call. The worked example builds the decoding step yourself and then asks a real local model for its probabilities. The numbers in it were measured on 2026-10-02.

## Before you start

You can already:

- Say what a model is: a function with adjustable numbers, fitted to data → [[ai-ml/00-foundations/02-what-is-a-model|what is a model]].
- Read TypeScript and run `node --test`.
- Know roughly what a dot product is → [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|dot product]]. This is only needed for the attention section.

After this lesson you will be able to:

1. Explain an LLM as one mechanism, "predict the next token", applied over and over.
2. Estimate tokens from text, and explain why tokens are what you pay for and what fills the context window.
3. Say what temperature, top-k, top-p, max tokens and stop sequences each do to the probabilities, and choose values for a task.
4. Explain **mechanically** why a model hallucinates. This is week 1's closed-book question.

**Study route.** Read §1–6. Run the lab, then predict what `live.ts` will print for your own prompt before you run it. The pitfalls and checks come last.

## The kid version

Imagine a game where you finish other people's sentences. Someone says "The capital of France is…" and you say "Paris", because you've heard that a thousand times. Someone says "My favourite colour is…" and you have to guess, so you might say blue, or red. Then you add your word to the sentence and finish the *new* sentence, one word at a time, until you decide to stop. An LLM plays exactly this game. It has read so much that its guesses are very good. **But it's still guessing what sounds right, not checking what's true.** If you ask it about something it never heard, it doesn't say "I don't know". It says whatever sounds most like an answer.

**Where the analogy stops working.** You guess with words; a model guesses with tokens, which are often pieces of words. And a model doesn't pick one guess. It gives a score to every one of about 100,000 tokens at once, and a separate rule, which you control, decides which one gets used.

## 1. Why this exists

You build a feature that sorts support tickets into categories. It works in testing. In production, the same ticket gets "billing" on Monday and "account" on Tuesday, and someone files a bug saying "the AI is broken". Nothing is broken. The model gave "billing" 55% and "account" 40%, and the default temperature told it to *sample*, so it sometimes picked the second one. **If you don't know that the output is a draw from a probability distribution, you'll debug the wrong thing.** The same mechanism explains why the model invents a confident citation, why a long chat "forgets" its start, and why output streams in word by word.

## Terms used in this lesson

1. **LLM (large language model)**: The letters stand for those three words. It is a model trained on a huge amount of text to predict the next token, given the tokens so far.
2. **Token**: This is the unit a model reads and writes. It is a chunk of text, often part of a word, that has a number in the model's fixed vocabulary.
3. **Vocabulary**: This is the full list of tokens a model knows, usually somewhere between 30,000 and 250,000 of them.
4. **Context window**: This is the most tokens, input and output together, that the model can take into account in one request.
5. **Transformer**: This is the neural network design that almost every modern LLM uses. It was introduced in 2017.
6. **Self-attention**: This is the step inside a transformer where each token works out how much every other token should influence it.
7. **Autoregressive generation**: This means generating one token at a time, where each new token is added to the input before the next one is predicted.
8. **Score**: This is also known as a **logit**. It is the raw number the model gives each token in the vocabulary before those numbers are turned into probabilities.
9. **Softmax**: This is the formula that turns a list of scores into probabilities that add up to 1. Bigger scores get bigger probabilities.
10. **Logprob (log-probability)**: This is the natural logarithm of a probability. APIs often return logprobs instead of probabilities, and `Math.exp(logprob)` turns one back into a probability.
11. **Decoding**: This is the rule that picks the actual next token from the probabilities. Temperature, top-k and top-p are decoding settings.
12. **Greedy decoding**: This means always picking the most likely token. Temperature 0 gives greedy decoding.
13. **Sampling**: This means picking a token at random, with each token's chance equal to its probability.
14. **Hallucination**: This is fluent, confident output that is false. It happens because the model is trained to produce likely text, not checked text.
15. **RLHF (reinforcement learning from human feedback)**: The letters stand for those words. It is a training step where people rate the model's answers and the model is adjusted toward the answers people preferred.

## 2. Tokens — the unit of everything

LLMs don't see characters or words; they see **tokens**. A common word is one token. A rare word splits into several (`under` + `stand` + `ing`).

```
"I love transformers" → ["I", " love", " transform", "ers"]   (splits vary by tokenizer)
```

Notice the spaces: `" love"` with its leading space is a different token from `"love"`. That's why you saw `"Blue"` and `"blue"` as separate entries in the worked example.

This is not trivia. **Tokens are the unit of pricing and of context limits.** For English, 1 token is about 4 characters, or about three-quarters of a word. Code, other languages and unusual words use more tokens per character. Every cost estimate and context-budget decision you make is in tokens.

## 3. The context window — the working memory

The **context window** is the most tokens, input and output combined, that the model can take into account at once. Anything outside it doesn't exist for that request. It hasn't been forgotten; it was never in view. That's why long conversations need summarising or trimming. It's also why [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]] exists: it feeds the model only the relevant slice of a large set of documents instead of needing an infinite window.

Modern windows are large, often hundreds of thousands of tokens, but they aren't free. More context costs more and is slower. Past a point, the model also pays less attention to any single detail; facts in the middle of a long input get used less than facts at the start or end ("lost in the middle"). On a laptop the limit is memory: the window you set (`num_ctx` in Ollama) has to fit in RAM alongside the model → [[ai-ml/03-ai-engineer/16-local-and-open-models/index|local and open models]].

## 4. Transformers and attention

Almost every modern LLM is a **transformer** (2017, "Attention Is All You Need"). Its key step is **self-attention**: for each token, the model computes how much every *other* token should influence it, then blends their information in those proportions. That is how "it" in "the trophy didn't fit in the suitcase because it was too big" ends up linked to "trophy". Mechanically, each token is a vector; the model takes [[ai-ml/00-foundations/03-mathematics/01-linear-algebra/03-dot-product|dot products]] between them and runs the results through softmax to get the attention weights.

The output of all those layers, for the last position, is one score per token in the vocabulary. **That list of scores is the only thing the network produces.** Everything after it is decoding, which is the part you control.

## 5. Autoregressive generation

An LLM generates **one token at a time**:

1. Score every token in the vocabulary.
2. Turn the scores into probabilities with softmax.
3. Pick one token, using the decoding settings.
4. Append it to the input, and go back to step 1.
5. Stop at an end-of-text token, a stop sequence, or the max-tokens limit.

This explains three things you'll see every day. Output streams in token by token. Generation time grows with output length, because every token is a full pass through the network. And an early wrong token can't be taken back; the model carries on from it.

## 6. The decoding settings you actually control

| Setting | What it does to the probabilities |
|---|---|
| **temperature** | divides every score by T before softmax. T below 1 sharpens the distribution toward the top token; T above 1 flattens it. `0` means greedy: always the top token. |
| **top-k** | keeps only the k most likely tokens, then renormalises. A fixed cutoff. |
| **top-p** (nucleus) | keeps the smallest set of most likely tokens whose probabilities add up to p (e.g. `0.9`), then renormalises. A cutoff that adapts: one token when the model is sure, many when it isn't. |
| **max tokens** | a hard cap on output length, and so on cost. |
| **frequency / presence penalty** | lowers the score of tokens that already appeared — by how often (frequency) or at all (presence). Reduces repetition. |
| **stop sequences** | strings that end generation when they're produced. |
| **seed** | where supported, fixes the random number generator so sampling repeats. |

The most useful instinct: **use low temperature for anything with one right answer** (classification, extraction, structured output); raise it for brainstorming. Different output across runs is expected sampling behaviour, not a bug.

Temperature 0 isn't a guarantee of identical output across runs on a hosted API, though. Servers batch requests together and floating-point arithmetic can differ slightly, so a near-tie can flip. Treat it as "nearly deterministic" and test for what matters.

## 7. Pretraining, fine-tuning and instruction-tuning

- **Pretraining** is training on a vast amount of general text so the model learns language broadly. This is the expensive, foundational phase, and it produces a model that *continues* text rather than answering it.
- **Fine-tuning** is further training on a smaller, specific dataset to specialise the model → [[ai-ml/03-ai-engineer/15-fine-tuning-applied|fine-tuning, applied]].
- **Instruction-tuning and RLHF** are additional training so the model follows instructions and prefers helpful, safe answers over merely likely ones. This is why a chat model behaves so differently from a raw pretrained one.

## 8. Why LLMs confidently state wrong things

Put §4–6 together. The network outputs scores for "what token is likely here". Training rewarded producing text that looks like its training data. **Nothing in that loop checks the text against the world.** When the training data clearly covers a fact, the likely continuation is also the true one, and you see 98.6% on "Paris". When it doesn't — an obscure person, a paper that doesn't exist, last week's news — the model still produces the most *answer-shaped* continuation. A citation format with plausible authors is very likely text, even when no such paper exists.

So hallucination is structural; it isn't a bug waiting for a patch. The fixes all add a check from outside the model: put the facts in the context ([[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]]), let it call a tool such as search ([[ai-ml/03-ai-engineer/07-tools-and-mcp|tools]]), validate its output ([[ai-ml/03-ai-engineer/11-structured-output/index|structured output]]), and measure how often it's wrong ([[ai-ml/03-ai-engineer/12-evals|evals]]).

## Worked example — decoding by hand, then a real model

Part 1 builds the decoding step from §5–6 and a toy model, so you can see each setting change the numbers. Part 2 asks a real model for its top five tokens.

**Part 1 — `decoding.ts`.** The toy model is a *bigram* model: it counts which word follows which in a few sentences. A real LLM scores tokens with a transformer, but the loop in `generate` is the same.

```ts
// decoding.ts — how a model turns scores into a next token, and generates one token at a time.

/** A seeded random generator (mulberry32), so sampling is repeatable in tests. */
export function seededRandom(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export type Distribution = Map<string, number>; // token -> probability, summing to 1

/** Softmax with temperature: divide the scores by T, then exponentiate and normalise.
 *  T < 1 sharpens the distribution toward the top token; T > 1 flattens it. */
export function softmax(scores: Map<string, number>, temperature: number): Distribution {
  const scaled = [...scores].map(([token, s]) => [token, s / temperature] as const);
  const max = Math.max(...scaled.map(([, s]) => s)); // subtract the max to avoid overflow
  const exps = scaled.map(([token, s]) => [token, Math.exp(s - max)] as const);
  const total = exps.reduce((sum, [, e]) => sum + e, 0);
  return new Map(exps.map(([token, e]) => [token, e / total]));
}

/** Keep only the k most likely tokens, renormalised. */
export function topK(dist: Distribution, k: number): Distribution {
  return renormalise([...dist].sort((a, b) => b[1] - a[1]).slice(0, k));
}

/** Keep the smallest set of most-likely tokens whose probabilities add up to at least p. */
export function topP(dist: Distribution, p: number): Distribution {
  const kept: [string, number][] = [];
  let cumulative = 0;
  for (const entry of [...dist].sort((a, b) => b[1] - a[1])) {
    kept.push(entry);
    cumulative += entry[1];
    if (cumulative >= p) break;
  }
  return renormalise(kept);
}

function renormalise(entries: [string, number][]): Distribution {
  const total = entries.reduce((sum, [, p]) => sum + p, 0);
  return new Map(entries.map(([token, p]) => [token, p / total]));
}

/** Pick one token: walk the cumulative probabilities until passing a random number in [0, 1). */
export function sample(dist: Distribution, random: () => number): string {
  let r = random();
  for (const [token, p] of dist) {
    if ((r -= p) < 0) return token;
  }
  return [...dist.keys()].at(-1)!;
}

export function greedy(dist: Distribution): string {
  return [...dist].sort((a, b) => b[1] - a[1])[0][0];
}

/** A toy language model: counts which token follows which in a tiny corpus (a "bigram" model).
 *  Real models score every token in a vocabulary of ~100,000 with a neural network; the
 *  generate loop below is the same either way. */
export function trainBigrams(corpus: string): Map<string, Map<string, number>> {
  const tokens = corpus.split(/\s+/).filter(Boolean);
  const counts = new Map<string, Map<string, number>>();
  for (let i = 0; i < tokens.length - 1; i++) {
    const next = counts.get(tokens[i]) ?? new Map();
    next.set(tokens[i + 1], (next.get(tokens[i + 1]) ?? 0) + 1);
    counts.set(tokens[i], next);
  }
  return counts;
}

export type DecodingOptions = { temperature: number; topK?: number; topP?: number; maxTokens: number; stop?: string };

/** Autoregressive generation: score the next token, pick one, append it, repeat. */
export function generate(model: Map<string, Map<string, number>>, start: string, opts: DecodingOptions, random: () => number): string[] {
  const out = [start];
  for (let i = 0; i < opts.maxTokens; i++) {
    const counts = model.get(out.at(-1)!);
    if (!counts) break; // no known continuation
    const scores = new Map([...counts].map(([t, c]) => [t, Math.log(c)])); // log-counts as scores
    let dist = opts.temperature === 0 ? new Map([[greedy(softmax(scores, 1)), 1]]) : softmax(scores, opts.temperature);
    if (opts.topK) dist = topK(dist, opts.topK);
    if (opts.topP) dist = topP(dist, opts.topP);
    const token = sample(dist, random);
    if (token === opts.stop) break;
    out.push(token);
  }
  return out;
}

/** The usual rule of thumb for English: about 4 characters per token. */
export const estimateTokens = (text: string) => Math.ceil(text.length / 4);
```

The tests use scores shaped like the real model's for "The capital of France is":

```ts
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
```

Read the temperature test as numbers. Same four scores, three temperatures:

| Token | T = 0.5 | T = 1 | T = 2 |
|---|---|---|---|
| Paris | 97.5% | 80.2% | 54.7% |
| a | 1.8% | 10.8% | 20.1% |
| the | 0.7% | 6.6% | 15.7% |
| Lyon | 0.1% | 2.4% | 9.5% |

At T = 2, "Lyon" — wrong — is picked almost one time in ten. The scores didn't change; only the decoding did. Also notice the greedy test: with temperature 0 the toy model loops ("the cat sat on the cat sat"), because the single most likely next word always leads back. Real models do this too, which is one reason penalties exist.

**Part 2 — `live.ts`.** This asks your local model through Ollama's OpenAI-compatible endpoint, with `logprobs` turned on.

```ts
// live.ts — ask a real local model for its next-token probabilities. Not run by the lab runner.
//   node live.ts                        # qwen3.5:4b through Ollama
//   node live.ts gemma4 "Once upon a"   # another model, another prompt
const model = process.argv[2] ?? "qwen3.5:4b";
const prompt = process.argv[3] ?? "Complete with one word. The capital of France is";

const res = await fetch("http://127.0.0.1:11434/v1/chat/completions", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({
    model,
    messages: [{ role: "user", content: prompt }],
    max_tokens: 3,
    temperature: 0,
    reasoning_effort: "none", // no hidden thinking: the first token generated is the answer
    logprobs: true,
    top_logprobs: 5,
  }),
});
if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
const data = await res.json();

for (const step of data.choices[0].logprobs.content) {
  console.log(`chose ${JSON.stringify(step.token)}; the top five it considered:`);
  for (const alt of step.top_logprobs) {
    const p = Math.exp(alt.logprob); // the API returns log-probabilities; exp turns them back into probabilities
    console.log(`  ${JSON.stringify(alt.token).padEnd(12)} ${(p * 100).toFixed(2).padStart(6)}%`);
  }
}
```

What it printed on the 16 GB laptop with `qwen3.5:4b`:

```
$ node live.ts
chose "Paris"; the top five it considered:
  "Paris"        98.59%
  "The"           0.57%
  "France"        0.34%
  "the"           0.18%
  "Par"           0.13%

$ node live.ts qwen3.5:4b "Name one colour. Just the word."
chose "Blue"; the top five it considered:
  "Blue"         50.77%
  "Red"          45.72%
  "red"           1.32%
  "blue"          1.16%
  "Green"         0.74%
```

The first prompt has one answer, and the model is nearly certain. The second has many, and it's close to a coin flip between Blue and Red. At temperature 0 you get "Blue" every time. At the usual default of around 0.7–1, you'd get "Red" almost half the time — the support-ticket problem from §1. The spread of these numbers is the model's uncertainty, and it's visible before any text is written.

**Lab:** these files are in [`ai-ml/03-ai-engineer/02-how-llms-work/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/02-how-llms-work/labs/typescript). From the vault root, `python3 labs/run.py how-llms-work/typescript` runs the tests and checks this page still shows the same code. `live.ts` needs Ollama running, so the runner doesn't call it; run it yourself from the lab folder with `node live.ts`.

## Common pitfalls

1. **Calling sampling variation a bug.** If the same input gives different answers, check the temperature before the prompt.
2. **Expecting temperature 0 to be perfectly repeatable on a hosted API.** It's close, not guaranteed. Tests should check properties of the output, not exact strings.
3. **Setting temperature and top-p both to unusual values.** They interact. Change one at a time; most providers recommend adjusting only one.
4. **Budgeting in words instead of tokens.** Code, JSON and non-English text use more tokens than the 4-characters rule suggests. Measure with the provider's token count in the response.
5. **Assuming the model remembers earlier conversations.** It only sees what's in this request's context window. Memory across sessions exists only if your application stores and re-sends it.
6. **Treating confidence as correctness.** Fluent, specific, confident text is exactly what a hallucination looks like.

## Check your understanding

1. In one sentence, what does an LLM's network actually output for each step?
2. About how many tokens is a 2,000-character English paragraph? Why might a 2,000-character JSON blob be more?
3. The scores are Paris 4, a 2, the 1.5, Lyon 0.5. What happens to Lyon's probability as temperature goes from 0.5 to 2, and why?
4. With probabilities Paris 0.80, a 0.11, the 0.07, Lyon 0.02, which tokens survive top-p 0.9? Which survive top-k 3?
5. Why does generation time grow with the length of the *output*, not just the input?
6. Explain, mechanically, why a model can cite a paper that doesn't exist.

<details>
<summary>Answers — after your attempt</summary>

1. One score for every token in the vocabulary, for the next position. Softmax turns these into probabilities, and decoding picks one.
2. About 500 tokens. JSON is full of quotes, braces, colons and short keys, which often become separate tokens, so it costs more tokens per character than prose.
3. It rises from about 0.1% to about 9.5%. Dividing by a bigger T shrinks the gaps between scores, so after softmax the probabilities are closer together and unlikely tokens get a bigger share.
4. Top-p 0.9: Paris and a (0.80 + 0.11 = 0.91 ≥ 0.9). Top-k 3: Paris, a and the.
5. Each output token needs its own full pass through the network, and it can't start until the previous token has been chosen and appended.
6. Training rewards producing likely text. A citation with plausible authors, a title and a year is very likely text in an academic context, and nothing in generation checks it against reality. When the real answer isn't well covered in the training data, the most answer-shaped continuation wins.

</details>

## Practice — independent task

**Map the model's uncertainty.** Use `live.ts` with five prompts of your own: two with one clear answer, two open-ended, and one about something obscure (a small local business, a minor historical figure, a made-up product name).

1. Before each run, write down what you expect the top token's probability to be.
2. Run it and record the top three tokens and their percentages.
3. For the obscure prompt, run it with `max_tokens` raised to 40 and read the answer. Is it true?

**Done when:** you have a table of five prompts with predicted and actual top probabilities, and you can explain in two sentences why a high top probability on the obscure prompt would *not* mean the answer is correct.

## Before moving on

You can explain, without notes, how a model goes from a prompt to one next token, which settings change that step, and why it produces false statements confidently.

**Recap.** An LLM scores every token in its vocabulary, softmax turns the scores into probabilities, and decoding picks one; repeat until it stops. Tokens set both the price and the context limit. Temperature, top-k and top-p reshape the probabilities but never the scores. Hallucination is likely-but-false text, and the fixes all bring a check from outside the model.

**Next.** [[ai-ml/03-ai-engineer/04-calling-models/index|Calling models]] — where you set these values in a real request.

## Related
- [[ai-ml/00-foundations/02-what-is-a-model|What is a model]] — the general "adjustable function" this specialises
- [[ai-ml/03-ai-engineer/05-prompt-engineering/index|Prompt engineering]] — shaping the input to this mechanism
- [[ai-ml/03-ai-engineer/04-calling-models/index|Calling models]] — where you set these settings in practice
- [[ai-ml/03-ai-engineer/16-local-and-open-models/index|Local and open models]] — the laptop this lab ran on
- [[ai-ml/02-ml-engineer/07-sequence-models-and-nlp/02-transformers-and-attention|Transformers and attention]] — the network inside, in depth

*Source: re-homed from the old `01-fundamentals/03-llms.md`, deepened with the decoding settings from [roadmap.sh ai-engineer](https://roadmap.sh/ai-engineer).*
