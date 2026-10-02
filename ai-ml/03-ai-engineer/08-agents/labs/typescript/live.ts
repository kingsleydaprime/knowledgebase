// live.ts — the agent and the workflow on the same questions, with a local model.
// Not run by the lab runner. Needs Ollama; about 3 model calls per question for the agent, 1 for the workflow.
//   node live.ts               # qwen3.5:4b
import { openAITools } from "../../../07-tools-and-mcp/labs/typescript/openai-tools.ts";
import { loadOrders, supportTools } from "../../../07-tools-and-mcp/labs/typescript/support-tools.ts";
import { runAgent } from "./agent.ts";
import { refundStatus } from "./workflow.ts";

const name = process.argv[2] ?? "qwen3.5:4b";
const base = "http://127.0.0.1:11434/v1";
const agentModel = openAITools({ baseUrl: base, model: name, extraBody: { reasoning_effort: "none", temperature: 0 } });
const write = async (prompt: string) => {
  const res = await fetch(`${base}/chat/completions`, {
    method: "POST",
    body: JSON.stringify({ model: name, messages: [{ role: "user", content: prompt }], reasoning_effort: "none", temperature: 0 }),
  });
  return (await res.json()).choices[0].message.content.trim();
};
const system = "You are a support assistant. Use the tools to look orders up; never guess. Answer in one or two sentences.";

for (const question of ["Where is my refund for order A123?", "Where is my refund for D012?", "Has my refund come through?"]) {
  console.log(`Q: ${question}`);
  let started = performance.now();
  const outcome = await runAgent(agentModel, [{ role: "system", content: system }, { role: "user", content: question }], supportTools(loadOrders()));
  const calls = outcome.trace.flatMap((s) => s.calls.map((c) => `${c.name}${c.isError ? "!" : ""}`));
  console.log(`  agent:    ${outcome.status}, ${outcome.trace.length} model calls [${calls.join(", ")}], ${((performance.now() - started) / 1000).toFixed(1)} s`);
  console.log(`            ${outcome.answer ?? "(no answer)"}`);
  started = performance.now();
  const flow = await refundStatus(question, supportTools(loadOrders()), write);
  const said = flow.kind === "handoff" ? `handoff: ${flow.reason}` : flow.text;
  console.log(`  workflow: ${flow.kind}, ${((performance.now() - started) / 1000).toFixed(1)} s\n            ${said}\n`);
}
