// harness.ts — run a classifier over the golden set, score it, and decide whether a change may ship.
import { readFileSync } from "node:fs";

export const LABELS = ["bug", "billing", "feature", "other"] as const;
export type Label = (typeof LABELS)[number];
export type Case = { id: string; ticket: string; label: Label; tags: string[] };
export type Classify = (ticket: string) => Promise<string>; // returns the raw reply

/** The golden set is a file in version control: one JSON object per line, reviewed like code. */
export function loadGolden(path = new URL("../shared/golden.jsonl", import.meta.url)): Case[] { // shared by every language
  return readFileSync(path, "utf8").split("\n").filter(Boolean).map((line) => JSON.parse(line));
}

/** Exact match on a closed set: the cheapest, most reliable scorer there is. */
export function parseLabel(reply: string): Label | null {
  const found = new Set(reply.toLowerCase().match(/\b(bug|billing|feature|other)\b/g) ?? []);
  return found.size === 1 ? ([...found][0] as Label) : null;
}

/** Wilson score interval: where the true pass rate probably lies (95%), given a small sample. */
export function wilson(passed: number, total: number, z = 1.96): [number, number] {
  if (total === 0) return [0, 1];
  const p = passed / total;
  const centre = p + (z * z) / (2 * total);
  const spread = z * Math.sqrt((p * (1 - p)) / total + (z * z) / (4 * total * total));
  const denominator = 1 + (z * z) / total;
  return [(centre - spread) / denominator, (centre + spread) / denominator];
}

export type CaseResult = { id: string; expected: Label; got: Label | null; reply: string; pass: boolean; tags: string[] };
export type Result = {
  results: CaseResult[];
  passed: number;
  total: number;
  rate: number;
  interval: [number, number];
  byTag: Record<string, { passed: number; total: number }>;
};

export async function runEval(classify: Classify, cases: Case[]): Promise<Result> {
  const results: CaseResult[] = [];
  for (const c of cases) {
    const reply = await classify(c.ticket);
    const got = parseLabel(reply);
    results.push({ id: c.id, expected: c.label, got, reply, pass: got === c.label, tags: c.tags });
  }
  const passed = results.filter((r) => r.pass).length;
  const byTag: Result["byTag"] = {};
  for (const r of results) {
    for (const tag of r.tags) {
      byTag[tag] ??= { passed: 0, total: 0 };
      byTag[tag].total++;
      if (r.pass) byTag[tag].passed++;
    }
  }
  return { results, passed, total: results.length, rate: passed / results.length, interval: wilson(passed, results.length), byTag };
}

/** Which cases changed between two runs: a single pass rate hides a fix that broke something else. */
export function compare(before: Result, after: Result) {
  const was = new Map(before.results.map((r) => [r.id, r.pass]));
  return {
    fixed: after.results.filter((r) => r.pass && was.get(r.id) === false).map((r) => r.id),
    broke: after.results.filter((r) => !r.pass && was.get(r.id) === true).map((r) => r.id),
  };
}

export type GateRules = { minRate: number; baseline?: Result; mustPass?: string[] };

/** The CI gate: fail below a floor, on any regression from the baseline, or on a must-pass case. */
export function gate(result: Result, rules: GateRules): { ok: boolean; reasons: string[] } {
  const reasons: string[] = [];
  if (result.rate < rules.minRate) reasons.push(`pass rate ${pct(result.rate)} is below the floor of ${pct(rules.minRate)}`);
  if (rules.baseline) {
    const { broke } = compare(rules.baseline, result);
    if (broke.length) reasons.push(`regressed on ${broke.join(", ")}`);
  }
  for (const id of rules.mustPass ?? []) {
    if (!result.results.find((r) => r.id === id)?.pass) reasons.push(`must-pass case ${id} failed`);
  }
  return { ok: reasons.length === 0, reasons };
}

export const pct = (x: number) => `${Math.round(x * 100)}%`;
