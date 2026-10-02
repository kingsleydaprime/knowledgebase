// agent.ts — the tool loop from the tools lesson, with the controls that make it safe to give more freedom:
// limits on steps and tokens, a stop when it repeats itself, a trace of every step, and a reason it ended.
import type { Message, Turn } from "../../../07-tools-and-mcp/labs/typescript/loop.ts";
import { type Approve, execute, specs, type Tool, type ToolSpec } from "../../../07-tools-and-mcp/labs/typescript/tools.ts";

export type AgentTurn = Turn & { usage?: { inputTokens: number; outputTokens: number } };
export type AgentModel = (messages: Message[], tools: ToolSpec[]) => Promise<AgentTurn>;

export type Limits = { maxSteps: number; maxTokens: number; maxRepeats: number };
export const DEFAULT_LIMITS: Limits = { maxSteps: 8, maxTokens: 50_000, maxRepeats: 2 };

export type Step = { step: number; calls: { name: string; arguments: string; isError: boolean }[]; tokens: number; text: string };
export type Outcome = {
  status: "answered" | "step_limit" | "token_limit" | "stuck";
  answer?: string;
  trace: Step[];
  messages: Message[];
};

export async function runAgent(
  model: AgentModel,
  messages: Message[],
  tools: Tool[],
  { limits = DEFAULT_LIMITS, approve = () => false }: { limits?: Limits; approve?: Approve } = {},
): Promise<Outcome> {
  const history = [...messages];
  const trace: Step[] = [];
  const seen = new Map<string, number>(); // how many times each exact call has been made
  let tokens = 0;
  const end = (status: Outcome["status"], answer?: string): Outcome => ({ status, answer, trace, messages: history });

  for (let step = 1; step <= limits.maxSteps; step++) {
    const turn = await model(history, specs(tools));
    const used = (turn.usage?.inputTokens ?? 0) + (turn.usage?.outputTokens ?? 0);
    tokens += used;
    history.push({ role: "assistant", content: turn.content, toolCalls: turn.toolCalls });
    const record: Step = { step, calls: [], tokens: used, text: turn.content };
    trace.push(record);
    if (turn.toolCalls.length === 0) return end("answered", turn.content);

    // The same call with the same arguments, again and again, means the agent is going round in circles.
    for (const call of turn.toolCalls) {
      const key = `${call.name} ${call.arguments}`;
      seen.set(key, (seen.get(key) ?? 0) + 1);
      if (seen.get(key)! > limits.maxRepeats) return end("stuck");
    }

    // Read-only calls run at the same time; anything with side effects runs alone, in order, after them.
    const sideEffects = new Set(tools.filter((t) => t.sideEffects).map((t) => t.name));
    const results = new Map<string, Awaited<ReturnType<typeof execute>>>();
    const readOnly = turn.toolCalls.filter((c) => !sideEffects.has(c.name));
    await Promise.all(readOnly.map(async (c) => results.set(c.id, await execute(c, tools, approve))));
    for (const c of turn.toolCalls.filter((c) => sideEffects.has(c.name))) results.set(c.id, await execute(c, tools, approve));

    for (const call of turn.toolCalls) { // results go back in the order of the calls, whatever order they finished in
      const result = results.get(call.id)!;
      history.push({ role: "tool", toolCallId: call.id, content: result.isError ? `ERROR: ${result.content}` : result.content });
      record.calls.push({ name: call.name, arguments: call.arguments, isError: result.isError });
    }
    if (tokens > limits.maxTokens) return end("token_limit");
  }
  return end("step_limit");
}
