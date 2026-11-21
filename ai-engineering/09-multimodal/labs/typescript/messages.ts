// messages.ts — the same image and question in three providers' formats, and an extraction pipeline.
import { checkInvariants, type Invoice, validateInvoice } from "../../../11-structured-output/labs/typescript/invoice.ts";
import { parseModelJson } from "../../../11-structured-output/labs/typescript/extract.ts";
import { sniff } from "./image.ts";

/** An image goes in the user message as one more content part, next to the text. Each API spells it differently. */
export function imageMessage(bytes: Uint8Array, question: string, format: "anthropic" | "openai" | "ollama") {
  const info = sniff(bytes);
  if (!info) throw new Error("not a supported image");
  const data = Buffer.from(bytes).toString("base64");
  switch (format) {
    case "anthropic": // Messages API: a content block with a base64 source
      return { role: "user", content: [{ type: "image", source: { type: "base64", media_type: info.type, data } }, { type: "text", text: question }] };
    case "openai": // Chat Completions: the image as a data URL
      return { role: "user", content: [{ type: "text", text: question }, { type: "image_url", image_url: { url: `data:${info.type};base64,${data}` } }] };
    case "ollama": // Ollama's own /api/chat: a list of base64 images beside the text
      return { role: "user", content: question, images: [data] };
  }
}

export type See = (bytes: Uint8Array, prompt: string) => Promise<string>;

export const EXTRACT_PROMPT = `Read this invoice and reply with JSON only:
{"vendor": string, "invoice_number": string, "currency": "GBP"|"USD"|"EUR"|"NGN", "due_date": "YYYY-MM-DD",
 "line_items": [{"description": string, "amount_cents": integer}], "total_cents": integer}
If you can't read a value, don't guess: reply {"unreadable": "<which field>"}.`;

/** Image in, checked data out. Reading an image is less reliable than reading text, so the same checks
 *  as the structured-output lesson apply, and "unreadable" is an answer, not an error. */
export async function extractInvoice(see: See, bytes: Uint8Array):
  Promise<{ ok: true; invoice: Invoice } | { ok: false; reason: string }> {
  if (!sniff(bytes)) return { ok: false, reason: "not a supported image" };
  let parsed: unknown;
  try {
    parsed = parseModelJson(await see(bytes, EXTRACT_PROMPT));
  } catch {
    return { ok: false, reason: "no JSON in the reply" };
  }
  if (parsed && typeof parsed === "object" && "unreadable" in parsed) return { ok: false, reason: `unreadable: ${(parsed as { unreadable: string }).unreadable}` };
  const shape = validateInvoice(parsed);
  if (!shape.ok) return { ok: false, reason: shape.errors.join("; ") };
  const sums = checkInvariants(shape.value); // a misread digit usually breaks the arithmetic
  return sums.ok ? { ok: true, invoice: sums.value } : { ok: false, reason: sums.errors.join("; ") };
}
