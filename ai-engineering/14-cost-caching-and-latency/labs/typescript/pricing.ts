// pricing.ts — what a call costs, worked out from its token counts.

/** US dollars per million tokens. */
export type Price = { input: number; output: number; cacheWrite: number; cacheRead: number };

/** Token counts for one call. `inputTokens` counts only the input that was neither written to nor read
 *  from the cache, which is how Anthropic reports it; check how your provider splits them. */
export type Usage = { inputTokens: number; outputTokens: number; cacheWriteTokens?: number; cacheReadTokens?: number };

/** Anthropic's list prices on 2026-10-02, with 5-minute cache writes. Prices change: check before relying on them. */
export const PRICES = {
  "claude-haiku-4-5": { input: 1, output: 5, cacheWrite: 1.25, cacheRead: 0.1 },
  "claude-sonnet-5-5": { input: 2, output: 10, cacheWrite: 2.5, cacheRead: 0.2 },
  "claude-opus-5-5": { input: 4, output: 20, cacheWrite: 5, cacheRead: 0.2 },
  local: { input: 0, output: 0, cacheWrite: 0, cacheRead: 0 }, // electricity and your time aren't on the bill
} satisfies Record<string, Price>;

export function cost(usage: Usage, price: Price): number {
  const dollars =
    usage.inputTokens * price.input +
    usage.outputTokens * price.output +
    (usage.cacheWriteTokens ?? 0) * price.cacheWrite +
    (usage.cacheReadTokens ?? 0) * price.cacheRead;
  return dollars / 1_000_000;
}

/** How many calls must share a prefix before caching it is cheaper than not.
 *  Caching n calls costs write + (n − 1) × read; not caching costs n × input. */
export function breakEvenCalls(price: Price): number {
  return Math.floor((price.cacheWrite - price.cacheRead) / (price.input - price.cacheRead)) + 1;
}

/** Batch APIs (Anthropic, OpenAI) charge half price for work that can wait up to 24 hours. */
export function batchPrice(price: Price): Price {
  return { input: price.input / 2, output: price.output / 2, cacheWrite: price.cacheWrite / 2, cacheRead: price.cacheRead / 2 };
}
