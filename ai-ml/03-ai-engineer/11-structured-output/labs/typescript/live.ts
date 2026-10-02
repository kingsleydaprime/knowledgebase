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
