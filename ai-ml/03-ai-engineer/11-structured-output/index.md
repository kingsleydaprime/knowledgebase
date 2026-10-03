# Structured Output

> **[Intermediate]** · How to get typed, validated data back from a model instead of prose: the three ways to ask for JSON, why valid JSON can still be wrong, and the retry loop that makes a model usable as a function in your code. The worked example extracts an invoice with a local model, asking with a prompt only and then with a schema. The numbers were measured on 2026-10-02.

## Before you start

You can already:

- Make a model call and read `finish_reason` → [[ai-ml/03-ai-engineer/04-calling-models/index|calling models]].
- Explain how decoding picks one token from probabilities → [[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]]. §3 builds on this.
- Read a JSON object and say what type each field is.

After this lesson you will be able to:

1. Choose between prompt-only JSON, JSON mode and schema-constrained decoding, and say what each one guarantees.
2. Write a schema that models fill in reliably: flat, with enums and machine-friendly units.
3. Separate three checks: is it JSON, is it the right shape, is it plausible.
4. Write a retry loop that feeds the specific errors back, stops on refusals and treats truncation as a retry.

**Study route.** Read §1–6. Before running `live.ts`, predict which mode will produce more failures, and what kind.

## The kid version

Imagine asking a friend to fill in a form for you, but instead of a form you just say "write down the name, the date and the total". They write a lovely paragraph. Now you have to hunt through it for the bits you need. So next time you give them a real form, with a box for each thing and "write the date like 2026-10-15" printed beside the box. Much easier. But even with a perfect form, they could still write the wrong total in the total box. So you add the numbers up yourself before you believe it.

**Where the analogy stops working.** With the strongest method, the model can't write outside the boxes at all. The rule is applied while it's writing, one token at a time, so a wrongly shaped answer can't even be produced. A friend could always scribble in the margin.

## 1. Why this exists

You ask a model to "return the invoice as JSON" and call `JSON.parse` on the reply. It works in every test. In production, one reply starts with "Sure! Here's the data:", another wraps the JSON in a Markdown fence, another writes the total as `"£655.50"` instead of a number, and one runs out of tokens halfway through. Each one throws, or worse, parses into something your code wasn't expecting. **A string is not an interface.** Structured output is what turns "a model" into a function you can call, like `extract(text) → Invoice` or `classify(ticket) → Priority`.

## Terms used in this lesson

1. **JSON (JavaScript Object Notation)**: The letters stand for those words. It is the text format for objects, arrays, strings, numbers and booleans that almost every API uses.
2. **Schema**: This is a description of the shape data must have: which fields, what types, which are required. **JSON Schema** is the standard format for writing one.
3. **Prompt-only JSON**: This means asking for JSON in the instructions and parsing whatever comes back. Nothing enforces it.
4. **JSON mode**: This is a provider setting that guarantees the reply is syntactically valid JSON, but not that it has your fields.
5. **Schema-constrained decoding**: This is also known as **structured outputs** or **strict mode**. The server forces generation to follow your schema, so the reply always has your shape.
6. **Validation**: This means checking data against rules in your own code before using it.
7. **Invariant**: This is a rule that must always be true of correct data, like "the line items add up to the total". A schema usually can't express it.
8. **Enum (enumeration)**: This is a field that must be one of a fixed list of values, such as `"GBP" | "USD" | "EUR" | "NGN"`.
9. **ISO 8601**: This is the international standard date format, `YYYY-MM-DD`, such as `2026-10-15`.
10. **Refusal**: This is when a model declines a request, usually for safety reasons. Its reply won't match your schema.
11. **Zod and Pydantic**: These are libraries, for TypeScript and Python, that define a schema once and give you a validator, a type and a JSON Schema from it.

## 2. Three ways to ask, from weakest to strongest

**1. Prompt-only.** Ask for JSON in the prompt and parse the reply yourself. The model can wrap it in a fence, add a preamble, leave a trailing comma or invent fields. Use this only when the provider offers nothing better, and always with the retry loop from §5.

**2. JSON mode.** The provider guarantees valid JSON: no fence, no preamble. It does **not** guarantee your fields or types. The "it isn't even JSON" failure disappears, but you still validate everything.

**3. Schema-constrained decoding.** You send a JSON Schema, and the reply always matches it: the right fields, the right types, required keys present, enum values from your list. This is what "strict" tool calling uses too. Ollama takes the schema in a `format` field; hosted providers call it structured outputs or `response_format` with a schema. In TypeScript SDKs it looks like this:

