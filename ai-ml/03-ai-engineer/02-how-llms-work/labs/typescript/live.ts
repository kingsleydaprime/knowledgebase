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
