// cassette.ts — record model replies once on your machine; replay them in CI with no model, no key and no cost.
import { createHash } from "node:crypto";
import { appendFileSync, existsSync, readFileSync } from "node:fs";

export type ModelRequest = { model: string; prompt: string; options: Record<string, unknown> };

/** The key is a hash of the exact request. Change one byte of the prompt and the old recording no longer matches. */
export function requestKey(request: ModelRequest): string {
  return createHash("sha256").update(JSON.stringify(request)).digest("hex").slice(0, 16);
}

export class MissingRecording extends Error {
  override name = "MissingRecording";
}

export class Cassette {
  private readonly replies = new Map<string, string>();
  private readonly path: string;

  constructor(path: string) {
    this.path = path;
    if (!existsSync(path)) return;
    for (const line of readFileSync(path, "utf8").split("\n").filter(Boolean)) {
      const { key, reply } = JSON.parse(line);
      this.replies.set(key, reply);
    }
  }

  get size(): number {
    return this.replies.size;
  }

  replay(request: ModelRequest): string {
    const reply = this.replies.get(requestKey(request));
    if (reply === undefined) throw new MissingRecording(`no recording for this ${request.model} request: record it locally and commit the cassette`);
    return reply;
  }

  /** Calls `send` only for requests not recorded yet, and appends the reply to the file. */
  async record(request: ModelRequest, send: (request: ModelRequest) => Promise<string>): Promise<string> {
    const key = requestKey(request);
    const known = this.replies.get(key);
    if (known !== undefined) return known;
    const reply = await send(request);
    this.replies.set(key, reply);
    appendFileSync(this.path, JSON.stringify({ key, model: request.model, reply }) + "\n");
    return reply;
  }
}
