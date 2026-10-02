# Cost, caching and latency

> **[Intermediate]** · Covers how to make an AI feature cheap and fast enough to ship: how the bill is worked out from tokens, prompt caching and the prefix rule that governs it, choosing and cascading models, latency as users feel it (time to first token and p95), cutting what you send, and logging cost and latency on every call. The worked example prices the ticket classifier with real list prices, finds a cache-breaking timestamp, and cascades from keyword rules to a model. A demo that costs $2 a query or takes 15 seconds stays a demo.

## Before you start

You can already:

- Read a call's token usage and stream a reply → [[ai-ml/03-ai-engineer/04-calling-models/index|calling models]].
- Explain how a model generates one token at a time, and why tokens set the price → [[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]].
- Score the classifier and its keyword baseline on the golden set → [[ai-ml/03-ai-engineer/12-evals/index|evals]].
- Log each model call with its latency and attempts → [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|reliability and plumbing]].

After this lesson you will be able to:

1. Work out what a call costs from its token counts, and say which part of the bill to cut first.
2. Lay out a prompt so a cache can reuse it, find what is stopping a cache from hitting, and say when caching pays.
3. Build a model cascade, and explain why its check, not its models, sets its quality.
4. Measure latency the way users feel it: time to first token, p50 and p95.

**Study route.** Read §1–4, and stop at the prediction in §3 before reading on. Then §5–7, the lab, and this week's Build.

## The kid version

A copy shop charges you by the page: a little for every page you hand in, and five times as much for every page it writes for you. Lots of your friends hand in the same first fifty pages, so the shop keeps those already copied and charges almost nothing to reuse them, but only if those fifty pages are exactly the same each time. If you write today's date on page one, nothing after it can be reused. For easy jobs, you ask the cheap assistant first, and only go to the expensive expert when the assistant isn't sure. And the shop hands you each page as it comes out of the machine, so you can start reading straight away instead of waiting for the whole stack.

**Where the analogy stops working.** The shop only keeps the copied pages for a few minutes, so reuse has to happen soon. And an assistant who is sure but wrong never sends you to the expert: the cascade is only as good as its way of telling "sure" from "right".

## 1. Why this exists

The ticket classifier works, and the team keeps improving its prompt: a page of labelling policy, then twenty worked examples. The prompt is now 6,000 tokens, and every ticket resends all of it. At 1,000 tickets an hour on a mid-priced model, that is about **$13 an hour**, nearly all of it spent re-reading the same instructions. It's also slow: before writing its one-word answer, the model processes 6,000 tokens. **The capability is the same as the demo's; what changed is that it now runs a thousand times an hour.** The same feature, with the prompt laid out for caching, costs about $2.50 an hour and answers sooner. This lesson is the set of levers that get you from one to the other, and the measurements that tell you which lever to pull.

## Terms used in this lesson

1. **Input tokens**: These are the tokens you send: the system prompt, examples, history, retrieved documents and the question. **Output tokens** are the tokens the model writes back.
2. **Price per million tokens**: This is how providers quote prices, with separate prices for input and output tokens.
3. **Prompt caching**: This means the provider keeps its processed form of the start of your prompt for a short time, so the next request that starts the same way reuses it instead of processing it again.
4. **Prefix**: This is the start of a prompt, from the first token up to some point. Caches match on prefixes: they reuse the longest start that is identical to a cached one.
5. **Cache write and cache read**: A cache write is the first request with a given prefix, which stores it, at a small premium. A cache read is a later request that reuses it, at a large discount.
6. **TTL (time to live)**: This is how long a cache entry lasts without being used. Each read starts the clock again.
7. **Silent invalidator**: This is anything near the front of a prompt that changes on every request, such as a timestamp, a random ID or a JSON object with keys in a different order, so the cache never hits and nothing reports an error.
8. **Model cascade**: This is also known as **model routing**. It means trying a cheap model first and escalating to an expensive one only when the cheap answer fails a check.
9. **Semantic caching**: This means storing whole answers keyed by the meaning of the question, and returning a stored answer when a new question is close enough, without calling the model at all.
10. **Latency**: This is how long the user waits. **TTFT (time to first token)** is how long until the first piece of a streamed reply arrives; **total latency** is how long until the last.
11. **Percentile**: The p50 latency is the time that half of calls finish within, also called the **median**. The p95 is the time that 95% finish within; the slowest 5% take longer.
12. **Batch API**: This is a way to send many requests to be processed within hours instead of seconds, at about half the price.

