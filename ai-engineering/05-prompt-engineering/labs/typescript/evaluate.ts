// evaluate.ts — score a prompt against labelled cases, so "this wording feels better" becomes a number.
import { type Example, type Label, fenceUserText, formatExamples, parseLabel, render } from "./prompt.ts";

export type Ask = (prompt: string) => Promise<string>;
export type CaseResult = { review: string; expected: Label; got: Label | null; reply: string };

export async function evaluate(ask: Ask, template: string, cases: Example[], examples: Example[] = []) {
  const results: CaseResult[] = [];
  for (const c of cases) {
    const values: Record<string, string> = { review: fenceUserText(c.review) };
    if (template.includes("{{examples}}")) values.examples = formatExamples(examples);
    const reply = await ask(render(template, values));
    results.push({ review: c.review, expected: c.label, got: parseLabel(reply), reply });
  }
  const correct = results.filter((r) => r.got === r.expected).length;
  return { accuracy: correct / cases.length, correct, total: cases.length, failures: results.filter((r) => r.got !== r.expected) };
}
