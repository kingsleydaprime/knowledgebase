# Calling Models

> **[Beginner]** · Covers what a model call actually sends and receives: the messages format, streaming, finish reasons, errors, and why your app should talk to a model through a port rather than through one provider's SDK. The worked example builds a small provider-neutral client and runs it against a local model. The numbers were measured on 2026-10-02.

## Before you start

You can already:

- Explain tokens, the context window and temperature → [[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]].
- Call an HTTP API with `fetch` and read JSON.
- Say what a port and an adapter are → [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/index|hexagonal and clean architecture]]. This helps with §6 but isn't required.

After this lesson you will be able to:

1. Write a chat request by hand: roles, messages, settings. Then read the response: text, finish reason, token usage.
2. Explain why a model has no memory between calls, and how chat apps fake it.
3. Explain how streaming works on the wire, and why a stream parser must cope with chunks that split lines.
4. Put model calls behind a port, so tests use a fake and switching providers touches one file.

**Study route.** Read §1–6, then run the lab. Before you run `live.ts`, guess how long the first token and the whole reply will take.

## The kid version

Imagine sending letters to a very clever pen pal who has no memory at all. Every letter you send, they read, write back, and then forget you completely. So if you want them to remember what you talked about, you have to copy out the whole conversation so far into every new letter. Sometimes they reply word by word on postcards so you can start reading straight away, instead of waiting for the full letter. And every pen-pal company has its own envelope rules. So you write your letters on your own standard paper, and a helper puts each one in whichever envelope that company wants.

**Where the analogy stops working.** Copying the whole conversation into every letter costs real money, because you pay for every token you send, every time. A long chat gets more expensive with each message, and eventually it no longer fits in the context window at all.

## 1. Why this exists

Your first AI feature imports one provider's SDK directly in the route handler. It works. Then three things happen in a month. Tests need a real key and network, so they're slow and cost money, and nobody runs them. The provider has an outage, and switching to another means editing twelve files. A user complains that the chat "forgot" what they said, and you find the code was sending only the latest message. **None of these is a model problem. They're all about how you call the model** — and they're cheap to get right on day one and expensive later.

## Terms used in this lesson

1. **API (application programming interface)**: The letters stand for those three words. Here it means the HTTP endpoints a model provider exposes.
2. **Message**: This is one entry in a conversation, with a **role** and some **content**.
3. **Role**: This says who a message is from. `system` holds standing instructions, `user` is the person, and `assistant` is the model's earlier replies.
4. **Stateless**: This means the server keeps nothing between requests. Every model call must contain everything the model needs to see.
5. **Finish reason**: This is the field in the response that says why generation stopped. `stop` means it finished naturally; `length` means it hit max tokens and the reply was cut off.
6. **Usage**: This is the response field that counts input and output tokens. It is what you're billed for.
7. **Streaming**: This means receiving the reply in pieces as it's generated, instead of all at once at the end.
8. **SSE (server-sent events)**: The letters stand for those three words. It is a simple format for a server to send a stream of messages over one HTTP response: lines starting `data:`, with a blank line between messages.
9. **Time to first token**: This is how long the user waits before any text appears. Streaming makes this small even when the whole reply takes a long time.
10. **SDK (software development kit)**: The letters stand for those three words. It is a library that wraps an API so you call functions instead of building HTTP requests.
11. **OpenAI-compatible**: This describes a server that accepts the same request format as OpenAI's chat completions endpoint. Ollama, vLLM, LM Studio and most gateways are OpenAI-compatible.
12. **Gateway**: This is a service that sits in front of many providers behind one API and one key, so you can switch models by changing a string.
13. **Port**: This is an interface your application defines for something it needs, such as "a chat model". The rest of the app depends only on the port.
14. **Adapter**: This is a class that implements a port for one real thing, such as one provider's HTTP API.

## 2. The messages format

Almost every provider's chat API takes a list of **messages**, each with a **role**:

