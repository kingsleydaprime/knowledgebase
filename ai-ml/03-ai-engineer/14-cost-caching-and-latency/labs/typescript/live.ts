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
