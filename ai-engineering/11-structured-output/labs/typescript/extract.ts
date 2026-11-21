// extract.ts — turn a model's reply into a validated Invoice, retrying with the errors as feedback.
import { checkInvariants, type Invoice, validateInvoice } from "./invoice.ts";

export type Message = { role: "system" | "user" | "assistant"; content: string };
export type Reply = { text: string; finishReason: "stop" | "length" | "other"; refusal?: string };
export type Model = (messages: Message[]) => Promise<Reply>;

/** Models asked for JSON often wrap it: "Sure! ```json {...} ```". Take the outermost {...}. */
export function parseModelJson(text: string): unknown {
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start === -1 || end < start) throw new SyntaxError("no JSON object in the reply");
  return JSON.parse(text.slice(start, end + 1));
}

export type Outcome =
  | { ok: true; invoice: Invoice; attempts: number }
  | { ok: false; reason: "refused" | "invalid"; detail: string; attempts: number };

const SYSTEM = "Extract the invoice as JSON with fields vendor, invoice_number, currency (GBP, USD, EUR or NGN), " +
  "due_date (YYYY-MM-DD), line_items (description, amount_cents) and total_cents. Amounts are integers in cents. " +
  "Reply with only the JSON object.";

export async function extractInvoice(model: Model, document: string, maxAttempts = 3): Promise<Outcome> {
  const messages: Message[] = [{ role: "system", content: SYSTEM }, { role: "user", content: document }];
  let problem = "";
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    const reply = await model(messages);
    // A refusal won't match the schema, and retrying won't change it: check it before parsing.
    if (reply.refusal) return { ok: false, reason: "refused", detail: reply.refusal, attempts: attempt };

    if (reply.finishReason === "length") {
      problem = "your reply was cut off before the JSON was complete; reply with a shorter, complete object";
    } else {
      try {
        const shape = validateInvoice(parseModelJson(reply.text));
        const checked = shape.ok ? checkInvariants(shape.value) : shape;
        if (checked.ok) return { ok: true, invoice: checked.value, attempts: attempt };
        problem = checked.errors.join("; ");
      } catch (e) {
        problem = `that was not valid JSON (${(e as Error).message})`;
      }
    }
    // Feed back exactly what was wrong; a bare "try again" usually gets the same mistake.
    messages.push({ role: "assistant", content: reply.text });
    messages.push({ role: "user", content: `Your reply had these problems: ${problem}. Return the corrected JSON object only.` });
  }
  return { ok: false, reason: "invalid", detail: problem, attempts: maxAttempts };
}