```jsonc
{
  "model": "…",
  "messages": [
    { "role": "system",    "content": "You are a terse code reviewer." },  // standing instructions
    { "role": "user",      "content": "Review this function: …" },          // the request
    { "role": "assistant", "content": "…" }                                  // earlier model replies
  ],
  "temperature": 0,
  "max_tokens": 500
}
```

- **system** holds stable instructions: role, tone, constraints. See [[ai-ml/03-ai-engineer/05-prompt-engineering/index|prompt engineering]].
- **user** and **assistant** alternate to make up the conversation.
- The decoding settings from [[ai-ml/03-ai-engineer/02-how-llms-work/index|how LLMs work]] (`temperature`, `top_p`, `max_tokens`, penalties) go in the same request.

The response gives you more than the text. Read these three fields every time:

```jsonc
{
  "choices": [{ "message": { "role": "assistant", "content": "…" }, "finish_reason": "stop" }],
  "usage": { "prompt_tokens": 412, "completion_tokens": 88 }
}
```

`finish_reason: "length"` means the reply was **cut off**. If you're about to parse it as JSON, it's probably broken. `usage` is what you log for cost → [[ai-ml/03-ai-engineer/14-cost-caching-and-latency/index|cost, caching and latency]].

Providers differ in the details. Anthropic's Messages API, for example, takes `system` as a top-level field rather than a message, requires `max_tokens`, and returns content as a list of blocks. That's exactly why §6 puts an adapter between your code and any one format.

## 3. The model has no memory

The model is **stateless**. Each request is processed on its own, and nothing is kept afterwards. A chat that "remembers" is the *application* resending every earlier message on every call.

Three consequences follow. Each turn costs more than the last, because the input grows. A long conversation eventually doesn't fit in the context window, so apps trim or summarise old turns. And if your code forgets to resend history, the model genuinely has no idea what was said. The `Conversation` class in the lab, and its test, show this directly.

## 4. Streaming

Without streaming, the user stares at nothing until the whole reply is generated. With `"stream": true`, the server sends each token as soon as it exists, as SSE:

```
data: {"choices":[{"delta":{"content":"Hel"}}]}

data: {"choices":[{"delta":{"content":"lo"}}]}

data: [DONE]
```

On the laptop in the worked example, the first token arrived after **2.3 seconds** and the whole reply after **16.6**. Streaming turns a 17-second blank screen into text that starts in two.

The tricky part is that **the network doesn't deliver whole lines**. One read might end halfway through `da|ta:`, or even halfway through a two-byte character like `é`. A parser that splits each chunk on newlines will lose or corrupt data — on a slow connection, in production, where it's hardest to reproduce. The fix is to keep the unfinished tail in a buffer until the next chunk arrives, and to decode bytes with `{ stream: true }`.

## 5. Errors, timeouts and retries

Model calls fail far more often than database calls. Sort errors by whether a retry could help:

- **429 (rate limited)** and **5xx (server error)**: retry, with backoff.
- **400 (bad request)**, **401 (bad key)** and **404 (unknown model)**: a retry will fail the same way. Fix the request.

Every call also needs a timeout, because a model can take a long time. Pass an `AbortSignal` so a slow call can be cancelled. Retries, backoff and fallbacks are covered in depth in [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|reliability and plumbing]]. Here the adapter just labels each error as retryable or not, so that later code can decide.

## 6. A port, not a provider

Put model calls behind an interface your app owns:

```ts
interface ChatModel {
  chat(messages: Message[], options?: ChatOptions): Promise<ChatResult>;
  stream(messages: Message[], options?: ChatOptions): AsyncIterable<string>;
}
```

Then write **adapters**: one for OpenAI-compatible servers, one for another provider if you need it, and a **fake** for tests. The route handler depends only on `ChatModel`. Tests run in milliseconds, with no key or network. Switching providers, or running against a local model, changes one line of wiring. This is week 1's Build task.

### Where SDKs fit

A unified SDK, such as the **Vercel AI SDK** (`ai` on npm, the common TypeScript choice), is a ready-made set of adapters. It gives you text generation, streaming, structured output and tool calling across many providers:

