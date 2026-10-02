// sse.ts — read a server-sent events stream: lines of "data: ...", events separated by a blank line.
// Network chunks don't respect line boundaries, so keep the unfinished tail until the next chunk.

export async function* sseData(body: AsyncIterable<Uint8Array>): AsyncIterable<string> {
  const decoder = new TextDecoder();
  let buffer = "";
  for await (const chunk of body) {
    buffer += decoder.decode(chunk, { stream: true }); // stream: true keeps a split multi-byte character
    const events = buffer.split(/\r?\n\r?\n/);
    buffer = events.pop()!; // the last piece may be incomplete
    for (const event of events) {
      const data = event
        .split(/\r?\n/)
        .filter((line) => line.startsWith("data:"))
        .map((line) => line.slice(5).trimStart())
        .join("\n");
      if (data === "[DONE]") return;
      if (data) yield data;
    }
  }
}
