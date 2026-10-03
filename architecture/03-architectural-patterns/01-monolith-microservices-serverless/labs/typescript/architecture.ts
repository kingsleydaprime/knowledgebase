// architecture.ts — the arithmetic behind choosing a monolith, microservices or serverless: how coordination grows
// with people, how often a shared release breaks, what moving a module behind the network costs, when paying per
// request beats paying for a server, how often a function starts cold, and a checker that keeps a modular
// monolith's boundaries honest. Every function is a model; each says what it assumes.

/** Pairs of people who may need to talk: n(n − 1)/2. It grows with the square of the team, not in step with it. */
export function coordinationLinks(people: number): number {
  return (people * (people - 1)) / 2;
}

/** The chance a release containing `changes` independent changes, each bad with probability p, has at least one bad one. */
export function releaseBreaks(changes: number, p: number): number {
  return 1 - (1 - p) ** changes;
}

/**
 * Moving a module behind the network: every in-process call becomes a network call, which adds time and can
 * fail. Returns the time added to a request and the chance all of its calls succeed.
 */
export function extract(callsPerRequest: number, networkMs: number, callAvailability: number) {
  return { addedMs: callsPerRequest * networkMs, availability: callAvailability ** callsPerRequest };
}

export interface Pricing {
  perMillionRequests: number; // dollars
  perGbSecond: number; // dollars for one second of one gigabyte of memory
}

/** A function platform charges per request plus per gigabyte-second of running time. */
export function serverlessMonthly(requests: number, ms: number, memoryGb: number, price: Pricing): number {
  return (requests / 1e6) * price.perMillionRequests + requests * (ms / 1000) * memoryGb * price.perGbSecond;
}

/** The monthly request count at which paying per request costs the same as a server that's always on. */
export function breakEvenRequests(serverMonthly: number, ms: number, memoryGb: number, price: Pricing): number {
  return serverMonthly / (price.perMillionRequests / 1e6 + (ms / 1000) * memoryGb * price.perGbSecond);
}

/**
 * One function instance stays warm for `warmMinutes` after each request. With requests arriving at random at
 * `perMinute`, a request finds it cold when the gap before it is longer than that: probability e^(−rate × window).
 */
export function coldShare(perMinute: number, warmMinutes: number): number {
  return Math.exp(-perMinute * warmMinutes);
}

/** The same, request by request, with a seeded generator (mulberry32, as in week 1's lab). */
export function simulateColdShare(perMinute: number, warmMinutes: number, requests: number, seed: number): number {
  let a = seed >>> 0;
  const random = () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  let cold = 0;
  for (let i = 0; i < requests; i++) {
    const gapMinutes = -Math.log(1 - random()) / perMinute;
    if (gapMinutes > warmMinutes) cold++;
  }
  return cold / requests;
}

/** A module of a modular monolith, and what it imports: "billing" is billing's public face; "billing/x" is inside it. */
export interface Module {
  name: string;
  imports: string[];
}

/** Imports that reach inside another module instead of going through its public face. */
export function boundaryViolations(modules: readonly Module[]): string[] {
  const names = new Set(modules.map((m) => m.name));
  const violations: string[] = [];
  for (const m of modules) {
    for (const imp of m.imports) {
      const [target, ...inside] = imp.split("/");
      if (target !== m.name && names.has(target) && inside.length > 0) violations.push(`${m.name} → ${imp}`);
    }
  }
  return violations;
}

/** A cycle in the modules' dependencies, as a path that starts and ends at the same module, or undefined if none. */
export function findCycle(modules: readonly Module[]): string[] | undefined {
  const deps = new Map(modules.map((m) => [m.name, [...new Set(m.imports.map((i) => i.split("/")[0]))].filter((d) => d !== m.name)]));
  const state = new Map<string, "visiting" | "done">();
  const path: string[] = [];
  const visit = (name: string): string[] | undefined => {
    if (state.get(name) === "done") return undefined;
    if (state.get(name) === "visiting") return [...path.slice(path.indexOf(name)), name]; // back to a module on the path
    state.set(name, "visiting");
    path.push(name);
    for (const d of deps.get(name) ?? []) {
      const cycle = visit(d);
      if (cycle) return cycle;
    }
    path.pop();
    state.set(name, "done");
    return undefined;
  };
  for (const m of modules) {
    const cycle = visit(m.name);
    if (cycle) return cycle;
  }
  return undefined;
}
