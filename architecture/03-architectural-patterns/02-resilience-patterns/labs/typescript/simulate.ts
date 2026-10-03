// simulate.ts — a service with two endpoints and one slow dependency, simulated tick by tick, so the
// cascade is visible and the numbers are the same on every run. One tick is 100 ms.

export type Kind = "search" | "profile";
export type Outcome = "ok" | "failed" | "timedOut" | "rejected" | "unfinished";

export type Config = {
  pools: Record<Kind, string>; // which worker pool each endpoint uses; the same name means a shared pool
  sizes: Record<string, number>; // workers per pool
  queueLimit: number; // waiting requests per pool before new ones are turned away (Infinity: never)
  dependencyTimeoutTicks: number; // how long search waits for the slow dependency (Infinity: forever)
};

export type Load = {
  ticks: number;
  arrivalsPerTick: Record<Kind, number>;
  serviceTicks: Record<Kind, number>; // how long each request needs a worker, if nothing times out
  clientTimeoutTicks: number; // how long a caller waits in the queue before giving up
};

type Request = { kind: Kind; arrived: number; endsAt?: number; outcome?: Outcome };

export function simulate(config: Config, load: Load): Record<Kind, Record<Outcome, number>> {
  const counts = { search: blank(), profile: blank() };
  const queues = new Map<string, Request[]>();
  const running = new Map<string, Request[]>();
  for (const pool of Object.keys(config.sizes)) (queues.set(pool, []), running.set(pool, []));

  for (let t = 0; t < load.ticks; t++) {
    for (const [pool, list] of running) { // 1. finished work frees its worker
      running.set(pool, list.filter((r) => (r.endsAt! <= t ? (counts[r.kind][r.outcome!]++, false) : true)));
    }
    for (const [pool, queue] of queues) { // 2. callers who waited too long give up
      queues.set(pool, queue.filter((r) => (t - r.arrived >= load.clientTimeoutTicks ? (counts[r.kind].timedOut++, false) : true)));
    }
    for (const kind of ["search", "profile"] as const) { // 3. new requests arrive, or are turned away
      const queue = queues.get(config.pools[kind])!;
      for (let i = 0; i < load.arrivalsPerTick[kind]; i++) {
        if (queue.length >= config.queueLimit) counts[kind].rejected++; // load shedding: a fast "no" beats a slow one
        else queue.push({ kind, arrived: t });
      }
    }
    for (const [pool, queue] of queues) { // 4. free workers take requests, oldest first
      const busy = running.get(pool)!;
      while (busy.length < config.sizes[pool] && queue.length) {
        const r = queue.shift()!;
        const needs = load.serviceTicks[r.kind];
        const limit = r.kind === "search" ? config.dependencyTimeoutTicks : Infinity;
        r.endsAt = t + Math.min(needs, limit); // a timeout frees the worker early, but the request fails
        r.outcome = needs > limit ? "failed" : "ok";
        busy.push(r);
      }
    }
  }
  for (const list of [...queues.values(), ...running.values()]) for (const r of list) counts[r.kind].unfinished++;
  return counts;
}

const blank = (): Record<Outcome, number> => ({ ok: 0, failed: 0, timedOut: 0, rejected: 0, unfinished: 0 });

/** Little's law: the average number of requests in a system is their arrival rate times how long each
 *  stays. If that's more than the workers you have, the queue grows until something gives. */
export const workersNeeded = (perSecond: number, seconds: number) => perSecond * seconds;
