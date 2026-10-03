// scaling.ts — the arithmetic behind performance and scalability: percentiles, how waiting grows as a server
// fills up, the bottleneck that sets a system's throughput, and why adding machines stops helping.
// These are models: each function says what it assumes.

/** The value at or below which p% of samples fall (the nearest-rank method). p99 of 1,000 samples is the 990th smallest. */
export function percentile(samples: readonly number[], p: number): number {
  if (samples.length === 0) throw new RangeError("no samples");
  const sorted = [...samples].sort((a, b) => a - b);
  const rank = Math.max(1, Math.ceil((p / 100) * sorted.length));
  return sorted[rank - 1];
}

export function mean(samples: readonly number[]): number {
  return samples.reduce((sum, x) => sum + x, 0) / samples.length;
}

/** A small seeded random number generator (mulberry32), so every run sees the same "random" traffic. */
export function seeded(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** An exponentially distributed wait with the given mean: how long until the next random event. */
function exponential(random: () => number, mean: number): number {
  return -mean * Math.log(1 - random());
}

/**
 * Average time a request spends in a single server, waiting plus being served, when requests arrive at random
 * and service times vary at random (the M/M/1 queueing model): service time ÷ (1 − utilisation).
 * Utilisation is the fraction of time the server is busy: arrival rate × service time.
 */
export function responseTime(serviceMs: number, utilisation: number): number {
  return utilisation >= 1 ? Infinity : serviceMs / (1 - utilisation);
}

/** The same server, simulated request by request, to check the formula and to see the tail it doesn't show. */
export function simulateServer(serviceMs: number, utilisation: number, requests: number, seed: number) {
  const random = seeded(seed);
  const gapMs = serviceMs / utilisation; // average time between arrivals
  let arrives = 0;
  let free = 0; // when the server finishes its current request
  const times: number[] = [];
  for (let i = 0; i < requests; i++) {
    arrives += exponential(random, gapMs);
    const starts = Math.max(arrives, free); // wait if the server is busy
    free = starts + exponential(random, serviceMs);
    times.push(free - arrives);
  }
  return { mean: mean(times), p50: percentile(times, 50), p99: percentile(times, 99) };
}

export interface Stage {
  name: string;
  perSecond: number; // the most requests this stage can handle a second
}

/** A request passes through every stage, so the system handles only as many as its slowest stage. */
export function throughput(stages: readonly Stage[]): { perSecond: number; bottleneck: string } {
  const slowest = stages.reduce((a, b) => (b.perSecond < a.perSecond ? b : a));
  return { perSecond: slowest.perSecond, bottleneck: slowest.name };
}

/** Amdahl's law: n machines speed up the part that can be split, not the part that can't (`serial`, 0 to 1). */
export function amdahl(n: number, serial: number): number {
  return 1 / (serial + (1 - serial) / n);
}

/**
 * The universal scalability law: capacity of n machines relative to one, when they also wait for each other
 * (contention, alpha) and must keep each other in step (coherence, beta). Past a point, adding machines lowers it.
 */
export function usl(n: number, alpha: number, beta: number): number {
  return n / (1 + alpha * (n - 1) + beta * n * (n - 1));
}

/** Where the universal scalability law peaks: the number of machines that gives the most capacity. */
export function uslPeak(alpha: number, beta: number): number {
  return Math.sqrt((1 - alpha) / beta);
}
