// pii.ts — replace personal data with placeholders before text leaves your system, and put it back after.

/** The Luhn check digit that every real card number satisfies, so a random 16-digit order number isn't taken for a card. */
export function luhn(digits: string): boolean {
  let sum = 0;
  for (let i = 0; i < digits.length; i++) {
    let d = Number(digits[digits.length - 1 - i]);
    if (i % 2 === 1 && (d *= 2) > 9) d -= 9;
    sum += d;
  }
  return digits.length >= 13 && sum % 10 === 0;
}

type Kind = "EMAIL" | "CARD" | "PHONE";
const DETECTORS: [Kind, RegExp, (match: string) => boolean][] = [
  ["EMAIL", /[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}/g, () => true],
  // Cards before phones, since both are runs of digits. Neither may start or end inside a longer run:
  // without the (?<!\d[ -]?) and (?![ -]?\d) guards, the phone pattern took the first 12 digits of a 16-digit number.
  ["CARD", /(?<![\w+]|\d[ -])\d(?:[ -]?\d){12,18}(?![ -]?\d|\w)/g, (m) => luhn(m.replace(/\D/g, ""))],
  ["PHONE", /(?<!\w|\d[ ()-])\+?\d(?:[ ()-]{0,2}\d){8,13}(?![ ()-]{0,2}\d|\w)/g, () => true],
];

/** Pseudonymisation: the same value always gets the same placeholder, and only this object can reverse it. */
export class Vault {
  private readonly byValue = new Map<string, string>();
  private readonly byPlaceholder = new Map<string, string>();
  private readonly counts = new Map<Kind, number>();

  redact(text: string): string {
    let out = text;
    for (const [kind, pattern, accept] of DETECTORS) {
      out = out.replace(pattern, (match) => (accept(match) ? this.placeholder(kind, match) : match));
    }
    return out;
  }

  restore(text: string): string {
    return text.replace(/<(EMAIL|CARD|PHONE)_\d+>/g, (p) => this.byPlaceholder.get(p) ?? p); // unknown placeholders stay as they are
  }

  get size(): number {
    return this.byValue.size;
  }

  private placeholder(kind: Kind, value: string): string {
    const known = this.byValue.get(value);
    if (known) return known;
    const n = (this.counts.get(kind) ?? 0) + 1;
    this.counts.set(kind, n);
    const p = `<${kind}_${n}>`;
    this.byValue.set(value, p);
    this.byPlaceholder.set(p, value);
    return p;
  }
}

/** Logs and traces outlive the request, and are read by more people. Redact before writing, and keep no vault. */
export const forLog = (record: Record<string, unknown>) => JSON.parse(new Vault().redact(JSON.stringify(record)));
