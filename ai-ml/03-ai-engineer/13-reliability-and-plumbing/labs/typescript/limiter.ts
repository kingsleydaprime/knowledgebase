// limiter.ts — a token bucket: pace requests under a rate limit instead of firing them and collecting 429s.
import { realSleep, type Sleep } from "./retry.ts";

export class TokenBucket {
  private tokens: number;
  private last: number;
  private readonly capacity: number;
  private readonly perSecond: number;
  private readonly now: () => number;

  /** `capacity` is the largest burst; `perSecond` is the steady rate, e.g. 60 requests a minute = 1. */
  constructor({ capacity, perSecond, now = Date.now }: { capacity: number; perSecond: number; now?: () => number }) {
    this.capacity = capacity;
    this.perSecond = perSecond;
    this.now = now;
    this.tokens = capacity;
    this.last = now();
  }

  /** Takes `cost` tokens and returns 0 if there are enough; otherwise takes nothing and
   *  returns how many milliseconds until there will be. */
  tryTake(cost = 1): number {
    if (cost > this.capacity) throw new RangeError(`a cost of ${cost} can never fit a bucket of ${this.capacity}`);
    const elapsed = (this.now() - this.last) / 1000;
    this.tokens = Math.min(this.capacity, this.tokens + elapsed * this.perSecond);
    this.last = this.now();
    if (this.tokens >= cost) {
      this.tokens -= cost;
      return 0;
    }
    return Math.ceil(((cost - this.tokens) / this.perSecond) * 1000);
  }

  /** Waits until `cost` tokens are free, then takes them. For a tokens-per-minute limit, cost is the
   *  request's estimated tokens; for requests per minute, it's 1. */
  async take(cost = 1, sleep: Sleep = realSleep): Promise<void> {
    for (let wait = this.tryTake(cost); wait > 0; wait = this.tryTake(cost)) await sleep(wait);
  }
}
