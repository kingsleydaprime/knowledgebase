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
