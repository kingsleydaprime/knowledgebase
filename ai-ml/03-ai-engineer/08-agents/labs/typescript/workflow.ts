// workflow.ts — the same refund question answered by fixed steps written in code. The model writes one
// sentence at the end and has no tools at all. When the steps are known in advance, this is the better design.
import { keywords } from "../../../12-evals/labs/typescript/baselines.ts";
import { execute, type Tool } from "../../../07-tools-and-mcp/labs/typescript/tools.ts";

export type Write = (prompt: string) => Promise<string>; // one plain model call, no tools

export type WorkflowResult =
  | { kind: "answer"; text: string; modelCalls: number; toolCalls: number }
  | { kind: "ask"; text: string } // we need something from the customer first
  | { kind: "handoff"; reason: string }; // not a question this workflow handles

export async function refundStatus(question: string, tools: Tool[], write: Write): Promise<WorkflowResult> {
  // 1. Route: the evals lab's keyword rules, free and instant.
  const label = await keywords(question);
  if (label !== "billing") return { kind: "handoff", reason: `classified as ${label}` };

  // 2. Extract the order ID with a pattern, not a model.
  const id = question.match(/\b([A-Za-z])(\d{3})\b/);
  if (!id) return { kind: "ask", text: "Could you tell me your order number? It looks like A123." };
  const orderId = id[1].toUpperCase() + id[2];

  // 3. Look the refund up: a fixed call, chosen by code.
  const refund = await execute({ id: "w1", name: "get_refund", arguments: JSON.stringify({ order_id: orderId }) }, tools, () => false);
  if (refund.isError) return { kind: "ask", text: `I couldn't find order ${orderId}. Could you check the number?` };

  // 4. One model call to phrase the facts. It has no tools, so nothing it reads can make it act.
  const text = await write(
    `Write a one-sentence reply to a customer about their refund, using only these facts.\n` +
      `Order: ${orderId}\nRefund: ${refund.content}\nTheir question: ${question}`,
  );
  return { kind: "answer", text, modelCalls: 1, toolCalls: 1 };
}
