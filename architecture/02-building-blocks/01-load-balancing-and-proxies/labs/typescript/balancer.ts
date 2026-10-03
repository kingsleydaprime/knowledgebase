// balancer.ts — how a load balancer picks a server: the common algorithms, health checks that take a failing
// server out and put it back, and consistent hashing, which keeps a key on the same server as servers come and go.

import { mean, percentile, seeded } from "../../../../01-system-design-fundamentals/02-scalability-and-performance/labs/typescript/scaling.ts";

/** What a balancer can see when it picks: how many requests each server is still working on. */
export type Pick = (outstanding: readonly number[], random: () => number) => number;

/** Each server in turn, ignoring how busy they are. */
export function roundRobin(): Pick {
  let next = 0;
  return (outstanding) => next++ % outstanding.length;
}

/** The server with the fewest requests in progress (least connections). Ties go to the lowest number. */
export const leastOutstanding: Pick = (outstanding) => outstanding.indexOf(Math.min(...outstanding));

/** Any server, at random. */
export const random: Pick = (outstanding, rand) => Math.floor(rand() * outstanding.length);

/** Two servers at random, then the less busy of the two ("power of two choices"). */
export const twoChoices: Pick = (outstanding, rand) => {
  const a = Math.floor(rand() * outstanding.length);
  const b = Math.floor(rand() * outstanding.length);
  return outstanding[b] < outstanding[a] ? b : a;
};

/**
 * Sends random traffic through a balancer to `servers` servers, each working through its own queue one request at
 * a time. Most requests take 10 ms, but 1 in 20 takes 200 ms (a search, a report), which is what makes the
 * algorithms differ. `busy` is the utilisation of the whole pool. Returns latency (wait plus work) in ms.
 */
export function simulate(pick: Pick, servers: number, busy: number, requests: number, seed: number) {
  const rand = seeded(seed);
  const meanWorkMs = 0.95 * 10 + 0.05 * 200;
  const gapMs = meanWorkMs / (busy * servers); // average time between arrivals
  const finishes: number[][] = Array.from({ length: servers }, () => []); // per server: when each queued request ends
  let now = 0;
  const times: number[] = [];
  for (let i = 0; i < requests; i++) {
    now += -gapMs * Math.log(1 - rand());
    for (const queue of finishes) while (queue.length > 0 && queue[0] <= now) queue.shift(); // drop finished ones
    const s = pick(finishes.map((queue) => queue.length), rand);
    const workMs = rand() < 0.05 ? 200 : 10;
    const ends = Math.max(now, finishes[s].at(-1) ?? 0) + workMs; // starts when the server's queue ahead of it is done
    finishes[s].push(ends);
    times.push(ends - now);
  }
  return { mean: Math.round(mean(times)), p50: Math.round(percentile(times, 50)), p99: Math.round(percentile(times, 99)) };
}

/**
 * Weighted round-robin that spreads each server's turns out instead of bunching them (nginx's "smooth" method):
 * every pick, each server gains its weight; the highest is chosen and pays back the total.
 */
export function smoothWeighted(weights: Record<string, number>): () => string {
  const names = Object.keys(weights);
  const total = names.reduce((sum, n) => sum + weights[n], 0);
  const current = new Map(names.map((n) => [n, 0]));
  return () => {
    for (const n of names) current.set(n, current.get(n)! + weights[n]);
    const best = names.reduce((a, b) => (current.get(b)! > current.get(a)! ? b : a));
    current.set(best, current.get(best)! - total);
    return best;
  };
}

/**
 * Tracks one server's health checks. It takes `fall` failures in a row to mark a server down, so one slow
 * check doesn't remove it, and `rise` successes in a row to bring it back, so a flapping server stays out.
 */
export class Health {
  up = true;
  #fall: number;
  #rise: number;
  #streak = 0; // consecutive results that disagree with the current state

  constructor(fall = 3, rise = 2) {
    this.#fall = fall;
    this.#rise = rise;
  }

  record(ok: boolean): void {
    if (ok === this.up) {
      this.#streak = 0; // agrees with what we already believe
      return;
    }
    this.#streak++;
    if (this.#streak >= (this.up ? this.#fall : this.#rise)) {
      this.up = !this.up;
      this.#streak = 0;
    }
  }
}

/** Round-robin over the servers that are up. With none up, there is nowhere to send the request. */
export function pickHealthy(servers: readonly { name: string; health: Health }[], turn: number): string {
  const up = servers.filter((s) => s.health.up);
  if (up.length === 0) throw new Error("no healthy servers: answer 503");
  return up[turn % up.length].name;
}

/** FNV-1a: a small, fast, non-cryptographic hash from a string to a 32-bit number. */
export function hash(text: string): number {
  let h = 0x811c9dc5;
  for (let i = 0; i < text.length; i++) h = Math.imul(h ^ text.charCodeAt(i), 0x01000193) >>> 0;
  // FNV-1a mixes its last characters poorly, which matters for keys like "user:1", "user:2"; finish with a mix step.
  h = Math.imul(h ^ (h >>> 16), 0x85ebca6b) >>> 0;
  h = Math.imul(h ^ (h >>> 13), 0xc2b2ae35) >>> 0;
  return (h ^ (h >>> 16)) >>> 0;
}

/** The naive way to spread keys: hash mod the number of servers. Changing the count moves almost every key. */
export function modulo(key: string, servers: readonly string[]): string {
  return servers[hash(key) % servers.length];
}

/**
 * Consistent hashing: servers and keys are placed on the same circle of hash values, and a key belongs to the
 * first server clockwise from it. Each server is placed `replicas` times (virtual nodes) to even out the arcs.
 * Adding a server takes keys only from its new neighbours.
 */
export class HashRing {
  #points: { at: number; server: string }[] = [];
  #replicas: number;

  constructor(servers: readonly string[], replicas = 100) {
    this.#replicas = replicas;
    for (const s of servers) this.add(s);
  }

  add(server: string): void {
    for (let r = 0; r < this.#replicas; r++) this.#points.push({ at: hash(`${server}#${r}`), server });
    this.#points.sort((a, b) => a.at - b.at);
  }

  remove(server: string): void {
    this.#points = this.#points.filter((p) => p.server !== server);
  }

  serverFor(key: string): string {
    if (this.#points.length === 0) throw new Error("the ring is empty");
    const h = hash(key);
    let lo = 0;
    let hi = this.#points.length; // binary search for the first point at or after h
    while (lo < hi) {
      const mid = (lo + hi) >> 1;
      if (this.#points[mid].at < h) lo = mid + 1;
      else hi = mid;
    }
    return this.#points[lo % this.#points.length].server; // past the last point, wrap round to the first
  }
}
