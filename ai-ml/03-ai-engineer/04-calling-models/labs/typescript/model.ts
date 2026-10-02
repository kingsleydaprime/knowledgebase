// model.ts — the port: what the rest of the app needs from "a model", with no provider in sight.

export type Role = "system" | "user" | "assistant";
export type Message = { role: Role; content: string };
export type ChatOptions = { temperature?: number; maxTokens?: number; signal?: AbortSignal };
export type ChatResult = {
  text: string;
  finishReason: "stop" | "length" | "other"; // "length" means max tokens cut it off
  usage: { inputTokens: number; outputTokens: number };
};

export interface ChatModel {
  chat(messages: Message[], options?: ChatOptions): Promise<ChatResult>;
  stream(messages: Message[], options?: ChatOptions): AsyncIterable<string>;
}

/** The model is stateless: "memory" is the app resending every earlier turn on every call. */
export class Conversation {
  readonly messages: Message[];
  private readonly model: ChatModel;

  constructor(model: ChatModel, system: string) {
    this.model = model;
    this.messages = [{ role: "system", content: system }];
  }

  async say(content: string, options?: ChatOptions): Promise<string> {
    this.messages.push({ role: "user", content });
    const result = await this.model.chat(this.messages, options);
    this.messages.push({ role: "assistant", content: result.text });
    return result.text;
  }
}

/** A fake for tests: replies from a script and records what it was sent. */
export class FakeModel implements ChatModel {
  readonly calls: Message[][] = [];
  private readonly replies: string[];

  constructor(replies: string[]) {
    this.replies = [...replies];
  }

  async chat(messages: Message[]): Promise<ChatResult> {
    this.calls.push(structuredClone(messages));
    const text = this.replies.shift() ?? "";
    return { text, finishReason: "stop", usage: { inputTokens: 0, outputTokens: 0 } };
  }

  async *stream(messages: Message[]): AsyncIterable<string> {
    const { text } = await this.chat(messages);
    for (const word of text.split(/(?<= )/)) yield word;
  }
}
