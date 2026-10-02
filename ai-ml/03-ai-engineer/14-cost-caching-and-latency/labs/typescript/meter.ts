// meter.ts — one log record per model call, and the numbers worth putting on a dashboard.
import type { Usage } from "./pricing.ts";

export type CallRecord = {
  feature: string;
  model: string;
  ms: number; // the whole call
  ttftMs?: number; // time to first token, for streamed calls
  usage: Usage;
  costUsd: number;
  ok: boolean;
};

/** Nearest-rank percentile: the smallest value that at least p% of the values are less than or equal to. */
export function percentile(values: number[], p: number): number {
  if (values.length === 0) return NaN;
  const sorted = [...values].sort((a, b) => a - b);
  return sorted[Math.max(0, Math.ceil((p / 100) * sorted.length) - 1)];
}

export function summarise(records: CallRecord[]) {
  const ms = records.map((r) => r.ms);
  const sum = (f: (r: CallRecord) => number) => records.reduce((total, r) => total + f(r), 0);
  const read = sum((r) => r.usage.cacheReadTokens ?? 0);
  const allInput = read + sum((r) => r.usage.inputTokens + (r.usage.cacheWriteTokens ?? 0));
  return {
    calls: records.length,
    failed: records.filter((r) => !r.ok).length,
    costUsd: sum((r) => r.costUsd),
    costPerCall: sum((r) => r.costUsd) / records.length,
    meanMs: sum((r) => r.ms) / records.length,
    p50Ms: percentile(ms, 50),
    p95Ms: percentile(ms, 95),
    cacheReadShare: allInput === 0 ? 0 : read / allInput, // of all input tokens, the share read from cache
  };
}

/** Read a stream to the end, timing the first chunk separately: that wait is the one users feel. */
export async function timeStream(chunks: AsyncIterable<string>, now = () => performance.now()) {
  const started = now();
  let ttftMs: number | undefined;
  let text = "";
  for await (const chunk of chunks) {
    ttftMs ??= now() - started;
    text += chunk;
  }
  return { text, ttftMs: ttftMs ?? now() - started, totalMs: now() - started };
}