```ts
// ILLUSTRATIVE — the idea is durable; the exact API isn't. Check your installed SDK's docs.
// (The AI SDK's older `generateObject` was replaced by `generateText` + `Output.object`.)
import { generateText, Output } from "ai";
import { z } from "zod";

const Invoice = z.object({
  vendor: z.string(),
  total_cents: z.number().int(),
  due_date: z.string().date(),
  line_items: z.array(z.object({ description: z.string(), amount_cents: z.number().int() })),
});

const { output } = await generateText({ model, prompt: invoiceText, output: Output.object({ schema: Invoice }) });
//      ^ typed as z.infer<typeof Invoice>, already validated
```

One schema does three jobs here: it constrains the model, it documents the contract, and it gives you a runtime validator and a static type.

## 3. How constrained decoding works

Recall from [[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]]: at every step, the model scores every token, and decoding picks one. Constrained decoding adds one more step before the pick: **any token that would break the schema has its probability set to zero**. After `{"currency": "` only tokens that can start `GBP`, `USD`, `EUR` or `NGN` remain. After `"total_cents": ` only digits remain. An invalid document can't be generated at all, because at every step the only tokens left are ones that keep it valid.

That also shows the limit. The constraint controls **which** tokens are allowed, not **which allowed token is true**. If the model's best guess for the total is `65500`, that is a perfectly valid integer.

## 4. Valid JSON is not correct data

Three separate checks, in order:

1. **Is it JSON?** Parsing answers this. Constrained decoding and JSON mode make it always yes.
2. **Is it the right shape?** Fields, types, enums. Constrained decoding makes it yes for everything the schema can express. Many constrained decoders ignore `minLength`, `maximum`, `pattern` and `format`, so check those yourself.
3. **Is it plausible?** Do the items add up to the total? Is the due date after the issue date? Does the vendor appear in the document? **Only your code can check this**, whichever mode you use.

Schema conformance is a guarantee about syntax, not about truth. A hallucinated vendor name is a perfectly valid string.

## 5. The retry loop

When a check fails, don't just call again with the same messages; you'll often get the same mistake. Add the bad reply and a message saying **exactly** what was wrong, and ask again:

> Your reply had these problems: line items add up to 65550 cents but total_cents is 65500. Return the corrected JSON object only.

Three cases need different handling:

- **Refusal.** Stop. The model declined, and asking again won't change that. Check for it *before* parsing.
- **Truncation** (`finish_reason: "length"`). The JSON is cut off mid-object. Don't parse it. Retry, and size `max_tokens` for the whole object.
- **Cap the attempts.** Two or three. If a schema keeps failing, the schema is usually too complicated, or the model too small.

## 6. Schemas models fill in well

- **Keep them flat and small.** Deep nesting and many optional fields raise the error rate and the token cost. Ask only for the fields your code uses.
- **Use enums for categories.** `"low" | "medium" | "high"` stops the "the model said `Medium` but my code checks `med`" bug.
- **Ask for machine-friendly units.** Integer cents instead of money as decimals, which suffer rounding errors. ISO 8601 dates instead of "next Tuesday". An explicit `null` instead of a missing key.
- **Set `additionalProperties: false`.** Strict modes usually require it; without it, the model may add extra keys. Typed SDK helpers set it for you.
- **Name fields clearly and add `description`s.** The model reads the schema; `amount_cents` tells it more than `amt`.

### Structured output and tool calling are the same machinery

Tool calling ([[ai-ml/03-ai-engineer/07-tools-and-mcp/index|tools and MCP]]) is structured output aimed at a function's arguments instead of an answer. "Strict" tools use the same constrained decoding. If your stack only offers structured data through tools, define one tool whose parameters are your schema and force the model to call it.

## Worked example — extracting an invoice

The contract: a JSON Schema to send, and a validator that checks the same things plus what the schema can't (the date format and the sum).

