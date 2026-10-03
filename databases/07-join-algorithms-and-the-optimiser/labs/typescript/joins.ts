// joins.ts — the three join algorithms, written out, each counting its work; and the arithmetic of two classic
// estimation failures. The same model as the Python lab. Rows are [key, value] pairs.

export type Row = readonly [number, string];
export type Joined = [string, string][];

/** For every outer row, look at every inner row: N × M comparisons. */
export function nestedLoop(outer: readonly Row[], inner: readonly Row[]): [Joined, number] {
  const out: Joined = [];
  let comparisons = 0;
  for (const [ok, ov] of outer) {
    for (const [ik, iv] of inner) {
      comparisons++;
      if (ok === ik) out.push([ov, iv]);
    }
  }
  return [out, comparisons];
}

/** The inner side has an index (a sorted list searched by halving): about N × log₂ M steps. */
export function indexNestedLoop(outer: readonly Row[], innerSorted: readonly Row[]): [Joined, number] {
  const out: Joined = [];
  let steps = 0;
  for (const [ok, ov] of outer) {
    let lo = 0;
    let hi = innerSorted.length;
    while (lo < hi) {
      steps++;
      const mid = (lo + hi) >> 1;
      if (innerSorted[mid][0] < ok) lo = mid + 1;
      else hi = mid;
    }
    for (; lo < innerSorted.length && innerSorted[lo][0] === ok; lo++) out.push([ov, innerSorted[lo][1]]);
  }
  return [out, steps];
}

/** Build a hash table on the inner side, probe it once per outer row: N + M operations. Equality only. */
export function hashJoin(outer: readonly Row[], inner: readonly Row[]): [Joined, number] {
  const table = new Map<number, string[]>();
  for (const [ik, iv] of inner) table.set(ik, [...(table.get(ik) ?? []), iv]);
  const out: Joined = [];
  for (const [ok, ov] of outer) for (const iv of table.get(ok) ?? []) out.push([ov, iv]);
  return [out, inner.length + outer.length];
}

/** Both sides sorted by key: walk them together like merging two sorted lists, about N + M steps. */
export function mergeJoin(outerSorted: readonly Row[], innerSorted: readonly Row[]): [Joined, number] {
  const out: Joined = [];
  let steps = 0;
  let i = 0;
  let j = 0;
  while (i < outerSorted.length && j < innerSorted.length) {
    steps++;
    const [ok, ik] = [outerSorted[i][0], innerSorted[j][0]];
    if (ok < ik) i++;
    else if (ok > ik) j++;
    else {
      for (let k = j; k < innerSorted.length && innerSorted[k][0] === ok; k++) out.push([outerSorted[i][1], innerSorted[k][1]]);
      i++; // the next outer row may share the key, so j stays at the start of the group
    }
  }
  return [out, steps];
}

/** What a planner assumes for `a AND b` without extended statistics: the selectivities multiply. */
export function independentEstimate(rows: number, ...selectivities: number[]): number {
  return selectivities.reduce((estimate, s) => estimate * s, rows);
}

/** OFFSET reads and discards every skipped row; keyset pagination starts at the right place. */
export function rowsReadForPage(offset: number, limit: number, keyset: boolean): number {
  return keyset ? limit : offset + limit;
}