```ts
// ILLUSTRATIVE shape — check the exact API against the installed version's docs.
import { generateText, streamText, tool, Output } from "ai";

const { text } = await generateText({ model, prompt: "…" });
const { textStream } = streamText({ model, prompt: "…" });
const { output } = await generateText({ model, prompt: "…", output: Output.object({ schema }) });
const result = await generateText({ model, tools: { getWeather: tool({ /* … */ }) }, prompt: "…" });
```

Using an SDK is a good choice. It still belongs *behind* your port, as the adapter, not in every route handler. Writing the small adapter in the worked example once by hand means you know what an SDK is doing for you, and you can debug it when it fails.

## 7. The discipline — the durable part

AI tooling moves faster than almost anything else in software. These habits matter more than any specific API:

- **Never hard-code model names from memory.** Models are released and retired constantly. Ask the server (`GET /v1/models`) or check the provider's current list, and keep the name in configuration.
- **Check APIs against docs that match your installed version, not recall.** Many SDKs ship their docs and source inside `node_modules`; those match your version exactly.
- **Keep the SDK current**, and read the migration guide before a major upgrade.
- **Type-check after changes.** Most errors are APIs you remember that have since changed, showing up as type errors.
- **Watch for thinking models.** Some models reason before answering, and that reasoning uses up `max_tokens` without appearing in `content`. The worked example hit exactly this.

## Worked example — a provider-neutral client

Five files. The port and a fake model:

```ts
// model.ts — the port: what the rest of the app needs from "a model", with no provider in sight.

export type Role = "system" | "user" | "assistant";
export type Message = { role: Role; content: string };
export type ChatOptions = { temperature?: number; maxTokens?: number; signal?: AbortSignal };
export type ChatResult = {
  text: string;
  finishReason: "stop" | "length" | "other"; // "length" means max tokens cut it off
  usage: { inputTokens: number; outputTokens: number };
};

export interface ChatModel {
  chat(messages: Message[], options?: ChatOptions): Promise<ChatResult>;
  stream(messages: Message[], options?: ChatOptions): AsyncIterable<string>;
}

/** The model is stateless: "memory" is the app resending every earlier turn on every call. */
export class Conversation {
  readonly messages: Message[];
  private readonly model: ChatModel;

  constructor(model: ChatModel, system: string) {
    this.model = model;
    this.messages = [{ role: "system", content: system }];
  }

  async say(content: string, options?: ChatOptions): Promise<string> {
    this.messages.push({ role: "user", content });
    const result = await this.model.chat(this.messages, options);
    this.messages.push({ role: "assistant", content: result.text });
    return result.text;
  }
}

/** A fake for tests: replies from a script and records what it was sent. */
export class FakeModel implements ChatModel {
  readonly calls: Message[][] = [];
  private readonly replies: string[];

  constructor(replies: string[]) {
    this.replies = [...replies];
  }

  async chat(messages: Message[]): Promise<ChatResult> {
    this.calls.push(structuredClone(messages));
    const text = this.replies.shift() ?? "";
    return { text, finishReason: "stop", usage: { inputTokens: 0, outputTokens: 0 } };
  }

  async *stream(messages: Message[]): AsyncIterable<string> {
    const { text } = await this.chat(messages);
    for (const word of text.split(/(?<= )/)) yield word;
  }
}
```

The SSE reader, which keeps the unfinished tail between chunks:

```ts
// sse.ts — read a server-sent events stream: lines of "data: ...", events separated by a blank line.
// Network chunks don't respect line boundaries, so keep the unfinished tail until the next chunk.

export async function* sseData(body: AsyncIterable<Uint8Array>): AsyncIterable<string> {
  const decoder = new TextDecoder();
  let buffer = "";
  for await (const chunk of body) {
    buffer += decoder.decode(chunk, { stream: true }); // stream: true keeps a split multi-byte character
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop()!; // the last piece may be incomplete
    for (const event of events) {
      const data = event
        .split(/\r?\n/)
        .filter((line) => line.startsWith("data:"))
        .map((line) => line.slice(5).trimStart())
        .join("\n");
      if (data === "[DONE]") return;
      if (data) yield data;
    }
  }
}
```

