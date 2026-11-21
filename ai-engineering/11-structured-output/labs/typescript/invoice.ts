// invoice.ts — the contract: one JSON Schema for the model, and a validator for your code.
// In a real project, Zod (TS) or Pydantic (Python) gives you both, plus a static type, from one
// definition. Writing them by hand once shows what those libraries check for you.

export type Invoice = {
  vendor: string;
  invoice_number: string;
  currency: "GBP" | "USD" | "EUR" | "NGN";
  due_date: string; // ISO 8601, e.g. "2026-10-15"
  line_items: { description: string; amount_cents: number }[];
  total_cents: number;
};

const CURRENCIES = ["GBP", "USD", "EUR", "NGN"];

/** Sent to the model for schema-constrained decoding. Flat, enums for categories, integer cents. */
export const invoiceSchema = {
  type: "object",
  properties: {
    vendor: { type: "string" },
    invoice_number: { type: "string" },
    currency: { type: "string", enum: CURRENCIES },
    due_date: { type: "string", description: "ISO 8601 date, YYYY-MM-DD" },
    line_items: {
      type: "array",
      items: {
        type: "object",
        properties: { description: { type: "string" }, amount_cents: { type: "integer" } },
        required: ["description", "amount_cents"],
        additionalProperties: false,
      },
    },
    total_cents: { type: "integer" },
  },
  required: ["vendor", "invoice_number", "currency", "due_date", "line_items", "total_cents"],
  additionalProperties: false,
} as const;

export type Checked<T> = { ok: true; value: T } | { ok: false; errors: string[] };

/** Does it have the right shape? Checks what the schema says, plus what schemas often can't (the date format). */
export function validateInvoice(value: unknown): Checked<Invoice> {
  const errors: string[] = [];
  if (typeof value !== "object" || value === null || Array.isArray(value)) return { ok: false, errors: ["expected a JSON object"] };
  const v = value as Record<string, unknown>;
  const allowed = new Set(Object.keys(invoiceSchema.properties));
  for (const key of Object.keys(v)) if (!allowed.has(key)) errors.push(`unexpected field "${key}"`);
  for (const key of invoiceSchema.required) if (!(key in v)) errors.push(`missing field "${key}"`);

  for (const key of ["vendor", "invoice_number"]) if (key in v && typeof v[key] !== "string") errors.push(`"${key}" must be a string`);
  if ("currency" in v && !CURRENCIES.includes(v.currency as string)) errors.push(`"currency" must be one of ${CURRENCIES.join(", ")}`);
  if ("due_date" in v && !(typeof v.due_date === "string" && /^\d{4}-\d{2}-\d{2}$/.test(v.due_date) && !isNaN(Date.parse(v.due_date))))
    errors.push(`"due_date" must be a date like 2026-10-15`);
  if ("total_cents" in v && !Number.isInteger(v.total_cents)) errors.push(`"total_cents" must be a whole number of cents`);
  if ("line_items" in v) {
    if (!Array.isArray(v.line_items)) errors.push(`"line_items" must be an array`);
    else v.line_items.forEach((item, i) => {
      if (typeof item?.description !== "string") errors.push(`line_items[${i}].description must be a string`);
      if (!Number.isInteger(item?.amount_cents)) errors.push(`line_items[${i}].amount_cents must be a whole number of cents`);
    });
  }
  return errors.length ? { ok: false, errors } : { ok: true, value: v as Invoice };
}

/** Is it plausible? A schema can't say "the items add up to the total"; only your code can. */
export function checkInvariants(invoice: Invoice): Checked<Invoice> {
  const sum = invoice.line_items.reduce((total, item) => total + item.amount_cents, 0);
  return sum === invoice.total_cents
    ? { ok: true, value: invoice }
    : { ok: false, errors: [`line items add up to ${sum} cents but total_cents is ${invoice.total_cents}`] };
}