## 2. How the bill is worked out

**The cost of one call is the number of tokens of each kind multiplied by that kind's price, added up.** The prices are per million tokens, so divide by a million:

$$\text{cost} = \frac{\text{input} \times p_\text{in} + \text{output} \times p_\text{out} + \text{cache writes} \times p_\text{write} + \text{cache reads} \times p_\text{read}}{1{,}000{,}000}$$

Anthropic's list prices on 2026-10-02, in US dollars per million tokens. They're here so the numbers in this lesson are real; prices change often, so check the provider's page before relying on them.

| Model | Input | Output | Cache write (5 min) | Cache read |
|---|---|---|---|---|
| Claude Haiku 4.5 | 1.00 | 5.00 | 1.25 | 0.10 |
| Claude Sonnet 5.5 | 2.00 | 10.00 | 2.50 | 0.20 |
| Claude Opus 5.5 | 4.00 | 20.00 | 5.00 | 0.20 |
| a local model | 0 | 0 | 0 | 0 |

Two things follow from this, and they drive everything else in the lesson.

- **Output costs five times as much as input.** A call to Sonnet with 2,000 input and 500 output tokens costs $0.009. The output is a fifth of the tokens and over half the cost. For generation-heavy features, shorter answers are the first saving.
- **Context is billed on every call.** A long system prompt, many examples, a long chat history or a lot of retrieved text is paid for on every request, not once.

Model choice multiplies all of it: on the table, the largest model costs four times the smallest per token, and some providers' frontier models cost ten or more times their small ones. A local model costs nothing per call, but it's slower on a laptop, and hosting one for real traffic is not free.

## 3. Prompt caching

Before writing its first token, a model runs the whole prompt through its network once, working out for every token the values that attention needs (the [[ai-ml/03-ai-engineer/02-how-llms-work/index|attention]] step from how LLMs work). Those stored values are called the **key-value cache**, and building them is most of the wait before the first token. When thousands of requests start with the same 6,000 tokens, the provider can keep that state and reuse it. **You pay a little extra the first time, and about a tenth of the input price for every reuse within the TTL.** On Anthropic's models a 5-minute cache write costs 1.25× the input price and a read 0.1× (0.05× on Opus 5.5). A 1-hour TTL is available at 2× for the write. The minimum prefix that can be cached is between 512 and 4,096 tokens depending on the model; shorter prompts silently aren't cached.

Providers differ in how you ask for it. Anthropic caches up to a point you mark in the request, or the last block of the prompt if you turn on automatic caching. OpenAI caches long prompts automatically, with no write premium. Ollama keeps the processed prompt of recent requests in memory and reuses whatever start matches. Check your provider's documentation for the exact rules; the prefix rule below is the same everywhere.

### What it saves

The classifier: a 6,000-token prefix of policy and examples, a 150-token ticket and a 100-token answer, 1,000 calls an hour on Sonnet 5.5, each less than 5 minutes after the last.

- **Without caching**, every call pays for 6,150 input tokens: 1,000 × (6,150 × $2 + 100 × $10) / 1,000,000 = **$13.30**.
- **With caching**, the first call writes the prefix ($0.015), and the other 999 read it at $0.20 per million ($1.20 together). The tickets ($0.30) and the answers ($1.00) cost the same as before. Total: **$2.51**, over five times cheaper.

After caching, the answers are 40% of the bill. The biggest cost has moved, so the next saving is somewhere else: shorter output, or a smaller model.