The adapter for any OpenAI-compatible server:

```ts
// openai-compatible.ts — an adapter for any server that speaks the OpenAI chat completions format:
// OpenAI, Ollama, vLLM, LM Studio, and most gateways. Other providers need their own adapter.
import type { ChatModel, ChatOptions, ChatResult, Message } from "./model.ts";
import { sseData } from "./sse.ts";

export class ModelError extends Error {
  readonly status: number;
  readonly retryable: boolean; // rate limits and server errors are worth retrying; bad requests aren't

  constructor(status: number, body: string) {
    super(`model request failed: ${status} ${body.slice(0, 200)}`);
    this.status = status;
    this.retryable = status === 429 || status >= 500;
  }
}

type Config = {
  baseUrl: string;
  model: string;
  apiKey?: string;
  extraBody?: Record<string, unknown>; // provider-specific fields, e.g. { reasoning_effort: "none" }
  fetch?: typeof fetch;
};

export class OpenAICompatibleModel implements ChatModel {
  private readonly config: Config;

  constructor(config: Config) {
    this.config = config;
  }

  async chat(messages: Message[], options: ChatOptions = {}): Promise<ChatResult> {
    const data = await (await this.post(messages, options, false)).json();
    const choice = data.choices[0];
    return {
      text: choice.message.content ?? "",
      finishReason: choice.finish_reason === "stop" ? "stop" : choice.finish_reason === "length" ? "length" : "other",
      usage: { inputTokens: data.usage?.prompt_tokens ?? 0, outputTokens: data.usage?.completion_tokens ?? 0 },
    };
  }

  async *stream(messages: Message[], options: ChatOptions = {}): AsyncIterable<string> {
    const res = await this.post(messages, options, true);
    for await (const data of sseData(res.body!)) {
      const delta = JSON.parse(data).choices[0]?.delta?.content;
      if (delta) yield delta;
    }
  }

  /** Never hard-code model names from memory: ask the server what it has. */
  async listModels(): Promise<string[]> {
    const res = await this.fetch("/models", { headers: this.headers() });
    return (await res.json()).data.map((m: { id: string }) => m.id).sort();
  }

  private async post(messages: Message[], options: ChatOptions, stream: boolean): Promise<Response> {
    return this.fetch("/chat/completions", {
      method: "POST",
      headers: { ...this.headers(), "content-type": "application/json" },
      body: JSON.stringify({
        model: this.config.model,
        messages,
        stream,
        ...this.config.extraBody,
        ...(options.temperature !== undefined && { temperature: options.temperature }),
        ...(options.maxTokens !== undefined && { max_tokens: options.maxTokens }),
      }),
      signal: options.signal,
    });
  }

  private async fetch(path: string, init: RequestInit): Promise<Response> {
    const res = await (this.config.fetch ?? fetch)(this.config.baseUrl + path, init);
    if (!res.ok) throw new ModelError(res.status, await res.text());
    return res;
  }

  private headers(): Record<string, string> {
    return this.config.apiKey ? { authorization: `Bearer ${this.config.apiKey}` } : {};
  }
}
```

The tests replace `fetch` with a fake server, so they check the exact request sent and run without a network. The SSE test splits a two-byte character across two chunks on purpose:

