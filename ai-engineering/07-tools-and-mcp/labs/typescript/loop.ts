// loop.ts — the tool-calling round trip: the model asks, your code runs, the result goes back, repeat.
import { type Approve, execute, specs, type Tool, type ToolCall, type ToolSpec } from "./tools.ts";

export type Message =
  | { role: "system" | "user"; content: string }
  | { role: "assistant"; content: string; toolCalls?: ToolCall[] }
  | { role: "tool"; toolCallId: string; content: string };

/** One model turn: some text, and zero or more tool calls. No tool calls means "this is my answer". */
export type Turn = { content: string; toolCalls: ToolCall[] };
export type ToolModel = (messages: Message[], tools: ToolSpec[]) => Promise<Turn>;

export async function answerWithTools(
  model: ToolModel,
  messages: Message[],
  tools: Tool[],
  { approve = () => false, maxRounds = 5 }: { approve?: Approve; maxRounds?: number } = {},
): Promise<{ answer: string; messages: Message[]; rounds: number }> {
  const history = [...messages];
  for (let round = 1; round <= maxRounds; round++) {
    const turn = await model(history, specs(tools));
    history.push({ role: "assistant", content: turn.content, toolCalls: turn.toolCalls });
    if (turn.toolCalls.length === 0) return { answer: turn.content, messages: history, rounds: round };
    for (const call of turn.toolCalls) {
      const result = await execute(call, tools, approve);
      // Every call gets exactly one result, in the same order, even when it failed.
      history.push({ role: "tool", toolCallId: call.id, content: result.isError ? `ERROR: ${result.content}` : result.content });
    }
  }
  throw new Error(`no answer after ${maxRounds} rounds of tool calls`);
}
