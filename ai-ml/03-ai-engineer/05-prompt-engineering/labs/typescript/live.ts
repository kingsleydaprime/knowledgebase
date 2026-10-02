// live.ts — zero-shot vs few-shot on the labelled reviews, with a local model. Not run by the lab runner.
//   node live.ts                  # qwen3.5:4b
//   node live.ts gemma4:latest
import { evaluate } from "./evaluate.ts";
import { loadPrompt } from "./prompt.ts";
import { cases, examples } from "./reviews.ts";

const model = process.argv[2] ?? "qwen3.5:4b";

async function ask(prompt: string): Promise<string> {
  const res = await fetch("http://127.0.0.1:11434/api/chat", {
    method: "POST",
    body: JSON.stringify({
      model,
      messages: [{ role: "user", content: prompt }],
      stream: false,
      think: false,
      options: { temperature: 0, num_predict: 5 }, // temperature 0: compare prompts, not luck
    }),
  });
  return (await res.json()).message.content;
}

for (const name of ["classify-zero-shot", "classify-few-shot"]) {
  const started = performance.now();
  const result = await evaluate(ask, loadPrompt(name), cases, examples);
  console.log(`\n${name}: ${result.correct}/${result.total} correct (${((performance.now() - started) / 1000).toFixed(0)} s)`);
  for (const f of result.failures) console.log(`  expected ${f.expected}, got ${f.got ?? `unreadable (${JSON.stringify(f.reply)})`}: ${f.review}`);
}