```ts
import { test } from "node:test";
import assert from "node:assert/strict";
import { Conversation, FakeModel } from "./model.ts";
import { ModelError, OpenAICompatibleModel } from "./openai-compatible.ts";
import { sseData } from "./sse.ts";

/** A fake server: records each request and answers with the next canned response. */
function fakeServer(...responses: Response[]) {
  const requests: { url: string; headers: Record<string, string>; body: any }[] = [];
  const fakeFetch = async (url: string | URL | Request, init?: RequestInit) => {
    requests.push({ url: String(url), headers: (init?.headers ?? {}) as Record<string, string>, body: init?.body ? JSON.parse(String(init.body)) : undefined });
    return responses.shift()!;
  };
  return { requests, fetch: fakeFetch as typeof fetch };
}

/** A body that arrives in the exact chunks given — split wherever the network likes. */
function chunked(...parts: string[]): Response {
  const encoder = new TextEncoder();
  return new Response(new ReadableStream({
    start(controller) {
      for (const part of parts) controller.enqueue(encoder.encode(part));
      controller.close();
    },
  }));
}

const config = { baseUrl: "http://model.test/v1", model: "some-model", apiKey: "sk-test" };

test("chat sends the messages format and reads text, finish reason and usage", async () => {
  const server = fakeServer(Response.json({
    choices: [{ message: { content: "Paris" }, finish_reason: "stop" }],
    usage: { prompt_tokens: 21, completion_tokens: 2 },
  }));
  const model = new OpenAICompatibleModel({ ...config, fetch: server.fetch });
  const result = await model.chat([{ role: "user", content: "Capital of France?" }], { temperature: 0, maxTokens: 5 });

  assert.deepEqual(result, { text: "Paris", finishReason: "stop", usage: { inputTokens: 21, outputTokens: 2 } });
  const [req] = server.requests;
  assert.equal(req.url, "http://model.test/v1/chat/completions");
  assert.equal(req.headers.authorization, "Bearer sk-test");
  assert.deepEqual(req.body, { model: "some-model", messages: [{ role: "user", content: "Capital of France?" }], stream: false, temperature: 0, max_tokens: 5 });
});

test("a reply cut off by max tokens says so", async () => {
  const server = fakeServer(Response.json({ choices: [{ message: { content: "The capital of" }, finish_reason: "length" }] }));
  const result = await new OpenAICompatibleModel({ ...config, fetch: server.fetch }).chat([{ role: "user", content: "…" }]);
  assert.equal(result.finishReason, "length");
});

test("provider-specific fields ride along in the body", async () => {
  const server = fakeServer(Response.json({ choices: [{ message: { content: "ok" }, finish_reason: "stop" }] }));
  await new OpenAICompatibleModel({ ...config, extraBody: { reasoning_effort: "none" }, fetch: server.fetch }).chat([]);
  assert.equal(server.requests[0].body.reasoning_effort, "none");
});

test("errors carry the status and whether a retry could help", async () => {
  const server = fakeServer(new Response("slow down", { status: 429 }), new Response("bad model name", { status: 400 }));
  const model = new OpenAICompatibleModel({ ...config, fetch: server.fetch });
  await assert.rejects(model.chat([]), (e: ModelError) => e.status === 429 && e.retryable);
  await assert.rejects(model.chat([]), (e: ModelError) => e.status === 400 && !e.retryable);
});

test("the SSE reader survives events split across network chunks, even mid-character", async () => {
  const bytes = (s: string) => [...new TextEncoder().encode(s)];
  // "é" is two bytes, 0xC3 0xA9; the second chunk ends between them
  const body = new Response(new ReadableStream({
    start(controller) {
      controller.enqueue(new Uint8Array(bytes('data: {"a":1}\n\nda')));
      controller.enqueue(new Uint8Array([...bytes('ta: {"b":"caf'), 0xc3]));
      controller.enqueue(new Uint8Array([0xa9, ...bytes('"}\n\ndata: [DONE]\n\ndata: {"ignored":true}\n\n')]));
      controller.close();
    },
  })).body!;
  const events: string[] = [];
  for await (const data of sseData(body)) events.push(data);
  assert.deepEqual(events, ['{"a":1}', '{"b":"café"}']); // and nothing after [DONE]
});

test("stream yields the text deltas in order", async () => {
  const delta = (content: string) => `data: ${JSON.stringify({ choices: [{ delta: { content } }] })}\n\n`;
  const server = fakeServer(chunked(delta("Hel") + delta("lo"), delta(", wor"), delta("ld"), "data: [DONE]\n\n"));
  const model = new OpenAICompatibleModel({ ...config, fetch: server.fetch });
  const parts: string[] = [];
  for await (const part of model.stream([{ role: "user", content: "hi" }])) parts.push(part);
  assert.deepEqual(parts, ["Hel", "lo", ", wor", "ld"]);
  assert.equal(server.requests[0].body.stream, true);
});

test("listModels asks the server instead of trusting memory", async () => {
  const server = fakeServer(Response.json({ data: [{ id: "qwen3.5:4b" }, { id: "gemma4:latest" }] }));
  assert.deepEqual(await new OpenAICompatibleModel({ ...config, fetch: server.fetch }).listModels(), ["gemma4:latest", "qwen3.5:4b"]);
  assert.equal(server.requests[0].url, "http://model.test/v1/models");
});

test("the model is stateless: a conversation resends every earlier turn", async () => {
  const model = new FakeModel(["Hi Kingsley.", "Your name is Kingsley."]);
  const chat = new Conversation(model, "Be brief.");
  await chat.say("My name is Kingsley.");
  assert.equal(await chat.say("What's my name?"), "Your name is Kingsley.");

  assert.equal(model.calls[0].length, 2); // system + first question
  assert.deepEqual(model.calls[1].map((m) => m.role), ["system", "user", "assistant", "user"]);
});
```