**When it pays.** Caching *n* calls that share a prefix costs one write plus *n* − 1 reads; not caching costs *n* full inputs. Caching wins as soon as

$$n > \frac{p_\text{write} - p_\text{read}}{p_\text{in} - p_\text{read}}$$

For Sonnet's 5-minute cache that is *n* > 1.28, so **from the second call**. With the 1-hour TTL's double-price write it is *n* > 2.1, from the third. Caching loses only when a prefix is used once, or calls are further apart than the TTL.

### The prefix rule: freeze the front, vary the end

**A cache reuses only the identical start of a prompt.** Change one token, and everything after it is processed and paid for again, even if the rest is the same. So order the prompt from what never changes to what changes on every request:

```
┌─ never changes ──────────────────────────────┬─ changes every request ─────────┐
│ tool definitions · system prompt · examples   │ history · retrieved text · question │
└───────────────────────────────────────────────┴─────────────────────────────────┘
                                                ▲ cache point
```

Then hunt the **silent invalidators**: anything that varies and sits before the cache point.

- **A timestamp or "today is…"** at the top of the system prompt. If the model needs the date, put it after the cache point.
- **A random or per-request ID**, or the user's name, in the system prompt.
- **JSON with keys in a different order.** `JSON.stringify` keeps the order keys were added in, so the same data built two ways gives different bytes. Sort the keys.
- **A tool list that changes order** between requests, or is built from an unordered set.
- **A different model.** Caches belong to one model, so a cascade's two models never share one.

**Predict before reading on.** Two requests put `Today is 2026-10-02T09:00:00Z.` and `Today is 2026-10-02T09:00:07Z.` at the very front of a long, identical system prompt. How many characters can a cache reuse? And if the same line moves after the system prompt?

The lab's answer: **27** characters, `Today is 2026-10-02T09:00:0`, and then the seconds differ, so the whole system prompt is processed again. Moved to the end, the shared prefix is the entire system prompt plus 28 characters. Same information, same model, a different bill.

**How to tell it's happening.** Every response reports its cache usage; on Anthropic's API, `usage.cache_read_input_tokens`. If that stays at zero across requests that should share a prefix, something in the prefix is changing. Log two requests' prompts and find where they diverge; the lab's `divergence` function does that.

### Semantic caching: a different idea

Prompt caching makes the model's work cheaper. **Semantic caching** skips the model: it embeds each question, and if a past question was close enough in meaning, it returns that question's stored answer. It suits FAQ-like traffic where many people ask the same thing. It is risky where the right answer changes over time ("what's my balance?") or depends on who is asking, and a threshold that's too loose returns an answer to a different question. Scope it to stable questions, and expire entries.

## 4. Choose the model, then cascade

The biggest cost decision is which model answers. Short classification, extraction and routing usually work well on a small model. Long reasoning, hard generation and multi-step agent work may need a large one. Your evals decide, not the model's reputation: run the golden set on both, and pick the cheapest one that passes the gate.

A **cascade** uses both. The cheap option answers first. A check decides whether to accept its answer; if not, the request goes to the expensive model. Most traffic is easy, so most of it never reaches the expensive model.

The lab cascades from the keyword rules (free) to a pretend big model that is always right ($0.002 a call), and accepts the keyword answer unless it is `other`, which is what the rules say when nothing matched. On the 20 golden tickets:

- **6 tickets are escalated**: t04, t10, t12, t14, t17 and t19, the ones the rules couldn't place. The big model gets all of them right.
- **2 tickets are wrong**: t15 (Italian, labelled *feature* because "addebitato" contains "add") and t20 (*billing* because "Apple Pay" contains "pay"). The rules were sure and wrong, so the check accepted them, and the big model never saw them.
- **Cost: $0.012** for the 20 tickets, against $0.040 for sending every ticket to the big model. **Accuracy: 18/20**, against 20/20.