```ts
// invoice.ts — the contract: one JSON Schema for the model, and a validator for your code.
// In a real project, Zod (TS) or Pydantic (Python) gives you both, plus a static type, from one
// definition. Writing them by hand once shows what those libraries check for you.

export type Invoice = {
  vendor: string;
  invoice_number: string;
  currency: "GBP" | "USD" | "EUR" | "NGN";
  due_date: string; // ISO 8601, e.g. "2026-10-15"
  line_items: { description: string; amount_cents: number }[];
  total_cents: number;
};

const CURRENCIES = ["GBP", "USD", "EUR", "NGN"];

/** Sent to the model for schema-constrained decoding. Flat, enums for categories, integer cents. */
export const invoiceSchema = {
  type: "object",
  properties: {
    vendor: { type: "string" },
    invoice_number: { type: "string" },
    currency: { type: "string", enum: CURRENCIES },
    due_date: { type: "string", description: "ISO 8601 date, YYYY-MM-DD" },
    line_items: {
      type: "array",
      items: {
        type: "object",
        properties: { description: { type: "string" }, amount_cents: { type: "integer" } },
        required: ["description", "amount_cents"],
        additionalProperties: false,
      },
    },
    total_cents: { type: "integer" },
  },
  required: ["vendor", "invoice_number", "currency", "due_date", "line_items", "total_cents"],
  additionalProperties: false,
} as const;

export type Checked<T> = { ok: true; value: T } | { ok: false; errors: string[] };

/** Does it have the right shape? Checks what the schema says, plus what schemas often can't (the date format). */
export function validateInvoice(value: unknown): Checked<Invoice> {
  const errors: string[] = [];
  if (typeof value !== "object" || value === null || Array.isArray(value)) return { ok: false, errors: ["expected a JSON object"] };
  const v = value as Record<string, unknown>;
  const allowed = new Set(Object.keys(invoiceSchema.properties));
  for (const key of Object.keys(v)) if (!allowed.has(key)) errors.push(`unexpected field "${key}"`);
  for (const key of invoiceSchema.required) if (!(key in v)) errors.push(`missing field "${key}"`);

  for (const key of ["vendor", "invoice_number"]) if (key in v && typeof v[key] !== "string") errors.push(`"${key}" must be a string`);
  if ("currency" in v && !CURRENCIES.includes(v.currency as string)) errors.push(`"currency" must be one of ${CURRENCIES.join(", ")}`);
  if ("due_date" in v && !(typeof v.due_date === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v.due_date) && !isNaN(Date.parse(v.due_date))))
    errors.push(`"due_date" must be a date like 2026-10-15`);
  if ("total_cents" in v && !Number.isInteger(v.total_cents)) errors.push(`"total_cents" must be a whole number of cents`);
  if ("line_items" in v) {
    if (!Array.isArray(v.line_items)) errors.push(`"line_items" must be an array`);
    else v.line_items.forEach((item, i) => {
      if (typeof item?.description !== "string") errors.push(`line_items[${i}].description must be a string`);
      if (!Number.isInteger(item?.amount_cents)) errors.push(`line_items[${i}].amount_cents must be a whole number of cents`);
    });
  }
  return errors.length ? { ok: false, errors } : { ok: true, value: v as Invoice };
}

/** Is it plausible? A schema can't say "the items add up to the total"; only your code can. */
export function checkInvariants(invoice: Invoice): Checked<Invoice> {
  const sum = invoice.line_items.reduce((total, item) => total + item.amount_cents, 0);
  return sum === invoice.total_cents
    ? { ok: true, value: invoice }
    : { ok: false, errors: [`line items add up to ${sum} cents but total_cents is ${invoice.total_cents}`] };
}
```

The extractor: parse, validate, check invariants, and retry with the errors as feedback.

```ts
// extract.ts — turn a model's reply into a validated Invoice, retrying with the errors as feedback.
import { checkInvariants, type Invoice, validateInvoice } from "./invoice.ts";

export type Message = { role: "system" | "user" | "assistant"; content: string };
export type Reply = { text: string; finishReason: "stop" | "length" | "other"; refusal?: string };
export type Model = (messages: Message[]) => Promise<Reply>;

/** Models asked for JSON often wrap it: "Sure! ```json {...} ```". Take the outermost {...}. */
export function parseModelJson(text: string): unknown {
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start === -1 || end < start) throw new SyntaxError("no JSON object in the reply");
  return JSON.parse(text.slice(start, end + 1));
}

export type Outcome =
  | { ok: true; invoice: Invoice; attempts: number }
  | { ok: false; reason: "refused" | "invalid"; detail: string; attempts: number };

const SYSTEM = "Extract the invoice as JSON with fields vendor, invoice_number, currency (GBP, USD, EUR or NGN), " +
  "due_date (YYYY-MM-DD), line_items (description, amount_cents) and total_cents. Amounts are integers in cents. " +
  "Reply with only the JSON object.";

export async function extractInvoice(model: Model, document: string, maxAttempts = 3): Promise<Outcome> {
  const messages: Message[] = [{ role: "system", content: SYSTEM }, { role: "user", content: document }];
  let problem = "";
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const reply = await model(messages);
    // A refusal won't match the schema, and retrying won't change it: check it before parsing.
    if (reply.refusal) return { ok: false, reason: "refused", detail: reply.refusal, attempts: attempt };

    if (reply.finishReason === "length") {
      problem = "your reply was cut off before the JSON was complete; reply with a shorter, complete object";
    } else {
      try {
        const shape = validateInvoice(parseModelJson(reply.text));
        const checked = shape.ok ? checkInvariants(shape.value) : shape;
        if (checked.ok) return { ok: true, invoice: checked.value, attempts: attempt };
        problem = checked.errors.join("; ");
      } catch (e) {
        problem = `that was not valid JSON (${(e as Error).message})`;
      }
    }
    // Feed back exactly what was wrong; a bare "try again" usually gets the same mistake.
    messages.push({ role: "assistant", content: reply.text });
    messages.push({ role: "user", content: `Your reply had these problems: ${problem}. Return the corrected JSON object only.` });
  }
  return { ok: false, reason: "invalid", detail: problem, attempts: maxAttempts };
}
```

