// judge.ts — LLM-as-judge for outputs code can't check, and the checks on the judge itself.

export type Ask = (prompt: string) => Promise<string>;

/** Binary criteria, each one a question a careful person would answer the same way twice. */
export const replyRubric = [
  "The reply addresses the customer's actual problem.",
  "The reply promises nothing the ticket gives no basis for (no refunds, dates or fixes that weren't agreed).",
  "The reply is under 80 words.",
  "The reply asks for any information needed to act, or says nothing is needed.",
];

export function rubricPrompt(ticket: string, reply: string, rubric: string[]): string {
  return [
    "You are grading a support reply. For each numbered criterion, answer PASS or FAIL, one per line,",
    'in the form "1: PASS". Judge only what is written. Do not reward length or politeness.',
    "",
    "<ticket>", ticket, "</ticket>",
    "<reply>", reply, "</reply>",
    "",
    ...rubric.map((criterion, i) => `${i + 1}. ${criterion}`),
  ].join("\n");
}

/** One verdict per criterion. A criterion the judge didn't answer counts as a failure, not a pass. */
export async function judge(ask: Ask, ticket: string, reply: string, rubric = replyRubric) {
  const answer = await ask(rubricPrompt(ticket, reply, rubric));
  const verdicts = rubric.map((criterion, i) => {
    const line = answer.match(new RegExp(`^\\s*${i + 1}\\s*[:.)]\\s*(PASS|FAIL)`, "im"));
    return { criterion, pass: line?.[1].toUpperCase() === "PASS", answered: Boolean(line) };
  });
  return { verdicts, pass: verdicts.every((v) => v.pass) };
}

/** Which of two replies is better? Ask in both orders: a judge that just prefers whatever comes
 *  first (position bias) gives opposite answers, and that's reported instead of trusted. */
export async function pairwise(ask: Ask, ticket: string, a: string, b: string): Promise<"a" | "b" | "inconsistent"> {
  const prompt = (first: string, second: string) =>
    `Which support reply is better for this ticket? Answer only FIRST or SECOND.\n<ticket>\n${ticket}\n</ticket>\n` +
    `<first>\n${first}\n</first>\n<second>\n${second}\n</second>`;
  const pick = (answer: string) => (/\bfirst\b/i.test(answer) ? "first" : /\bsecond\b/i.test(answer) ? "second" : null);
  const forward = pick(await ask(prompt(a, b)));  // a shown first
  const backward = pick(await ask(prompt(b, a))); // b shown first
  if (forward === "first" && backward === "second") return "a";
  if (forward === "second" && backward === "first") return "b";
  return "inconsistent";
}

/** How far to trust the judge: compare it with a human on the same items.
 *  Kappa corrects for agreement you'd get by chance; a lenient judge that passes almost everything
 *  can agree often and still have a kappa near zero. */
export function agreement(judgeSays: boolean[], humanSays: boolean[]) {
  const n = judgeSays.length;
  const agree = judgeSays.filter((j, i) => j === humanSays[i]).length / n;
  const judgeYes = judgeSays.filter(Boolean).length / n;
  const humanYes = humanSays.filter(Boolean).length / n;
  const chance = judgeYes * humanYes + (1 - judgeYes) * (1 - humanYes);
  return { agreement: agree, kappa: chance === 1 ? 1 : (agree - chance) / (1 - chance) };
}