**The check sets the cascade's quality.** No improvement to the big model can fix t15 or t20, because they never reach it. A weak check either escalates everything (no saving) or accepts confident mistakes (lower quality). Good checks are things you can verify: the output parses, a validator accepts it, the label is one the rules are reliable on, or a confidence score is above a threshold you have checked against the golden set.

Two cautions. A cheaper single option sometimes beats a cascade: the large model with less reasoning effort, or the small model with better examples, may cost less than you think and is simpler to run. And judge cost per *finished task*, not per call: a cheap answer that needs a retry or a human fix isn't cheap.

## 5. Latency: real and perceived

Users feel two different waits:

- **Time to first token** is how long until anything appears. It is mostly the model processing your prompt, plus queueing and network time. Long prompts make it longer; caching makes it shorter, because a cached prefix doesn't have to be processed again.
- **Total latency** is how long until the answer is complete. Output is generated one token at a time, so it grows with the length of the answer.

**Streaming** doesn't make the model faster, but it turns ten seconds of a blank screen into one second and then text appearing, which feels very different. It is the default for anything a person reads as it arrives. For a one-word classification nobody reads, streaming changes nothing; shortening the prompt and capping `max_tokens` do.

To make it actually faster:

- **Use a smaller model.** It's cheaper and faster, so the same choice pays twice.
- **Ask for less output.** Cap `max_tokens` and ask for the short form.
- **Run independent calls at the same time.** Classify 20 tickets with `Promise.all`, not one after another. But send one request first and wait for it, so the rest find the prefix already cached: if all 20 start together, they all miss.
- **Cache the prefix**, which cuts time to first token as well as cost.

**Measure percentiles, not averages.** Ten calls take 900 to 1,200 ms, except one that takes 9,000. The mean is 1,819 ms, which describes no real call. The p50 is 1,000 ms: what a typical user sees. The p95 is 9,000 ms: what your unluckiest users see, and the number to watch. Set targets as "p95 under 3 seconds", not "average under 2".

## 6. Send less

Every token you send is paid for on every call, so the cheapest token is the one you don't send:

- **Retrieve precisely.** In [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG]], a few relevant chunks beat many loosely related ones: cheaper, faster, and usually more accurate, because irrelevant text distracts the model.
- **Keep history short.** A chat resends the whole conversation on every turn. Twenty turns of 200 tokens each send 200 + 400 + … + 4,000 = **42,000** input tokens in total, for 4,000 tokens of conversation. Summarise or drop old turns; since the start stays fixed, keep what's cached at the front.
- **Batch what can wait** at half price, as in [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|reliability and plumbing]] §7: re-running a large eval, nightly enrichment, relabelling.

## 7. Make it visible

You can't cut a cost you can't see. Extend last lesson's log line so every call records the feature, the model, the token counts (input, output, cache writes and reads), the cost, the total time and, for streams, the time to first token. From those records, a dashboard needs only a few numbers per feature and model:

1. **Cost per request**, and per day. A jump means a prompt grew, a cache stopped hitting, or traffic moved to a bigger model.
2. **Cache read share**: of all input tokens, the share read from the cache. On the classifier it should be close to 6,000 out of every 6,150 tokens. A drop to zero means a silent invalidator.
3. **p50 and p95 latency**, and time to first token for streamed features.
4. **Failure and fallback rate**, from last lesson.

Most "why is this so expensive?" questions are answered by one of three things: a cache that stopped hitting, a model bigger than the task needs, or context that grows without limit. You only find out which by measuring.

## Worked example — pricing and tuning the classifier

The prices and the cost formula:

