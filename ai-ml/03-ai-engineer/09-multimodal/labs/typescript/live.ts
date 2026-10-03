// live.ts — extract an invoice from a photo or scan of your own, with a local vision model.
// Not run by the lab runner. Needs Ollama and a vision-capable model (qwen3.5:4b and gemma4 both are); 1 call.
//   node live.ts path/to/receipt.jpg              # qwen3.5:4b
//   node live.ts path/to/receipt.jpg gemma4:latest
import { readFileSync } from "node:fs";
import { fit, HIGH_RES, sniff } from "./image.ts";
import { extractInvoice } from "./messages.ts";

const [path, model = "qwen3.5:4b"] = process.argv.slice(2);
if (!path) throw new Error("usage: node live.ts <image> [model]");
const bytes = readFileSync(path);
const info = sniff(bytes);
console.log(`${path}: ${info?.type ?? "not an image"} ${info?.width ?? "?"}×${info?.height ?? "?"}`);
if (info?.width && info.height) console.log(`on a high-resolution hosted model this would be about ${fit(info.width, info.height, HIGH_RES).tokens} tokens`);

const started = performance.now();
const result = await extractInvoice(async (image, prompt) => {
  const res = await fetch("http://127.0.0.1:11434/api/chat", {
    method: "POST",
    body: JSON.stringify({ model, stream: false, think: false, options: { temperature: 0 },
      messages: [{ role: "user", content: prompt, images: [Buffer.from(image).toString("base64")] }] }),
  });
  return (await res.json()).message.content;
}, bytes);
console.log(JSON.stringify(result, null, 2));
console.log(`(${((performance.now() - started) / 1000).toFixed(1)} s)`);
