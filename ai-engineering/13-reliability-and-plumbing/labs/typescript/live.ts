// live.ts — the layers around a real local model: a normal call, a timeout, and a model that doesn't exist.
// Not run by the lab runner. Needs Ollama; about 3 model calls.
//   node live.ts               # qwen3.5:4b
//   node live.ts gemma4:latest
import { keywords } from "../../../12-evals/labs/typescript/baselines.ts";
import { CircuitBreaker } from "./breaker.ts";
import { resilient } from "./resilient.ts";
import { CallError, parseRetryAfter } from "./retry.ts";

const model = process.argv[2] ?? "qwen3.5:4b";

const ollama = (name: string) => async (ticket: string, signal: AbortSignal) => {
  const res = await fetch("http://127.0.0.1:11434/api/chat", {
    method: "POST",
    body: JSON.stringify({
      model: name,
      messages: [{ role: "user", content: `Classify as bug, billing, feature or other. One word.\n\n${ticket}` }],
      stream: false,
      think: false,
      options: { temperature: 0, num_predict: 5 },
    }),
    signal,
  });
  if (!res.ok) throw new CallError(res.status, await res.text(), parseRetryAfter(res.headers.get("retry-after")));
  return (await res.json()).message.content.trim();
};

async function attempt(label: string, call: (ticket: string) => Promise<{ by: string; value: string }>) {
  const started = performance.now();
  const { by, value } = await call("I was charged twice for my March subscription.");
  console.log(`${label}: ${JSON.stringify(value)} from ${by}, in ${((performance.now() - started) / 1000).toFixed(1)} s\n`);
}

const layers = (timeoutMs: number) => ({
  timeoutMs,
  retry: { maxAttempts: 2, baseMs: 500 },
  breaker: new CircuitBreaker({ threshold: 5 }),
  fallback: keywords,
  log: (line: string) => console.log("  " + line),
});

await attempt("normal (2-minute timeout)", resilient(model, ollama(model), layers(120_000)));
await attempt("impatient (1-second timeout)", resilient(model, ollama(model), layers(1_000)));
await attempt("unknown model", resilient("no-such-model", ollama("no-such-model:1b"), layers(120_000)));