```ts
// pricing.ts — what a call costs, worked out from its token counts.

/** US dollars per million tokens. */
export type Price = { input: number; output: number; cacheWrite: number; cacheRead: number };

/** Token counts for one call. `inputTokens` counts only the input that was neither written to nor read
 *  from the cache, which is how Anthropic reports it; check how your provider splits them. */
export type Usage = { inputTokens: number; outputTokens: number; cacheWriteTokens?: number; cacheReadTokens?: number };

/** Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Prices change: check before relying on them. */
export const PRICES = {
  "claude-haiku-4-5": { input: 1, output: 5, cacheWrite: 1.25, cacheRead: 0.1 },
  "claude-sonnet-5-5": { input: 2, output: 10, cacheWrite: 2.5, cacheRead: 0.2 },
  "claude-opus-5-5": { input: 4, output: 20, cacheWrite: 5, cacheRead: 0.2 },
  local: { input: 0, output: 0, cacheWrite: 0, cacheRead: 0 }, // electricity and your time aren't on the bill
} satisfies Record<string, Price>;

export function cost(usage: Usage, price: Price): number {
  const dollars =
    usage.inputTokens * price.input +
    usage.outputTokens * price.output +
    (usage.cacheWriteTokens ?? 0) * price.cacheWrite +
    (usage.cacheReadTokens ?? 0) * price.cacheRead;
  return dollars / 1_000_000;
}

/** How many calls must share a prefix before caching it is cheaper than not.
 *  Caching n calls costs write + (n − 1) × read; not caching costs n × input. */
export function breakEvenCalls(price: Price): number {
  return Math.floor((price.cacheWrite - price.cacheRead) / (price.input - price.cacheRead)) + 1;
}

/** Batch APIs (Anthropic, OpenAI) charge half price for work that can wait up to 24 hours. */
export function batchPrice(price: Price): Price {
  return { input: price.input / 2, output: price.output / 2, cacheWrite: price.cacheWrite / 2, cacheRead: price.cacheRead / 2 };
}
```

Finding where two prompts diverge, and JSON that always gives the same bytes:

```ts
// prefix.ts — why a prompt cache misses: find where two requests stop being identical.

/** How many leading characters two prompts share. A prompt cache can reuse at most this much. */
export function sharedPrefix(a: string, b: string): number {
  let i = 0;
  while (i < a.length && i < b.length && a[i] === b[i]) i++;
  return i;
}

/** Where they diverge, with a little context, for a log line or a test failure. */
export function divergence(a: string, b: string, context = 20): string {
  const at = sharedPrefix(a, b);
  if (at === a.length && at === b.length) return "identical";
  const show = (s: string) => JSON.stringify(s.slice(Math.max(0, at - context), at + context));
  return `differ at character ${at}: ${show(a)} vs ${show(b)}`;
}

/** JSON with object keys sorted, so the same data always gives the same bytes.
 *  JSON.stringify keeps insertion order, so {b, a} and {a, b} would never share a cache entry. */
export function stableJson(value: unknown): string {
  return JSON.stringify(value, (_key, v) =>
    v && typeof v === "object" && !Array.isArray(v)
      ? Object.fromEntries(Object.entries(v).sort(([x], [y]) => (x < y ? -1 : x > y ? 1 : 0)))
      : v,
  );
}
```

The cascade:

```ts
// cascade.ts — answer with the cheap option when its answer passes a check; pay for the expensive one only when it doesn't.

export type Tier = {
  name: string;
  costUsd: number; // per call, estimated from typical usage
  answer: (input: string) => Promise<string>;
  accept: (answer: string) => boolean; // the check; the last tier's answer is used whatever it says
};

export async function cascade(input: string, tiers: Tier[]): Promise<{ answer: string; by: string; costUsd: number }> {
  let costUsd = 0;
  for (const [i, tier] of tiers.entries()) {
    const answer = await tier.answer(input);
    costUsd += tier.costUsd; // a rejected answer was still paid for
    if (i === tiers.length - 1 || tier.accept(answer)) return { answer, by: tier.name, costUsd };
  }
  throw new Error("a cascade needs at least one tier");
}
```

The per-call record, the summary, and timing a stream:

