// rates.ts — one interface, one real source, three wrappers that compose
export interface RateSource {
  rate(from: string, to: string): Promise<number>;
}

// Stands in for a slow, flaky HTTP API. Fails the first `failures` calls.
export class FlakyApi implements RateSource {
  calls = 0;
  failures: number;
  constructor(failures: number) {
    this.failures = failures;
  }
  async rate(from: string, to: string) {
    this.calls++;
    if (this.calls <= this.failures) throw new Error("503 from rates API");
    return from === "GBP" && to === "NGN" ? 2000 : 1;
  }
}

// Decorator: adds retries. Same interface in, same interface out.
export class Retrying implements RateSource {
  inner: RateSource;
  attempts: number;
  constructor(inner: RateSource, attempts: number) {
    this.inner = inner;
    this.attempts = attempts;
  }
  async rate(from: string, to: string) {
    let lastError: unknown;
    for (let i = 0; i < this.attempts; i++) {
      try {
        return await this.inner.rate(from, to);
      } catch (err) {
        lastError = err;
      }
    }
    throw lastError;
  }
}

// Proxy: controls access — answers from memory when it can.
export class Caching implements RateSource {
  inner: RateSource;
  cache = new Map<string, number>();
  constructor(inner: RateSource) {
    this.inner = inner;
  }
  async rate(from: string, to: string) {
    const key = `${from}->${to}`;
    const hit = this.cache.get(key);
    if (hit !== undefined) return hit;
    const value = await this.inner.rate(from, to);
    this.cache.set(key, value);
    return value;
  }
}

// Decorator: adds logging.
export class Logging implements RateSource {
  inner: RateSource;
  log: string[];
  constructor(inner: RateSource, log: string[]) {
    this.inner = inner;
    this.log = log;
  }
  async rate(from: string, to: string) {
    const value = await this.inner.rate(from, to);
    this.log.push(`${from}->${to} = ${value}`);
    return value;
  }
}

// Adapter: a third-party client with the wrong shape, made to fit RateSource.
export class ThirdPartyFx {
  async getQuote(pair: { base: string; quote: string }) {
    return { pair: `${pair.base}/${pair.quote}`, mid: pair.base === "USD" ? 1500 : 1 };
  }
}
export class ThirdPartyFxAdapter implements RateSource {
  client: ThirdPartyFx;
  constructor(client: ThirdPartyFx) {
    this.client = client;
  }
  async rate(from: string, to: string) {
    const quote = await this.client.getQuote({ base: from, quote: to });
    return quote.mid;
  }
}