And the same adapter against the local model:

```ts
// live.ts — the same adapter against your local Ollama. Not run by the lab runner.
//   node live.ts               # lists models, then streams a reply from qwen3.5:4b
//   node live.ts gemma4:latest
import { OpenAICompatibleModel } from "./openai-compatible.ts";

const model = new OpenAICompatibleModel({
  baseUrl: "http://127.0.0.1:11434/v1",
  model: process.argv[2] ?? "qwen3.5:4b",
  // qwen3.5 thinks before answering by default; that thinking counts against maxTokens and isn't
  // in the reply's content. Without this line, 120 tokens of thinking left the reply empty.
  extraBody: { reasoning_effort: "none" },
});
console.log("models on this server:", (await model.listModels()).join(", "));

const started = performance.now();
let firstToken = 0;
let text = "";
for await (const part of model.stream(
  [{ role: "system", content: "Answer in two short sentences. Do not think out loud." },
   { role: "user", content: "Why do chat apps stream their replies?" }],
  { temperature: 0, maxTokens: 120 },
)) {
  firstToken ||= performance.now();
  text += part;
  process.stdout.write(part);
}
const seconds = (ms: number) => (ms / 1000).toFixed(1);
if (!text) console.log("(empty reply: the model used its whole token budget before writing any answer)");
else console.log(`\n\nfirst token after ${seconds(firstToken - started)} s; whole reply after ${seconds(performance.now() - started)} s`);
```

**What happened on the laptop.** The first run had no `extraBody` line, and it printed the model list and then an empty reply. `qwen3.5:4b` thinks before answering by default. Its 120-token budget all went on reasoning, which streams in a separate field, so `content` never arrived. Nothing errored, and the finish reason was `length`. With thinking turned off:

```
$ node live.ts
models on this server: gemma4:latest, qwen3.5:4b, qwen3.5:latest, study-qwen3.5:4b
Streaming allows messages to appear instantly as they are generated, reducing perceived wait times
for users. This technique also enables the app to send subsequent parts of a message before it has
fully finished processing or formatting them all in memory.

first token after 2.3 s; whole reply after 16.6 s
```

The answer's second sentence is vague and a bit wrong; this is a 4B model on a laptop. The timing is the point.