```ts
// meter.ts — one log record per model call, and the numbers worth putting on a dashboard.
import type { Usage } from "./pricing.ts";

export type CallRecord = {
  feature: string;
  model: string;
  ms: number; // the whole call
  ttftMs?: number; // time to first token, for streamed calls
  usage: Usage;
  costUsd: number;
  ok: boolean;
};

/** Nearest-rank percentile: the smallest value that at least p% of the values are less than or equal to. */
export function percentile(values: number[], p: number): number {
  if (values.length === 0) return NaN;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.max(0, Math.ceil((p / 100) * sorted.length) - 1)];
}

export function summarise(records: CallRecord[]) {
  const ms = records.map((r) => r.ms);
  const sum = (f: (r: CallRecord) => number) => records.reduce((total, r) => total + f(r), 0);
  const read = sum((r) => r.usage.cacheReadTokens ?? 0);
  const allInput = read + sum((r) => r.usage.inputTokens + (r.usage.cacheWriteTokens ?? 0));
  return {
    calls: records.length,
    failed: records.filter((r) => !r.ok).length,
    costUsd: sum((r) => r.costUsd),
    costPerCall: sum((r) => r.costUsd) / records.length,
    meanMs: sum((r) => r.ms) / records.length,
    p50Ms: percentile(ms, 50),
    p95Ms: percentile(ms, 95),
    cacheReadShare: allInput === 0 ? 0 : read / allInput, // of all input tokens, the share read from cache
  };
}

/** Read a stream to the end, timing the first chunk separately: that wait is the one users feel. */
export async function timeStream(chunks: AsyncIterable<string>, now = () => performance.now()) {
  const started = now();
  let ttftMs: number | undefined;
  let text = "";
  for await (const chunk of chunks) {
    ttftMs ??= now() - started;
    text += chunk;
  }
  return { text, ttftMs: ttftMs ?? now() - started, totalMs: now() - started };
}
```

The tests pin down every number in this lesson. The cascade test runs on the golden set from the evals lab:

```ts
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
```

### Against a local model

This script measures prefix caching and time to first token on Ollama. It uses the golden set's twenty labelled tickets as worked examples, so the prompt is about 500 tokens of fixed prefix and a different ticket at the end.

```ts
// live.ts — prefix caching and time to first token, measured on a local model.
// Not run by the lab runner. Needs Ollama; 4 calls, each with a prompt of about 500 tokens.
//   node live.ts               # qwen3.5:4b
//   node live.ts gemma4:latest
import { loadGolden } from "../../../12-evals/labs/typescript/harness.ts";
import { timeStream } from "./meter.ts";

const model = process.argv[2] ?? "qwen3.5:4b";
const examples = loadGolden().map((c) => `Ticket: ${c.ticket}\nLabel: ${c.label}`).join("\n\n");
const system = `Classify support tickets as bug, billing, feature or other. Label by what the team has to do next.
Reply with one word. Examples:\n\n${examples}`;

const body = (prompt: string, stream: boolean) =>
  JSON.stringify({ model, prompt, stream, think: false, options: { temperature: 0, num_predict: 5 } });

/** Ollama reports how many prompt tokens it processed, and how long that took, in nanoseconds. */
async function call(label: string, prompt: string) {
  const res = await fetch("http://127.0.0.1:11434/api/generate", { method: "POST", body: body(prompt, false) });
  const data = await res.json();
  const seconds = (ns: number) => (ns / 1e9).toFixed(1);
  console.log(`${label.padEnd(34)} prompt ${data.prompt_eval_count} tokens in ${seconds(data.prompt_eval_duration)} s, total ${seconds(data.total_duration)} s → ${JSON.stringify(data.response.trim())}`);
}

async function* chunks(prompt: string) {
  const res = await fetch("http://127.0.0.1:11434/api/generate", { method: "POST", body: body(prompt, true) });
  const decoder = new TextDecoder();
  let buffered = "";
  for await (const bytes of res.body!) {
    buffered += decoder.decode(bytes, { stream: true });
    const lines = buffered.split("\n");
    buffered = lines.pop()!;
    for (const line of lines.filter(Boolean)) yield JSON.parse(line).response as string;
  }
}

await call("1. cold: the prefix is new", `${system}\n\nTicket: The app crashes on start.\nLabel:`);
await call("2. same prefix, new question", `${system}\n\nTicket: I was charged twice.\nLabel:`);
await call("3. timestamp at the front", `Now: ${new Date().toISOString()}\n${system}\n\nTicket: Add dark mode.\nLabel:`);
const { ttftMs, totalMs } = await timeStream(chunks(`${system}\n\nTicket: Where is my invoice?\nLabel:`));
console.log(`4. streamed, same prefix: first token after ${(ttftMs / 1000).toFixed(1)} s, finished after ${(totalMs / 1000).toFixed(1)} s`);
```

