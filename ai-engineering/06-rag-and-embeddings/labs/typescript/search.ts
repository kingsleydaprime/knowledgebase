// search.ts — two ways to find relevant chunks (by meaning and by words), and one way to combine them.

/** Cosine similarity: how closely two vectors point the same way, from -1 to 1, whatever their length. */
export function cosine(a: number[], b: number[]): number {
  let dot = 0, na = 0, nb = 0;
  for (let i = 0; i < a.length; i++) {
    dot += a[i] * b[i];
    na += a[i] * a[i];
    nb += b[i] * b[i];
  }
  return na && nb ? dot / Math.sqrt(na * nb) : 0;
}

export const tokens = (text: string) => text.toLowerCase().match(/[a-z0-9]+/g) ?? [];

/** A HAND-MADE embedding for teaching: six dimensions, one per topic, and a small table of words for each.
 *  A real embedding model learns hundreds of dimensions from data; this one shows the idea in a form you
 *  can read: different words with the same meaning land in the same place. */
const TOPICS: Record<string, string[]> = {
  account: ["password", "login", "sign", "account", "locked", "reset"],
  money: ["refund", "refunds", "charge", "charged", "billing", "card", "paid", "plan", "plans"],
  export: ["export", "exports", "csv", "download", "data", "reports"],
  appearance: ["dark", "darker", "light", "theme", "appearance", "mode"],
  delivery: ["ship", "ships", "shipping", "delivery", "parcel", "tracking", "arrive", "arrives"],
  time: ["days", "hour", "minutes", "when", "long", "takes"],
};
const DIMENSIONS = Object.keys(TOPICS);

export function toyEmbed(text: string): number[] {
  const v = DIMENSIONS.map(() => 0);
  for (const t of tokens(text)) DIMENSIONS.forEach((d, i) => TOPICS[d].includes(t) && v[i]++);
  return v;
}

export type Embed = (text: string) => number[] | Promise<number[]>;
export type Ranked = { id: string; score: number }[];

/** Exact nearest neighbours: score every chunk. Fine for thousands; vector databases use approximate
 *  indexes (such as HNSW) to do the same over millions, trading a little recall for speed. */
export async function vectorSearch(query: string, items: { id: string; text: string }[], embed: Embed): Promise<Ranked> {
  const q = await embed(query);
  const scored = await Promise.all(items.map(async (it) => ({ id: it.id, score: cosine(q, await embed(it.text)) })));
  return scored.filter((s) => s.score > 0).sort((a, b) => b.score - a.score);
}

/** BM25, the standard keyword ranking: rare words count for more, repeats count for less each time,
 *  and long chunks don't win just by being long. k1 and b are the usual defaults. */
export function bm25(query: string, items: { id: string; text: string }[], k1 = 1.2, b = 0.75): Ranked {
  const docs = items.map((it) => ({ id: it.id, terms: tokens(it.text) }));
  const avg = docs.reduce((n, d) => n + d.terms.length, 0) / docs.length;
  const df = new Map<string, number>();
  for (const d of docs) for (const t of new Set(d.terms)) df.set(t, (df.get(t) ?? 0) + 1);
  const scored = docs.map((d) => {
    let score = 0;
    for (const t of new Set(tokens(query))) {
      const n = df.get(t) ?? 0;
      if (!n) continue;
      const idf = Math.log((docs.length - n + 0.5) / (n + 0.5) + 1);
      const tf = d.terms.filter((x) => x === t).length;
      score += idf * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + (b * d.terms.length) / avg)));
    }
    return { id: d.id, score };
  });
  return scored.filter((s) => s.score > 0).sort((a, b) => b.score - a.score);
}

/** Reciprocal rank fusion: combine rankings by position, not by score, so a cosine of 0.9 and a BM25
 *  score of 4.2 never have to be compared. k = 60 is the constant from the original paper. */
export function rrf(rankings: Ranked[], k = 60): Ranked {
  const total = new Map<string, number>();
  for (const ranking of rankings) ranking.forEach((r, i) => total.set(r.id, (total.get(r.id) ?? 0) + 1 / (k + i + 1)));
  return [...total].map(([id, score]) => ({ id, score })).sort((a, b) => b.score - a.score);
}