The tests use a scripted fake model, so every path — fences, wrong shape, wrong sum, truncation, refusal, the retry cap — runs in milliseconds:

```ts
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
```

And the live comparison against a local model, three runs of each mode at temperature 0.8:

```ts
// live.ts — prompt-only JSON vs schema-constrained JSON from a local model. Not run by the lab runner.
//   node live.ts            # 3 runs of each, qwen3.5:4b
//   node live.ts 5 gemma4:latest
import { extractInvoice, type Message, parseModelJson } from "./extract.ts";
import { checkInvariants, invoiceSchema, validateInvoice } from "./invoice.ts";

const runs = Number(process.argv[2] ?? 3);
const model = process.argv[3] ?? "qwen3.5:4b";
const document = `From: Brightline Studio Ltd, 4 Canal Street, Manchester
Invoice INV-2041 — payment due 15 October 2026
Logo design ............ £450.00
Two revisions .......... £120.00
Brand guide (PDF) ...... £85.50
TOTAL DUE: £655.50`;

/** Ollama's native chat endpoint: `format` takes a JSON Schema and constrains decoding to it. */
async function ask(messages: Message[], schema?: object) {
  const res = await fetch("http://127.0.0.1:11434/api/chat", {
    method: "POST",
    body: JSON.stringify({ model, messages, stream: false, think: false, format: schema, options: { temperature: 0.8 } }),
  });
  const data = await res.json();
  return { text: data.message.content as string, finishReason: data.done_reason === "length" ? "length" as const : "stop" as const };
}

function grade(text: string): string {
  try {
    const shape = validateInvoice(parseModelJson(text));
    if (!shape.ok) return `wrong shape: ${shape.errors[0]}`;
    const sums = checkInvariants(shape.value);
    return sums.ok ? "valid" : `valid shape, wrong numbers: ${sums.errors[0]}`;
  } catch (e) {
    return `not JSON: ${(e as Error).message}`;
  }
}

for (const [label, schema] of [["prompt only", undefined], ["schema-constrained", invoiceSchema]] as const) {
  console.log(`\n${label}:`);
  for (let i = 1; i <= runs; i++) {
    const started = performance.now();
    const outcome = await extractInvoice(async (messages) => {
      const reply = await ask(messages, schema);
      console.log(`  run ${i}: ${grade(reply.text)}`);
      return reply;
    }, document);
    console.log(`  run ${i} → ${outcome.ok ? "accepted" : "rejected"} after ${outcome.attempts} call(s), ${((performance.now() - started) / 1000).toFixed(0)} s`);
  }
}
```

What it printed on the 16 GB laptop with `qwen3.5:4b`:

```
$ node live.ts
prompt only:
  run 1: wrong shape: "vendor" must be a string
  run 1: valid
  run 1 → accepted after 2 call(s), 115 s
  run 2: valid
  run 2 → accepted after 1 call(s), 55 s
  run 3: wrong shape: "vendor" must be a string
  run 3: valid
  run 3 → accepted after 2 call(s), 114 s

schema-constrained:
  run 1: valid
  run 1 → accepted after 1 call(s), 51 s
  run 2: valid
  run 2 → accepted after 1 call(s), 51 s
  run 3: valid
  run 3 → accepted after 1 call(s), 51 s
```

Read it in three parts.

- **Prompt-only failed on the shape two times out of three.** The retry with the error fed back fixed it each time, so the loop from §5 did its job, but each fix cost a whole second call. That's about twice the time and twice the tokens.
- **The schema removed that failure entirely.** Every run was right first time, and the time per run was steady at 51 s.
- **Every final answer added up.** The invariant check never fired. That's this document and this model, not a guarantee: a less tidy invoice, or a smaller model, will eventually produce a total that doesn't match the items, and no schema will notice.

