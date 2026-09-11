/**
 * Abbreviations — a Quartz transformer.
 *
 * Authors write the bare acronym in markdown. At build time every occurrence is
 * wrapped in <abbr title="...">, so the full meaning appears on hover without
 * putting 167 KB of markup into the notes.
 *
 * Skips anything inside code, pre, a, abbr and headings, so identifiers such as
 * a variable called `dfs` or a filename are never touched.
 */
import { readFileSync } from "fs";
import { fileURLToPath } from "url";
import { dirname, join } from "path";
import { visit } from "unist-util-visit";

const here = dirname(fileURLToPath(import.meta.url));
const GLOSSARY = JSON.parse(readFileSync(join(here, "glossary.json"), "utf8"));

const SKIP = new Set(["code", "pre", "abbr", "a", "script", "style",
                      "h1", "h2", "h3", "h4", "h5", "h6"]);

// longest first, so "SCCs" is matched before "SCC"
const TERMS = Object.keys(GLOSSARY).sort((a, b) => b.length - a.length);
const PATTERN = new RegExp(`\\b(${TERMS.map(escapeRe).join("|")})\\b`, "g");

function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

export const Abbreviations = (opts = {}) => {
  const glossary = { ...GLOSSARY, ...(opts.extra || {}) };
  return {
    name: "Abbreviations",
    htmlPlugins() {
      return [
        () => (tree) => {
          visit(tree, "text", (node, index, parent) => {
            if (!parent || SKIP.has(parent.tagName)) return;
            const value = node.value;
            if (!PATTERN.test(value)) return;
            PATTERN.lastIndex = 0;

            const out = [];
            let last = 0;
            let m;
            while ((m = PATTERN.exec(value)) !== null) {
              const expansion = glossary[m[1]];
              if (!expansion) continue;
              if (m.index > last) {
                out.push({ type: "text", value: value.slice(last, m.index) });
              }
              out.push({
                type: "element",
                tagName: "abbr",
                properties: { title: expansion, className: ["abbr-term"] },
                children: [{ type: "text", value: m[1] }],
              });
              last = m.index + m[1].length;
            }
            if (!out.length) return;
            if (last < value.length) {
              out.push({ type: "text", value: value.slice(last) });
            }
            parent.children.splice(index, 1, ...out);
            return index + out.length;
          });
        },
      ];
    },
  };
};

export default Abbreviations;
