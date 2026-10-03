// cache.ts — a cache in front of a slow store: a size-limited LRU cache with expiry, the cache-aside pattern with
// request coalescing, and the arithmetic that says how much a cache takes off the database.
// The clock is passed in, so tests can move time forward instead of waiting.

interface Entry<V> {
  value: V;
  expires: number; // the clock time after which this entry is stale and must not be served
}

/** Holds at most `max` entries. When full, it evicts the least recently used one. Each entry expires after its TTL. */
export class LruCache<V> {
  #max: number;
  #now: () => number;
  #entries = new Map<string, Entry<V>>(); // a Map keeps insertion order: the first key is the least recently used

  constructor(max: number, now: () => number = Date.now) {
    if (max < 1) throw new RangeError("a cache needs room for at least one entry");
    this.#max = max;
    this.#now = now;
  }

  get(key: string): V | undefined {
    const entry = this.#entries.get(key);
    if (entry === undefined) return undefined;
    if (this.#now() >= entry.expires) {
      this.#entries.delete(key); // expired: treat it as a miss
      return undefined;
    }
    this.#entries.delete(key); // move it to the back: it's now the most recently used
    this.#entries.set(key, entry);
    return entry.value;
  }

  set(key: string, value: V, ttlMs: number): void {
    this.#entries.delete(key);
    this.#entries.set(key, { value, expires: this.#now() + ttlMs });
    if (this.#entries.size > this.#max) {
      const oldest = this.#entries.keys().next().value!;
      this.#entries.delete(oldest);
    }
  }

  delete(key: string): void {
    this.#entries.delete(key);
  }

  keys(): string[] {
    return [...this.#entries.keys()]; // least recently used first
  }
}

/**
 * Cache-aside: the application checks the cache first; on a miss it loads from the store and fills the cache.
 * With `coalesce`, concurrent misses for one key share a single load instead of each going to the store.
 */
export class CacheAside<V> {
  hits = 0;
  misses = 0;
  #cache: LruCache<V>;
  #load: (key: string) => Promise<V>;
  #ttlMs: number;
  #coalesce: boolean;
  #inFlight = new Map<string, Promise<V>>();

  constructor(cache: LruCache<V>, load: (key: string) => Promise<V>, options: { ttlMs: number; coalesce?: boolean }) {
    this.#cache = cache;
    this.#load = load;
    this.#ttlMs = options.ttlMs;
    this.#coalesce = options.coalesce ?? false;
  }

  async get(key: string): Promise<V> {
    const cached = this.#cache.get(key);
    if (cached !== undefined) {
      this.hits++;
      return cached;
    }
    this.misses++;
    if (this.#coalesce) {
      const pending = this.#inFlight.get(key);
      if (pending) return pending; // someone is already loading this key: wait for their answer
    }
    const loading = this.#load(key).then((value) => {
      this.#cache.set(key, value, this.#ttlMs);
      return value;
    });
    if (this.#coalesce) {
      this.#inFlight.set(key, loading);
      loading.finally(() => this.#inFlight.delete(key)).catch(() => {}); // a failed load isn't kept: the next miss retries
    }
    return loading;
  }

  /** Write to the store first, then delete the cached copy so the next read loads the new value. */
  async write(key: string, value: V, save: (key: string, value: V) => Promise<void>): Promise<void> {
    await save(key, value);
    this.#cache.delete(key);
  }
}

/** The share of reads the cache answers. */
export function hitRatio(hits: number, misses: number): number {
  return hits / (hits + misses);
}

/** Average read time: every read asks the cache, and a miss also pays for the store. */
export function averageReadMs(hitRatio: number, cacheMs: number, storeMs: number): number {
  return cacheMs + (1 - hitRatio) * storeMs;
}

/** Reads a second that still reach the store: only the misses. */
export function storeReadsPerSecond(readsPerSecond: number, hitRatio: number): number {
  return readsPerSecond * (1 - hitRatio);
}

/** A TTL spread by ±`spread` (0.1 is ±10%), so keys written together don't all expire in the same instant. */
export function jittered(ttlMs: number, spread: number, random: () => number): number {
  return ttlMs * (1 - spread + 2 * spread * random());
}

/**
 * Picks key numbers 0..keys-1 with a Zipf distribution: key k is requested in proportion to 1/(k+1)^s.
 * Real traffic looks like this: a few items are very popular and a long tail is rarely asked for.
 */
export function zipf(keys: number, s: number, random: () => number): () => number {
  const cumulative: number[] = [];
  let total = 0;
  for (let k = 0; k < keys; k++) cumulative.push((total += 1 / (k + 1) ** s));
  return () => {
    const target = random() * total;
    let lo = 0;
    let hi = keys - 1;
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (cumulative[mid] < target) lo = mid + 1;
      else hi = mid;
    }
    return lo;
  };
}