Three runs each is a small sample. It's enough to see the pattern on one document, not to quote a failure rate. Week 3's evals are where you measure that properly.

**Lab:** these files are in [`ai-ml/03-ai-engineer/11-structured-output/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/11-structured-output/labs/typescript). From the vault root, `python3 labs/run.py structured-output/typescript` runs the tests and checks this page still shows the same code. `live.ts` needs Ollama running and takes several minutes on a laptop, so run it yourself from the lab folder with `node live.ts`.

## Common pitfalls

1. **`JSON.parse` on the raw reply, with no `try`.** One preamble or fence and production throws.
2. **Trusting schema-valid output.** The shape is guaranteed; the values aren't. Check the invariants.
3. **Retrying with "try again".** Feed back the specific errors, or you'll get the same mistake.
4. **Retrying a refusal.** It costs money and changes nothing. Detect it and handle it separately.
5. **Parsing a truncated reply.** Check `finish_reason` first.
6. **Money as decimals, dates as prose.** Ask for integer cents and ISO 8601 dates.
7. **A schema with everything in it.** Every extra field is another chance to be wrong. Ask for what the code uses.

## Check your understanding

1. What does JSON mode guarantee that prompt-only doesn't? What does it still not guarantee?
2. How can constrained decoding make an invalid document impossible to generate? Use the word "token".
3. A schema-constrained reply has `total_cents: 65500`, but the items add up to 65550. Which of the three checks catches it, and why couldn't the schema?
4. Why should a retry include the specific error, rather than just repeating the request?
5. Why is a refusal handled differently from a validation failure?
6. Why ask for `amount_cents: 45000` rather than `amount: 450.00`?

<details>
<summary>Answers — after your attempt</summary>

1. That the reply is syntactically valid JSON, with no fence, preamble or trailing comma. It doesn't guarantee your fields, types or enum values.
2. At each step, before a token is picked, every token that would break the schema has its probability set to zero. Only tokens that keep the document valid can be chosen, so every complete document is valid.
3. The third, the plausibility check in your own code. JSON Schema describes the shape of each field, not relationships between fields, so it can't say "these must add up to that".
4. A bare repeat gives the model the same context, so it tends to make the same choice. The error message adds new information, which changes the probabilities for the next attempt.
5. A refusal is the model declining the task. Repeating the same request doesn't change that, so a retry only wastes time and money. A validation failure is a mistake the model can often fix when told what it was.
6. Integers are exact. Decimal money in floating point suffers rounding errors (0.1 + 0.2 ≠ 0.3), and models also get creative with decimal formats, such as `"£450.00"` or `450`.

</details>

## Practice — independent task

**Extract something from your flagship.** Pick one thing the flagship's AI feature should return as data, not prose.

1. Write its schema with the rules from §6: flat, enums, machine units, `additionalProperties: false`.
2. Write one invariant that the schema can't express, and the check for it.
3. Adapt `extractInvoice` to it, and write tests with a scripted fake for: good first try, wrong shape, invariant broken, truncation, refusal.
4. Run it against the local model five times with the schema and five without. Record what failed.

**Done when:** the tests pass without a model, you have a five-and-five table of real results, and you can say which failures the schema removed and which it couldn't.

## Before moving on

You can say what each of the three modes guarantees, name the three checks in order, and explain why a retry includes the error.

**Recap.** Ask for structured output with the strongest mode available: schema-constrained, then JSON mode, then prompt-only. Constrained decoding zeroes out invalid tokens, so the shape is guaranteed, but the values aren't. Check JSON, then shape, then invariants. Retry with the specific errors; stop on refusals; treat truncation as a retry. Keep schemas flat, with enums and machine units.

**Next.** [[ai-ml/03-ai-engineer/05-prompt-engineering/index|Prompt engineering]] — the rest of week 2.

## Related
- [[ai-ml/03-ai-engineer/11-structured-output/in-other-languages|Structured output in other languages]] — Pydantic, Go struct tags, Jackson, serde and System.Text.Json
- [[ai-ml/03-ai-engineer/04-calling-models/index|Calling models]] — where the schema goes on the request
- [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|Tools and MCP]] — the same schema machinery, aimed at function arguments
- [[ai-ml/03-ai-engineer/12-evals/index|Evals]] — structural checks are the cheapest, most reliable eval
- [[ai-ml/03-ai-engineer/10-safety-and-production/index|Safety and production]] — refusals, and containing what a model outputs

*Source: Part II of the AI-engineer track. SDK shapes change fast; check them against current docs.*
