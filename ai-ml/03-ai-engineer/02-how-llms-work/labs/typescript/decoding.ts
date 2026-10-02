// decoding.ts — how a model turns scores into a next token, and generates one token at a time.

/** A seeded random generator (mulberry32), so sampling is repeatable in tests. */
export function seededRandom(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export type Distribution = Map<string, number>; // token -> probability, summing to 1

/** Softmax with temperature: divide the scores by T, then exponentiate and normalise.
 *  T < 1 sharpens the distribution toward the top token; T > 1 flattens it. */
export function softmax(scores: Map<string, number>, temperature: number): Distribution {
  const scaled = [...scores].map(([token, s]) => [token, s / temperature] as const);
  const max = Math.max(...scaled.map(([, s]) => s)); // subtract the max to avoid overflow
  const exps = scaled.map(([token, s]) => [token, Math.exp(s - max)] as const);
  const total = exps.reduce((sum, [, e]) => sum + e, 0);
  return new Map(exps.map(([token, e]) => [token, e / total]));
}

/** Keep only the k most likely tokens, renormalised. */
export function topK(dist: Distribution, k: number): Distribution {
  return renormalise([...dist].sort((a, b) => b[1] - a[1]).slice(0, k));
}

/** Keep the smallest set of most-likely tokens whose probabilities add up to at least p. */
export function topP(dist: Distribution, p: number): Distribution {
  const kept: [string, number][] = [];
  let cumulative = 0;
  for (const entry of [...dist].sort((a, b) => b[1] - a[1])) {
    kept.push(entry);
    cumulative += entry[1];
    if (cumulative >= p) break;
  }
  return renormalise(kept);
}

function renormalise(entries: [string, number][]): Distribution {
  const total = entries.reduce((sum, [, p]) => sum + p, 0);
  return new Map(entries.map(([token, p]) => [token, p / total]));
}

/** Pick one token: walk the cumulative probabilities until passing a random number in [0, 1). */
export function sample(dist: Distribution, random: () => number): string {
  let r = random();
  for (const [token, p] of dist) {
    if ((r -= p) < 0) return token;
  }
  return [...dist.keys()].at(-1)!;
}

export function greedy(dist: Distribution): string {
  return [...dist].sort((a, b) => b[1] - a[1])[0][0];
}

/** A toy language model: counts which token follows which in a tiny corpus (a "bigram" model).
 *  Real models score every token in a vocabulary of ~100,000 with a neural network; the
 *  generate loop below is the same either way. */
export function trainBigrams(corpus: string): Map<string, Map<string, number>> {
  const tokens = corpus.split(/\s+/).filter(Boolean);
  const counts = new Map<string, Map<string, number>>();
  for (let i = 0; i < tokens.length - 1; i++) {
    const next = counts.get(tokens[i]) ?? new Map();
    next.set(tokens[i + 1], (next.get(tokens[i + 1]) ?? 0) + 1);
    counts.set(tokens[i], next);
  }
  return counts;
}

export type DecodingOptions = { temperature: number; topK?: number; topP?: number; maxTokens: number; stop?: string };

/** Autoregressive generation: score the next token, pick one, append it, repeat. */
export function generate(model: Map<string, Map<string, number>>, start: string, opts: DecodingOptions, random: () => number): string[] {
  const out = [start];
  for (let i = 0; i < opts.maxTokens; i++) {
    const counts = model.get(out.at(-1)!);
    if (!counts) break; // no known continuation
    const scores = new Map([...counts].map(([t, c]) => [t, Math.log(c)])); // log-counts as scores
    let dist = opts.temperature === 0 ? new Map([[greedy(softmax(scores, 1)), 1]]) : softmax(scores, opts.temperature);
    if (opts.topK) dist = topK(dist, opts.topK);
    if (opts.topP) dist = topP(dist, opts.topP);
    const token = sample(dist, random);
    if (token === opts.stop) break;
    out.push(token);
  }
  return out;
}

/** The usual rule of thumb for English: about 4 characters per token. */
export const estimateTokens = (text: string) => Math.ceil(text.length / 4);
