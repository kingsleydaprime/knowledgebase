// prompt.ts — prompts as files: load, fill in, keep user text fenced off from instructions.
import { readFileSync } from "node:fs";

/** Prompts live in version control as files, so a change is a diff you can review and roll back. */
export function loadPrompt(name: string): string {
  return readFileSync(new URL(`./prompts/${name}.md`, import.meta.url), "utf8");
}

/** Fill {{name}} slots. A missing value is a bug, not an empty string. */
export function render(template: string, values: Record<string, string>): string {
  return template.replace(/\{\{(\w+)\}\}/g, (_, name: string) => {
    if (!(name in values)) throw new Error(`prompt needs a value for {{${name}}}`);
    return values[name];
  });
}

/** User text goes inside <review> tags. Stop it from closing the tag early and adding
 *  "instructions" after it. This lowers the risk of prompt injection; it doesn't remove it. */
export function fenceUserText(text: string): string {
  return text.replace(/<\/?review>/gi, (tag) => tag.replace("<", "&lt;"));
}

export type Label = "positive" | "negative" | "mixed";
export type Example = { review: string; label: Label };

/** Few-shot examples in exactly the format the real question uses: consistency beats explanation. */
export function formatExamples(examples: Example[]): string {
  return examples.map((e) => `<review>\n${fenceUserText(e.review)}\n</review>\n${e.label}`).join("\n\n");
}

/** Models don't always reply with exactly one word. Accept "Mixed." or "Sentiment: positive"; reject anything ambiguous. */
export function parseLabel(reply: string): Label | null {
  const found = reply.toLowerCase().match(/\b(positive|negative|mixed)\b/g) ?? [];
  return new Set(found).size === 1 ? (found[0] as Label) : null;
}
