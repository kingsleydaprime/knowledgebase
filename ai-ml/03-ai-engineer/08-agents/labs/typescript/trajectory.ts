// trajectory.ts — score how an agent got there, not only where it ended up.
import type { Outcome } from "./agent.ts";

export type Expect = {
  status?: Outcome["status"];
  mustCall?: string[]; // tools that must appear somewhere in the trace
  mustNotCall?: string[]; // tools that must never be requested
  maxSteps?: number;
  answerMatches?: RegExp;
};

/** Every expectation the trace breaks, in words. An empty list is a pass. */
export function scoreTrajectory(outcome: Outcome, expect: Expect): string[] {
  const called = outcome.trace.flatMap((s) => s.calls.map((c) => c.name));
  const failures: string[] = [];
  if (expect.status && outcome.status !== expect.status) failures.push(`ended ${outcome.status}, expected ${expect.status}`);
  for (const name of expect.mustCall ?? []) if (!called.includes(name)) failures.push(`never called ${name}`);
  for (const name of expect.mustNotCall ?? []) if (called.includes(name)) failures.push(`called ${name}`);
  if (expect.maxSteps && outcome.trace.length > expect.maxSteps) failures.push(`took ${outcome.trace.length} steps, expected at most ${expect.maxSteps}`);
  if (expect.answerMatches && !expect.answerMatches.test(outcome.answer ?? "")) failures.push(`answer doesn't match ${expect.answerMatches}`);
  return failures;
}
