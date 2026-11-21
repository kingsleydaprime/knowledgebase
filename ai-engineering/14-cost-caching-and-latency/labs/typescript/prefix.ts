// prefix.ts — why a prompt cache misses: find where two requests stop being identical.

/** How many leading characters two prompts share. A prompt cache can reuse at most this much. */
export function sharedPrefix(a: string, b: string): number {
  let i = 0;
  while (i < a.length && i < b.length && a[i] === b[i]) i++;
  return i;
}

/** Where they diverge, with a little context, for a log line or a test failure. */
export function divergence(a: string, b: string, context = 20): string {
  const at = sharedPrefix(a, b);
  if (at === a.length && at === b.length) return "identical";
  const show = (s: string) => JSON.stringify(s.slice(Math.max(0, at - context), at + context));
  return `differ at character ${at}: ${show(a)} vs ${show(b)}`;
}

/** JSON with object keys sorted, so the same data always gives the same bytes.
 *  JSON.stringify keeps insertion order, so {b, a} and {a, b} would never share a cache entry. */
export function stableJson(value: unknown): string {
  return JSON.stringify(value, (_key, v) =>
    v && typeof v === "object" && !Array.isArray(v)
      ? Object.fromEntries(Object.entries(v).sort(([x], [y]) => (x < y ? -1 : x > y ? 1 : 0)))
      : v,
  );
}
