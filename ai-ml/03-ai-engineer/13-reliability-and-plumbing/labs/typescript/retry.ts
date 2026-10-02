// retry.ts — retry only the failures a retry can fix, wait longer each time, and stop in time.

export type Sleep = (ms: number) => Promise<void>;
export const realSleep: Sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

/** A failed model call. `status` is the HTTP status; `retryAfterMs` comes from the Retry-After header. */
export class CallError extends Error {
  readonly status: number;
  readonly retryAfterMs: number | undefined;

  constructor(status: number, message = `HTTP ${status}`, retryAfterMs?: number) {
    super(message);
    this.status = status;
    this.retryAfterMs = retryAfterMs;
  }
}

/** Could the same request succeed if sent again? */
export function isRetryable(error: unknown): boolean {
  const status = (error as { status?: unknown })?.status;
  if (typeof status === "number") return status === 408 || status === 429 || status >= 500; // 529 "overloaded" included
  const name = (error as Error)?.name;
  if (name === "TimeoutError") return true; // our own deadline for one attempt fired
  return error instanceof TypeError && error.message === "fetch failed"; // no response at all: DNS, refused, reset
}

/** Retry-After is either a number of seconds or an HTTP date. Returns milliseconds to wait. */
export function parseRetryAfter(header: string | null, now = Date.now()): number | undefined {
  if (header === null || header.trim() === "") return undefined;
  const seconds = Number(header);
  if (Number.isFinite(seconds)) return Math.max(0, seconds * 1000);
  const date = Date.parse(header);
  return Number.isNaN(date) ? undefined : Math.max(0, date - now);
}

/** Exponential backoff with full jitter: a random wait between 0 and min(cap, base × 2^(attempt − 1)). */
export function backoff(attempt: number, baseMs: number, capMs: number, random = Math.random): number {
  return Math.round(random() * Math.min(capMs, baseMs * 2 ** (attempt - 1)));
}

export type RetryOptions = {
  maxAttempts?: number; // every try, including the first
  baseMs?: number;
  capMs?: number;
  deadlineMs?: number; // the whole operation, measured from the first try
  sleep?: Sleep;
  random?: () => number;
  now?: () => number;
  onRetry?: (info: { attempt: number; waitMs: number; error: unknown }) => void;
};

export async function withRetry<T>(call: (attempt: number) => Promise<T>, options: RetryOptions = {}): Promise<T> {
  const { maxAttempts = 3, baseMs = 500, capMs = 10_000, deadlineMs = Infinity } = options;
  const { sleep = realSleep, random = Math.random, now = Date.now, onRetry } = options;
  const started = now();
  for (let attempt = 1; ; attempt++) {
    try {
      return await call(attempt);
    } catch (error) {
      if (!isRetryable(error) || attempt >= maxAttempts) throw error;
      const hinted = (error as { retryAfterMs?: number }).retryAfterMs; // the server knows best
      const waitMs = hinted ?? backoff(attempt, baseMs, capMs, random);
      if (now() - started + waitMs > deadlineMs) throw error; // waiting would blow the deadline: fail now
      onRetry?.({ attempt, waitMs, error });
      await sleep(waitMs);
    }
  }
}

/** A deadline for one attempt. The call gets a signal to cancel its request; if it ignores the
 *  signal, the caller still gets a TimeoutError on time, though the request runs on unseen. */
export async function withTimeout<T>(call: (signal: AbortSignal) => Promise<T>, ms: number): Promise<T> {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  const expired = new Promise<never>((_, reject) => {
    timer = setTimeout(() => {
      const reason = new DOMException(`timed out after ${ms} ms`, "TimeoutError");
      controller.abort(reason);
      reject(reason);
    }, ms);
  });
  try {
    return await Promise.race([call(controller.signal), expired]);
  } finally {
    clearTimeout(timer);
  }
}