**Lab:** these files are in [`ai-ml/03-ai-engineer/04-calling-models/labs/typescript/`](https://github.com/kingsleydaprime/knowledgebase/tree/main/ai-ml/03-ai-engineer/04-calling-models/labs/typescript). From the vault root, `python3 labs/run.py calling-models/typescript` runs the tests and checks this page still shows the same code. `live.ts` needs Ollama running, so run it yourself from the lab folder with `node live.ts`.

## Common pitfalls

1. **Sending only the latest message.** The model has no memory; resend the history, or it really has forgotten.
2. **Ignoring `finish_reason`.** A reply cut off at `length` looks like a normal string until you parse it.
3. **Splitting stream chunks on newlines.** It works locally and breaks on a slow network. Buffer the tail.
4. **Retrying a 400.** It fails the same way every time and burns your rate limit. Retry only 429 and 5xx.
5. **Importing the provider SDK in route handlers.** Tests then need a key and a network, and switching providers is a refactor.
6. **Hard-coding a model name you remember.** It may be retired or renamed. Put it in configuration and check it against the server's list.
7. **No timeout.** One slow call holds a request, and a connection, open until something upstream gives up.

## Check your understanding

1. A chat has had 10 turns. What does the 11th request contain, and why?
2. A JSON reply fails to parse, and the response says `finish_reason: "length"`. What happened, and what are two fixes?
3. A stream parser does `chunk.split("\n")` on each network read. Describe an input that breaks it.
4. Which of these should be retried: 400, 401, 429, 500, 503?
5. What does putting the model behind a `ChatModel` port buy you in tests? In production?
6. A thinking model returns an empty `content` with no error. What's the likely cause?

<details>
<summary>Answers — after your attempt</summary>

1. The system message, all 10 earlier user messages and assistant replies, and the new user message. The model is stateless, so anything not in the request doesn't exist for it.
2. The reply hit max tokens and was cut off mid-JSON. Raise `max_tokens`, or make the requested output shorter. Either way, check `finish_reason` before parsing.
3. A chunk that ends in the middle of a line, such as one read ending at `data: {"cho` and the next starting `ices":…`. Each half fails to parse. A two-byte character split between reads is corrupted too unless decoded with `stream: true`.
4. 429, 500 and 503. 400 and 401 will fail the same way again.
5. In tests, a fake that runs in milliseconds with no key or network, and lets you assert exactly what was sent. In production, switching provider or adding a fallback changes one adapter and the wiring, not every caller.
6. The reasoning used the whole `max_tokens` budget before any answer was written. The finish reason will be `length`. Raise the budget or turn thinking off.

</details>

## Practice — independent task

**Add a second adapter.** Write `AnthropicModel implements ChatModel` for Anthropic's Messages API, using its current docs (not memory).

1. Map the port's messages to that API's shape: the system message becomes a top-level field, and `max_tokens` is required.
2. Map its response back to `ChatResult`, including its stop reason and usage field names.
3. Test it with the same fake-server approach as `calling.test.ts`: assert the exact request body, and parse a canned response.

**Done when:** your adapter's tests pass without a network or key, `Conversation` works with it unchanged, and you can point to the one place in the code where you'd choose which adapter to use.

## Before moving on

You can write a chat request and read its response without looking anything up, explain why chats resend history, and explain why a stream parser needs a buffer.

**Recap.** A model call is a list of role-tagged messages plus settings. The response gives text, a finish reason and token usage; read all three. The model keeps nothing between calls. Streaming sends SSE events that can split anywhere, so buffer them. Retry only errors a retry can fix. Keep every provider behind a port, with a fake for tests.

**Next.** [[ai-ml/03-ai-engineer/11-structured-output/index|Structured output]] — getting data back instead of prose (week 2).

## Related
- [[ai-ml/03-ai-engineer/04-calling-models/in-other-languages|Calling models in other languages]] — the same client in Python, Go, Java, Rust, C, C++ and C#
- [[ai-ml/03-ai-engineer/02-how-llms-work/index|How LLMs work]] — the settings sent on each call
- [[ai-ml/03-ai-engineer/05-prompt-engineering/index|Prompt engineering]] — what goes in the messages
- [[ai-ml/03-ai-engineer/07-tools-and-mcp/index|Tools and MCP]] — tool calling in depth
- [[ai-ml/03-ai-engineer/13-reliability-and-plumbing/index|Reliability and plumbing]] — retries, backoff and fallbacks
- [[backend/03-structuring-a-backend/04-hexagonal-and-clean-architecture/index|Hexagonal and clean architecture]] — ports and adapters in general

*Source: new for the AI-engineer track, grounded in the AI-feature work in these projects. SDK shapes change fast; check them against current docs.*
