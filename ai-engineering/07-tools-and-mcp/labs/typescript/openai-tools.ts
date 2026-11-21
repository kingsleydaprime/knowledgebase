// openai-tools.ts — the ToolModel port over the OpenAI chat completions format, which Ollama, vLLM,
// OpenAI and most gateways accept. Anthropic's Messages API has the same ideas in a different shape.
import type { Message, ToolModel, Turn } from "./loop.ts";

type Config = { baseUrl: string; model: string; apiKey?: string; extraBody?: Record<string, unknown>; fetch?: typeof fetch };

export function toWire(messages: Message[]) {
  return messages.map((m) => {
    if (m.role === "tool") return { role: "tool", tool_call_id: m.toolCallId, content: m.content };
    if (m.role === "assistant" && m.toolCalls?.length) {
      return {
        role: "assistant",
        content: m.content,
        tool_calls: m.toolCalls.map((c) => ({ id: c.id, type: "function", function: { name: c.name, arguments: c.arguments } })),
      };
    }
    return { role: m.role, content: m.content };
  });
}

export function openAITools(config: Config): ToolModel {
  return async (messages, tools): Promise<Turn> => {
    const res = await (config.fetch ?? fetch)(`${config.baseUrl}/chat/completions`, {
      method: "POST",
      headers: { "content-type": "application/json", ...(config.apiKey && { authorization: `Bearer ${config.apiKey}` }) },
      body: JSON.stringify({
        model: config.model,
        messages: toWire(messages),
        tools: tools.map((t) => ({ type: "function", function: { name: t.name, description: t.description, parameters: t.inputSchema } })),
        ...config.extraBody,
      }),
    });
    if (!res.ok) throw new Error(`model request failed: ${res.status} ${(await res.text()).slice(0, 200)}`);
    const message = (await res.json()).choices[0].message;
    return {
      content: message.content ?? "",
      toolCalls: (message.tool_calls ?? []).map((c: { id: string; function: { name: string; arguments: string | object } }) => ({
        id: c.id,
        name: c.function.name,
        // The OpenAI format says a JSON string; Ollama's own /api/chat sends an object. Accept both.
        arguments: typeof c.function.arguments === "string" ? c.function.arguments : JSON.stringify(c.function.arguments),
      })),
    };
  };
}
