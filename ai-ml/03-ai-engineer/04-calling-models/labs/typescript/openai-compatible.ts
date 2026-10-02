// openai-compatible.ts — an adapter for any server that speaks the OpenAI chat completions format:
// OpenAI, Ollama, vLLM, LM Studio, and most gateways. Other providers need their own adapter.
import type { ChatModel, ChatOptions, ChatResult, Message } from "./model.ts";
import { sseData } from "./sse.ts";

export class ModelError extends Error {
  readonly status: number;
  readonly retryable: boolean; // rate limits and server errors are worth retrying; bad requests aren't

  constructor(status: number, body: string) {
    super(`model request failed: ${status} ${body.slice(0, 200)}`);
    this.status = status;
    this.retryable = status === 429 || status >= 500;
  }
}

type Config = {
  baseUrl: string;
  model: string;
  apiKey?: string;
  extraBody?: Record<string, unknown>; // provider-specific fields, e.g. { reasoning_effort: "none" }
  fetch?: typeof fetch;
};

export class OpenAICompatibleModel implements ChatModel {
  private readonly config: Config;

  constructor(config: Config) {
    this.config = config;
  }

  async chat(messages: Message[], options: ChatOptions = {}): Promise<ChatResult> {
    const data = await (await this.post(messages, options, false)).json();
    const choice = data.choices[0];
    return {
      text: choice.message.content ?? "",
      finishReason: choice.finish_reason === "stop" ? "stop" : choice.finish_reason === "length" ? "length" : "other",
      usage: { inputTokens: data.usage?.prompt_tokens ?? 0, outputTokens: data.usage?.completion_tokens ?? 0 },
    };
  }

  async *stream(messages: Message[], options: ChatOptions = {}): AsyncIterable<string> {
    const res = await this.post(messages, options, true);
    for await (const data of sseData(res.body!)) {
      const delta = JSON.parse(data).choices[0]?.delta?.content;
      if (delta) yield delta;
    }
  }

  /** Never hard-code model names from memory: ask the server what it has. */
  async listModels(): Promise<string[]> {
    const res = await this.fetch("/models", { headers: this.headers() });
    return (await res.json()).data.map((m: { id: string }) => m.id).sort();
  }

  private async post(messages: Message[], options: ChatOptions, stream: boolean): Promise<Response> {
    return this.fetch("/chat/completions", {
      method: "POST",
      headers: { ...this.headers(), "content-type": "application/json" },
      body: JSON.stringify({
        model: this.config.model,
        messages,
        stream,
        ...this.config.extraBody,
        ...(options.temperature !== undefined && { temperature: options.temperature }),
        ...(options.maxTokens !== undefined && { max_tokens: options.maxTokens }),
      }),
      signal: options.signal,
    });
  }

  private async fetch(path: string, init: RequestInit): Promise<Response> {
    const res = await (this.config.fetch ?? fetch)(this.config.baseUrl + path, init);
    if (!res.ok) throw new ModelError(res.status, await res.text());
    return res;
  }

  private headers(): Record<string, string> {
    return this.config.apiKey ? { authorization: `Bearer ${this.config.apiKey}` } : {};
  }
}
