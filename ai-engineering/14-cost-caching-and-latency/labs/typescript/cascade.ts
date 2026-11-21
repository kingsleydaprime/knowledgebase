// cascade.ts — answer with the cheap option when its answer passes a check; pay for the expensive one only when it doesn't.

export type Tier = {
  name: string;
  costUsd: number; // per call, estimated from typical usage
  answer: (input: string) => Promise<string>;
  accept: (answer: string) => boolean; // the check; the last tier's answer is used whatever it says
};

export async function cascade(input: string, tiers: Tier[]): Promise<{ answer: string; by: string; costUsd: number }> {
  let costUsd = 0;
  for (const [i, tier] of tiers.entries()) {
    const answer = await tier.answer(input);
    costUsd += tier.costUsd; // a rejected answer was still paid for
    if (i === tiers.length - 1 || tier.accept(answer)) return { answer, by: tier.name, costUsd };
  }
  throw new Error("a cascade needs at least one tier");
}
