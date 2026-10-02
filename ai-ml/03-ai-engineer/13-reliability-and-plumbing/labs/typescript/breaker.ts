// breaker.ts — stop calling a dependency that keeps failing, and test it again after a cool-down.
import { isRetryable } from "./retry.ts";

export type BreakerState = "closed" | "open" | "half-open";

export class CircuitOpenError extends Error {
  override name = "CircuitOpenError";
}

export class CircuitBreaker {
  private state: BreakerState = "closed";
  private failures = 0;
  private openedAt = 0;
  private trialRunning = false;
  private readonly threshold: number;
  private readonly coolDownMs: number;
  private readonly now: () => number;

  constructor({ threshold = 5, coolDownMs = 30_000, now = Date.now } = {}) {
    this.threshold = threshold;
    this.coolDownMs = coolDownMs;
    this.now = now;
  }

  current(): BreakerState {
    if (this.state === "open" && this.now() - this.openedAt >= this.coolDownMs) this.state = "half-open";
    return this.state;
  }

  async call<T>(fn: () => Promise<T>): Promise<T> {
    const state = this.current();
    if (state === "open") throw new CircuitOpenError("circuit open: not calling a dependency that keeps failing");
    if (state === "half-open") {
      if (this.trialRunning) throw new CircuitOpenError("circuit half-open: one trial call is already running");
      this.trialRunning = true;
    }
    try {
      const result = await fn();
      this.state = "closed";
      this.failures = 0;
      return result;
    } catch (error) {
      // Only failures that say the dependency is unhealthy count. A 400 is our bug, not its outage.
      if (isRetryable(error)) {
        this.failures++;
        if (state === "half-open" || this.failures >= this.threshold) {
          this.state = "open";
          this.openedAt = this.now();
        }
      }
      throw error;
    } finally {
      if (state === "half-open") this.trialRunning = false;
    }
  }
}
