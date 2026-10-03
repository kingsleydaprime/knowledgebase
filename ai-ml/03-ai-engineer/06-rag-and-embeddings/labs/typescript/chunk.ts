// chunk.ts — split documents into passages small enough to retrieve, without cutting a thought in half.
import { readFileSync } from "node:fs";

export type Doc = { id: string; title: string; body: string };
export type Chunk = { id: string; doc: string; heading: string; text: string };

export const loadHelp = (): Doc[] => JSON.parse(readFileSync(new URL("../shared/help.json", import.meta.url), "utf8"));

/** One chunk per section: a "## heading" and the paragraphs under it. Sections longer than `maxWords` are
 *  split on paragraph boundaries, and each extra piece repeats the last paragraph before it (overlap),
 *  so a sentence that refers back still has what it refers to. */
export function chunkDoc(doc: Doc, maxWords = 60): Chunk[] {
  const chunks: Chunk[] = [];
  for (const section of doc.body.split(/^## /m).filter((s) => s.trim())) {
    const [heading, ...rest] = section.split("\n");
    const paragraphs = rest.join("\n").split(/\n\s*\n/).map((p) => p.trim()).filter(Boolean);
    let current: string[] = [];
    const flush = () => {
      chunks.push({ id: `${doc.id}#${chunks.length + 1}`, doc: doc.id, heading: heading.trim(), text: current.join("\n\n") });
    };
    for (const p of paragraphs) {
      const words = (xs: string[]) => xs.join(" ").split(/\s+/).length;
      if (current.length && words([...current, p]) > maxWords) {
        flush();
        current = [current.at(-1)!]; // overlap: carry the last paragraph into the next chunk
      }
      current.push(p);
    }
    if (current.length) flush();
  }
  return chunks;
}

/** Contextual retrieval: prefix each chunk with where it came from, so "it takes 5 to 10 days" still says
 *  *what* takes 5 to 10 days when it's embedded or searched on its own. */
export const withContext = (c: Chunk, title: string) => `${title} > ${c.heading}\n${c.text}`;
