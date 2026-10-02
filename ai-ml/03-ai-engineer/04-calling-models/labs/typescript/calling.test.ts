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
