// bulkhead.ts — a limit on how much of the service one dependency may use: at most `maxConcurrent` calls
// at once, at most `maxQueue` waiting, and an immediate rejection beyond that.

export class BulkheadFull extends Error {
  override name = "BulkheadFull";
}

export class Bulkhead {
  private active = 0;
  private readonly waiting: (() => void)[] = [];
  private readonly maxConcurrent: number;
  private readonly maxQueue: number;

  constructor(maxConcurrent: number, maxQueue: number) {
    this.maxConcurrent = maxConcurrent;
    this.maxQueue = maxQueue;
  }

  get stats() {
    return { active: this.active, waiting: this.waiting.length };
  }

  async run<T>(fn: () => Promise<T>): Promise<T> {
    if (this.active < this.maxConcurrent) {
      this.active++;
    } else if (this.waiting.length < this.maxQueue) {
      await new Promise<void>((resolve) => this.waiting.push(resolve)); // woken holding a place already counted
    } else {
      // A fast "no" now is better than a slow failure later, for the caller and for everyone else.
      throw new BulkheadFull(`${this.active} running and ${this.waiting.length} waiting`);
    }
    try {
      return await fn();
    } finally {
      // Hand the place straight to the oldest waiting call, without freeing it first. Freeing it and then
      // waking the waiter would let a call arriving in between take it: two running in a bulkhead of one.
      const next = this.waiting.shift();
      if (next) next();
      else this.active--;
    }
  }
}
