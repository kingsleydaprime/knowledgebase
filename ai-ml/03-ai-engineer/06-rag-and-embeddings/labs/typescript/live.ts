// live.ts — the same retrieval scores with a real embedding model, then one grounded answer.
// Not run by the lab runner. Needs Ollama with an embedding model (`ollama pull nomic-embed-text`, about 270 MB)
// and a chat model; about 20 embedding calls and 1 chat call.
//   node live.ts
import { readFileSync } from "node:fs";
import { chunkDoc, loadHelp, withContext } from "./chunk.ts";
import { checkCitations, docsOf, groundedPrompt, mrr, type Question, recallAtK } from "./rag.ts";
import { bm25, rrf, vectorSearch } from "./search.ts";

const OLLAMA = "http://127.0.0.1:11434";
const cache = new Map<string, number[]>();
async function embed(text: string): Promise<number[]> {
  if (!cache.has(text)) {
    const res = await fetch(`${OLLAMA}/api/embed`, { method: "POST", body: JSON.stringify({ model: "nomic-embed-text", input: text }) });
    cache.set(text, (await res.json()).embeddings[0]);
  }
  return cache.get(text)!;
}

const docs = loadHelp();
const chunks = docs.flatMap((d) => chunkDoc(d).map((c) => ({ id: c.id, text: withContext(c, d.title) })));
const questions: Question[] = JSON.parse(readFileSync(new URL("../shared/questions.json", import.meta.url), "utf8"));

const results = { keyword: new Map<string, string[]>(), vector: new Map<string, string[]>(), hybrid: new Map<string, string[]>() };
for (const q of questions) {
  const keyword = bm25(q.question, chunks);
  const vector = await vectorSearch(q.question, chunks, embed);
  results.keyword.set(q.id, docsOf(keyword));
  results.vector.set(q.id, docsOf(vector));
  results.hybrid.set(q.id, docsOf(rrf([keyword, vector])));
  console.log(`${q.id} ${q.kind.padEnd(24)} vector top 3: ${docsOf(vector).slice(0, 3).join(", ")}  (best cosine ${vector[0]?.score.toFixed(3)})`);
}
for (const [name, r] of Object.entries(results)) {
  console.log(`${name.padEnd(8)} recall@1 ${recallAtK(r, questions, 1)}  recall@3 ${recallAtK(r, questions, 3)}  MRR ${mrr(r, questions).toFixed(3)}`);
}

const question = "How long does a refund take on an annual plan?";
const top = rrf([bm25(question, chunks), await vectorSearch(question, chunks, embed)]).slice(0, 3);
const sources = top.map((t) => ({ id: t.id, text: chunks.find((c) => c.id === t.id)!.text }));
const res = await fetch(`${OLLAMA}/api/chat`, {
  method: "POST",
  body: JSON.stringify({ model: "qwen3.5:4b", stream: false, think: false, options: { temperature: 0 },
    messages: [{ role: "user", content: groundedPrompt(question, sources) }] }),
});
const answer = (await res.json()).message.content.trim();
console.log(`\nQ: ${question}\nsources: ${sources.map((s) => s.id).join(", ")}\nA: ${answer}\ncitations: ${JSON.stringify(checkCitations(answer, sources.length))}`);
