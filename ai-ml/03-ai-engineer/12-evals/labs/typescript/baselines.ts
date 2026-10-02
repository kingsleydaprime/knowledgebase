// baselines.ts — the trivial classifiers a model has to beat to earn its cost.
import type { Case, Classify, Label } from "./harness.ts";

/** Always answer with the most common label in the set. */
export function majority(cases: Case[]): Classify {
  const counts = new Map<Label, number>();
  for (const c of cases) counts.set(c.label, (counts.get(c.label) ?? 0) + 1);
  const top = [...counts].sort((a, b) => b[1] - a[1])[0][0];
  return async () => top;
}

/** A few keyword rules, in the order a support lead would check them. */
export const keywords: Classify = async (ticket) => {
  const t = ticket.toLowerCase();
  if (/charg|refund|invoice|pay|price|subscription|discount|receipt/.test(t)) return "billing";
  if (/crash|error|broken|bug|blank|empty|doesn't work|not working/.test(t)) return "bug";
  if (/add|would be great|should support|could you|please support/.test(t)) return "feature";
  return "other";
};
