// resilient.ts — the layers assembled around one model call, in the order that lets each one work.
import type { CircuitBreaker } from "./breaker.ts";
import { firstThatWorks, type Option } from "./fallback.ts";
import { type RetryOptions, withRetry, withTimeout } from "./retry.ts";

export type Call = (input: string, signal: AbortSignal) => Promise<string>;

export type Layers = {
  timeoutMs: number;
  retry: RetryOptions;
  breaker: CircuitBreaker;
  fallback?: (input: string) => Promise<string>;
  log?: (line: string) => void;
};

/** fallback( retry( breaker( timeout( call ) ) ) )
 *  - The timeout is per attempt, so one hung attempt can't use up the whole time budget.
 *  - The breaker sees every attempt. Once it opens, the retry loop stops at once,
 *    because CircuitOpenError isn't retryable.
 *  - The fallback runs only when retries are used up or the circuit is open. */
export function resilient(name: string, call: Call, layers: Layers) {
  const log = layers.log ?? (() => {});
  const primary = (input: string) =>
    withRetry(() => layers.breaker.call(() => withTimeout((signal) => call(input, signal), layers.timeoutMs)), {
      ...layers.retry,
      onRetry: ({ attempt, waitMs, error }) => log(`${name}: attempt ${attempt} failed (${describe(error)}), retrying in ${waitMs} ms`),
    });

  return (input: string) => {
    const options: Option<string>[] = [{ name, run: () => primary(input) }];
    if (layers.fallback) options.push({ name: "fallback", run: () => layers.fallback!(input) });
    return firstThatWorks(options, (by, error) => log(`${by}: gave up (${describe(error)})`));
  };
}

function describe(error: unknown): string {
  const status = (error as { status?: number })?.status;
  return status ? `HTTP ${status}` : ((error as Error)?.name ?? String(error));
}