**Not measured yet.** Write your predictions first. Call 2 shares call 1's prefix: will Ollama report fewer prompt tokens processed, or only a shorter time? Call 3 puts a timestamp at the front: how will its prompt time compare with call 2's? For call 4, how much of the total time comes before the first token? Then run it on a quiet laptop (check `uptime` and `free -h` first) and record the output here.

**Lab:** the code is in [`ai-ml/03-ai-engineer/14-cost-caching-and-latency/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/14-cost-caching-and-latency/labs/typescript). From the vault root, `python3 labs/run.py cost-caching-and-latency/typescript` runs the tests and checks this page still shows the same code. `live.ts` needs Ollama, so run it yourself from the lab folder with `node live.ts`.

## Common pitfalls

1. **A cache that never hits.** A timestamp, ID or unsorted JSON near the front. Check the cache-read count; if it's zero, compare two prompts and find where they diverge.
2. **A prefix below the minimum.** Under 512 to 4,096 tokens, depending on the model, nothing is cached and nothing says so.
3. **Firing parallel requests at a cold cache.** They all miss and all pay to write. Warm the cache with one request first.
4. **Ignoring output cost.** At five times the input price, long answers often cost more than long prompts, especially once the prompt is cached.
5. **A cascade with a weak check.** It accepts confident mistakes or escalates everything. Test the check on the golden set, like any other component.
6. **Averages instead of percentiles.** The mean hides the slow calls your unluckiest users get.
7. **A semantic cache that serves stale or wrong answers.** Scope it to stable questions, set a tight similarity threshold, and expire entries.
8. **Optimising without measuring.** Log tokens, cost and latency per call before deciding which lever to pull.

## Check your understanding

1. A call sends 3,000 tokens and receives 600 on Sonnet 5.5. What does it cost, and which part is bigger?
2. Why does putting the current time at the start of a system prompt make caching useless, and where should it go instead?
3. A prefix is reused 10 times within 5 minutes. Is caching it worth it? What if it's used once an hour?
4. In the lab's cascade, why can't a better big model fix t15 or t20? What would?
5. What does streaming improve, and what doesn't it improve?
6. Ten calls have a mean latency of 1.8 s and a p50 of 1.0 s. What does that tell you, and which number would you set a target on?
7. You start 20 classifications at once with a shared, uncached prefix. What happens to the cache, and what would you do instead?

<details>
<summary>Answers — after your attempt</summary>

1. (3,000 × $2 + 600 × $10) / 1,000,000 = $0.006 + $0.006 = $0.012. Input and output cost the same here, even though the output is a sixth of the tokens.
2. The cache reuses only the identical start of a prompt. A timestamp that changes every request makes the start different every time, so nothing after it can be reused. Put it after the cached part, near the question.
3. Yes: with a 5-minute TTL, caching pays from the second call, so 10 reuses is a large saving. Once an hour, the 5-minute entry has expired before each call, so every call pays the write premium and gets nothing back. The 1-hour TTL would pay from the third call within the hour, so it wouldn't help either.
4. The check accepted the keyword answers for t15 and t20, so they never reached the big model. A better check would: for example, treating *feature* and *billing* from the rules as reliable only for English tickets, or only when one specific word matched.
5. It improves the time until the user sees something, which is what people feel. It doesn't reduce the total time, the token count or the cost.
6. Some calls are much slower than the typical one, and they pull the mean up. Set the target on the p95 (and watch the p50 for the typical case), because the mean describes no real call.
7. They all start before any of them has written the cache, so all 20 miss and all 20 pay to process the prefix. Send one, wait for it, then send the other 19, which can read the cache.

</details>

## Practice — independent task

**Week 4's Build, second half: per-request cost and latency logging in your flagship.**

1. Extend the log line from [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|reliability and plumbing]] with the token counts (including cache reads and writes if your provider reports them), the cost from your provider's current prices, and time to first token for streamed calls.
2. Run your golden set and summarise the log: cost per request, cost per 1,000 requests, p50 and p95 latency, and cache read share.
3. Lay out your prompt for caching. If your provider reports cache reads, show the share going up; if you're on a local model, use `live.ts` as a template to compare prompt processing time before and after.
4. Write down one change you would make to cut cost or latency, with the number you expect it to move. You don't have to make it this week.

Then try exercise 14 in [[ai-ml/03-ai-engineer/19-practice-exercises|practice exercises]]: a cascade on your own classifier, with a two-row table of accuracy and cost.

**Done when:** you can quote your feature's cost per 1,000 requests and its p95 latency from your own logs, and you've found and removed one thing that changes before the cache point (or shown there isn't one).

## Tradeoffs, limits and extensions

- **Effort and reasoning settings.** Many models let you set how much they reason before answering. Lower effort on a strong model can be cheaper than a cascade and simpler to run; measure both on the golden set.
- **Fine-tuning a small model** for a narrow task can replace a long prompt of examples, cutting cost and latency per call, at the price of a training pipeline → [[ai-ml/03-ai-engineer/15-fine-tuning-applied|fine-tuning applied]].
- **Running models yourself.** Per-token cost becomes per-hour hardware cost, and you take on capacity planning → [[ai-ml/03-ai-engineer/16-local-and-open-models/index|local and open models]].
- **Prices change.** Keep prices in one place in your code, with the date you copied them, and recheck them when a provider releases new models.

## Before moving on

You can price a call from its usage, lay out a prompt so it caches and find what breaks the cache, reason about when caching and cascades pay, and measure latency with time to first token and percentiles.

**Recap.** The bill is tokens times prices, with output about five times input, and context paid for on every call. Cache the stable prefix: freeze the front, vary the end, and hunt silent invalidators; caching pays from the second call within the TTL. Pick the cheapest model that passes your evals, and cascade only with a check you have tested, because the check sets the cascade's quality. Stream to cut the wait users feel; use smaller models, shorter output, parallel calls and caching to cut the real wait. Watch p95, not the mean. Send less: precise retrieval, short history, batch what can wait. Log tokens, cost and latency on every call.

**Next.** Week 5: [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|tools and MCP]] and [[ai-ml/03-ai-engineer/08-agents/index|agents]]. Agents make many calls per task, so everything in this lesson, especially history length and caching, matters more there.

## Related
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|Reliability and plumbing]] — the log line extended here, and the gateway that can do caching and cost tracking
- [[ai-ml/03-ai-engineer/04-calling-models/index|Calling models]] — usage, streaming and `max_tokens`
- [[ai-ml/03-ai-engineer/02-how-llms-work/index|How LLMs work]] — tokens, attention, and generating one token at a time
- [[ai-ml/03-ai-engineer/12-evals/index|Evals]] — how to tell whether a cheaper option is good enough
- [[ai-ml/03-ai-engineer/06-rag-and-embeddings|RAG and embeddings]] — precise retrieval as a cost lever
- [[ai-ml/03-ai-engineer/03-the-model-landscape|The model landscape]] — choosing models by task

*Source: Part II of the AI-engineer track. Prices from Anthropic's list on 2026-10-02.*
